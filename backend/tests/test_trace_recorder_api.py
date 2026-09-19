import json

from httpx import AsyncClient
from sqlalchemy import select

from app.models import Exercise
from app.services.trace_recorder import record_trace, trace_to_json

# Exercise 49 is the seeded debugging exercise (broken binary_search) in
# lesson 38, "Searching Algorithms" -- see migrations/add_break_the_code_lesson_38.py.
BUGGY_DEBUGGING_EXERCISE_ID = 49
# Exercise 3 is a prediction exercise whose validation_config holds a real
# expected_output answer -- it must never come back as `trace`.
NON_DEBUGGING_EXERCISE_ID = 3


class TestTraceExposedOverApi:
    """The lesson payload's ExerciseResponse.trace field -- populated only
    for a debugging exercise whose validation_config actually carries one,
    and validation_config itself (the answer key for other exercise types)
    must never be present in the response regardless."""

    async def test_debugging_exercise_with_a_trace_exposes_it(
        self, client: AsyncClient, test_user, db_session
    ):
        exercise = (
            await db_session.execute(select(Exercise).where(Exercise.id == BUGGY_DEBUGGING_EXERCISE_ID))
        ).scalar_one()
        assert exercise.exercise_type.value == "debugging"

        result = record_trace(exercise.starter_code, "binary_search([1, 3, 5, 7, 9], 5)")
        assert result.is_valid
        exercise.validation_config = json.dumps({"trace": trace_to_json(result)})
        await db_session.commit()

        lesson = (
            await client.get(f"/lessons/{exercise.lesson_id}", headers=test_user["headers"])
        ).json()
        item = next(e for e in lesson["exercises"] if e["id"] == BUGGY_DEBUGGING_EXERCISE_ID)

        assert item["trace"] is not None
        assert len(item["trace"]) == len(result.steps)
        assert item["trace"][0]["line"] == result.steps[0].line
        assert "validation_config" not in item
        assert "solution_code" not in item
        assert "test_code" not in item

    async def test_non_debugging_exercise_never_exposes_a_trace(
        self, client: AsyncClient, test_user, db_session
    ):
        exercise = (
            await db_session.execute(select(Exercise).where(Exercise.id == NON_DEBUGGING_EXERCISE_ID))
        ).scalar_one()
        assert exercise.exercise_type.value != "debugging"

        lesson = (
            await client.get(f"/lessons/{exercise.lesson_id}", headers=test_user["headers"])
        ).json()
        item = next(e for e in lesson["exercises"] if e["id"] == NON_DEBUGGING_EXERCISE_ID)

        # Not just null -- the key must be absent entirely. A present-but-null
        # "trace" would still advertise the field's existence for an exercise
        # type it was never meant to apply to.
        assert "trace" not in item
        assert "validation_config" not in item
