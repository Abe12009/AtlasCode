import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, fireEvent, act } from '@testing-library/react';
import { renderWithProviders } from '../../test/setup.tsx';
import { authApi, duelsApi } from '../../api/services';
import type { DuelSocketMessage, DuelStateResponse } from '../../types';

const mockedDuelsApi = vi.mocked(duelsApi);
const mockedAuthApi = vi.mocked(authApi);

let latestOnMessage: ((message: DuelSocketMessage) => void) | null = null;
let latestSocketStatus: 'connecting' | 'open' | 'closed' = 'open';

vi.mock('../../hooks/useDuelSocket', () => ({
  useDuelSocket: (
    _duelId: number | null,
    _ticket: string | null,
    onMessage: (message: DuelSocketMessage) => void
  ) => {
    latestOnMessage = onMessage;
    return { status: latestSocketStatus };
  },
}));

const ME = { id: 1, email: 'me@example.com', username: 'me_student', preferred_language: 'en', is_active: true, created_at: '2026-01-01T00:00:00Z' };

const DUEL_STATE: DuelStateResponse = {
  id: 42,
  status: 'active',
  started_at: '2026-01-01T00:00:00.000000',
  ends_at: new Date(Date.now() + 5 * 60 * 1000).toISOString().replace('Z', ''),
  ended_at: null,
  winner_user_id: null,
  problem_prompt: 'Write a function that reverses a string.',
  problem_starter_code: 'def reverse(s):\n    pass\n',
  me: { user_id: 1, username: 'me_student', is_connected: true, passed_count: 0, total_count: 0 },
  opponent: { user_id: 2, username: 'rival_student', is_connected: true, passed_count: 0, total_count: 0 },
};

describe('DuelArena', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    latestOnMessage = null;
    latestSocketStatus = 'open';
    mockedAuthApi.getMe.mockResolvedValue(ME);
    mockedAuthApi.getProfile.mockResolvedValue({
      id: 1,
      user_id: 1,
      name: 'me_student',
      xp: 0,
      level: 1,
      streak: 0,
      completed_lessons: 0,
      completed_projects: 0,
      current_mission_id: null,
    } as any);
    mockedDuelsApi.getState.mockResolvedValue(DUEL_STATE);
    mockedDuelsApi.mintTicket.mockResolvedValue({ ticket: 'a-ticket' });
  });

  async function open() {
    return renderWithProviders(null as never, { authToken: 'a-token', duelId: '42' });
  }

  it('renders both players, the shared problem, and a live indicator', async () => {
    await open();

    expect(await screen.findByText('me_student')).toBeInTheDocument();
    expect(await screen.findByText('rival_student')).toBeInTheDocument();
    expect(screen.getByText('Write a function that reverses a string.')).toBeInTheDocument();
    expect(screen.getByTestId('duel-live-indicator')).toHaveTextContent('Live');
    expect(screen.getByTestId('duel-countdown')).toHaveTextContent(/\d:\d\d/);
  });

  it('updates the opponent progress bar from a WebSocket broadcast, never rendering code', async () => {
    await open();
    await screen.findByText('rival_student');

    expect(latestOnMessage).not.toBeNull();
    act(() => {
      // A real backend message never carries `code` (see DuelSocketMessage) --
      // this adds one anyway, bypassing the type system, to prove the
      // component itself has no rendering path for it, not just that the
      // type declaration omits it. Distinct from the student's own starter
      // code text so this can't coincidentally pass by matching the
      // student's own editor instead of an opponent-code surface that
      // shouldn't exist.
      latestOnMessage!({
        type: 'opponent_progress',
        passed_count: 2,
        total_count: 5,
        code: 'SECRET_OPPONENT_CODE',
      } as unknown as DuelSocketMessage);
    });

    await waitFor(() => {
      expect(screen.getByText('2/5')).toBeInTheDocument();
    });
    expect(screen.queryByText(/SECRET_OPPONENT_CODE/)).not.toBeInTheDocument();
  });

  it('shows the opponent-disconnected indicator when the socket reports it', async () => {
    await open();
    await screen.findByText('rival_student');

    act(() => {
      latestOnMessage!({ type: 'opponent_disconnected' });
    });
    expect(await screen.findByText('Offline')).toBeInTheDocument();
  });

  it('submits the current code and shows a win overlay when the submission wins', async () => {
    mockedDuelsApi.submit.mockResolvedValue({
      is_correct: true,
      passed_count: 3,
      total_count: 3,
      won: true,
      duel_status: 'completed',
      winner_user_id: 1,
    });

    await open();
    await screen.findByText('rival_student');

    fireEvent.click(screen.getByTestId('duel-submit'));

    await waitFor(() => expect(mockedDuelsApi.submit).toHaveBeenCalledWith(42, expect.any(String)));
    expect(await screen.findByText('You won!')).toBeInTheDocument();
  });

  it('shows the opponent-won overlay when a duel_ended broadcast names the opponent', async () => {
    await open();
    await screen.findByText('rival_student');

    act(() => {
      latestOnMessage!({ type: 'duel_ended', winner_user_id: 2, reason: 'solved' });
    });

    expect(await screen.findByText("Your opponent solved it first")).toBeInTheDocument();
  });
});
