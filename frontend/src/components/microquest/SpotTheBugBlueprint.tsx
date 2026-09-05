import { useState } from 'react';
import { Bug, CheckCircle, Lightbulb, X } from 'lucide-react';
import { Alert, Button, CodeBlock, cn } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { localized } from './localized';
import type { SpotTheBugConfig } from './types';

interface SpotTheBugBlueprintProps {
  config: SpotTheBugConfig;
  language: string;
  /** Called once, the first time the student picks the actually-buggy statement. */
  onSolved: () => void;
  solved: boolean;
}

/**
 * "Read these claims about the code. Exactly one of them is wrong — which one?"
 *
 * The third blueprint interaction, and the one built for a debugging quest: a
 * single-select puzzle among several statements, mechanically distinct from
 * reordering (order_steps) and from pairwise connecting (match_pairs). It
 * exercises the actual habit a debugging exercise asks for — read a claim
 * about the code and judge whether it holds — without stating what the fix
 * is, so the real exercise still requires real work.
 *
 * Built as a native radio group (one input per statement, one fieldset/legend
 * for the whole question) for the same reason ExerciseAnswerPanel's
 * multiple-choice UI is: a native control is free accessibility — arrow-key
 * navigation, screen-reader announcement of "N of M" — that a div-based
 * button grid would have to reimplement.
 */
export function SpotTheBugBlueprint({ config, language, onSolved, solved }: SpotTheBugBlueprintProps) {
  const { t } = useTranslation();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [checked, setChecked] = useState<'correct' | 'incorrect' | null>(null);

  const isLocked = solved;

  function select(id: string) {
    if (isLocked) return;
    setChecked(null);
    setSelectedId(id);
  }

  function check() {
    if (selectedId === null) return;
    const correct = selectedId === config.buggy_id;
    setChecked(correct ? 'correct' : 'incorrect');
    if (correct && !solved) onSolved();
  }

  return (
    <div className="space-y-4" data-testid="blueprint">
      {config.snippet && <CodeBlock data-testid="spot-bug-snippet">{config.snippet}</CodeBlock>}

      <fieldset className="space-y-3" data-testid="spot-bug-statements">
        <legend className="sr-only">{t('microquest.spot_bug_legend')}</legend>
        {config.statements.map((statement) => {
          const isSelected = selectedId === statement.id;
          const isWrongPick = checked === 'incorrect' && isSelected;
          const isCorrectPick = checked === 'correct' && isSelected;
          return (
            <label
              key={statement.id}
              data-testid={`spot-bug-statement-${statement.id}`}
              className={cn(
                'flex w-full items-start gap-3 rounded-xl border p-3 sm:p-4 transition-all',
                'bg-bg-secondary/40',
                isCorrectPick
                  ? 'border-success-500/60 bg-success-500/10'
                  : isWrongPick
                    ? 'border-error-500/60 bg-error-500/10'
                    : isSelected
                      ? 'border-primary-500 ring-2 ring-primary-500/30 bg-primary-500/10'
                      : 'border-border-primary/50 hover:bg-bg-secondary/70',
                isLocked ? 'cursor-not-allowed opacity-80' : 'cursor-pointer',
              )}
            >
              <input
                type="radio"
                name="spot-the-bug"
                value={statement.id}
                checked={isSelected}
                disabled={isLocked}
                onChange={() => select(statement.id)}
                className="mt-1 h-4 w-4 flex-shrink-0 accent-primary-500"
              />
              <span className="min-w-0 break-words text-text-primary">
                {localized(statement.text, language)}
              </span>
            </label>
          );
        })}
      </fieldset>

      {!solved && (
        <Button
          onClick={check}
          disabled={selectedId === null}
          data-testid="blueprint-check"
          leftIcon={<Bug className="h-4 w-4" />}
          className="w-full sm:w-auto bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
        >
          {t('microquest.check_bug')}
        </Button>
      )}

      {checked === 'incorrect' && !solved && (
        <Alert variant="error" data-testid="blueprint-feedback" className="animate-slide-up">
          <div className="flex items-start gap-2">
            <X className="h-5 w-5 flex-shrink-0 text-error-500" />
            <div className="min-w-0">
              <p className="font-medium">{t('microquest.bug_incorrect')}</p>
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
              {localized(config.success, language) || t('microquest.bug_correct')}
            </p>
          </div>
        </Alert>
      )}
    </div>
  );
}
