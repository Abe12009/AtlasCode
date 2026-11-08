import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { lessonsApi, exercisesApi, coursesApi } from '../api/services';
import { ArrowLeft, CheckCircle, Clock, Target, Code, ChevronLeft, ChevronRight, Copy, Check, RotateCcw, Terminal, Sparkles, Compass, Lightbulb, Lock, AlertTriangle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import type { Course, Exercise, ExerciseSubmitRequest, ExerciseSubmitResponse, Lesson, LessonBlock } from '../types';
import { Badge, Button, cn, Progress, Skeleton, CodeEditor, StatusBadge, XPBadge } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';
import { ExercisePanel } from '../components/ExercisePanel';
import { MicroQuestLesson } from '../components/microquest/MicroQuestLesson';
import { LESSON_SHELL_HEIGHT_CLASS } from '../lib/layout';
import { showXpToast } from '../components/XpToast';
import { showAchievementToast } from '../components/AchievementToast';
import { errorDetail, errorStatus, isLockedError } from '../lib/apiError';

/**
 * The course a locked lesson belongs to, and the lesson that opens it.
 *
 * A 403 body carries only a message, so this reads the catalog (GET /courses),
 * which already reports a real per-lesson status. The unlocking lesson is the
 * one in progress if there is one, else the furthest one still open -- both
 * straight from the status the backend computed, nothing re-derived here.
 * Returns null when the lesson belongs to no course the student can see, and
 * the locked screen then falls back to the catalog link.
 */
function findLockedContext(
  courses: Course[] | undefined,
  lessonId: string | undefined,
): { courseId: number; unlockingLesson: Lesson | null } | null {
  if (!courses || !lessonId) return null;
  const id = Number(lessonId);
  for (const course of courses) {
    const sequence = (course.modules ?? []).flatMap((m) => m.lessons ?? []);
    if (!sequence.some((l) => l.id === id)) continue;
    const unlockingLesson =
      sequence.find((l) => l.status === 'current') ??
      [...sequence].reverse().find((l) => l.status && l.status !== 'locked') ??
      null;
    return { courseId: course.id, unlockingLesson };
  }
  return null;
}

export function LessonDetail() {
  const { t, isRTL, currentLanguage } = useTranslation();
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0);
  const [exerciseResults, setExerciseResults] = useState<Record<number, ExerciseSubmitResponse>>({});
  const [terminalOutput, setTerminalOutput] = useState<string>('');
  const [terminalError, setTerminalError] = useState<string>('');

  const { data: lesson, isLoading, error } = useQuery({
    queryKey: ['lesson', lessonId, currentLanguage],
    queryFn: () => lessonsApi.getById(Number(lessonId), currentLanguage),
    enabled: !!lessonId,
  });

  // POST /lessons/{id}/start used to be fire-and-forget with `.catch(() => {})`,
  // which swallowed every failure -- including the 403 that says this lesson is
  // locked, and including a real server error, leaving the student on a lesson
  // whose progress row was never created and no way to know.
  // Carries the lesson it belongs to, so navigating to another lesson drops a
  // stale failure during render -- rather than needing a synchronous
  // setState(null) inside the effect below, which would start a second render
  // and still show the previous lesson's error for the first one.
  const [startFailure, setStartFailure] = useState<
    { lessonId: string; status?: number; detail?: string } | null
  >(null);

  useEffect(() => {
    if (!lessonId) return;
    lessonsApi.start(Number(lessonId)).catch((err: unknown) => {
      setStartFailure({ lessonId, status: errorStatus(err), detail: errorDetail(err) });
    });
  }, [lessonId]);

  const startError = startFailure?.lessonId === lessonId ? startFailure : null;

  const runMutation = useMutation({
    mutationFn: ({ exerciseId, code }: { exerciseId: number; code: string }) =>
      exercisesApi.run(exerciseId, { code, exercise_id: exerciseId }),
    onSuccess: (data, variables) => {
      setExerciseResults((prev) => ({ ...prev, [variables.exerciseId]: data }));
      if (data.output) setTerminalOutput(data.output);
      if (data.error) setTerminalError(data.error);
    },
    onError: (error: any) => {
      setTerminalError(error.response?.data?.detail || 'Execution failed');
    },
  });

  const submitMutation = useMutation({
    mutationFn: ({ exerciseId, ...answer }: { exerciseId: number } & Omit<ExerciseSubmitRequest, 'exercise_id'>) =>
      exercisesApi.submit(exerciseId, { ...answer, exercise_id: exerciseId }),
    onSuccess: (data, variables) => {
      setExerciseResults((prev) => ({ ...prev, [variables.exerciseId]: data }));
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['lesson', lessonId] });
      if (data.is_correct) queryClient.invalidateQueries({ queryKey: ['notifications'] });
      if (data.is_correct && data.xp_earned > 0) showXpToast(data.xp_earned);
      data.achievements_earned?.forEach((a) => showAchievementToast(a.icon, a.title, a.xp_reward));
      if (data.output) setTerminalOutput(data.output);
    },
    onError: (error: any) => {
      setTerminalError(error.response?.data?.detail || 'Submission failed');
    },
  });

  // A 403 on the lesson itself -- or on its /start -- is the sequence gate,
  // not a missing lesson. Both are checked because either call can be the one
  // that refuses first.
  const isLocked = isLockedError(error) || startError?.status === 403;

  // Fetched only while locked. A 403 body carries nothing but a message, so
  // the course this lesson belongs to and the lesson that opens it have to
  // come from the catalog, which already reports a real per-lesson status.
  const { data: coursesForLocked } = useQuery({
    queryKey: ['courses', currentLanguage],
    queryFn: () => coursesApi.getAll(currentLanguage),
    enabled: isLocked,
  });

  const lockedContext = findLockedContext(coursesForLocked, lessonId);

  if (isLoading) {
    return (
      <div className={cn(LESSON_SHELL_HEIGHT_CLASS, 'flex flex-col bg-bg-primary')} dir={isRTL ? 'rtl' : 'ltr'}>
        <header className="bg-bg-secondary/80 backdrop-blur-xl border-b border-border-primary/50 px-4 py-3 flex-shrink-0">
          <div className="max-w-full mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 animate-pulse bg-bg-tertiary rounded-lg" />
              <div className="h-6 w-40 animate-pulse bg-bg-tertiary rounded" />
            </div>
            <div className="h-8 w-48 animate-pulse bg-bg-tertiary rounded" />
          </div>
        </header>
        <div className="flex-1 flex overflow-hidden">
          <aside className="w-64 bg-bg-secondary/50 border-r border-border-primary/50 overflow-y-auto flex-shrink-0 hidden lg:block">
            <nav className="p-4 space-y-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-12 animate-pulse bg-bg-tertiary rounded-lg" />
              ))}
            </nav>
          </aside>
          <main className="flex-1 min-w-0 overflow-x-hidden overflow-y-auto p-6 lg:p-8">
            <div className="max-w-4xl mx-auto space-y-6">
              <Skeleton variant="text" width="40%" height={16} data-testid="loading-spinner" />
              <Skeleton variant="rectangular" width="100%" height={300} />
              <div className="flex gap-3">
                <Skeleton variant="rectangular" width={160} height={44} />
                <Skeleton variant="rectangular" width={160} height={44} />
              </div>
            </div>
          </main>
        </div>
      </div>
    );
  }

  // A locked lesson is a 403, not a 404: a pasted deep link has to say "this
  // opens later" rather than "no such lesson", which is both wrong and
  // unactionable. Checked before the not-found branch below, which would
  // otherwise swallow it -- `error` is truthy for either.
  if (isLocked) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center gap-4" dir={isRTL ? 'rtl' : 'ltr'}>
        <div className="p-4 rounded-full bg-bg-tertiary border border-border-primary/50">
          <Lock className="h-8 w-8 text-text-tertiary" aria-hidden="true" />
        </div>
        <h1 className="text-xl font-semibold text-text-primary" data-testid="lesson-locked-title">
          {t('courses.locked')}
        </h1>
        <p className="text-text-secondary max-w-md">{t('errors.lesson_locked')}</p>
        <div className="flex flex-col sm:flex-row items-center gap-3">
          {lockedContext?.unlockingLesson && (
            <Link
              to={`/app/lessons/${lockedContext.unlockingLesson.id}`}
              data-testid="locked-unlocking-lesson"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 btn-primary-gradient text-white font-semibold rounded-xl transition-all"
            >
              <span>{t('lessons.go_to_unlocking_lesson')}</span>
            </Link>
          )}
          {lockedContext?.courseId ? (
            <Link
              to={`/app/courses/${lockedContext.courseId}`}
              data-testid="locked-back-to-course"
              className="text-primary-400 hover:text-primary-300"
            >
              {t('lessons.back_to_course')}
            </Link>
          ) : (
            <Link to="/app/courses" className="text-primary-400 hover:text-primary-300">
              {t('common.back_to_courses')}
            </Link>
          )}
        </div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="text-center py-12" dir={isRTL ? 'rtl' : 'ltr'}>
        <p className="text-error-600 dark:text-error-400">{t('lessons.not_found')}</p>
        <Link to="/app/courses" className="mt-4 inline-block text-primary-400 hover:text-primary-300">
          {t('common.back_to_courses')}
        </Link>
      </div>
    );
  }

  const isMicroQuest =
    (lesson.blocks || []).some((b) => b.block_type === 'hook') &&
    (lesson.blocks || []).some((b) => b.block_type === 'blueprint');
  if (isMicroQuest) {
    return <MicroQuestLesson lesson={lesson} currentLanguage={currentLanguage} />;
  }

  const blocks = lesson.blocks || [];
  const exercises = lesson.exercises || [];
  const currentBlock = blocks[currentBlockIndex];
  const isExerciseStep = currentBlockIndex >= blocks.length;
  const currentExercise = isExerciseStep
    ? exercises.find((ex) => ex.order === currentBlockIndex - blocks.length + 1)
    : undefined;
  const totalSteps = blocks.length + exercises.length;
  const hasPrev = currentBlockIndex > 0;

  const goToNext = () => {
    if (currentBlockIndex < totalSteps - 1) {
      setCurrentBlockIndex((prev) => prev + 1);
      setTerminalOutput('');
      setTerminalError('');
    } else {
      navigate('/app/dashboard');
    }
  };

  const goToPrev = () => {
    if (currentBlockIndex > 0) {
      setCurrentBlockIndex((prev) => prev - 1);
      setTerminalOutput('');
      setTerminalError('');
    }
  };

  return (
    <div className={cn(LESSON_SHELL_HEIGHT_CLASS, 'flex flex-col overflow-hidden bg-bg-primary')} dir={isRTL ? 'rtl' : 'ltr'}>
      <header className="bg-bg-secondary/80 backdrop-blur-xl border-b border-border-primary/50 px-4 py-3 flex-shrink-0 space-y-2">
        <div className="max-w-full mx-auto flex items-center justify-between gap-3">
          {/* min-w-0 lets this column shrink so the title's truncate applies;
              without it the header forces the whole page wider than a 320px
              viewport and pushes the lesson content off-screen. */}
          <div className="flex items-center gap-4 min-w-0 flex-1">
            <Link
              to="/app/courses"
              className="p-2 rounded-lg hover:bg-bg-tertiary/50 transition-colors text-text-tertiary hover:text-text-primary flex-shrink-0"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div className="min-w-0">
              <nav
                aria-label={t('lessons.breadcrumb')}
                className="hidden sm:flex items-center gap-1.5 text-xs text-text-tertiary mb-0.5"
              >
                <Link to="/app/dashboard" className="hover:text-text-secondary truncate">
                  {t('navigation.dashboard')}
                </Link>
                {lesson.course_title && (
                  <>
                    <ChevronRight className={cn('h-3 w-3 flex-shrink-0', isRTL && 'rotate-180')} aria-hidden="true" />
                    {lesson.course_id ? (
                      <Link to={`/app/courses/${lesson.course_id}`} className="hover:text-text-secondary truncate max-w-[10rem]">
                        {lesson.course_title}
                      </Link>
                    ) : (
                      <span className="truncate max-w-[10rem]">{lesson.course_title}</span>
                    )}
                  </>
                )}
                <ChevronRight className={cn('h-3 w-3 flex-shrink-0', isRTL && 'rotate-180')} aria-hidden="true" />
                <span className="text-text-secondary truncate max-w-[12rem]">{lesson.translations[0]?.title}</span>
              </nav>
              <p className="text-xs text-text-tertiary uppercase tracking-wide sm:hidden">{t('lessons.lesson')} {lesson.order}</p>
              <h1 className="font-semibold text-text-primary truncate max-w-md">
                {lesson.translations[0]?.title}
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm text-text-tertiary flex-shrink-0">
            {/* Duration and difficulty are also shown on the course page, so
                they step aside on the narrowest screens to keep the XP badge. */}
            <span className="hidden sm:flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>{lesson.estimated_minutes} {t('common.min')}</span>
            </span>
            <span className="hidden sm:flex items-center gap-1">
              <Target className="h-4 w-4" />
              <span>{t(`courses.difficulty_level.${lesson.difficulty}`)}</span>
            </span>
            <XPBadge xp={lesson.xp_reward} size="sm" />
          </div>
        </div>

        <div className="max-w-full mx-auto flex items-center gap-3">
          <span className="text-xs text-text-tertiary flex-shrink-0 tabular-nums">
            {t('lessons.step_of', { current: currentBlockIndex + 1, total: totalSteps })}
          </span>
          <Progress
            value={((currentBlockIndex + 1) / totalSteps) * 100}
            size="sm"
            variant="primary"
            showLabel={false}
            className="flex-1 max-w-xs"
          />
        </div>

        {/* A non-403 /start failure is shown rather than swallowed: the lesson
            itself loaded, so the student can read on, but their progress row
            was not created and the server's own reason is worth seeing. The
            403 case never reaches here -- it renders the locked state above. */}
        {startError && startError.status !== 403 && (
          <div
            role="alert"
            data-testid="lesson-start-error"
            className="max-w-full mx-auto flex items-center gap-2 rounded-lg border border-warning-500/30 bg-warning-500/10 px-3 py-2 text-xs text-warning-400"
          >
            <AlertTriangle className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
            <span>{startError.detail || t('errors.generic')}</span>
          </div>
        )}
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-64 bg-bg-secondary/50 border-r border-border-primary/50 overflow-y-auto flex-shrink-0 hidden lg:block">
          <nav className="p-4 space-y-1.5" aria-label={t('lessons.lesson_navigation')}>
            <div className="px-2 py-2 text-xs font-semibold text-text-tertiary uppercase tracking-wider">
              {t('lessons.content')}
            </div>
            {blocks.map((block, index) => (
              <button
                key={block.id}
                onClick={() => setCurrentBlockIndex(index)}
                className={cn(
                  'w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-fast flex items-center gap-2',
                  index === currentBlockIndex
                    ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                    : index < currentBlockIndex
                    ? 'text-text-secondary hover:bg-bg-tertiary/50'
                    : 'text-text-tertiary hover:bg-bg-tertiary/50'
                )}
              >
                <div className={cn(
                  'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0',
                  index === currentBlockIndex
                    ? 'bg-primary-500 text-white'
                    : index < currentBlockIndex
                    ? 'bg-success-500/20 text-success-400'
                    : 'bg-bg-tertiary text-text-tertiary'
                )}>
                  {index < currentBlockIndex ? <Check className="h-4 w-4" /> : index + 1}
                </div>
                <span className="truncate capitalize">
                  {block.block_type === 'code'
                    ? t('lessons.code')
                    : block.block_type === 'text'
                    ? t('lessons.read')
                    : block.block_type === 'hook'
                    ? t('lessons.scenario')
                    : block.block_type === 'exam_tip'
                    ? t('lessons.tip')
                    : t('lessons.practice')}
                </span>
              </button>
            ))}
            {exercises.length > 0 && (
              <>
                <div className="px-2 py-2 text-xs font-semibold text-text-tertiary uppercase tracking-wider mt-2">
                  {t('lessons.practice')}
                </div>
                {exercises.map((exercise, index) => (
                  <button
                    key={exercise.id}
                    onClick={() => setCurrentBlockIndex(blocks.length + index)}
                    className={cn(
                      'w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-fast flex items-center gap-2',
                      blocks.length + index === currentBlockIndex
                        ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                        : index < currentBlockIndex - blocks.length
                        ? 'text-success-400 hover:bg-success-500/10'
                        : 'text-text-tertiary hover:bg-bg-tertiary/50'
                    )}
                  >
                    <div className={cn(
                      'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0',
                      blocks.length + index === currentBlockIndex
                        ? 'bg-primary-500 text-white'
                        : index < currentBlockIndex - blocks.length
                        ? 'bg-success-500/20 text-success-400'
                        : 'bg-bg-tertiary text-text-tertiary'
                    )}>
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <span className="truncate">{t('lessons.exercise')} {index + 1}</span>
                  </button>
                ))}
              </>
            )}
          </nav>
        </aside>

        <main className="flex-1 min-w-0 flex flex-col overflow-hidden">
          <div
            className={cn(
              'flex-1 min-w-0',
              isExerciseStep
                ? 'overflow-hidden p-4 lg:p-6 flex flex-col'
                : 'overflow-x-hidden overflow-y-auto p-6 lg:p-8'
            )}
          >
            <div className={cn(isExerciseStep ? 'max-w-6xl mx-auto w-full flex-1 min-h-0 flex flex-col' : 'max-w-4xl mx-auto space-y-6')}>
              {!isExerciseStep ? (
                <LessonBlockView
                  block={currentBlock}
                  index={currentBlockIndex}
                  currentIndex={currentBlockIndex}
                  total={totalSteps}
                  onNext={goToNext}
                  onPrev={goToPrev}
                  hasNext={currentBlockIndex < totalSteps - 1}
                  hasPrev={currentBlockIndex > 0}
                />
              ) : (
                <ExerciseView
                  exercise={currentExercise!}
                  onSubmit={submitMutation.mutate}
                  onRun={runMutation.mutate}
                  result={exerciseResults[currentExercise!.id]}
                  isSubmitting={submitMutation.isPending}
                  isRunning={runMutation.isPending}
                  index={currentBlockIndex}
                  total={totalSteps}
                  onNext={goToNext}
                  onPrev={goToPrev}
                  hasNext={false}
                  hasPrev={currentBlockIndex > 0}
                  terminalOutput={terminalOutput}
                  terminalError={terminalError}
                  onClearTerminal={() => { setTerminalOutput(''); setTerminalError(''); }}
                />
              )}
            </div>
          </div>

          {!isExerciseStep && (
            <div className="border-t border-border-primary/50 p-4 lg:p-6 bg-bg-secondary/30 backdrop-blur-sm">
              <div className="max-w-4xl mx-auto flex items-center justify-between gap-2">
                <Button
                  variant="ghost"
                  onClick={goToPrev}
                  disabled={!hasPrev}
                  leftIcon={isRTL ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
                  data-testid="lesson-nav-prev"
                >
                  {t('lessons.previous')}
                </Button>
                <div className="hidden sm:flex items-center gap-3 min-w-0 flex-1 justify-center">
                  <Progress
                    value={((currentBlockIndex + 1) / totalSteps) * 100}
                    size="md"
                    variant="primary"
                    showLabel
                    className="w-full max-w-48"
                  />
                </div>
                {currentBlockIndex < totalSteps - 1 ? (
                  <Button
                    onClick={goToNext}
                    rightIcon={isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    data-testid="lesson-nav-next"
                  >
                    {t('lessons.next')}
                  </Button>
                ) : (
                  <Link
                    to="/app/dashboard"
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-accent-700 to-accent-800 hover:from-accent-800 hover:to-accent-900 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-glow-accent"
                    data-testid="lesson-nav-finish"
                  >
                    <span>{t('lessons.finish_lesson')}</span>
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

interface LessonBlockViewProps {
  block: LessonBlock;
  index: number;
  /** The step the student is on, so the badge below states this block's real
   * position in the walk instead of a hardcoded guess. */
  currentIndex: number;
  total: number;
  onNext: () => void;
  onPrev: () => void;
  hasNext: boolean;
  hasPrev: boolean;
}

function LessonBlockView({ block, index, currentIndex, total, onNext, onPrev, hasPrev }: LessonBlockViewProps) {
  // The API returns the block's translations already filtered to the requested
  // language. Prefer them; fall back to the base columns for blocks that have
  // no translation row yet (the original courses store English there).
  const translation = block.translations?.[0];
  const content = translation?.content ?? block.content;
  const codeExample = translation?.code_example ?? block.code_example;
  const { t, isRTL } = useTranslation();

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center gap-2">
        {/* Same rule the sidebar uses (see the block buttons above): behind the
            student is done, where they are is current. Never 'locked' -- the
            sidebar lets them jump to any block freely, and gating is per
            lesson, not per block. This component is only ever handed the
            current block today, so in practice this reads 'current'; the
            comparison is spelled out so it stays right if it is ever handed
            another one. The old `index < 2 ? ... : index === 2 ? ...` compared
            the live step against the literal 2 and so claimed the first two
            steps of every lesson were already completed. */}
        <StatusBadge
          status={index < currentIndex ? 'completed' : index === currentIndex ? 'current' : 'available'}
          size="sm"
        />
        <Badge variant="outline" size="sm" className="border-border-primary/50">
          {block.block_type}
        </Badge>
      </div>

      {block.block_type === 'text' && (
        <div className="prose dark:prose-invert max-w-none">
          <div className="bg-bg-secondary/30 rounded-xl p-6 border border-border-primary/50">
            <p className="whitespace-pre-wrap text-text-secondary leading-relaxed text-lg">
              {content}
            </p>
          </div>
        </div>
      )}

      {block.block_type === 'code' && codeExample && (
        <div className="space-y-3">
          <p className="text-text-secondary">{content}</p>
          <CodeEditor
            code={codeExample}
            onChange={() => {}}
            language="python"
            readOnly={true}
            showLineNumbers
            minHeight="200px"
            showToolbar
          />
        </div>
      )}

      {block.block_type === 'hook' && (
        <div className="rounded-xl border border-primary-500/30 bg-primary-500/5 p-6">
          <div className="mb-3 flex items-center gap-2 text-primary-400">
            <Compass className="h-5 w-5" aria-hidden="true" />
            <span className="text-sm font-semibold uppercase tracking-wide">{t('lessons.scenario')}</span>
          </div>
          <p className="whitespace-pre-wrap text-text-secondary leading-relaxed text-lg">{content}</p>
        </div>
      )}

      {block.block_type === 'exam_tip' && (
        <div className="rounded-xl border border-warning-500/30 bg-warning-500/5 p-6">
          <div className="mb-3 flex items-center gap-2 text-warning-400">
            <Lightbulb className="h-5 w-5" aria-hidden="true" />
            <span className="text-sm font-semibold uppercase tracking-wide">{t('lessons.tip')}</span>
          </div>
          <p className="whitespace-pre-wrap text-text-secondary leading-relaxed text-lg">{content}</p>
        </div>
      )}

      <div className="flex items-center justify-between pt-4 border-t border-border-primary/50">
        <Button
          variant="ghost"
          onClick={onPrev}
          disabled={!hasPrev}
          leftIcon={isRTL ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        >
          {t('lessons.previous')}
        </Button>
        <Button
          onClick={onNext}
          rightIcon={isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        >
          {t('lessons.next')}
        </Button>
      </div>
    </div>
  );
}

type SubmitVars = { exerciseId: number } & Omit<ExerciseSubmitRequest, 'exercise_id'>;

interface ExerciseViewProps {
  exercise: Exercise;
  onSubmit: (vars: SubmitVars) => void;
  onRun: (vars: { exerciseId: number; code: string }) => void;
  result: ExerciseSubmitResponse | undefined;
  isSubmitting: boolean;
  isRunning: boolean;
  index: number;
  total: number;
  onNext: () => void;
  onPrev: () => void;
  hasNext: boolean;
  hasPrev: boolean;
  terminalOutput: string;
  terminalError: string;
  onClearTerminal: () => void;
}

function ExerciseView({
  exercise,
  onSubmit,
  onRun,
  result,
  isSubmitting,
  isRunning,
  index,
  total,
  onNext,
  onPrev,
  hasNext,
  hasPrev,
  terminalOutput,
  terminalError,
  onClearTerminal,
}: ExerciseViewProps) {
  const { t } = useTranslation();

  return (
    <div className="flex-1 min-h-0 flex flex-col gap-3 animate-fade-in">
      <div className="flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <StatusBadge status="current" size="sm" />
          <Badge variant="primary" size="sm" dot dotColor="primary">
            {t('lessons.practice')}
          </Badge>
        </div>
      </div>

      <ExercisePanel
        exercise={exercise}
        onSubmit={onSubmit}
        onRun={onRun}
        result={result}
        isSubmitting={isSubmitting}
        isRunning={isRunning}
        terminalOutput={terminalOutput}
        terminalError={terminalError}
        onClearTerminal={onClearTerminal}
        onNext={onNext}
        onPrev={onPrev}
        hasNext={hasNext}
        hasPrev={hasPrev}
      />
    </div>
  );
}
