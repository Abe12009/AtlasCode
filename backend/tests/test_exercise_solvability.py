"""Every exercise must be solvable, and the sandbox must stay closed.

Auditing all 138 exercises by feeding each one its own stored reference answer
found six that no student could ever pass, which silently blocked the lesson
containing them. These tests make that class of defect fail loudly.
"""

import json

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Exercise, ExerciseTypeEnum
from app.services.code_executor import execute_code, validate_python_code
from app.services.exercise_grading import (
    STRATEGY_BLANKS,
    STRATEGY_OPTION,
    STRATEGY_ORDERING,
    grade_exercise,
    resolve_strategy,
)


class Answer:
    """Minimal stand-in for ExerciseSubmitRequest."""

    def __init__(self, **kwargs):
        self.code = kwargs.get("code", "")
        self.answer = kwargs.get("answer")
        self.selected_option_id = kwargs.get("selected_option_id")
        self.ordered_option_ids = kwargs.get("ordered_option_ids")
        self.blanks = kwargs.get("blanks")


def reference_answer(exercise, options, strategy) -> Answer:
    """The answer the curriculum itself says is correct."""
    if strategy == STRATEGY_OPTION:
        return Answer(selected_option_id=next(o.id for o in options if o.is_correct))
    if strategy == STRATEGY_ORDERING:
        return Answer(ordered_option_ids=[o.id for o in sorted(options, key=lambda o: o.order)])
    if strategy == STRATEGY_BLANKS:
        blanks = json.loads(exercise.validation_config)["blanks"]
        return Answer(blanks=[b["answer"] for b in blanks])
    solution = exercise.solution_code or ""
    return Answer(code=solution, answer=solution)


async def all_exercises(db_session):
    result = await db_session.execute(
        select(Exercise).options(selectinload(Exercise.options)).order_by(Exercise.id)
    )
    return list(result.scalars().unique())


class TestEveryExerciseIsSolvable:
    async def test_every_reference_answer_is_accepted(self, db_session):
        """The curriculum's own answer must pass its own grader."""
        exercises = await all_exercises(db_session)
        assert exercises, "seeded database should contain exercises"

        rejected = []
        for exercise in exercises:
            strategy = resolve_strategy(exercise, exercise.options)
            result = grade_exercise(
                exercise, exercise.options, reference_answer(exercise, exercise.options, strategy)
            )
            if not result.is_correct:
                rejected.append((exercise.id, exercise.exercise_type.value, strategy,
                                 (result.error or "")[:60]))

        assert rejected == [], (
            f"{len(rejected)} exercise(s) reject their own reference answer, "
            f"so no student can complete them: {rejected}"
        )

    async def test_a_wrong_answer_is_still_rejected_everywhere(self, db_session):
        """Solvability must not have been bought by accepting anything."""
        exercises = await all_exercises(db_session)
        wrongly_accepted = []
        for exercise in exercises:
            strategy = resolve_strategy(exercise, exercise.options)
            if strategy == STRATEGY_OPTION:
                wrong = [o for o in exercise.options if not o.is_correct]
                answer = Answer(selected_option_id=wrong[0].id)
            elif strategy == STRATEGY_ORDERING:
                ids = [o.id for o in sorted(exercise.options, key=lambda o: o.order)]
                if len(ids) < 2:
                    continue
                answer = Answer(ordered_option_ids=list(reversed(ids)))
            elif strategy == STRATEGY_BLANKS:
                count = len(json.loads(exercise.validation_config)["blanks"])
                answer = Answer(blanks=["definitely-not-the-answer"] * count)
            else:
                junk = "totally unrelated nonsense answer"
                answer = Answer(code=f"print('{junk}')", answer=junk)

            if grade_exercise(exercise, exercise.options, answer).is_correct:
                wrongly_accepted.append((exercise.id, exercise.exercise_type.value, strategy))

        assert wrongly_accepted == [], f"exercises accepting a wrong answer: {wrongly_accepted}"

    async def test_no_exercise_is_ungradable(self, db_session):
        exercises = await all_exercises(db_session)
        ungradable = [
            (e.id, e.exercise_type.value)
            for e in exercises
            if resolve_strategy(e, e.options) == "ungradable"
        ]
        assert ungradable == [], f"exercises with no grading strategy: {ungradable}"

    async def test_every_validation_config_is_valid_json(self, db_session):
        exercises = await all_exercises(db_session)
        broken = []
        for exercise in exercises:
            raw = (exercise.validation_config or "").strip()
            if not raw:
                continue
            try:
                parsed = json.loads(raw)
            except ValueError as exc:
                broken.append((exercise.id, str(exc)))
                continue
            if not isinstance(parsed, dict):
                broken.append((exercise.id, "not a JSON object"))
        assert broken == [], f"malformed validation_config: {broken}"


