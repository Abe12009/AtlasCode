import { useTranslation } from '../hooks/useTranslation';
import { Skeleton, SkeletonCard } from './ui/Skeleton';

/** Route-level Suspense fallback. Used for every lazy page (Dashboard,
 * Courses, Login, ...), so it approximates the shape most of them share --
 * a heading plus a card grid -- rather than a page-specific layout. A
 * generic skeleton reads calmer than a spinner during the brief chunk-load
 * window and matches the polish pass everywhere else in the app. */
export function LoadingFallback() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen pt-20 pb-8 max-w-full w-full mx-auto px-4 sm:px-6 lg:px-8">
      <span className="sr-only" role="status">{t('common.loading')}</span>
      <div className="space-y-8 animate-fade-in" aria-hidden="true">
        <div className="flex items-center justify-between">
          <Skeleton variant="text" width="30%" height={32} />
          <Skeleton variant="rectangular" width={140} height={40} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard className="hidden sm:block" />
          <SkeletonCard className="hidden lg:block" />
        </div>
      </div>
    </div>
  );
}
