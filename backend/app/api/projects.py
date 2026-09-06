from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.compat import conflict_insert
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import (
    Project, ProjectTranslation, ProjectTask, ProjectTaskTranslation,
    ProjectProgress, Lesson, LessonProgress, StudentProfile,
    MissionStatusEnum, LanguageEnum, NotificationTypeEnum
)
from app.schemas import (
    ProjectResponse, ProjectProgressResponse, LanguageEnum as SchemaLanguageEnum,
    ProjectTaskSubmitRequest
)
from app.services.notifications import create_notification
from app.services.stats import record_activity

router = APIRouter(prefix="/projects", tags=["projects"])


async def _get_or_create_project_progress(
    db: AsyncSession,
    user_id: int,
    project_id: int,
    initial_status: MissionStatusEnum,
) -> ProjectProgress:
    """Idempotently obtain this user's progress row for a project.

    Same race as lesson progress: a "select, then insert if missing" lets two
    concurrent requests both insert and the loser fails uq_user_project with a
    500. The database resolves the conflict instead, so both read back the same
    single row. An existing row is never modified here.
    """
    stmt = (
        conflict_insert(ProjectProgress)
        .values(user_id=user_id, project_id=project_id, status=initial_status)
        .on_conflict_do_nothing(index_elements=["user_id", "project_id"])
    )
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(
        select(ProjectProgress).where(
            ProjectProgress.user_id == user_id,
            ProjectProgress.project_id == project_id,
        )
    )
    return result.scalar_one()


@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    language: SchemaLanguageEnum = Query(SchemaLanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Project).options(
        selectinload(Project.translations),
        selectinload(Project.tasks).selectinload(ProjectTask.translations),
    ).order_by(Project.order)

    result = await db.execute(query)
    projects = result.scalars().unique().all()

    for project in projects:
        project.translations = [t for t in project.translations if t.language == language]
        for task in project.tasks:
            task.translations = [t for t in task.translations if t.language == language]

    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    language: SchemaLanguageEnum = Query(SchemaLanguageEnum.en),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Project).options(
        selectinload(Project.translations),
        selectinload(Project.tasks).selectinload(ProjectTask.translations),
    ).where(Project.id == project_id)

    result = await db.execute(query)
    project = result.scalars().unique().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.translations = [t for t in project.translations if t.language == language]
    for task in project.tasks:
        task.translations = [t for t in task.translations if t.language == language]

    return project


@router.get("/{project_id}/progress", response_model=ProjectProgressResponse)
async def get_project_progress(
    project_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_unlocked = await _check_project_unlocked(project, current_user, db)

    return await _get_or_create_project_progress(
        db,
        current_user.id,
        project_id,
        MissionStatusEnum.ready if is_unlocked else MissionStatusEnum.locked,
    )


@router.post("/{project_id}/start", response_model=ProjectProgressResponse)
async def start_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_unlocked = await _check_project_unlocked(project, current_user, db)
    if not is_unlocked:
        raise HTTPException(status_code=403, detail="Project is locked. Complete prerequisite lessons/projects first.")

    progress = await _get_or_create_project_progress(
        db, current_user.id, project_id, MissionStatusEnum.in_progress
    )

    # Only advance a not-yet-started project. One already in progress or
    # completed keeps its status, xp_earned, current_task and code_snapshot.
    if progress.status in (MissionStatusEnum.locked, MissionStatusEnum.ready):
        progress.status = MissionStatusEnum.in_progress
        await db.commit()
        await db.refresh(progress)

    return progress


@router.post("/{project_id}/submit-task")
async def submit_project_task(
    project_id: int,
    request: ProjectTaskSubmitRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task_id = request.task_id
    code = request.code
    progress_result = await db.execute(
        select(ProjectProgress).where(
            ProjectProgress.user_id == current_user.id,
            ProjectProgress.project_id == project_id
        )
    )
    progress = progress_result.scalar_one_or_none()
    if not progress:
        raise HTTPException(status_code=404, detail="Project progress not found")

    if progress.status == MissionStatusEnum.locked:
        raise HTTPException(status_code=403, detail="Project is locked")

    task_result = await db.execute(select(ProjectTask).where(ProjectTask.id == task_id, ProjectTask.project_id == project_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.validation_code:
        from app.services.code_executor import execute_code
        # Combine user code and validation code so validation can access user-defined functions
        combined_code = code + "\n\n" + task.validation_code
        result = execute_code(combined_code, None)
        if not result.success:
            return {"success": False, "error": result.error, "output": result.output}

    now = datetime.utcnow()
    progress.code_snapshot = code
    was_completed = progress.status == MissionStatusEnum.completed
    if task_id >= progress.current_task:
        progress.current_task = task_id + 1

    activity_profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    await record_activity(
        db, current_user, activity_profile_result.scalar_one_or_none(), now_utc=now
    )

    all_tasks_result = await db.execute(select(func.count(ProjectTask.id)).where(ProjectTask.project_id == project_id))
    total_tasks = all_tasks_result.scalar() or 0

    if not was_completed and progress.current_task >= total_tasks:
        progress.status = MissionStatusEnum.completed
        progress.completed_at = now

        project_result = await db.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalar_one_or_none()

        profile_result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
        profile = profile_result.scalar_one_or_none()
        if profile and project:
            profile.xp += project.xp_reward
            profile.completed_projects += 1
            new_level = (profile.xp // 100) + 1
            if new_level > profile.level:
                profile.level = new_level

            progress.xp_earned = project.xp_reward

            await create_notification(
                db, current_user.id, NotificationTypeEnum.project_completed,
                {"project_id": project_id, "xp": project.xp_reward}
            )

    await db.commit()
    await db.refresh(progress)

    return {"success": True, "progress": progress}


async def _check_project_unlocked(project: Project, current_user, db: AsyncSession) -> bool:
    if project.prerequisite_lesson_id:
        lesson_progress_result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == current_user.id,
                LessonProgress.lesson_id == project.prerequisite_lesson_id
            )
        )
        lesson_progress = lesson_progress_result.scalar_one_or_none()
        if not lesson_progress or lesson_progress.status != MissionStatusEnum.completed:
            return False

    if project.prerequisite_project_id:
        project_progress_result = await db.execute(
            select(ProjectProgress).where(
                ProjectProgress.user_id == current_user.id,
                ProjectProgress.project_id == project.prerequisite_project_id
            )
        )
        project_progress = project_progress_result.scalar_one_or_none()
        if not project_progress or project_progress.status != MissionStatusEnum.completed:
            return False

    return True