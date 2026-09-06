"""Learning statistics: streaks and week-over-week progress.

Everything here is derived from rows the student actually created — exercise
attempts, lesson completions, project completions. Nothing is estimated and
nothing is supplied by the client, so a brand-new account reports zeros rather
than an encouraging fiction.

Timezones
---------
"This week" and "today" are questions about the student's calendar, not the
server's. Each user carries ``timezone_offset_minutes`` (minutes east of UTC,
as reported by their browser); every boundary in this module is computed in
that local frame and then converted back to UTC for querying, because all
timestamps are stored as naive UTC.

The week starts on Monday, matching ISO-8601.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    ExerciseAttempt,
    LessonProgress,
    MissionStatusEnum,
    ProjectProgress,
    StudentProfile,
    User,
)

#: 0 = Monday, matching `datetime.weekday()` and ISO-8601.
WEEK_STARTS_ON = 0

#: XP needed per level. Mirrors the progression used when awarding XP in
#: app/api/exercises.py; kept here so level maths lives in one place.
XP_PER_LEVEL = 100

#: Guard against a nonsense offset from a hostile or broken client. Real world
#: offsets run from UTC-12:00 to UTC+14:00.
_MIN_OFFSET_MINUTES = -12 * 60
_MAX_OFFSET_MINUTES = 14 * 60


def clamp_timezone_offset(offset_minutes: Optional[int]) -> int:
    """Coerce a client-supplied UTC offset into a real-world value."""
    if offset_minutes is None:
        return 0
    try:
        value = int(offset_minutes)
    except (TypeError, ValueError):
        return 0
    return max(_MIN_OFFSET_MINUTES, min(_MAX_OFFSET_MINUTES, value))


def level_for_xp(xp: int) -> int:
    """The level a given lifetime XP total corresponds to (levels start at 1)."""
    return max(1, (max(xp, 0) // XP_PER_LEVEL) + 1)


def to_local(moment: datetime, offset_minutes: int) -> datetime:
    """Interpret a naive-UTC timestamp in the student's local frame."""
    return moment + timedelta(minutes=offset_minutes)


def to_utc(local_moment: datetime, offset_minutes: int) -> datetime:
    return local_moment - timedelta(minutes=offset_minutes)


def local_date(moment: datetime, offset_minutes: int) -> date:
    return to_local(moment, offset_minutes).date()


def week_start_utc(now_utc: datetime, offset_minutes: int) -> datetime:
    """The UTC instant at which the student's current local week began.

    Crossing midnight on Monday flips this to the new week, which is exactly
    what makes a Sunday-evening total disappear on Monday morning — the
    behaviour a weekly indicator is supposed to have.
    """
    local_now = to_local(now_utc, offset_minutes)
    days_since_week_start = (local_now.weekday() - WEEK_STARTS_ON) % 7
    local_week_start = datetime.combine(
        local_now.date() - timedelta(days=days_since_week_start), datetime.min.time()
    )
    return to_utc(local_week_start, offset_minutes)


def _distinct_local_days(moments: Iterable[Optional[datetime]], offset_minutes: int) -> set[date]:
    return {local_date(m, offset_minutes) for m in moments if m is not None}


# ---------------------------------------------------------------------------
# Streaks
# ---------------------------------------------------------------------------


def next_streak_value(
    *,
    current_streak: int,
    last_activity: Optional[datetime],
    now_utc: datetime,
    offset_minutes: int,
) -> int:
    """The streak after recording activity at ``now_utc``.

    Same local day → unchanged. The very next local day → +1. A gap, or no
    history at all → the streak restarts at 1.
    """
    today = local_date(now_utc, offset_minutes)
    if last_activity is None:
        return 1
    last_day = local_date(last_activity, offset_minutes)
    if last_day == today:
        return max(current_streak, 1)
    if last_day == today - timedelta(days=1):
        return max(current_streak, 0) + 1
    return 1


def effective_streak(
    *,
    stored_streak: int,
    last_activity: Optional[datetime],
    now_utc: datetime,
    offset_minutes: int,
) -> int:
    """The streak as it should be *displayed* right now.

    A stored streak goes stale the moment a day is missed, and nothing writes
    to the row while a student is away. Anything older than yesterday is
    therefore reported as broken.
    """
    if last_activity is None:
        return 0
    today = local_date(now_utc, offset_minutes)
    last_day = local_date(last_activity, offset_minutes)
    if last_day >= today - timedelta(days=1):
        return max(stored_streak, 0)
    return 0


async def record_activity(
    db: AsyncSession,
    user: User,
    profile: Optional[StudentProfile],
    *,
    now_utc: Optional[datetime] = None,
) -> Optional[StudentProfile]:
    """Register that the student did something today and advance the streak.

    Callers are responsible for committing; this only mutates the profile so it
    can join whatever transaction the endpoint is already running.
    """
    if profile is None:
        return None
    moment = now_utc or datetime.utcnow()
    offset = clamp_timezone_offset(getattr(user, "timezone_offset_minutes", 0))

    profile.streak = next_streak_value(
        current_streak=profile.streak or 0,
        last_activity=profile.last_activity_date,
        now_utc=moment,
        offset_minutes=offset,
    )
    profile.longest_streak = max(profile.longest_streak or 0, profile.streak)
    profile.last_activity_date = moment
    return profile


# ---------------------------------------------------------------------------
# Weekly deltas
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WeeklyStats:
    """Real change since the start of the student's current local week."""

    week_start: datetime
    xp: int
    lessons_completed: int
    projects_completed: int
    levels_gained: int
    active_days: int

    @property
    def has_activity(self) -> bool:
        return bool(
            self.xp
            or self.lessons_completed
            or self.projects_completed
            or self.levels_gained
            or self.active_days
        )

    def as_dict(self) -> dict:
        return {
            "week_start": self.week_start,
            "xp": self.xp,
            "lessons_completed": self.lessons_completed,
            "projects_completed": self.projects_completed,
            "levels_gained": self.levels_gained,
            "active_days": self.active_days,
            "has_activity": self.has_activity,
        }


async def compute_weekly_stats(
    db: AsyncSession,
    user: User,
    profile: StudentProfile,
    *,
    now_utc: Optional[datetime] = None,
) -> WeeklyStats:
    """Aggregate this week's real activity for one student."""
    moment = now_utc or datetime.utcnow()
    offset = clamp_timezone_offset(getattr(user, "timezone_offset_minutes", 0))
    start = week_start_utc(moment, offset)

    attempts = (
        await db.execute(
            select(ExerciseAttempt.xp_earned, ExerciseAttempt.created_at).where(
                ExerciseAttempt.user_id == user.id,
                ExerciseAttempt.created_at >= start,
            )
        )
    ).all()
    exercise_xp = sum((row[0] or 0) for row in attempts)

    completed_lessons = (
        await db.execute(
            select(LessonProgress.completed_at).where(
                LessonProgress.user_id == user.id,
                LessonProgress.status == MissionStatusEnum.completed,
                LessonProgress.completed_at.is_not(None),
                LessonProgress.completed_at >= start,
            )
        )
    ).scalars().all()

    completed_projects = (
        await db.execute(
            select(ProjectProgress.xp_earned, ProjectProgress.completed_at).where(
                ProjectProgress.user_id == user.id,
                ProjectProgress.status == MissionStatusEnum.completed,
                ProjectProgress.completed_at.is_not(None),
                ProjectProgress.completed_at >= start,
            )
        )
    ).all()
    project_xp = sum((row[0] or 0) for row in completed_projects)

    xp_this_week = exercise_xp + project_xp

    # Levels gained is derived from where the XP total stood before this week,
    # so it can never claim a level the student did not actually cross.
    current_xp = max(profile.xp or 0, 0)
    xp_before_week = max(current_xp - xp_this_week, 0)
    levels_gained = max(level_for_xp(current_xp) - level_for_xp(xp_before_week), 0)

    active_days = _distinct_local_days(
        [row[1] for row in attempts]
        + list(completed_lessons)
        + [row[1] for row in completed_projects],
        offset,
    )

    return WeeklyStats(
        week_start=start,
        xp=xp_this_week,
        lessons_completed=len(completed_lessons),
        projects_completed=len(completed_projects),
        levels_gained=levels_gained,
        active_days=len(active_days),
    )
