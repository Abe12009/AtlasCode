import { useMemo, useState } from 'react';
import { CheckCircle, ChevronDown, ChevronUp, Lightbulb, X } from 'lucide-react';
import { Alert, Button, cn } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { localized } from './localized';
import type { OrderStepsConfig } from './types';

interface BlueprintOrderStepsProps {
  config: OrderStepsConfig;
  language: string;
  /** Called once, the first time the student gets the order right. */
  onSolved: () => void;
  solved: boolean;
}

/**
 * "Put the steps in the order a program would run them."
 *
 * The only interaction the reference lesson needs, kept reusable: everything
 * shown comes from the block's config, so another lesson can ship a different
 * set of steps without touching this file. It is deliberately not a general
 * visual-programming engine.
 *
 * No syntax is involved — the student orders plain-language ideas — and the
 * success condition is exact: the submitted sequence must equal correct_order.
 */
export function BlueprintOrderSteps({
  config,
  language,
  onSolved,
  solved,
}: BlueprintOrderStepsProps) {
  const { t } = useTranslation();

  const stepsById = useMemo(
    () => new Map(config.steps.map((step) => [step.id, step])),
    [config.steps],
  );

  // Start in a deliberately wrong order so there is a real puzzle. Reversing
  // the answer guarantees it never accidentally starts solved.
  const [order, setOrder] = useState<string[]>(() => {
    const shuffled = [...config.correct_order].reverse();
    return shuffled.every((id, i) => id === config.correct_order[i])
      ? [...config.correct_order].slice(1).concat(config.correct_order[0])
      : shuffled;
  });
  const [checked, setChecked] = useState<'correct' | 'incorrect' | null>(null);

  const isLocked = solved;

  function move(position: number, delta: number) {
    if (isLocked) return;
    setChecked(null);
    setOrder((prev) => {
      const next = [...prev];
      const target = position + delta;
      if (target < 0 || target >= next.length) return prev;
      [next[position], next[target]] = [next[target], next[position]];
      return next;
    });
  }

  function check() {
    const correct = order.every((id, index) => id === config.correct_order[index]);
    setChecked(correct ? 'correct' : 'incorrect');
    if (correct && !solved) onSolved();
  }

  const wrongPositions = useMemo(() => {
    if (checked !== 'incorrect') return new Set<number>();
    return new Set(
      order.map((id, index) => (id === config.correct_order[index] ? -1 : index)).filter((i) => i >= 0),
    );
  }, [checked, order, config.correct_order]);

  return (
    <div className="space-y-4" data-testid="blueprint">
      <ol className="space-y-2" data-testid="blueprint-steps">
        {order.map((stepId, position) => {
          const step = stepsById.get(stepId);
          const isWrong = wrongPositions.has(position);
          return (
            <li
              key={stepId}
              data-testid={`blueprint-step-${stepId}`}
              data-position={position}
              className={cn(
                'flex items-center gap-3 p-3 sm:p-4 rounded-xl border transition-all bg-bg-secondary/40',
                checked === 'correct'
                  ? 'border-success-500/50 bg-success-500/5'
                  : isWrong
                    ? 'border-error-500/50 bg-error-500/5'
                    : 'border-border-primary/50',
              )}
            >
              <span
                className={cn(
                  'flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-sm font-semibold',
                  checked === 'correct'
                    ? 'bg-success-500 text-white'
                    : 'bg-bg-tertiary text-text-secondary',
                )}
              >
                {position + 1}
              </span>
              <span className="flex-1 min-w-0 break-words text-text-primary">
                {localized(step?.label, language)}
              </span>
              <span className="flex flex-shrink-0 gap-1">
                <button
                  type="button"
                  aria-label={t('microquest.move_up')}
                  disabled={position === 0 || isLocked}
                  onClick={() => move(position, -1)}
                  className="p-1.5 rounded-lg border border-border-primary/50 text-text-secondary disabled:opacity-40 hover:bg-bg-tertiary/50"
                >
                  <ChevronUp className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  aria-label={t('microquest.move_down')}
                  disabled={position === order.length - 1 || isLocked}
                  onClick={() => move(position, 1)}
                  className="p-1.5 rounded-lg border border-border-primary/50 text-text-secondary disabled:opacity-40 hover:bg-bg-tertiary/50"
                >
                  <ChevronDown className="h-4 w-4" />
                </button>
              </span>
            </li>
          );
        })}
      </ol>

      {!solved && (
        <Button
          onClick={check}
          data-testid="blueprint-check"
          className="w-full sm:w-auto bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
        >
          {t('microquest.check_blueprint')}
        </Button>
      )}

      {checked === 'incorrect' && !solved && (
        <Alert variant="error" data-testid="blueprint-feedback" className="animate-slide-up">
          <div className="flex items-start gap-2">
            <X className="h-5 w-5 flex-shrink-0 text-error-500" />
            <div className="min-w-0">
              <p className="font-medium">{t('microquest.blueprint_incorrect')}</p>
              {config.hint && (
                <p className="mt-1 flex items-start gap-1.5 text-sm text-text-secondary">
                  <Lightbulb className="h-4 w-4 flex-shrink-0 text-warning-400" />
                  <span className="break-words">{localized(config.hint, language)}</span>
                </p>
              )}
            </div>
          </div>
        </Alert>
      )}

      {solved && (
        <Alert variant="success" data-testid="blueprint-feedback" className="animate-slide-up">
          <div className="flex items-start gap-2">
            <CheckCircle className="h-5 w-5 flex-shrink-0 text-success-500" />
            <p className="min-w-0 break-words font-medium">
              {localized(config.success, language) || t('microquest.blueprint_correct')}
            </p>
          </div>
        </Alert>
      )}
    </div>
  );
}
