import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { lessonsApi, exercisesApi } from '../api/services';
import { ArrowLeft, CheckCircle, Clock, Target, Code, ChevronLeft, ChevronRight, Copy, Check, RotateCcw, Terminal, Sparkles } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import type { Exercise, ExerciseSubmitRequest, ExerciseSubmitResponse, LessonBlock } from '../types';
import { Badge, Button, cn, Progress, Skeleton, CodeEditor, StatusBadge, XPBadge } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';
import { ExercisePanel } from '../components/ExercisePanel';
import { MicroQuestLesson } from '../components/microquest/MicroQuestLesson';
import { LESSON_SHELL_HEIGHT_CLASS } from '../lib/layout';

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

  useEffect(() => {
    if (lessonId) {
      lessonsApi.start(Number(lessonId)).catch(() => {});
    }
  }, [lessonId]);

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
      if (data.output) setTerminalOutput(data.output);
    },
    onError: (error: any) => {
      setTerminalError(error.response?.data?.detail || 'Submission failed');
    },
  });

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
  const currentExercise = currentBlockIndex >= blocks.length
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
      <header className="bg-bg-secondary/80 backdrop-blur-xl border-b border-border-primary/50 px-4 py-3 flex-shrink-0">
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
              <p className="text-xs text-text-tertiary uppercase tracking-wide">{t('lessons.lesson')} {lesson.order}</p>
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
                  {block.block_type === 'code' ? t('lessons.code') : block.block_type === 'text' ? t('lessons.read') : t('lessons.practice')}
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
          <div className="flex-1 min-w-0 overflow-x-hidden overflow-y-auto p-6 lg:p-8">
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="flex items-center justify-between text-sm text-text-tertiary mb-4">
                <span>
                  {currentBlockIndex < blocks.length
                    ? `${t('lessons.block')} ${currentBlockIndex + 1} ${t('lessons.of')} ${totalSteps}`
                    : `${t('lessons.exercise')} ${currentBlockIndex - blocks.length + 1} ${t('lessons.of')} ${totalSteps}`}
                </span>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-bg-tertiary rounded-full text-xs font-mono tabular-nums">
                    {currentBlockIndex + 1} / {totalSteps}
                  </span>
                </div>
              </div>

              {currentBlockIndex < blocks.length ? (
                <LessonBlockView
                  block={currentBlock}
                  index={currentBlockIndex}
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
                  label={`${Math.round(((currentBlockIndex + 1) / totalSteps) * 100)}%`}
                  className="w-full max-w-48"
                />
              </div>
              {currentBlockIndex < totalSteps - 1 ? (
                <Button
                  onClick={goToNext}
                  disabled={currentBlockIndex >= blocks.length && exerciseResults[currentExercise!.id] && !exerciseResults[currentExercise!.id].is_correct}
                  rightIcon={isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
                  data-testid="lesson-nav-next"
                >
                  {t('lessons.next')}
                </Button>
              ) : (
                <Link
                  to="/app/dashboard"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-glow-accent"
                  data-testid="lesson-nav-finish"
                >
                  <span>{t('lessons.finish_lesson')}</span>
                  <ChevronRight className="h-4 w-4" />
                </Link>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

interface LessonBlockViewProps {
  block: LessonBlock;
  index: number;
  total: number;
  onNext: () => void;
  onPrev: () => void;
  hasNext: boolean;
  hasPrev: boolean;
}

function LessonBlockView({ block, index, total, onNext, onPrev, hasPrev }: LessonBlockViewProps) {
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
        <StatusBadge
          status={index < 2 ? 'completed' : index === 2 ? 'current' : 'locked'}
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
          className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
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
  const { t, isRTL } = useTranslation();

  return (
    <div className="max-w-4xl min-w-0 mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
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
      />

      <div className="flex items-center justify-between pt-4 border-t border-border-primary/50">
        <Button
          variant="ghost"
          onClick={onPrev}
          disabled={!hasPrev}
          leftIcon={isRTL ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        >
          {t('lessons.previous')}
        </Button>
        {hasNext ? (
          <Button
            onClick={onNext}
            disabled={result && !result.is_correct}
            rightIcon={isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
          >
            {t('lessons.next')}
          </Button>
        ) : (
          <Link
            to="/app/dashboard"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-glow-accent"
          >
            <span>{t('lessons.finish_lesson')}</span>
            <ChevronRight className="h-4 w-4" />
          </Link>
        )}
      </div>
    </div>
  );
}
