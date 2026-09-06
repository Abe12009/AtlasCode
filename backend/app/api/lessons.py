from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.compat import conflict_insert
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import (
    Lesson, LessonBlock, LessonBlockTranslation, Exercise, ExerciseTranslation,
    ExerciseOption, ExerciseOptionTranslation, LessonProgress, StudentProfile,
    MissionStatusEnum, LanguageEnum
)
from app.schemas import LessonResponse, LessonProgressResponse, ExerciseResponse, LanguageEnum as SchemaLanguageEnum

router = APIRouter(prefix="/lessons", tags=["lessons"])


async def _get_or_create_lesson_progress(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
    initial_status: MissionStatusEnum,
) -> LessonProgress:
    """Idempotently obtain this user's progress row for a lesson.

    A plain "select, then insert if missing" races: two concurrent requests can
    both see no row and both insert, and the loser fails the uq_user_lesson
    constraint with a 500. Letting the database resolve the conflict instead
    makes the loser's insert a no-op, so both requests read back the same
    single row. An existing row is never modified here.
    """
    stmt = (
        conflict_insert(LessonProgress)
        .values(user_id=user_id, lesson_id=lesson_id, status=initial_status)
        .on_conflict_do_nothing(index_elements=["user_id", "lesson_id"])
    )
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    return result.scalar_one()


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    language: SchemaLanguageEnum = Query(SchemaLanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Lesson).options(
        selectinload(Lesson.translations),
        selectinload(Lesson.blocks).selectinload(LessonBlock.translations),
        selectinload(Lesson.exercises).selectinload(Exercise.translations),
        selectinload(Lesson.exercises).selectinload(Exercise.options).selectinload(ExerciseOption.translations),
    ).where(Lesson.id == lesson_id)

    result = await db.execute(query)
    lesson = result.scalars().unique().first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson.translations = [t for t in lesson.translations if t.language == language]
    for block in lesson.blocks:
        block.translations = [t for t in block.translations if t.language == language]
    for exercise in lesson.exercises:
        exercise.translations = [t for t in exercise.translations if t.language == language]
        exercise.options = [o for o in exercise.options]
        for option in exercise.options:
            option.translations = [t for t in option.translations if t.language == language]
        exercise.solution_code = None
        exercise.test_code = None
        exercise.validation_config = None

    progress_query = select(LessonProgress).where(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()

    if progress and progress.status == MissionStatusEnum.locked:
        progress.status = MissionStatusEnum.ready
        await db.commit()

    return lesson


@router.get("/{lesson_id}/progress", response_model=LessonProgressResponse)
async def get_lesson_progress(
    lesson_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await _get_or_create_lesson_progress(
        db, current_user.id, lesson_id, MissionStatusEnum.ready
    )


@router.post("/{lesson_id}/start", response_model=LessonProgressResponse)
async def start_lesson(
    lesson_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    progress = await _get_or_create_lesson_progress(
        db, current_user.id, lesson_id, MissionStatusEnum.in_progress
    )

    # Only advance a not-yet-started lesson. A lesson already in progress or
    # completed keeps its status, xp_earned and current_block untouched.
    if progress.status in (MissionStatusEnum.locked, MissionStatusEnum.ready):
        progress.status = MissionStatusEnum.in_progress
        await db.commit()
        await db.refresh(progress)

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile:
        profile.current_mission_id = lesson_id
        await db.commit()

    return progress