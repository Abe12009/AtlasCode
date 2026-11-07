"""Sequential lesson unlocking, computed entirely from existing rows.

A gated course is walked in order: a lesson opens once the one before it is
completed. Nothing is stored for this -- no column, no migration, no
bookkeeping row. The whole state is derived from the LessonProgress rows the
user already has, which is what makes it safe to turn on for accounts that
predate it (see `ceiling` below).

Scope is deliberately narrow. `Course.prerequisite_course_id` and
`RoadmapEntry.prerequisite_slug` stay advisory -- any course can be started
at any time -- and only the sequence *inside* a course is enforced, for
courses whose RoadmapEntry says `gated=True`.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.curriculum import ROADMAP_BY_SLUG
from app.models import Course, Lesson, LessonProgress, MissionStatusEnum, Module


def _slug_is_gated(slug: str | None) -> bool:
    """Whether lesson order is enforced for this course slug.

    Fail-open on an unknown slug: a course that isn't on the roadmap yet (or
    one a test fabricates) must not become unreachable because of a lookup
    miss. `TestEverySeededCourseIsOnTheRoadmap` is what keeps that from
    quietly swallowing a real course.
    """
    entry = ROADMAP_BY_SLUG.get(slug or "")
    return bool(entry and entry.gated)


async def _course_sequences(
    db: AsyncSession, course_ids: list[int]
) -> dict[int, list[int]]:
    """Each course's lesson ids in curriculum order, index 0..N-1.

    `Lesson.id` is the final tie-break so a sequence is stable even if two
    modules or two lessons share an `order` -- without it, equal-order rows
    come back in whatever order the database feels like, and a lesson's index
    (hence whether it is locked) could change between two requests.
    """
    result = await db.execute(
        select(Lesson.id, Module.course_id)
        .join(Module, Lesson.module_id == Module.id)
        .where(Module.course_id.in_(course_ids))
        .order_by(Module.course_id, Module.order, Lesson.order, Lesson.id)
    )
    sequences: dict[int, list[int]] = {course_id: [] for course_id in course_ids}
    for lesson_id, course_id in result.all():
        sequences[course_id].append(lesson_id)
    return sequences


def _ceiling(sequence: list[int], completed_ids: set[int], any_row_ids: set[int]) -> int:
    """Highest index this user has unlocked, from their rows alone.

    max(last completed + 1, last touched). The first term is the actual
    progression rule: finish lesson n and n+1 opens. The second is what makes
    this safe to switch on retroactively -- any lesson the user already has a
    row for stays reachable, whatever its status, so nobody loses access to a
    lesson they were midway through.

    Note the second term is `last touched`, not `last touched + 1`: merely
    opening or starting a lesson must not open the next one, or the gate would
    unlock the whole course one request at a time. Starting lesson n puts the
    ceiling at exactly n, which keeps n reachable and leaves n+1 shut until n
    is actually completed.

    -1 when the user has no rows at all; callers clamp with max(ceiling, 0) so
    the first lesson is always reachable.
    """
    last_completed = max(
        (i for i, lesson_id in enumerate(sequence) if lesson_id in completed_ids),
        default=-1,
    )
    last_touched = max(
        (i for i, lesson_id in enumerate(sequence) if lesson_id in any_row_ids),
        default=-1,
    )
    return max(last_completed + 1, last_touched)


async def unlocked_lesson_ids_for_courses(
    db: AsyncSession, user_id: int, course_ids: list[int]
) -> dict[int, set[int]]:
    """Every lesson id the user may open, per course.

    Three queries regardless of how many courses or lessons are involved, so
    the course-list endpoint stays flat rather than fanning out into one check
    per lesson (140 of them, at the current curriculum size).
    """
    course_ids = list(dict.fromkeys(course_ids))
    if not course_ids:
        return {}

    slug_result = await db.execute(
        select(Course.id, Course.slug).where(Course.id.in_(course_ids))
    )
    gated = {
        course_id: _slug_is_gated(slug) for course_id, slug in slug_result.all()
    }

    sequences = await _course_sequences(db, course_ids)

    gated_lesson_ids = [
        lesson_id
        for course_id, sequence in sequences.items()
        if gated.get(course_id)
        for lesson_id in sequence
    ]
    rows = []
    if gated_lesson_ids:
        rows_result = await db.execute(
            select(LessonProgress.lesson_id, LessonProgress.status).where(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id.in_(gated_lesson_ids),
            )
        )
        rows = rows_result.all()
    any_row_ids = {lesson_id for lesson_id, _ in rows}
    completed_ids = {
        lesson_id for lesson_id, status in rows if status == MissionStatusEnum.completed
    }

    unlocked: dict[int, set[int]] = {}
    for course_id, sequence in sequences.items():
        if not gated.get(course_id):
            unlocked[course_id] = set(sequence)
            continue
        ceiling = max(_ceiling(sequence, completed_ids, any_row_ids), 0)
        unlocked[course_id] = {
            lesson_id for i, lesson_id in enumerate(sequence) if i <= ceiling
        }
    return unlocked


async def unlocked_lesson_ids(db: AsyncSession, user_id: int, course_id: int) -> set[int]:
    """Every lesson id in this one course the user may open."""
    per_course = await unlocked_lesson_ids_for_courses(db, user_id, [course_id])
    return per_course.get(course_id, set())


async def is_lesson_unlocked(db: AsyncSession, user_id: int, lesson: Lesson) -> bool:
    """Whether this user may open this one lesson.

    `is_project` lessons are gated like any other: they occupy an index and
    obey the same rule. (Project *missions* -- the separate `projects` table
    reached through /projects -- keep their own prerequisite check in
    app.api.projects; that is a different object, not this.)
    """
    course_id_result = await db.execute(
        select(Module.course_id).where(Module.id == lesson.module_id)
    )
    course_id = course_id_result.scalar_one_or_none()
    if course_id is None:
        # A lesson with no reachable course has no sequence to sit in, so
        # there is nothing to enforce -- fail open, same as an unknown slug.
        return True

    return lesson.id in await unlocked_lesson_ids(db, user_id, course_id)
