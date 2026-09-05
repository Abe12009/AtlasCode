import { useMemo, useState } from 'react';
import { CheckCircle, Lightbulb, RotateCcw, X } from 'lucide-react';
import { Alert, Button, cn } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { localized } from './localized';
import { shuffledRight } from './shuffleRight';
import type { MatchPairsConfig } from './types';

interface MatchPairsBlueprintProps {
  config: MatchPairsConfig;
  language: string;
  /** Called once, the first time every pair is matched correctly. */
  onSolved: () => void;
  solved: boolean;
}

/** One connection the student has drawn, in the order they drew it. */
interface Match {
  left: string;
  right: string;
}

/**
 * "Connect each concept to what it actually does."
 *
 * The second blueprint interaction, and the one that proves the architecture
 * is genuinely data-driven: everything shown comes from the block's config, so
 * a lesson ships a different set of pairs without touching this file.
 *
 * Tapping picks; there is no drag-and-drop, because a drag target is painful
 * on a 320px phone and would pull in a dependency for a puzzle this small.
 *
 * On the answer living in the config at all: a blueprint is a teaching device,
 * not an assessment. It awards no XP, writes nothing to the server, and its
 * result is never submitted anywhere — real correctness and real XP stay with
 * the exercise grader on the backend, which keeps its own answers server-side.
 * Hiding a lesson's own teaching material would buy nothing that reading the
 * lesson text does not already give away.
 */
