import { Link } from 'react-router-dom';
import { ArrowLeft, Code } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import { LEGAL_LAST_UPDATED } from '../config/site';

interface LegalLayoutProps {
  title: string;
  intro?: string;
  children: React.ReactNode;
  showLastUpdated?: boolean;
}

/**
 * Shared chrome for the standalone legal/contact pages reached from the
 * landing footer. Keeps them visually consistent with the marketing site
 * without pulling in the full authenticated app shell.
 */
export function LegalLayout({ title, intro, children, showLastUpdated = true }: LegalLayoutProps) {
  const { t, isRTL } = useTranslation();

  return (
    <div className={isRTL ? 'rtl' : 'ltr'}>
      <div className="min-h-screen bg-bg-primary">
        <header className="border-b border-border-primary/50 bg-bg-primary/90 backdrop-blur-xl">
          <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-4 sm:px-6">
            <Link to="/" className="flex items-center gap-2" aria-label={t('common.home')}>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-accent-500">
                <Code className="h-4 w-4 text-white" aria-hidden="true" />
              </div>
              <span className="text-lg font-bold text-text-primary">AtlasCode</span>
            </Link>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary"
            >
              <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden="true" />
              {t('legal.back_home')}
            </Link>
          </div>
        </header>

        <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
          <h1 className="text-3xl font-bold text-text-primary sm:text-4xl">{title}</h1>
          {showLastUpdated && (
            <p className="mt-2 text-sm text-text-tertiary">
              {t('legal.last_updated', { date: LEGAL_LAST_UPDATED })}
            </p>
          )}
          {intro && <p className="mt-6 text-lg leading-relaxed text-text-secondary">{intro}</p>}
          <div className="mt-10 space-y-8">{children}</div>
        </main>
      </div>
    </div>
  );
}
