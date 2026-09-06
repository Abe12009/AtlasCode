from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import Achievement, StudentProfile, User, UserAchievement
from app.schemas import PublicProfileResponse
from app.services.stats import clamp_timezone_offset, effective_streak

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}", response_model=PublicProfileResponse)
async def get_public_profile(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """A user's public profile: username, avatar, level/XP/streak, achievements.

    Nothing else — no email, no settings, no per-lesson progress, no auth
    provider details. Visible when the target account's `profile_visibility`
    is "public", or always to the account's own owner (so a private profile
    still previews correctly to the person who owns it).
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.profile_visibility != "public" and user.id != current_user.id:
        # Same response as "not found": a private profile's existence is not
        # revealed to someone who isn't allowed to see it.
        raise HTTPException(status_code=404, detail="User not found")

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()

    live_streak = 0
    if profile is not None:
        live_streak = effective_streak(
            stored_streak=profile.streak or 0,
            last_activity=profile.last_activity_date,
            now_utc=datetime.utcnow(),
            offset_minutes=clamp_timezone_offset(user.timezone_offset_minutes),
        )

    achievements_result = await db.execute(
        select(UserAchievement)
        .options(selectinload(UserAchievement.achievement).selectinload(Achievement.translations))
        .where(UserAchievement.user_id == user.id)
        .order_by(UserAchievement.earned_at.desc())
    )
    achievements = achievements_result.scalars().all()
    for ua in achievements:
        ua.achievement.translations = [
            t for t in ua.achievement.translations if t.language == current_user.preferred_language
        ]

    return PublicProfileResponse(
        username=user.username,
        avatar_url=user.avatar_url,
        avatar_config=user.avatar_config,
        avatar_type=user.avatar_type,
        level=profile.level if profile else 1,
        xp=profile.xp if profile else 0,
        streak=live_streak,
        member_since=user.created_at,
        achievements=achievements,
    )
