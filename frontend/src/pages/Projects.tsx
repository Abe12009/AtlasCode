import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { projectsApi } from '../api/services';
import { FolderKanban, Clock, Target, ArrowRight, Lock, CheckCircle, ChevronRight, Flag, Code, Zap, Shield, AlertCircle } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import type { ProjectProgress } from '../types';
import { Card, Badge, Button, Progress, Skeleton, cn, StatusBadge, XPBadge } from '../components/ui';

export function Projects() {
  const { t, currentLanguage } = useTranslation();

  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects', currentLanguage],
    queryFn: () => projectsApi.getAll(currentLanguage),
  });

  const { data: allProgress } = useQuery<ProjectProgress[]>({
    queryKey: ['allProjectProgress'],
    queryFn: async () => {
      if (!projects) return [];
      const progressPromises = projects.map((p) => projectsApi.getProgress(p.id));
      return Promise.all(progressPromises);
    },
    enabled: !!projects && projects.length > 0,
  });

  const progressMap = new Map<number, ProjectProgress>(
    (allProgress ?? []).map((p) => [p.project_id, p])
  );

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div>
          <Skeleton variant="text" width="30%" height={32} data-testid="loading-spinner" />
          <Skeleton variant="text" width="50%" height={20} className="mt-2" />
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <SkeletonProjectCard key={i} />
          ))}
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

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gradient-brand">
          {t('projects_page.title')}
        </h1>
        <p className="text-text-secondary mt-1">
          {t('projects_page.browse')}
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects?.map((project) => {
          const progress = progressMap.get(project.id);
          const isLocked = progress?.status === 'locked';
          const isCompleted = progress?.status === 'completed';
          const isInProgress = progress?.status === 'in_progress';
          const completedTasks = progress?.current_task || 0;
          const totalTasks = project.tasks?.length || 0;
          const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

          const status: 'completed' | 'current' | 'available' | 'locked' = isCompleted ? 'completed' : isInProgress ? 'current' : isLocked ? 'locked' : 'available';

          return (
            <Link
              key={project.id}
              to={`/app/projects/${project.id}`}
              className="block"
            >
              <Card
                variant={isLocked ? 'outlined' : isCompleted ? 'default' : 'interactive'}
                padding="lg"
                className={cn(
                  'relative overflow-hidden group',
                  isLocked && 'opacity-60 border-border-primary/50',
                  isCompleted && 'border-success-500/30 bg-success-500/5',
                  isInProgress && 'border-primary-500/30 bg-primary-500/5'
                )}
              >
                <div className="relative">
                  {isLocked && (
                    <div className="absolute inset-0 bg-bg-secondary flex items-center justify-center rounded-xl z-20">
                      <div className="text-center p-4">
                        <Lock className="h-12 w-12 text-text-tertiary mx-auto mb-2" />
                        <p className="text-text-secondary text-sm">{t('projects_page.project_locked')}</p>
                      </div>
                    </div>
                  )}

                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div className={cn(
                        'p-3 rounded-xl transition-all duration-300 group-hover:scale-110',
                        isCompleted ? 'bg-success-500/10 text-success-400 border border-success-500/20' :
                        isInProgress ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20' :
                        isLocked ? 'bg-bg-tertiary text-text-tertiary border border-border-primary/50' :
                        'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                      )}>
                        <FolderKanban className="h-6 w-6" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" size="sm" className="border-primary-500/30 text-primary-400">
                          {t('projects_page.project_number', { order: project.order })}
                        </Badge>
                        <StatusBadge status={status} size="sm" />
                      </div>
                    </div>

                    <h2 className="text-xl font-semibold text-text-primary mb-2 group-hover:text-primary-400 transition-colors">
                      {project.translations[0]?.title}
                    </h2>

                    <p className="text-text-secondary text-sm mb-4 line-clamp-2">
                      {project.translations[0]?.story}
                    </p>

                    {project.prerequisite_lesson_id && (
                      <div className="mb-4 flex items-center gap-2 text-xs text-text-tertiary">
                        <Lock className="h-3 w-3" />
                        <span>{t('projects_page.prerequisite', { lesson: project.prerequisite_lesson_id })}</span>
                      </div>
                    )}

                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {project.translations[0]?.skills?.split(', ').slice(0, 4).map((skill) => (
                        <Badge key={skill} variant="neutral" size="sm" className="border-border-primary/50 bg-bg-tertiary/50 text-text-secondary">
                          {skill}
                        </Badge>
                      ))}
                    </div>

                    <div className="pt-4 border-t border-border-primary/50">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3 text-sm text-text-tertiary">
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            <span>{t('projects_page.tasks', { count: totalTasks })}</span>
                          </span>
                          <span className="flex items-center gap-1">
                            <Target className="h-4 w-4" />
                            <Badge variant="primary" size="sm">
                              {project.difficulty}
                            </Badge>
                          </span>
                        </div>
                        {isCompleted && (
                          <span className="flex items-center gap-1 text-success-400 font-medium">
                            <CheckCircle className="h-4 w-4" />
                            <span className="text-sm">{t('projects_page.completed')}</span>
                          </span>
                        )}
                      </div>

                      {!isLocked && totalTasks > 0 && (
                        <div className="space-y-2 mb-3">
                          <Progress
                            value={progressPercent}
                            size="sm"
                            variant={isCompleted ? 'success' : isInProgress ? 'primary' : 'accent'}
                            className="h-1.5"
                          />
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-text-tertiary">
                              {isCompleted ? t('projects_page.completed') : `${progressPercent}% ${t('projects_page.complete')}`}
                            </span>
                            <span className="font-medium text-primary-400">{progressPercent}%</span>
                          </div>
                        </div>
                      )}

                      {isLocked && (
                        <p className="text-xs text-text-tertiary">
                          {t('projects_page.locked_complete_lesson', { lesson: project.prerequisite_lesson_id || 0 })}
                        </p>
                      )}

                      <div className="flex items-center justify-between mt-3">
                        <ChevronRight className="h-5 w-5 text-text-tertiary transition-transform group-hover:translate-x-1 group-hover:text-primary-400" />
                      </div>
                    </div>
                  </div>

                  <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" aria-hidden="true" />
                </div>
              </Card>
            </Link>
          );
        })}

        {(!projects || projects.length === 0) && (
          <div className="col-span-full text-center py-16 animate-fade-in">
            <div className="p-4 bg-primary-500/10 rounded-2xl w-fit mx-auto mb-4 border border-primary-500/20">
              <FolderKanban className="h-12 w-12 text-primary-400" />
            </div>
            <h2 className="text-xl font-semibold text-text-primary mb-2">{t('projects_page.no_projects')}</h2>
            <p className="text-text-secondary">{t('projects_page.complete_prerequisites')}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function SkeletonProjectCard() {
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