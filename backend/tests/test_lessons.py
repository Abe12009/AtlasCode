import asyncio
import random
from dataclasses import replace

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.curriculum import ROADMAP_BY_SLUG
from app.models import Course, Lesson, LessonProgress, MissionStatusEnum, Module, User
from app.services.lesson_gating import unlocked_lesson_ids


class TestLessons:
    @pytest.fixture(autouse=True)
    async def _unlock_lessons(self, test_user, unlock_course):
        """Lesson gating locks everything past the first lesson of a course.

        These tests predate app.services.lesson_gating and address lessons and
        exercises by hard-coded id, several courses deep. Grant them the same
        grandfathered access a pre-existing account gets -- see
        conftest.unlock_course_for -- rather than softening what they assert.
        """
        await unlock_course(test_user)

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

#: The gate is exercised against python-basics throughout: lessons 1..17 in
#: curriculum order, so a lesson id doubles as a readable index (lesson 1 is
#: index 0). Resolved by slug rather than assumed wherever a test needs the
#: whole sequence.
GATED_COURSE_SLUG = "python-basics"


async def _me_id(client, test_user) -> int:
    return (await client.get("/auth/me", headers=test_user["headers"])).json()["id"]


async def _sequence(db_session, slug=GATED_COURSE_SLUG) -> list[int]:
    """Lesson ids of `slug`, in the same order the gate indexes them."""
    result = await db_session.execute(
        select(Lesson.id)
        .join(Module, Lesson.module_id == Module.id)
        .join(Course, Module.course_id == Course.id)
        .where(Course.slug == slug)
        .order_by(Module.order, Lesson.order, Lesson.id)
    )
    return list(result.scalars().all())


async def _set_rows(db_session, user_id, pairs):
    """Make this user's progress rows be exactly `pairs` of (lesson_id, status)."""
    await db_session.execute(
        LessonProgress.__table__.delete().where(LessonProgress.user_id == user_id)
    )
    for lesson_id, status in pairs:
        db_session.add(
            LessonProgress(user_id=user_id, lesson_id=lesson_id, status=status)
        )
    await db_session.commit()


