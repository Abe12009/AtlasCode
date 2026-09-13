from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import decode_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    if payload.get("purpose"):
        # A single-purpose token (e.g. password reset) must never double as a
        # session token, even if it leaks into a log or a Referer header.
        raise credentials_exception
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        # 403, not 401: the token itself is valid (it decoded and names a
        # real account) -- the account is suspended. Matches the status
        # code the Firebase login path already uses for the same state
        # (app.api.auth.login_with_firebase), which previously disagreed
        # with this one (400 here, 403 there) for no reason.
        raise HTTPException(status_code=403, detail="This account has been disabled")
    return user


async def get_current_staff_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Gate for /admin/* routes. 404, not 403: an unmoderated account
    probing for admin routes learns nothing about whether they exist."""
    if not current_user.is_staff:
        raise HTTPException(status_code=404, detail="Not found")
    return current_user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("purpose"):
        return None
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()