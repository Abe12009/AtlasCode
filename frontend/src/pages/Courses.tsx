import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { coursesApi } from '../api/services';
import { BookOpen, Clock, Target, ArrowRight, ChevronRight, CheckCircle, Lock, Flag, Star, Layers } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import { Card, Badge, Button, Skeleton, cn, StatusBadge, XPBadge, ProgressBar } from '../components/ui';

export function Courses() {
  const { t, currentLanguage } = useTranslation();

  const { data: courses, isLoading, error } = useQuery({
    queryKey: ['courses', currentLanguage],
    queryFn: () => coursesApi.getAll(currentLanguage),
  });

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div>
          <Skeleton variant="text" width="30%" height={32} data-testid="loading-spinner" />
          <Skeleton variant="text" width="50%" height={20} className="mt-2" />
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <SkeletonCourseCard key={i} />
          ))}
        </div>
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

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-text-primary bg-gradient-to-r from-text-primary via-primary-400 to-accent-400 bg-clip-text text-transparent">
          {t('courses.title')}
        </h1>
        <p className="text-text-secondary mt-1">
          {t('courses.browse')}
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses?.map((course) => {
          const totalLessons = course.modules?.reduce((acc: number, m: any) => acc + (m.lessons?.length || 0), 0) || 0;
          const completedLessons = 0;
          const progressPercent = totalLessons > 0 ? (completedLessons / totalLessons) * 100 : 0;
          const isStarted = completedLessons > 0;
          const isCompleted = completedLessons === totalLessons && totalLessons > 0;

          return (
            <Link
              key={course.id}
              to={`/app/courses/${course.id}`}
              className="block"
            >
              <Card
                variant={isCompleted ? 'default' : 'interactive'}
                padding="lg"
                className={cn(
                  'relative overflow-hidden group',
                  isCompleted && 'border-success-500/30 bg-success-500/5',
                  !isStarted && 'border-border-primary/50'
                )}
              >
                <div className="relative">
                  <div className="flex items-start justify-between mb-4">
                    <div className={cn(
                      'p-3 rounded-xl transition-all duration-300 group-hover:scale-110',
                      isCompleted ? 'bg-success-500/10 text-success-400 border border-success-500/20' :
                      isStarted ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20' :
                      'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    )}>
                      <BookOpen className="h-6 w-6" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" size="sm" className="border-primary-500/30 text-primary-400">
                        {t('courses.course_number', { order: course.order })}
                      </Badge>
                      {isCompleted && (
                        <StatusBadge status="completed" size="sm" showIcon />
                      )}
                    </div>
                  </div>

                  <h2 className="text-xl font-semibold text-text-primary mb-2 line-clamp-1 group-hover:text-primary-400 transition-colors">
                    {course.translations[0]?.title}
                  </h2>

                  <p className="text-text-secondary text-sm mb-4 line-clamp-2">
                    {course.translations[0]?.description}
                  </p>

                  {course.translations[0]?.skills && (
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {course.translations[0]?.skills?.split(', ').slice(0, 4).map((skill) => (
                        <Badge key={skill} variant="neutral" size="sm" className="border-border-primary/50 bg-bg-tertiary/50 text-text-secondary">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <div className="pt-4 border-t border-border-primary/50">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3 text-sm text-text-tertiary">
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          <span>{t('courses.estimated_per_lesson')}</span>
                        </span>
                        <span className="flex items-center gap-1">
                          <Target className="h-4 w-4" />
                          <Badge variant="primary" size="sm">
                            {t(`courses.difficulty_level.${course.difficulty?.toLowerCase() || 'beginner'}`)}
                          </Badge>
                        </span>
                      </div>
                      <ChevronRight className="h-5 w-5 text-text-tertiary transition-transform group-hover:translate-x-1 group-hover:text-primary-400" />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-text-tertiary">
                          {isCompleted ? t('courses.completed') : isStarted ? `${completedLessons}/${totalLessons} ${t('courses.lessons')}` : `${totalLessons} ${t('courses.lessons')}`}
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

                  <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" aria-hidden="true" />
                </div>
              </Card>
            </Link>
          );
        })}

        {(!courses || courses.length === 0) && (
          <div className="col-span-full text-center py-16 animate-fade-in">
            <div className="p-4 bg-primary-500/10 rounded-2xl w-fit mx-auto mb-4 border border-primary-500/20">
              <BookOpen className="h-12 w-12 text-primary-400" />
            </div>
            <h2 className="text-xl font-semibold text-text-primary mb-2">{t('courses.no_courses')}</h2>
            <p className="text-text-secondary">{t('courses.check_back_later')}</p>
          </div>
        )}
      </div>
    </div>
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