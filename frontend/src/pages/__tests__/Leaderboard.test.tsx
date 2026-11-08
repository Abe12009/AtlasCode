import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Leaderboard } from '../Leaderboard';
import { renderWithProviders, mockUser, mockProfile } from '../../test/setup.tsx';
import { authApi, leaderboardApi } from '../../api/services';
import type { LeaderboardResponse } from '../../types';

const mockedLeaderboard = vi.mocked(leaderboardApi);
const mockedAuth = vi.mocked(authApi);

function entry(rank: number, username: string, xp: number, level = 1) {
  return { rank, username, avatar_type: 'upload', level, xp };
}

function board(overrides: Partial<LeaderboardResponse> = {}): LeaderboardResponse {
  return {
    entries: [entry(1, 'ada', 9000, 9), entry(2, 'grace', 4200, 5), entry(3, 'alan', 100, 2)],
    me: { rank: 12, xp: 80, level: 1, is_listed: false },
    next_cursor: null,
    ...overrides,
  };
}

/** The page reads the signed-in user from AuthContext, which fetches it. */
function signedInAs(username: string, visibility: 'public' | 'private') {
  mockedAuth.getMe.mockResolvedValue({ ...mockUser, username, profile_visibility: visibility } as any);
  mockedAuth.getProfile.mockResolvedValue(mockProfile as any);
}

async function renderBoard(language = 'en') {
  return renderWithProviders(<Leaderboard />, { initialLanguage: language, authToken: 'a-token' });
}

describe('Leaderboard page states', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs('testuser', 'private');
  });

  it('shows a loading state before the first page arrives', async () => {
    mockedLeaderboard.get.mockImplementation(() => new Promise(() => {}));

    await renderBoard();

    await waitFor(() => {
      expect(screen.getByTestId('leaderboard-loading')).toBeInTheDocument();
    });
  });

  it('renders the ranked rows as a list', async () => {
    mockedLeaderboard.get.mockResolvedValue(board());

    await renderBoard();

    await waitFor(() => expect(screen.getByText('ada')).toBeInTheDocument());
    const list = screen.getByRole('list', { name: /leaderboard/i });
    const rows = within(list).getAllByRole('listitem');
    expect(rows).toHaveLength(3);
    expect(rows[0]).toHaveTextContent('ada');
    expect(rows[0]).toHaveTextContent('1');
    expect(rows[2]).toHaveTextContent('alan');
  });

  it('shows an empty state when nobody has joined', async () => {
    mockedLeaderboard.get.mockResolvedValue(board({ entries: [] }));

    await renderBoard();

    await waitFor(() => {
      expect(screen.getByTestId('leaderboard-empty')).toBeInTheDocument();
    });
    expect(screen.getByTestId('leaderboard-empty')).toHaveTextContent(/Nobody has joined/i);
  });

  it('shows an error state with a retry that refetches', async () => {
    mockedLeaderboard.get.mockRejectedValue({ response: { status: 500 } });

    await renderBoard();

    await waitFor(() => {
      expect(screen.getByTestId('leaderboard-error')).toBeInTheDocument();
    });

    mockedLeaderboard.get.mockResolvedValue(board());
    await userEvent.click(screen.getByRole('button', { name: /try again/i }));

    await waitFor(() => expect(screen.getByText('ada')).toBeInTheDocument());
  });

  it('always shows the own-rank card, listed or not', async () => {
    mockedLeaderboard.get.mockResolvedValue(board());

    await renderBoard();

    await waitFor(() => {
      expect(screen.getByTestId('my-rank')).toHaveTextContent('#12');
    });
    expect(screen.getByTestId('listing-status')).toHaveTextContent(/not on the leaderboard/i);
  });
});

describe('Leaderboard own row', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs('grace', 'public');
  });

  it('marks the caller’s own row with aria-current', async () => {
    mockedLeaderboard.get.mockResolvedValue(
      board({ me: { rank: 2, xp: 4200, level: 5, is_listed: true } }),
    );

    await renderBoard();

    await waitFor(() => expect(screen.getByTestId('leaderboard-row-me')).toBeInTheDocument());
    const mine = screen.getByTestId('leaderboard-row-me');
    expect(mine).toHaveAttribute('aria-current', 'true');
    expect(mine).toHaveTextContent('grace');
    // Nobody else is marked.
    expect(document.querySelectorAll('[aria-current]')).toHaveLength(1);
  });
});

