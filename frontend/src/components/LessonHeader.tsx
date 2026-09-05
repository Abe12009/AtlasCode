import { Link } from 'react-router-dom';
import { ArrowLeft, Clock, Target } from 'lucide-react';
import { XPBadge } from './ui';
import { useTranslation } from '../hooks/useTranslation';
import type { Lesson } from '../types';

interface LessonHeaderProps {
  lesson: Lesson;
}

/**
 * The lesson page header, shared by the classic LessonDetail flow and the
 * Micro-Quest flow so the 320px layout fixes live in exactly one place.
 */
export function LessonHeader({ lesson }: LessonHeaderProps) {
  const { t } = useTranslation();

  return (
    <header className="bg-bg-secondary/80 backdrop-blur-xl border-b border-border-primary/50 px-4 py-3 flex-shrink-0">
      <div className="max-w-full mx-auto flex items-center justify-between gap-3">
        {/* min-w-0 lets this column shrink so the title's truncate applies;
            without it the header forces the whole page wider than a 320px
            viewport and pushes the lesson content off-screen. */}
        <div className="flex items-center gap-4 min-w-0 flex-1">
          <Link
            to="/app/courses"
            className="p-2 rounded-lg hover:bg-bg-tertiary/50 transition-colors text-text-tertiary hover:text-text-primary flex-shrink-0"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="min-w-0">
            <p className="text-xs text-text-tertiary uppercase tracking-wide">
              {t('lessons.lesson')} {lesson.order}
            </p>
            <h1 className="font-semibold text-text-primary truncate max-w-md">
              {lesson.translations[0]?.title}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-text-tertiary flex-shrink-0">
          {/* Duration and difficulty are also shown on the course page, so
              they step aside on the narrowest screens to keep the XP badge. */}
          <span className="hidden sm:flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>
              {lesson.estimated_minutes} {t('common.min')}
            </span>
          </span>
          <span className="hidden sm:flex items-center gap-1">
            <Target className="h-4 w-4" />
            <span>{t(`courses.difficulty_level.${lesson.difficulty}`)}</span>
          </span>
          <XPBadge xp={lesson.xp_reward} size="sm" />
        </div>
      </div>
    </header>
  );
}
