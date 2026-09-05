import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { coursesApi } from '../api/services';
import { BookOpen, Clock, Target, CheckCircle, ChevronDown, ChevronLeft, Play, Code, ArrowRight, Flag, Trophy, Layers, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Module } from '../types';
import { useState } from 'react';
import { Card, Badge, Progress, Button, cn, Skeleton, StatusBadge, XPBadge } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';

export function CourseDetail() {
  const { t, currentLanguage } = useTranslation();
  const { courseId } = useParams<{ courseId: string }>();
  const [expandedModules, setExpandedModules] = useState<Set<number>>(new Set());

  const { data: course, isLoading, error } = useQuery({
    queryKey: ['course', courseId, currentLanguage],
    queryFn: () => coursesApi.getById(Number(courseId), currentLanguage),
    enabled: !!courseId,
  });

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div className="flex items-center gap-4">
          <Skeleton variant="text" width="30%" height={32} />
          <Skeleton variant="text" width="40%" height={20} />
        </div>
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton variant="rectangular" width="100%" height={300} />
            <Skeleton variant="rectangular" width="100%" height={400} />
          </div>
          <div className="space-y-6">
            <Skeleton variant="rectangular" width="100%" height={400} />
          </div>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="text-center py-12">
        <p className="text-error-600 dark:text-error-400">{t('errors.not_found')}</p>
      </div>
    );
  }

  const toggleModule = (moduleId: number) => {
    setExpandedModules((prev) => {
      const next = new Set(prev);
      if (next.has(moduleId)) {
        next.delete(moduleId);
      } else {
        next.add(moduleId);
      }
      return next;
    });
  };

  const totalLessons = course.modules?.reduce((acc: number, m: Module) => acc + (m.lessons?.length || 0), 0) || 0;

  return (
    <div className="space-y-8 animate-fade-in">
      <Link to="/app/courses" className="inline-flex items-center gap-2 text-text-tertiary hover:text-primary-400 dark:hover:text-primary-300 text-sm font-medium transition-colors">
        <ChevronLeft className="h-4 w-4" />
        <span>{t('common.back_to_courses')}</span>
      </Link>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Card variant="default" padding="lg" className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5" aria-hidden="true" />
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-primary-500/10 rounded-xl">
                  <BookOpen className="h-8 w-8 text-primary-400" />
                </div>
                <div>
                  <div className="flex items-center flex-wrap gap-2">
                    <Badge variant="primary" size="sm">
                      {t('courses.course_number', { order: course.order })}
                    </Badge>
                    <span className="px-2 py-1 bg-accent-500/10 text-accent-400 rounded-full text-xs font-mono">
                      {t('courses.mission')}
                    </span>
                  </div>
                  <h1 className="text-2xl font-bold text-text-primary mt-2">
                    {course.translations[0]?.title}
                  </h1>
                </div>
              </div>

              <p className="text-text-secondary mb-6">
                {course.translations[0]?.description}
              </p>

              <div className="flex flex-wrap gap-2 mb-6">
                {course.translations[0]?.skills?.split(', ').map((skill) => (
                  <Badge key={skill} variant="outline" size="sm" className="border-primary-500/30 text-primary-400">
                    {skill}
                  </Badge>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-4 pt-6 border-t border-border-primary/50">
                <div className="text-center p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                  <div className="flex items-center justify-center gap-1 text-text-tertiary mb-1">
                    <Clock className="h-5 w-5" />
                    <span className="text-sm">{t('courses.estimated_per_lesson')}</span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary">{totalLessons}</div>
                  <div className="text-sm text-text-tertiary">{t('courses.lessons')}</div>
                </div>
                <div className="text-center p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50 border-x border-border-primary/50">
                  <div className="flex items-center justify-center gap-1 text-text-tertiary mb-1">
                    <Target className="h-5 w-5" />
                    <span className="text-sm">{t('courses.difficulty')}</span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary capitalize">{course.difficulty}</div>
                  <div className="text-sm text-text-tertiary">{t('courses.level')}</div>
                </div>
                <div className="text-center p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                  <div className="flex items-center justify-center gap-1 text-text-tertiary mb-1">
                    <Code className="h-5 w-5" />
                    <span className="text-sm">{t('courses.est_hours')}</span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary">{Math.round(totalLessons * 0.5)}</div>
                  <div className="text-sm text-text-tertiary">{t('courses.hours')}</div>
                </div>
              </div>
            </div>
          </Card>

          <Card variant="default" padding="lg" className="relative overflow-hidden">
            <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
            <div className="relative z-10">
              <div className="p-5 border-b border-border-primary/50 mb-5">
                <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                  <Layers className="h-5 w-5 text-accent-400" />
                  <span>{t('courses.course_content')}</span>
                  <Sparkles className="h-4 w-4 text-accent-400" />
                </h2>
              </div>
              <div className="divide-y divide-border-primary/50">
                {course.modules?.map((module) => {
                  const isExpanded = expandedModules.has(module.id);
                  const moduleLessons = module.lessons?.length || 0;

                  return (
                    <div key={module.id}>
                      <button
                        onClick={() => toggleModule(module.id)}
                        className="w-full px-5 py-4 flex items-center justify-between hover:bg-primary-500/5 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-primary-500/10 rounded-lg">
                            <BookOpen className="h-5 w-5 text-primary-400" />
                          </div>
                          <div>
                            <h3 className="font-medium text-text-primary">
                              {module.translations[0]?.title}
                            </h3>
                            <p className="text-sm text-text-tertiary">
                              {t('courses.lessons_count', { count: moduleLessons })}
                            </p>
                          </div>
                        </div>
                        <ChevronDown
                          className={cn('h-5 w-5 text-text-tertiary transition-transform duration-200', isExpanded && 'rotate-180')}
                        />
                      </button>

                      {isExpanded && (
                        <div className="px-5 pb-5 pl-14 space-y-2 animate-slide-down">
                          {module.lessons?.map((lesson, index) => {
                            const lessonStatus = lesson.status || 'available';
                            const isCompleted = lessonStatus === 'completed';
                            const isCurrent = lessonStatus === 'current';
                            return (
                            <Link
                              key={lesson.id}
                              to={`/app/lessons/${lesson.id}`}
                              className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary-500/5 transition-colors group"
                            >
                              <div className={cn(
                                'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all',
                                'group-hover:scale-110',
                                isCompleted
                                  ? 'bg-success-500/20 text-success-400 border border-success-500/30'
                                  : isCurrent
                                  ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30 animate-pulse'
                                  : 'bg-bg-tertiary text-text-tertiary border border-border-primary/50'
                              )}>
                                {isCompleted ? <CheckCircle className="h-5 w-5" /> : index + 1}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="font-medium text-text-primary truncate group-hover:text-primary-400 transition-colors">
                                  {lesson.translations[0]?.title}
                                </p>
                                <div className="flex items-center gap-3 text-xs text-text-tertiary mt-1">
                                  <span className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    <span>{lesson.estimated_minutes} {t('common.min')}</span>
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Target className="h-3 w-3" />
                                    <span>{t(`courses.difficulty_level.${lesson.difficulty}`)}</span>
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Code className="h-3 w-3" />
                                    <XPBadge xp={lesson.xp_reward} size="sm" showIcon={false} />
                                  </span>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <StatusBadge status={lessonStatus} size="sm" />
                                <Play className="h-5 w-5 text-text-tertiary group-hover:text-primary-400 transition-colors opacity-0 group-hover:opacity-100" />
                              </div>
                            </Link>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card variant="default" padding="lg" className="sticky top-24 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5" aria-hidden="true" />
            <div className="relative z-10">
              <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                <Flag className="h-5 w-5 text-accent-400" />
                <span>{t('courses.what_youll_learn')}</span>
              </h2>
              <ul className="space-y-3">
                {course.translations[0]?.skills?.split(', ').map((skill) => (
                  <li key={skill} className="flex items-center gap-3 p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <div className="p-2 bg-success-500/10 rounded-full">
                      <CheckCircle className="h-5 w-5 text-success-400" />
                    </div>
                    <span className="text-text-secondary">{skill}</span>
                  </li>
                ))}
              </ul>

              <div className="mt-6 pt-6 border-t border-border-primary/50">
                <h3 className="font-medium text-text-primary mb-3 flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-yellow-400" />
                  <span>{t('courses.course_details')}</span>
                </h3>
                <dl className="space-y-3 text-sm">
                  <div className="flex justify-between p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <dt className="text-text-tertiary">{t('courses.total_lessons')}</dt>
                    <dd className="font-medium text-text-primary">{totalLessons}</dd>
                  </div>
                  <div className="flex justify-between p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <dt className="text-text-tertiary">{t('courses.estimated_time')}</dt>
                    <dd className="font-medium text-text-primary">{Math.round(totalLessons * 0.5)} {t('courses.hours')}</dd>
                  </div>
                  <div className="flex justify-between p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <dt className="text-text-tertiary">{t('courses.difficulty')}</dt>
                    <dd className="font-medium text-text-primary capitalize">{t(`courses.difficulty_level.${course.difficulty?.toLowerCase() || 'beginner'}`)}</dd>
                  </div>
                  <div className="flex justify-between p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <dt className="text-text-tertiary">{t('courses.language')}</dt>
                    <dd className="font-medium text-text-primary capitalize">{currentLanguage}</dd>
                  </div>
                </dl>
              </div>

              <div className="mt-6">
                <Link
                  to={`/app/lessons/${course.modules?.[0]?.lessons?.[0]?.id}`}
                  className="w-full"
                >
                  <Button
                    className="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
                    size="lg"
                    leftIcon={<Play className="h-5 w-5" />}
                  >
                    {t('courses.start_learning')}
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function SkeletonCourseDetail() {
  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center gap-4">
        <Skeleton variant="text" width="30%" height={32} />
        <Skeleton variant="text" width="40%" height={20} />
      </div>
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Skeleton variant="rectangular" width="100%" height={300} />
          <Skeleton variant="rectangular" width="100%" height={400} />
        </div>
        <div className="space-y-6">
          <Skeleton variant="rectangular" width="100%" height={400} />
        </div>
      </div>
    </div>
  );
}