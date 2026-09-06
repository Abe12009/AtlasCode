"""Apply the curriculum roadmap to whatever courses exist.

Separate from content seeding on purpose: the roadmap describes *placement*
(stage, order, prerequisite, difficulty, icon), and placement has to be
refreshed for courses that were seeded long before the roadmap existed. Running
this never creates, deletes or edits a lesson — it only writes the handful of
metadata columns on ``courses``.

Safe to run repeatedly: it is a convergence step, not an insert.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.curriculum import ORDER_BY_SLUG, ROADMAP, ROADMAP_BY_SLUG
from app.models import Course, DifficultyEnum


async def apply_roadmap(db: AsyncSession, *, verbose: bool = False) -> int:
    """Align every known course with its roadmap entry. Returns rows changed."""
    result = await db.execute(select(Course))
    courses = {course.slug: course for course in result.scalars().all()}

    # Resolve prerequisite slugs to ids first so ordering within one pass does
    # not matter. A prerequisite that is not seeded yet simply stays null.
    id_by_slug = {slug: course.id for slug, course in courses.items()}

    changed = 0
    for entry in ROADMAP:
        course = courses.get(entry.slug)
        if course is None:
            continue

        desired = {
            "order": ORDER_BY_SLUG[entry.slug],
            "stage": entry.stage,
            "track": entry.track,
            "icon": entry.icon,
            "difficulty": DifficultyEnum(entry.difficulty),
            "estimated_hours": entry.estimated_hours,
            "prerequisite_course_id": id_by_slug.get(entry.prerequisite_slug or ""),
        }

        dirty = False
        for attribute, value in desired.items():
            if getattr(course, attribute) != value:
                setattr(course, attribute, value)
                dirty = True
        if dirty:
            changed += 1
            if verbose:
                print(f"  roadmap: {entry.slug} -> stage {entry.stage}, order {desired['order']}")

    # Anything not in the roadmap keeps its content but is parked at the end so
    # it can never appear before the foundations.
    unplaced = [c for slug, c in courses.items() if slug not in ROADMAP_BY_SLUG]
    for offset, course in enumerate(sorted(unplaced, key=lambda c: c.order), start=1):
        target = len(ORDER_BY_SLUG) + offset
        if course.order != target:
            course.order = target
            changed += 1

    return changed
