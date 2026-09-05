import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../api/services';
import { ArrowLeft, FolderKanban, Clock, Target, CheckCircle, ChevronDown, ChevronRight, Play, Code, Copy, AlertCircle, Globe, Lock, Flag, ExternalLink, ChevronLeft, Sparkles, Terminal, GitBranch } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { Card, Badge, Button, Progress, Alert, cn, Skeleton, CodeEditor, TerminalPanel, StatusBadge, XPBadge } from '../components/ui';

export function ProjectDetail() {
  const { t, isRTL, currentLanguage } = useTranslation();
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [expandedTasks, setExpandedTasks] = useState<Set<number>>(new Set());
  const [taskCode, setTaskCode] = useState<Record<number, string>>({});
  const [language, setLanguage] = useState<'en' | 'fr' | 'ar'>(currentLanguage as 'en' | 'fr' | 'ar');
  const [submitFeedback, setSubmitFeedback] = useState<Record<number, { success: boolean; message: string }>>({});
  const [terminalOutput, setTerminalOutput] = useState<string>('');
  const [terminalError, setTerminalError] = useState<string>('');

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', projectId, language],
    queryFn: () => projectsApi.getById(Number(projectId), language),
    enabled: !!projectId,
  });

  const { data: progress } = useQuery({
    queryKey: ['projectProgress', projectId],
    queryFn: () => projectsApi.getProgress(Number(projectId)),
    enabled: !!projectId,
  });

  const submitMutation = useMutation({
    mutationFn: ({ taskId, code }: { taskId: number; code: string }) =>
      projectsApi.submitTask(Number(projectId), taskId, code),
    onSuccess: (result, variables) => {
      queryClient.invalidateQueries({ queryKey: ['projectProgress', projectId] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      if ((result as { success?: boolean }).success) {
        queryClient.invalidateQueries({ queryKey: ['notifications'] });
      }
      setSubmitFeedback(prev => ({
        ...prev,
        [variables.taskId]: { success: true, message: t('projects.task_submitted') }
      }));
    },
    onError: (error: any, variables) => {
      setSubmitFeedback(prev => ({
        ...prev,
        [variables.taskId]: { success: false, message: error.response?.data?.detail || t('projects.submission_failed') }
      }));
      setTerminalError(error.response?.data?.detail || 'Submission failed');
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <Skeleton variant="text" width="40%" height={24} data-testid="loading-spinner" />
          <Skeleton variant="rectangular" width={120} height={36} />
        </div>
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton variant="rectangular" width="100%" height={250} />
            <Skeleton variant="rectangular" width="100%" height={400} />
          </div>
          <div className="space-y-6">
            <Skeleton variant="rectangular" width="100%" height={500} />
          </div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="text-center py-12" dir={isRTL ? 'rtl' : 'ltr'}>
        <p className="text-error-600 dark:text-error-400">{t('errors.not_found')}</p>
        <Link to="/app/projects" className="mt-4 inline-block text-primary-400 hover:text-primary-300">
          {t('common.back_to_projects')}
        </Link>
      </div>
    );
  }

  const isLocked = progress?.status === 'locked';
  const isCompleted = progress?.status === 'completed';
  const isInProgress = progress?.status === 'in_progress';
  const completedTasks = progress?.current_task || 0;
  const totalTasks = project.tasks?.length || 0;
  const progressPercent = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
  const currentTaskIndex = isCompleted ? totalTasks - 1 : (progress?.current_task || 0);

  const toggleTask = (taskId: number) => {
    setExpandedTasks((prev) => {
      const next = new Set(prev);
      if (next.has(taskId)) {
        next.delete(taskId);
      } else {
        next.add(taskId);
      }
      return next;
    });
  };

  const expandTask = (taskId: number) => {
    setExpandedTasks(prev => new Set(prev).add(taskId));
  };

  const collapseTask = (taskId: number) => {
    setExpandedTasks(prev => {
      const next = new Set(prev);
      next.delete(taskId);
      return next;
    });
  };

  const handleSubmit = (taskId: number) => {
    const task = project.tasks?.find(t => t.id === taskId);
    const code = taskCode[taskId] || task?.starter_code || '';
    if (!code.trim()) {
      setSubmitFeedback(prev => ({
        ...prev,
        [taskId]: { success: false, message: t('projects.please_write_code') }
      }));
      return;
    }
    setTerminalOutput('');
    setTerminalError('');
    submitMutation.mutate({ taskId, code });
  };

  const getTranslation = (translations: any[], lang: string) => {
    return translations.find(t => t.language === lang) || translations[0];
  };

  const projectTranslation = getTranslation(project.translations, language);
  const canSubmitTask = (index: number) => !isLocked && (index <= currentTaskIndex);

  return (
    <div className="space-y-8 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between flex-wrap gap-4">
        <Link to="/app/projects" className="inline-flex items-center gap-2 text-text-tertiary hover:text-primary-400 dark:hover:text-primary-300 text-sm font-medium transition-colors">
          <ChevronLeft className="h-4 w-4" />
          <span>{t('common.back_to_projects')}</span>
        </Link>
        <div className="flex items-center gap-2">
          <label className="text-sm text-text-tertiary">{t('common.language')}</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as 'en' | 'fr' | 'ar')}
            className="px-3 py-1.5 bg-bg-secondary border border-border-primary/50 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-transparent"
          >
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="ar">العربية</option>
          </select>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Card variant="default" padding="lg" className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5" aria-hidden="true" />
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-blue-500/10 rounded-xl">
                  <FolderKanban className="h-8 w-8 text-blue-400" />
                </div>
                <div>
                  <div className="flex items-center flex-wrap gap-2">
                    <Badge variant="primary" size="sm">
                      {t('projects.project_number', { order: project.order })}
                    </Badge>
                    {project.prerequisite_lesson_id && (
                      <Badge variant="warning" size="sm" className="gap-1">
                        <Lock className="h-3 w-3" />
                        {t('projects.prerequisite_lesson', { lesson: project.prerequisite_lesson_id })}
                      </Badge>
                    )}
                  </div>
                  <h1 className="text-2xl font-bold text-text-primary mt-2">
                    {projectTranslation?.title}
                  </h1>
                </div>
              </div>

              <div className="prose dark:prose-invert max-w-none mb-6">
                <p className="text-text-secondary">
                  {projectTranslation?.story}
                </p>
              </div>

              {projectTranslation?.objective && (
                <div className="mb-6 p-4 bg-primary-500/10 border border-primary-500/30 rounded-xl">
                  <h3 className="font-semibold text-primary-400 mb-2 flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    <span>{t('projects.objective')}</span>
                  </h3>
                  <p className="text-primary-300 text-sm">
                    {projectTranslation?.objective}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 pt-6 border-t border-border-primary/50">
                <div className="text-center p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                  <div className="flex items-center justify-center gap-1 text-text-tertiary mb-1">
                    <Clock className="h-5 w-5" />
                    <span className="text-sm">{t('projects.tasks_count', { count: totalTasks })}</span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary">{totalTasks}</div>
                  <div className="text-sm text-text-tertiary">{t('projects.tasks')}</div>
                </div>
                <div className="text-center p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50 border-x border-border-primary/50">
                  <div className="flex items-center justify-center gap-1 text-text-tertiary mb-1">
                    <Target className="h-5 w-5" />
                    <span className="text-sm">{t('projects.difficulty')}</span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary capitalize">{project.difficulty}</div>
                  <div className="text-sm text-text-tertiary">{t('projects.level')}</div>
                </div>
                <div className="text-center p-4 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                  <div className="flex items-center justify-center gap-1 text-text-tertiary mb-1">
                    <Code className="h-5 w-5" />
                    <span className="text-sm">{t('projects.xp_reward')}</span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary">{project.xp_reward}</div>
                  <div className="text-sm text-text-tertiary">{t('common.xp')}</div>
                </div>
              </div>
            </div>
          </Card>

          <Card variant="default" padding="lg" className="relative overflow-hidden">
            <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
            <div className="relative z-10">
              <div className="p-5 border-b border-border-primary/50 mb-5">
                <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                  <GitBranch className="h-5 w-5 text-accent-400" />
                  <span>{t('projects.tasks')}</span>
                  <Sparkles className="h-4 w-4 text-accent-400" />
                </h2>
              </div>
              <div className="divide-y divide-border-primary/50">
                {project.tasks?.map((task, index) => {
                  const isExpanded = expandedTasks.has(task.id);
                  const isCompletedTask = progress && progress.current_task > index;
                  const isCurrentTask = progress && progress.current_task === index && !isCompleted;
                  const canSubmit = !isLocked && (isCurrentTask || isCompletedTask);

                  const taskTranslation = getTranslation(task.translations, language);
                  const feedback = submitFeedback[task.id];

                  return (
                    <div key={task.id}>
                      <button
                        onClick={() => toggleTask(task.id)}
                        className="w-full px-5 py-4 flex items-center justify-between hover:bg-primary-500/5 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium relative',
                            isCompletedTask
                              ? 'bg-success-500/20 text-success-400 border border-success-500/30'
                              : isCurrentTask
                              ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30 ring-2 ring-primary-500/20 animate-pulse'
                              : 'bg-bg-tertiary text-text-tertiary border border-border-primary/50'
                          )}>
                            {isCompletedTask ? (
                              <CheckCircle className="h-5 w-5" />
                            ) : (
                              <>
                                {index + 1}
                                {isCurrentTask && !isCompleted && (
                                  <span className="absolute -top-1 -right-1 bg-primary-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                                    {t('projects.current')}
                                  </span>
                                )}
                              </>
                            )}
                          </div>
                          <div>
                            <h3 className="font-medium text-text-primary">
                              {taskTranslation?.title}
                            </h3>
                            <p className="text-sm text-text-tertiary">
                              {t('projects.task_of', { current: index + 1, total: totalTasks })}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {feedback && (
                            <span className={cn('flex items-center gap-1 text-xs', feedback.success ? 'text-success-400' : 'text-error-400')}>
                              {feedback.success ? <CheckCircle className="h-3 w-3" /> : <AlertCircle className="h-3 w-3" />}
                              <span>{feedback.message}</span>
                            </span>
                          )}
                          <ChevronDown
                            className={cn('h-5 w-5 text-text-tertiary transition-transform duration-200', isExpanded && 'rotate-180')}
                          />
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="px-5 pb-5 pl-14 space-y-4 animate-slide-down">
                          <div className="prose dark:prose-invert max-w-none">
                            <p className="text-text-secondary">
                              {taskTranslation?.description}
                            </p>
                          </div>

                          {taskTranslation?.hint && (
                            <div className="bg-warning-500/10 border border-warning-500/30 rounded-xl p-4">
                              <div className="flex items-start gap-2">
                                <span className="text-warning-400 text-xl">💡</span>
                                <p className="text-warning-300 text-sm">{taskTranslation?.hint}</p>
                              </div>
                            </div>
                          )}

                          <div className="border border-border-primary/50 rounded-xl overflow-hidden bg-bg-code">
                            <div className="flex items-center justify-between px-3 py-2 bg-bg-code-light border-b border-border-primary/50">
                              <span className="text-xs text-text-tertiary font-mono">python</span>
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => {
                                    const code = taskCode[task.id] || task.starter_code || '';
                                    navigator.clipboard.writeText(code);
                                    setSubmitFeedback(prev => ({
                                      ...prev,
                                      [task.id]: { success: true, message: t('projects.copied') }
                                    }));
                                  }}
                                  className="p-1 rounded hover:bg-bg-tertiary/50 transition-colors"
                                  title={t('projects.copy_code')}
                                  data-testid={`task-copy-btn-${task.id}`}
                                >
                                  <Copy className="h-4 w-4 text-text-tertiary" />
                                </button>
                              </div>
                            </div>
                            <CodeEditor
                              code={taskCode[task.id] || task.starter_code || ''}
                              onChange={(code) => setTaskCode((prev) => ({ ...prev, [task.id]: code }))}
                              language="python"
                              readOnly={isLocked}
                              showLineNumbers
                              minHeight="300px"
                              placeholder={t('projects.write_code_here')}
                            />
                          </div>

                          <div className="flex items-center gap-3 flex-wrap">
                            <Button
                              onClick={() => handleSubmit(task.id)}
                              disabled={submitMutation.isPending || isLocked || isCompletedTask || !canSubmitTask(index)}
                              leftIcon={<Play className="h-4 w-4" />}
                              className="flex-1 min-w-[180px] bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
                            >
                              {submitMutation.isPending ? t('projects.submitting') : isCompletedTask ? t('projects.task_completed') : isLocked ? t('projects.locked') : canSubmitTask(index) ? t('projects.submit_task') : t('projects.complete_previous')}
                            </Button>

                            {index > 0 && (
                              <Button
                                variant="outline"
                                onClick={() => { collapseTask(task.id); expandTask(project.tasks![index - 1].id); }}
                                leftIcon={<ChevronLeft className="h-4 w-4" />}
                              >
                                {t('projects.previous_task')}
                              </Button>
                            )}
                            {index < totalTasks - 1 && (
                              <Button
                                variant="outline"
                                onClick={() => { collapseTask(task.id); expandTask(project.tasks![index + 1].id); }}
                                rightIcon={<ChevronRight className="h-4 w-4" />}
                              >
                                {t('projects.next_task')}
                              </Button>
                            )}
                          </div>
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
                <span>{t('projects.project_guide')}</span>
              </h2>
              <div className="prose dark:prose-invert max-w-none text-sm">
                <p className="text-text-secondary mb-4">
                  {projectTranslation?.guide || t('projects.complete_all_tasks')}
                </p>
              </div>

              {projectTranslation?.skills && (
                <div className="mb-4">
                  <h3 className="font-medium text-text-primary mb-2 flex items-center gap-2">
                    <ExternalLink className="h-5 w-5" />
                    <span>{t('projects.skills_learn')}</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {projectTranslation?.skills?.split(',').map((skill: string, i: number) => (
                      <Badge key={i} variant="primary" size="sm">
                        {skill.trim()}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-6 pt-6 border-t border-border-primary/50">
                <h3 className="font-medium text-text-primary mb-3 flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  <span>{t('projects.your_progress')}</span>
                </h3>
                <dl className="space-y-3 text-sm">
                  <div className="flex justify-between p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <dt className="text-text-tertiary">{t('projects.status')}</dt>
                    <dd className="font-medium text-text-primary capitalize">
                      {progress?.status === 'completed' ? (
                        <StatusBadge status="completed" size="sm" data-testid="project-status-badge" />
                      ) : isInProgress ? (
                        <StatusBadge status="current" size="sm" data-testid="project-status-badge" />
                      ) : isLocked ? (
                        <StatusBadge status="locked" size="sm" data-testid="project-status-badge" />
                      ) : (
                        <StatusBadge status="available" size="sm" data-testid="project-status-badge" />
                      )}
                    </dd>
                  </div>
                  <div className="flex justify-between p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <dt className="text-text-tertiary">{t('projects.completed_tasks')}</dt>
                    <dd className="font-medium text-text-primary">{completedTasks} / {totalTasks}</dd>
                  </div>
                  <div className="flex justify-between p-3 bg-bg-secondary/50 rounded-xl border border-border-primary/50">
                    <dt className="text-text-tertiary">{t('projects.xp_reward')}</dt>
                    <dd className="font-medium text-text-primary">{project.xp_reward} XP</dd>
                  </div>
                  {progress?.xp_earned && progress?.xp_earned > 0 && (
                    <div className="flex justify-between p-3 bg-success-500/10 rounded-xl border border-success-500/30 text-success-400">
                      <dt className="text-text-tertiary">{t('projects.xp_earned')}</dt>
                      <dd className="font-medium">{progress.xp_earned} XP</dd>
                    </div>
                  )}
                </dl>

                <div className="mt-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-text-tertiary">{t('projects.overall_progress')}</span>
                    <span className="font-medium text-text-primary">{Math.round(progressPercent)}%</span>
                  </div>
                  <Progress
                    value={progressPercent}
                    size="md"
                    variant={isCompleted ? 'success' : isInProgress ? 'primary' : 'accent'}
                  />
                </div>
              </div>

              {isLocked && project.prerequisite_lesson_id && (
                <div className="mt-6 pt-6 border-t border-border-primary/50">
                  <div className="flex items-center gap-2 p-3 bg-warning-500/10 border border-warning-500/30 rounded-lg">
                    <Lock className="h-5 w-5 text-warning-400" />
                    <span className="text-sm text-warning-300">
                      {t('projects.locked_complete_prerequisite', { lesson: project.prerequisite_lesson_id })}
                    </span>
                  </div>
                </div>
              )}

              <TerminalPanel
                output={terminalOutput}
                error={terminalError}
                isRunning={submitMutation.isPending}
                clearable={true}
                onClear={() => { setTerminalOutput(''); setTerminalError(''); }}
                className="mt-4 h-64"
              />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}