"""Account provisioning and identity linking.

One AtlasCode user, several ways to prove it. This module is the single place
that decides when a federated identity may attach to an existing account and
when a new account is created, so the rules cannot drift between endpoints.

Linking policy
--------------
1. Known ``firebase_uid`` → that account, always. This is the stable identity.
2. Same email, and the provider says the email is **verified** → link. Google
   and GitHub only mint verified emails for addresses the person proved they
   control, so this cannot be used to seize someone else's account.
3. Same email but **unverified** → refuse. Otherwise anyone could register
   ``victim@example.com`` with Firebase, skip the verification mail, and walk
   into the victim's AtlasCode account.
4. No match → create a fresh account with a profile, exactly like registration.
"""

from __future__ import annotations

import re
import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AuthProviderEnum,
    LanguageEnum,
    NotificationTypeEnum,
    StudentProfile,
    User,
)
from app.services.firebase_auth import FirebaseIdentity
from app.services.notifications import create_notification

#: Firebase's provider ids mapped onto our own enum.
_PROVIDER_MAP = {
    "google.com": AuthProviderEnum.google,
    "github.com": AuthProviderEnum.github,
    "password": AuthProviderEnum.firebase_password,
}

_USERNAME_SAFE = re.compile(r"[^a-zA-Z0-9_]+")


class AccountLinkConflict(Exception):
    """An existing account owns this email and the identity cannot claim it."""


def provider_from_firebase(sign_in_provider: str) -> AuthProviderEnum:
    return _PROVIDER_MAP.get(sign_in_provider, AuthProviderEnum.firebase_password)


def _username_seed(identity: FirebaseIdentity) -> str:
    """A readable starting point for the generated username."""
    raw = ""
    if identity.name:
        raw = identity.name
    elif identity.email:
        raw = identity.email.split("@", 1)[0]
    cleaned = _USERNAME_SAFE.sub("_", raw).strip("_").lower()
    if len(cleaned) < 3:
        cleaned = f"learner_{secrets.token_hex(3)}"
    return cleaned[:80]


async def _allocate_username(db: AsyncSession, seed: str) -> str:
    """Find a free username near `seed`.

    Usernames are unique, and two people called "alex" are entirely normal, so
    collisions get a short random suffix rather than an error the user cannot
    act on.
    """
    result = await db.execute(select(User.id).where(User.username == seed))
    if result.scalar_one_or_none() is None:
        return seed

    for _ in range(10):
        candidate = f"{seed[:88]}_{secrets.token_hex(3)}"
        result = await db.execute(select(User.id).where(User.username == candidate))
        if result.scalar_one_or_none() is None:
            return candidate
    # Practically unreachable; keeps the function total rather than looping.
    return f"learner_{secrets.token_hex(8)}"


async def get_or_create_user_for_firebase_identity(
    db: AsyncSession,
    identity: FirebaseIdentity,
    *,
    preferred_language: LanguageEnum = LanguageEnum.en,
    timezone_offset_minutes: int = 0,
) -> tuple[User, bool]:
    """Resolve a verified Firebase identity to an AtlasCode user.

    Returns ``(user, created)``. Raises :class:`AccountLinkConflict` when the
    email belongs to someone else and the identity has not proved ownership.
    """
    provider = provider_from_firebase(identity.sign_in_provider)

    # 1. Already linked.
    result = await db.execute(select(User).where(User.firebase_uid == identity.uid))
    user = result.scalar_one_or_none()
    if user is not None:
        _refresh_profile_fields(user, identity, provider, timezone_offset_minutes)
        await db.commit()
        await db.refresh(user)
        return user, False

    if not identity.email:
        # Every AtlasCode account is keyed by email (it is how support, resets
        # and notifications work), so an identity without one cannot be used.
        raise AccountLinkConflict("This sign-in method did not provide an email address")

    # 2/3. An account already owns this email.
    result = await db.execute(select(User).where(User.email == identity.email))
    existing = result.scalar_one_or_none()
    if existing is not None:
        if not identity.email_verified:
            raise AccountLinkConflict(
                "An account already exists for this email address. Sign in with your "
                "password, or verify your email with the provider first."
            )
        existing.firebase_uid = identity.uid
        existing.email_verified = True
        if existing.auth_provider == AuthProviderEnum.password.value and existing.hashed_password:
            # Keep `password` as the primary provider: the account can still
            # sign in with its AtlasCode password, and now also with Firebase.
            pass
        else:
            existing.auth_provider = provider.value
        _refresh_profile_fields(existing, identity, provider, timezone_offset_minutes)
        await _ensure_profile(db, existing)
        await db.commit()
        await db.refresh(existing)
        return existing, False

    # 4. Brand new account.
    username = await _allocate_username(db, _username_seed(identity))
    user = User(
        email=identity.email,
        username=username,
        hashed_password=None,
        firebase_uid=identity.uid,
        auth_provider=provider.value,
        email_verified=identity.email_verified,
        avatar_url=identity.picture,
        preferred_language=preferred_language,
        timezone_offset_minutes=timezone_offset_minutes,
        last_login_at=datetime.utcnow(),
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as exc:
        # Two concurrent first sign-ins for the same identity: let the winner
        # stand and read it back instead of failing the request.
        await db.rollback()
        result = await db.execute(select(User).where(User.firebase_uid == identity.uid))
        raced = result.scalar_one_or_none()
        if raced is None:
            raise AccountLinkConflict("Could not create the account") from exc
        return raced, False

    db.add(StudentProfile(user_id=user.id, name=identity.name))
    await create_notification(db, user.id, NotificationTypeEnum.welcome)
    await db.commit()
    await db.refresh(user)
    return user, True


def _refresh_profile_fields(
    user: User,
    identity: FirebaseIdentity,
    provider: AuthProviderEnum,
    timezone_offset_minutes: int,
) -> None:
    """Keep the cheap provider-supplied details current on each sign-in."""
    if identity.picture and user.avatar_url != identity.picture:
        user.avatar_url = identity.picture
    if identity.email_verified and not user.email_verified:
        user.email_verified = True
    if user.firebase_uid is None:
        user.firebase_uid = identity.uid
    user.timezone_offset_minutes = timezone_offset_minutes
    user.last_login_at = datetime.utcnow()


async def _ensure_profile(db: AsyncSession, user: User) -> None:
    """A user without a StudentProfile has no XP to show; create one lazily."""
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    if result.scalar_one_or_none() is None:
        db.add(StudentProfile(user_id=user.id))
