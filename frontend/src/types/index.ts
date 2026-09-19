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
  | 'visual_programming'
  | 'circuit_lab'
  | 'git_quest';

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
  profile_visibility?: 'public' | 'private';
  has_password?: boolean;
  timezone_offset_minutes?: number;
  has_completed_onboarding?: boolean;
}

export interface PublicProfile {
  username: string;
  avatar_url: string | null;
  avatar_image_data: string | null;
  avatar_config: string | null;
  avatar_type: string;
  level: number;
  xp: number;
  streak: number;
  member_since: string;
  achievements: UserAchievement[];
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
  stage: number;
  track?: string | null;
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

export interface TraceStep {
  line: number;
  /** variable name -> value (already JSON-serializable; a non-primitive is a repr() string). */
  locals: Record<string, unknown>;
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
  /** Break-the-Code's step-through trace of the buggy starter_code. Only
   * ever present on a `debugging` exercise authored with one. */
  trace?: TraceStep[] | null;
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
  /** Breadcrumb data (Dashboard / Course / Lesson), resolved server-side
   * from the lesson's module/course relationship -- null when the module or
   * a translation for it doesn't exist. */
  course_title?: string | null;
  course_id?: number | null;
  module_title?: string | null;
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
  title: string | null;
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
  current_mission_course_title: string | null;
  current_mission_module_title: string | null;
  course_progress: CourseProgress[];
  recent_achievements: UserAchievement[];
  current_project: ProjectProgress | null;
}

export type NotificationType = 'welcome' | 'xp_earned' | 'lesson_completed' | 'project_completed' | 'achievement_earned';

export interface Notification {
  id: number;
  type: NotificationType;
  data: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface CodyMessage {
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface CodyChatResponse {
  reply: CodyMessage;
  messages_remaining_this_hour: number;
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

/** One achievement newly unlocked by the request that returned it, already
 * translated into the requesting user's language. */
export interface AchievementEarned {
  slug: string;
  icon: string;
  title: string;
  xp_reward: number;
}

export interface TestCaseResult {
  assertion: string;
  passed: boolean;
  message: string | null;
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
  achievements_earned?: AchievementEarned[];
  /** Per-assertion pass/fail, present only when the exercise's test_code
   * decomposed into a trailing run of plain asserts server-side -- null
   * otherwise (non-code exercise types, and code exercises whose test_code
   * didn't decompose that way keep only the single pass/fail above). */
  test_results?: TestCaseResult[] | null;
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

// --- Circuit Lab ---------------------------------------------------------

export type GateType = 'and' | 'or' | 'not' | 'nand' | 'nor' | 'xor' | 'xnor';
export type CircuitNodeType = GateType | 'input' | 'output';

export interface CircuitNode {
  id: string;
  type: CircuitNodeType;
  position: { x: number; y: number };
  config: { name?: string };
}

export interface CircuitEdge {
  id: string;
  source: string;
  target: string;
  targetHandle?: string;
}

export interface CircuitGraph {
  nodes: CircuitNode[];
  edges: CircuitEdge[];
}

export interface CircuitCompileResponse {
  python_code: string;
  is_valid: boolean;
  errors: string[];
}

export interface CircuitEvaluateResponse {
  values: Record<string, boolean>;
  outputs: Record<string, boolean>;
  errors: string[];
}

// --- Orientini ---------------------------------------------------------

export type BacTrack = 'sciences_math_a' | 'sciences_math_b' | 'pc' | 'svt' | 'ste' | 'stm';

export type InstitutionType = 'code_school' | 'est' | 'fst' | 'cpge' | 'engineering_school';

export interface InstitutionRequirement {
  eligible_bac_tracks: BacTrack[] | null;
  min_bac_average: number | null;
  entrance_exam_name: string | null;
  entrance_exam_format: string | null;
  application_window: string | null;
  /** False means the fields above are placeholders, not confirmed facts --
   * render a "needs verification" indicator instead of presenting them as
   * reliable admission requirements. */
  data_verified: boolean;
  verification_notes: string | null;
}

export interface InstitutionTranslation {
  language: Language;
  name: string;
  description: string | null;
  career_outcomes: string | null;
}

export interface Institution {
  id: number;
  slug: string;
  type: InstitutionType;
  order: number;
  icon?: string | null;
  translations: InstitutionTranslation[];
  requirement: InstitutionRequirement | null;
}

export interface OrientiniOptionTranslation {
  language: Language;
  text: string;
}

export interface OrientiniOption {
  id: number;
  order: number;
  translations: OrientiniOptionTranslation[];
}

export interface OrientiniQuestionTranslation {
  language: Language;
  text: string;
}

export interface OrientiniQuestion {
  id: number;
  order: number;
  translations: OrientiniQuestionTranslation[];
  options: OrientiniOption[];
}

export interface OrientiniSubmitRequest {
  answers: Record<number, number>;
  bac_track?: BacTrack | null;
}

export interface OrientiniScore {
  institution_id: number;
  score: number;
  eligible: boolean;
  trait_breakdown: Record<string, number>;
}

export interface OrientiniResult {
  id: number;
  bac_track: BacTrack | null;
  scores: OrientiniScore[];
  created_at: string;
}

// --- Git & Open-Source Quests ---------------------------------------------

export interface GitCommit {
  parents: string[];
  message: string;
  files: Record<string, string>;
}

export interface GitMergeInProgress {
  other_branch: string;
  other_commit: string;
  conflicted_files: string[];
}

export interface GitQuestState {
  commits: Record<string, GitCommit>;
  branches: Record<string, string | null>;
  remote_branches: Record<string, string>;
  head: { branch: string } | { commit: string } | null;
  working_files: Record<string, string>;
  staged_files: Record<string, string>;
  merge_in_progress: GitMergeInProgress | null;
  initialized: boolean;
}

export type GitQuestAction =
  | { kind: 'command'; value: string }
  | { kind: 'edit'; file: string; content: string };

export interface GitQuestExecuteResponse {
  state: GitQuestState;
  output: string;
  error: string | null;
}

export type DuelDifficulty = 'beginner' | 'intermediate' | 'advanced';

export interface DuelQueueStatusResponse {
  status: 'idle' | 'waiting' | 'matched';
  duel_id: number | null;
}

export interface DuelTicketResponse {
  ticket: string;
}

export interface DuelParticipantView {
  user_id: number;
  username: string;
  is_connected: boolean;
  passed_count: number;
  total_count: number;
}

export interface DuelStateResponse {
  id: number;
  status: 'active' | 'completed' | 'abandoned';
  started_at: string;
  ends_at: string;
  ended_at: string | null;
  winner_user_id: number | null;
  problem_prompt: string;
  problem_starter_code: string | null;
  me: DuelParticipantView;
  opponent: DuelParticipantView;
}

export interface DuelSubmitResponse {
  is_correct: boolean;
  passed_count: number;
  total_count: number;
  won: boolean;
  duel_status: 'active' | 'completed' | 'abandoned';
  winner_user_id: number | null;
}

/** The only shapes ever pushed over the WebSocket -- never carries code,
 * matching the backend's fairness guarantee (see duel_realtime.py). */
export type DuelSocketMessage =
  | { type: 'opponent_connected' }
  | { type: 'opponent_disconnected' }
  | { type: 'opponent_progress'; passed_count: number; total_count: number }
  | { type: 'duel_ended'; winner_user_id: number; reason: string };
