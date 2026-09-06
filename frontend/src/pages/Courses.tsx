import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { coursesApi, sectionsApi, dashboardApi } from '../api/services';
import { BookOpen, Clock, Target, ChevronRight, Lock } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import { Card, Badge, Skeleton, cn, StatusBadge, ProgressBar } from '../components/ui';
import type { Course, Section } from '../types';

interface SectionGroup {
  id: number | null;
  slug: string | null;
  icon: string;
  title: string;
  description: string;
  order: number;
  courses: Course[];
}

export function Courses() {
  const { t, currentLanguage } = useTranslation();

  const { data: courses, isLoading: coursesLoading, error } = useQuery({
    queryKey: ['courses', currentLanguage],
    queryFn: () => coursesApi.getAll(currentLanguage),
  });

  const { data: sections, isLoading: sectionsLoading } = useQuery({
    queryKey: ['sections', currentLanguage],
    queryFn: () => sectionsApi.getAll(currentLanguage),
  });

  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
  });

  const isLoading = coursesLoading || sectionsLoading;

  if (isLoading) {
    return (
      <div className="space-y-10 animate-fade-in">
        <div>
          <Skeleton variant="text" width="30%" height={32} data-testid="loading-spinner" />
          <Skeleton variant="text" width="50%" height={20} className="mt-2" />
        </div>
        {[1, 2].map((section) => (
          <div key={section} className="space-y-4">
            <Skeleton variant="text" width="20%" height={24} />
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <SkeletonCourseCard key={i} />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-error-600 dark:text-error-400">{t('courses.failed_to_load')}</p>
      </div>
    );
  }

  const progressByCourseId = new Map(
    (dashboard?.course_progress ?? []).map((p) => [p.course_id, p]),
  );

  // Every course is either in a real Section (grouped below) or unsectioned
  // (foundational/theory courses that underpin every section — see
  // backend/app/seed/sections.py). The unsectioned group renders first since
  // those are meant to come before everything else in the roadmap.
  const groups: SectionGroup[] = [
    {
      id: null,
      slug: null,
      icon: '🧭',
      title: t('courses.unsectioned'),
      description: t('courses.unsectioned_description'),
      order: 0,
      courses: [],
    },
    ...(sections ?? []).map((section: Section) => ({
      id: section.id,
      slug: section.slug,
      icon: section.icon || '📘',
      title: section.translations[0]?.title ?? section.slug,
      description: section.translations[0]?.description ?? '',
      order: section.order,
      courses: [] as Course[],
    })),
  ];
  const groupById = new Map(groups.map((g) => [g.id, g]));

  for (const course of courses ?? []) {
    const group = groupById.get(course.section_id ?? null) ?? groups[0];
    group.courses.push(course);
  }
  for (const group of groups) {
    group.courses.sort((a, b) => a.order - b.order);
  }
  const visibleGroups = groups.filter((g) => g.courses.length > 0);

  return (
    <div className="space-y-10 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gradient-brand">{t('courses.title')}</h1>
        <p className="text-text-secondary mt-1">{t('courses.browse')}</p>
      </div>

      {visibleGroups.map((group) => (
        <section key={group.id ?? 'unsectioned'} className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-500/10 border border-primary-500/20 text-2xl flex-shrink-0">
              <span aria-hidden="true">{group.icon}</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">{group.title}</h2>
              {group.description && (
                <p className="text-sm text-text-tertiary">{group.description}</p>
              )}
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {group.courses.map((course) => (
              <CourseCard
                key={course.id}
                course={course}
                progress={progressByCourseId.get(course.id)}
                prerequisite={
                  course.prerequisite_course_id
                    ? courses?.find((c) => c.id === course.prerequisite_course_id)
                    : undefined
                }
                prerequisiteProgress={
                  course.prerequisite_course_id
                    ? progressByCourseId.get(course.prerequisite_course_id)
                    : undefined
                }
              />
            ))}
          </div>
        </section>
      ))}

      {visibleGroups.length === 0 && (
        <div className="text-center py-16 animate-fade-in">
          <div className="p-4 bg-primary-500/10 rounded-2xl w-fit mx-auto mb-4 border border-primary-500/20">
            <BookOpen className="h-12 w-12 text-primary-400" />
          </div>
          <h2 className="text-xl font-semibold text-text-primary mb-2">{t('courses.no_courses')}</h2>
          <p className="text-text-secondary">{t('courses.check_back_later')}</p>
        </div>
      )}
    </div>
  );
}

function CourseCard({
  course,
  progress,
  prerequisite,
  prerequisiteProgress,
}: {
  course: Course;
  progress?: { completed_lessons: number; total_lessons: number; progress_percent: number };
  prerequisite?: Course;
  prerequisiteProgress?: { progress_percent: number };
}) {
  const { t } = useTranslation();

  const totalLessons =
    progress?.total_lessons ??
    course.modules?.reduce((acc, m) => acc + (m.lessons?.length || 0), 0) ??
    0;
  const completedLessons = progress?.completed_lessons ?? 0;
  const progressPercent = progress?.progress_percent ?? 0;
  const isStarted = completedLessons > 0;
  const isCompleted = totalLessons > 0 && completedLessons === totalLessons;

  // Advisory lock: a prerequisite exists and hasn't been finished yet. The
  // course is still reachable (backend never hard-blocks it — see
  // app/curriculum.py), this is purely a UI nudge toward the right order.
  const isLocked = Boolean(prerequisite) && (prerequisiteProgress?.progress_percent ?? 0) < 100;

  const card = (
    <Card
      variant={isLocked ? 'default' : isCompleted ? 'default' : 'interactive'}
      padding="lg"
      className={cn(
        'relative overflow-hidden group h-full',
        isCompleted && 'border-success-500/30 bg-success-500/5',
        isLocked && 'opacity-70',
        !isStarted && !isLocked && 'border-border-primary/50',
      )}
    >
      <div className="relative">
        <div className="flex items-start justify-between mb-4">
          <div
            className={cn(
              'p-3 rounded-xl transition-all duration-300 text-xl flex items-center justify-center',
              !isLocked && 'group-hover:scale-110',
              isCompleted
                ? 'bg-success-500/10 text-success-400 border border-success-500/20'
                : isStarted
                ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                : 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
            )}
          >
            {course.icon ? <span aria-hidden="true">{course.icon}</span> : <BookOpen className="h-6 w-6" />}
          </div>
          <div className="flex items-center gap-2">
            {isLocked ? (
              <Badge variant="neutral" size="sm" className="gap-1">
                <Lock className="h-3 w-3" aria-hidden="true" />
                {t('courses.locked')}
              </Badge>
            ) : isCompleted ? (
              <StatusBadge status="completed" size="sm" showIcon />
            ) : null}
          </div>
        </div>

        <h2 className="text-xl font-semibold text-text-primary mb-2 line-clamp-1 group-hover:text-primary-400 transition-colors">
          {course.translations[0]?.title}
        </h2>

        <p className="text-text-secondary text-sm mb-4 line-clamp-2">
          {course.translations[0]?.description}
        </p>

        {isLocked && prerequisite && (
          <p className="text-xs text-warning-500 mb-4 flex items-center gap-1">
            <Lock className="h-3 w-3 flex-shrink-0" aria-hidden="true" />
            {t('courses.prerequisite_required', { course: prerequisite.translations[0]?.title })}
          </p>
        )}

        {course.translations[0]?.skills && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {course.translations[0]?.skills
              ?.split(', ')
              .slice(0, 4)
              .map((skill) => (
                <Badge
                  key={skill}
                  variant="neutral"
                  size="sm"
                  className="border-border-primary/50 bg-bg-tertiary/50 text-text-secondary"
                >
                  {skill}
                </Badge>
              ))}
          </div>
        )}

        <div className="pt-4 border-t border-border-primary/50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3 text-sm text-text-tertiary">
              {!!course.estimated_hours && (
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" aria-hidden="true" />
                  <span>{t('courses.est_hours_short', { hours: course.estimated_hours })}</span>
                </span>
              )}
              <span className="flex items-center gap-1">
                <Target className="h-4 w-4" aria-hidden="true" />
                <Badge variant="primary" size="sm">
                  {t(`courses.difficulty_level.${course.difficulty?.toLowerCase() || 'beginner'}`)}
                </Badge>
              </span>
            </div>
            {!isLocked && (
              <ChevronRight
                className="h-5 w-5 text-text-tertiary transition-transform group-hover:translate-x-1 group-hover:text-primary-400"
                aria-hidden="true"
              />
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-tertiary">
                {isCompleted
                  ? t('courses.completed')
                  : isStarted
                  ? `${completedLessons}/${totalLessons} ${t('courses.lessons')}`
                  : `${totalLessons} ${t('courses.lessons')}`}
              </span>
              <span className="font-medium text-primary-400">{Math.round(progressPercent)}%</span>
            </div>
            <ProgressBar
              value={progressPercent}
              size="sm"
              variant={isCompleted ? 'success' : isStarted ? 'primary' : 'accent'}
              className="h-1.5"
            />
          </div>
        </div>

        {!isLocked && (
          <div
            className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
            aria-hidden="true"
          />
        )}
      </div>
    </Card>
  );

  if (isLocked) {
    // Still reachable — this is advisory, not a hard lock (see app/curriculum.py) —
    // but the card itself isn't the primary path in, so it renders as a plain div.
    return <div className="block h-full">{card}</div>;
  }

  return (
    <Link to={`/app/courses/${course.id}`} className="block h-full">
      {card}
    </Link>
  );
}

function SkeletonCourseCard() {
  return (
    <Card variant="default" padding="lg">
      <div className="flex items-start justify-between mb-3">
        <div className="p-3 bg-bg-tertiary rounded-xl animate-pulse" />
        <div className="h-5 w-24 bg-bg-tertiary rounded animate-pulse" />
      </div>
      <div className="h-6 w-3/4 bg-bg-tertiary rounded animate-pulse mb-2" />
      <div className="h-4 w-full bg-bg-tertiary rounded animate-pulse mb-2" />
      <div className="h-4 w-1/2 bg-bg-tertiary rounded animate-pulse mb-4" />
      <div className="flex gap-2">
        <div className="h-5 w-20 bg-bg-tertiary rounded animate-pulse" />
        <div className="h-5 w-20 bg-bg-tertiary rounded animate-pulse" />
      </div>
      <div className="pt-4 border-t border-border-primary mt-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-4 w-24 bg-bg-tertiary rounded animate-pulse" />
            <div className="h-5 w-24 bg-bg-tertiary rounded animate-pulse" />
          </div>
        </div>
      </div>
    </Card>
  );
}
