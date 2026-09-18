"""Orientini -- Morocco-specific post-Bac career/institution matching.

The quiz endpoints are read-only content (questions/options, institutions);
submitting the quiz computes and stores a ranked result but never mutates
StudentProfile.bac_track unless the student's most recent submission carried
a track -- see submit_quiz.
"""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import (
    Institution,
    OrientiniOption,
    OrientiniQuestion,
    OrientiniResult,
    StudentProfile,
    User,
)
from app.schemas import (
    InstitutionResponse,
    LanguageEnum,
    OrientiniQuestionResponse,
    OrientiniResultResponse,
    OrientiniScoreResponse,
    OrientiniSubmitRequest,
)
from app.services.orientini import compute_student_vector, score_institutions

router = APIRouter(prefix="/orientini", tags=["orientini"])


def _filter_translations(items, language: LanguageEnum):
    for item in items:
        item.translations = [t for t in item.translations if t.language == language]


@router.get("/questions", response_model=List[OrientiniQuestionResponse])
async def get_questions(
    language: LanguageEnum = Query(LanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OrientiniQuestion)
        .options(
            selectinload(OrientiniQuestion.translations),
            selectinload(OrientiniQuestion.options).selectinload(OrientiniOption.translations),
        )
        .order_by(OrientiniQuestion.order)
    )
    questions = result.scalars().unique().all()
    _filter_translations(questions, language)
    for question in questions:
        _filter_translations(question.options, language)
    return questions


@router.get("/institutions", response_model=List[InstitutionResponse])
async def get_institutions(
    language: LanguageEnum = Query(LanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Institution)
        .options(selectinload(Institution.translations), selectinload(Institution.requirement))
        .order_by(Institution.order)
    )
    institutions = result.scalars().unique().all()
    _filter_translations(institutions, language)
    return institutions


@router.post("/submit", response_model=OrientiniResultResponse)
async def submit_quiz(
    payload: OrientiniSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.answers:
        raise HTTPException(status_code=400, detail="At least one answer is required")

    option_ids = list(payload.answers.values())
    options_result = await db.execute(
        select(OrientiniOption).where(OrientiniOption.id.in_(option_ids))
    )
    options_by_id = {o.id: o for o in options_result.scalars().all()}
    missing = [oid for oid in option_ids if oid not in options_by_id]
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown option id(s): {missing}")

    student_vector = compute_student_vector(list(options_by_id.values()))

    institutions_result = await db.execute(
        select(Institution).options(selectinload(Institution.requirement))
    )
    institutions = institutions_result.scalars().unique().all()

    ranked = score_institutions(student_vector, institutions, payload.bac_track)
    scores = [
        OrientiniScoreResponse(
            institution_id=r.institution_id,
            score=r.score,
            eligible=r.eligible,
            trait_breakdown=r.trait_breakdown,
        )
        for r in ranked
    ]

    result_row = OrientiniResult(
        user_id=current_user.id,
        bac_track=payload.bac_track,
        answers=json.dumps(payload.answers),
        scores=json.dumps([s.model_dump() for s in scores]),
    )
    db.add(result_row)

    if payload.bac_track is not None:
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == current_user.id)
        )
        profile = profile_result.scalar_one_or_none()
        if profile is not None:
            profile.bac_track = payload.bac_track

    await db.commit()
    await db.refresh(result_row)

    return OrientiniResultResponse(
        id=result_row.id,
        bac_track=result_row.bac_track,
        scores=scores,
        created_at=result_row.created_at,
    )


@router.get("/results/latest", response_model=OrientiniResultResponse)
async def get_latest_result(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OrientiniResult)
        .where(OrientiniResult.user_id == current_user.id)
        .order_by(OrientiniResult.created_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="No Orientini result yet")

    scores = [OrientiniScoreResponse(**s) for s in json.loads(row.scores)]
    return OrientiniResultResponse(
        id=row.id,
        bac_track=row.bac_track,
        scores=scores,
        created_at=row.created_at,
    )
