import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Compass, ChevronLeft, ChevronRight, Sparkles, RotateCcw, Map as MapIcon } from 'lucide-react';
import { orientiniApi } from '../api/services';
import { useTranslation } from '../hooks/useTranslation';
import { Card, Button, Badge, Skeleton, cn } from '../components/ui';
import type { BacTrack, Institution, OrientiniResult } from '../types';

const BAC_TRACKS: BacTrack[] = ['sciences_math_a', 'sciences_math_b', 'pc', 'svt', 'ste', 'stm'];

type Stage = 'intro' | 'quiz' | 'results';

function translationFor<T extends { language: string }>(items: T[], language: string): T | undefined {
  return items.find((item) => item.language === language) || items[0];
}

export function Orientini() {
  const { t, currentLanguage, isRTL } = useTranslation();
  const queryClient = useQueryClient();
  const [stage, setStage] = useState<Stage>('intro');
  const [stepIndex, setStepIndex] = useState(0);
  const [bacTrack, setBacTrack] = useState<BacTrack | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<OrientiniResult | null>(null);

  const { data: questions, isLoading: questionsLoading } = useQuery({
    queryKey: ['orientini-questions', currentLanguage],
    queryFn: () => orientiniApi.getQuestions(currentLanguage),
    enabled: stage === 'quiz',
  });

  const { data: institutions } = useQuery({
    queryKey: ['orientini-institutions', currentLanguage],
    queryFn: () => orientiniApi.getInstitutions(currentLanguage),
  });

  const { data: latestResult } = useQuery({
    queryKey: ['orientini-latest-result'],
    queryFn: () => orientiniApi.getLatestResult(),
    retry: false,
    throwOnError: false,
  });

  const submitMutation = useMutation({
    mutationFn: () => orientiniApi.submit({ answers, bac_track: bacTrack }),
    onSuccess: (data) => {
      setResult(data);
      setStage('results');
      queryClient.invalidateQueries({ queryKey: ['orientini-latest-result'] });
    },
  });

  // Steps: [bac-track step, ...questions]
  const totalSteps = (questions?.length ?? 0) + 1;
  const isBacTrackStep = stepIndex === 0;
  const currentQuestion = questions?.[stepIndex - 1];

  const canGoNext = isBacTrackStep ? bacTrack !== null : currentQuestion ? answers[currentQuestion.id] !== undefined : false;

  const institutionById = useMemo(() => {
    const map = new Map<number, Institution>();
    (institutions ?? []).forEach((inst) => map.set(inst.id, inst));
    return map;
  }, [institutions]);

  const displayedResult = result ?? latestResult ?? null;

  const startQuiz = () => {
    setStepIndex(0);
    setBacTrack(null);
    setAnswers({});
    setResult(null);
    setStage('quiz');
  };

  const goNext = () => {
    if (stepIndex + 1 >= totalSteps) {
      submitMutation.mutate();
    } else {
      setStepIndex((i) => i + 1);
    }
  };

  const goBack = () => setStepIndex((i) => Math.max(0, i - 1));

  return (
    <div className="space-y-8 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
            <Compass className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">{t('orientini.nav_label')}</h1>
            <p className="text-text-tertiary text-sm">{t('orientini.intro_description')}</p>
          </div>
        </div>
        <Link to="/app/orientini/explorer">
          <Button variant="outline" leftIcon={<MapIcon className="h-4 w-4" />}>
            {t('orientini.view_explorer')}
          </Button>
        </Link>
      </div>

      {stage === 'intro' && (
        <Card padding="lg" className="text-center space-y-6">
          <Sparkles className="h-10 w-10 text-primary-500 mx-auto" />
          <div>
            <h2 className="text-xl font-semibold text-text-primary">{t('orientini.intro_title')}</h2>
            <p className="text-text-tertiary mt-2 max-w-xl mx-auto">{t('orientini.intro_description')}</p>
          </div>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Button size="lg" onClick={startQuiz} data-testid="orientini-start-quiz">
              {t('orientini.start_quiz')}
            </Button>
            {displayedResult && (
              <Button size="lg" variant="secondary" onClick={() => setStage('results')} leftIcon={<RotateCcw className="h-4 w-4" />}>
                {t('orientini.retake_quiz')}
              </Button>
            )}
          </div>
        </Card>
      )}

      {stage === 'quiz' && (
        <Card padding="lg" className="space-y-6">
          {questionsLoading ? (
            <Skeleton variant="rectangular" height={200} />
          ) : (
            <>
              <div className="flex items-center justify-between text-sm text-text-tertiary">
                <span>{t('orientini.step_label', { current: stepIndex + 1, total: totalSteps })}</span>
              </div>
              <div className="w-full h-2 rounded-full bg-bg-tertiary overflow-hidden">
                <div
                  className="h-full bg-primary-500 transition-all duration-300"
                  style={{ width: `${((stepIndex + 1) / totalSteps) * 100}%` }}
                />
              </div>

              {isBacTrackStep ? (
                <div className="space-y-4">
                  <h2 className="text-lg font-semibold text-text-primary">{t('orientini.bac_track_question')}</h2>
                  <p className="text-sm text-text-tertiary">{t('orientini.bac_track_optional')}</p>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {BAC_TRACKS.map((track) => (
                      <button
                        key={track}
                        type="button"
                        onClick={() => setBacTrack(track)}
                        className={cn(
                          'text-start px-4 py-3 rounded-xl border transition-colors',
                          bacTrack === track
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-border-primary hover:border-primary-300',
                        )}
                      >
                        {t(`orientini.bac_track_${track}`)}
                      </button>
                    ))}
                  </div>
                </div>
              ) : currentQuestion ? (
                <div className="space-y-4">
                  <h2 className="text-lg font-semibold text-text-primary">
                    {translationFor(currentQuestion.translations, currentLanguage)?.text}
                  </h2>
                  <div className="grid gap-3">
                    {currentQuestion.options.map((option) => (
                      <button
                        key={option.id}
                        type="button"
                        onClick={() => setAnswers((prev) => ({ ...prev, [currentQuestion.id]: option.id }))}
                        className={cn(
                          'text-start px-4 py-3 rounded-xl border transition-colors',
                          answers[currentQuestion.id] === option.id
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-border-primary hover:border-primary-300',
                        )}
                      >
                        {translationFor(option.translations, currentLanguage)?.text}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}

              <div className="flex items-center justify-between pt-2">
                <Button variant="ghost" onClick={goBack} disabled={stepIndex === 0} leftIcon={<ChevronLeft className="h-4 w-4" />}>
                  {t('orientini.back')}
                </Button>
                <Button
                  onClick={goNext}
                  disabled={!canGoNext || submitMutation.isPending}
                  loading={submitMutation.isPending}
                  rightIcon={stepIndex + 1 < totalSteps ? <ChevronRight className="h-4 w-4" /> : undefined}
                >
                  {stepIndex + 1 >= totalSteps ? t('orientini.submit') : t('orientini.next')}
                </Button>
              </div>
            </>
          )}
        </Card>
      )}

      {stage === 'results' && displayedResult && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-text-primary">{t('orientini.results_title')}</h2>
              <p className="text-text-tertiary text-sm">{t('orientini.results_description')}</p>
            </div>
            <Button variant="outline" onClick={startQuiz} leftIcon={<RotateCcw className="h-4 w-4" />}>
              {t('orientini.retake_quiz')}
            </Button>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {displayedResult.scores.map((score) => {
              const institution = institutionById.get(score.institution_id);
              if (!institution) return null;
              const translation = translationFor(institution.translations, currentLanguage);
              const percent = Math.round(Math.max(0, score.score) * 100);
              return (
                <Card key={score.institution_id} padding="md" className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl" aria-hidden="true">{institution.icon}</span>
                      <h3 className="font-semibold text-text-primary">{translation?.name}</h3>
                    </div>
                    <Badge variant={percent >= 60 ? 'success' : 'neutral'}>
                      {t('orientini.match_score', { percent })}
                    </Badge>
                  </div>
                  {translation?.description && (
                    <p className="text-sm text-text-tertiary">{translation.description}</p>
                  )}
                  {!score.eligible && (
                    <Badge variant="warning" size="sm">{t('orientini.not_eligible')}</Badge>
                  )}
                  <Link to="/app/orientini/explorer" className="text-sm text-primary-600 dark:text-primary-400 hover:underline">
                    {t('orientini.requirements')}
                  </Link>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
