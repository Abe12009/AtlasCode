import { Check, ChevronDown, Globe } from 'lucide-react';
import { Dropdown, DropdownItem } from './ui/Dropdown';
import { useTranslation } from '../hooks/useTranslation';
import { cn } from '../lib/utils';

const FLAGS: Record<string, string> = {
  en: '🇬🇧',
  fr: '🇫🇷',
  ar: '🇸🇦',
};

/**
 * The single language control used everywhere — marketing pages and the app
 * alike. It writes through `useTranslation().changeLanguage`, which is the one
 * place that persists the choice and syncs it to the signed-in user's profile,
 * so a language picked before logging in survives into the application.
 */
export function LanguageSwitcher({
  className,
  align = 'end',
}: {
  className?: string;
  align?: 'start' | 'center' | 'end';
}) {
  const { t, currentLanguage, changeLanguage, languages } = useTranslation();
  const active = languages.find((language) => language.code === currentLanguage);

  return (
    <Dropdown position="bottom" align={align}>
      <button
        type="button"
        aria-label={t('common.language')}
        className={cn(
          'inline-flex items-center gap-1.5 rounded-xl border border-border-primary bg-bg-secondary px-2.5 py-2',
          'text-sm font-medium text-text-secondary',
          'transition-colors duration-fast hover:text-text-primary hover:border-border-secondary',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary',
          className,
        )}
      >
        <Globe className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
        <span className="hidden sm:inline">{active?.nativeName ?? currentLanguage}</span>
        <span className="sm:hidden uppercase">{currentLanguage}</span>
        <ChevronDown className="h-3.5 w-3.5 text-text-tertiary" aria-hidden="true" />
      </button>
      <div className="w-44 py-1">
        {languages.map((language) => {
          const isActive = currentLanguage === language.code;
          return (
            <DropdownItem
              key={language.code}
              onClick={() => changeLanguage(language.code)}
              aria-current={isActive ? 'true' : undefined}
            >
              <span className="flex w-full items-center gap-2">
                <span className="text-base leading-none" aria-hidden="true">
                  {FLAGS[language.code] ?? '🌐'}
                </span>
                <span className="flex-1 text-start">{language.nativeName}</span>
                {isActive && (
                  <Check className="h-4 w-4 flex-shrink-0 text-primary-500" aria-hidden="true" />
                )}
              </span>
            </DropdownItem>
          );
        })}
      </div>
    </Dropdown>
  );
}
