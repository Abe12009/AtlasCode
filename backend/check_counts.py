import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from app.models import Lesson, Module, Course, Exercise, Project, Achievement

async def main():
    test_engine = create_async_engine('sqlite+aiosqlite:///./atlascode.db', echo=False)
    session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_maker() as db:
        from sqlalchemy import select, func
        
        courses = (await db.execute(select(Course))).scalars().all()
        modules = (await db.execute(select(Module))).scalars().all()
        lessons = (await db.execute(select(Lesson))).scalars().all()
        exercises = (await db.execute(select(Exercise))).scalars().all()
        projects = (await db.execute(select(Project))).scalars().all()
        achievements = (await db.execute(select(Achievement))).scalars().all()
        
        print(f'Courses: {len(courses)}')
        print(f'Modules: {len(modules)}')
        print(f'Lessons: {len(lessons)}')
        print(f'Exercises: {len(exercises)}')
        print(f'Projects: {len(projects)}')
        print(f'Achievements: {len(achievements)}')

asyncio.run(main())