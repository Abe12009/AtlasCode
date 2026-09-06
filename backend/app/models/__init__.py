import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, Float, UniqueConstraint
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


class ExerciseTypeEnum(str, enum.Enum):
    multiple_choice = "multiple_choice"
    prediction = "prediction"
    fill_blank = "fill_blank"
    ordering = "ordering"
    debugging = "debugging"
    code_writing = "code_writing"
    visual_programming = "visual_programming"


class NotificationTypeEnum(str, enum.Enum):
    welcome = "welcome"
    xp_earned = "xp_earned"
    lesson_completed = "lesson_completed"
    project_completed = "project_completed"


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
    avatar_url = Column(String(512), nullable=True)
    #: Minutes east of UTC as reported by the client, so day and week
    #: boundaries for streaks and weekly stats match what the student sees.
    timezone_offset_minutes = Column(Integer, default=0, nullable=False)
    preferred_language = Column(Enum(LanguageEnum), default=LanguageEnum.en, nullable=False)
    is_active = Column(Boolean, default=True)
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

    user = relationship("User", back_populates="profile")
    current_mission = relationship("Lesson", foreign_keys=[current_mission_id])


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
    difficulty = Column(Enum(DifficultyEnum), default=DifficultyEnum.beginner)
    estimated_hours = Column(Integer, default=0)
    icon = Column(String(50), nullable=True)
    #: The course a student should finish first. Advisory, not a hard lock:
    #: the UI surfaces it and orders around it.
    prerequisite_course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prerequisite_course = relationship("Course", remote_side=[id], foreign_keys=[prerequisite_course_id])
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


class VisualNode(Base):
    __tablename__ = "visual_nodes"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    node_type = Column(String(50), nullable=False)
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    config = Column(Text)

    exercise = relationship("Exercise", foreign_keys=[exercise_id])