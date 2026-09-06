"""A compact authoring layer for curriculum content.

The original seed modules spell out every translation row by hand, which is
accurate but so verbose that a single lesson runs to fifty lines and mistakes
(a missing Arabic block, an ungradable exercise) are easy to make and hard to
see.

This module gives the curriculum a small declarative vocabulary —
``Course → Module → Lesson → Block/Exercise`` — and makes the invariants the
test-suite enforces true *by construction*:

* every translatable row is written in all three languages, because a
  :class:`T` carries all three or the code will not type-check by eye;
* every exercise is gradable, because each exercise helper fills in the
  ``validation_config`` its grading strategy requires (see
  ``app.services.exercise_grading``);
* seeding stays idempotent, because it reuses the existing
  ``get_or_create_*`` helpers keyed on the same unique slugs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course, DifficultyEnum, ExerciseTypeEnum, LanguageEnum

from .base import get_or_create_course, get_or_create_lesson, get_or_create_module

EN, FR, AR = LanguageEnum.en, LanguageEnum.fr, LanguageEnum.ar


class T(tuple):
    """One string in English, French and Arabic.

    Written as ``T("Loops", "Boucles", "الحلقات")``. Because the three are one
    value, a translation cannot be forgotten while the content is written.
    """

    __slots__ = ()

    def __new__(cls, en: str, fr: str, ar: str):
        return super().__new__(cls, (en, fr, ar))

    @property
    def en(self) -> str:
        return self[0]

    @property
    def fr(self) -> str:
        return self[1]

    @property
    def ar(self) -> str:
        return self[2]

    def rows(self, key: str) -> list[dict]:
        """Translation rows for a single field, e.g. ``title``."""
        return [
            {"language": EN, key: self.en},
            {"language": FR, key: self.fr},
            {"language": AR, key: self.ar},
        ]


def _merge(*parts: list[dict]) -> list[dict]:
    """Merge per-field translation rows into one row per language."""
    merged: dict[LanguageEnum, dict] = {EN: {"language": EN}, FR: {"language": FR}, AR: {"language": AR}}
    for rows in parts:
        for row in rows:
            merged[row["language"]].update(row)
    return [merged[EN], merged[FR], merged[AR]]


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Block:
    """One piece of lesson content, translated into all three languages."""

    block_type: str
    content: T
    #: Code is universal, so it is not translated — the same snippet is stored
    #: for every language.
    code: Optional[str] = None
    config: Optional[dict] = None

    def to_seed(self, order: int) -> dict:
        return {
            "type": self.block_type,
            "order": order,
            "content": self.content.en,
            "code_example": self.code,
            "config": json.dumps(self.config, ensure_ascii=False) if self.config else None,
            "translations": [
                {"language": EN, "content": self.content.en, "code_example": self.code},
                {"language": FR, "content": self.content.fr, "code_example": self.code},
                {"language": AR, "content": self.content.ar, "code_example": self.code},
            ],
        }


def Text(content: T) -> Block:
    """Prose."""
    return Block("text", content)


def Code(caption: T, code: str) -> Block:
    """A worked example: a sentence of framing plus the snippet itself."""
    return Block("code", caption, code=code)


def _localized(value: T) -> dict:
    """Config carries every language inline (see frontend microquest/types.ts)."""
    return {"en": value.en, "fr": value.fr, "ar": value.ar}


def Hook(content: T, challenge: T, learn: Optional[T] = None) -> Block:
    """The opening real-world scenario.

    Rendered as ordinary prose in the standard lesson view, and as the quest
    hook card when the lesson also ships a `blueprint` block. The structured
    half lives in `config` in the shape the frontend's `HookConfig` expects.
    """
    config = {"kind": "hook", "challenge": _localized(challenge)}
    if learn is not None:
        config["learn"] = _localized(learn)
    return Block("hook", content, config=config)


def ExamTip(content: T) -> Block:
    """A short revision note closing the lesson."""
    return Block("exam_tip", content)


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Option:
    text: T
    correct: bool = False

    def to_seed(self, order: int) -> dict:
        return {
            "order": order,
            "is_correct": self.correct,
            "translations": self.text.rows("text"),
        }


@dataclass(frozen=True)
class Exercise:
    exercise_type: ExerciseTypeEnum
    prompt: T
    hint: T
    explanation: T
    xp: int = 10
    options: Sequence[Option] = ()
    starter_code: str = ""
    solution_code: str = ""
    test_code: str = ""
    validation: dict = field(default_factory=dict)

    def to_seed(self, order: int) -> dict:
        return {
            "type": self.exercise_type,
            "order": order,
            "xp_reward": self.xp,
            "starter_code": self.starter_code,
            "solution_code": self.solution_code,
            "test_code": self.test_code,
            "validation_config": json.dumps(self.validation, ensure_ascii=False)
            if self.validation
            else "",
            "translations": _merge(
                self.prompt.rows("prompt"),
                self.hint.rows("hint"),
                self.explanation.rows("explanation"),
            ),
            "options": [option.to_seed(i + 1) for i, option in enumerate(self.options)],
        }


def MCQ(prompt: T, hint: T, explanation: T, options: Sequence[Option], xp: int = 10) -> Exercise:
    """Multiple choice. Exactly one option must be marked correct."""
    correct = [o for o in options if o.correct]
    assert len(correct) == 1, f"MCQ needs exactly one correct option: {prompt.en!r}"
    assert len(options) >= 2, f"MCQ needs at least two options: {prompt.en!r}"
    return Exercise(ExerciseTypeEnum.multiple_choice, prompt, hint, explanation, xp, options)


def Ordering(prompt: T, hint: T, explanation: T, steps: Sequence[T], xp: int = 15) -> Exercise:
    """Put the steps in order. Declaration order *is* the correct order."""
    assert len(steps) >= 2, f"Ordering needs at least two steps: {prompt.en!r}"
    return Exercise(
        ExerciseTypeEnum.ordering,
        prompt,
        hint,
        explanation,
        xp,
        [Option(step) for step in steps],
    )


def Prediction(
    prompt: T, hint: T, explanation: T, code: str, expected_output: str, xp: int = 15
) -> Exercise:
    """"What does this print?" — graded against the exact expected output."""
    return Exercise(
        ExerciseTypeEnum.prediction,
        prompt,
        hint,
        explanation,
        xp,
        starter_code=code,
        solution_code=expected_output,
        validation={"expected_output": expected_output},
    )


def ShortAnswer(
    prompt: T,
    hint: T,
    explanation: T,
    keywords: Sequence,
    reference_answer: str,
    xp: int = 15,
) -> Exercise:
    """A written answer that must mention specific ideas.

    ``keywords`` entries may be lists of interchangeable spellings, e.g.
    ``[["O(log n)", "logarithmic"], "halves"]``.
    """
    assert keywords, f"ShortAnswer needs keywords: {prompt.en!r}"
    return Exercise(
        ExerciseTypeEnum.prediction,
        prompt,
        hint,
        explanation,
        xp,
        starter_code="",
        solution_code=reference_answer,
        validation={"expected_keywords": list(keywords)},
    )


def FillBlank(
    prompt: T, hint: T, explanation: T, snippet: str, answers: Sequence[str], xp: int = 15
) -> Exercise:
    """Fill the ``____`` placeholders in a snippet, left to right."""
    assert answers, f"FillBlank needs answers: {prompt.en!r}"
    return Exercise(
        ExerciseTypeEnum.fill_blank,
        prompt,
        hint,
        explanation,
        xp,
        starter_code=snippet,
        solution_code=" ".join(answers),
        validation={"blanks": [{"answer": a} for a in answers]},
    )


def CodeWriting(
    prompt: T,
    hint: T,
    explanation: T,
    starter_code: str,
    solution_code: str,
    test_code: str,
    xp: int = 20,
) -> Exercise:
    """Write Python that passes real tests in the existing sandbox."""
    assert test_code.strip(), f"CodeWriting needs test_code: {prompt.en!r}"
    return Exercise(
        ExerciseTypeEnum.code_writing,
        prompt,
        hint,
        explanation,
        xp,
        starter_code=starter_code,
        solution_code=solution_code,
        test_code=test_code,
    )


def SQLWriting(
    prompt: T,
    hint: T,
    explanation: T,
    starter_code: str,
    solution_code: str,
    expected_keywords: Sequence,
    xp: int = 15,
) -> Exercise:
    """Write a SQL statement, graded by required fragments rather than the
    Python sandbox — there is no SQL execution engine to run it against, so
    this is the same code_writing + expected_keywords shape the original
    ``app.seed.sql_databases`` lessons already ship (frontend still renders
    the real code editor: ``CODE_EXERCISE_TYPES`` includes ``code_writing``
    regardless of grading strategy)."""
    assert expected_keywords, f"SQLWriting needs expected_keywords: {prompt.en!r}"
    return Exercise(
        ExerciseTypeEnum.code_writing,
        prompt,
        hint,
        explanation,
        xp,
        starter_code=starter_code,
        solution_code=solution_code,
        validation={"expected_keywords": list(expected_keywords)},
    )


def prints(*expected: str) -> str:
    """`test_code` asserting the submitted program printed each fragment.

    The sandbox hands the grader two names: ``code`` (the student's source) and
    ``output`` (what it printed). Checking ``output`` needs neither, so this is
    the cheapest and most robust shape of test.
    """
    checks = " and ".join(f"{fragment!r} in output" for fragment in expected)
    return f"assert {checks}, 'Expected output not found. Got: ' + repr(output)"


def asserts(*statements: str) -> str:
    """`test_code` that re-runs the student's source and then inspects it.

    Use this when the exercise is about what a function *returns* rather than
    what the program prints. The source is executed into the grader's globals,
    so the student's functions and classes are callable by name.
    """
    body = chr(10).join(statements)
    prelude = 'exec(compile(code, "<student>", "exec"), globals())'
    return prelude + chr(10) + body


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Lesson:
    slug: str
    title: T
    story: T
    objective: T
    skills: T
    blocks: Sequence[Block]
    exercises: Sequence[Exercise] = ()
    minutes: int = 30
    xp: int = 50
    difficulty: DifficultyEnum = DifficultyEnum.beginner


@dataclass(frozen=True)
class Module:
    slug: str
    title: T
    description: T
    lessons: Sequence[Lesson]


@dataclass(frozen=True)
class CourseSpec:
    slug: str
    title: T
    description: T
    skills: T
    modules: Sequence[Module]
    #: Roadmap placement — see app.curriculum.
    stage: int = 1
    track: str = "foundations"
    icon: str = "📘"
    difficulty: DifficultyEnum = DifficultyEnum.beginner
    estimated_hours: int = 6
    prerequisite_slug: Optional[str] = None


async def seed_course(db: AsyncSession, spec: CourseSpec, order: int) -> int:
    """Create a course and everything under it, skipping what already exists.

    Returns the course id. Nothing existing is modified here — roadmap metadata
    is applied separately by ``app.seed.roadmap`` so it can also be refreshed
    for courses that predate this module.
    """
    course_id = await get_or_create_course(
        db,
        spec.slug,
        order,
        _merge(
            spec.title.rows("title"),
            spec.description.rows("description"),
            spec.skills.rows("skills"),
        ),
    )

    for module_index, module in enumerate(spec.modules, start=1):
        module_id = await get_or_create_module(
            db,
            course_id,
            module.slug,
            module_index,
            _merge(module.title.rows("title"), module.description.rows("description")),
        )

        for lesson_index, lesson in enumerate(module.lessons, start=1):
            await get_or_create_lesson(
                db,
                module_id,
                lesson.slug,
                lesson_index,
                lesson.difficulty,
                lesson.minutes,
                lesson.xp,
                _merge(
                    lesson.title.rows("title"),
                    lesson.story.rows("story"),
                    lesson.objective.rows("objective"),
                    lesson.skills.rows("skills"),
                ),
                [block.to_seed(i + 1) for i, block in enumerate(lesson.blocks)],
                [exercise.to_seed(i + 1) for i, exercise in enumerate(lesson.exercises)],
            )

    return course_id


async def course_id_for_slug(db: AsyncSession, slug: str) -> Optional[int]:
    result = await db.execute(select(Course.id).where(Course.slug == slug))
    return result.scalar_one_or_none()
