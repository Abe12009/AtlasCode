import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, Float, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.session import Base


class LanguageEnum(str, enum.Enum):
    en = "en"
    fr = "fr"
    ar = "ar"


class DifficultyEnum(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class MissionStatusEnum(str, enum.Enum):
    locked = "locked"
    ready = "ready"
    in_progress = "in_progress"
    completed = "completed"


class BacTrackEnum(str, enum.Enum):
    """Moroccan Bac (2ème Bac) subject tracks relevant to Orientini's matching.
    Not exhaustive of every track offered nationally -- limited to the
    science/technology tracks Orientini targets."""

    sciences_math_a = "sciences_math_a"
    sciences_math_b = "sciences_math_b"
    pc = "pc"
    svt = "svt"
    ste = "ste"
    stm = "stm"


class InstitutionTypeEnum(str, enum.Enum):
    code_school = "code_school"
    est = "est"
    fst = "fst"
    cpge = "cpge"
    engineering_school = "engineering_school"


class ExerciseTypeEnum(str, enum.Enum):
    multiple_choice = "multiple_choice"
    prediction = "prediction"
    fill_blank = "fill_blank"
    ordering = "ordering"
    debugging = "debugging"
    code_writing = "code_writing"
    visual_programming = "visual_programming"
    circuit_lab = "circuit_lab"
    git_quest = "git_quest"


class NotificationTypeEnum(str, enum.Enum):
    welcome = "welcome"
    xp_earned = "xp_earned"
    lesson_completed = "lesson_completed"
    project_completed = "project_completed"
    achievement_earned = "achievement_earned"


class AuthProviderEnum(str, enum.Enum):
    """How an account proves who it is.

    `password` is AtlasCode's own email/password credential (the only kind that
    has a `hashed_password`). The rest are federated identities verified by
    Firebase; their credential lives with the provider, never here.
    """

    password = "password"
    firebase_password = "firebase_password"
    google = "google"
    github = "github"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    #: Null for accounts that authenticate through a federated provider only.
    #: Never stores a password, only a PBKDF2 hash (see app.core.security).
    hashed_password = Column(String(255), nullable=True)
    #: Firebase's stable user id. Unique so one Firebase identity maps to at
    #: most one AtlasCode account.
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)
    auth_provider = Column(String(32), default=AuthProviderEnum.password.value, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    #: A federated provider's picture URL (Google/GitHub). Only meaningful
    #: when avatar_type == "upload" and avatar_image_data is empty.
    avatar_url = Column(String(512), nullable=True)
    #: A device-uploaded photo, stored as a data: URL (base64). There is no
    #: object storage in this deployment, so small images live directly in
    #: the row; the API enforces a size cap (see app.api.auth) rather than
    #: relying on a column limit. Takes priority over avatar_url when both
    #: are set and avatar_type == "upload".
    avatar_image_data = Column(Text, nullable=True)
    #: The built cartoon avatar's layer choices (skin tone, hair, face shape,
    #: outfit, accessories, ...), serialized as JSON. Structured data, not a
    #: rendered image — the frontend composes it from a fixed set of original
    #: SVG layer assets. Only meaningful when avatar_type == "generated".
    avatar_config = Column(Text, nullable=True)
    #: Which of avatar_url / avatar_config is the active profile picture.
    avatar_type = Column(String(20), default="upload", nullable=False)
    #: Whether this account's public profile (username, level, achievements)
    #: is visible to other signed-in users. Defaults to private: an opt-in
    #: model is the safer default for anything shown to other users.
    profile_visibility = Column(String(20), default="private", nullable=False)
    #: Minutes east of UTC as reported by the client, so day and week
    #: boundaries for streaks and weekly stats match what the student sees.
    timezone_offset_minutes = Column(Integer, default=0, nullable=False)
    preferred_language = Column(Enum(LanguageEnum), default=LanguageEnum.en, nullable=False)
    is_active = Column(Boolean, default=True)
    #: Grants access to the /admin/* moderation endpoints (report review,
    #: suspend/reinstate, avatar clearing). Nobody has this by default --
    #: the first staff account is granted by a direct DB update, the same
    #: pattern this project already uses for anything that has no signup
    #: flow of its own.
    is_staff = Column(Boolean, default=False, nullable=False)
    #: True once this account has been through (or skipped) the first-login
    #: walkthrough. Defaults True so the additive migration backfills every
    #: pre-existing account as "already onboarded" -- only code paths that
    #: create a brand-new account (password register, and the Firebase
    #: creation branch in app.services.accounts) explicitly set this False.
    has_completed_onboarding = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def has_password(self) -> bool:
        """True when this account can sign in with an AtlasCode password.

        Federated-only accounts have no local credential; the UI uses this to
        decide whether to offer "change password" at all.
        """
        return bool(self.hashed_password)

    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    lesson_progress = relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    course_progress = relationship("CourseProgress", back_populates="user", cascade="all, delete-orphan")
    project_progress = relationship("ProjectProgress", back_populates="user", cascade="all, delete-orphan")
    exercise_attempts = relationship("ExerciseAttempt", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    cody_messages = relationship("CodyMessage", back_populates="user", cascade="all, delete-orphan")


class PasswordResetAttempt(Base):
    """One row per /auth/forgot-password call, logged unconditionally.

    Logging every attempt -- whether or not the email belongs to an account,
    and whether or not it's a local-password account -- means the rate limit
    computed from this table never reveals which emails exist: the counters
    look identical either way.
    """

    __tablename__ = "password_reset_attempts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100))
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    completed_lessons = Column(Integer, default=0)
    completed_projects = Column(Integer, default=0)
    current_mission_id = Column(Integer, ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True)
    #: Set from the student's most recent Orientini quiz. Advisory only --
    #: not re-derived automatically if they retake the quiz with a different
    #: answer, since a student could genuinely be unsure/between tracks.
    bac_track = Column(Enum(BacTrackEnum), nullable=True)

    user = relationship("User", back_populates="profile")
    current_mission = relationship("Lesson", foreign_keys=[current_mission_id])


class Section(Base):
    """A degree-style subject area grouping several courses (Programming,
    Networking, Cybersecurity, ...). Coarser than ``Course.track``, which is
    an existing finer-grained roadmap tag — Section is the top-level grouping
    the course catalog UI organizes by. A course's section is optional: the
    foundational/theory courses that underpin every section are deliberately
    left unsectioned.
    """

    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    #: Display position among sections.
    order = Column(Integer, default=0)
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    translations = relationship("SectionTranslation", back_populates="section", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="section", order_by="Course.order")


class SectionTranslation(Base):
    __tablename__ = "section_translations"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    section = relationship("Section", back_populates="translations")

    __table_args__ = (UniqueConstraint("section_id", "language", name="uq_section_language"),)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    #: Global position in the curriculum. Unchanged meaning: courses are always
    #: listed by it.
    order = Column(Integer, default=0)
    #: Which stage of the roadmap the course belongs to (see app.curriculum).
    #: Stages group courses the way a degree groups years.
    stage = Column(Integer, default=1, nullable=False, index=True)
    #: Subject area, e.g. "programming", "theory", "systems", "security".
    track = Column(String(50), nullable=True)
    #: Top-level catalog grouping (see Section). Null for foundational/theory
    #: courses that don't belong to one specific subject area.
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="SET NULL"), nullable=True, index=True)
    difficulty = Column(Enum(DifficultyEnum), default=DifficultyEnum.beginner)
    estimated_hours = Column(Integer, default=0)
    icon = Column(String(50), nullable=True)
    #: The course a student should finish first. Advisory, not a hard lock:
    #: the UI surfaces it and orders around it.
    prerequisite_course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prerequisite_course = relationship("Course", remote_side=[id], foreign_keys=[prerequisite_course_id])
    section = relationship("Section", back_populates="courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order")
    translations = relationship("CourseTranslation", back_populates="course", cascade="all, delete-orphan")
    progress = relationship("CourseProgress", back_populates="course", cascade="all, delete-orphan")


