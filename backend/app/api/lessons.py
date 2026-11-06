import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.lesson_progress import get_or_create_lesson_progress
from app.models import (
    Lesson, LessonBlock, LessonBlockTranslation, Exercise, ExerciseTranslation,
    ExerciseOption, ExerciseOptionTranslation, ExerciseTypeEnum, LessonProgress, StudentProfile,
    MissionStatusEnum, LanguageEnum, Module, Course
)
from app.schemas import LessonResponse, LessonProgressResponse, ExerciseResponse, LanguageEnum as SchemaLanguageEnum


def _extract_trace(exercise: Exercise) -> Optional[list]:
    """Break-the-Code's step-through trace, pulled off validation_config
    before that field is nulled out below -- see ExerciseResponse.trace."""
    if exercise.exercise_type != ExerciseTypeEnum.debugging or not exercise.validation_config:
        return None
    try:
        config = json.loads(exercise.validation_config)
    except (ValueError, TypeError):
        return None
    trace = config.get("trace") if isinstance(config, dict) else None
    return trace if isinstance(trace, list) else None


async def _require_lesson(db: AsyncSession, lesson_id: int) -> None:
    """404 on a lesson that does not exist.

    Mirrors projects.py. Both progress endpoints below go on to insert a
    progress row keyed on lesson_id, which on Postgres trips the foreign key
    and surfaces as a 500 (the test engine does not enforce FKs, so there it
    silently created an orphan row and returned 200).
    """
    result = await db.execute(select(Lesson.id).where(Lesson.id == lesson_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Lesson not found")


router = APIRouter(prefix="/lessons", tags=["lessons"])


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
        selectinload(Lesson.module).selectinload(Module.translations),
        selectinload(Lesson.module).selectinload(Module.course).selectinload(Course.translations),
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
        exercise.trace = _extract_trace(exercise)
        exercise.solution_code = None
        exercise.test_code = None
        exercise.validation_config = None

    # Breadcrumb (Dashboard / Course / Lesson): Lesson carries a module_id on
    # the ORM model but LessonResponse never exposed it (or a course), so the
    # frontend had no way to render a real trail -- same gap Step 2 found and
    # fixed for the dashboard's current-mission card.
    course_title = None
    course_id = None
    module_title = None
    module = lesson.module
    if module:
        module_translation = next((t for t in module.translations if t.language == language), None)
        module_title = module_translation.title if module_translation else None
        if module.course:
            course_translation = next((t for t in module.course.translations if t.language == language), None)
            course_title = course_translation.title if course_translation else None
            course_id = module.course.id
    lesson.course_title = course_title
    lesson.course_id = course_id
    lesson.module_title = module_title

    progress_query = select(LessonProgress).where(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()

    if progress and progress.status == MissionStatusEnum.locked:
        progress.status = MissionStatusEnum.ready
        await db.commit()

    payload = LessonResponse.model_validate(lesson, from_attributes=True).model_dump(mode="json")
    for exercise_payload in payload["exercises"]:
        # `trace` is Break-the-Code-only: for every exercise type except a
        # `debugging` one authored with a trace, the key must be absent from
        # the response entirely, not merely present-and-null -- a present
        # key still advertises the field's existence to every exercise type,
        # which is more than "debugging only" should expose. model_dump()
        # always includes Optional fields (as null) with no per-field
        # exclude_none, so this is stripped by hand rather than by widening
        # exclude_none across the whole payload (which would also swallow
        # every other legitimately-null field, e.g. block content/config).
        if exercise_payload.get("trace") is None:
            exercise_payload.pop("trace", None)

    return JSONResponse(payload)


@router.get("/{lesson_id}/progress", response_model=LessonProgressResponse)
async def get_lesson_progress(
    lesson_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await _require_lesson(db, lesson_id)
    return await get_or_create_lesson_progress(
        db, current_user.id, lesson_id, MissionStatusEnum.ready
    )


@router.post("/{lesson_id}/start", response_model=LessonProgressResponse)
async def start_lesson(
    lesson_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await _require_lesson(db, lesson_id)
    progress = await get_or_create_lesson_progress(
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