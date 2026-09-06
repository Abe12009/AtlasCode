"""Curriculum seeding.

``seed_all`` builds a complete curriculum from nothing (used by the test suite
and a fresh install). ``seed_curriculum`` is the idempotent half: it adds any
course that is missing and re-applies the roadmap, without touching a single
existing lesson, exercise or progress row, so it is safe to run against a
database that already has students on it.

Order of operations matters: content first (so every course exists), then the
roadmap (so prerequisites can resolve to real ids).
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.curriculum import ORDER_BY_SLUG
from app.db.session import init_db
from app.models import Course

from .achievements import seed_achievements
from .block_translations import apply_block_translations
from .cs_fundamentals import seed_cs_fundamentals
from .expansions import seed_expansions
from .git_github import seed_git_github
from .projects import seed_projects
from .python_foundations import seed_python_foundations
from .roadmap import apply_roadmap
from .sql_databases import seed_sql_databases
from .stage1_computational_thinking import seed_computational_thinking
from .stage1_foundations import seed_cs_foundations
from .stage2_python_in_depth import seed_python_in_depth
from .stage3_algorithms import seed_algorithms_complexity
from .stage3_mathematics import seed_discrete_mathematics, seed_math_for_cs
from .stage5_software_engineering import seed_software_engineering
from .stage6_security import (
    seed_cybersecurity_foundations,
    seed_network_security,
    seed_secure_development,
)
from .stage7_ai import seed_ai_foundations, seed_ai_literacy, seed_machine_learning
from .stage8_advanced import (
    seed_advanced_computing,
    seed_computer_architecture,
    seed_operating_systems,
)
from .web_fundamentals import seed_web_fundamentals


def get_test_session_maker():
    """A throwaway SQLite engine, used only by ad-hoc scripts that explicitly
    want an isolated local database. The test suite does NOT use this — it
    builds its own session maker against ``test_atlascode.db`` in
    ``tests/conftest.py`` and passes it to ``seed_all`` explicitly.
    """
    test_engine = create_async_engine("sqlite+aiosqlite:///./test_atlascode.db", echo=False)
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


def _order(slug: str) -> int:
    """A course's position in the roadmap, used as its `order` column."""
    return ORDER_BY_SLUG[slug]


#: Courses introduced with the roadmap. Each entry is (seeder, slug); the slug
#: resolves to the position the roadmap assigns it.
NEW_COURSE_SEEDERS = (
    (seed_cs_foundations, "cs-foundations"),
    (seed_computational_thinking, "computational-thinking"),
    (seed_python_in_depth, "python-in-depth"),
    (seed_discrete_mathematics, "discrete-mathematics"),
    (seed_math_for_cs, "math-for-cs"),
    (seed_algorithms_complexity, "algorithms-complexity"),
    (seed_software_engineering, "software-engineering"),
    (seed_cybersecurity_foundations, "cybersecurity-foundations"),
    (seed_network_security, "network-security-fundamentals"),
    (seed_secure_development, "secure-software-development"),
    (seed_ai_foundations, "ai-foundations"),
    (seed_machine_learning, "machine-learning-fundamentals"),
    (seed_ai_literacy, "ai-literacy"),
    (seed_operating_systems, "operating-systems"),
    (seed_computer_architecture, "computer-architecture"),
    (seed_advanced_computing, "advanced-computing"),
)


async def seed_curriculum(db: AsyncSession, *, verbose: bool = True) -> None:
    """Add anything missing and align the roadmap. Never destructive.

    Every seeder is keyed on a unique slug and skips what already exists, so
    this converges: running it on a fully seeded database is a no-op, and
    running it on a partially seeded one fills only the gaps.
    """
    for seeder, slug in NEW_COURSE_SEEDERS:
        await seeder(db, _order(slug))

    await seed_expansions(db)
    await seed_achievements(db)

    changed = await apply_roadmap(db, verbose=verbose)
    await db.commit()
    if verbose:
        print(f"Roadmap applied ({changed} course rows aligned).")


async def seed_all(session_maker=None):
    """Build the whole curriculum. Skips work that is already present.

    With no argument this seeds whatever database the app is actually
    configured for (``DATABASE_URL`` — SQLite locally, PostgreSQL in
    production), via the same session maker the running app uses. Pass an
    explicit ``session_maker`` to target a different database (the test suite
    does this to use its own isolated SQLite file).
    """
    if session_maker is None:
        from app.db.session import async_session_maker

        session_maker = async_session_maker

    async with session_maker() as db:
        result = await db.execute(select(Course))
        already_seeded = result.scalars().first() is not None

        if not already_seeded:
            print("Seeding database...")
            # The original five courses, unchanged.
            await seed_python_foundations(db)
            await seed_web_fundamentals(db)
            await seed_sql_databases(db)
            await seed_git_github(db)
            await seed_cs_fundamentals(db)
            await seed_projects(db)

            # Courses 1-5 define their blocks without translations; courses 6+
            # ship them inline. This fills the gap so every seeded database has
            # en/fr/ar block bodies.
            await apply_block_translations(db)
            await db.commit()

        await seed_curriculum(db, verbose=not already_seeded)
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(seed_all())