class CourseTranslation(Base):
    __tablename__ = "course_translations"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    skills = Column(Text)

    course = relationship("Course", back_populates="translations")

    __table_args__ = (UniqueConstraint("course_id", "language", name="uq_course_language"),)


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(100), nullable=False)
    order = Column(Integer, default=0)

    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order")
    translations = relationship("ModuleTranslation", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("course_id", "slug", name="uq_module_slug"),)


class ModuleTranslation(Base):
    __tablename__ = "module_translations"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    module = relationship("Module", back_populates="translations")

    __table_args__ = (UniqueConstraint("module_id", "language", name="uq_module_language"),)


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(100), nullable=False)
    order = Column(Integer, default=0)
    difficulty = Column(Enum(DifficultyEnum), default=DifficultyEnum.beginner)
    estimated_minutes = Column(Integer, default=30)
    xp_reward = Column(Integer, default=50)
    is_project = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    module = relationship("Module", back_populates="lessons")
    blocks = relationship("LessonBlock", back_populates="lesson", cascade="all, delete-orphan", order_by="LessonBlock.order")
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan", order_by="Exercise.order")
    translations = relationship("LessonTranslation", back_populates="lesson", cascade="all, delete-orphan")
    progress = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    project = relationship("Project", foreign_keys=[project_id])

    __table_args__ = (UniqueConstraint("module_id", "slug", name="uq_lesson_slug"),)


