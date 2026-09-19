import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Play, Check, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button, CodeEditor, TerminalPanel } from './ui';
import { useTranslation } from '../hooks/useTranslation';
import { ExerciseAnswerPanel, ExerciseResult } from './ExerciseAnswer';
import { isCodeExercise } from './exerciseTypes';
import { CircuitLabPanel } from './circuitLab/CircuitLabPanel';
import { GitQuestPanel } from './gitQuest/GitQuestPanel';
import type { Exercise, ExerciseSubmitResponse } from '../types';
import type { SubmitVars } from './exerciseTypes';

interface ExercisePanelProps {
  exercise: Exercise;
  onSubmit: (vars: SubmitVars) => void;
  onRun: (vars: { exerciseId: number; code: string }) => void;
  result: ExerciseSubmitResponse | undefined;
  isSubmitting: boolean;
  isRunning: boolean;
  terminalOutput: string;
  terminalError: string;
  onClearTerminal: () => void;
  /** Step nav, rendered at the bottom of the left panel for a code exercise
   * -- only LessonDetail's classic flow passes these; Micro-Quest has its
   * own pacing model and simply omits them. */
  onNext?: () => void;
  onPrev?: () => void;
  hasNext?: boolean;
  hasPrev?: boolean;
}

/**
 * Prompt + hint + type-aware answer area (code editor & terminal, or
 * ExerciseAnswerPanel for non-code types) + result. This is the exercise
 * functionality itself — LessonDetail's classic flow and the Micro-Quest flow
 * both render it unchanged, so grading, the sandbox and XP behavior stay in
 * exactly one place.
 */
export function ExercisePanel({
  exercise,
  onSubmit,
  onRun,
  result,
  isSubmitting,
  isRunning,
  terminalOutput,
  terminalError,
  onClearTerminal,
  onNext,
  onPrev,
  hasNext,
  hasPrev,
}: ExercisePanelProps) {
  const { t, isRTL } = useTranslation();
  const [code, setCode] = useState(exercise.starter_code || '');
  const showStepNav = onNext !== undefined || onPrev !== undefined;

  const stepNav = showStepNav && (
    <div className="flex items-center justify-between pt-4 mt-4 border-t border-border-primary/50 flex-shrink-0">
      <Button
        variant="ghost"
        onClick={onPrev}
        disabled={!hasPrev}
        leftIcon={isRTL ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        data-testid="exercise-nav-prev"
      >
        {t('lessons.previous')}
      </Button>
      {hasNext ? (
        <Button
          onClick={onNext}
          disabled={!!result && !result.is_correct}
          rightIcon={isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
          data-testid="exercise-nav-next"
        >
          {t('lessons.next')}
        </Button>
      ) : (
        <Link
          to="/app/dashboard"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-glow-accent"
          data-testid="exercise-nav-finish"
        >
          <span>{t('lessons.finish_lesson')}</span>
          <ChevronRight className="h-4 w-4" />
        </Link>
      )}
    </div>
  );

  if (exercise.exercise_type === 'circuit_lab') {
    return (
      <div className="space-y-6">
        <ExercisePrompt exercise={exercise} />
        <div className="space-y-4">
          <CircuitLabPanel
            exercise={exercise}
            onSubmit={onSubmit}
            onRun={onRun}
            isSubmitting={isSubmitting}
            isRunning={isRunning}
          />
          {result && <ExerciseResult result={result} />}
        </div>
        {stepNav}
      </div>
    );
  }

  if (exercise.exercise_type === 'git_quest') {
    return (
      <div className="space-y-6">
        <ExercisePrompt exercise={exercise} />
        <div className="space-y-4">
          <GitQuestPanel exercise={exercise} onSubmit={onSubmit} isSubmitting={isSubmitting} />
          {result && <ExerciseResult result={result} />}
        </div>
        {stepNav}
      </div>
    );
  }

  if (!isCodeExercise(exercise)) {
    return (
      <div className="space-y-6">
        <ExercisePrompt exercise={exercise} />
        <ExerciseAnswerPanel
          exercise={exercise}
          onSubmit={onSubmit}
          result={result}
          isSubmitting={isSubmitting}
        />
        {stepNav}
      </div>
    );
  }

  // Code-writing/debugging: the target two-panel layout -- prompt/hint/nav
  // fixed-width on the left, editor+output filling the right. Both columns
  // are sized from a shared flex-1 min-h-0 ancestor (see LessonDetail's
  // ExerciseView) so this is the ONE scroll region for the whole exercise:
  // the editor and terminal fill their allotted height instead of each
  // scrolling independently nested inside a page that's also scrolling.
  return (
    <div className="flex-1 min-h-0 flex flex-col lg:flex-row gap-4 lg:gap-6">
      <div className="lg:w-[380px] lg:flex-shrink-0 flex flex-col min-h-0 overflow-y-auto">
        <ExercisePrompt exercise={exercise} />
        <div className="flex-1" />
        {stepNav}
      </div>

      <div className="flex-1 min-w-0 flex flex-col min-h-0 gap-3">
        <div className="flex-[2] min-h-0">
          <CodeEditor
            code={code}
            onChange={setCode}
            language="python"
            readOnly={false}
            showLineNumbers
            fillHeight
            placeholder={t('lessons.write_code_here')}
            onRun={() => onRun({ exerciseId: exercise.id, code })}
            onSubmit={() => onSubmit({ exerciseId: exercise.id, code })}
            isRunning={isRunning}
            isSubmitting={isSubmitting}
          />
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <Button
            variant="outline"
            onClick={() => onRun({ exerciseId: exercise.id, code })}
            disabled={isRunning}
            leftIcon={<Play className="h-4 w-4" />}
            className="flex-1"
          >
            {isRunning ? t('lessons.running') : t('lessons.run_code')}
          </Button>
          <Button
            onClick={() => onSubmit({ exerciseId: exercise.id, code })}
            disabled={isSubmitting}
            leftIcon={<Check className="h-4 w-4" />}
            className="flex-1 bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent"
          >
            {isSubmitting ? t('lessons.submitting') : t('lessons.submit_solution')}
          </Button>
        </div>

        <div className="flex-1 min-h-0 overflow-y-auto space-y-3">
          {result && <ExerciseResult result={result} />}
          <TerminalPanel
            output={terminalOutput}
            error={terminalError}
            isRunning={isRunning}
            clearable={true}
            onClear={onClearTerminal}
            className="min-h-[180px]"
            data-testid="terminal-panel"
          />
        </div>
      </div>
    </div>
  );
}

function ExercisePrompt({ exercise }: { exercise: Exercise }) {
  return (
    <div className="prose dark:prose-invert max-w-none mb-4 flex-shrink-0">
      <h3 className="text-lg font-semibold text-text-primary mb-3">
        {exercise.translations[0]?.prompt}
      </h3>
      {exercise.translations[0]?.hint && (
        <div className="bg-warning-500/10 border border-warning-500/30 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <span className="text-warning-400 text-xl">💡</span>
            <p className="text-warning-300 text-sm">{exercise.translations[0]?.hint}</p>
          </div>
        </div>
      )}
    </div>
  );
}
