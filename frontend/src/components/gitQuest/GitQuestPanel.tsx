import { useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Check, RotateCcw, GitBranch } from 'lucide-react';
import { Button, Badge } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { gitQuestApi } from '../../api/services';
import { GitTerminal, type TerminalEntry } from './GitTerminal';
import { GitFileEditor } from './GitFileEditor';
import type { Exercise, GitQuestAction, GitQuestState } from '../../types';
import type { SubmitVars } from '../exerciseTypes';

interface GitQuestPanelProps {
  exercise: Exercise;
  onSubmit: (vars: SubmitVars) => void;
  isSubmitting: boolean;
}

function parseStarter(raw: string | null): GitQuestState | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as GitQuestState;
  } catch {
    return null;
  }
}

export function GitQuestPanel({ exercise, onSubmit, isSubmitting }: GitQuestPanelProps) {
  const { t } = useTranslation();
  const starter = useMemo(() => parseStarter(exercise.starter_code), [exercise.starter_code]);
  const [state, setState] = useState<GitQuestState | null>(starter);
  const [actions, setActions] = useState<GitQuestAction[]>([]);
  const [history, setHistory] = useState<TerminalEntry[]>([]);

  const executeMutation = useMutation({
    mutationFn: (vars: { state: GitQuestState; action: GitQuestAction }) =>
      gitQuestApi.execute(vars.state, vars.action),
  });

  const runAction = async (action: GitQuestAction, label: string) => {
    if (!state) return;
    const result = await executeMutation.mutateAsync({ state, action });
    setState(result.state);
    setActions((prev) => [...prev, action]);
    setHistory((prev) => [...prev, { command: label, output: result.output, error: result.error }]);
  };

  const handleCommand = (command: string) => {
    runAction({ kind: 'command', value: `git ${command.replace(/^git\s+/, '')}` }, `git ${command.replace(/^git\s+/, '')}`);
  };

  const handleFileSave = (file: string, content: string) => {
    runAction({ kind: 'edit', file, content }, `# edited ${file}`);
  };

  const handleReset = () => {
    setState(starter);
    setActions([]);
    setHistory([]);
  };

  const handleSubmit = () => {
    onSubmit({ exerciseId: exercise.id, answer: JSON.stringify(actions) });
  };

  if (!starter || !state) {
    return (
      <div className="rounded-lg border border-error-500/30 bg-error-500/10 p-3 text-sm text-error-600 dark:text-error-400">
        {t('git_quest.load_error')}
      </div>
    );
  }

  const currentBranch = state.head && 'branch' in state.head ? state.head.branch : null;
  const conflictedFiles = state.merge_in_progress?.conflicted_files ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm">
        <GitBranch className="h-4 w-4 text-text-tertiary" />
        <span className="text-text-secondary">{t('git_quest.current_branch')}:</span>
        <Badge variant={conflictedFiles.length > 0 ? 'warning' : 'primary'} size="sm">
          {currentBranch ?? t('git_quest.not_initialized')}
        </Badge>
        {conflictedFiles.length > 0 && (
          <span className="text-warning-500 text-xs">
            {t('git_quest.conflict_banner', { files: conflictedFiles.join(', ') })}
          </span>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <GitTerminal history={history} onCommand={handleCommand} disabled={executeMutation.isPending} />
        <GitFileEditor files={state.working_files} conflictedFiles={conflictedFiles} onSave={handleFileSave} />
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <Button variant="outline" onClick={handleReset} leftIcon={<RotateCcw className="h-4 w-4" />}>
          {t('git_quest.reset')}
        </Button>
        <div className="flex-1" />
        <Button
          onClick={handleSubmit}
          disabled={isSubmitting || actions.length === 0}
          loading={isSubmitting}
          leftIcon={<Check className="h-4 w-4" />}
          className="bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent"
          data-testid="git-quest-submit"
        >
          {t('lessons.submit_solution')}
        </Button>
      </div>
    </div>
  );
}
