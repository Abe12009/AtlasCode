export type Language = 'en' | 'fr' | 'ar';

export type Difficulty = 'beginner' | 'intermediate' | 'advanced';

export type MissionStatus = 'locked' | 'ready' | 'in_progress' | 'completed';

export type ExerciseType =
  | 'multiple_choice'
  | 'prediction'
  | 'fill_blank'
  | 'ordering'
  | 'debugging'
  | 'code_writing'
  | 'visual_programming';

export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  preferred_language: Language;
  is_active: boolean;
  created_at: string;
  auth_provider?: string;
  email_verified?: boolean;
  avatar_url?: string | null;
  avatar_image_data?: string | null;
  avatar_config?: string | null;
  avatar_type?: string;
  has_password?: boolean;
  timezone_offset_minutes?: number;
}

export interface StudentProfile {
  id: number;
  name: string | null;
  xp: number;
  level: number;
  streak: number;
  completed_lessons: number;
  completed_projects: number;
  current_mission_id: number | null;
}

export interface CourseTranslation {
  language: Language;
  title: string;
  description: string | null;
  skills: string | null;
}

export interface Course {
  id: number;
  slug: string;
  order: number;
  section_id?: number | null;
  difficulty: Difficulty;
  estimated_hours?: number;
  icon?: string | null;
  prerequisite_course_id?: number | null;
  translations: CourseTranslation[];
  modules?: Module[];
}

export interface SectionTranslation {
  language: Language;
  title: string;
  description: string | null;
}

export interface Section {
  id: number;
  slug: string;
  order: number;
  icon?: string | null;
  translations: SectionTranslation[];
}

export interface ModuleTranslation {
  language: Language;
  title: string;
  description: string | null;
}

export interface Module {
  id: number;
  slug: string;
  order: number;
  translations: ModuleTranslation[];
  lessons: Lesson[];
}

export interface LessonBlockTranslation {
  language: Language;
  content: string | null;
  code_example: string | null;
}

export interface LessonBlock {
  id: number;
  block_type: string;
  order: number;
  content: string | null;
  code_example: string | null;
  /** JSON string for Micro-Quest block types ('hook' | 'blueprint' | 'exam_tip');
   * null for ordinary text/code blocks. Parse with the block's own type guard. */
  config: string | null;
  translations: LessonBlockTranslation[];
}

export interface ExerciseOptionTranslation {
  language: Language;
  text: string;
}

export interface ExerciseOption {
  id: number;
  order: number;
  translations: ExerciseOptionTranslation[];
}

export interface ExerciseTranslation {
  language: Language;
  prompt: string;
  hint: string | null;
  explanation: string | null;
}

export interface Exercise {
  id: number;
  exercise_type: ExerciseType;
  order: number;
  xp_reward: number;
  starter_code: string | null;
  translations: ExerciseTranslation[];
  options: ExerciseOption[];
  course_id?: number;
  course_title?: string;
  lesson_id?: number;
  lesson_title?: string;
}

export interface LessonTranslation {
  language: Language;
  title: string;
  story: string | null;
  objective: string | null;
  skills: string | null;
}

export interface Lesson {
  id: number;
  slug: string;
  order: number;
  difficulty: Difficulty;
  estimated_minutes: number;
  xp_reward: number;
  is_project: boolean;
  module_id: number;
  translations: LessonTranslation[];
  blocks: LessonBlock[];
  exercises: Exercise[];
  status?: 'completed' | 'current' | 'available' | 'locked';
}

export interface LessonProgress {
  id: number;
  lesson_id: number;
  status: MissionStatus;
  completed_at: string | null;
  xp_earned: number;
  current_block: number;
}

export interface CourseProgress {
  course_id: number;
  completed_lessons: number;
  total_lessons: number;
  progress_percent: number;
}

export interface ProjectTaskTranslation {
  language: Language;
  title: string;
  description: string | null;
  hint: string | null;
}

export interface ProjectTask {
  id: number;
  order: number;
  starter_code: string | null;
  translations: ProjectTaskTranslation[];
}

export interface ProjectTranslation {
  language: Language;
  title: string;
  story: string | null;
  objective: string | null;
  skills: string | null;
  guide: string | null;
}

export interface Project {
  id: number;
  slug: string;
  order: number;
  difficulty: Difficulty;
  xp_reward: number;
  prerequisite_lesson_id: number | null;
  prerequisite_project_id: number | null;
  translations: ProjectTranslation[];
  tasks: ProjectTask[];
}

export interface ProjectProgress {
  id: number;
  project_id: number;
  status: MissionStatus;
  current_task: number;
  completed_at: string | null;
  xp_earned: number;
  code_snapshot: string | null;
}

export interface AchievementTranslation {
  language: Language;
  title: string;
  description: string | null;
}

export interface Achievement {
  id: number;
  slug: string;
  icon: string | null;
  xp_reward: number;
  translations: AchievementTranslation[];
}

export interface UserAchievement {
  id: number;
  achievement_id: number;
  earned_at: string;
  achievement: Achievement;
}

export interface WeeklyStats {
  week_start: string;
  xp: number;
  lessons_completed: number;
  projects_completed: number;
  levels_gained: number;
  active_days: number;
  has_activity: boolean;
}

export interface DashboardData {
  user: User;
  profile: StudentProfile;
  weekly: WeeklyStats;
  current_mission: Lesson | null;
  course_progress: CourseProgress[];
  recent_achievements: UserAchievement[];
  current_project: ProjectProgress | null;
}

export type NotificationType = 'welcome' | 'xp_earned' | 'lesson_completed' | 'project_completed';

export interface Notification {
  id: number;
  type: NotificationType;
  data: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface ExerciseSubmitRequest {
  exercise_id: number;
  /** Code exercises. Non-code types send the field matching how they are answered. */
  code?: string;
  selected_option_id?: number;
  ordered_option_ids?: number[];
  answer?: string;
  blanks?: string[];
}

export interface ExerciseSubmitResponse {
  is_correct: boolean;
  xp_earned: number;
  feedback: string;
  output: string | null;
  error: string | null;
  /** True once this user has ever solved the exercise. */
  is_completed?: boolean;
  lesson_completed?: boolean;
}

export interface CodeExecutionRequest {
  code: string;
  test_code?: string;
}

export interface CodeExecutionResponse {
  success: boolean;
  output: string;
  error: string | null;
  execution_time: number;
}

export interface VisualProgramRequest {
  nodes: Record<string, unknown>[];
  edges: Record<string, unknown>[];
}

export interface VisualProgramResponse {
  python_code: string;
  is_valid: boolean;
  errors: string[];
}

export interface CodeValidationRequest {
  code: string;
}

export interface CodeValidationResponse {
  is_valid: boolean;
  errors: string[];
}