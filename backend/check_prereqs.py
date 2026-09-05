import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from app.models import Project, Lesson

async def main():
    test_engine = create_async_engine('sqlite+aiosqlite:///./atlascode.db', echo=False)
    session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_maker() as db:
        from sqlalchemy import select
        projects = (await db.execute(
            select(Project)
            .options(selectinload(Project.translations))
            .order_by(Project.id)
        )).scalars().all()
        for p in projects:
            prereq = None
            if p.prerequisite_lesson_id:
                prereq = (await db.execute(
                    select(Lesson)
                    .options(selectinload(Lesson.translations))
                    .where(Lesson.id == p.prerequisite_lesson_id)
                )).scalar_one_or_none()
            prereq_title = "N/A"
            if prereq and prereq.translations:
                prereq_title = next((t.title for t in prereq.translations if t.language.value == 'en'), "N/A")
            print(f'Project {p.id} ({p.slug}): prereq_lesson_id={p.prerequisite_lesson_id}, prereq_title={prereq_title}')

asyncio.run(main())