import { useState } from 'react';
import { Play, Check } from 'lucide-react';
import { Button, CodeEditor, TerminalPanel } from './ui';
import { useTranslation } from '../hooks/useTranslation';
import { ExerciseAnswerPanel, ExerciseResult } from './ExerciseAnswer';
import { isCodeExercise } from './exerciseTypes';
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
}: ExercisePanelProps) {
  const { t } = useTranslation();
  const [code, setCode] = useState(exercise.starter_code || '');

  return (
    <div className="space-y-6">
      <div className="prose dark:prose-invert max-w-none">
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

      {!isCodeExercise(exercise) ? (
        <ExerciseAnswerPanel
          exercise={exercise}
          onSubmit={onSubmit}
          result={result}
          isSubmitting={isSubmitting}
        />
      ) : (
        <div className="grid lg:grid-cols-[minmax(0,1fr)_380px] gap-6">
          <div className="space-y-4">
            <CodeEditor
              code={code}
              onChange={setCode}
              language="python"
              readOnly={false}
              showLineNumbers
              minHeight="350px"
              placeholder={t('lessons.write_code_here')}
              onRun={() => onRun({ exerciseId: exercise.id, code })}
              onSubmit={() => onSubmit({ exerciseId: exercise.id, code })}
              isRunning={isRunning}
              isSubmitting={isSubmitting}
            />

            <div className="flex items-center gap-3">
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

            {result && <ExerciseResult result={result} />}
          </div>

          <TerminalPanel
            output={terminalOutput}
            error={terminalError}
            isRunning={isRunning}
            clearable={true}
            onClear={onClearTerminal}
            className="h-[350px]"
            data-testid="terminal-panel"
          />
        </div>
      )}
    </div>
  );
}
