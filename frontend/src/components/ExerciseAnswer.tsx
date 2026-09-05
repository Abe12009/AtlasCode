import { useMemo, useState } from 'react';
import { Check, CheckCircle, ChevronUp, ChevronDown, X } from 'lucide-react';
import { Alert, Button, XPBadge, CodeBlock, cn } from './ui';
import { useTranslation } from '../hooks/useTranslation';
import type { Exercise, ExerciseSubmitResponse } from '../types';
import type { SubmitVars } from './exerciseTypes';

interface ExerciseResultProps {
  result: ExerciseSubmitResponse;
}

export function ExerciseResult({ result }: ExerciseResultProps) {
  const { t } = useTranslation();
  return (
    <Alert
      variant={result.is_correct ? 'success' : 'error'}
      className="animate-slide-up"
      data-testid="exercise-result"
    >
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        {result.is_correct ? (
          <CheckCircle className="h-5 w-5 text-success-500" />
        ) : (
          <X className="h-5 w-5 text-error-500" />
        )}
        <span className="font-medium">
          {result.is_correct ? t('lessons.correct') : t('lessons.incorrect')}
        </span>
        {result.xp_earned > 0 && <XPBadge xp={result.xp_earned} size="sm" />}
      </div>
      <p className="text-sm text-text-secondary break-words">{result.feedback}</p>
      {result.output && (
        <div
          dir="ltr"
          className="mt-3 p-3 bg-bg-code rounded-lg font-mono text-sm text-gray-100 overflow-x-auto text-left"
        >
          {result.output}
        </div>
      )}
    </Alert>
  );
}

interface ExerciseAnswerPanelProps {
  exercise: Exercise;
  onSubmit: (vars: SubmitVars) => void;
  result: ExerciseSubmitResponse | undefined;
  isSubmitting: boolean;
}

/**
 * Answer UI for the non-code exercise types. Correctness is never known here:
 * the API omits option correctness and expected answers, so this component can
 * only collect an answer and show whatever the backend decides.
 */
