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
            prereq_lesson = None
            if p.prerequisite_lesson_id:
                prereq_lesson = (await db.execute(
                    select(Lesson)
                    .options(selectinload(Lesson.translations))
                    .where(Lesson.id == p.prerequisite_lesson_id)
                )).scalar_one_or_none()
            title = p.translations[0].title if p.translations else 'N/A'
            en_title = next((t.title for t in p.translations if t.language.value == 'en'), title)
            prereq_title = "None"
            if prereq_lesson and prereq_lesson.translations:
                prereq_title = next((t.title for t in prereq_lesson.translations if t.language.value == 'en'), "Unknown")
            print(f'Project {p.id}: slug={p.slug}, title={en_title}, prereq_lesson_id={p.prerequisite_lesson_id}, prereq_title={prereq_title}')

asyncio.run(main())