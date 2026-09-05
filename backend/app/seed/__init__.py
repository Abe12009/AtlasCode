import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.db.session import init_db
from app.models import Course
from .base import get_test_session_maker
from .python_foundations import seed_python_foundations
from .web_fundamentals import seed_web_fundamentals
from .sql_databases import seed_sql_databases
from .git_github import seed_git_github
from .cs_fundamentals import seed_cs_fundamentals
from .projects import seed_projects
from .achievements import seed_achievements
from .block_translations import apply_block_translations


def get_test_session_maker():
    test_engine = create_async_engine("sqlite+aiosqlite:///./test_atlascode.db", echo=False)
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def seed_all(session_maker=None):
    if session_maker is None:
        session_maker = get_test_session_maker()
    
    async with session_maker() as db:
        # Check if data already exists
        result = await db.execute(select(Course))
        if result.scalars().first():
            print("Data already exists, skipping seed")
            return

        print("Seeding database...")
        
        # Seed in order
        await seed_python_foundations(db)
        await seed_web_fundamentals(db)
        await seed_sql_databases(db)
        await seed_git_github(db)
        await seed_cs_fundamentals(db)
        await seed_projects(db)
        await seed_achievements(db)

        # Courses 1-5 define their blocks without translations; courses 6-15
        # ship them inline. This fills the gap so every seeded database has
        # en/fr/ar block bodies.
        await apply_block_translations(db)

        await db.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(seed_all())