export function ExerciseAnswerPanel({
  exercise,
  onSubmit,
  result,
  isSubmitting,
}: ExerciseAnswerPanelProps) {
  const { t } = useTranslation();

  const sortedOptions = useMemo(
    () => [...(exercise.options ?? [])].sort((a, b) => a.order - b.order),
    [exercise.options],
  );
  const optionById = useMemo(
    () => new Map(sortedOptions.map((option) => [option.id, option])),
    [sortedOptions],
  );

  const [selectedOptionId, setSelectedOptionId] = useState<number | null>(null);
  const [answerText, setAnswerText] = useState('');
  const [orderedIds, setOrderedIds] = useState<number[]>(() =>
    // Present the steps shuffled — showing them already in the stored order
    // would give the answer away.
    [...(exercise.options ?? [])].sort((a, b) => a.id - b.id).map((option) => option.id).reverse(),
  );

  const blankCount = useMemo(() => {
    const matches = (exercise.starter_code ?? '').match(/_{2,}/g);
    return matches ? matches.length : 1;
  }, [exercise.starter_code]);
  const [blankValues, setBlankValues] = useState<string[]>(() => Array(blankCount).fill(''));

  // Once solved, the answer is locked so a stray click cannot look like a retry.
  const isLocked = Boolean(result?.is_correct);

  function setBlank(index: number, value: string) {
    setBlankValues((prev) => prev.map((current, i) => (i === index ? value : current)));
  }

  function moveOrdered(position: number, delta: number) {
    setOrderedIds((prev) => {
      const next = [...prev];
      const target = position + delta;
      if (target < 0 || target >= next.length) return prev;
      [next[position], next[target]] = [next[target], next[position]];
      return next;
    });
  }

  let canSubmit = false;
  if (exercise.exercise_type === 'multiple_choice') canSubmit = selectedOptionId !== null;
  else if (exercise.exercise_type === 'ordering') canSubmit = orderedIds.length > 0;
  else if (exercise.exercise_type === 'fill_blank') canSubmit = blankValues.some((v) => v.trim() !== '');
  else canSubmit = answerText.trim() !== '';

  function handleSubmit() {
    if (exercise.exercise_type === 'multiple_choice' && selectedOptionId !== null) {
      onSubmit({ exerciseId: exercise.id, selected_option_id: selectedOptionId });
    } else if (exercise.exercise_type === 'ordering') {
      onSubmit({ exerciseId: exercise.id, ordered_option_ids: orderedIds });
    } else if (exercise.exercise_type === 'fill_blank') {
      onSubmit({ exerciseId: exercise.id, blanks: blankValues });
    } else {
      onSubmit({ exerciseId: exercise.id, answer: answerText });
    }
  }

  return (
    <div className="space-y-4" data-testid="answer-panel">
      {exercise.exercise_type === 'multiple_choice' && (
        <fieldset className="space-y-3" data-testid="mcq-options">
          <legend className="sr-only">{exercise.translations[0]?.prompt ?? ''}</legend>
          {sortedOptions.map((option, optionIndex) => {
            const selected = selectedOptionId === option.id;
            return (
              <label
                key={option.id}
                data-testid={`mcq-option-${option.id}`}
                className={cn(
                  'flex items-start gap-3 w-full p-4 rounded-xl border transition-all',
                  'bg-bg-secondary/40 hover:bg-bg-secondary/70',
                  selected
                    ? 'border-primary-500 ring-2 ring-primary-500/30 bg-primary-500/10'
                    : 'border-border-primary/50',
                  isLocked ? 'cursor-not-allowed opacity-70' : 'cursor-pointer',
                )}
              >
                <input
                  type="radio"
                  name={`exercise-${exercise.id}`}
                  value={option.id}
                  checked={selected}
                  disabled={isLocked}
                  onChange={() => setSelectedOptionId(option.id)}
                  className="mt-1 h-4 w-4 flex-shrink-0 accent-primary-500"
                />
                <span className="flex items-start gap-2 min-w-0">
                  <span className="font-semibold text-text-tertiary flex-shrink-0">
                    {String.fromCharCode(65 + optionIndex)}.
                  </span>
                  <span className="text-text-primary break-words">
                    {option.translations[0]?.text ?? ''}
                  </span>
                </span>
              </label>
            );
          })}
        </fieldset>
      )}

      {exercise.exercise_type === 'ordering' && (
        <ol className="space-y-2" data-testid="ordering-list">
          {orderedIds.map((optionId, position) => (
            <li
              key={optionId}
              data-testid={`ordering-item-${optionId}`}
              className="flex items-center gap-3 p-3 rounded-xl border border-border-primary/50 bg-bg-secondary/40"
            >
              <span className="font-semibold text-text-tertiary flex-shrink-0">{position + 1}.</span>
              <span className="flex-1 min-w-0 break-words font-mono text-sm text-text-primary">
                {optionById.get(optionId)?.translations[0]?.text ?? ''}
              </span>
              <span className="flex flex-shrink-0 gap-1">
                <button
                  type="button"
                  aria-label={t('lessons.move_up')}
                  disabled={position === 0 || isLocked}
                  onClick={() => moveOrdered(position, -1)}
                  className="p-1.5 rounded-lg border border-border-primary/50 text-text-secondary disabled:opacity-40"
                >
                  <ChevronUp className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  aria-label={t('lessons.move_down')}
                  disabled={position === orderedIds.length - 1 || isLocked}
                  onClick={() => moveOrdered(position, 1)}
                  className="p-1.5 rounded-lg border border-border-primary/50 text-text-secondary disabled:opacity-40"
                >
                  <ChevronDown className="h-4 w-4" />
                </button>
              </span>
            </li>
          ))}
        </ol>
      )}

      {exercise.exercise_type === 'fill_blank' && (
        <div className="space-y-4" data-testid="fill-blank">
          {exercise.starter_code && (
            <CodeBlock>{exercise.starter_code}</CodeBlock>
          )}
          <div className="space-y-3">
            {blankValues.map((value, blankIndex) => (
              <div key={blankIndex} className="flex items-center gap-3">
                <label
                  htmlFor={`blank-${exercise.id}-${blankIndex}`}
                  className="text-sm font-medium text-text-secondary flex-shrink-0"
                >
                  {t('lessons.blank')} {blankIndex + 1}
                </label>
                <input
                  id={`blank-${exercise.id}-${blankIndex}`}
                  type="text"
                  value={value}
                  disabled={isLocked}
                  onChange={(e) => setBlank(blankIndex, e.target.value)}
                  className="flex-1 min-w-0 rounded-xl border border-border-primary bg-bg-primary px-4 py-2.5 font-mono text-sm text-text-primary focus:border-border-focus focus:outline-none focus:ring-2 focus:ring-border-focus/20"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {exercise.exercise_type === 'prediction' && (
        <div className="space-y-3" data-testid="prediction">
          {exercise.starter_code && (
            <CodeBlock>{exercise.starter_code}</CodeBlock>
          )}
          <label
            htmlFor={`prediction-${exercise.id}`}
            className="block text-sm font-medium text-text-secondary"
          >
            {t('lessons.your_prediction')}
          </label>
          <textarea
            id={`prediction-${exercise.id}`}
            value={answerText}
            disabled={isLocked}
            onChange={(e) => setAnswerText(e.target.value)}
            rows={5}
            placeholder={t('lessons.prediction_placeholder')}
            className="w-full rounded-xl border border-border-primary bg-bg-primary px-4 py-3 font-mono text-sm text-text-primary focus:border-border-focus focus:outline-none focus:ring-2 focus:ring-border-focus/20"
          />
        </div>
      )}

      <Button
        onClick={handleSubmit}
        disabled={isSubmitting || isLocked || !canSubmit}
        leftIcon={<Check className="h-4 w-4" />}
        className="w-full sm:w-auto bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent"
        data-testid="submit-answer"
      >
        {isSubmitting ? t('lessons.submitting') : t('lessons.submit_answer')}
      </Button>

      {result && <ExerciseResult result={result} />}
    </div>
  );
}
