import { useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Alert } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { BlueprintOrderSteps } from './BlueprintOrderSteps';
import { MatchPairsBlueprint } from './MatchPairsBlueprint';
import { SpotTheBugBlueprint } from './SpotTheBugBlueprint';
import {
  isMatchPairsConfig,
  isOrderStepsConfig,
  isSpotTheBugConfig,
  type AnyBlueprintConfig,
} from './types';

interface BlueprintProps {
  /** The blueprint block's parsed config, or null if it had none / was not
   * valid JSON. */
  config: AnyBlueprintConfig | null;
  language: string;
  onSolved: () => void;
  solved: boolean;
}

/**
 * Picks the interaction a blueprint block asks for.
 *
 *   config.kind === 'order_steps'   ->  BlueprintOrderSteps
 *   config.kind === 'match_pairs'   ->  MatchPairsBlueprint
 *   config.kind === 'spot_the_bug'  ->  SpotTheBugBlueprint
 *   anything else                   ->  the fallback below
 *
 * This is the only place that knows the mapping, so adding a fourth
 * interaction means adding a component, a guard, and one branch here —
 * nothing else in the Micro-Quest changes. See types.ts for the contract
 * every blueprint config follows (typed shape + a validating `isXConfig`
 * guard next to it) and the individual blueprint components for the
 * contract each *implementation* follows (own interaction state, own
 * correctness check, `localized()` for config text, an accessible native
 * control, `solved`/`onSolved` as its only link back to the lesson flow).
 */
export function Blueprint({ config, language, onSolved, solved }: BlueprintProps) {
  if (isOrderStepsConfig(config)) {
    return (
      <BlueprintOrderSteps config={config} language={language} onSolved={onSolved} solved={solved} />
    );
  }
  if (isMatchPairsConfig(config)) {
    return (
      <MatchPairsBlueprint config={config} language={language} onSolved={onSolved} solved={solved} />
    );
  }
  if (isSpotTheBugConfig(config)) {
    return (
      <SpotTheBugBlueprint config={config} language={language} onSolved={onSolved} solved={solved} />
    );
  }
  return <UnsupportedBlueprint onSolved={onSolved} solved={solved} />;
}

/**
 * A blueprint this build cannot render: an unknown `kind`, or a config that
 * lost a field somewhere between the database and here.
 *
 * The blueprint is a warm-up, not the graded work, so a broken one must never
 * strand a student in front of a lesson they cannot finish. It says so plainly
 * and unlocks the quest, leaving the real exercise — and the real XP — exactly
 * as reachable as on any other lesson.
 */
function UnsupportedBlueprint({ onSolved, solved }: { onSolved: () => void; solved: boolean }) {
  const { t } = useTranslation();

  useEffect(() => {
    if (!solved) onSolved();
  }, [solved, onSolved]);

  return (
    <Alert variant="warning" data-testid="blueprint-unsupported">
      <div className="flex items-start gap-2">
        <AlertTriangle className="h-5 w-5 flex-shrink-0 text-warning-400" />
        <p className="min-w-0 break-words">{t('microquest.blueprint_unavailable')}</p>
      </div>
    </Alert>
  );
}
