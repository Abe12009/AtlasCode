from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import (
    Exercise, ExerciseTranslation, ExerciseOption, ExerciseOptionTranslation,
    ExerciseAttempt, LessonProgress, StudentProfile, Lesson, MissionStatusEnum,
    LanguageEnum, CourseProgress, Module, NotificationTypeEnum
)
from app.schemas import (
    ExerciseResponse, ExerciseSubmitRequest, ExerciseSubmitResponse,
    LanguageEnum as SchemaLanguageEnum, ExerciseTypeEnum
)
from app.services.code_executor import execute_code, validate_python_code
from app.services.exercise_grading import grade_exercise, resolve_strategy, STRATEGY_SANDBOX
from app.services.notifications import create_notification
from app.services.stats import record_activity

router = APIRouter(prefix="/exercises", tags=["exercises"])


def _submitted_answer_text(request) -> str:
    """A readable record of what the student answered, for ExerciseAttempt."""
    if request.selected_option_id is not None:
        return f"option:{request.selected_option_id}"
    if request.ordered_option_ids:
        return "order:" + ",".join(str(i) for i in request.ordered_option_ids)
    if request.blanks is not None:
        return "blanks:" + " | ".join(request.blanks)
    if request.answer is not None:
        return request.answer
    return request.code or ""


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: int,
    language: SchemaLanguageEnum = Query(SchemaLanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Exercise).options(
        selectinload(Exercise.translations),
        selectinload(Exercise.options).selectinload(ExerciseOption.translations),
    ).where(Exercise.id == exercise_id)

    result = await db.execute(query)
    exercise = result.scalars().unique().first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    exercise.translations = [t for t in exercise.translations if t.language == language]
    exercise.options = [o for o in exercise.options]
    for option in exercise.options:
        option.translations = [t for t in option.translations if t.language == language]

    exercise.solution_code = None
    exercise.test_code = None
    exercise.validation_config = None

    return exercise


@router.post("/{exercise_id}/run", response_model=ExerciseSubmitResponse)
async def run_exercise(
    exercise_id: int,
    request: ExerciseSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Exercise).options(selectinload(Exercise.options)).where(Exercise.id == exercise_id)
    result = await db.execute(query)
    exercise = result.scalars().unique().first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # "Run" only means anything for exercises whose answer is code. For the
    # others there is nothing to execute, and running arbitrary code would say
    # nothing about the answer.
    if resolve_strategy(exercise, exercise.options) != STRATEGY_SANDBOX:
        return ExerciseSubmitResponse(
            is_correct=False,
            xp_earned=0,
            feedback="This exercise is answered, not run. Use Submit.",
            output="",
        )

    validation = validate_python_code(request.code)
    if not validation.is_valid:
        return ExerciseSubmitResponse(
            is_correct=False,
            xp_earned=0,
            feedback="Code validation failed: " + "; ".join(validation.errors),
            error="Validation error"
        )

    exec_result = execute_code(request.code, exercise.test_code)

    return ExerciseSubmitResponse(
        is_correct=exec_result.success,
        xp_earned=0,
        feedback="Code executed successfully" if exec_result.success else exec_result.error or "Execution failed",
        output=exec_result.output,
        error=exec_result.error
    )


