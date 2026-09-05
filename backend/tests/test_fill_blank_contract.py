"""The documented comparison contract for fill-in-the-blank answers.

The stored answers are inconsistent about quotes, and that inconsistency is in
the data, not a bug in the grader:

  * exercise 5's template is ``student_name = "____"`` -- the quotes are already
    in the snippet, so the student types ``Amine`` -- yet the stored answer is
    ``"Amine"``, with quotes.
  * exercise 26's template is ``colors = {____, "red", ...}`` -- the blank sits
    outside the quotes, so ``"blue"`` with quotes is genuinely correct.

A grader that compared byte-for-byte would fail the correct answer to exercise
5. So one layer of surrounding quotes is stripped from BOTH the expected and
the submitted value. These exercises test tuples, sets and variable assignment,
not quoting style, so the tolerance matches the educational intent rather than
papering over a defect.

The contract, pinned below, is exactly: trim whitespace, strip at most one
matching pair of surrounding quotes, compare case-insensitively. Nothing else
is folded -- the answer itself must be right.
"""

import json

import pytest
from sqlalchemy import select

from app.models import Exercise, ExerciseTypeEnum
from app.services.exercise_grading import grade_exercise


class Answer:
    def __init__(self, blanks=None, code="", answer=None):
        self.blanks = blanks
        self.code = code
        self.answer = answer
        self.selected_option_id = None
        self.ordered_option_ids = None


class FakeFillBlank:
    exercise_type = ExerciseTypeEnum.fill_blank
    test_code = None

    def __init__(self, answers):
        self.validation_config = json.dumps({"blanks": [{"answer": a} for a in answers]})


def grade(answers, submitted):
    return grade_exercise(FakeFillBlank(answers), [], Answer(blanks=submitted)).is_correct


class TestFillBlankComparisonContract:
    def test_exact_match_passes(self):
        assert grade(["Amine", "19"], ["Amine", "19"]) is True

    def test_surrounding_whitespace_is_trimmed(self):
        assert grade(["Amine", "19"], ["  Amine  ", " 19 "]) is True

    def test_comparison_is_case_insensitive(self):
        # Exercise 57 stores "Virtual" capitalised only because it starts a
        # sentence in a comment; "virtual" is the same answer.
        assert grade(["Virtual"], ["virtual"]) is True

    def test_one_layer_of_quotes_is_stripped_from_the_expected_value(self):
        """Exercise 5's stored answer is quoted but its blank is not."""
        assert grade(['"Amine"'], ["Amine"]) is True

    def test_one_layer_of_quotes_is_stripped_from_the_submitted_value(self):
        """Exercise 26's blank is outside the quotes; both spellings are accepted."""
        assert grade(["blue"], ['"blue"']) is True
        assert grade(['"blue"'], ['"blue"']) is True

    def test_single_and_double_quotes_are_treated_alike(self):
        assert grade(['"blue"'], ["'blue'"]) is True

    def test_a_wrong_word_still_fails(self):
        assert grade(['"Amine"', "19"], ["Youssef", "19"]) is False
        assert grade(['"Amine"', "19"], ["Amine", "21"]) is False

    def test_an_empty_answer_fails(self):
        assert grade(["Amine", "19"], ["", ""]) is False

    def test_the_wrong_number_of_blanks_fails(self):
        assert grade(["Amine", "19"], ["Amine"]) is False
        assert grade(["Amine", "19"], ["Amine", "19", "extra"]) is False

    def test_stripping_happens_once_and_does_not_cascade(self):
        """Exactly one quote pair comes off each side, so a doubled quote is
        still a different answer -- the tolerance cannot swallow real content."""
        # Each value is normalised once: '""nested""' -> '"nested"'.
        assert grade(['""nested""'], ['""nested""']) is True
        # ...so it does NOT collapse all the way down to 'nested'.
        assert grade(['""nested""'], ["nested"]) is False
        assert grade(["plain"], ['""plain""']) is False


class TestRealFillBlankExercises:
    async def test_every_stored_answer_set_is_accepted(self, db_session):
        exercises = (
            await db_session.execute(
                select(Exercise).where(Exercise.exercise_type == ExerciseTypeEnum.fill_blank)
            )
        ).scalars().all()
        assert exercises, "expected fill_blank exercises in the seeded database"

        for exercise in exercises:
            answers = [b["answer"] for b in json.loads(exercise.validation_config)["blanks"]]
            result = grade_exercise(exercise, [], Answer(blanks=answers))
            assert result.is_correct, f"exercise {exercise.id} rejects its own answers"

    async def test_unquoted_variants_of_stored_answers_are_also_accepted(self, db_session):
        """This is the tolerance exercise 5 actually depends on."""
        exercises = (
            await db_session.execute(
                select(Exercise).where(Exercise.exercise_type == ExerciseTypeEnum.fill_blank)
            )
        ).scalars().all()

        for exercise in exercises:
            answers = [b["answer"] for b in json.loads(exercise.validation_config)["blanks"]]
            unquoted = [a.strip('"').strip("'") for a in answers]
            result = grade_exercise(exercise, [], Answer(blanks=unquoted))
            assert result.is_correct, f"exercise {exercise.id} rejects the unquoted answers"

    async def test_nonsense_is_rejected_by_every_fill_blank_exercise(self, db_session):
        exercises = (
            await db_session.execute(
                select(Exercise).where(Exercise.exercise_type == ExerciseTypeEnum.fill_blank)
            )
        ).scalars().all()

        for exercise in exercises:
            count = len(json.loads(exercise.validation_config)["blanks"])
            result = grade_exercise(exercise, [], Answer(blanks=["zzz-not-an-answer"] * count))
            assert not result.is_correct, f"exercise {exercise.id} accepted nonsense"
