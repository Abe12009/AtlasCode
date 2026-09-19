import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../test/setup.tsx';
import { GitQuestPanel } from '../GitQuestPanel';
import { gitQuestApi } from '../../../api/services';
import type { Exercise, GitQuestState } from '../../../types';

const mockedApi = vi.mocked(gitQuestApi);

const EMPTY_STATE: GitQuestState = {
  commits: {},
  branches: {},
  remote_branches: {},
  head: null,
  working_files: {},
  staged_files: {},
  merge_in_progress: null,
  initialized: false,
};

const EXERCISE: Exercise = {
  id: 99,
  exercise_type: 'git_quest',
  order: 1,
  xp_reward: 40,
  starter_code: JSON.stringify(EMPTY_STATE),
  translations: [],
  options: [],
};

/** A tiny fake of just enough of the real engine's behavior (init + edit)
 * to drive the panel's UI without re-implementing the whole simulator. */
function fakeExecute(state: GitQuestState, action: { kind: string; value?: string; file?: string; content?: string }) {
  if (action.kind === 'command' && action.value === 'git init') {
    const next: GitQuestState = { ...state, initialized: true, branches: { main: null }, head: { branch: 'main' } };
    return Promise.resolve({ state: next, output: 'Initialized empty Git repository.', error: null });
  }
  if (action.kind === 'edit' && action.file) {
    const next: GitQuestState = { ...state, working_files: { ...state.working_files, [action.file]: action.content ?? '' } };
    return Promise.resolve({ state: next, output: `Edited ${action.file}.`, error: null });
  }
  return Promise.resolve({ state, output: '', error: `git: unsupported in test: ${action.value}` });
}

beforeEach(() => {
  mockedApi.execute.mockReset();
  mockedApi.execute.mockImplementation((state, action) => fakeExecute(state, action));
});

describe('GitQuestPanel', () => {
  it('runs a typed command and shows its output in the terminal transcript', async () => {
    const user = userEvent.setup();
    await renderWithProviders(<GitQuestPanel exercise={EXERCISE} onSubmit={vi.fn()} isSubmitting={false} />);

    const input = screen.getByTestId('git-terminal-input');
    await user.type(input, 'git init');
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(screen.getByText('Initialized empty Git repository.')).toBeInTheDocument();
    });
    expect(screen.getByTestId('git-terminal-history')).toHaveTextContent('$ git init');
  });

  it('creates a new file and edits it via the file editor', async () => {
    const user = userEvent.setup();
    await renderWithProviders(<GitQuestPanel exercise={EXERCISE} onSubmit={vi.fn()} isSubmitting={false} />);

    await user.click(screen.getByTestId('git-new-file-button'));
    await user.type(screen.getByTestId('git-new-file-input'), 'hello.py');
    await user.click(screen.getByText('Create'));

    const textarea = await screen.findByTestId('git-file-editor-textarea');
    await user.clear(textarea);
    await user.type(textarea, "print('hi')");
    await user.click(screen.getByTestId('git-file-save-button'));

    await waitFor(() => {
      expect(mockedApi.execute).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({ kind: 'edit', file: 'hello.py' })
      );
    });
  });

  it('submits the full action transcript, not just the current state', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    await renderWithProviders(<GitQuestPanel exercise={EXERCISE} onSubmit={onSubmit} isSubmitting={false} />);

    await user.type(screen.getByTestId('git-terminal-input'), 'git init');
    await user.keyboard('{Enter}');
    await waitFor(() => expect(screen.getByText('Initialized empty Git repository.')).toBeInTheDocument());

    await user.click(screen.getByTestId('git-quest-submit'));

    expect(onSubmit).toHaveBeenCalledWith({
      exerciseId: 99,
      answer: JSON.stringify([{ kind: 'command', value: 'git init' }]),
    });
  });

  it('disables submit until at least one action has been taken', async () => {
    await renderWithProviders(<GitQuestPanel exercise={EXERCISE} onSubmit={vi.fn()} isSubmitting={false} />);
    expect(screen.getByTestId('git-quest-submit')).toBeDisabled();
  });

  it('reset clears the transcript back to the starter state', async () => {
    const user = userEvent.setup();
    await renderWithProviders(<GitQuestPanel exercise={EXERCISE} onSubmit={vi.fn()} isSubmitting={false} />);

    await user.type(screen.getByTestId('git-terminal-input'), 'git init');
    await user.keyboard('{Enter}');
    await waitFor(() => expect(screen.getByTestId('git-quest-submit')).not.toBeDisabled());

    await user.click(screen.getByText('Reset'));
    expect(screen.getByTestId('git-quest-submit')).toBeDisabled();
    expect(screen.getByTestId('git-terminal-history')).not.toHaveTextContent('$ git init');
  });
});
