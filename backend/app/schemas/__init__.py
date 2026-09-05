from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from app.models import LanguageEnum, DifficultyEnum, MissionStatusEnum, ExerciseTypeEnum, NotificationTypeEnum


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    preferred_language: LanguageEnum = LanguageEnum.en


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    preferred_language: Optional[LanguageEnum] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StudentProfileResponse(BaseModel):
    id: int
    name: Optional[str] = None
    xp: int
    level: int
    streak: int
    completed_lessons: int
    completed_projects: int
    current_mission_id: Optional[int] = None

    class Config:
        from_attributes = True


class CourseTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    description: Optional[str] = None
    skills: Optional[str] = None


class CourseResponse(BaseModel):
    id: int
    slug: str
    order: int
    translations: List[CourseTranslationResponse]
    modules: List[ModuleResponse] = []

    class Config:
        from_attributes = True


class ModuleTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    description: Optional[str] = None


class ModuleResponse(BaseModel):
    id: int
    slug: str
    order: int
    translations: List[ModuleTranslationResponse]
    lessons: List["LessonResponse"] = []

    class Config:
        from_attributes = True


class LessonBlockTranslationResponse(BaseModel):
    language: LanguageEnum
    content: Optional[str] = None
    code_example: Optional[str] = None


class LessonBlockResponse(BaseModel):
    id: int
    block_type: str
    order: int
    content: Optional[str] = None
    code_example: Optional[str] = None
    #: Raw JSON string for Micro-Quest block types; null for ordinary blocks.
    config: Optional[str] = None
    translations: List[LessonBlockTranslationResponse] = []

    class Config:
        from_attributes = True


class ExerciseOptionTranslationResponse(BaseModel):
    language: LanguageEnum
    text: str


class ExerciseOptionResponse(BaseModel):
    # is_correct is deliberately absent: the client must never learn which
    # option is right before it submits. Correctness is decided server-side.
    id: int
    order: int
    translations: List[ExerciseOptionTranslationResponse] = []

    class Config:
        from_attributes = True


class ExerciseTranslationResponse(BaseModel):
    language: LanguageEnum
    prompt: str
    hint: Optional[str] = None
    explanation: Optional[str] = None


class ExerciseResponse(BaseModel):
    id: int
    exercise_type: ExerciseTypeEnum
    order: int
    xp_reward: int
    starter_code: Optional[str] = None
    translations: List[ExerciseTranslationResponse] = []
    options: List[ExerciseOptionResponse] = []

    class Config:
        from_attributes = True


class LessonTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    story: Optional[str] = None
    objective: Optional[str] = None
    skills: Optional[str] = None


class LessonResponse(BaseModel):
    id: int
    slug: str
    order: int
    difficulty: DifficultyEnum
    estimated_minutes: int
    xp_reward: int
    is_project: bool
    translations: List[LessonTranslationResponse] = []
    blocks: List[LessonBlockResponse] = []
    exercises: List[ExerciseResponse] = []
    status: Optional[str] = None

    class Config:
        from_attributes = True


class LessonProgressResponse(BaseModel):
    id: int
    lesson_id: int
    status: MissionStatusEnum
    completed_at: Optional[datetime] = None
    xp_earned: int
    current_block: int

    class Config:
        from_attributes = True


class CourseProgressResponse(BaseModel):
    course_id: int
    completed_lessons: int
    total_lessons: int
    progress_percent: float

    class Config:
        from_attributes = True


class ProjectTaskTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    description: Optional[str] = None
    hint: Optional[str] = None


class ProjectTaskResponse(BaseModel):
    id: int
    order: int
    starter_code: Optional[str] = None
    translations: List[ProjectTaskTranslationResponse] = []

    class Config:
        from_attributes = True


class ProjectTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    story: Optional[str] = None
    objective: Optional[str] = None
    skills: Optional[str] = None
    guide: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    slug: str
    order: int
    difficulty: DifficultyEnum
    xp_reward: int
    prerequisite_lesson_id: Optional[int] = None
    prerequisite_project_id: Optional[int] = None
    translations: List[ProjectTranslationResponse] = []
    tasks: List[ProjectTaskResponse] = []

    class Config:
        from_attributes = True


class ProjectProgressResponse(BaseModel):
    id: int
    project_id: int
    status: MissionStatusEnum
    current_task: int
    completed_at: Optional[datetime] = None
    xp_earned: int
    code_snapshot: Optional[str] = None

    class Config:
        from_attributes = True


class AchievementTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    description: Optional[str] = None


class AchievementResponse(BaseModel):
    id: int
    slug: str
    icon: Optional[str] = None
    xp_reward: int
    translations: List[AchievementTranslationResponse] = []

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    id: int
    achievement_id: int
    earned_at: datetime
    achievement: AchievementResponse

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    user: UserResponse
    profile: StudentProfileResponse
    current_mission: Optional[LessonResponse] = None
    course_progress: List[CourseProgressResponse] = []
    recent_achievements: List[UserAchievementResponse] = []
    current_project: Optional[ProjectProgressResponse] = None


class CodeExecutionRequest(BaseModel):
    code: str
    test_code: Optional[str] = None


class ProjectTaskSubmitRequest(BaseModel):
    task_id: int
    code: str


class CodeExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float


class CodeValidationRequest(BaseModel):
    code: str


class CodeValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str] = []


class ExerciseSubmitRequest(BaseModel):
    exercise_id: int
    # Code exercises keep sending `code`. Non-code types carry their answer in
    # the field that matches how they are answered; the grader picks the one
    # its strategy needs and ignores the rest.
    code: str = ""
    selected_option_id: Optional[int] = None
    ordered_option_ids: Optional[List[int]] = None
    answer: Optional[str] = None
    blanks: Optional[List[str]] = None


class ExerciseSubmitResponse(BaseModel):
    is_correct: bool
    xp_earned: int
    feedback: str
    output: Optional[str] = None
    error: Optional[str] = None
    # True once this user has ever solved the exercise, so the UI can show a
    # completed state without re-deriving it.
    is_completed: bool = False
    lesson_completed: bool = False


class VisualProgramRequest(BaseModel):
    nodes: List[dict]
    edges: List[dict]


class VisualProgramResponse(BaseModel):
    python_code: str
    is_valid: bool
    errors: List[str] = []


class NotificationResponse(BaseModel):
    id: int
    type: NotificationTypeEnum
    data: Dict[str, Any] = {}
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info):
        # Stored as naive UTC (see Notification.created_at); mark it explicitly
        # so clients don't misinterpret it as local time.
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class UnreadCountResponse(BaseModel):
    count: int


LessonResponse.model_rebuild()
ModuleResponse.model_rebuild()