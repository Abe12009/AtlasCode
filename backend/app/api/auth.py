from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import (
    verify_password,
    verify_and_upgrade_password,
    get_password_hash,
    create_access_token,
)
from app.core.dependencies import get_current_user
from app.models import User, StudentProfile, NotificationTypeEnum
from app.schemas import UserCreate, UserLogin, UserResponse, UserUpdate, Token, StudentProfileResponse
from app.services.notifications import create_notification

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where((User.email == user_data.email) | (User.username == user_data.username)))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        preferred_language=user_data.preferred_language
    )
    db.add(user)
    await db.flush()

    profile = StudentProfile(user_id=user.id)
    db.add(profile)
    await create_notification(db, user.id, NotificationTypeEnum.welcome)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    is_valid, upgraded_hash = verify_and_upgrade_password(
        credentials.password, user.hashed_password
    )
    if not is_valid:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Only a correct password reaches here, so a wrong attempt can never
    # rewrite the stored hash. Accounts migrate off the slow legacy scheme one
    # successful login at a time, with no forced reset and no invalidated
    # session; an account that never logs in simply keeps its old hash.
    if upgraded_hash:
        user.hashed_password = upgraded_hash
        await db.commit()

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_update.username is not None:
        result = await db.execute(select(User).where(User.username == user_update.username, User.id != current_user.id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_update.username
    if user_update.preferred_language is not None:
        current_user.preferred_language = user_update.preferred_language

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/profile", response_model=StudentProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile