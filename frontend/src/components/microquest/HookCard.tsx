import { Compass, Lightbulb, Sparkles } from 'lucide-react';
import { Card } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { localized } from './localized';
import type { HookConfig } from './types';

interface HookCardProps {
  /** The block's main paragraph, already resolved to the current language. */
  scenario: string;
  config: HookConfig;
  language: string;
}

/**
 * The Local Hook: a short real-world scenario, the challenge it raises, and
 * what the student is about to learn. Purely informational — reading it is
 * "completing" it, so the quest advances via the Continue button that follows.
 */
export function HookCard({ scenario, config, language }: HookCardProps) {
  const { t } = useTranslation();

  return (
    <Card
      data-testid="quest-hook"
      className="p-5 sm:p-6 space-y-4 bg-gradient-to-br from-primary-500/5 to-accent-500/5 border-primary-500/20"
    >
      <div className="flex items-center gap-2 text-primary-400">
        <Compass className="h-5 w-5 flex-shrink-0" />
        <span className="text-sm font-semibold uppercase tracking-wide">
          {t('microquest.hook_label')}
        </span>
      </div>

      <p className="text-text-primary leading-relaxed break-words">{scenario}</p>

      <div className="flex items-start gap-2 rounded-xl border border-border-primary/50 bg-bg-secondary/40 p-4">
        <Sparkles className="h-5 w-5 flex-shrink-0 text-accent-400" />
        <p className="min-w-0 break-words font-medium text-text-primary">
          {localized(config.challenge, language)}
        </p>
      </div>

      <div className="flex items-start gap-2 text-sm text-text-secondary">
        <Lightbulb className="h-4 w-4 flex-shrink-0 text-warning-400 mt-0.5" />
        <p className="min-w-0 break-words">
          <span className="font-medium text-text-primary">{t('microquest.you_will_learn')}</span>{' '}
          {localized(config.learn, language)}
        </p>
      </div>
    </Card>
  );
}
