import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Swords, Wifi, WifiOff, Loader2, Trophy, Frown, Clock } from 'lucide-react';
import { duelsApi } from '../api/services';
import { useAuth } from '../contexts/AuthContext';
import { useDuelSocket } from '../hooks/useDuelSocket';
import { Button, CodeEditor, Progress, cn } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';
import { parseUtcDate } from '../lib/utils';
import { LESSON_SHELL_HEIGHT_CLASS } from '../lib/layout';
import type { DuelSocketMessage } from '../types';

function formatCountdown(msRemaining: number): string {
  const totalSeconds = Math.max(0, Math.round(msRemaining / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

interface PlayerCardProps {
  username: string;
  isConnected: boolean;
  isMe: boolean;
  align: 'start' | 'end';
}

function PlayerCard({ username, isConnected, isMe, align }: PlayerCardProps) {
  const { t } = useTranslation();
  return (
    <div className={cn('flex items-center gap-3', align === 'end' && 'flex-row-reverse text-right')}>
      <div
        className={cn(
          'w-11 h-11 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0',
          isMe ? 'bg-gradient-to-br from-primary-500 to-primary-700' : 'bg-gradient-to-br from-accent-500 to-accent-700'
        )}
        aria-hidden="true"
      >
        {username.charAt(0).toUpperCase()}
      </div>
      <div className="min-w-0">
        <p className="font-semibold text-text-primary truncate max-w-[10rem]">
          {username} {isMe && <span className="text-text-tertiary font-normal">{t('duels.you_suffix')}</span>}
        </p>
        <span
          className={cn(
            'flex items-center gap-1.5 text-xs',
            align === 'end' && 'flex-row-reverse',
            isConnected ? 'text-success-400' : 'text-text-tertiary'
          )}
        >
          <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', isConnected ? 'bg-success-500' : 'bg-text-tertiary')} />
          {isConnected ? t('duels.connected') : t('duels.disconnected')}
        </span>
      </div>
    </div>
  );
}

export function DuelArena() {
  const { t, isRTL } = useTranslation();
  const { duelId: duelIdParam } = useParams<{ duelId: string }>();
  const duelId = Number(duelIdParam);
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [ticketVersion, setTicketVersion] = useState(0);
  const [opponentConnected, setOpponentConnected] = useState(false);
  const [myProgress, setMyProgress] = useState({ passed: 0, total: 0 });
  const [opponentProgress, setOpponentProgress] = useState({ passed: 0, total: 0 });
  const [endResult, setEndResult] = useState<{ winnerId: number | null; reason: string } | null>(null);
  const [code, setCode] = useState('');
  const [now, setNow] = useState(() => Date.now());

  const { data: duelState, isLoading: stateLoading } = useQuery({
    queryKey: ['duel-state', duelId],
    queryFn: () => duelsApi.getState(duelId),
    enabled: Number.isFinite(duelId),
    refetchOnWindowFocus: false,
  });

  // Minted fresh for every connect attempt -- a ticket is single-use, so
  // reusing one across a reconnect would just be rejected (see
  // duel_tickets.py). ticketVersion bumping is what actually retriggers
  // this query and, downstream, the socket effect.
  const { data: ticketData, error: ticketError } = useQuery({
    queryKey: ['duel-ticket', duelId, ticketVersion],
    queryFn: () => duelsApi.mintTicket(duelId),
    enabled: Number.isFinite(duelId) && duelState?.status === 'active' && !endResult,
    staleTime: 0,
    gcTime: 0,
    refetchOnWindowFocus: false,
    retry: false,
  });

  const handleSocketMessage = useCallback(
    (message: DuelSocketMessage) => {
      switch (message.type) {
        case 'opponent_connected':
          setOpponentConnected(true);
          break;
        case 'opponent_disconnected':
          setOpponentConnected(false);
          break;
        case 'opponent_progress':
          // This is the entire opponent-progress payload the backend will
          // ever send -- passed_count/total_count only. There's no `code`
          // field on DuelSocketMessage's opponent_progress variant to read
          // even if this wanted to show it.
          setOpponentProgress({ passed: message.passed_count, total: message.total_count });
          break;
        case 'duel_ended':
          setEndResult({ winnerId: message.winner_user_id, reason: message.reason });
          break;
      }
    },
    []
  );

  const { status: socketStatus } = useDuelSocket(duelId, ticketData?.ticket ?? null, handleSocketMessage);

  // Auto-reconnect with a fixed backoff for as long as the duel is live.
  // Two independent things can fail and need their own retry trigger:
  // the ticket mint (REST, e.g. the backend is briefly unreachable) and
  // the socket itself (e.g. a network blip after a successful connect).
  // Watching only `socketStatus` missed the first case: if minting a
  // fresh ticket after a bump fails, `ticketData` stays undefined, so
  // `useDuelSocket` never even attempts a connection and its status
  // never changes from 'closed' -- nothing would re-fire this effect and
  // the client was stuck in "Reconnecting..." forever. Watching
  // `ticketError` too closes that gap. This can't fire before the first
  // ticket exists (status starts at 'connecting', not 'closed').
  useEffect(() => {
    if ((socketStatus === 'closed' || ticketError) && !endResult) {
      const timer = setTimeout(() => setTicketVersion((v) => v + 1), 1500);
      return () => clearTimeout(timer);
    }
  }, [socketStatus, ticketError, endResult]);

  // Seed local state from the REST snapshot -- the source of truth for a
  // fresh page load or a resync after a reconnect, never trusting the
  // socket alone to have carried every state change while it was closed.
  useEffect(() => {
    if (!duelState) return;
    setMyProgress({ passed: duelState.me.passed_count, total: duelState.me.total_count });
    setOpponentProgress({ passed: duelState.opponent.passed_count, total: duelState.opponent.total_count });
    setOpponentConnected(duelState.opponent.is_connected);
    setCode((prev) => (prev ? prev : duelState.problem_starter_code || ''));
    if (duelState.status !== 'active') {
      setEndResult((prev) =>
        prev ?? {
          winnerId: duelState.winner_user_id,
          reason: duelState.winner_user_id ? 'solved' : 'timeout',
        }
      );
    }
  }, [duelState]);

  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);

  const submitMutation = useMutation({
    mutationFn: (codeToSubmit: string) => duelsApi.submit(duelId, codeToSubmit),
    onSuccess: (result) => {
      setMyProgress({ passed: result.passed_count, total: result.total_count });
      if (result.won && user) {
        setEndResult({ winnerId: user.id, reason: 'solved' });
      } else if (result.duel_status !== 'active') {
        setEndResult((prev) =>
          prev ?? { winnerId: result.winner_user_id, reason: result.winner_user_id ? 'solved' : 'timeout' }
        );
      }
    },
    onError: (error: any) => {
      if (error.response?.status === 409) {
        queryClient.invalidateQueries({ queryKey: ['duel-state', duelId] });
      }
    },
  });

  if (stateLoading || !duelState) {
    return (
      <div className={cn(LESSON_SHELL_HEIGHT_CLASS, 'flex items-center justify-center')}>
        <Loader2 className="h-8 w-8 text-primary-400 animate-spin" aria-hidden="true" />
      </div>
    );
  }

  const endsAtMs = parseUtcDate(duelState.ends_at).getTime();
  const remainingMs = endsAtMs - now;
  const timeIsUp = remainingMs <= 0;
  const duelIsOver = !!endResult;
  const iWon = duelIsOver && endResult!.winnerId === user?.id;
  const opponentWon = duelIsOver && endResult!.winnerId !== null && endResult!.winnerId !== user?.id;
  const timedOutNoWinner = duelIsOver && endResult!.winnerId === null;

  return (
    <div className={cn(LESSON_SHELL_HEIGHT_CLASS, 'flex flex-col overflow-hidden bg-bg-primary')} dir={isRTL ? 'rtl' : 'ltr'}>
      <header className="bg-bg-secondary/80 backdrop-blur-xl border-b border-border-primary/50 px-4 py-3 flex-shrink-0">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-3">
          <Link
            to="/app/dashboard"
            className="p-2 rounded-lg hover:bg-bg-tertiary/50 transition-colors text-text-tertiary hover:text-text-primary flex-shrink-0"
            aria-label={t('duels.exit')}
            data-testid="duel-exit"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>

          <div className="flex items-center gap-2 font-mono text-lg font-semibold tabular-nums text-text-primary" role="timer" aria-live="off">
            <Clock className={cn('h-4 w-4', timeIsUp ? 'text-error-400' : 'text-text-tertiary')} aria-hidden="true" />
            <span className={timeIsUp ? 'text-error-400' : undefined} data-testid="duel-countdown">
              {duelIsOver ? '--:--' : formatCountdown(remainingMs)}
            </span>
          </div>

          <span
            className={cn(
              'flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full flex-shrink-0',
              socketStatus === 'open'
                ? 'bg-success-500/10 text-success-400'
                : 'bg-warning-500/10 text-warning-400'
            )}
            data-testid="duel-live-indicator"
          >
            {socketStatus === 'open' ? <Wifi className="h-3.5 w-3.5" /> : <WifiOff className="h-3.5 w-3.5" />}
            {socketStatus === 'open' ? t('duels.live') : t('duels.reconnecting')}
          </span>
        </div>
      </header>

      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4">
        <div className="max-w-5xl mx-auto flex flex-col gap-4 h-full">
          <div className="bg-bg-secondary/50 border border-border-primary/50 rounded-2xl px-5 py-4 flex items-center justify-between gap-4 flex-shrink-0">
            <PlayerCard username={duelState.me.username} isConnected={socketStatus === 'open'} isMe align="start" />
            <Swords className="h-5 w-5 text-text-tertiary flex-shrink-0" aria-hidden="true" />
            <PlayerCard username={duelState.opponent.username} isConnected={opponentConnected} isMe={false} align="end" />
          </div>

          <div className="grid grid-cols-2 gap-4 flex-shrink-0">
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-medium text-text-primary">{t('duels.your_progress')}</span>
                <span className="text-sm text-text-tertiary tabular-nums">
                  {myProgress.passed}/{myProgress.total}
                </span>
              </div>
              <Progress value={myProgress.total > 0 ? myProgress.passed : 0} max={myProgress.total || 1} variant="primary" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-medium text-text-primary">{t('duels.opponent_progress')}</span>
                <span className="text-sm text-text-tertiary tabular-nums">
                  {opponentProgress.passed}/{opponentProgress.total}
                </span>
              </div>
              <Progress
                value={opponentProgress.total > 0 ? opponentProgress.passed : 0}
                max={opponentProgress.total || 1}
                variant="accent"
              />
            </div>
          </div>

          <div className="bg-bg-secondary/50 border border-border-primary/50 rounded-2xl p-5 flex-shrink-0">
            <h2 className="text-sm font-semibold text-text-tertiary uppercase tracking-wide mb-2">
              {t('duels.problem')}
            </h2>
            <p className="text-text-primary whitespace-pre-wrap">{duelState.problem_prompt}</p>
          </div>

          <div className="flex-1 min-h-[320px] flex flex-col">
            <CodeEditor
              code={code}
              onChange={setCode}
              fillHeight
              readOnly={duelIsOver}
              onSubmit={() => submitMutation.mutate(code)}
              isSubmitting={submitMutation.isPending}
              className="flex-1"
            />
            <div className="flex items-center justify-between gap-3 mt-3 flex-shrink-0">
              <div aria-live="polite" className="text-sm text-text-secondary">
                {submitMutation.data && !submitMutation.data.won && submitMutation.data.duel_status === 'active' && (
                  <span>
                    {t('duels.passed_x_of_y', {
                      passed: submitMutation.data.passed_count,
                      total: submitMutation.data.total_count,
                    })}
                  </span>
                )}
              </div>
              <Button
                onClick={() => submitMutation.mutate(code)}
                loading={submitMutation.isPending}
                disabled={duelIsOver || timeIsUp}
                data-testid="duel-submit"
              >
                {t('duels.submit')}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {duelIsOver && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-bg-secondary border border-border-primary rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl">
            {iWon && (
              <>
                <Trophy className="h-14 w-14 text-warning-400 mx-auto mb-4" aria-hidden="true" />
                <h2 className="text-xl font-bold text-text-primary">{t('duels.you_won')}</h2>
              </>
            )}
            {opponentWon && (
              <>
                <Frown className="h-14 w-14 text-text-tertiary mx-auto mb-4" aria-hidden="true" />
                <h2 className="text-xl font-bold text-text-primary">{t('duels.opponent_won')}</h2>
              </>
            )}
            {timedOutNoWinner && (
              <>
                <Clock className="h-14 w-14 text-text-tertiary mx-auto mb-4" aria-hidden="true" />
                <h2 className="text-xl font-bold text-text-primary">{t('duels.time_expired')}</h2>
              </>
            )}
            <Button onClick={() => navigate('/app/duels')} className="mt-6" fullWidth data-testid="duel-end-continue">
              {t('duels.back_to_lobby')}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
