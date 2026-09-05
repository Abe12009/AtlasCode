import { useCallback, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import { exercisesApi, lessonsApi } from '../../api/services';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from '../../hooks/useTranslation';
import { LessonHeader } from '../LessonHeader';
import { ExercisePanel } from '../ExercisePanel';
import type { SubmitVars } from '../exerciseTypes';
import { Button, CodeBlock } from '../ui';
import { cn } from '../../lib/utils';
import { LESSON_SHELL_HEIGHT_CLASS } from '../../lib/layout';
import { HookCard } from './HookCard';
import { Blueprint } from './Blueprint';
import { ExamTip } from './ExamTip';
import { QuestProgress } from './QuestProgress';
import { QuestClear } from './QuestClear';
import { useQuestStage } from './questStage';
import { QUEST_STAGES, type AnyBlueprintConfig, type HookConfig } from './types';
import type { Lesson, LessonBlock, ExerciseSubmitResponse } from '../../types';

function parseConfig<T>(block: LessonBlock | undefined): T | null {
  if (!block?.config) return null;
  try {
    const parsed: unknown = JSON.parse(block.config);
    return typeof parsed === 'object' && parsed !== null ? (parsed as T) : null;
  } catch {
    return null;
  }
}

function blockText(block: LessonBlock, language: string): { content: string; code: string | null } {
  const translation = block.translations.find((t) => t.language === language) ?? block.translations[0];
  return {
    content: translation?.content ?? block.content ?? '',
    code: translation?.code_example ?? block.code_example ?? null,
  };
}

/** A hook block whose config went missing still gets its scenario and its
 * Continue button; only the two config-driven lines fall away. */
const EMPTY_HOOK: HookConfig = { kind: 'hook', challenge: {}, learn: {} };

interface MicroQuestLessonProps {
  lesson: Lesson;
  currentLanguage: string;
}

/**
 * The Micro-Quest experience: Hook -> Blueprint -> Quest -> Complete.
 *
 * This component orchestrates; it does not reimplement anything. Reading and
 * writing lesson content reuses the same block data every lesson already has,
 * exercise submission goes through the exact same ExercisePanel (and so the
 * same sandbox, grader and XP path) as the classic LessonDetail flow, and
 * completion is whatever the backend says it is — the exercise-submit response
 * while the student is here, the lesson's own progress row after a reload.
 *
 * The blueprint interaction is chosen from the block's config.kind, so the
 * flow is identical whether the quest ends in a code editor, a multiple-choice
 * question or a prediction box.
 */
export function MicroQuestLesson({ lesson, currentLanguage }: MicroQuestLessonProps) {
  const { t, isRTL } = useTranslation();
  const { user, loading: authLoading } = useAuth();
  const queryClient = useQueryClient();

  const blocks = lesson.blocks || [];
  const hookBlock = blocks.find((b) => b.block_type === 'hook');
  const blueprintBlock = blocks.find((b) => b.block_type === 'blueprint');
  const examTipBlock = blocks.find((b) => b.block_type === 'exam_tip');
  // Everything else (order 1..) is the lesson's existing reading content —
  // shown during the Blueprint stage, ahead of the interactive puzzle.
  const readingBlocks = blocks.filter(
    (b) => b.block_type !== 'hook' && b.block_type !== 'blueprint' && b.block_type !== 'exam_tip',
  );
  const exercise = useMemo(
    () => [...(lesson.exercises || [])].sort((a, b) => a.order - b.order || a.id - b.id)[0],
    [lesson.exercises],
  );

  const hookConfig = parseConfig<HookConfig>(hookBlock) ?? EMPTY_HOOK;
  const blueprintConfig = parseConfig<AnyBlueprintConfig>(blueprintBlock);

  // The server's own record of this lesson. It decides completion and the XP
  // shown on Quest Clear; localStorage only ever remembers the visual stage.
  const progressQuery = useQuery({
    queryKey: ['lesson-progress', lesson.id],
    queryFn: () => lessonsApi.getProgress(lesson.id),
  });
  const progressSettled = progressQuery.isSuccess || progressQuery.isError;
  const isCompleted = progressQuery.data?.status === 'completed';

  const { stage, advanceTo } = useQuestStage({
    lessonId: lesson.id,
    userKey: user ? String(user.id) : 'anon',
    isCompleted,
    ready: !authLoading && progressSettled,
  });

  const [solvedThisVisit, setSolvedThisVisit] = useState(false);
  const [result, setResult] = useState<ExerciseSubmitResponse | undefined>(undefined);
  const [terminalOutput, setTerminalOutput] = useState('');
  const [terminalError, setTerminalError] = useState('');

  // Reaching the quest is only possible by solving the blueprint, so a resumed
  // student who is already past it must not be asked to solve it again.
  const blueprintSolved =
    solvedThisVisit || QUEST_STAGES.indexOf(stage) >= QUEST_STAGES.indexOf('quest');
  const handleBlueprintSolved = useCallback(() => setSolvedThisVisit(true), []);

  const runMutation = useMutation({
    mutationFn: ({ exerciseId, code }: { exerciseId: number; code: string }) =>
      exercisesApi.run(exerciseId, { code, exercise_id: exerciseId }),
    onSuccess: (data) => {
      if (data.output) setTerminalOutput(data.output);
      if (data.error) setTerminalError(data.error);
    },
    onError: (error: any) => {
      setTerminalError(error.response?.data?.detail || 'Execution failed');
    },
  });

  const submitMutation = useMutation({
    mutationFn: ({ exerciseId, ...answer }: SubmitVars) =>
      exercisesApi.submit(exerciseId, { ...answer, exercise_id: exerciseId }),
    onSuccess: (data) => {
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['lesson', String(lesson.id)] });
      queryClient.invalidateQueries({ queryKey: ['lesson-progress', lesson.id] });
      if (data.is_correct) queryClient.invalidateQueries({ queryKey: ['notifications'] });
      if (data.output) setTerminalOutput(data.output);
      if (data.is_correct) advanceTo('complete');
    },
    onError: (error: any) => {
      setTerminalError(error.response?.data?.detail || 'Submission failed');
    },
  });

  const lessonTitle = lesson.translations[0]?.title ?? '';

  // Both candidates come from the backend and neither is ever recomputed here.
  // A fresh solve reports its award directly; a resumed or re-submitted quest
  // (which earns 0 a second time) reads what the lesson actually banked.
  const questXp =
    result?.is_correct && result.xp_earned > 0
      ? result.xp_earned
      : (progressQuery.data?.xp_earned ?? result?.xp_earned ?? 0);

  return (
    <div className={cn(LESSON_SHELL_HEIGHT_CLASS, 'flex flex-col overflow-hidden bg-bg-primary')} dir={isRTL ? 'rtl' : 'ltr'}>
      <LessonHeader lesson={lesson} />

      <div className="flex-1 min-w-0 overflow-x-hidden overflow-y-auto p-4 sm:p-6 lg:p-8">
        <div className="max-w-3xl min-w-0 mx-auto space-y-6" data-testid="micro-quest">
          <QuestProgress current={stage} />

          {stage === 'hook' && hookBlock && (
            <div className="space-y-4 animate-fade-in">
              <HookCard
                scenario={blockText(hookBlock, currentLanguage).content}
                config={hookConfig}
                language={currentLanguage}
              />
              <div className="flex justify-end">
                <Button
                  onClick={() => advanceTo('blueprint')}
                  data-testid="hook-continue"
                  rightIcon={isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  className="w-full sm:w-auto bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
                >
                  {t('microquest.continue')}
                </Button>
              </div>
            </div>
          )}

          {stage === 'blueprint' && blueprintBlock && (
            <div className="space-y-6 animate-fade-in">
              {readingBlocks.map((block) => {
                const { content, code } = blockText(block, currentLanguage);
                return (
                  <div key={block.id} className="space-y-2">
                    <p className="text-text-secondary leading-relaxed break-words">{content}</p>
                    {block.block_type === 'code' && code && (
                      <CodeBlock>{code}</CodeBlock>
                    )}
                  </div>
                );
              })}

              <div>
                <h3 className="mb-3 text-lg font-semibold text-text-primary">
                  {blockText(blueprintBlock, currentLanguage).content}
                </h3>
                <Blueprint
                  config={blueprintConfig}
                  language={currentLanguage}
                  solved={blueprintSolved}
                  onSolved={handleBlueprintSolved}
                />
              </div>

              {blueprintSolved && (
                <div className="flex justify-end">
                  <Button
                    onClick={() => advanceTo('quest')}
                    data-testid="blueprint-continue"
                    rightIcon={isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    className="w-full sm:w-auto bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
                  >
                    {t('microquest.start_quest')}
                  </Button>
                </div>
              )}
            </div>
          )}

          {stage === 'quest' && exercise && (
            <div className="space-y-6 animate-fade-in" data-testid="quest-stage">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-primary-400">
                {t('microquest.quest_objective')}
              </h2>

              <ExercisePanel
                exercise={exercise}
                onSubmit={submitMutation.mutate}
                onRun={runMutation.mutate}
                result={result}
                isSubmitting={submitMutation.isPending}
                isRunning={runMutation.isPending}
                terminalOutput={terminalOutput}
                terminalError={terminalError}
                onClearTerminal={() => {
                  setTerminalOutput('');
                  setTerminalError('');
                }}
              />

              {examTipBlock && (
                <ExamTip text={blockText(examTipBlock, currentLanguage).content} />
              )}
            </div>
          )}

          {stage === 'complete' && <QuestClear xpEarned={questXp} lessonTitle={lessonTitle} />}
        </div>
      </div>
    </div>
  );
}
