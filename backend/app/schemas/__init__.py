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
    #: Minutes east of UTC, from the browser. Used for streak/week boundaries.
    timezone_offset_minutes: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    timezone_offset_minutes: Optional[int] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    preferred_language: Optional[LanguageEnum] = None
    timezone_offset_minutes: Optional[int] = None
    #: "public" or "private". Whether other signed-in users can view this
    #: account's profile/achievements. See GET /users/{username}.
    profile_visibility: Optional[str] = Field(default=None, pattern="^(public|private)$")
    #: "upload" (avatar_url) or "generated" (avatar_config). Switching this
    #: does not clear the other field, so a user can flip back and forth
    #: without losing either the built avatar or the uploaded photo.
    avatar_type: Optional[str] = Field(default=None, pattern="^(upload|generated)$")
    #: The built avatar's layer choices, as a JSON string. Validated shape-only
    #: here (parseable JSON, reasonable size) — the frontend owns which layer
    #: values are meaningful, since that catalog only ever grows.
    avatar_config: Optional[str] = Field(default=None, max_length=4096)


class AvatarUploadRequest(BaseModel):
    """A device photo, already resized/compressed client-side.

    ``data_url`` must be a base64 data: URL (``data:image/png;base64,...``)
    for one of the allowed image types — validated server-side in
    app.api.auth, since a client-side check alone is not trustworthy.
    """

    data_url: str = Field(min_length=32, max_length=2_000_000)


class FirebaseLoginRequest(BaseModel):
    """Exchange a verified Firebase ID token for an AtlasCode session token."""

    id_token: str = Field(min_length=16, max_length=8192)
    preferred_language: Optional[LanguageEnum] = None
    timezone_offset_minutes: Optional[int] = None


class PasswordChangeRequest(BaseModel):
    """Change an AtlasCode password while signed in."""

    current_password: str = Field(min_length=1, max_length=100)
    new_password: str = Field(min_length=8, max_length=100)


class AuthConfigResponse(BaseModel):
    """What sign-in methods this deployment actually supports."""

    firebase_enabled: bool
    password_login_enabled: bool = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    auth_provider: str = "password"
    email_verified: bool = False
    avatar_url: Optional[str] = None
    avatar_image_data: Optional[str] = None
    avatar_config: Optional[str] = None
    avatar_type: str = "upload"
    profile_visibility: str = "private"
    #: True when the account can sign in with an AtlasCode password. False for
    #: accounts that exist only through a federated provider.
    has_password: bool = False
    timezone_offset_minutes: int = 0

    class Config:
        from_attributes = True


class StudentProfileResponse(BaseModel):
    id: int
    name: Optional[str] = None
    xp: int
    level: int
    streak: int
    longest_streak: int = 0
    completed_lessons: int
    completed_projects: int
    current_mission_id: Optional[int] = None

    class Config:
        from_attributes = True


class WeeklyStatsResponse(BaseModel):
    """Real, server-computed change since the start of the student's week.

    Every field is a count of things that actually happened. A new account
    reports zeros, and the client renders a neutral state rather than a
    fabricated increase.
    """

    #: UTC instant at which the student's local week began (Monday 00:00).
    week_start: datetime
    xp: int = 0
    lessons_completed: int = 0
    projects_completed: int = 0
    levels_gained: int = 0
    #: Distinct days this week on which the student did something.
    active_days: int = 0
    has_activity: bool = False


class CourseTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    description: Optional[str] = None
    skills: Optional[str] = None


class CourseResponse(BaseModel):
    id: int
    slug: str
    order: int
    #: Roadmap grouping (see app.curriculum.STAGES).
    stage: int = 1
    track: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.beginner
    estimated_hours: int = 0
    icon: Optional[str] = None
    prerequisite_course_id: Optional[int] = None
    translations: List[CourseTranslationResponse]
    modules: List["ModuleResponse"] = []

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
    weekly: WeeklyStatsResponse
    current_mission: Optional[LessonResponse] = None
    course_progress: List[CourseProgressResponse] = []
    recent_achievements: List[UserAchievementResponse] = []
    current_project: Optional[ProjectProgressResponse] = None


class PublicProfileResponse(BaseModel):
    """What one user may see of another's profile.

    Deliberately narrow: no email, no settings, no auth/provider details, no
    per-lesson progress — only what a public profile is meant to show. See
    GET /users/{username} for the visibility rule this backs.
    """

    username: str
    avatar_url: Optional[str] = None
    avatar_image_data: Optional[str] = None
    avatar_config: Optional[str] = None
    avatar_type: str = "upload"
    level: int = 1
    xp: int = 0
    streak: int = 0
    member_since: datetime
    achievements: List[UserAchievementResponse] = []


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