export function MatchPairsBlueprint({ config, language, onSolved, solved }: MatchPairsBlueprintProps) {
  const { t } = useTranslation();

  const rightColumn = useMemo(() => shuffledRight(config.pairs), [config.pairs]);

  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedLeft, setSelectedLeft] = useState<string | null>(null);
  const [selectedRight, setSelectedRight] = useState<string | null>(null);
  const [checked, setChecked] = useState<'correct' | 'incorrect' | null>(null);

  const isLocked = solved;

  const matchOfLeft = useMemo(
    () => new Map(matches.map((match, index) => [match.left, { match, index }])),
    [matches],
  );
  const matchOfRight = useMemo(
    () => new Map(matches.map((match, index) => [match.right, { match, index }])),
    [matches],
  );

  /** A connection is wrong when its two sides come from different pairs. Only
   * revealed once the student asks to be checked, never while they work. */
  const wrongMatches = useMemo(() => {
    if (checked !== 'incorrect') return new Set<string>();
    return new Set(matches.filter((match) => match.left !== match.right).map((match) => match.left));
  }, [checked, matches]);

  function pick(side: 'left' | 'right', pairId: string) {
    if (isLocked) return;
    setChecked(null);

    const existing = side === 'left' ? matchOfLeft.get(pairId) : matchOfRight.get(pairId);
    if (existing) {
      // Tapping a connected item disconnects it, so a mistake is one tap to undo.
      setMatches((prev) => prev.filter((match) => match !== existing.match));
      setSelectedLeft(null);
      setSelectedRight(null);
      return;
    }

    const otherSelected = side === 'left' ? selectedRight : selectedLeft;
    if (otherSelected === null) {
      if (side === 'left') setSelectedLeft(pairId === selectedLeft ? null : pairId);
      else setSelectedRight(pairId === selectedRight ? null : pairId);
      return;
    }

    const match: Match =
      side === 'left'
        ? { left: pairId, right: otherSelected }
        : { left: otherSelected, right: pairId };
    setMatches((prev) => [...prev, match]);
    setSelectedLeft(null);
    setSelectedRight(null);
  }

  function check() {
    const allCorrect =
      matches.length === config.pairs.length && matches.every((match) => match.left === match.right);
    setChecked(allCorrect ? 'correct' : 'incorrect');
    if (allCorrect && !solved) onSolved();
  }

  function reset() {
    setMatches([]);
    setSelectedLeft(null);
    setSelectedRight(null);
    setChecked(null);
  }

  const allMatched = matches.length === config.pairs.length;

  function itemClassName(state: { connected: boolean; selected: boolean; wrong: boolean }) {
    return cn(
      // min-w-0 + break-words keep two columns of prose inside a 320px screen.
      'flex w-full min-w-0 items-start gap-2 break-words rounded-xl border p-2.5 text-start text-sm transition-all sm:p-3.5',
      state.wrong
        ? 'border-error-500/60 bg-error-500/10 text-text-primary'
        : checked === 'correct'
          ? 'border-success-500/50 bg-success-500/10 text-text-primary'
          : state.connected
            ? 'border-primary-500/60 bg-primary-500/10 text-text-primary'
            : state.selected
              ? 'border-accent-500 bg-accent-500/10 text-text-primary ring-2 ring-accent-500/30'
              : 'border-border-primary/50 bg-bg-secondary/40 text-text-secondary hover:bg-bg-secondary/70',
      isLocked ? 'cursor-default' : 'cursor-pointer',
    );
  }

  function connectionBadge(index: number | null) {
    return (
      <span
        className={cn(
          'flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full text-xs font-semibold',
          index === null ? 'bg-bg-tertiary text-text-tertiary' : 'bg-primary-500 text-white',
        )}
        aria-hidden="true"
      >
        {index === null ? '' : index + 1}
      </span>
    );
  }

  return (
    <div className="space-y-4" data-testid="blueprint">
      <div className="grid grid-cols-2 gap-2 sm:gap-3" data-testid="match-pairs">
        <ul className="space-y-2" data-testid="match-pairs-left">
          {config.pairs.map((pair) => {
            const connected = matchOfLeft.get(pair.id);
            return (
              <li key={pair.id}>
                <button
                  type="button"
                  data-testid={`match-left-${pair.id}`}
                  data-connected={connected ? String(connected.index + 1) : ''}
                  aria-pressed={selectedLeft === pair.id}
                  disabled={isLocked}
                  onClick={() => pick('left', pair.id)}
                  className={itemClassName({
                    connected: Boolean(connected),
                    selected: selectedLeft === pair.id,
                    wrong: wrongMatches.has(pair.id),
                  })}
                >
                  {connectionBadge(connected ? connected.index : null)}
                  <span className="min-w-0 break-words">{localized(pair.left, language)}</span>
                </button>
              </li>
            );
          })}
        </ul>

        <ul className="space-y-2" data-testid="match-pairs-right">
          {rightColumn.map((pair) => {
            const connected = matchOfRight.get(pair.id);
            return (
              <li key={pair.id}>
                <button
                  type="button"
                  data-testid={`match-right-${pair.id}`}
                  data-connected={connected ? String(connected.index + 1) : ''}
                  aria-pressed={selectedRight === pair.id}
                  disabled={isLocked}
                  onClick={() => pick('right', pair.id)}
                  className={itemClassName({
                    connected: Boolean(connected),
                    selected: selectedRight === pair.id,
                    wrong: wrongMatches.has(connected?.match.left ?? ''),
                  })}
                >
                  {connectionBadge(connected ? connected.index : null)}
                  <span className="min-w-0 break-words">{localized(pair.right, language)}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      {!solved && (
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <Button
            onClick={check}
            disabled={!allMatched}
            data-testid="blueprint-check"
            className="w-full bg-gradient-to-r from-primary-500 to-primary-600 shadow-lg hover:from-primary-600 hover:to-primary-700 hover:shadow-glow-primary sm:w-auto"
          >
            {t('microquest.check_pairs')}
          </Button>
          <Button
            variant="ghost"
            onClick={reset}
            disabled={matches.length === 0}
            data-testid="match-reset"
            leftIcon={<RotateCcw className="h-4 w-4" />}
            className="w-full sm:w-auto"
          >
            {t('microquest.reset_pairs')}
          </Button>
          <span className="text-sm text-text-tertiary" data-testid="match-progress">
            {t('microquest.pairs_matched', { matched: matches.length, total: config.pairs.length })}
          </span>
        </div>
      )}

      {checked === 'incorrect' && !solved && (
        <Alert variant="error" data-testid="blueprint-feedback" className="animate-slide-up">
          <div className="flex items-start gap-2">
            <X className="h-5 w-5 flex-shrink-0 text-error-500" />
            <div className="min-w-0">
              <p className="font-medium">{t('microquest.pairs_incorrect')}</p>
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
              {localized(config.success, language) || t('microquest.pairs_correct')}
            </p>
          </div>
        </Alert>
      )}
    </div>
  );
}
