import { Check } from 'lucide-react';
import { cn } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { QUEST_STAGES, type QuestStage } from './types';

const STAGES = QUEST_STAGES;

interface QuestProgressProps {
  current: QuestStage;
}

/** HOOK -> BLUEPRINT -> QUEST -> COMPLETE. Purely derived from the parent's
 * current stage — no independent state, so it can never disagree with what
 * the student is actually looking at. */
export function QuestProgress({ current }: QuestProgressProps) {
  const { t } = useTranslation();
  const currentIndex = STAGES.indexOf(current);

  const labels: Record<QuestStage, string> = {
    hook: t('microquest.stage_hook'),
    blueprint: t('microquest.stage_blueprint'),
    quest: t('microquest.stage_quest'),
    complete: t('microquest.stage_complete'),
  };

  return (
    <ol
      data-testid="quest-progress"
      aria-label={t('microquest.progress_label')}
      className="flex items-center gap-1 sm:gap-2 overflow-x-auto"
    >
      {STAGES.map((stage, index) => {
        const isDone = index < currentIndex;
        const isCurrent = index === currentIndex;
        return (
          <li key={stage} className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
            <span
              data-testid={`quest-stage-${stage}`}
              data-status={isDone ? 'done' : isCurrent ? 'current' : 'upcoming'}
              className={cn(
                'flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs font-semibold whitespace-nowrap transition-colors',
                isCurrent
                  ? 'bg-primary-500 text-white'
                  : isDone
                    ? 'bg-success-500/20 text-success-400'
                    : 'bg-bg-tertiary text-text-tertiary',
              )}
              aria-current={isCurrent ? 'step' : undefined}
            >
              {isDone ? <Check className="h-3.5 w-3.5" /> : <span>{index + 1}</span>}
              <span>{labels[stage]}</span>
            </span>
            {index < STAGES.length - 1 && (
              <span
                className={cn('h-0.5 w-4 sm:w-6 flex-shrink-0 rounded', isDone ? 'bg-success-500/40' : 'bg-border-primary/50')}
                aria-hidden="true"
              />
            )}
          </li>
        );
      })}
    </ol>
  );
}
