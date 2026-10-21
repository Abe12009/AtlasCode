import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.models import Lesson, LessonProgress, MissionStatusEnum, User


class TestLessons:
    async def test_get_lesson_detail(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        assert response.status_code == 200
        lesson = response.json()
        assert lesson["id"] == 1
        assert "blocks" in lesson
        assert "exercises" in lesson
        assert "translations" in lesson
        assert len(lesson["blocks"]) > 0
        assert len(lesson["exercises"]) > 0

    async def test_lesson_detail_carries_breadcrumb_course_and_module_titles(
        self, client: AsyncClient, test_user
    ):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        assert response.status_code == 200
        lesson = response.json()
        assert lesson["course_title"]
        assert lesson["course_id"]
        assert lesson["module_title"]

    async def test_lesson_breadcrumb_titles_follow_the_requested_language(
        self, client: AsyncClient, test_user
    ):
        en = (await client.get("/lessons/1?language=en", headers=test_user["headers"])).json()
        fr = (await client.get("/lessons/1?language=fr", headers=test_user["headers"])).json()
        assert en["course_title"] != fr["course_title"]

    async def test_lesson_blocks_render(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        lesson = response.json()
        
        block_types = {b["block_type"] for b in lesson["blocks"]}
        assert "text" in block_types or "code" in block_types
        
        for block in lesson["blocks"]:
            assert "id" in block
            assert "block_type" in block
            assert "order" in block

    async def test_lesson_exercises_render(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        lesson = response.json()
        
        for exercise in lesson["exercises"]:
            assert "id" in exercise
            assert "exercise_type" in exercise
            assert "order" in exercise
            assert "xp_reward" in exercise
            assert "translations" in exercise
            assert len(exercise["translations"]) > 0

    async def test_lesson_progress(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1/progress", headers=test_user["headers"])
        assert response.status_code == 200
        progress = response.json()
        assert progress["lesson_id"] == 1
        assert "status" in progress

    async def test_start_lesson(self, client: AsyncClient, test_user):
        response = await client.post("/lessons/1/start", headers=test_user["headers"])
        assert response.status_code == 200
        progress = response.json()
        assert progress["status"] in ["in_progress", "completed"]

    async def test_concurrent_start_lesson_is_idempotent(
        self, client: AsyncClient, test_user, db_session
    ):
        """Reproduces the race: many simultaneous starts of the same lesson.

        Each request gets its own session, so they genuinely interleave. Before
        the fix the losers raised UNIQUE constraint failed on
        (user_id, lesson_id) and returned 500.
        """
        responses = await asyncio.gather(
            *[client.post("/lessons/2/start", headers=test_user["headers"]) for _ in range(8)]
        )

        assert [r.status_code for r in responses] == [200] * 8, [r.status_code for r in responses]

        # All requests must describe the same single row.
        ids = {r.json()["id"] for r in responses}
        assert len(ids) == 1, ids
        for r in responses:
            assert r.json()["lesson_id"] == 2
            assert r.json()["status"] in ("in_progress", "completed")

        user_result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user_id = user_result.scalar_one().id

        count = await db_session.execute(
            select(func.count())
            .select_from(LessonProgress)
            .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == 2)
        )
        assert count.scalar() == 1

    async def test_concurrent_progress_reads_do_not_duplicate(
        self, client: AsyncClient, test_user, db_session
    ):
        """GET /progress auto-creates a row too, so it has the same race."""
        responses = await asyncio.gather(
            *[client.get("/lessons/3/progress", headers=test_user["headers"]) for _ in range(8)]
        )

        assert [r.status_code for r in responses] == [200] * 8, [r.status_code for r in responses]
        assert len({r.json()["id"] for r in responses}) == 1

        user_result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user_id = user_result.scalar_one().id

        count = await db_session.execute(
            select(func.count())
            .select_from(LessonProgress)
            .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == 3)
        )
        assert count.scalar() == 1

    async def test_start_lesson_does_not_overwrite_existing_progress(
        self, client: AsyncClient, test_user, db_session
    ):
        """Restarting a lesson must preserve earned XP, position and completion."""
        first = await client.post("/lessons/4/start", headers=test_user["headers"])
        assert first.status_code == 200
        progress_id = first.json()["id"]

        result = await db_session.execute(
            select(LessonProgress).where(LessonProgress.id == progress_id)
        )
        progress = result.scalar_one()
        progress.status = MissionStatusEnum.completed
        progress.xp_earned = 42
        progress.current_block = 3
        await db_session.commit()

        again = await client.post("/lessons/4/start", headers=test_user["headers"])
        assert again.status_code == 200
        assert again.json()["id"] == progress_id
        assert again.json()["status"] == "completed"
        assert again.json()["xp_earned"] == 42
        assert again.json()["current_block"] == 3

    async def test_unauthenticated_lesson(self, client: AsyncClient):
        response = await client.get("/lessons/1")
        assert response.status_code == 401

    async def test_multiple_lessons_from_different_courses(self, client: AsyncClient, test_user):
        lesson_ids = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45]
        
        for lesson_id in lesson_ids:
            response = await client.get(f"/lessons/{lesson_id}", headers=test_user["headers"])
            if response.status_code == 200:
                lesson = response.json()
                assert "blocks" in lesson
                assert "exercises" in lesson

class TestSubmitCompletesLessonWithoutStart:
    """Submitting an exercise must complete its lesson even if the lesson was
    never explicitly /start-ed.

    Before this, submit looked up the progress row with scalar_one_or_none()
    and skipped the whole completion block when there was none: the exercise
    XP was awarded, but the lesson stayed incomplete with no lesson XP, no
    notification, no course roll-up and no achievement -- and the response was
    still 200, so nothing signalled the half-finish. The web client always
    opens a lesson first, so only a non-first-party caller reached it. See
    lesson_completion_findings.md finding #1.
    """

    @staticmethod
    async def _single_exercise_lesson(db_session):
        """A lesson whose only exercise is option-graded.

        One exercise means one correct submission completes the lesson;
        option-graded means the grader never enters the code sandbox, so the
        test stays fast and deterministic. Discovered by query rather than
        hardcoded so a reseed cannot silently retarget it.
        """
        from app.models import Exercise, ExerciseOption

        rows = await db_session.execute(
            select(Exercise.lesson_id, Exercise.id)
            .where(
                Exercise.lesson_id.in_(
                    select(Exercise.lesson_id)
                    .group_by(Exercise.lesson_id)
                    .having(func.count(Exercise.id) == 1)
                ),
                Exercise.id.in_(
                    select(ExerciseOption.exercise_id).where(ExerciseOption.is_correct.is_(True))
                ),
            )
            .order_by(Exercise.lesson_id)
        )
        pair = rows.first()
        assert pair, "seed should contain a single-exercise, option-graded lesson"
        lesson_id, exercise_id = pair

        option = await db_session.execute(
            select(ExerciseOption.id).where(
                ExerciseOption.exercise_id == exercise_id,
                ExerciseOption.is_correct.is_(True),
            )
        )
        lesson_xp = await db_session.execute(
            select(Lesson.xp_reward).where(Lesson.id == lesson_id)
        )
        return lesson_id, exercise_id, option.scalars().first(), lesson_xp.scalar_one()

    @staticmethod
    async def _lesson_progress(db_session, email, lesson_id):
        user = await db_session.execute(select(User).where(User.email == email))
        user_id = user.scalar_one().id
        row = await db_session.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id == lesson_id,
            )
        )
        return row.scalar_one_or_none()

    async def test_submit_without_start_creates_progress_and_completes_lesson(
        self, client: AsyncClient, test_user, db_session
    ):
        lesson_id, exercise_id, option_id, lesson_xp = await self._single_exercise_lesson(db_session)
        email = test_user["data"]["email"]

        # The precondition that made the old bug possible: no row at all.
        assert await self._lesson_progress(db_session, email, lesson_id) is None

        before = (await client.get("/auth/profile", headers=test_user["headers"])).json()
        response = await client.post(
            f"/exercises/{exercise_id}/submit",
            headers=test_user["headers"],
            json={"exercise_id": exercise_id, "selected_option_id": option_id},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_correct"] is True

        # The row is created, and the lesson is actually completed -- not
        # merely present. expire_all() because the request committed behind
        # this session.
        db_session.expire_all()
        progress = await self._lesson_progress(db_session, email, lesson_id)
        assert progress is not None, "submit should have created the progress row"
        assert progress.status == MissionStatusEnum.completed
        assert progress.completed_at is not None

        # lesson_completed is the flag that was silently false before the fix.
        assert body["lesson_completed"] is True

        # Three distinct sources, asserted as a sum so this test states where
        # every point came from rather than hardcoding a seed-dependent total:
        # the exercise's own reward (the response's xp_earned), the lesson's
        # completion reward (Lesson.xp_reward, credited since the xp_reward
        # fix -- it used to be defined but never awarded), and any achievement
        # the completion unlocked.
        achievement_xp = sum(a["xp_reward"] for a in body["achievements_earned"])
        after = (await client.get("/auth/profile", headers=test_user["headers"])).json()
        assert after["xp"] - before["xp"] == body["xp_earned"] + lesson_xp + achievement_xp
        assert lesson_xp > 0, "the seeded lesson should carry a completion reward"
        assert achievement_xp > 0, "completing a first lesson should unlock an achievement"
        assert after["completed_lessons"] == before["completed_lessons"] + 1

    async def test_submit_after_start_is_unchanged(
        self, client: AsyncClient, test_user, db_session
    ):
        """The path the web client already takes must behave exactly as before."""
        lesson_id, exercise_id, option_id, lesson_xp = await self._single_exercise_lesson(db_session)
        email = test_user["data"]["email"]

        start = await client.post(f"/lessons/{lesson_id}/start", headers=test_user["headers"])
        assert start.status_code == 200
        assert start.json()["status"] == MissionStatusEnum.in_progress.value

        before = (await client.get("/auth/profile", headers=test_user["headers"])).json()
        response = await client.post(
            f"/exercises/{exercise_id}/submit",
            headers=test_user["headers"],
            json={"exercise_id": exercise_id, "selected_option_id": option_id},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is True

        db_session.expire_all()
        progress = await self._lesson_progress(db_session, email, lesson_id)
        assert progress is not None
        assert progress.status == MissionStatusEnum.completed
        after = (await client.get("/auth/profile", headers=test_user["headers"])).json()
        assert after["completed_lessons"] == before["completed_lessons"] + 1

    async def test_auto_create_does_not_double_count_a_resubmission(
        self, client: AsyncClient, test_user, db_session
    ):
        """Submitting the same correct answer twice must not complete twice.

        Auto-create now runs on every correct submission, so previous_success
        is the only thing stopping a second submission from incrementing
        completed_lessons again.
        """
        lesson_id, exercise_id, option_id, lesson_xp = await self._single_exercise_lesson(db_session)
        payload = {"exercise_id": exercise_id, "selected_option_id": option_id}

        first = await client.post(
            f"/exercises/{exercise_id}/submit", headers=test_user["headers"], json=payload
        )
        assert first.status_code == 200
        mid = (await client.get("/auth/profile", headers=test_user["headers"])).json()

        second = await client.post(
            f"/exercises/{exercise_id}/submit", headers=test_user["headers"], json=payload
        )
        assert second.status_code == 200
        assert second.json()["xp_earned"] == 0

        after = (await client.get("/auth/profile", headers=test_user["headers"])).json()
        assert after["xp"] == mid["xp"]
        assert after["completed_lessons"] == mid["completed_lessons"]


    async def test_lesson_reward_is_not_paid_twice_when_the_lesson_re_completes(
        self, client: AsyncClient, test_user, db_session
    ):
        """The completion branch can be re-entered; the reward must not repeat.

        `previous_success` stops a *resubmission* from re-entering the block,
        but it is per-exercise: add a new exercise to an already-completed
        lesson and solve it, and the branch runs again with
        `correct_count >= total_exercises` still true. Without the
        `lesson_already_completed` guard that pays Lesson.xp_reward a second
        time and increments completed_lessons again.
        """
        from app.models import Exercise, ExerciseOption, ExerciseTypeEnum

        lesson_id, exercise_id, option_id, lesson_xp = await self._single_exercise_lesson(
            db_session
        )

        first = await client.post(
            f"/exercises/{exercise_id}/submit",
            headers=test_user["headers"],
            json={"exercise_id": exercise_id, "selected_option_id": option_id},
        )
        assert first.status_code == 200
        assert first.json()["lesson_completed"] is True
        after_first = (await client.get("/auth/profile", headers=test_user["headers"])).json()

        # A second exercise appears in the lesson after it was completed.
        extra = Exercise(
            lesson_id=lesson_id,
            exercise_type=ExerciseTypeEnum.multiple_choice,
            order=99,
            xp_reward=7,
        )
        db_session.add(extra)
        await db_session.flush()
        right = ExerciseOption(exercise_id=extra.id, order=0, is_correct=True)
        db_session.add_all([right, ExerciseOption(exercise_id=extra.id, order=1, is_correct=False)])
        await db_session.commit()

        try:
            second = await client.post(
                f"/exercises/{extra.id}/submit",
                headers=test_user["headers"],
                json={"exercise_id": extra.id, "selected_option_id": right.id},
            )
            assert second.status_code == 200
            body = second.json()
            assert body["is_correct"] is True

            achievement_xp = sum(a["xp_reward"] for a in body["achievements_earned"])
            after_second = (
                await client.get("/auth/profile", headers=test_user["headers"])
            ).json()

            # Only the new exercise's own reward (plus any achievement it
            # happened to unlock) -- emphatically not another lesson_xp.
            assert after_second["xp"] - after_first["xp"] == body["xp_earned"] + achievement_xp
            assert after_second["xp"] - after_first["xp"] < lesson_xp + body["xp_earned"]
            assert after_second["completed_lessons"] == after_first["completed_lessons"]
        finally:
            # Leave the shared session-scoped seed as it was found.
            await db_session.delete(extra)
            await db_session.commit()

class TestLessonLockIsNotEnforced:
    """Pins the premise behind *not* adding a lock check to submit.

    No code path can put a lesson progress row into locked: the single
    creation site always passes an explicit ready or in_progress, so the
    model default=locked is unreachable, and both GET /lessons/{id} and
    /start clear the status anyway. A lock check on submit would therefore be
    dead code. If lesson gating is ever built, this test should fail and send
    its author to lesson_completion_findings.md finding #2, still open.
    """

    async def test_no_endpoint_produces_a_locked_lesson_progress_row(
        self, client: AsyncClient, test_user, db_session
    ):
        for path in ("/lessons/2/progress", "/lessons/3/progress"):
            assert (await client.get(path, headers=test_user["headers"])).status_code == 200
        assert (
            await client.post("/lessons/2/start", headers=test_user["headers"])
        ).status_code == 200

        user = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user_id = user.scalar_one().id
        db_session.expire_all()
        statuses = await db_session.execute(
            select(LessonProgress.status).where(LessonProgress.user_id == user_id)
        )
        assert MissionStatusEnum.locked not in set(statuses.scalars().all())


class TestMissingLessonIsNotFound:
    """A bogus lesson id must 404, not 500.

    Both endpoints went straight to get_or_create_lesson_progress, which
    inserts a progress row keyed on lesson_id -- a nonexistent lesson tripped
    the foreign key and surfaced as a 500.
    """

    async def test_start_missing_lesson_404(self, client: AsyncClient, test_user):
        response = await client.post("/lessons/999999/start", headers=test_user["headers"])
        assert response.status_code == 404

    async def test_progress_missing_lesson_404(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/999999/progress", headers=test_user["headers"])
        assert response.status_code == 404
