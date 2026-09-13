"""Achievement award-checking.

Runs synchronously right after anything that can change a user's XP,
streak, level, lessons_completed, or projects_completed. Today that's
exactly two call sites -- exercise submission and project-task submission,
both of which already call `record_activity()` (app.services.stats) -- so a
synchronous check there is real-time by construction, with no periodic
sweep needed: nothing else moves these numbers.

Idempotent: relies on UserAchievement's (user_id, achievement_id) unique
constraint via an in-memory "already earned" set checked before each award,
so calling this twice for the same user is a no-op the second time.

Loops until a pass awards nothing new, so an achievement's own XP reward
pushing a user's level across a threshold can unlock a level-based
achievement in the same call, rather than only on their next action.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Achievement,
    AchievementTranslation,
    Course,
    CourseProgress,
    Lesson,
    LanguageEnum,
    NotificationTypeEnum,
    StudentProfile,
    UserAchievement,
)
from app.services.notifications import create_notification
from app.services.stats import level_for_xp

@dataclass(frozen=True)
class EarnedAchievement:
    """What a caller needs to show a toast/notification for one award."""

    slug: str
    icon: str
    title: str
    xp_reward: int


async def _completed_courses_count(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count(CourseProgress.id)).where(
            CourseProgress.user_id == user_id,
            CourseProgress.total_lessons > 0,
            CourseProgress.completed_lessons >= CourseProgress.total_lessons,
        )
    )
    return result.scalar_one()


async def _current_value(
    db: AsyncSession, user_id: int, profile: StudentProfile, condition_type: str
) -> int:
    if condition_type == "lessons_completed":
        return profile.completed_lessons or 0
    if condition_type == "projects_completed":
        return profile.completed_projects or 0
    if condition_type == "streak":
        return profile.streak or 0
    if condition_type == "level":
        return level_for_xp(profile.xp or 0)
    if condition_type == "courses_completed":
        return await _completed_courses_count(db, user_id)
    raise ValueError(f"Unknown achievement condition_type: {condition_type!r}")


async def _threshold(db: AsyncSession, achievement: Achievement) -> int:
    # These two achievements mean "literally all of them", so their
    # threshold is computed from the current catalog size rather than the
    # condition_value seeded once at a point in curriculum history -- a
    # fixed number here is exactly the kind of value that silently goes
    # stale as the curriculum grows (see app/curriculum.py's own
    # PLANNED_SLUGS note on the same class of bug). Achievement.condition_value
    # is left as originally seeded for these two slugs; it is simply not read.
    if achievement.slug == "all-lessons":
        result = await db.execute(select(func.count(Lesson.id)))
        return result.scalar_one()
    if achievement.slug == "all-courses":
        result = await db.execute(select(func.count(Course.id)))
        return result.scalar_one()
    return achievement.condition_value


async def check_and_award_achievements(
    db: AsyncSession,
    user_id: int,
    profile: StudentProfile,
    language: LanguageEnum = LanguageEnum.en,
) -> list[EarnedAchievement]:
    """Evaluate every achievement's condition and award any newly-qualifying
    one. Does not commit -- caller controls the transaction boundary, same
    convention as create_notification.

    Returns the achievements newly awarded by this call, translated into
    `language`, for callers that want to toast/notify about them. Empty if
    none newly qualified.
    """
    already_earned_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
    )
    already_earned = set(already_earned_result.scalars().all())

    achievements = (await db.execute(select(Achievement))).scalars().all()

    earned: list[EarnedAchievement] = []
    changed = True
    while changed:
        changed = False
        for achievement in achievements:
            if achievement.id in already_earned:
                continue
            try:
                current = await _current_value(db, user_id, profile, achievement.condition_type)
            except ValueError:
                continue
            threshold = await _threshold(db, achievement)
            if current < threshold:
                continue

            db.add(UserAchievement(user_id=user_id, achievement_id=achievement.id))
            already_earned.add(achievement.id)
            if achievement.xp_reward:
                profile.xp += achievement.xp_reward

            title_result = await db.execute(
                select(AchievementTranslation.title).where(
                    AchievementTranslation.achievement_id == achievement.id,
                    AchievementTranslation.language == language,
                )
            )
            title = title_result.scalar_one_or_none() or achievement.slug.replace("-", " ").title()

            await create_notification(
                db,
                user_id,
                NotificationTypeEnum.achievement_earned,
                {"achievement_slug": achievement.slug, "icon": achievement.icon, "xp_reward": achievement.xp_reward},
            )

            earned.append(
                EarnedAchievement(
                    slug=achievement.slug,
                    icon=achievement.icon,
                    title=title,
                    xp_reward=achievement.xp_reward or 0,
                )
            )
            changed = True

    return earned