class TestLessonLockingIsEnforced:
    """Sequential lesson unlocking, as enforced by app.services.lesson_gating.

    Replaces TestLessonLockIsNotEnforced, which pinned the opposite premise --
    that no lock existed, so a check on submit would be dead code. Its
    docstring told a future author to go read lesson_completion_findings.md
    finding #2 if it ever failed; this class is that finding being closed.

    The rule: index a course's lessons 0..N-1, then
    ceiling = max(last completed + 1, last touched), and lesson i is open when
    i <= max(ceiling, 0). The second term is what grandfathers accounts that
    predate gating. It is `last touched`, not `last touched + 1`, so merely
    opening or starting a lesson never opens the one after it.
    """

    async def test_first_lesson_of_a_course_is_always_open(
        self, client: AsyncClient, test_user
    ):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        assert response.status_code == 200

    async def test_second_lesson_is_forbidden_before_the_first_is_completed(
        self, client: AsyncClient, test_user
    ):
        response = await client.get("/lessons/2", headers=test_user["headers"])
        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()

    async def test_every_gated_endpoint_refuses_a_locked_lesson(
        self, client: AsyncClient, test_user
    ):
        """All five gated routes -- and /run staying open on purpose."""
        headers = test_user["headers"]
        assert (await client.get("/lessons/2", headers=headers)).status_code == 403
        assert (
            await client.get("/lessons/2/progress", headers=headers)
        ).status_code == 403
        assert (await client.post("/lessons/2/start", headers=headers)).status_code == 403
        # Exercise 4 belongs to lesson 2.
        assert (await client.get("/exercises/4", headers=headers)).status_code == 403
        submit = await client.post(
            "/exercises/4/submit",
            headers=headers,
            json={"exercise_id": 4, "answer": "whatever"},
        )
        assert submit.status_code == 403

        # /run is ungated by design: it executes code and awards nothing.
        run = await client.post(
            "/exercises/4/run",
            headers=headers,
            json={"exercise_id": 4, "code": "print(1)"},
        )
        assert run.status_code != 403

    async def test_a_403_creates_no_progress_row(
        self, client: AsyncClient, test_user, db_session
    ):
        """The refusal must land before get_or_create_lesson_progress.

        A progress row is itself an input to the gate, so a 403 that still
        wrote one would be handing out the access it just refused -- and the
        retry at the end of this test would succeed.
        """
        headers = test_user["headers"]
        user_id = await _me_id(client, test_user)

        assert (await client.get("/lessons/2", headers=headers)).status_code == 403
        assert (
            await client.get("/lessons/2/progress", headers=headers)
        ).status_code == 403
        assert (await client.post("/lessons/2/start", headers=headers)).status_code == 403
        assert (await client.get("/exercises/4", headers=headers)).status_code == 403

        db_session.expire_all()
        count = await db_session.execute(
            select(func.count())
            .select_from(LessonProgress)
            .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == 2)
        )
        assert count.scalar() == 0

        assert (await client.get("/lessons/2", headers=headers)).status_code == 403

    async def test_completing_a_lesson_unlocks_the_next_one(
        self, client: AsyncClient, test_user, db_session
    ):
        headers = test_user["headers"]
        user_id = await _me_id(client, test_user)
        assert (await client.get("/lessons/2", headers=headers)).status_code == 403

        await _set_rows(db_session, user_id, [(1, MissionStatusEnum.completed)])

        assert (await client.get("/lessons/2", headers=headers)).status_code == 200
        # The next one, and no further.
        assert (await client.get("/lessons/3", headers=headers)).status_code == 403

    async def test_starting_a_lesson_does_not_unlock_the_next_one(
        self, client: AsyncClient, test_user
    ):
        headers = test_user["headers"]
        assert (await client.post("/lessons/1/start", headers=headers)).status_code == 200
        assert (await client.get("/lessons/2", headers=headers)).status_code == 403

    async def test_opening_a_lesson_does_not_unlock_the_one_after_it(
        self, client: AsyncClient, test_user, db_session
    ):
        headers = test_user["headers"]
        user_id = await _me_id(client, test_user)
        await _set_rows(db_session, user_id, [(1, MissionStatusEnum.completed)])

        # Lesson 2 is open. Opening it, reading its progress and starting it
        # all take a row at index 1 -- none of which may reach lesson 3.
        assert (await client.get("/lessons/2", headers=headers)).status_code == 200
        assert (
            await client.get("/lessons/2/progress", headers=headers)
        ).status_code == 200
        assert (await client.post("/lessons/2/start", headers=headers)).status_code == 200
        assert (await client.get("/lessons/3", headers=headers)).status_code == 403

    async def test_a_pre_existing_progress_row_grandfathers_access(
        self, client: AsyncClient, test_user, db_session
    ):
        """An account already mid-course when gating arrives keeps what it had."""
        headers = test_user["headers"]
        user_id = await _me_id(client, test_user)
        await _set_rows(db_session, user_id, [(10, MissionStatusEnum.ready)])

        for lesson_id in (1, 5, 9, 10):
            assert (
                await client.get(f"/lessons/{lesson_id}", headers=headers)
            ).status_code == 200, lesson_id
        assert (await client.get("/lessons/11", headers=headers)).status_code == 403

    async def test_an_ungated_course_skips_the_check(
        self, client: AsyncClient, test_user, monkeypatch
    ):
        entry = ROADMAP_BY_SLUG[GATED_COURSE_SLUG]
        monkeypatch.setitem(
            ROADMAP_BY_SLUG, GATED_COURSE_SLUG, replace(entry, gated=False)
        )
        response = await client.get("/lessons/12", headers=test_user["headers"])
        assert response.status_code == 200

    async def test_a_course_missing_from_the_roadmap_fails_open(
        self, client: AsyncClient, test_user, monkeypatch
    ):
        """An unknown slug is ungated, so an unplaced course can't be bricked.

        test_every_seeded_course_is_on_the_roadmap_and_gated is what keeps
        this escape hatch from quietly swallowing a real course.
        """
        monkeypatch.delitem(ROADMAP_BY_SLUG, GATED_COURSE_SLUG)
        response = await client.get("/lessons/12", headers=test_user["headers"])
        assert response.status_code == 200

    async def test_a_project_lesson_is_gated_like_any_other(
        self, client: AsyncClient, test_user, db_session
    ):
        """is_project earns no exemption: it occupies an index and obeys the rule.

        Project *missions* -- the separate `projects` table behind /projects --
        keep their own prerequisite check in app.api.projects. Different
        object, different gate.
        """
        module_id = (
            await db_session.execute(
                select(Module.id)
                .join(Course, Module.course_id == Course.id)
                .where(Course.slug == GATED_COURSE_SLUG)
                .order_by(Module.order.desc())
                .limit(1)
            )
        ).scalar_one()

        extra = Lesson(
            module_id=module_id,
            slug="gating-project-probe",
            order=9999,
            is_project=True,
            xp_reward=0,
        )
        db_session.add(extra)
        await db_session.commit()
        await db_session.refresh(extra)
        try:
            sequence = await _sequence(db_session)
            assert sequence[-1] == extra.id, "the probe must sort last"

            response = await client.get(
                f"/lessons/{extra.id}", headers=test_user["headers"]
            )
            assert response.status_code == 403
        finally:
            # Leave the shared session-scoped seed as it was found.
            await db_session.delete(extra)
            await db_session.commit()

    async def test_unlocked_set_matches_the_rule_for_random_completion_sets(
        self, client: AsyncClient, test_user, db_session
    ):
        """Property check: the service agrees with the rule, restated here.

        The expectation is recomputed from the rule rather than by calling the
        gate's own `_ceiling`, so a change to the formula has to be made twice
        before it can pass unnoticed.
        """
        user_id = await _me_id(client, test_user)
        sequence = await _sequence(db_session)
        course_id = (
            await db_session.execute(
                select(Course.id).where(Course.slug == GATED_COURSE_SLUG)
            )
        ).scalar_one()
        all_indexes = list(range(len(sequence)))
        # Several seeds rather than one: a single fixed seed only ever covers
        # the one walk it happens to generate.
        seeds = (20261106, 7, 101, 4242, 99991)

        for seed in seeds:
            rng = random.Random(seed)
            for _trial in range(6):
                completed = set(rng.sample(all_indexes, rng.randint(0, 4)))
                touched = set(rng.sample(all_indexes, rng.randint(0, 4))) | completed

                await _set_rows(
                    db_session,
                    user_id,
                    [
                        (
                            sequence[i],
                            MissionStatusEnum.completed
                            if i in completed
                            else MissionStatusEnum.ready,
                        )
                        for i in sorted(touched)
                    ],
                )

                last_completed = max(completed) if completed else -1
                last_touched = max(touched) if touched else -1
                ceiling = max(max(last_completed + 1, last_touched), 0)
                expected = {
                    lesson_id for i, lesson_id in enumerate(sequence) if i <= ceiling
                }

                actual = await unlocked_lesson_ids(db_session, user_id, course_id)
                assert actual == expected, (
                    seed,
                    sorted(completed),
                    sorted(touched),
                )

        await _set_rows(db_session, user_id, [])

    async def test_every_seeded_course_is_on_the_roadmap_and_gated(self, db_session):
        """Fail-open must never apply to a real course.

        `_slug_is_gated` treats an unknown slug as ungated so a course that
        isn't placed on the roadmap yet can't be made unreachable. That is
        only safe while every seeded course really is on the roadmap -- this
        is the check that stops the escape hatch becoming the behaviour.
        """
        slugs = list((await db_session.execute(select(Course.slug))).scalars().all())
        assert slugs, "no seeded courses"
        missing = [slug for slug in slugs if slug not in ROADMAP_BY_SLUG]
        assert missing == [], f"not on the roadmap, so silently ungated: {missing}"
        ungated = [slug for slug in slugs if not ROADMAP_BY_SLUG[slug].gated]
        assert ungated == [], f"seeded but not gated: {ungated}"


