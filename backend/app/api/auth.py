import base64
import json
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_and_upgrade_password,
    verify_password,
)
from app.db.session import get_db
from app.models import (
    AuthProviderEnum,
    LanguageEnum,
    NotificationTypeEnum,
    StudentProfile,
    User,
)
from app.schemas import (
    AuthConfigResponse,
    AvatarUploadRequest,
    FirebaseLoginRequest,
    PasswordChangeRequest,
    StudentProfileResponse,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.services.accounts import (
    AccountLinkConflict,
    get_or_create_user_for_firebase_identity,
)
from app.services.firebase_auth import (
    FirebaseAuthError,
    FirebaseNotConfigured,
    is_firebase_configured,
    verify_firebase_id_token,
)
from app.services.notifications import create_notification
from app.services.stats import clamp_timezone_offset

router = APIRouter(prefix="/auth", tags=["auth"])

#: One message for "no such account" and "wrong password" alike. Distinct
#: messages would turn the login form into an email-enumeration oracle.
INVALID_CREDENTIALS = "Incorrect email or password"


def _apply_timezone(user: User, offset_minutes) -> None:
    if offset_minutes is not None:
        user.timezone_offset_minutes = clamp_timezone_offset(offset_minutes)


@router.get("/config", response_model=AuthConfigResponse)
async def get_auth_config():
    """Which sign-in methods this deployment supports.

    The client uses this to decide whether to show the Google/GitHub buttons at
    all, so an unconfigured deployment presents an honest UI instead of buttons
    that fail when pressed.
    """
    return AuthConfigResponse(
        firebase_enabled=is_firebase_configured(),
        password_login_enabled=True,
    )


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user_data.email.lower().strip()
    result = await db.execute(
        select(User).where((User.email == email) | (User.username == user_data.username))
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    user = User(
        email=email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        auth_provider=AuthProviderEnum.password.value,
        preferred_language=user_data.preferred_language,
        timezone_offset_minutes=clamp_timezone_offset(user_data.timezone_offset_minutes),
        last_login_at=datetime.utcnow(),
    )
    db.add(user)
    await db.flush()

    db.add(StudentProfile(user_id=user.id))
    await create_notification(db, user.id, NotificationTypeEnum.welcome)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == credentials.email.lower().strip())
    )
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password:
        # No account, or an account that only signs in through a provider.
        # Same response either way — see INVALID_CREDENTIALS.
        raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)

    is_valid, upgraded_hash = verify_and_upgrade_password(
        credentials.password, user.hashed_password
    )
    if not is_valid:
        raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)

    # Only a correct password reaches here, so a wrong attempt can never
    # rewrite the stored hash. Accounts migrate off the slow legacy scheme one
    # successful login at a time, with no forced reset and no invalidated
    # session; an account that never logs in simply keeps its old hash.
    if upgraded_hash:
        user.hashed_password = upgraded_hash
    _apply_timezone(user, credentials.timezone_offset_minutes)
    user.last_login_at = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/firebase", response_model=Token)
async def login_with_firebase(
    payload: FirebaseLoginRequest, db: AsyncSession = Depends(get_db)
):
    """Exchange a Firebase ID token for an AtlasCode session token.

    This is the single bridge between Firebase Authentication and AtlasCode's
    own user model: Google, GitHub and Firebase email/password sign-ins all
    arrive here. The token's signature, audience and issuer are verified
    server-side before any account is touched — a client-supplied token is
    never taken at face value.
    """
    try:
        identity = await verify_firebase_id_token(payload.id_token)
    except FirebaseNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except FirebaseAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    try:
        user, _created = await get_or_create_user_for_firebase_identity(
            db,
            identity,
            preferred_language=payload.preferred_language or LanguageEnum.en,
            timezone_offset_minutes=clamp_timezone_offset(payload.timezone_offset_minutes),
        )
    except AccountLinkConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been disabled")

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user_update.username is not None:
        result = await db.execute(
            select(User).where(
                User.username == user_update.username, User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_update.username
    if user_update.preferred_language is not None:
        current_user.preferred_language = user_update.preferred_language
    if user_update.avatar_config is not None:
        try:
            json.loads(user_update.avatar_config)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="avatar_config must be valid JSON") from exc
        current_user.avatar_config = user_update.avatar_config
    if user_update.avatar_type is not None:
        if user_update.avatar_type == "generated" and not (
            user_update.avatar_config or current_user.avatar_config
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot switch to a generated avatar before one has been built",
            )
        current_user.avatar_type = user_update.avatar_type
    _apply_timezone(current_user, user_update.timezone_offset_minutes)

    await db.commit()
    await db.refresh(current_user)
    return current_user


#: Formats accepted for an uploaded avatar. SVG is excluded deliberately —
#: it can embed script content and this is rendered back to other users.
_ALLOWED_AVATAR_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
#: Decoded byte size cap. The frontend resizes/compresses before sending;
#: this is the server-side backstop, since a client-side check alone proves
#: nothing.
_MAX_AVATAR_BYTES = 500_000


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    payload: AvatarUploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set a device-uploaded photo as the active avatar.

    Expects a base64 data: URL for an allowed image type, already resized and
    cropped client-side. Re-validates type and size here rather than trusting
    the client: the mime type in the data URL prefix, and the true decoded
    byte length (a client could lie about either).
    """
    match = re.match(r"^data:([\w/+.-]+);base64,(.+)$", payload.data_url, re.DOTALL)
    if not match:
        raise HTTPException(status_code=400, detail="avatar must be a base64 data URL")

    mime_type, encoded = match.group(1).lower(), match.group(2)
    if mime_type not in _ALLOWED_AVATAR_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type. Allowed: {', '.join(sorted(_ALLOWED_AVATAR_MIME_TYPES))}",
        )

    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="Invalid image data") from exc

    if len(decoded) > _MAX_AVATAR_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large (max {_MAX_AVATAR_BYTES // 1000}KB after compression)",
        )
    if len(decoded) == 0:
        raise HTTPException(status_code=400, detail="Image is empty")

    current_user.avatar_image_data = payload.data_url
    current_user.avatar_type = "upload"
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the AtlasCode password of an already-authenticated account.

    Requires the current password, so a stolen session alone cannot lock the
    owner out. Accounts that sign in only through a provider have no password
    to change — they reset it with the provider instead.
    """
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail="This account signs in with an external provider and has no AtlasCode password",
        )
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    current_user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()
    return None


@router.get("/profile", response_model=StudentProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile
