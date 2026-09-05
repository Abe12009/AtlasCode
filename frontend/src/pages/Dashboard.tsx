import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { dashboardApi } from '../api/services';
import { BookOpen, FolderKanban, Trophy, Flame, Code, ArrowRight, Target, CheckCircle, TrendingUp, Sparkles, Flag, MapPin } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Card, Badge, Progress, Button, cn, Skeleton, StatusBadge, XPBadge, StreakBadge, QuestRoadmap } from '../components/ui';
import type { QuestNodeData } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';

export function Dashboard() {
  const { t } = useTranslation();
  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
  });

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div className="flex items-center justify-between">
          <Skeleton variant="text" width="40%" height={32} />
          <Skeleton variant="rectangular" width={160} height={44} />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
        <div className="space-y-6">
          <SkeletonCard className="h-96" />
          <SkeletonCard className="h-64" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-error-600 dark:text-error-400">{t('errors.generic')}</p>
      </div>
    );
  }

  const user = dashboard?.user;
  const profile = dashboard?.profile;
  const currentMission = dashboard?.current_mission;
  const courseProgress = dashboard?.course_progress || [];
  const recentAchievements = dashboard?.recent_achievements || [];
  const currentProject = dashboard?.current_project;

  const stats = [
    { label: t('dashboard.level'), value: profile?.level || 1, icon: Trophy, color: 'text-yellow-500 bg-yellow-900/30 border-yellow-500/30', trend: '+1' },
    { label: t('dashboard.xp'), value: profile?.xp || 0, icon: Target, color: 'text-blue-500 bg-blue-900/30 border-blue-500/30', trend: '+150' },
    { label: t('dashboard.lessons_completed'), value: profile?.completed_lessons || 0, icon: CheckCircle, color: 'text-green-500 bg-green-900/30 border-green-500/30', trend: '+3' },
    { label: t('dashboard.streak'), value: `${profile?.streak || 0} ${t('dashboard.days')}`, icon: Flame, color: 'text-orange-500 bg-orange-900/30 border-orange-500/30', trend: '+1' },
  ];

  const buildQuestNodes = (): QuestNodeData[] => {
    const nodes: QuestNodeData[] = [];

    if (courseProgress.length > 0) {
      courseProgress.forEach((progress, courseIndex) => {
        const courseId = progress.course_id;
        const completed = progress.completed_lessons;
        const total = progress.total_lessons;
        const percent = progress.progress_percent;

        for (let i = 1; i <= total; i++) {
          let status: QuestNodeData['status'] = 'locked';
          if (i < completed) status = 'completed';
          else if (i === completed + 1 && percent < 100) status = 'current';
          else if (i === completed + 1 && percent >= 100) status = 'completed';
          else if (i <= completed) status = 'completed';
          else status = 'available';

          nodes.push({
            id: `course-${courseId}-lesson-${i}`,
            title: `${t('dashboard.course')} ${courseIndex + 1} - ${t('dashboard.lesson')} ${i}`,
            type: 'lesson',
            status,
            estimatedMinutes: 30,
            xpReward: 50 + (i * 10),
            path: `/app/lessons/${courseId}-${i}`,
          });
        }

        if (courseIndex < courseProgress.length - 1) {
          nodes.push({
            id: `checkpoint-${courseId}`,
            title: t('dashboard.checkpoint'),
            type: 'checkpoint',
            status: percent >= 100 ? 'completed' : 'locked',
            estimatedMinutes: 0,
            xpReward: 200,
          });
        }
      });
    }

    if (nodes.length === 0) {
      nodes.push(
        { id: 'welcome-1', title: t('dashboard.welcome_lesson_1'), type: 'lesson', status: 'available', estimatedMinutes: 30, xpReward: 50, path: '/app/courses' },
        { id: 'welcome-2', title: t('dashboard.welcome_lesson_2'), type: 'lesson', status: 'locked', estimatedMinutes: 30, xpReward: 50 },
        { id: 'welcome-3', title: t('dashboard.welcome_lesson_3'), type: 'lesson', status: 'locked', estimatedMinutes: 45, xpReward: 75 },
        { id: 'welcome-project', title: t('dashboard.first_project'), type: 'project', status: 'locked', estimatedMinutes: 120, xpReward: 300 },
      );
    }

    return nodes;
  };

  const questNodes = buildQuestNodes();

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary bg-gradient-to-r from-text-primary via-primary-400 to-accent-400 bg-clip-text text-transparent">
            {t('dashboard.welcome_back', { username: user?.username || '' })}
          </h1>
          <p className="text-text-secondary mt-1">
            {t('dashboard.continue_journey')}
          </p>
        </div>
        <Link
          to="/app/courses"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-glow-primary"
        >
          <BookOpen className="h-5 w-5" />
          <span>{t('dashboard.browse_courses')}</span>
        </Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label} variant="default" padding="md" className="animate-slide-up group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-tertiary">{stat.label}</p>
                <p className="text-2xl font-bold text-text-primary mt-1 tabular-nums">{stat.value}</p>
              </div>
              <div className={cn('p-3 rounded-xl', stat.color)}>
                <stat.icon className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-success-500" />
              <span className="text-sm font-medium text-success-600 dark:text-success-400">{stat.trend} {t('dashboard.this_week')}</span>
            </div>
          </Card>
        ))}
      </div>

      <div className="bg-bg-secondary/50 border border-border-primary/50 rounded-2xl p-6 lg:p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-500/10 rounded-xl">
              <MapPin className="h-6 w-6 text-primary-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                {t('dashboard.quest_board')}
                <Sparkles className="h-4 w-4 text-accent-400" />
              </h2>
              <p className="text-sm text-text-secondary">
                {t('dashboard.quest_board_desc')}
              </p>
            </div>
          </div>
          <Link
            to="/app/courses"
            className="text-sm text-primary-400 hover:text-primary-300 font-medium flex items-center gap-1"
          >
            {t('dashboard.view_all')}
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <QuestRoadmap nodes={questNodes} variant="horizontal" />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {currentMission && (
            <Card variant="interactive" padding="lg" className="border-primary-500/20 bg-primary-500/5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary-500/10 rounded-xl">
                    <Code className="h-6 w-6 text-primary-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h2 className="text-lg font-semibold text-text-primary">
                        {t('dashboard.current_mission')}
                      </h2>
                      <StatusBadge status="in_progress" size="sm" />
                    </div>
                    <p className="text-sm text-text-secondary">
                      {currentMission.translations[0]?.title}
                    </p>
                  </div>
                </div>
              </div>
              <p className="text-text-secondary mb-4">
                {currentMission.translations[0]?.story}
              </p>
              <div className="flex flex-wrap gap-2 mb-4">
                {currentMission.translations[0]?.skills?.split(', ').map((skill) => (
                  <Badge key={skill} variant="outline" size="sm" className="border-primary-500/30 text-primary-400">
                    {skill}
                  </Badge>
                ))}
              </div>
              <Link
                to={`/app/lessons/${currentMission.id}`}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-glow-primary"
              >
                <span>{t('dashboard.continue_learning')}</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Card>
          )}

          <Card variant="default" padding="lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                <Flag className="h-5 w-5 text-accent-400" />
                <span>{t('dashboard.your_progress')}</span>
              </h2>
              <Link to="/app/courses" className="text-sm text-primary-400 hover:text-primary-300 font-medium flex items-center gap-1">
                {t('dashboard.view_all')}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="space-y-4">
              {courseProgress.length > 0 ? (
                courseProgress.map((progress) => (
                  <div key={progress.course_id}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-text-primary">
                        {t('dashboard.course')} {progress.course_id}
                      </span>
                      <span className="text-sm font-semibold text-primary-400">
                        {progress.progress_percent.toFixed(0)}%
                      </span>
                    </div>
                    <Progress
                      value={progress.progress_percent}
                      size="md"
                      variant="primary"
                      showLabel={false}
                    />
                    <p className="text-xs text-text-tertiary">
                      {progress.completed_lessons} {t('dashboard.of')} {progress.total_lessons} {t('dashboard.lessons_completed')}
                    </p>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-text-tertiary mx-auto mb-3" />
                  <p className="text-text-secondary mb-3">{t('dashboard.no_courses_started')}</p>
                  <Link
                    to="/app/courses"
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-glow-primary"
                  >
                    <BookOpen className="h-4 w-4" />
                    <span>{t('dashboard.browse_courses')}</span>
                  </Link>
                </div>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card variant="default" padding="lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                <Trophy className="h-5 w-5 text-yellow-400" />
                <span>{t('dashboard.achievements')}</span>
              </h2>
              <Link to="/app/profile?tab=achievements" className="text-sm text-primary-400 hover:text-primary-300 font-medium">
                {t('dashboard.view_all')}
              </Link>
            </div>
            <div className="space-y-3">
              {recentAchievements.length > 0 ? (
                recentAchievements.map((ua) => (
                  <div key={ua.id} className="flex items-center gap-3 p-3 bg-bg-secondary rounded-xl border border-border-primary/50 group hover:border-primary-500/30 transition-colors">
                    <div className="p-2 bg-yellow-500/10 rounded-full">
                      <span className="text-2xl">{ua.achievement.icon || '🏆'}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-text-primary truncate">
                        {ua.achievement.translations[0]?.title}
                      </p>
                      <p className="text-xs text-text-tertiary">
                        {t('dashboard.earned', { date: formatDistanceToNow(new Date(ua.earned_at), { addSuffix: true }) ?? '' })}
                      </p>
                    </div>
                    <XPBadge xp={ua.achievement.xp_reward} size="sm" />
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Trophy className="h-12 w-12 text-text-tertiary mx-auto mb-3" />
                  <p className="text-text-secondary mb-1">{t('dashboard.no_achievements')}</p>
                  <p className="text-xs text-text-tertiary">{t('dashboard.complete_lessons')}</p>
                </div>
              )}
            </div>
          </Card>

          {currentProject && (
            <Card variant="interactive" padding="lg" className="border-blue-500/20 bg-blue-500/5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-500/10 rounded-xl">
                    <FolderKanban className="h-6 w-6 text-blue-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-text-primary">{t('dashboard.current_project')}</h2>
                    <p className="text-sm text-text-secondary">{t('dashboard.project')} {currentProject.project_id}</p>
                  </div>
                </div>
                <StatusBadge
                  status={currentProject.status === 'in_progress' ? 'in_progress' : 'available'}
                  size="sm"
                />
              </div>
              <Link
                to={`/app/projects/${currentProject.project_id}`}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-blue-500/30 w-full justify-center"
              >
                <FolderKanban className="h-4 w-4" />
                <span>{t('dashboard.continue_project')}</span>
              </Link>
            </Card>
          )}

          <Card variant="default" padding="lg" className="bg-gradient-to-br from-primary-900/10 via-transparent to-accent-900/10 border-primary-500/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-accent-500/10 rounded-xl">
                <Sparkles className="h-6 w-6 text-accent-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-text-primary">{t('dashboard.quick_actions')}</h3>
                <p className="text-sm text-text-secondary">{t('dashboard.quick_actions_desc')}</p>
              </div>
            </div>
            <div className="space-y-2">
              <Link
                to="/app/courses"
                className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary/50 border border-border-primary/50 hover:border-primary-500/30 hover:bg-primary-500/5 transition-colors group"
              >
                <div className="p-2 bg-primary-500/10 rounded-lg group-hover:scale-110 transition-transform">
                  <BookOpen className="h-5 w-5 text-primary-400" />
                </div>
                <span className="font-medium text-text-primary">{t('dashboard.browse_courses')}</span>
                <ArrowRight className="h-4 w-4 text-text-tertiary group-hover:text-primary-400 transition-colors ml-auto" />
              </Link>
              <Link
                to="/app/projects"
                className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary/50 border border-border-primary/50 hover:border-blue-500/30 hover:bg-blue-500/5 transition-colors group"
              >
                <div className="p-2 bg-blue-500/10 rounded-lg group-hover:scale-110 transition-transform">
                  <FolderKanban className="h-5 w-5 text-blue-400" />
                </div>
                <span className="font-medium text-text-primary">{t('navigation.projects')}</span>
                <ArrowRight className="h-4 w-4 text-text-tertiary group-hover:text-blue-400 transition-colors ml-auto" />
              </Link>
              <Link
                to="/app/profile"
                className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary/50 border border-border-primary/50 hover:border-yellow-500/30 hover:bg-yellow-500/5 transition-colors group"
              >
                <div className="p-2 bg-yellow-500/10 rounded-lg group-hover:scale-110 transition-transform">
                  <Trophy className="h-5 w-5 text-yellow-400" />
                </div>
                <span className="font-medium text-text-primary">{t('navigation.profile')}</span>
                <ArrowRight className="h-4 w-4 text-text-tertiary group-hover:text-yellow-400 transition-colors ml-auto" />
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <Card variant="default" padding="md" className={className}>
      <Skeleton variant="text" width="60%" height={16} />
      <Skeleton variant="text" width="40%" height={28} className="mt-2" />
    </Card>
  );
}