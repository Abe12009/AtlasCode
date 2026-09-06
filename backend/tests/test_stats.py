"""Weekly dashboard statistics: new accounts must report zero, not a fabricated
increase, and real activity must move the numbers by exactly the right amount.

See app/services/stats.py for the computation this pins down.
"""

from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from app.services.stats import (
    effective_streak,
    level_for_xp,
    next_streak_value,
    week_start_utc,
)

MCQ_ID = 6


class TestPureHelpers:
    """No DB needed: these are plain functions of their inputs."""

    def test_level_for_xp_starts_at_one(self):
        assert level_for_xp(0) == 1
        assert level_for_xp(-50) == 1

    def test_level_for_xp_advances_every_hundred(self):
        assert level_for_xp(99) == 1
        assert level_for_xp(100) == 2
        assert level_for_xp(250) == 3

    def test_week_start_is_the_local_monday_midnight(self):
        # Wednesday 2024-01-10 15:00 UTC, student in UTC+0.
        now = datetime(2024, 1, 10, 15, 0, 0)
        start = week_start_utc(now, offset_minutes=0)
        assert start == datetime(2024, 1, 8, 0, 0, 0)  # Monday

    def test_week_start_respects_timezone_offset(self):
        # 2024-01-08 01:00 UTC is already Monday morning in UTC+2, but still
        # Sunday night in UTC-3 -- the previous week for that student.
        now = datetime(2024, 1, 8, 1, 0, 0)
        assert week_start_utc(now, offset_minutes=120) == datetime(2024, 1, 8, 0, 0, 0) - timedelta(hours=2)
        assert week_start_utc(now, offset_minutes=-180) == datetime(2024, 1, 1, 0, 0, 0) + timedelta(hours=3)

    def test_streak_unchanged_within_the_same_local_day(self):
        now = datetime(2024, 1, 10, 20, 0, 0)
        last = datetime(2024, 1, 10, 8, 0, 0)
        assert next_streak_value(current_streak=4, last_activity=last, now_utc=now, offset_minutes=0) == 4

    def test_streak_increments_on_the_very_next_day(self):
        now = datetime(2024, 1, 11, 8, 0, 0)
        last = datetime(2024, 1, 10, 22, 0, 0)
        assert next_streak_value(current_streak=4, last_activity=last, now_utc=now, offset_minutes=0) == 5

    def test_streak_resets_after_a_gap(self):
        now = datetime(2024, 1, 15, 8, 0, 0)
        last = datetime(2024, 1, 10, 22, 0, 0)
        assert next_streak_value(current_streak=9, last_activity=last, now_utc=now, offset_minutes=0) == 1

    def test_streak_starts_at_one_with_no_history(self):
        now = datetime(2024, 1, 15, 8, 0, 0)
        assert next_streak_value(current_streak=0, last_activity=None, now_utc=now, offset_minutes=0) == 1

    def test_effective_streak_is_zero_with_no_history(self):
        now = datetime(2024, 1, 15, 8, 0, 0)
        assert effective_streak(stored_streak=5, last_activity=None, now_utc=now, offset_minutes=0) == 0

    def test_effective_streak_survives_until_tomorrow(self):
        now = datetime(2024, 1, 11, 8, 0, 0)
        last = datetime(2024, 1, 10, 22, 0, 0)
        assert effective_streak(stored_streak=5, last_activity=last, now_utc=now, offset_minutes=0) == 5

    def test_effective_streak_breaks_after_missing_a_day(self):
        now = datetime(2024, 1, 12, 8, 0, 0)
        last = datetime(2024, 1, 10, 22, 0, 0)
        assert effective_streak(stored_streak=5, last_activity=last, now_utc=now, offset_minutes=0) == 0


class TestDashboardWeeklyStats:
    """End to end: a brand-new account must never show a fake weekly delta."""

    async def test_new_account_has_zero_weekly_stats(self, client: AsyncClient, test_user):
        response = await client.get("/dashboard", headers=test_user["headers"])
        assert response.status_code == 200
        weekly = response.json()["weekly"]

        assert weekly["xp"] == 0
        assert weekly["lessons_completed"] == 0
        assert weekly["projects_completed"] == 0
        assert weekly["levels_gained"] == 0
        assert weekly["active_days"] == 0
        assert weekly["has_activity"] is False

    async def test_completing_an_exercise_moves_the_weekly_xp_and_active_days(
        self, client: AsyncClient, test_user, db_session
    ):
        from sqlalchemy import select
        from app.models import ExerciseOption

        options = (
            await db_session.execute(
                select(ExerciseOption).where(ExerciseOption.exercise_id == MCQ_ID)
            )
        ).scalars().all()
        correct = next(o for o in options if o.is_correct)

        before = (await client.get("/dashboard", headers=test_user["headers"])).json()["weekly"]
        assert before["has_activity"] is False

        submit = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID, "selected_option_id": correct.id},
        )
        assert submit.status_code == 200
        awarded_xp = submit.json()["xp_earned"]
        assert awarded_xp > 0

        after = (await client.get("/dashboard", headers=test_user["headers"])).json()["weekly"]
        assert after["xp"] == awarded_xp
        assert after["active_days"] == 1
        assert after["has_activity"] is True

    async def test_a_wrong_answer_earns_no_xp_even_though_it_counts_as_showing_up(
        self, client: AsyncClient, second_user, db_session
    ):
        """A wrong submission still logs today as an active day (practising
        counts toward a streak whether or not the answer was right), but it
        must never fabricate XP or a completed lesson.
        """
        from sqlalchemy import select
        from app.models import ExerciseOption

        options = (
            await db_session.execute(
                select(ExerciseOption).where(ExerciseOption.exercise_id == MCQ_ID)
            )
        ).scalars().all()
        wrong = next(o for o in options if not o.is_correct)

        await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=second_user["headers"],
            json={"exercise_id": MCQ_ID, "selected_option_id": wrong.id},
        )

        weekly = (await client.get("/dashboard", headers=second_user["headers"])).json()["weekly"]
        assert weekly["xp"] == 0
        assert weekly["lessons_completed"] == 0
        assert weekly["active_days"] == 1
