from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from app.models import LanguageEnum, DifficultyEnum, MissionStatusEnum, ExerciseTypeEnum, NotificationTypeEnum, CodyRoleEnum, ReportReasonEnum, ReportStatusEnum, FeedbackCategoryEnum, BacTrackEnum, InstitutionTypeEnum


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


class DeleteAccountRequest(BaseModel):
    """Permanently delete the signed-in account. Irreversible.

    ``current_password`` is required for password accounts (re-verified
    server-side in app.api.auth) and omitted/ignored for provider-only
    accounts, which have no password to check.
    """

    confirmation: str = Field(min_length=1, max_length=20)
    current_password: Optional[str] = Field(default=None, max_length=100)


class ForgotPasswordRequest(BaseModel):
    """Request a password-reset email. Always answered the same way
    regardless of whether the address belongs to an account -- see
    app.api.auth.forgot_password.
    """

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Complete a password reset using the token from the emailed link."""

    token: str = Field(min_length=16, max_length=2048)
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
    has_completed_onboarding: bool = True

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


class SectionTranslationResponse(BaseModel):
    language: LanguageEnum
    title: str
    description: Optional[str] = None


class SectionResponse(BaseModel):
    id: int
    slug: str
    order: int
    icon: Optional[str] = None
    translations: List[SectionTranslationResponse]

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: int
    slug: str
    order: int
    #: Roadmap grouping (see app.curriculum.STAGES).
    stage: int = 1
    track: Optional[str] = None
    #: Course catalog section (Programming, Networking, ...). Null for
    #: unsectioned foundational/theory courses.
    section_id: Optional[int] = None
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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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
    #: Set by GET /lessons/{id} from the lesson's own module/course
    #: relationship -- not stored columns, so these are absent (None)
    #: anywhere else this schema might theoretically be reused.
    course_title: Optional[str] = None
    #: Numeric id, not slug -- CourseDetail.tsx's route (/app/courses/:courseId)
    #: takes the numeric Course.id, not a slug.
    course_id: Optional[int] = None
    module_title: Optional[str] = None

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
    #: Set by the dashboard endpoint from the course's own translations --
    #: not a stored column, so it's absent (None) anywhere else this schema
    #: might theoretically be reused.
    title: Optional[str] = None

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

    class Config:
        from_attributes = True


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
    #: current_mission's own course/module title -- LessonResponse carries
    #: neither (not even module_id), so the dashboard endpoint resolves these
    #: separately from the ORM object's .module.course relationship.
    current_mission_course_title: Optional[str] = None
    current_mission_module_title: Optional[str] = None
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


class AchievementEarnedResponse(BaseModel):
    """One achievement newly unlocked by this request, already translated
    into the requesting user's language -- returned inline so the frontend
    can show a toast immediately, without waiting on the notification feed.
    """

    slug: str
    icon: str
    title: str
    xp_reward: int


class TestCaseResultResponse(BaseModel):
    assertion: str
    passed: bool
    message: Optional[str] = None


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
    achievements_earned: List[AchievementEarnedResponse] = []
    #: Per-assertion pass/fail, present only for a code_writing/debugging
    #: exercise whose test_code decomposed into a trailing run of plain
    #: asserts (see code_executor._split_assertion_tail). None for every
    #: other exercise type, and for the ones whose test_code didn't
    #: decompose that way -- those keep the single pass/fail in `error`.
    test_results: Optional[List[TestCaseResultResponse]] = None


class VisualProgramRequest(BaseModel):
    nodes: List[dict]
    edges: List[dict]


class VisualProgramResponse(BaseModel):
    python_code: str
    is_valid: bool
    errors: List[str] = []


class CircuitCompileRequest(BaseModel):
    nodes: List[dict]
    edges: List[dict]


class CircuitCompileResponse(BaseModel):
    python_code: str
    is_valid: bool
    errors: List[str] = []


class CircuitEvaluateRequest(BaseModel):
    nodes: List[dict]
    edges: List[dict]
    #: input pin name -> boolean value.
    input_values: Dict[str, bool] = {}


class CircuitEvaluateResponse(BaseModel):
    #: node id -> propagated boolean value, for every node in the graph.
    values: Dict[str, bool] = {}
    #: output pin name -> boolean value.
    outputs: Dict[str, bool] = {}
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


class CodyChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class CodyMessageResponse(BaseModel):
    role: CodyRoleEnum
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class CodyChatResponse(BaseModel):
    reply: CodyMessageResponse
    messages_remaining_this_hour: int


class ReportCreateRequest(BaseModel):
    reason: ReportReasonEnum
    details: Optional[str] = Field(default=None, max_length=2000)


class ReportResponse(BaseModel):
    id: int
    reporter_user_id: Optional[int] = None
    reported_user_id: Optional[int] = None
    reported_username: str
    reason: ReportReasonEnum
    details: Optional[str] = None
    status: ReportStatusEnum
    resolution_note: Optional[str] = None
    resolved_by_user_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportResolveRequest(BaseModel):
    resolution_note: str = Field(min_length=1, max_length=2000)


class FeedbackCreateRequest(BaseModel):
    category: FeedbackCategoryEnum = FeedbackCategoryEnum.other
    message: str = Field(min_length=1, max_length=4000)
    #: Frontend route the user was on, e.g. "/app/dashboard" -- the backend
    #: has no way to know this on its own, so the client reports it.
    page_path: Optional[str] = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    category: FeedbackCategoryEnum
    message: str
    page_path: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CodySpendResponse(BaseModel):
    spend_usd_last_24h: float
    spend_usd_last_7d: float
    spend_usd_last_30d: float
    daily_cap_usd: float


# ---------------------------------------------------------------------------
# Orientini
# ---------------------------------------------------------------------------


class InstitutionRequirementResponse(BaseModel):
    eligible_bac_tracks: Optional[List[BacTrackEnum]] = None
    min_bac_average: Optional[float] = None
    entrance_exam_name: Optional[str] = None
    entrance_exam_format: Optional[str] = None
    application_window: Optional[str] = None
    #: When False, the fields above are placeholders/estimates, not confirmed
    #: facts -- the frontend must show a "needs verification" indicator and
    #: must not present them as reliable admission requirements.
    data_verified: bool = False
    verification_notes: Optional[str] = None

    class Config:
        from_attributes = True


class InstitutionTranslationResponse(BaseModel):
    language: LanguageEnum
    name: str
    description: Optional[str] = None
    career_outcomes: Optional[str] = None


class InstitutionResponse(BaseModel):
    id: int
    slug: str
    type: InstitutionTypeEnum
    order: int
    icon: Optional[str] = None
    translations: List[InstitutionTranslationResponse]
    requirement: Optional[InstitutionRequirementResponse] = None

    class Config:
        from_attributes = True


class OrientiniOptionTranslationResponse(BaseModel):
    language: LanguageEnum
    text: str


class OrientiniOptionResponse(BaseModel):
    id: int
    order: int
    translations: List[OrientiniOptionTranslationResponse]

    class Config:
        from_attributes = True


class OrientiniQuestionTranslationResponse(BaseModel):
    language: LanguageEnum
    text: str


class OrientiniQuestionResponse(BaseModel):
    id: int
    order: int
    translations: List[OrientiniQuestionTranslationResponse]
    options: List[OrientiniOptionResponse]

    class Config:
        from_attributes = True


class OrientiniSubmitRequest(BaseModel):
    #: {question_id: option_id}, one entry per answered question. Unanswered
    #: questions are simply omitted rather than sent with a null option.
    answers: Dict[int, int]
    bac_track: Optional[BacTrackEnum] = None


class OrientiniScoreResponse(BaseModel):
    institution_id: int
    score: float
    eligible: bool
    trait_breakdown: Dict[str, float]


class OrientiniResultResponse(BaseModel):
    id: int
    bac_track: Optional[BacTrackEnum] = None
    scores: List[OrientiniScoreResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class DuelQueueJoinRequest(BaseModel):
    difficulty: DifficultyEnum


class DuelQueueStatusResponse(BaseModel):
    #: "idle" (no active queue entry at all -- distinct from "waiting" so
    #: the client knows there's nothing to poll), "waiting", or "matched".
    status: str
    duel_id: Optional[int] = None


class DuelTicketResponse(BaseModel):
    #: Single-use, ~20s-lived, duel-scoped -- see app.services.duel_tickets.
    #: Not a reusable credential; safe to pass as a WebSocket query param in
    #: a way the student's real access token wouldn't be.
    ticket: str


class DuelParticipantView(BaseModel):
    user_id: int
    username: str
    is_connected: bool
    #: This participant's own best attempt in the duel so far -- see
    #: app.services.duels.best_pass_counts. On the OPPONENT's view, this is
    #: the entire fairness boundary: never anything more specific than these
    #: two numbers, never their code, never which assertions passed.
    passed_count: int
    total_count: int


class DuelStateResponse(BaseModel):
    id: int
    status: str
    started_at: datetime
    ends_at: datetime
    ended_at: Optional[datetime] = None
    winner_user_id: Optional[int] = None
    problem_prompt: str
    problem_starter_code: Optional[str] = None
    me: DuelParticipantView
    opponent: DuelParticipantView


class DuelSubmitRequest(BaseModel):
    code: str


class DuelSubmitResponse(BaseModel):
    is_correct: bool
    passed_count: int
    total_count: int
    won: bool
    duel_status: str
    winner_user_id: Optional[int] = None


LessonResponse.model_rebuild()
ModuleResponse.model_rebuild()
