import { useTranslation } from '../hooks/useTranslation';

export function LoadingFallback() {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent" />
      <p className="mt-4 text-gray-600 dark:text-gray-400">{t('common.loading')}</p>
    </div>
  );
}