class LessonTranslation(Base):
    __tablename__ = "lesson_translations"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    story = Column(Text)
    objective = Column(Text)
    skills = Column(Text)

    lesson = relationship("Lesson", back_populates="translations")

    __table_args__ = (UniqueConstraint("lesson_id", "language", name="uq_lesson_language"),)


class LessonBlock(Base):
    __tablename__ = "lesson_blocks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    # Free-form on purpose. Alongside "text" and "code", a lesson may add the
    # Micro-Quest block types "hook", "blueprint" and "exam_tip". A lesson with
    # none of them renders exactly as it always has.
    block_type = Column(String(50), nullable=False)
    order = Column(Integer, default=0)
    content = Column(Text)
    code_example = Column(Text)
    #: JSON for block types that need structure beyond prose (the blueprint's
    #: steps and correct order, the hook's challenge line). Null everywhere else.
    config = Column(Text)

    lesson = relationship("Lesson", back_populates="blocks")
    translations = relationship("LessonBlockTranslation", back_populates="block", cascade="all, delete-orphan")


class LessonBlockTranslation(Base):
    __tablename__ = "lesson_block_translations"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("lesson_blocks.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    content = Column(Text)
    code_example = Column(Text)

    block = relationship("LessonBlock", back_populates="translations")

    __table_args__ = (UniqueConstraint("block_id", "language", name="uq_block_language"),)


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    exercise_type = Column(Enum(ExerciseTypeEnum), nullable=False)
    order = Column(Integer, default=0)
    xp_reward = Column(Integer, default=10)
    starter_code = Column(Text)
    solution_code = Column(Text)
    test_code = Column(Text)
    validation_config = Column(Text)

    lesson = relationship("Lesson", back_populates="exercises")
    translations = relationship("ExerciseTranslation", back_populates="exercise", cascade="all, delete-orphan")
    options = relationship("ExerciseOption", back_populates="exercise", cascade="all, delete-orphan", order_by="ExerciseOption.order")
    attempts = relationship("ExerciseAttempt", back_populates="exercise", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("lesson_id", "order", name="uq_exercise_order"),)


class ExerciseTranslation(Base):
    __tablename__ = "exercise_translations"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    prompt = Column(Text, nullable=False)
    hint = Column(Text)
    explanation = Column(Text)

    exercise = relationship("Exercise", back_populates="translations")

    __table_args__ = (UniqueConstraint("exercise_id", "language", name="uq_exercise_language"),)


class ExerciseOption(Base):
    __tablename__ = "exercise_options"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, default=0)
    is_correct = Column(Boolean, default=False)

    exercise = relationship("Exercise", back_populates="options")
    translations = relationship("ExerciseOptionTranslation", back_populates="option", cascade="all, delete-orphan")


