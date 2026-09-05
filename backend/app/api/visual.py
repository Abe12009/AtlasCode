from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import Exercise, ExerciseTranslation, ExerciseOption, ExerciseOptionTranslation, LanguageEnum
from app.schemas import VisualProgramRequest, VisualProgramResponse, ExerciseSubmitRequest, ExerciseSubmitResponse
from app.services.visual_compiler import compile_visual_program
from app.services.code_executor import execute_code, validate_python_code

router = APIRouter(prefix="/visual", tags=["visual-programming"])


@router.post("/compile", response_model=VisualProgramResponse)
async def compile_visual(
    request: VisualProgramRequest,
    current_user = Depends(get_current_user)
):
    result = compile_visual_program(request.nodes, request.edges)
    return result


@router.post("/{exercise_id}/run", response_model=ExerciseSubmitResponse)
async def run_visual_exercise(
    exercise_id: int,
    request: ExerciseSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    exercise_result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = exercise_result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

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
        feedback="Visual program executed successfully" if exec_result.success else exec_result.error or "Execution failed",
        output=exec_result.output,
        error=exec_result.error
    )


@router.post("/{exercise_id}/submit", response_model=ExerciseSubmitResponse)
async def submit_visual_exercise(
    exercise_id: int,
    request: ExerciseSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from app.api.exercises import submit_exercise
    return await submit_exercise(exercise_id, request, db, current_user)


@router.get("/{exercise_id}/starter")
async def get_visual_starter(
    exercise_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exercise_result = await db.execute(
        select(Exercise).options(
            selectinload(Exercise.translations)
        ).where(Exercise.id == exercise_id)
    )
    exercise = exercise_result.scalars().unique().first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    if exercise.exercise_type.value != "visual_programming":
        raise HTTPException(status_code=400, detail="Not a visual programming exercise")

    starter = exercise.starter_code or "{}"
    import json
    try:
        starter_data = json.loads(starter)
        return starter_data
    except json.JSONDecodeError:
        return {"nodes": [], "edges": []}