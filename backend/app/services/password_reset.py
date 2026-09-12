"""Token minting/verification and rate limiting for password-reset-by-email.

The reset token is a normal AtlasCode JWT (see app.core.security), not a
separate mechanism, but it carries a `purpose` claim that:

  * app.core.dependencies rejects on every normal authenticated endpoint, so
    a reset token can never be replayed as a session bearer token, and
  * is bound to a fingerprint of the account's *current* password hash, so
    the token stops verifying the instant the password changes -- by this
    flow or any other. That gives one-time-use semantics without a token
    table to store or clean up.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, decode_token
from app.models import PasswordResetAttempt, User

RESET_TOKEN_PURPOSE = "password_reset"


def _password_fingerprint(hashed_password: str) -> str:
    return hashlib.sha256(hashed_password.encode()).hexdigest()[:16]


def create_password_reset_token(user: User) -> str:
    settings = get_settings()
    return create_access_token(
        data={
            "sub": user.id,
            "purpose": RESET_TOKEN_PURPOSE,
            "pwf": _password_fingerprint(user.hashed_password),
        },
        expires_delta=timedelta(minutes=settings.password_reset_token_expire_minutes),
    )


def verify_password_reset_token(token: str, user: User) -> bool:
    """True only for a token minted for this exact user and password hash."""
    payload = decode_token(token)
    if payload is None or payload.get("purpose") != RESET_TOKEN_PURPOSE:
        return False
    if payload.get("sub") != str(user.id):
        return False
    if not user.hashed_password:
        return False
    return payload.get("pwf") == _password_fingerprint(user.hashed_password)


async def check_and_log_reset_rate_limit(
    db: AsyncSession, email: str, ip_address: str | None
) -> bool:
    """Log this attempt, then report whether the email or IP is over its
    hourly limit. Logging happens before the check (and for every email,
    real or not) so the counters look identical whether or not an account
    exists -- the rate limit itself must never become an enumeration oracle.
    """
    settings = get_settings()
    db.add(PasswordResetAttempt(email=email, ip_address=ip_address))
    await db.flush()

    cutoff = datetime.utcnow() - timedelta(hours=1)

    email_count = await db.scalar(
        select(func.count(PasswordResetAttempt.id)).where(
            PasswordResetAttempt.email == email,
            PasswordResetAttempt.created_at >= cutoff,
        )
    )
    if email_count > settings.password_reset_rate_limit_per_email_per_hour:
        return False

    if ip_address:
        ip_count = await db.scalar(
            select(func.count(PasswordResetAttempt.id)).where(
                PasswordResetAttempt.ip_address == ip_address,
                PasswordResetAttempt.created_at >= cutoff,
            )
        )
        if ip_count > settings.password_reset_rate_limit_per_ip_per_hour:
            return False

    return True
