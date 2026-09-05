from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.models import (
    Course, CourseTranslation, Module, ModuleTranslation,
    Lesson, LessonTranslation, LessonBlock, LessonBlockTranslation,
    Exercise, ExerciseTranslation, ExerciseOption, ExerciseOptionTranslation,
    Project, ProjectTranslation, ProjectTask, ProjectTaskTranslation,
    Achievement, AchievementTranslation,
    LanguageEnum, DifficultyEnum, ExerciseTypeEnum, MissionStatusEnum
)


async def course_exists(db: AsyncSession, slug: str) -> bool:
    result = await db.execute(select(Course).where(Course.slug == slug))
    return result.scalar_one_or_none() is not None


async def module_exists(db: AsyncSession, course_id: int, slug: str) -> bool:
    result = await db.execute(select(Module).where(Module.course_id == course_id, Module.slug == slug))
    return result.scalar_one_or_none() is not None


async def lesson_exists(db: AsyncSession, module_id: int, slug: str) -> bool:
    result = await db.execute(select(Lesson).where(Lesson.module_id == module_id, Lesson.slug == slug))
    return result.scalar_one_or_none() is not None


async def get_or_create_course(db: AsyncSession, slug: str, order: int, translations: list) -> int:
    result = await db.execute(select(Course).where(Course.slug == slug))
    course = result.scalar_one_or_none()
    if course:
        return course.id
    
    course = Course(slug=slug, order=order)
    db.add(course)
    await db.flush()
    
    for t in translations:
        db.add(CourseTranslation(
            course_id=course.id,
            language=t["language"],
            title=t["title"],
            description=t["description"],
            skills=t.get("skills", "")
        ))
    await db.flush()
    return course.id


async def get_or_create_module(db: AsyncSession, course_id: int, slug: str, order: int, translations: list) -> int:
    result = await db.execute(select(Module).where(Module.course_id == course_id, Module.slug == slug))
    module = result.scalar_one_or_none()
    if module:
        return module.id
    
    module = Module(course_id=course_id, slug=slug, order=order)
    db.add(module)
    await db.flush()
    
    for t in translations:
        db.add(ModuleTranslation(
            module_id=module.id,
            language=t["language"],
            title=t["title"],
            description=t.get("description", "")
        ))
    await db.flush()
    return module.id


async def get_or_create_lesson(db: AsyncSession, module_id: int, slug: str, order: int,
                               difficulty: DifficultyEnum, estimated_minutes: int, xp_reward: int,
                               translations: list, blocks: list, exercises: list) -> int:
    result = await db.execute(select(Lesson).where(Lesson.module_id == module_id, Lesson.slug == slug))
    lesson = result.scalar_one_or_none()
    if lesson:
        return lesson.id
    
    lesson = Lesson(
        module_id=module_id,
        slug=slug,
        order=order,
        difficulty=difficulty,
        estimated_minutes=estimated_minutes,
        xp_reward=xp_reward
    )
    db.add(lesson)
    await db.flush()
    
    for t in translations:
        db.add(LessonTranslation(
            lesson_id=lesson.id,
            language=t["language"],
            title=t["title"],
            story=t.get("story", ""),
            objective=t.get("objective", ""),
            skills=t.get("skills", "")
        ))
    await db.flush()
    
    for i, block in enumerate(blocks):
        lesson_block = LessonBlock(
            lesson_id=lesson.id,
            block_type=block["type"],
            order=block.get("order", i + 1),
            content=block["content"],
            code_example=block.get("code_example"),
            config=block.get("config"),
        )
        db.add(lesson_block)
        await db.flush()
        
        for t in block.get("translations", []):
            db.add(LessonBlockTranslation(
                block_id=lesson_block.id,
                language=t["language"],
                content=t["content"],
                code_example=t.get("code_example")
            ))
    await db.flush()
    
    for ex in exercises:
        exercise = Exercise(
            lesson_id=lesson.id,
            exercise_type=ex["type"],
            order=ex["order"],
            xp_reward=ex.get("xp_reward", 10),
            starter_code=ex.get("starter_code"),
            solution_code=ex.get("solution_code"),
            test_code=ex.get("test_code"),
            validation_config=ex.get("validation_config")
        )
        db.add(exercise)
        await db.flush()
        
        for t in ex.get("translations", []):
            db.add(ExerciseTranslation(
                exercise_id=exercise.id,
                language=t["language"],
                prompt=t["prompt"],
                hint=t.get("hint"),
                explanation=t.get("explanation")
            ))
        await db.flush()
        
        for opt in ex.get("options", []):
            option = ExerciseOption(
                exercise_id=exercise.id,
                order=opt["order"],
                is_correct=opt["is_correct"]
            )
            db.add(option)
            await db.flush()
            
            for t in opt.get("translations", []):
                db.add(ExerciseOptionTranslation(
                    option_id=option.id,
                    language=t["language"],
                    text=t["text"]
                ))
        await db.flush()
    
    return lesson.id


def get_test_session_maker():
    test_engine = create_async_engine("sqlite+aiosqlite:///./test_atlascode.db", echo=False)
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)