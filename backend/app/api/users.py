from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import Achievement, Report, StudentProfile, User, UserAchievement
from app.schemas import PublicProfileResponse, ReportCreateRequest, ReportResponse
from app.services.stats import clamp_timezone_offset, effective_streak

router = APIRouter(prefix="/users", tags=["users"])

#: A report queue that fills with junk is as useless as no queue at all.
#: Same "count rows in a trailing window" style as Cody's per-user limit.
REPORT_RATE_LIMIT_PER_HOUR = 5


async def _reports_filed_this_hour(db: AsyncSession, reporter_user_id: int) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(func.count(Report.id)).where(
            Report.reporter_user_id == reporter_user_id,
            Report.created_at >= cutoff,
        )
    )
    return result.scalar_one()


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


@router.post("/{username}/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_user(
    username: str,
    payload: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """File a report against another account for staff review.

    Same visibility rule as viewing a profile: you can only report an
    account whose profile you can actually see (public, or your own --
    though reporting yourself is allowed and simply pointless, not blocked,
    since there's no real harm in it and no reason to special-case it).
    """
    result = await db.execute(select(User).where(User.username == username))
    target = result.scalar_one_or_none()
    if target is None or (target.profile_visibility != "public" and target.id != current_user.id):
        raise HTTPException(status_code=404, detail="User not found")

    if await _reports_filed_this_hour(db, current_user.id) >= REPORT_RATE_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reports filed. Please try again later.",
        )

    db.add(
        Report(
            reporter_user_id=current_user.id,
            reported_user_id=target.id,
            reported_username=target.username,
            reason=payload.reason,
            details=payload.details,
        )
    )
    await db.commit()
    return None
