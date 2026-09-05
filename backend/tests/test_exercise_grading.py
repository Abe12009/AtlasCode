"""Grading regression for every non-code exercise type.

Before this suite existed, any exercise without ``test_code`` awarded full XP
for any Python that merely ran. These tests pin the real contract: the answer
must match the stored expected answer, XP is awarded exactly once, and the
correct answer is never sent to the client before submission.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import (
    Exercise,
    ExerciseOption,
    ExerciseTypeEnum,
    LessonProgress,
    MissionStatusEnum,
)

# Exercise 6 is a multiple_choice exercise in a seeded lesson.
MCQ_ID = 6
# Exercise 3 is a prediction with a stored expected_output.
PREDICTION_ID = 3
# Exercise 1 is a code_writing exercise with real test_code (sandbox path).
CODE_ID = 1


async def options_for(db_session, exercise_id: int):
    result = await db_session.execute(
        select(ExerciseOption)
        .where(ExerciseOption.exercise_id == exercise_id)
        .order_by(ExerciseOption.order)
    )
    return list(result.scalars())


async def correct_option_id(db_session, exercise_id: int) -> int:
    options = await options_for(db_session, exercise_id)
    correct = [o for o in options if o.is_correct]
    assert len(correct) == 1, f"exercise {exercise_id} must have exactly one correct option"
    return correct[0].id


async def wrong_option_id(db_session, exercise_id: int) -> int:
    options = await options_for(db_session, exercise_id)
    wrong = [o for o in options if not o.is_correct]
    assert wrong, f"exercise {exercise_id} must have at least one wrong option"
    return wrong[0].id


async def get_xp(client: AsyncClient, headers: dict) -> int:
    return (await client.get("/dashboard", headers=headers)).json()["profile"]["xp"]


class TestMultipleChoiceGrading:
    async def test_correct_option_is_correct_and_awards_xp(
        self, client: AsyncClient, test_user, db_session
    ):
        option_id = await correct_option_id(db_session, MCQ_ID)
        before = await get_xp(client, test_user["headers"])

        response = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID, "selected_option_id": option_id},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_correct"] is True
        assert body["xp_earned"] > 0
        assert body["is_completed"] is True
        assert await get_xp(client, test_user["headers"]) == before + body["xp_earned"]

    async def test_incorrect_option_awards_no_xp(
        self, client: AsyncClient, test_user, db_session
    ):
        option_id = await wrong_option_id(db_session, MCQ_ID)
        before = await get_xp(client, test_user["headers"])

        response = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID, "selected_option_id": option_id},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_correct"] is False
        assert body["xp_earned"] == 0
        assert body["is_completed"] is False
        assert await get_xp(client, test_user["headers"]) == before

    async def test_running_code_cannot_pass_a_multiple_choice_exercise(
        self, client: AsyncClient, test_user
    ):
        """The old grader passed this: valid Python that simply ran."""
        before = await get_xp(client, test_user["headers"])
        response = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID, "code": "print('anything at all')"},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False
        assert response.json()["xp_earned"] == 0
        assert await get_xp(client, test_user["headers"]) == before

    async def test_invalid_option_id_is_rejected(
        self, client: AsyncClient, test_user, db_session
    ):
        """An option belonging to another exercise must never be accepted."""
        foreign = await db_session.execute(
            select(ExerciseOption).where(ExerciseOption.exercise_id != MCQ_ID).limit(1)
        )
        foreign_id = foreign.scalar_one().id

        response = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID, "selected_option_id": foreign_id},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False
        assert response.json()["xp_earned"] == 0

    async def test_missing_selection_is_not_correct(self, client: AsyncClient, test_user):
        response = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False
        assert response.json()["xp_earned"] == 0

    async def test_duplicate_correct_submission_awards_xp_once(
        self, client: AsyncClient, test_user, db_session
    ):
        option_id = await correct_option_id(db_session, MCQ_ID)
        payload = {"exercise_id": MCQ_ID, "selected_option_id": option_id}
        before = await get_xp(client, test_user["headers"])

        first = (await client.post(f"/exercises/{MCQ_ID}/submit", headers=test_user["headers"], json=payload)).json()
        second = (await client.post(f"/exercises/{MCQ_ID}/submit", headers=test_user["headers"], json=payload)).json()

        assert first["is_correct"] is True and first["xp_earned"] > 0
        assert second["is_correct"] is True
        assert second["xp_earned"] == 0, "XP must be awarded only on the first success"
        assert second["is_completed"] is True
        assert await get_xp(client, test_user["headers"]) == before + first["xp_earned"]

    async def test_unauthenticated_submission_is_rejected(self, client: AsyncClient):
        response = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            json={"exercise_id": MCQ_ID, "selected_option_id": 1},
        )
        assert response.status_code == 401


class TestApiDoesNotLeakAnswers:
    async def test_lesson_payload_never_reveals_the_correct_option(
        self, client: AsyncClient, test_user, db_session
    ):
        exercise = (
            await db_session.execute(select(Exercise).where(Exercise.id == MCQ_ID))
        ).scalar_one()
        lesson = (await client.get(f"/lessons/{exercise.lesson_id}", headers=test_user["headers"])).json()

        mcq = [e for e in lesson["exercises"] if e["exercise_type"] == "multiple_choice"]
        assert mcq, "expected a multiple-choice exercise in this lesson"
        for item in mcq:
            assert item["options"], "options must still be sent so they can be displayed"
            for option in item["options"]:
                assert "is_correct" not in option
            assert "solution_code" not in item
            assert "test_code" not in item
            assert "validation_config" not in item

    async def test_exercise_endpoint_never_reveals_the_correct_option(
        self, client: AsyncClient, test_user
    ):
        exercise = (await client.get(f"/exercises/{MCQ_ID}", headers=test_user["headers"])).json()
        assert exercise["options"]
        for option in exercise["options"]:
            assert "is_correct" not in option
            assert option["translations"], "option text must be translated for display"
        assert "validation_config" not in exercise
        assert "test_code" not in exercise
        assert "solution_code" not in exercise

    async def test_options_are_translated_for_the_requested_language(
        self, client: AsyncClient, test_user
    ):
        # Exercise 11's options are prose, so their text genuinely differs per
        # language (exercise 6's options are Python type names, identical in
        # all three, which would prove nothing here).
        translated_mcq = 11
        seen = {}
        for language in ("en", "fr", "ar"):
            exercise = (
                await client.get(
                    f"/exercises/{translated_mcq}?language={language}",
                    headers=test_user["headers"],
                )
            ).json()
            texts = [o["translations"][0]["text"] for o in exercise["options"]]
            assert all(t.strip() for t in texts)
            for option in exercise["options"]:
                assert len(option["translations"]) == 1, "only the requested language is sent"
                assert option["translations"][0]["language"] == language
            seen[language] = texts
        assert seen["en"] != seen["fr"], seen
        assert seen["en"] != seen["ar"], seen


class TestPredictionGrading:
    async def test_correct_prediction_is_correct(self, client: AsyncClient, test_user, db_session):
        exercise = (
            await db_session.execute(select(Exercise).where(Exercise.id == PREDICTION_ID))
        ).scalar_one()
        assert exercise.exercise_type == ExerciseTypeEnum.prediction

        import json

        expected = json.loads(exercise.validation_config)["expected_output"]
        response = await client.post(
            f"/exercises/{PREDICTION_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": PREDICTION_ID, "answer": expected},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is True
        assert response.json()["xp_earned"] > 0

    async def test_incorrect_prediction_awards_no_xp(self, client: AsyncClient, test_user):
        before = await get_xp(client, test_user["headers"])
        response = await client.post(
            f"/exercises/{PREDICTION_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": PREDICTION_ID, "answer": "definitely not the output"},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False
        assert response.json()["xp_earned"] == 0
        assert await get_xp(client, test_user["headers"]) == before

    async def test_submitting_the_code_instead_of_its_output_is_incorrect(
        self, client: AsyncClient, test_user
    ):
        """This is exactly what the old grader accepted."""
        response = await client.post(
            f"/exercises/{PREDICTION_ID}/submit",
            headers=test_user["headers"],
            json={
                "exercise_id": PREDICTION_ID,
                "code": "print('Line 1')\nprint('Line 2')\nprint('Line 3')",
            },
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False

    async def test_run_is_not_a_shortcut_for_non_code_exercises(
        self, client: AsyncClient, test_user
    ):
        response = await client.post(
            f"/exercises/{PREDICTION_ID}/run",
            headers=test_user["headers"],
            json={"exercise_id": PREDICTION_ID, "code": "print('anything')"},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False
        assert response.json()["xp_earned"] == 0


class TestCodeExercisesStillWork:
    """Task 4: the sandbox path must be untouched."""

    async def test_valid_solution_is_correct_and_awards_xp(self, client: AsyncClient, test_user):
        before = await get_xp(client, test_user["headers"])
        response = await client.post(
            f"/exercises/{CODE_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": CODE_ID, "code": "print('Hello, World!')"},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is True
        assert response.json()["xp_earned"] > 0
        assert await get_xp(client, test_user["headers"]) > before

    async def test_wrong_solution_is_incorrect(self, client: AsyncClient, test_user):
        response = await client.post(
            f"/exercises/{CODE_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": CODE_ID, "code": "print('wrong output entirely')"},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False
        assert response.json()["xp_earned"] == 0

    async def test_syntax_error_fails_cleanly(self, client: AsyncClient, test_user):
        response = await client.post(
            f"/exercises/{CODE_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": CODE_ID, "code": "print('unclosed"},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False
        assert response.json()["error"]

    async def test_forbidden_import_is_still_blocked_by_the_sandbox(
        self, client: AsyncClient, test_user
    ):
        response = await client.post(
            f"/exercises/{CODE_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": CODE_ID, "code": "import os\nprint('Hello, World!')"},
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False

    async def test_resubmitting_a_solved_code_exercise_awards_no_extra_xp(
        self, client: AsyncClient, test_user
    ):
        payload = {"exercise_id": CODE_ID, "code": "print('Hello, World!')"}
        first = (await client.post(f"/exercises/{CODE_ID}/submit", headers=test_user["headers"], json=payload)).json()
        after_first = await get_xp(client, test_user["headers"])
        second = (await client.post(f"/exercises/{CODE_ID}/submit", headers=test_user["headers"], json=payload)).json()

        assert first["xp_earned"] > 0
        assert second["is_correct"] is True
        assert second["xp_earned"] == 0
        assert await get_xp(client, test_user["headers"]) == after_first


class TestLessonCompletionAndNotifications:
    async def test_multiple_choice_completion_completes_the_lesson_and_notifies(
        self, client: AsyncClient, test_user, db_session
    ):
        """A lesson whose exercises are all MCQ must complete like a code lesson."""
        exercise = (
            await db_session.execute(select(Exercise).where(Exercise.id == MCQ_ID))
        ).scalar_one()
        lesson_id = exercise.lesson_id

        all_exercises = list(
            (
                await db_session.execute(select(Exercise).where(Exercise.lesson_id == lesson_id))
            ).scalars()
        )

        await client.post(f"/lessons/{lesson_id}/start", headers=test_user["headers"])

        for item in all_exercises:
            if item.exercise_type == ExerciseTypeEnum.multiple_choice:
                payload = {
                    "exercise_id": item.id,
                    "selected_option_id": await correct_option_id(db_session, item.id),
                }
            else:
                payload = {"exercise_id": item.id, "code": item.solution_code or ""}
            result = await client.post(
                f"/exercises/{item.id}/submit", headers=test_user["headers"], json=payload
            )
            assert result.status_code == 200, result.text
            assert result.json()["is_correct"] is True, (item.id, item.exercise_type, result.text)

        progress = (
            await client.get(f"/lessons/{lesson_id}/progress", headers=test_user["headers"])
        ).json()
        assert progress["status"] == "completed"

        notifications = (
            await client.get("/notifications?limit=50", headers=test_user["headers"])
        ).json()
        types = [n["type"] for n in notifications]
        assert types.count("lesson_completed") == 1, types
        assert types.count("xp_earned") == len(all_exercises), types

    async def test_incorrect_mcq_creates_no_notification(
        self, client: AsyncClient, test_user, db_session
    ):
        before = (await client.get("/notifications?limit=50", headers=test_user["headers"])).json()
        option_id = await wrong_option_id(db_session, MCQ_ID)
        await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID, "selected_option_id": option_id},
        )
        after = (await client.get("/notifications?limit=50", headers=test_user["headers"])).json()
        assert len(after) == len(before)

    async def test_duplicate_mcq_submission_creates_one_xp_notification(
        self, client: AsyncClient, test_user, db_session
    ):
        option_id = await correct_option_id(db_session, MCQ_ID)
        payload = {"exercise_id": MCQ_ID, "selected_option_id": option_id}
        await client.post(f"/exercises/{MCQ_ID}/submit", headers=test_user["headers"], json=payload)
        await client.post(f"/exercises/{MCQ_ID}/submit", headers=test_user["headers"], json=payload)

        notifications = (
            await client.get("/notifications?limit=50", headers=test_user["headers"])
        ).json()
        assert [n["type"] for n in notifications].count("xp_earned") == 1

    async def test_completion_survives_a_new_login(
        self, client: AsyncClient, test_user, db_session
    ):
        option_id = await correct_option_id(db_session, MCQ_ID)
        await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": MCQ_ID, "selected_option_id": option_id},
        )
        xp_before = await get_xp(client, test_user["headers"])

        login = await client.post(
            "/auth/login",
            json={
                "email": test_user["data"]["email"],
                "password": test_user["data"]["password"],
            },
        )
        assert login.status_code == 200
        fresh = {"Authorization": f"Bearer {login.json()['access_token']}"}

        assert await get_xp(client, fresh) == xp_before
        attempts = (await client.get(f"/exercises/{MCQ_ID}/attempts", headers=fresh)).json()
        assert any(a["is_correct"] for a in attempts)


class TestEveryExerciseHasAGradingStrategy:
    async def test_no_exercise_is_ungradable(self, db_session):
        """Task 5's guarantee, enforced as a test against the seeded content."""
        from app.services.exercise_grading import UNGRADABLE, resolve_strategy
        from sqlalchemy.orm import selectinload

        exercises = list(
            (
                await db_session.execute(
                    select(Exercise).options(selectinload(Exercise.options))
                )
            )
            .scalars()
            .unique()
        )
        assert exercises, "seeded database should contain exercises"

        ungradable = [
            (e.id, e.exercise_type.value)
            for e in exercises
            if resolve_strategy(e, e.options) == UNGRADABLE
        ]
        assert ungradable == [], f"exercises with no grading strategy: {ungradable}"

    async def test_every_multiple_choice_has_exactly_one_correct_option(self, db_session):
        from sqlalchemy.orm import selectinload

        exercises = list(
            (
                await db_session.execute(
                    select(Exercise)
                    .options(selectinload(Exercise.options))
                    .where(Exercise.exercise_type == ExerciseTypeEnum.multiple_choice)
                )
            )
            .scalars()
            .unique()
        )
        assert exercises

        broken = [
            (e.id, len(e.options), sum(1 for o in e.options if o.is_correct))
            for e in exercises
            if len(e.options) < 2 or sum(1 for o in e.options if o.is_correct) != 1
        ]
        assert broken == [], f"malformed multiple-choice exercises: {broken}"