class ExerciseOptionTranslation(Base):
    __tablename__ = "exercise_option_translations"

    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("exercise_options.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    text = Column(Text, nullable=False)

    option = relationship("ExerciseOption", back_populates="translations")

    __table_args__ = (UniqueConstraint("option_id", "language", name="uq_option_language"),)


class ExerciseAttempt(Base):
    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    submitted_code = Column(Text)
    is_correct = Column(Boolean, default=False)
    xp_earned = Column(Integer, default=0)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="exercise_attempts")
    exercise = relationship("Exercise", back_populates="attempts")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(MissionStatusEnum), default=MissionStatusEnum.locked)
    completed_at = Column(DateTime)
    xp_earned = Column(Integer, default=0)
    current_block = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")

    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)


class CourseProgress(Base):
    __tablename__ = "course_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    completed_lessons = Column(Integer, default=0)
    total_lessons = Column(Integer, default=0)
    progress_percent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="course_progress")
    course = relationship("Course", back_populates="progress")

    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course"),)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    order = Column(Integer, default=0)
    difficulty = Column(Enum(DifficultyEnum), default=DifficultyEnum.beginner)
    xp_reward = Column(Integer, default=200)
    prerequisite_lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True)
    prerequisite_project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    translations = relationship("ProjectTranslation", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan", order_by="ProjectTask.order")
    progress = relationship("ProjectProgress", back_populates="project", cascade="all, delete-orphan")
    lesson_ref = relationship("Lesson", foreign_keys=[prerequisite_lesson_id])


class ProjectTranslation(Base):
    __tablename__ = "project_translations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    story = Column(Text)
    objective = Column(Text)
    skills = Column(Text)
    guide = Column(Text)

    project = relationship("Project", back_populates="translations")

    __table_args__ = (UniqueConstraint("project_id", "language", name="uq_project_language"),)


class ProjectTask(Base):
    __tablename__ = "project_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, default=0)
    starter_code = Column(Text)
    validation_code = Column(Text)

    project = relationship("Project", back_populates="tasks")
    translations = relationship("ProjectTaskTranslation", back_populates="task", cascade="all, delete-orphan")


class ProjectTaskTranslation(Base):
    __tablename__ = "project_task_translations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("project_tasks.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    hint = Column(Text)

    task = relationship("ProjectTask", back_populates="translations")

    __table_args__ = (UniqueConstraint("task_id", "language", name="uq_task_language"),)


class ProjectProgress(Base):
    __tablename__ = "project_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(MissionStatusEnum), default=MissionStatusEnum.locked)
    current_task = Column(Integer, default=0)
    completed_at = Column(DateTime)
    xp_earned = Column(Integer, default=0)
    code_snapshot = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="project_progress")
    project = relationship("Project", back_populates="progress")

    __table_args__ = (UniqueConstraint("user_id", "project_id", name="uq_user_project"),)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    icon = Column(String(50))
    xp_reward = Column(Integer, default=0)
    condition_type = Column(String(50))
    condition_value = Column(Integer)

    translations = relationship("AchievementTranslation", back_populates="achievement", cascade="all, delete-orphan")
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class AchievementTranslation(Base):
    __tablename__ = "achievement_translations"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    achievement = relationship("Achievement", back_populates="translations")

    __table_args__ = (UniqueConstraint("achievement_id", "language", name="uq_achievement_language"),)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(NotificationTypeEnum), nullable=False)
    # Small JSON payload of interpolation values only (e.g. {"xp": 50}), never translated
    # text — the frontend renders the message from `type` via its own i18n templates.
    data = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="notifications")


class CodyRoleEnum(str, enum.Enum):
    """Who authored a Cody chat turn."""

    user = "user"
    assistant = "assistant"