describe('Leaderboard joining and leaving', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockedLeaderboard.get.mockResolvedValue(board());
  });

  it('explains exactly what joining reveals, then joins via profile visibility', async () => {
    signedInAs('testuser', 'private');
    mockedAuth.updateMe.mockResolvedValue({
      ...mockUser,
      username: 'testuser',
      profile_visibility: 'public',
    } as any);

    await renderBoard();

    await waitFor(() => expect(screen.getByTestId('join-leaderboard')).toBeInTheDocument());
    // The four fields the endpoint actually returns, named before the tap.
    const card = screen.getByTestId('my-rank-card');
    expect(card).toHaveTextContent(/username, avatar, level and XP/i);
    expect(card).toHaveTextContent(/Nothing else is shared/i);

    await userEvent.click(screen.getByTestId('join-leaderboard'));

    await waitFor(() => {
      expect(mockedAuth.updateMe).toHaveBeenCalledWith({ profile_visibility: 'public' });
    });
  });

  it('offers a way to leave once listed', async () => {
    signedInAs('grace', 'public');
    mockedLeaderboard.get.mockResolvedValue(
      board({ me: { rank: 2, xp: 4200, level: 5, is_listed: true } }),
    );
    mockedAuth.updateMe.mockResolvedValue({
      ...mockUser,
      username: 'grace',
      profile_visibility: 'private',
    } as any);

    await renderBoard();

    await waitFor(() => expect(screen.getByTestId('leave-leaderboard')).toBeInTheDocument());
    expect(screen.queryByTestId('join-leaderboard')).not.toBeInTheDocument();

    await userEvent.click(screen.getByTestId('leave-leaderboard'));

    await waitFor(() => {
      expect(mockedAuth.updateMe).toHaveBeenCalledWith({ profile_visibility: 'private' });
    });
  });

  it('surfaces a failure to join instead of silently doing nothing', async () => {
    signedInAs('testuser', 'private');
    mockedAuth.updateMe.mockRejectedValue({ response: { status: 500 } });

    await renderBoard();

    await waitFor(() => expect(screen.getByTestId('join-leaderboard')).toBeInTheDocument());
    await userEvent.click(screen.getByTestId('join-leaderboard'));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });
});

describe('Leaderboard pagination', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs('testuser', 'private');
  });

  it('loads the next page with the cursor and appends it', async () => {
    mockedLeaderboard.get.mockResolvedValueOnce(board({ next_cursor: 'CURSOR_2' }));

    await renderBoard();
    await waitFor(() => expect(screen.getByTestId('leaderboard-load-more')).toBeInTheDocument());

    mockedLeaderboard.get.mockResolvedValueOnce(
      board({ entries: [entry(4, 'linus', 50)], next_cursor: null }),
    );
    await userEvent.click(screen.getByTestId('leaderboard-load-more'));

    await waitFor(() => expect(screen.getByText('linus')).toBeInTheDocument());
    expect(mockedLeaderboard.get).toHaveBeenLastCalledWith({ limit: 25, cursor: 'CURSOR_2' });
    // Appended, not replaced.
    expect(screen.getByText('ada')).toBeInTheDocument();
    // No cursor left: the button retires and the depth notice takes over.
    expect(screen.queryByTestId('leaderboard-load-more')).not.toBeInTheDocument();
  });

  it('shows no load-more button when the first page is the whole board', async () => {
    mockedLeaderboard.get.mockResolvedValue(board({ next_cursor: null }));

    await renderBoard();

    await waitFor(() => expect(screen.getByText('ada')).toBeInTheDocument());
    expect(screen.queryByTestId('leaderboard-load-more')).not.toBeInTheDocument();
  });
});

describe('Leaderboard translations', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs('testuser', 'private');
    mockedLeaderboard.get.mockResolvedValue(board());
  });

  const expected: Record<string, { title: RegExp; join: RegExp }> = {
    en: { title: /Leaderboard/, join: /Join the leaderboard/ },
    fr: { title: /Classement/, join: /Rejoindre le classement/ },
    ar: { title: /المتصدرين/, join: /انضم إلى قائمة المتصدرين/ },
  };

  for (const [language, labels] of Object.entries(expected)) {
    it(`renders its labels in ${language}`, async () => {
      await renderBoard(language);

      await waitFor(() => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(labels.title);
      });
      expect(screen.getByTestId('join-leaderboard')).toHaveTextContent(labels.join);
      // No raw i18n keys leaked into the page.
      expect(document.body.textContent).not.toMatch(/leaderboard\.[a-z_]+/);
    });
  }
});
