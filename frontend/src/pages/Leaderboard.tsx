import { useState } from 'react';
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Trophy, Lock, Globe, AlertCircle } from 'lucide-react';
import { authApi, leaderboardApi } from '../api/services';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { Button, Card, Skeleton, XPBadge, cn } from '../components/ui';
import { ProfileAvatar } from '../components/ProfileAvatar';
import type { LeaderboardEntry, LeaderboardResponse } from '../types';

const PAGE_SIZE = 25;

/**
 * The all-time XP board.
 *
 * Opt-in: a learner is listed only while `profile_visibility` is "public",
 * which is the same switch that makes their profile viewable (Profile →
 * settings). This page offers it as one tap, and says in full what becomes
 * visible before it is tapped -- username, avatar, level, XP, and nothing
 * else, which is exactly what the endpoint returns.
 *
 * Numbers are formatted with a bare `toLocaleString()`, matching XPBadge, so
 * a rank and an XP figure in the same row use the same numerals. Passing the
 * UI language instead would print Arabic-Indic digits next to XPBadge's
 * Western ones on the very same line.
 */
function formatNumber(value: number): string {
  return value.toLocaleString();
}

export function Leaderboard() {
  const { t, isRTL } = useTranslation();
  const { user, refreshUser } = useAuth();
  const queryClient = useQueryClient();
  const [visibilityError, setVisibilityError] = useState(false);

  const {
    data,
    isLoading,
    isError,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery<LeaderboardResponse>({
    queryKey: ['leaderboard'],
    queryFn: ({ pageParam }) =>
      leaderboardApi.get({
        limit: PAGE_SIZE,
        ...(typeof pageParam === 'string' ? { cursor: pageParam } : {}),
      }),
    initialPageParam: undefined as string | undefined,
    // Null once the listing is exhausted or the depth cap is reached, which
    // is what retires the "Load more" button.
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
  });

  /** Joining and leaving are the same call -- PATCH /auth/me, the existing
   * profile-visibility switch. There is no leaderboard-specific opt-in that
   * could drift out of step with the profile one. */
  const visibilityMutation = useMutation({
    mutationFn: (visibility: 'public' | 'private') =>
      authApi.updateMe({ profile_visibility: visibility }),
    onMutate: () => setVisibilityError(false),
    onSuccess: async () => {
      await refreshUser();
      // The board itself changes: the caller joins or leaves the listing,
      // which shifts everyone below them by one.
      await queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
    },
    onError: () => setVisibilityError(true),
  });

  const pages = data?.pages ?? [];
  const entries: LeaderboardEntry[] = pages.flatMap((page) => page.entries);
  // `me` is the same on every page; the newest one is as good as the first.
  const me = pages.length > 0 ? pages[pages.length - 1].me : undefined;
  const isListed = me?.is_listed ?? user?.profile_visibility === 'public';

  return (
    <div className="space-y-6 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
      <header className="flex items-center gap-3">
        <div className="p-3 rounded-xl bg-yellow-500/10">
          <Trophy className="h-7 w-7 text-yellow-400" aria-hidden="true" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-text-primary">{t('leaderboard.title')}</h1>
          <p className="text-sm text-text-secondary">{t('leaderboard.subtitle')}</p>
        </div>
      </header>

      {/* The only blurred surface on the page: the learner's own standing,
          which is the one thing they came to read. Every row below is
          .glass-flat (Card's default). */}
      <Card variant="glass" padding="lg" data-testid="my-rank-card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <ProfileAvatar user={user} size="lg" />
            <div className="min-w-0">
              <p className="text-xs uppercase tracking-wide text-text-tertiary">
                {t('leaderboard.your_rank')}
              </p>
              <p className="text-2xl font-bold text-text-primary tabular-nums" data-testid="my-rank">
                {me ? `#${formatNumber(me.rank)}` : '—'}
              </p>
              <p className="text-sm text-text-secondary truncate">
                {user?.username}
                {me ? ` · ${t('profile.level')} ${formatNumber(me.level)}` : ''}
              </p>
            </div>
          </div>
          <div className="flex flex-col items-start sm:items-end gap-2">
            {me ? <XPBadge xp={me.xp} size="md" /> : null}
            <p
              className={cn(
                'flex items-center gap-1.5 text-xs',
                isListed ? 'text-success-400' : 'text-text-tertiary',
              )}
              data-testid="listing-status"
            >
              {isListed ? (
                <Globe className="h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
              ) : (
                <Lock className="h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
              )}
              <span>{isListed ? t('leaderboard.listed') : t('leaderboard.not_listed')}</span>
            </p>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-border-primary/50 space-y-3">
          <p className="text-sm text-text-secondary">
            {isListed ? t('leaderboard.listed_explainer') : t('leaderboard.join_explainer')}
          </p>
          <div className="flex items-center gap-3 flex-wrap">
            {isListed ? (
              <Button
                variant="secondary"
                onClick={() => visibilityMutation.mutate('private')}
                disabled={visibilityMutation.isPending}
                data-testid="leave-leaderboard"
              >
                {visibilityMutation.isPending ? t('leaderboard.leaving') : t('leaderboard.leave')}
              </Button>
            ) : (
              <Button
                onClick={() => visibilityMutation.mutate('public')}
                disabled={visibilityMutation.isPending}
                leftIcon={<Trophy className="h-4 w-4" />}
                data-testid="join-leaderboard"
              >
                {visibilityMutation.isPending ? t('leaderboard.joining') : t('leaderboard.join')}
              </Button>
            )}
            {visibilityError && (
              <span role="alert" className="text-xs text-error-400">
                {t('errors.generic')}
              </span>
            )}
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="space-y-2" data-testid="leaderboard-loading">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} variant="rectangular" width="100%" height={64} />
          ))}
        </div>
      ) : isError ? (
        <Card padding="lg" className="text-center space-y-3" data-testid="leaderboard-error">
          <AlertCircle className="h-6 w-6 text-error-400 mx-auto" aria-hidden="true" />
          <p className="text-text-secondary">{t('leaderboard.failed_to_load')}</p>
          <Button variant="secondary" onClick={() => refetch()}>
            {t('leaderboard.retry')}
          </Button>
        </Card>
      ) : entries.length === 0 ? (
        <Card padding="lg" className="text-center" data-testid="leaderboard-empty">
          <p className="text-text-secondary">{t('leaderboard.empty')}</p>
        </Card>
      ) : (
        <>
          <ol className="space-y-2" aria-label={t('leaderboard.title')}>
            {entries.map((entry) => {
              const isMe = entry.username === user?.username;
              return (
                <li key={`${entry.rank}-${entry.username}`}>
                  <Card
                    padding="none"
                    // aria-current marks the learner's own row for a screen
                    // reader, not just the ring that marks it visually.
                    aria-current={isMe ? 'true' : undefined}
                    data-testid={isMe ? 'leaderboard-row-me' : `leaderboard-row-${entry.rank}`}
                    className={cn(
                      'flex items-center gap-3 p-3 sm:p-4',
                      isMe && 'ring-2 ring-primary-500/60',
                    )}
                  >
                    <span
                      className="w-10 shrink-0 text-end text-sm font-semibold text-text-secondary tabular-nums"
                      aria-label={`${t('leaderboard.rank')} ${formatNumber(entry.rank)}`}
                    >
                      {formatNumber(entry.rank)}
                    </span>
                    <ProfileAvatar user={entry} size="sm" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-text-primary truncate">
                        {entry.username}
                        {isMe && (
                          <span className="ms-2 text-xs font-normal text-primary-400">
                            {t('leaderboard.you')}
                          </span>
                        )}
                      </p>
                      <p className="text-xs text-text-tertiary tabular-nums">
                        {t('profile.level')} {formatNumber(entry.level)}
                      </p>
                    </div>
                    <XPBadge xp={entry.xp} size="sm" showIcon={false} />
                  </Card>
                </li>
              );
            })}
          </ol>

          <div className="flex flex-col items-center gap-2">
            {hasNextPage ? (
              <Button
                variant="secondary"
                onClick={() => fetchNextPage()}
                disabled={isFetchingNextPage}
                data-testid="leaderboard-load-more"
              >
                {isFetchingNextPage ? t('leaderboard.loading_more') : t('leaderboard.load_more')}
              </Button>
            ) : (
              <p className="text-xs text-text-tertiary text-center">
                {t('leaderboard.depth_notice')}
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