class CodyMessage(Base):
    """One turn of a user's persistent chat history with Cody, the CS Q&A
    companion agent. Kept indefinitely (like other user content) but only
    the most recent turns are replayed as LLM context per request -- see
    app.services.cody. Deletes with the owning user (ondelete="CASCADE" +
    the User.cody_messages cascade) so there is nothing left orphaned once
    account deletion exists.
    """

    __tablename__ = "cody_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(CodyRoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    #: Only ever set on assistant-role rows, from the OpenRouter response's
    #: own usage/cost accounting -- see app.services.cody.get_reply. Null on
    #: user-role rows and on any assistant row from before this column
    #: existed, or if the provider didn't return usage data for that call.
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    estimated_cost_usd = Column(Float, nullable=True)

    user = relationship("User", back_populates="cody_messages")


class VisualNode(Base):
    __tablename__ = "visual_nodes"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    node_type = Column(String(50), nullable=False)
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    config = Column(Text)

    exercise = relationship("Exercise", foreign_keys=[exercise_id])


class ReportReasonEnum(str, enum.Enum):
    harassment = "harassment"
    inappropriate_username = "inappropriate_username"
    inappropriate_content = "inappropriate_content"
    spam = "spam"
    other = "other"


class ReportStatusEnum(str, enum.Enum):
    open = "open"
    resolved = "resolved"


class Report(Base):
    """A user-filed report against another account, reviewed by staff.

    reporter_user_id/reported_user_id are SET NULL (not CASCADE) on account
    deletion -- unlike a user's own content, a report is an audit trail of a
    moderation event, and either party deleting their account shouldn't
    erase that history. reported_username is snapshotted at creation time so
    the report stays legible even after the reported account is gone.
    """

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reported_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reported_username = Column(String(100), nullable=False)
    reason = Column(Enum(ReportReasonEnum), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(Enum(ReportStatusEnum), default=ReportStatusEnum.open, nullable=False, index=True)
    resolution_note = Column(Text, nullable=True)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class FeedbackCategoryEnum(str, enum.Enum):
    bug = "bug"
    suggestion = "suggestion"
    other = "other"


class FeedbackSubmission(Base):
    """A free-text bug report / suggestion, reachable from Settings (and the
    signed-in app footer). user_id is nullable and SET NULL on account
    deletion, the same audit-trail rationale as Report above: feedback is a
    record of something that was said, not the user's own content, so it
    outlives the account. Anonymous submission is supported at the schema
    level (ip_address covers rate limiting when there's no user_id) even
    though every current entry point requires being signed in.
    """

    __tablename__ = "feedback_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(Enum(FeedbackCategoryEnum), default=FeedbackCategoryEnum.other, nullable=False)
    message = Column(Text, nullable=False)
    page_path = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ---------------------------------------------------------------------------
# Orientini -- Morocco-specific post-Bac career/institution matching.
#
# Institution "requirement" facts (min average, exam name/format) are
# consequential to a real student's decision, so `data_verified=False` is the
# default and the API/frontend must surface that flag instead of presenting
# unverified numbers as fact. Only flip it once Abdessamad has confirmed the
# figures for that row.
# ---------------------------------------------------------------------------


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    type = Column(Enum(InstitutionTypeEnum), nullable=False, index=True)
    order = Column(Integer, default=0)
    icon = Column(String(50), nullable=True)
    #: JSON object of trait_key -> weight (e.g. {"hands_on": 2, "theory": -1}),
    #: the target vector Orientini's matching compares a student's quiz
    #: vector against. Keys must be a subset of app.services.orientini.TRAIT_KEYS.
    trait_weights = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    translations = relationship("InstitutionTranslation", back_populates="institution", cascade="all, delete-orphan")
    requirement = relationship("InstitutionRequirement", back_populates="institution", uselist=False, cascade="all, delete-orphan")


class InstitutionTranslation(Base):
    __tablename__ = "institution_translations"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    career_outcomes = Column(Text, nullable=True)

    institution = relationship("Institution", back_populates="translations")

    __table_args__ = (UniqueConstraint("institution_id", "language", name="uq_institution_language"),)


class InstitutionRequirement(Base):
    """Structured admission facts for one institution. See module note above
    on `data_verified`."""

    __tablename__ = "institution_requirements"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), unique=True, nullable=False)
    #: JSON list of BacTrackEnum values eligible for this institution, or
    #: null meaning "any track" (e.g. most code schools admit any Bac holder).
    eligible_bac_tracks = Column(Text, nullable=True)
    min_bac_average = Column(Float, nullable=True)
    entrance_exam_name = Column(String(200), nullable=True)
    entrance_exam_format = Column(Text, nullable=True)
    application_window = Column(String(200), nullable=True)
    #: False until a human has confirmed the figures above against an
    #: authoritative source. The UI must show an unverified badge, not the
    #: raw fields, while this is False.
    data_verified = Column(Boolean, default=False, nullable=False)
    verification_notes = Column(Text, nullable=True)

    institution = relationship("Institution", back_populates="requirement")


