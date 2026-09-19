import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Swords, Loader2, X } from 'lucide-react';
import { duelsApi } from '../api/services';
import { Button, Card, cn } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';
import type { DuelDifficulty } from '../types';

const DIFFICULTIES: DuelDifficulty[] = ['beginner', 'intermediate', 'advanced'];

export function DuelLobby() {
  const { t, isRTL } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [difficulty, setDifficulty] = useState<DuelDifficulty | null>(null);
  const [waiting, setWaiting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const joinMutation = useMutation({
    mutationFn: (d: DuelDifficulty) => duelsApi.joinQueue(d),
    onSuccess: (result) => {
      if (result.status === 'matched' && result.duel_id) {
        navigate(`/app/duels/${result.duel_id}`);
      } else {
        setWaiting(true);
      }
    },
    onError: (error: any) => {
      setErrorMessage(error.response?.data?.detail || t('duels.join_failed'));
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => duelsApi.cancelQueue(),
    onSuccess: () => {
      setWaiting(false);
      setDifficulty(null);
      queryClient.removeQueries({ queryKey: ['duel-queue-status'] });
    },
  });

  // Polled while waiting -- queue-wait latency doesn't need to feel instant
  // (see the Step 4 architecture), only the live duel itself does.
  const { data: queueStatus } = useQuery({
    queryKey: ['duel-queue-status'],
    queryFn: () => duelsApi.queueStatus(),
    enabled: waiting,
    refetchInterval: 2000,
  });

  useEffect(() => {
    if (queueStatus?.status === 'matched' && queueStatus.duel_id) {
      setWaiting(false);
      navigate(`/app/duels/${queueStatus.duel_id}`);
    }
  }, [queueStatus, navigate]);

  const handleJoin = (d: DuelDifficulty) => {
    setErrorMessage('');
    setDifficulty(d);
    joinMutation.mutate(d);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10" dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-700 to-accent-800 shadow-glow-accent mb-4">
          <Swords className="h-8 w-8 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-text-primary">{t('duels.lobby_title')}</h1>
        <p className="text-text-tertiary mt-2">{t('duels.lobby_subtitle')}</p>
      </div>

      {waiting ? (
        <Card className="p-8 text-center">
          <Loader2 className="h-10 w-10 text-primary-400 animate-spin mx-auto mb-4" aria-hidden="true" />
          <p className="text-text-primary font-medium" role="status" aria-live="polite">
            {t('duels.waiting_for_opponent', { difficulty: t(`courses.difficulty_level.${difficulty}`) })}
          </p>
          <Button
            variant="ghost"
            onClick={() => cancelMutation.mutate()}
            loading={cancelMutation.isPending}
            leftIcon={<X className="h-4 w-4" />}
            className="mt-6"
            data-testid="duel-lobby-cancel"
          >
            {t('common.cancel')}
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {DIFFICULTIES.map((d) => (
            <button
              key={d}
              onClick={() => handleJoin(d)}
              disabled={joinMutation.isPending}
              data-testid={`duel-lobby-join-${d}`}
              className={cn(
                'p-6 rounded-2xl border border-border-primary bg-bg-secondary hover:border-primary-500/50 hover:bg-bg-tertiary/50 transition-all text-left disabled:opacity-50',
                joinMutation.isPending && difficulty === d && 'border-primary-500 bg-bg-tertiary/50'
              )}
            >
              <p className="font-semibold text-text-primary">{t(`courses.difficulty_level.${d}`)}</p>
              <p className="text-sm text-text-tertiary mt-1">{t(`duels.difficulty_hint.${d}`)}</p>
              {joinMutation.isPending && difficulty === d && (
                <Loader2 className="h-4 w-4 text-primary-400 animate-spin mt-3" aria-hidden="true" />
              )}
            </button>
          ))}
        </div>
      )}

      {errorMessage && (
        <p className="text-error-400 text-sm text-center mt-6" role="alert">
          {errorMessage}
        </p>
      )}
    </div>
  );
}
