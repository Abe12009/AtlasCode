import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { coursesApi, dashboardApi } from '../api/services';
import { BookOpen, FolderKanban, Trophy, Flame, Zap, Code, ArrowRight, TrendingUp, Sparkles, Flag, MapPin, ChevronDown, ChevronUp } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Card, Badge, Progress, Button, cn, Skeleton, StatusBadge, XPBadge, StreakBadge, QuestRoadmap } from '../components/ui';
import type { QuestNodeData } from '../components/ui';
import { ShareAchievementButton } from '../components/ShareAchievementButton';
import { useTranslation } from '../hooks/useTranslation';

export function Dashboard() {
  const { t, currentLanguage } = useTranslation();
  const [storyExpanded, setStoryExpanded] = useState(false);
  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
  });

  /** Which course the quest map represents.
   *
   * 1. the course the student's current mission belongs to, else
   * 2. the first course still in progress, else
   * 3. `suggested_course_id` -- the first course in curriculum order, which
   *    is what a student who has started nothing should see, else
   * 4. nothing -- the map shows an empty state instead of inventing lessons.
   *
   * Rule 3 exists because rules 1 and 2 both read `course_progress`, which is
   * empty for a brand-new account -- so the first screen a new student ever
   * sees had a titled, empty quest board. The backend resolves the suggestion
   * (app/api/dashboard.py `suggested_course_id`) rather than the client
   * fetching the whole catalog to read one id off it.
   *
   * The dashboard endpoint puts no `course_id` on `current_mission` (it
   * resolves only the course *title*), so rule 1 matches that title against
   * `course_progress` -- the same join the welcome subtitle below already
   * does. A current mission whose course has no CourseProgress row yet (that
   * row is created lazily on first visit to the course page) therefore falls
   * through to rule 2, and for a new account on to rule 3.
   */
  const roadmapCourseId = (() => {
    const rows = dashboard?.course_progress ?? [];
    const missionCourseTitle = dashboard?.current_mission_course_title;
    if (missionCourseTitle) {
      const matched = rows.find((p) => p.title === missionCourseTitle);
      if (matched) return matched.course_id;
    }
    return (
      rows.find((p) => p.progress_percent < 100)?.course_id ??
      dashboard?.suggested_course_id ??
      null
    );
  })();

  /** Real lessons for that one course. Same query key as CourseDetail, so
   * opening the course page next is a cache hit rather than a second fetch.
   * GET /courses/{id} is what carries per-lesson `status` -- the dashboard
   * endpoint's course_progress has only counts. */
  const { data: roadmapCourse } = useQuery({
    queryKey: ['course', String(roadmapCourseId), currentLanguage],
    queryFn: () => coursesApi.getById(roadmapCourseId as number, currentLanguage),
    enabled: roadmapCourseId != null,
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
  const weekly = dashboard?.weekly;
  const currentMission = dashboard?.current_mission;
  const currentMissionCourseTitle = dashboard?.current_mission_course_title;
  const currentMissionModuleTitle = dashboard?.current_mission_module_title;
  const courseProgress = dashboard?.course_progress || [];
  const recentAchievements = dashboard?.recent_achievements || [];
  const currentProject = dashboard?.current_project;

  /** A weekly delta only shows for values that actually happened — see backend/app/services/stats.py. */
  const trendFor = (amount: number): string | null => (amount > 0 ? `+${amount}` : null);

  const coursesInProgress = courseProgress.filter(
    (p) => p.progress_percent > 0 && p.progress_percent < 100
  ).length;

  const stats = [
    {
      label: t('dashboard.courses_in_progress'),
      value: coursesInProgress,
      icon: BookOpen,
      color: 'text-blue-500 bg-blue-900/30 border-blue-500/30',
      trend: null,
      note: null as string | null,
    },
    {
      label: t('dashboard.projects_completed'),
      value: profile?.completed_projects || 0,
      icon: FolderKanban,
      color: 'text-green-500 bg-green-900/30 border-green-500/30',
      trend: trendFor(weekly?.projects_completed ?? 0),
      note: null as string | null,
    },
    {
      label: t('dashboard.day_streak'),
      value: `${profile?.streak || 0} ${t('dashboard.days')}`,
      icon: Flame,
      color: 'text-orange-500 bg-orange-900/30 border-orange-500/30',
      trend: null,
      note:
        (weekly?.active_days ?? 0) > 0
          ? t('dashboard.active_days_this_week', { count: weekly!.active_days })
          : null,
    },
    {
      label: t('dashboard.total_xp'),
      value: profile?.xp || 0,
      icon: Zap,
      color: 'text-yellow-500 bg-yellow-900/30 border-yellow-500/30',
      trend: trendFor(weekly?.xp ?? 0),
      note: null as string | null,
    },
  ];

  /** The course the welcome subtitle refers to: the one tied to the
   * student's actual current lesson if they have one (matched against
   * course_progress by title for a percent -- current_mission carries no
   * course_id, and a course_progress row for it may not exist yet, since
   * that row is only created lazily on first visit to the course page),
   * else whichever in-progress course is furthest along, else none
   * (brand-new account, no dynamic subtitle). */
  const subtitleCourse = (() => {
    if (currentMissionCourseTitle) {
      const matched = courseProgress.find((p) => p.title === currentMissionCourseTitle);
      return { title: currentMissionCourseTitle, percent: matched ? matched.progress_percent : null };
    }
    const furthest = [...courseProgress]
      .filter((p) => p.progress_percent > 0 && p.progress_percent < 100 && p.title)
      .sort((a, b) => b.progress_percent - a.progress_percent)[0];
    return furthest ? { title: furthest.title as string, percent: furthest.progress_percent } : null;
  })();

  /** One node per real lesson of `roadmapCourse`, carrying that lesson's own
   * id and the status the backend computed for it (completed / current /
   * available / locked -- see app/api/courses.py `_lesson_status`).
   *
   * What this replaces: nodes numbered 1..total_lessons from the course's
   * *counts*, with a status re-derived from `completed_lessons` (so the
   * initial `let status = 'locked'` was dead -- the final `else` overwrote it
   * with 'available'), and a `path` of `/app/lessons/${courseId}-${i}` that
   * matched no route. QuestRoadmap never read `path`, so no node was ever a
   * link; the strings are simply gone rather than repointed, and nodes stay
   * non-clickable.
   */
  const buildQuestNodes = (): QuestNodeData[] => {
    const lessons = (roadmapCourse?.modules ?? []).flatMap((m) => m.lessons ?? []);
    return lessons.map((lesson) => ({
      id: lesson.id,
      title: lesson.translations[0]?.title || `${t('dashboard.lesson')} ${lesson.order}`,
      type: lesson.is_project ? 'project' : 'lesson',
      // An absent status means an older backend, not a locked lesson: the
      // gate itself fails open, so the node does too.
      status: lesson.status ?? 'available',
      estimatedMinutes: lesson.estimated_minutes,
      xpReward: lesson.xp_reward,
      difficulty: lesson.difficulty,
    }));
  };

  const questNodes = buildQuestNodes();

  return (
      <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gradient-brand">
            {t('dashboard.welcome_back', { username: user?.username || '' })}
          </h1>
          <p className="text-text-secondary mt-1">
            {subtitleCourse?.percent != null
              ? t('dashboard.welcome_subtitle_progress', {
                  percent: Math.round(subtitleCourse.percent),
                  course: subtitleCourse.title,
                })
              : subtitleCourse
              ? t('dashboard.welcome_subtitle_course', { course: subtitleCourse.title })
              : t('dashboard.continue_journey')}
          </p>
        </div>
        <Link
          to="/app/courses"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 btn-primary-gradient text-white font-semibold rounded-xl transition-all shadow-[var(--depth-raise-top),var(--depth-raise-bottom),var(--shadow-card),var(--btn-primary-glow)]"
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
              {stat.trend ? (
                <>
                  <TrendingUp className="h-4 w-4 text-success-500" aria-hidden="true" />
                  <span className="text-sm font-medium text-success-600 dark:text-success-400">
                    {stat.trend} {t('dashboard.this_week')}
                  </span>
                </>
              ) : stat.note ? (
                <span className="text-sm font-medium text-text-tertiary">{stat.note}</span>
              ) : (
                <span className="text-sm text-text-tertiary">{t('dashboard.no_activity_this_week')}</span>
              )}
            </div>
          </Card>
        ))}
      </div>

      <div className="glass-surface rounded-2xl p-6 lg:p-8">
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
        {questNodes.length > 0 ? (
          <QuestRoadmap nodes={questNodes} variant="horizontal" />
        ) : roadmapCourseId == null ? (
          // Nothing to map (no course seeded at all, since `suggested_course_id`
          // covers every other case), so the empty state is at least a way out:
          // the catalog, rather than a dead sentence.
          //
          // Gated on `roadmapCourseId` rather than on `questNodes` alone: with
          // a course id in hand the nodes are merely in flight, and claiming
          // "no courses started yet" for those few hundred milliseconds is a
          // statement that is about to be false. Blank, then the map.
          <p className="text-sm py-6 text-center" data-testid="quest-board-empty">
            <Link to="/app/courses" className="text-primary-400 hover:text-primary-300">
              {t('dashboard.no_courses_started')}
            </Link>
          </p>
        ) : null}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {currentMission && (() => {
            const matchedProgress = currentMissionCourseTitle
              ? courseProgress.find((p) => p.title === currentMissionCourseTitle)
              : undefined;
            const courseTitle = currentMissionCourseTitle || currentMission.translations[0]?.title;
            const percent = matchedProgress?.progress_percent ?? 0;
            const story = currentMission.translations[0]?.story;
            const skills = currentMission.translations[0]?.skills?.split(', ').filter(Boolean) ?? [];
            const hasExtra = Boolean(story) || skills.length > 0;

            return (
              <Card variant="interactive" padding="lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-3 bg-primary-500/10 rounded-xl flex-shrink-0">
                      <Code className="h-6 w-6 text-primary-400" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h2 className="text-lg font-semibold text-text-primary truncate">
                          {courseTitle}
                        </h2>
                        <StatusBadge status="in_progress" size="sm" />
                      </div>
                      {currentMissionModuleTitle && (
                        <p className="text-sm text-text-secondary truncate">
                          {currentMissionModuleTitle}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                <Progress
                  value={percent}
                  size="md"
                  variant="primary"
                  showLabel
                  className="mb-4"
                />

                <Link
                  to={`/app/lessons/${currentMission.id}`}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 btn-primary-gradient text-white font-semibold rounded-xl transition-all shadow-[var(--depth-raise-top),var(--depth-raise-bottom),var(--shadow-card),var(--btn-primary-glow)]"
                >
                  <span>{t('dashboard.continue_lesson')}</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>

                {hasExtra && (
                  <div className="mt-4 pt-4 border-t border-border-primary/50">
                    <button
                      type="button"
                      onClick={() => setStoryExpanded((v) => !v)}
                      className="flex items-center gap-1.5 text-sm font-medium text-primary-400 hover:text-primary-300"
                      aria-expanded={storyExpanded}
                      data-testid="dashboard-story-toggle"
                    >
                      {storyExpanded ? (
                        <>
                          <ChevronUp className="h-4 w-4" />
                          {t('dashboard.hide_story')}
                        </>
                      ) : (
                        <>
                          <ChevronDown className="h-4 w-4" />
                          {t('dashboard.show_story')}
                        </>
                      )}
                    </button>
                    {storyExpanded && (
                      <div className="mt-3 animate-slide-down">
                        {story && <p className="text-text-secondary mb-3">{story}</p>}
                        {skills.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {skills.map((skill) => (
                              <Badge key={skill} variant="outline" size="sm" className="border-primary-500/30 text-primary-400">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </Card>
            );
          })()}

          <Card variant="glass" padding="lg">
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
                        {progress.title || `${t('dashboard.course')} ${progress.course_id}`}
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
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 btn-primary-gradient text-white font-semibold rounded-xl transition-all shadow-[var(--depth-raise-top),var(--depth-raise-bottom),var(--shadow-card),var(--btn-primary-glow)]"
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
          <Card variant="glass" padding="lg">
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
                    {/* The dashboard only ever shows the signed-in user's own
                        achievements, so sharing is safe here. */}
                    <ShareAchievementButton
                      achievement={{
                        icon: ua.achievement.icon || '🏆',
                        title: ua.achievement.translations[0]?.title ?? 'Achievement',
                        username: user?.username ?? '',
                      }}
                    />
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
            <Card variant="interactive" padding="lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary-500/10 rounded-xl">
                    <FolderKanban className="h-6 w-6 text-primary-400" />
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
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 btn-primary-gradient text-white font-semibold rounded-xl transition-all shadow-[var(--depth-raise-top),var(--depth-raise-bottom),var(--shadow-card),var(--btn-primary-glow)] w-full justify-center"
              >
                <FolderKanban className="h-4 w-4" />
                <span>{t('dashboard.continue_project')}</span>
              </Link>
            </Card>
          )}

          <Card variant="default" padding="lg">
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
                <ArrowRight className="h-4 w-4 text-text-tertiary group-hover:text-primary-400 transition-colors ms-auto" />
              </Link>
              <Link
                to="/app/projects"
                className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary/50 border border-border-primary/50 hover:border-blue-500/30 hover:bg-blue-500/5 transition-colors group"
              >
                <div className="p-2 bg-blue-500/10 rounded-lg group-hover:scale-110 transition-transform">
                  <FolderKanban className="h-5 w-5 text-blue-400" />
                </div>
                <span className="font-medium text-text-primary">{t('navigation.projects')}</span>
                <ArrowRight className="h-4 w-4 text-text-tertiary group-hover:text-blue-400 transition-colors ms-auto" />
              </Link>
              <Link
                to="/app/profile"
                className="flex items-center gap-3 p-3 rounded-xl bg-bg-secondary/50 border border-border-primary/50 hover:border-yellow-500/30 hover:bg-yellow-500/5 transition-colors group"
              >
                <div className="p-2 bg-yellow-500/10 rounded-lg group-hover:scale-110 transition-transform">
                  <Trophy className="h-5 w-5 text-yellow-400" />
                </div>
                <span className="font-medium text-text-primary">{t('navigation.profile')}</span>
                <ArrowRight className="h-4 w-4 text-text-tertiary group-hover:text-yellow-400 transition-colors ms-auto" />
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