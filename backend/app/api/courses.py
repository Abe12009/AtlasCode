from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import (
    Course, Module, Lesson, CourseTranslation, ModuleTranslation, LessonTranslation,
    LessonBlock, LessonBlockTranslation, Exercise, ExerciseTranslation, ExerciseOption,
    ExerciseOptionTranslation, CourseProgress, LessonProgress, StudentProfile,
    MissionStatusEnum
)
from app.schemas import (
    CourseResponse, ModuleResponse, LessonResponse, LessonProgressResponse,
    CourseProgressResponse, LanguageEnum
)

router = APIRouter(prefix="/courses", tags=["courses"])


def _get_language_filter(language: LanguageEnum):
    return language.value


@router.get("", response_model=List[CourseResponse])
async def get_courses(
    language: LanguageEnum = Query(LanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Course).options(
        selectinload(Course.translations),
        selectinload(Course.modules).selectinload(Module.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.blocks).selectinload(LessonBlock.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.exercises).selectinload(Exercise.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.exercises).selectinload(Exercise.options).selectinload(ExerciseOption.translations),
    ).order_by(Course.order)

    result = await db.execute(query)
    courses = result.scalars().unique().all()

    for course in courses:
        course.translations = [t for t in course.translations if t.language == language]
        for module in course.modules:
            module.translations = [t for t in module.translations if t.language == language]
            for lesson in module.lessons:
                lesson.translations = [t for t in lesson.translations if t.language == language]
                lesson.blocks = [b for b in lesson.blocks]
                for block in lesson.blocks:
                    block.translations = [t for t in block.translations if t.language == language]
                lesson.exercises = [e for e in lesson.exercises]
                for exercise in lesson.exercises:
                    exercise.translations = [t for t in exercise.translations if t.language == language]
                    exercise.options = [o for o in exercise.options]
                    for option in exercise.options:
                        option.translations = [t for t in option.translations if t.language == language]

    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    language: LanguageEnum = Query(LanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Course).options(
        selectinload(Course.translations),
        selectinload(Course.modules).selectinload(Module.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.blocks).selectinload(LessonBlock.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.exercises).selectinload(Exercise.translations),
        selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.exercises).selectinload(Exercise.options).selectinload(ExerciseOption.translations),
    ).where(Course.id == course_id)

    result = await db.execute(query)
    course = result.scalars().unique().first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    all_lesson_ids = [lesson.id for module in course.modules for lesson in module.lessons]
    progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id.in_(all_lesson_ids),
        )
    )
    status_by_lesson_id = {p.lesson_id: p.status.value for p in progress_result.scalars().all()}

    course.translations = [t for t in course.translations if t.language == language]
    for module in course.modules:
        module.translations = [t for t in module.translations if t.language == language]
        for lesson in module.lessons:
            lesson.translations = [t for t in lesson.translations if t.language == language]
            lesson.blocks = [b for b in lesson.blocks]
            for block in lesson.blocks:
                block.translations = [t for t in block.translations if t.language == language]
            lesson.exercises = [e for e in lesson.exercises]
            for exercise in lesson.exercises:
                exercise.translations = [t for t in exercise.translations if t.language == language]
                exercise.options = [o for o in exercise.options]
                for option in exercise.options:
                    option.translations = [t for t in option.translations if t.language == language]
            db_status = status_by_lesson_id.get(lesson.id)
            lesson.status = {
                "completed": "completed",
                "in_progress": "current",
                "ready": "available",
                "locked": "locked",
            }.get(db_status, "available")

    return course


@router.get("/{course_id}/progress", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CourseProgress).where(
            CourseProgress.user_id == current_user.id,
            CourseProgress.course_id == course_id
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        total_lessons_result = await db.execute(
            select(func.count(Lesson.id)).join(Module).where(Module.course_id == course_id)
        )
        total_lessons = total_lessons_result.scalar() or 0

        progress = CourseProgress(
            user_id=current_user.id,
            course_id=course_id,
            total_lessons=total_lessons,
            completed_lessons=0,
            progress_percent=0.0
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)

    return progress