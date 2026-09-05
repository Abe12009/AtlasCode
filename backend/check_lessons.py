import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from app.models import Lesson, Module, Course

async def main():
    test_engine = create_async_engine('sqlite+aiosqlite:///./atlascode.db', echo=False)
    session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_maker() as db:
        from sqlalchemy import select
        lessons = (await db.execute(
            select(Lesson)
            .options(selectinload(Lesson.translations))
            .order_by(Lesson.id)
        )).scalars().all()
        for l in lessons:
            module = (await db.execute(select(Module).where(Module.id == l.module_id))).scalar_one_or_none()
            course = None
            if module:
                course = (await db.execute(select(Course).where(Course.id == module.course_id))).scalar_one_or_none()
            title = l.translations[0].title if l.translations else 'N/A'
            en_title = next((t.title for t in l.translations if t.language.value == 'en'), title)
            print(f'Lesson {l.id}: slug={l.slug}, title={en_title}, module={module.slug if module else "N/A"}, course={course.slug if course else "N/A"}')

asyncio.run(main())