class TestKeywordAlternatives:
    """A keyword entry may be a list meaning 'any one of these'."""

    def _grade(self, config, answer):
        class Fake:
            exercise_type = ExerciseTypeEnum.code_writing
            test_code = None
            validation_config = json.dumps(config)

        return grade_exercise(Fake(), [], Answer(code=answer, answer=answer)).is_correct

    def test_any_one_alternative_satisfies_the_entry(self):
        config = {"expected_keywords": [["n²", "n^2", "quadratic"]]}
        assert self._grade(config, "the answer is O(n^2)") is True
        assert self._grade(config, "it is quadratic") is True
        assert self._grade(config, "n²") is True

    def test_an_unrelated_answer_still_fails(self):
        config = {"expected_keywords": [["n²", "n^2", "quadratic"]]}
        assert self._grade(config, "it is linear, O(n)") is False

    def test_plain_string_entries_are_all_required(self):
        config = {"expected_keywords": ["SELECT", "FROM students", "WHERE"]}
        assert self._grade(config, "SELECT * FROM students WHERE age > 20") is True
        assert self._grade(config, "SELECT * FROM students") is False

    def test_matching_ignores_case_and_extra_whitespace(self):
        config = {"expected_keywords": ["age >= 20"]}
        assert self._grade(config, "WHERE AGE  >=   20") is True


class TestSandboxRemainsClosed:
    """The sandbox was loosened for OOP builtins; nothing dangerous may pass."""

    @pytest.mark.parametrize(
        "code",
        [
            "import os",
            "from os import system",
            "import subprocess",
            "import socket",
            "import sys",
            "import importlib",
            "import pathlib",
            "open('/etc/passwd')",
            "eval('1+1')",
            "exec('x = 1')",
            "__import__('os')",
            "getattr(__builtins__, 'eval')",
            "print(globals())",
            "print(locals())",
            "print((1).__class__.__bases__)",
            "input('give me input')",
        ],
    )
    def test_dangerous_code_is_rejected(self, code):
        validation = validate_python_code(code)
        if validation.is_valid:
            # Not caught statically; the runtime must still stop it.
            assert execute_code(code).success is False, f"sandbox executed: {code!r}"

    @pytest.mark.parametrize(
        "code,expected",
        [
            ("class T:\n    def __init__(s, c): s._c = c\n    @property\n    def f(s): return s._c * 9 / 5 + 32\nprint(T(25).f)", "77.0"),
            ("class T:\n    @staticmethod\n    def add(a, b): return a + b\nprint(T.add(2, 3))", "5"),
            ("class A:\n    def __init__(s): s.x = 1\nclass B(A):\n    def __init__(s):\n        super().__init__()\nprint(B().x)", "1"),
            ("from collections import deque\nprint(len(deque([1, 2, 3])))", "3"),
            ("import statistics\nprint(statistics.mean([1, 2, 3]))", "2"),
            ("from decimal import Decimal\nprint(Decimal('0.1') + Decimal('0.2'))", "0.3"),
        ],
    )
    def test_legitimate_teaching_code_runs(self, code, expected):
        """These are exactly what lessons 121, 124, 127 and the DSA course teach."""
        result = execute_code(code)
        assert result.success is True, result.error
        assert expected in result.output
