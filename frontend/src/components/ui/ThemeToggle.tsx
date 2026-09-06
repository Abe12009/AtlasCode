import { Monitor, Moon, Sun } from 'lucide-react';
import { useTheme, type ThemePreference } from '../../contexts/ThemeContext';
import { useTranslation } from '../../hooks/useTranslation';
import { cn } from '../../lib/utils';

const ICONS: Record<ThemePreference, typeof Sun> = {
  light: Sun,
  dark: Moon,
  system: Monitor,
};

const LABEL_KEYS: Record<ThemePreference, string> = {
  light: 'theme.light',
  dark: 'theme.dark',
  system: 'theme.system',
};

/**
 * Segmented light / dark / system control.
 *
 * A three-state setting is genuinely three choices, so it gets three visible
 * targets rather than a toggle the user has to click twice to understand. On
 * narrow screens the labels drop away and the icons carry the meaning, with the
 * text kept for assistive technology.
 */
export function ThemeToggle({
  className,
  showLabels = false,
}: {
  className?: string;
  /** Render the text label beside each icon (used in wide menus/settings). */
  showLabels?: boolean;
}) {
  const { preference, setPreference, preferences } = useTheme();
  const { t } = useTranslation();

  return (
    <div
      role="radiogroup"
      aria-label={t('theme.label')}
      className={cn(
        'inline-flex items-center gap-0.5 rounded-xl border border-border-primary bg-bg-secondary p-0.5',
        className,
      )}
    >
      {preferences.map((option) => {
        const Icon = ICONS[option];
        const isActive = preference === option;
        const label = t(LABEL_KEYS[option]);
        return (
          <button
            key={option}
            type="button"
            role="radio"
            aria-checked={isActive}
            aria-label={label}
            title={label}
            onClick={() => setPreference(option)}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-[0.6rem] px-2 py-1.5 text-xs font-medium',
              'transition-colors duration-fast',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:ring-offset-1 focus-visible:ring-offset-bg-secondary',
              isActive
                ? 'bg-bg-elevated text-text-primary shadow-xs'
                : 'text-text-tertiary hover:text-text-primary hover:bg-bg-tertiary',
            )}
          >
            <Icon className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
            {showLabels ? <span>{label}</span> : <span className="sr-only">{label}</span>}
          </button>
        );
      })}
    </div>
  );
}
