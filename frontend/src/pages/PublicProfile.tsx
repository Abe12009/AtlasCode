import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Trophy, Target, Flame, Award, UserX } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { usersApi } from '../api/services';
import { Card, Skeleton, AchievementBadge, EmptyState } from '../components/ui';
import { ProfileAvatar } from '../components/ProfileAvatar';
import { useTranslation } from '../hooks/useTranslation';

export function PublicProfile() {
  const { username } = useParams<{ username: string }>();
  const { t, isRTL } = useTranslation();

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['public-profile', username],
    queryFn: () => usersApi.getPublicProfile(username!),
    enabled: !!username,
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
        <Skeleton variant="rectangular" width="100%" height={200} />
        <Skeleton variant="rectangular" width="100%" height={300} />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="max-w-2xl mx-auto animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
        <EmptyState
          icon={<UserX className="h-12 w-12" />}
          title={t('public_profile.not_found_title')}
          description={t('public_profile.not_found_description')}
          action={
            <Link to="/app/dashboard" className="text-primary-400 hover:text-primary-300 font-medium">
              {t('common.back_to_courses')}
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
      <Card variant="default" padding="lg" className="text-center relative overflow-hidden">
        <div className="relative z-10 flex flex-col items-center">
          <ProfileAvatar user={profile} size="2xl" className="ring-4 ring-primary-500/20 mb-4" />
          <h1 className="text-2xl font-bold text-text-primary">{profile.username}</h1>
          <p className="text-text-tertiary text-sm mt-1">
            {t('public_profile.member_since', {
              date: formatDistanceToNow(new Date(profile.member_since), { addSuffix: true }),
            })}
          </p>

          <div className="grid grid-cols-3 gap-4 mt-6 w-full max-w-sm">
            <div className="p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
              <Trophy className="h-5 w-5 text-yellow-500 mx-auto mb-1" aria-hidden="true" />
              <div className="text-xl font-bold text-text-primary">{profile.level}</div>
              <div className="text-xs text-text-tertiary">{t('profile.level')}</div>
            </div>
            <div className="p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
              <Target className="h-5 w-5 text-blue-500 mx-auto mb-1" aria-hidden="true" />
              <div className="text-xl font-bold text-text-primary">{profile.xp}</div>
              <div className="text-xs text-text-tertiary">{t('profile.total_xp')}</div>
            </div>
            <div className="p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
              <Flame className="h-5 w-5 text-orange-500 mx-auto mb-1" aria-hidden="true" />
              <div className="text-xl font-bold text-text-primary">{profile.streak}</div>
              <div className="text-xs text-text-tertiary">{t('profile.streak')}</div>
            </div>
          </div>
        </div>
      </Card>

      <Card variant="default" padding="lg" className="relative overflow-hidden">
        <div className="relative z-10">
          <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
            <Award className="h-5 w-5 text-yellow-400" aria-hidden="true" />
            <span>{t('profile_page.achievements')}</span>
          </h2>
          {profile.achievements.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {profile.achievements.map((ua) => (
                <AchievementBadge
                  key={ua.id}
                  icon={ua.achievement.icon || '🏆'}
                  title={ua.achievement.translations[0]?.title}
                  description={ua.achievement.translations[0]?.description ?? ''}
                  xpReward={ua.achievement.xp_reward}
                  earned={true}
                  earnedAt={formatDistanceToNow(new Date(ua.earned_at), { addSuffix: true }) ?? ''}
                  size="md"
                />
              ))}
            </div>
          ) : (
            <p className="text-text-secondary text-center py-8">{t('profile_page.no_achievements')}</p>
          )}
        </div>
      </Card>
    </div>
  );
}
