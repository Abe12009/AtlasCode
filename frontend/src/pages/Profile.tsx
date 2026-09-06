import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { dashboardApi, authApi } from '../api/services';
import { Trophy, Target, Flame, FolderKanban, CheckCircle, Award, Settings, User, TrendingUp, Sparkles, Code, BookOpen, Terminal, Palette } from 'lucide-react';
import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { Card, Badge, Progress, Button, cn, Skeleton, XPBadge, StreakBadge, AchievementBadge, Alert, Modal } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';
import { ProfileAvatar } from '../components/ProfileAvatar';
import { AvatarBuilder } from '../components/AvatarBuilder';
import { AvatarUpload } from '../components/AvatarUpload';
import { ChangePasswordForm } from '../components/ChangePasswordForm';
import { DEFAULT_AVATAR_CONFIG, parseAvatarConfig, serializeAvatarConfig, type AvatarConfig } from '../lib/avatar';

export function Profile() {
  const { t, isRTL } = useTranslation();
  const queryClient = useQueryClient();
  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
  });

  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'settings'>('overview');
  const [editingAvatar, setEditingAvatar] = useState(false);
  const [avatarSaving, setAvatarSaving] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);
  const [avatarSaved, setAvatarSaved] = useState(false);
  const [privacySaving, setPrivacySaving] = useState(false);
  const [privacySaved, setPrivacySaved] = useState(false);
  const [deleteAccountModalOpen, setDeleteAccountModalOpen] = useState(false);

  const refreshDashboard = () => queryClient.invalidateQueries({ queryKey: ['dashboard'] });

  const saveAvatarConfig = async (config: AvatarConfig) => {
    setAvatarSaving(true);
    setAvatarSaved(false);
    try {
      await authApi.updateMe({ avatar_config: serializeAvatarConfig(config), avatar_type: 'generated' });
      await refreshDashboard();
      setAvatarSaved(true);
      setEditingAvatar(false);
    } finally {
      setAvatarSaving(false);
    }
  };

  const uploadAvatarPhoto = async (dataUrl: string) => {
    setAvatarUploading(true);
    setAvatarSaved(false);
    try {
      await authApi.uploadAvatar(dataUrl);
      await refreshDashboard();
      setAvatarSaved(true);
    } finally {
      setAvatarUploading(false);
    }
  };

  const setActiveAvatarType = async (type: 'upload' | 'generated') => {
    await authApi.updateMe({ avatar_type: type });
    await refreshDashboard();
  };

  const togglePrivacy = async (visibility: 'public' | 'private') => {
    setPrivacySaving(true);
    setPrivacySaved(false);
    try {
      await authApi.updateMe({ profile_visibility: visibility });
      await refreshDashboard();
      setPrivacySaved(true);
    } finally {
      setPrivacySaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
        <div>
          <Skeleton variant="text" width="30%" height={32} />
          <Skeleton variant="text" width="50%" height={20} className="mt-2" />
        </div>
        <div className="flex flex-col lg:flex-row gap-8">
          <aside className="lg:w-64 flex-shrink-0">
            <Skeleton variant="rectangular" width="100%" height={300} />
          </aside>
          <main className="flex-1 space-y-6">
            <Skeleton variant="rectangular" width="100%" height={200} />
            <Skeleton variant="rectangular" width="100%" height={200} />
            <Skeleton variant="rectangular" width="100%" height={200} />
          </main>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12" dir={isRTL ? 'rtl' : 'ltr'}>
        <p className="text-error-600 dark:text-error-400">{t('errors.generic')}</p>
      </div>
    );
  }

  const user = dashboard?.user;
  const profile = dashboard?.profile;
  const weekly = dashboard?.weekly;
  const recentAchievements = dashboard?.recent_achievements || [];

  /** A weekly delta only shows for values that actually happened — see backend/app/services/stats.py. */
  const trendFor = (amount: number): string | null => (amount > 0 ? `+${amount}` : null);

  const stats = [
    { label: t('profile.level'), value: profile?.level || 1, icon: Trophy, color: 'text-yellow-500 bg-yellow-900/30 border-yellow-500/30', trend: trendFor(weekly?.levels_gained ?? 0) },
    { label: t('profile.total_xp'), value: profile?.xp || 0, icon: Target, color: 'text-blue-500 bg-blue-900/30 border-blue-500/30', trend: trendFor(weekly?.xp ?? 0) },
    { label: t('profile.streak'), value: `${profile?.streak || 0} ${t('profile.days')}`, icon: Flame, color: 'text-orange-500 bg-orange-900/30 border-orange-500/30', trend: null },
    { label: t('profile.completed_lessons'), value: profile?.completed_lessons || 0, icon: CheckCircle, color: 'text-green-500 bg-green-900/30 border-green-500/30', trend: trendFor(weekly?.lessons_completed ?? 0) },
    { label: t('profile.completed_projects'), value: profile?.completed_projects || 0, icon: FolderKanban, color: 'text-purple-500 bg-purple-900/30 border-purple-500/30', trend: trendFor(weekly?.projects_completed ?? 0) },
  ];

  const tabs = [
    { id: 'overview', label: t('profile_page.overview'), icon: User },
    { id: 'achievements', label: t('profile_page.achievements'), icon: Award },
    { id: 'settings', label: t('profile_page.settings'), icon: Settings },
  ];

  return (
    <div className="space-y-8 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
      <div>
        <h1 className="text-2xl font-bold text-gradient-brand">
          {t('profile_page.title')}
        </h1>
        <p className="text-text-secondary mt-1">
          {t('profile_page.subtitle')}
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        <aside className="lg:w-64 flex-shrink-0">
          <Card variant="default" padding="lg" className="space-y-6 sticky top-24 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5" aria-hidden="true" />
            <div className="relative z-10">
              <div className="text-center">
                <ProfileAvatar
                  user={user}
                  size="xl"
                  className="mx-auto mb-4 ring-4 ring-primary-500/20"
                />
                <h2 className="text-xl font-bold text-text-primary">{user?.username}</h2>
                {user?.username && (
                  <Link
                    to={`/app/u/${encodeURIComponent(user.username)}`}
                    className="text-xs text-primary-400 hover:text-primary-300 font-medium"
                  >
                    {t('public_profile.view_public')}
                  </Link>
                )}
                <div className="flex items-center justify-center gap-2 mt-1">
                  <span className="px-3 py-1 bg-primary-500/10 text-primary-400 rounded-full text-sm font-medium">
                    {t('profile_page.level_label', { level: profile?.level || 1 })}
                  </span>
                </div>
                <div className="mt-4">
                  <Progress
                    value={(profile?.xp || 0) % 100}
                    max={100}
                    size="md"
                    variant="primary"
                    showLabel
                    label={t('profile_page.xp_to_next', { current: (profile?.xp || 0) % 100, total: 100 })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 pt-4 border-t border-border-primary/50">
                <div className="text-center p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                  <div className="text-2xl font-bold text-primary-400">{profile?.completed_lessons || 0}</div>
                  <div className="text-xs text-text-tertiary">{t('profile.completed_lessons')}</div>
                </div>
                <div className="text-center p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                  <div className="text-2xl font-bold text-accent-400">{profile?.completed_projects || 0}</div>
                  <div className="text-xs text-text-tertiary">{t('profile.completed_projects')}</div>
                </div>
                <div className="text-center p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                  <div className="text-2xl font-bold text-yellow-400">{recentAchievements.length}</div>
                  <div className="text-xs text-text-tertiary">{t('profile.achievements')}</div>
                </div>
              </div>

              <nav className="space-y-2" aria-label={t('profile_page.sections')}>
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as typeof activeTab)}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-fast',
                      activeTab === tab.id
                        ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                        : 'text-text-secondary hover:bg-bg-tertiary/50 hover:text-text-primary'
                    )}
                  >
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          </Card>
        </aside>

        <main className="flex-1 space-y-6">
          {activeTab === 'overview' && (
            <>
              <Card variant="default" padding="lg" className="relative overflow-hidden">
                <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
                <div className="relative z-10">
                  <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-accent-400" />
                    <span>{t('profile_page.statistics')}</span>
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {stats.map((stat) => (
                      <div key={stat.label} className="p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                        <div className={cn('p-3 rounded-xl', stat.color)}>
                          <stat.icon className="h-6 w-6" />
                        </div>
                        <p className="text-2xl font-bold text-text-primary mt-2 tabular-nums">{stat.value}</p>
                        <p className="text-sm text-text-tertiary">{stat.label}</p>
                        <div className="mt-2 flex items-center gap-1">
                          {stat.trend ? (
                            <>
                              <TrendingUp className="h-4 w-4 text-success-500" aria-hidden="true" />
                              <span className="text-sm font-medium text-success-600 dark:text-success-400">
                                {stat.trend} {t('profile_page.this_week')}
                              </span>
                            </>
                          ) : (
                            <span className="text-sm text-text-tertiary">{t('dashboard.no_activity_this_week')}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>

              <Card variant="default" padding="lg" className="relative overflow-hidden">
                <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
                <div className="relative z-10">
                  <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
                    <Code className="h-5 w-5 text-accent-400" />
                    <span>{t('profile_page.account_info')}</span>
                  </h2>
                  <dl className="space-y-4">
                    <div className="grid grid-cols-3 gap-4 py-3 border-b border-border-primary/50">
                      <dt className="text-text-tertiary">{t('common.username')}</dt>
                      <dd className="col-span-2 font-medium text-text-primary">{user?.username}</dd>
                    </div>
                    <div className="grid grid-cols-3 gap-4 py-3 border-b border-border-primary/50">
                      <dt className="text-text-tertiary">{t('common.email')}</dt>
                      <dd className="col-span-2 font-medium text-text-primary">{user?.email}</dd>
                    </div>
                    <div className="grid grid-cols-3 gap-4 py-3 border-b border-border-primary/50">
                      <dt className="text-text-tertiary">{t('common.preferred_language')}</dt>
                      <dd className="col-span-2 font-medium text-text-primary capitalize">{user?.preferred_language}</dd>
                    </div>
                    <div className="grid grid-cols-3 gap-4 py-3">
                      <dt className="text-text-tertiary">{t('profile_page.member_since')}</dt>
                      <dd className="col-span-2 font-medium text-text-primary">
                        {user?.created_at ? (formatDistanceToNow(new Date(user.created_at), { addSuffix: true }) ?? '') : t('common.unknown')}
                      </dd>
                    </div>
                  </dl>
                </div>
              </Card>

              <Card variant="default" padding="lg" className="relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5" aria-hidden="true" />
                <div className="relative z-10">
                  <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-primary-400" />
                    <span>{t('profile_page.skills_overview')}</span>
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                      <div className="p-2 bg-primary-500/10 rounded-lg mb-2">
                        <Code className="h-5 w-5 text-primary-400" />
                      </div>
                      <h4 className="font-medium text-text-primary">Python</h4>
                      <p className="text-sm text-text-tertiary mt-1">Primary Language</p>
                    </div>
                    <div className="p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                      <div className="p-2 bg-accent-500/10 rounded-lg mb-2">
                        <Terminal className="h-5 w-5 text-accent-400" />
                      </div>
                      <h4 className="font-medium text-text-primary">Algorithms</h4>
                      <p className="text-sm text-text-tertiary mt-1">Problem Solving</p>
                    </div>
                    <div className="p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                      <div className="p-2 bg-success-500/10 rounded-lg mb-2">
                        <BookOpen className="h-5 w-5 text-success-400" />
                      </div>
                      <h4 className="font-medium text-text-primary">Data Structures</h4>
                      <p className="text-sm text-text-tertiary mt-1">Core CS Concepts</p>
                    </div>
                  </div>
                </div>
              </Card>
            </>
          )}

          {activeTab === 'achievements' && (
            <Card variant="default" padding="lg" className="relative overflow-hidden">
              <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
              <div className="relative z-10">
                <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
                  <Award className="h-5 w-5 text-yellow-400" />
                  <span>{t('profile_page.your_achievements')}</span>
                </h2>
                {recentAchievements.length > 0 ? (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {recentAchievements.map((ua) => (
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
                  <div className="text-center py-12">
                    <Award className="h-16 w-16 text-text-tertiary mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-text-primary mb-2">{t('profile_page.no_achievements')}</h3>
                    <p className="text-text-secondary">{t('profile_page.complete_lessons')}</p>
                  </div>
                )}
              </div>
            </Card>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-6 max-w-2xl">
              <Card variant="default" padding="lg" className="relative overflow-hidden">
                <div className="relative z-10">
                  <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
                    <Palette className="h-5 w-5 text-accent-400" />
                    <span>{t('avatar.title')}</span>
                  </h2>

                  {avatarSaved && <Alert variant="success" className="mb-4">{t('avatar.saved')}</Alert>}

                  {editingAvatar ? (
                    <AvatarBuilder
                      initialConfig={parseAvatarConfig(user?.avatar_config) ?? DEFAULT_AVATAR_CONFIG}
                      onSave={saveAvatarConfig}
                      saving={avatarSaving}
                    />
                  ) : (
                    <div className="flex flex-col sm:flex-row items-start gap-6">
                      <ProfileAvatar user={user} size="2xl" />
                      <div className="flex-1 space-y-4">
                        <div className="flex items-center gap-3">
                          <label className="flex items-center gap-2 text-sm text-text-secondary">
                            <input
                              type="radio"
                              name="avatar_type"
                              checked={user?.avatar_type !== 'generated'}
                              onChange={() => setActiveAvatarType('upload')}
                              disabled={!user?.avatar_url && !user?.avatar_image_data}
                            />
                            {t('avatar.uploaded')}
                          </label>
                          <label className="flex items-center gap-2 text-sm text-text-secondary">
                            <input
                              type="radio"
                              name="avatar_type"
                              checked={user?.avatar_type === 'generated'}
                              onChange={() => setActiveAvatarType('generated')}
                              disabled={!user?.avatar_config}
                            />
                            {t('avatar.built')}
                          </label>
                        </div>
                        <div className="flex flex-wrap gap-3">
                          <Button variant="outline" onClick={() => setEditingAvatar(true)}>
                            {user?.avatar_config ? t('avatar.edit') : t('avatar.build_one')}
                          </Button>
                          <AvatarUpload onUpload={uploadAvatarPhoto} uploading={avatarUploading} />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </Card>

              {user?.has_password ? (
                <Card variant="default" padding="lg" className="relative overflow-hidden">
                  <div className="relative z-10">
                    <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
                      <Settings className="h-5 w-5 text-accent-400" />
                      <span>{t('settings.change_password')}</span>
                    </h2>
                    <ChangePasswordForm />
                  </div>
                </Card>
              ) : (
                <Card variant="default" padding="lg" className="relative overflow-hidden">
                  <div className="relative z-10">
                    <h2 className="text-lg font-semibold text-text-primary mb-2">{t('settings.no_password_title')}</h2>
                    <p className="text-text-secondary text-sm">{t('settings.no_password_description')}</p>
                  </div>
                </Card>
              )}

              <Card variant="default" padding="lg" className="relative overflow-hidden">
                <div className="relative z-10">
                  <h2 className="text-lg font-semibold text-text-primary mb-2">{t('settings.privacy_title')}</h2>
                  <p className="text-text-secondary text-sm mb-4">{t('settings.privacy_description')}</p>
                  {privacySaved && <Alert variant="success" className="mb-4">{t('settings.privacy_updated')}</Alert>}
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm text-text-primary">
                      <input
                        type="radio"
                        name="profile_visibility"
                        checked={(user?.profile_visibility ?? 'private') === 'private'}
                        disabled={privacySaving}
                        onChange={() => togglePrivacy('private')}
                      />
                      {t('settings.profile_private')}
                    </label>
                    <label className="flex items-center gap-2 text-sm text-text-primary">
                      <input
                        type="radio"
                        name="profile_visibility"
                        checked={user?.profile_visibility === 'public'}
                        disabled={privacySaving}
                        onChange={() => togglePrivacy('public')}
                      />
                      {t('settings.profile_public')}
                    </label>
                  </div>
                </div>
              </Card>

              <Card variant="default" padding="lg" className="relative overflow-hidden">
                <div className="relative z-10">
                  <h2 className="text-lg font-semibold text-text-primary mb-6 flex items-center gap-2">
                    <Settings className="h-5 w-5 text-accent-400" />
                    <span>{t('profile_page.settings')}</span>
                  </h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-1">
                        {t('common.preferred_language')}
                      </label>
                      <select
                        defaultValue={user?.preferred_language}
                        className="w-full px-4 py-3 border border-border-primary/50 rounded-lg bg-bg-secondary/50 text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-transparent"
                      >
                        <option value="en">{t('common.english')}</option>
                        <option value="fr">{t('common.french')}</option>
                        <option value="ar">{t('common.arabic')}</option>
                      </select>
                    </div>
                    <div className="pt-6 border-t border-border-primary/50">
                      <Button
                        variant="destructive"
                        className="w-full"
                        onClick={() => setDeleteAccountModalOpen(true)}
                      >
                        {t('profile_page.delete_account')}
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </main>

        <Modal
          isOpen={deleteAccountModalOpen}
          onClose={() => setDeleteAccountModalOpen(false)}
          title={t('profile_page.delete_account')}
          size="sm"
        >
          <p className="text-text-secondary text-sm">
            {t('profile_page.delete_account_confirm')}
          </p>
          <p className="mt-3 text-sm text-text-tertiary">
            {t('profile_page.delete_account_not_implemented')}
          </p>
          <div className="mt-6 flex justify-end gap-3">
            <Button variant="outline" onClick={() => setDeleteAccountModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              variant="destructive"
              disabled
              title={t('profile_page.delete_account_not_implemented')}
            >
              {t('profile_page.delete_account')}
            </Button>
          </div>
        </Modal>
      </div>
    </div>
  );
}
