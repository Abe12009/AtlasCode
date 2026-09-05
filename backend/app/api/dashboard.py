from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import (
    User, StudentProfile, LessonProgress, CourseProgress, ProjectProgress,
    Lesson, LessonBlock, Module, Course, Project, ProjectTask, Achievement, UserAchievement,
    MissionStatusEnum, Exercise, ExerciseOption
)
from app.schemas import DashboardResponse, UserResponse, StudentProfileResponse, CourseProgressResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    current_mission = None
    if profile.current_mission_id:
        mission_result = await db.execute(
            select(Lesson).options(
                selectinload(Lesson.translations),
                selectinload(Lesson.blocks).selectinload(LessonBlock.translations),
                selectinload(Lesson.exercises).selectinload(Exercise.translations),
                selectinload(Lesson.exercises).selectinload(Exercise.options).selectinload(ExerciseOption.translations),
            ).where(Lesson.id == profile.current_mission_id)
        )
        current_mission = mission_result.scalars().unique().first()
        if current_mission:
            current_mission.translations = [t for t in current_mission.translations if t.language == current_user.preferred_language]
            for block in current_mission.blocks:
                block.translations = [t for t in block.translations if t.language == current_user.preferred_language]
            for exercise in current_mission.exercises:
                exercise.translations = [t for t in exercise.translations if t.language == current_user.preferred_language]
                exercise.options = [o for o in exercise.options]
                for option in exercise.options:
                    option.translations = [t for t in option.translations if t.language == current_user.preferred_language]
                exercise.solution_code = None
                exercise.test_code = None
                exercise.validation_config = None

    course_progress_result = await db.execute(
        select(CourseProgress).where(CourseProgress.user_id == current_user.id)
    )
    course_progress = course_progress_result.scalars().all()

    recent_achievements_result = await db.execute(
        select(UserAchievement).options(
            selectinload(UserAchievement.achievement).selectinload(Achievement.translations)
        ).where(
            UserAchievement.user_id == current_user.id
        ).order_by(UserAchievement.earned_at.desc()).limit(5)
    )
    recent_achievements = recent_achievements_result.scalars().all()
    for ua in recent_achievements:
        ua.achievement.translations = [t for t in ua.achievement.translations if t.language == current_user.preferred_language]

    current_project = None
    project_progress_result = await db.execute(
        select(ProjectProgress).where(
            ProjectProgress.user_id == current_user.id,
            ProjectProgress.status.in_([MissionStatusEnum.in_progress, MissionStatusEnum.ready])
        ).order_by(ProjectProgress.updated_at.desc())
    )
    project_progress = project_progress_result.scalars().first()
    if project_progress:
        project_result = await db.execute(
            select(Project).options(
                selectinload(Project.translations),
                selectinload(Project.tasks).selectinload(ProjectTask.translations)
            ).where(Project.id == project_progress.project_id)
        )
        project = project_result.scalars().unique().first()
        if project:
            project.translations = [t for t in project.translations if t.language == current_user.preferred_language]
            for task in project.tasks:
                task.translations = [t for t in task.translations if t.language == current_user.preferred_language]
        current_project = project_progress

    return {
        "user": current_user,
        "profile": profile,
        "current_mission": current_mission,
        "course_progress": course_progress,
        "recent_achievements": recent_achievements,
        "current_project": current_project
    }