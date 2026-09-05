import { Link } from 'react-router-dom';
import { PartyPopper, ArrowRight, RotateCcw } from 'lucide-react';
import { Card, Button, XPBadge } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';

interface QuestClearProps {
  /** XP actually reported by the backend for this submission — never
   * recomputed on the client. */
  xpEarned: number;
  lessonTitle: string;
}

/** The Quest Clear state: shown once the reference exercise is genuinely
 * solved (the backend said so). All the state it displays — XP, completion —
 * comes straight from the exercise submission response. */
export function QuestClear({ xpEarned, lessonTitle }: QuestClearProps) {
  const { t } = useTranslation();

  return (
    <Card
      data-testid="quest-clear"
      className="p-6 sm:p-8 text-center space-y-5 bg-gradient-to-br from-success-500/10 to-primary-500/10 border-success-500/30 animate-fade-in"
    >
      <div className="flex justify-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-success-500/20">
          <PartyPopper className="h-8 w-8 text-success-400" />
        </div>
      </div>

      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-text-primary">
          {t('microquest.quest_clear_title')}
        </h2>
        <p className="mt-1 text-text-secondary break-words">
          {t('microquest.quest_clear_subtitle', { lesson: lessonTitle })}
        </p>
      </div>

      <div className="flex justify-center" data-testid="quest-clear-xp">
        <XPBadge xp={xpEarned} size="lg" />
      </div>

      <p className="text-sm text-success-400 font-medium">{t('microquest.progress_saved')}</p>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
        <Link to="/app/dashboard" className="w-full sm:w-auto">
          <Button
            className="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
            rightIcon={<ArrowRight className="h-4 w-4" />}
            data-testid="quest-clear-continue"
          >
            {t('microquest.continue_learning')}
          </Button>
        </Link>
        <Link to="/app/courses" className="w-full sm:w-auto">
          <Button variant="outline" className="w-full" leftIcon={<RotateCcw className="h-4 w-4" />}>
            {t('microquest.back_to_courses')}
          </Button>
        </Link>
      </div>
    </Card>
  );
}