class OrientiniQuestion(Base):
    __tablename__ = "orientini_questions"

    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    translations = relationship("OrientiniQuestionTranslation", back_populates="question", cascade="all, delete-orphan")
    options = relationship("OrientiniOption", back_populates="question", cascade="all, delete-orphan", order_by="OrientiniOption.order")


class OrientiniQuestionTranslation(Base):
    __tablename__ = "orientini_question_translations"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("orientini_questions.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    text = Column(Text, nullable=False)

    question = relationship("OrientiniQuestion", back_populates="translations")

    __table_args__ = (UniqueConstraint("question_id", "language", name="uq_orientini_question_language"),)


class OrientiniOption(Base):
    __tablename__ = "orientini_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("orientini_questions.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, default=0)
    #: JSON object of trait_key -> weight this answer contributes to the
    #: student's vector (same trait space as Institution.trait_weights).
    trait_weights = Column(Text, nullable=False)

    question = relationship("OrientiniQuestion", back_populates="options")
    translations = relationship("OrientiniOptionTranslation", back_populates="option", cascade="all, delete-orphan")


class OrientiniOptionTranslation(Base):
    __tablename__ = "orientini_option_translations"

    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("orientini_options.id", ondelete="CASCADE"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    text = Column(Text, nullable=False)

    option = relationship("OrientiniOption", back_populates="translations")

    __table_args__ = (UniqueConstraint("option_id", "language", name="uq_orientini_option_language"),)


class OrientiniResult(Base):
    """One completed quiz attempt. Attempts are kept (not upserted) so a
    student can see how their answers/results changed if they retake it."""

    __tablename__ = "orientini_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bac_track = Column(Enum(BacTrackEnum), nullable=True)
    #: JSON object of {question_id: option_id}.
    answers = Column(Text, nullable=False)
    #: JSON list of {institution_id, score, trait_breakdown}, ranked descending.
    scores = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ---------------------------------------------------------------------------
# Duel Arena -- real-time 1v1 coding duels.
#
# Reuses the existing Exercise/grading infrastructure entirely (a duel
# problem is just an existing code exercise, graded through the same
# execute_code() sandbox and per-assertion checklist Step 3 added) rather
# than building a parallel content or grading system. See app.services.duels
# for the matchmaking/race-resolution logic that operates on these tables.
# ---------------------------------------------------------------------------


class DuelStatusEnum(str, enum.Enum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"


class DuelQueueStatusEnum(str, enum.Enum):
    waiting = "waiting"
    matched = "matched"
    cancelled = "cancelled"


class DuelProblem(Base):
    """A curated, duel-appropriate exercise -- deliberately NOT every
    code_writing exercise. Most exercises assume prior lesson context or
    lean on tutorial-specific starter code; only ones explicitly vetted as a
    clean, self-contained problem belong in the duel pool. Same
    authored-allowlist pattern as Circuit Lab and Git Quest content: opted
    in, not auto-included."""

    __tablename__ = "duel_problems"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True)
    #: The duel's own difficulty tag, independent of the exercise's parent
    #: lesson -- a problem can be curated into a harder/easier duel pool than
    #: the lesson it originally came from without touching that lesson.
    difficulty = Column(Enum(DifficultyEnum), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    exercise = relationship("Exercise")


class DuelQueueEntry(Base):
    """One student waiting to be matched. Matching happens synchronously in
    the join-queue request (see app.services.duels.join_queue): the second
    student to join a given difficulty pool always finds the first one
    already waiting, so there's no background worker or scheduler pairing
    people up after the fact."""

    __tablename__ = "duel_queue_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    difficulty = Column(Enum(DifficultyEnum), nullable=False, index=True)
    status = Column(Enum(DuelQueueStatusEnum), default=DuelQueueStatusEnum.waiting, nullable=False, index=True)
    #: Set once matched; the waiting client's poll of queue/status reads this
    #: to learn which duel it was paired into.
    duel_id = Column(Integer, ForeignKey("duels.id", ondelete="SET NULL"), nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    duel = relationship("Duel")

    __table_args__ = (
        #: A real DB-level guarantee against the same user ending up with two
        #: simultaneous 'waiting' rows (e.g. a double-submitted join-queue
        #: request racing itself) -- app.services.duels.join_queue treats the
        #: resulting IntegrityError as "you're already queued", not a crash.
        #: Partial index: only 'waiting' rows are constrained, so a user's
        #: past matched/cancelled entries never collide with a new one.
        Index(
            "uq_one_waiting_entry_per_user",
            "user_id",
            unique=True,
            postgresql_where=(status == DuelQueueStatusEnum.waiting),
            sqlite_where=(status == DuelQueueStatusEnum.waiting),
        ),
    )


class Duel(Base):
    """One live or finished match. `ends_at` is set once at match time and
    is the server-authoritative countdown target -- clients render the
    countdown locally from it and resync periodically, but only the server
    decides a duel is actually over (see app.services.duels)."""

    __tablename__ = "duels"

    id = Column(Integer, primary_key=True, index=True)
    duel_problem_id = Column(Integer, ForeignKey("duel_problems.id", ondelete="RESTRICT"), nullable=False)
    status = Column(Enum(DuelStatusEnum), default=DuelStatusEnum.active, nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    #: Null until someone wins (or the duel times out with no winner).
    #: Set via an atomic conditional UPDATE ("... WHERE status='active'") so
    #: two near-simultaneous correct submissions resolve at the database
    #: level -- exactly one UPDATE affects a row -- rather than trusting
    #: whichever request the server happens to handle first in application
    #: code.
    winner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    duel_problem = relationship("DuelProblem")
    winner = relationship("User", foreign_keys=[winner_user_id])
    participants = relationship("DuelParticipant", back_populates="duel", cascade="all, delete-orphan")
    submissions = relationship("DuelSubmissionAttempt", back_populates="duel", cascade="all, delete-orphan")


class DuelParticipant(Base):
    """One side of a duel. A closed WebSocket sets is_connected=False but
    does NOT end the duel by itself -- see the 30s grace-window/forfeit-claim
    flow in app.services.duels. `forfeited` is set only via the opponent's
    explicit forfeit claim after that window has visibly elapsed, never by
    an automatic server-side timeout."""

    __tablename__ = "duel_participants"

    id = Column(Integer, primary_key=True, index=True)
    duel_id = Column(Integer, ForeignKey("duels.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_connected = Column(Boolean, default=False, nullable=False)
    disconnected_at = Column(DateTime, nullable=True)
    forfeited = Column(Boolean, default=False, nullable=False)

    duel = relationship("Duel", back_populates="participants")
    user = relationship("User")

    __table_args__ = (UniqueConstraint("duel_id", "user_id", name="uq_duel_participant"),)


class DuelSubmissionAttempt(Base):
    """A full grading record, kept server-side for audit purposes -- NEVER
    serialized back to the opponent. The live opponent-progress broadcast
    (see app.services.duels) only ever carries {user_id, passed_count,
    total_count}; nothing in the API layer has a code path that can put this
    row's `code` column in a response addressed to anyone but its own
    submitter."""

    __tablename__ = "duel_submission_attempts"

    id = Column(Integer, primary_key=True, index=True)
    duel_id = Column(Integer, ForeignKey("duels.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    passed_count = Column(Integer, nullable=False)
    total_count = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    duel = relationship("Duel", back_populates="submissions")
    user = relationship("User")