"""Duel Arena's curated problem pool.

Deliberately NOT "every code_writing exercise" -- a duel problem has to be
fully self-contained (no dependency on a specific lesson's prior blocks or
story context) and have a clear, fast-to-verify correctness check, since two
students are racing against the same test suite. Each entry below was
picked by hand from the existing curriculum, same spirit as Circuit Lab's
and Git Quest's own authored-allowlist content.

Referenced by numeric exercise_id from a from-scratch seed_all() run, which
is deterministic (insertion order is fixed, so the same seed content always
produces the same ids) -- the same trust level backend/tests already places
in fixed ids like test_exercise_grading.py's CODE_ID. If a given id doesn't
exist in this database (e.g. a partially-seeded or hand-edited dev db),
seeding skips it with a warning rather than crashing startup.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DifficultyEnum, DuelProblem, Exercise

#: (exercise_id, difficulty). Each exercise is a plain code_writing exercise
#: with real test_code, picked for being a clean, self-contained problem --
#: see the module docstring.
DUEL_PROBLEMS: tuple[tuple[int, DifficultyEnum], ...] = (
    (14, DifficultyEnum.beginner),       # print the numbers 1 to 10
    (19, DifficultyEnum.beginner),       # def add(a, b)
    (23, DifficultyEnum.intermediate),   # is_even / count_evens
    (86, DifficultyEnum.intermediate),   # initials(full_name)
    (88, DifficultyEnum.intermediate),   # safe_divide with try/except
    (126, DifficultyEnum.advanced),      # reverse_in_place, two-pointer
    (130, DifficultyEnum.advanced),      # fib with memoization
)


async def seed_duel_problems(db: AsyncSession) -> int:
    existing_result = await db.execute(select(DuelProblem.exercise_id))
    existing_exercise_ids = {row[0] for row in existing_result.all()}

    added = 0
    for exercise_id, difficulty in DUEL_PROBLEMS:
        if exercise_id in existing_exercise_ids:
            continue
        exercise = (await db.execute(select(Exercise.id).where(Exercise.id == exercise_id))).scalar_one_or_none()
        if exercise is None:
            print(f"  duel_problems: skipping exercise_id={exercise_id}, not found in this database")
            continue
        db.add(DuelProblem(exercise_id=exercise_id, difficulty=difficulty))
        added += 1

    return added