@router.post("/{exercise_id}/submit", response_model=ExerciseSubmitResponse)
async def submit_exercise(
    exercise_id: int,
    request: ExerciseSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Exercise).options(
        selectinload(Exercise.translations),
        selectinload(Exercise.options),
        selectinload(Exercise.lesson).selectinload(Lesson.module)
    ).where(Exercise.id == exercise_id)
    result = await db.execute(query)
    exercise = result.scalars().unique().first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Every type is graded against its own stored expected answer. Code
    # exercises still go through the sandbox unchanged.
    grading = grade_exercise(exercise, exercise.options, request)
    is_correct = grading.is_correct

    existing_attempt = await db.execute(
        select(ExerciseAttempt).where(
            ExerciseAttempt.user_id == current_user.id,
            ExerciseAttempt.exercise_id == exercise_id,
            ExerciseAttempt.is_correct == True
        )
    )
    previous_success = existing_attempt.scalar()

    xp_earned = 0
    lesson_completed = False
    if is_correct and not previous_success:
        xp_earned = exercise.xp_reward

    now = datetime.utcnow()
    attempt = ExerciseAttempt(
        user_id=current_user.id,
        exercise_id=exercise_id,
        submitted_code=_submitted_answer_text(request),
        is_correct=is_correct,
        xp_earned=xp_earned,
        feedback=grading.feedback,
        created_at=now,
    )
    db.add(attempt)

    # Practising counts as showing up, whether or not the answer was right —
    # that is what a learning streak is measuring.
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    activity_profile = profile_result.scalar_one_or_none()
    await record_activity(db, current_user, activity_profile, now_utc=now)

    if is_correct and not previous_success:
        profile = activity_profile
        if profile:
            profile.xp += xp_earned
            new_level = (profile.xp // 100) + 1
            if new_level > profile.level:
                profile.level = new_level

        await create_notification(
            db, current_user.id, NotificationTypeEnum.xp_earned, {"xp": xp_earned}
        )

        lesson_progress_result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == current_user.id,
                LessonProgress.lesson_id == exercise.lesson_id
            )
        )
        lesson_progress = lesson_progress_result.scalar_one_or_none()
        if lesson_progress:
            lesson_progress.xp_earned += xp_earned

            all_exercises_result = await db.execute(
                select(func.count(Exercise.id)).where(Exercise.lesson_id == exercise.lesson_id)
            )
            total_exercises = all_exercises_result.scalar() or 0

            correct_attempts_result = await db.execute(
                select(func.count(ExerciseAttempt.id.distinct())).where(
                    ExerciseAttempt.user_id == current_user.id,
                    ExerciseAttempt.exercise_id.in_(
                        select(Exercise.id).where(Exercise.lesson_id == exercise.lesson_id)
                    ),
                    ExerciseAttempt.is_correct == True
                )
            )
            correct_count = correct_attempts_result.scalar() or 0

            if correct_count >= total_exercises and total_exercises > 0:
                lesson_completed = True
                lesson_progress.status = MissionStatusEnum.completed
                lesson_progress.completed_at = now
                profile.completed_lessons += 1

                await create_notification(
                    db, current_user.id, NotificationTypeEnum.lesson_completed,
                    {"lesson_id": exercise.lesson_id}
                )

                course_progress_result = await db.execute(
                    select(LessonProgress).join(Lesson).join(Module).where(
                        LessonProgress.user_id == current_user.id,
                        Module.course_id == exercise.lesson.module.course_id
                    )
                )
                completed_in_course = sum(1 for lp in course_progress_result.scalars() if lp.status == MissionStatusEnum.completed)

                cp_result = await db.execute(
                    select(CourseProgress).where(
                        CourseProgress.user_id == current_user.id,
                        CourseProgress.course_id == exercise.lesson.module.course_id
                    )
                )
                cp = cp_result.scalar_one_or_none()
                if cp:
                    cp.completed_lessons = completed_in_course
                    cp.progress_percent = (completed_in_course / cp.total_lessons * 100) if cp.total_lessons > 0 else 0

    await db.commit()

    hint_text = ""
    if not is_correct:
        hint_result = await db.execute(
            select(ExerciseTranslation).where(
                ExerciseTranslation.exercise_id == exercise_id,
                ExerciseTranslation.language == current_user.preferred_language
            )
        )
        hint_trans = hint_result.scalar_one_or_none()
        if hint_trans and hint_trans.hint:
            hint_text = f" Hint: {hint_trans.hint}"

    return ExerciseSubmitResponse(
        is_correct=is_correct,
        xp_earned=xp_earned,
        feedback=grading.feedback + hint_text,
        output=grading.output,
        error=grading.error if not is_correct else None,
        # Completed once solved, whether on this submission or an earlier one.
        is_completed=bool(is_correct or previous_success),
        lesson_completed=lesson_completed,
    )


@router.get("/{exercise_id}/attempts")
async def get_exercise_attempts(
    exercise_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ExerciseAttempt).where(
            ExerciseAttempt.user_id == current_user.id,
            ExerciseAttempt.exercise_id == exercise_id
        ).order_by(ExerciseAttempt.created_at.desc())
    )
    attempts = result.scalars().all()
    return attempts