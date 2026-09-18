import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DuelLobby } from '../DuelLobby';
import { renderWithProviders } from '../../test/setup.tsx';
import { duelsApi } from '../../api/services';

const mockedApi = vi.mocked(duelsApi);

describe('DuelLobby', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows a difficulty picker with no active queue', async () => {
    await renderWithProviders(<DuelLobby />);
    expect(await screen.findByTestId('duel-lobby-join-beginner')).toBeInTheDocument();
    expect(screen.getByTestId('duel-lobby-join-intermediate')).toBeInTheDocument();
    expect(screen.getByTestId('duel-lobby-join-advanced')).toBeInTheDocument();
  });

  it('joins the queue and shows a waiting state when no opponent is found yet', async () => {
    const user = userEvent.setup();
    mockedApi.joinQueue.mockResolvedValue({ status: 'waiting', duel_id: null });
    mockedApi.queueStatus.mockResolvedValue({ status: 'waiting', duel_id: null });

    await renderWithProviders(<DuelLobby />);
    await user.click(await screen.findByTestId('duel-lobby-join-beginner'));

    expect(await screen.findByRole('status')).toHaveTextContent('Beginner');
    expect(mockedApi.joinQueue).toHaveBeenCalledWith('beginner');
  });

  it('lets the student cancel out of the queue back to the picker', async () => {
    const user = userEvent.setup();
    mockedApi.joinQueue.mockResolvedValue({ status: 'waiting', duel_id: null });
    mockedApi.queueStatus.mockResolvedValue({ status: 'waiting', duel_id: null });
    mockedApi.cancelQueue.mockResolvedValue({ status: 'idle', duel_id: null });

    await renderWithProviders(<DuelLobby />);
    await user.click(await screen.findByTestId('duel-lobby-join-intermediate'));
    await screen.findByRole('status');

    await user.click(screen.getByTestId('duel-lobby-cancel'));

    await waitFor(() => expect(mockedApi.cancelQueue).toHaveBeenCalled());
    expect(await screen.findByTestId('duel-lobby-join-beginner')).toBeInTheDocument();
  });

  it('shows an error message when joining fails', async () => {
    const user = userEvent.setup();
    mockedApi.joinQueue.mockRejectedValue({ response: { data: { detail: 'No duel problems are available yet.' } } });

    await renderWithProviders(<DuelLobby />);
    await user.click(await screen.findByTestId('duel-lobby-join-advanced'));

    expect(await screen.findByRole('alert')).toHaveTextContent('No duel problems are available yet.');
  });
});