class TestLessonLockingAcrossModulesAndCourses:
    """The sequence is per *course*, so module boundaries are invisible to it.

    A course's lessons are indexed 0..N-1 across all its modules in
    (module.order, lesson.order, lesson.id) order, which means the first
    lesson of module 2 is simply the next index after the last lesson of
    module 1 -- it gets no special treatment, and crossing a module must not
    reset or skip the ceiling.
    """

    async def test_first_lesson_of_the_second_module_waits_for_the_first_module(
        self, client: AsyncClient, test_user, db_session
    ):
        """python-basics: module 1 `getting-started` is lessons 1-5, module 2
        `control-flow` starts at lesson 6."""
        headers = test_user["headers"]
        user_id = await _me_id(client, test_user)

        modules = (
            await db_session.execute(
                select(Module.slug)
                .join(Course, Module.course_id == Course.id)
                .where(Course.slug == GATED_COURSE_SLUG)
                .order_by(Module.order)
            )
        ).scalars().all()
        assert modules[:2] == ["getting-started", "control-flow"], modules

        # Finish module 1 up to but not including its final lesson.
        await _set_rows(
            db_session,
            user_id,
            [(lesson_id, MissionStatusEnum.completed) for lesson_id in (1, 2, 3, 4)],
        )
        # Lesson 5 (last of module 1) is open; lesson 6 (first of module 2) is not.
        assert (await client.get("/lessons/5", headers=headers)).status_code == 200
        assert (await client.get("/lessons/6", headers=headers)).status_code == 403

        # Completing the last lesson of module 1 opens the first of module 2.
        await _set_rows(
            db_session,
            user_id,
            [(lesson_id, MissionStatusEnum.completed) for lesson_id in (1, 2, 3, 4, 5)],
        )
        assert (await client.get("/lessons/6", headers=headers)).status_code == 200
        # And no further: lesson 7 stays shut.
        assert (await client.get("/lessons/7", headers=headers)).status_code == 403

    async def test_a_second_course_walks_start_to_end(
        self, client: AsyncClient, test_user, db_session
    ):
        """Same walk on math-for-cs, which is not python-basics.

        Three lessons across two modules, so it also crosses a module
        boundary -- and its own first lesson is open regardless of how much
        of python-basics the student has done, because gating is per course.
        """
        headers = test_user["headers"]
        user_id = await _me_id(client, test_user)
        sequence = await _sequence(db_session, "math-for-cs")
        assert len(sequence) >= 3, sequence

        await _set_rows(db_session, user_id, [])

        # Nothing done anywhere: the course's own first lesson is open.
        assert (
            await client.get(f"/lessons/{sequence[0]}", headers=headers)
        ).status_code == 200
        assert (
            await client.get(f"/lessons/{sequence[1]}", headers=headers)
        ).status_code == 403

        completed = []
        for i in range(len(sequence) - 1):
            completed.append((sequence[i], MissionStatusEnum.completed))
            await _set_rows(db_session, user_id, completed)
            assert (
                await client.get(f"/lessons/{sequence[i + 1]}", headers=headers)
            ).status_code == 200, sequence[i + 1]

        # Walked to the end: every lesson in the course is now reachable.
        for lesson_id in sequence:
            assert (
                await client.get(f"/lessons/{lesson_id}", headers=headers)
            ).status_code == 200, lesson_id

        await _set_rows(db_session, user_id, [])

    async def test_tied_order_values_sequence_by_lesson_id_and_stay_stable(
        self, client: AsyncClient, test_user, db_session, monkeypatch
    ):
        """Ties in both order columns must resolve by Lesson.id, repeatably.

        `Module.order` and `Lesson.order` are plain `default=0` integers with
        no uniqueness, so a real curriculum can tie. Without Lesson.id as the
        final tie-break the database may return tied rows in any order, and a
        lesson's index -- hence whether it is locked -- could differ between
        two requests. Built as throwaway rows because no seeded course ties.
        """
        from app.curriculum import RoadmapEntry

        slug = "gating-tie-probe"
        course = Course(slug=slug, order=9999, stage=1, track="probe")
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        created = [course]
        try:
            # Two modules sharing one order, each with two lessons sharing one
            # order: every comparison before Lesson.id is a tie.
            lesson_ids = []
            for _ in range(2):
                module = Module(course_id=course.id, slug=f"m{len(created)}", order=1)
                db_session.add(module)
                await db_session.commit()
                await db_session.refresh(module)
                created.append(module)
                for n in range(2):
                    lesson = Lesson(
                        module_id=module.id,
                        slug=f"l{len(created)}-{n}",
                        order=1,
                        xp_reward=0,
                    )
                    db_session.add(lesson)
                    await db_session.commit()
                    await db_session.refresh(lesson)
                    created.append(lesson)
                    lesson_ids.append(lesson.id)

            # The probe course is not on the roadmap, so it would fail open.
            # Register it as gated so the ordering is actually exercised.
            monkeypatch.setitem(
                ROADMAP_BY_SLUG,
                slug,
                RoadmapEntry(slug, 1, "probe", "?", "beginner", 1, None, True),
            )

            user_id = await _me_id(client, test_user)
            await _set_rows(db_session, user_id, [])

            # Deterministic: ties broken by ascending Lesson.id.
            sequence = await _sequence(db_session, slug)
            assert sequence == sorted(lesson_ids), (sequence, sorted(lesson_ids))

            # Stable: repeated calls agree with each other and with the rule.
            first_call = await unlocked_lesson_ids(db_session, user_id, course.id)
            for _ in range(4):
                assert (
                    await unlocked_lesson_ids(db_session, user_id, course.id)
                ) == first_call
            assert first_call == {sorted(lesson_ids)[0]}

            # And the gate agrees over HTTP: lowest id open, next one shut.
            headers = test_user["headers"]
            ordered = sorted(lesson_ids)
            assert (
                await client.get(f"/lessons/{ordered[0]}", headers=headers)
            ).status_code == 200
            assert (
                await client.get(f"/lessons/{ordered[1]}", headers=headers)
            ).status_code == 403
        finally:
            # Leave the shared session-scoped seed as it was found. Children
            # first: Lesson -> Module -> Course.
            await _set_rows(db_session, await _me_id(client, test_user), [])
            for row in reversed(created):
                await db_session.delete(row)
            await db_session.commit()


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
