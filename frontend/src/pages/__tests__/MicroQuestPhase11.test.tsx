import { describe, it, expect, vi, beforeEach } from 'vitest';
import { cleanup, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockProfile } from '../../test/setup.tsx';
import {
  mockFillBlankLesson,
  mockOrderingLesson,
  questProgress,
  questSubmitResponse,
} from '../../test/microQuestFixtures';
import { authApi, lessonsApi, exercisesApi } from '../../api/services';

/**
 * Phase 11 adds ten lessons, two of which exercise the Micro-Quest Quest
 * stage with exercise types no earlier Micro-Quest ever used: fill_blank
 * (lesson 15) and ordering (lesson 32). Everything else about the flow —
 * Hook, Blueprint, persistence, Quest Clear — is exhaustively covered
 * already by the Phase 9/10 suites against the exercise types they did use
 * (code_writing, multiple_choice, prediction, debugging); this file only
 * proves the two genuinely new combinations work through the same,
 * unmodified MicroQuestLesson/ExercisePanel/ExerciseAnswerPanel path.
 */

const STUDENT = {
  id: 41,
  email: 'sara@example.com',
  username: 'sara',
  preferred_language: 'en',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
};

function signedInAs(user: typeof STUDENT) {
  authApi.getMe.mockResolvedValue(user);
  authApi.getProfile.mockResolvedValue({ ...mockProfile, user_id: user.id });
}

async function openLesson(lessonId: string) {
  return renderWithProviders(null as never, {
    initialLanguage: 'en',
    authToken: 'a-token',
    lessonId,
  });
}

describe('Micro-Quest over a fill_blank exercise (lesson 15)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs(STUDENT);
    lessonsApi.start.mockResolvedValue(questProgress({ lesson_id: 15 }));
    lessonsApi.getById.mockResolvedValue(mockFillBlankLesson);
    lessonsApi.getProgress.mockResolvedValue(questProgress({ lesson_id: 15 }));
  });

  async function reachQuest(user: ReturnType<typeof userEvent.setup>) {
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    await waitFor(() => expect(screen.getByTestId('spot-bug-statements')).toBeInTheDocument());
    await user.click(screen.getByTestId('spot-bug-statement-editable').querySelector('input')!);
    await user.click(screen.getByTestId('blueprint-check'));
    await user.click(await screen.findByTestId('blueprint-continue'));
  }

  it('renders the fill_blank answer widget in the Quest stage', async () => {
    const user = userEvent.setup();
    await openLesson('15');
    await reachQuest(user);

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    expect(screen.getByTestId('fill-blank')).toBeInTheDocument();
    expect(screen.getAllByRole('textbox').length).toBeGreaterThanOrEqual(3);
    // Not a code exercise: no editor/terminal chrome.
    expect(screen.queryByTestId('terminal-panel')).not.toBeInTheDocument();
  });

  it('submits the three blanks through the same exercise API and shows Quest Clear', async () => {
    exercisesApi.submit.mockResolvedValue(
      questSubmitResponse({
        is_correct: true,
        xp_earned: 10,
        is_completed: true,
        lesson_completed: true,
      }),
    );
    const user = userEvent.setup();
    await openLesson('15');
    await reachQuest(user);

    const textboxes = screen.getAllByRole('textbox');
    await user.type(textboxes[0], '10');
    await user.type(textboxes[1], '20');
    await user.type(textboxes[2], 'blue');
    await user.click(screen.getByTestId('submit-answer'));

    await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
    const [exerciseId, payload] = exercisesApi.submit.mock.calls[0];
    expect(exerciseId).toBe(1526);
    expect(payload.blanks).toEqual(['10', '20', 'blue']);

    expect(await screen.findByTestId('quest-clear')).toBeInTheDocument();
    expect(screen.getByTestId('quest-clear-xp')).toHaveTextContent('10');
  });

  it('does not show Quest Clear when the backend rejects the blanks', async () => {
    exercisesApi.submit.mockResolvedValue(questSubmitResponse({ is_correct: false, xp_earned: 0 }));
    const user = userEvent.setup();
    await openLesson('15');
    await reachQuest(user);

    const textboxes = screen.getAllByRole('textbox');
    await user.type(textboxes[0], '1');
    await user.type(textboxes[1], '2');
    await user.type(textboxes[2], 'green');
    await user.click(screen.getByTestId('submit-answer'));

    await screen.findByTestId('exercise-result');
    expect(screen.queryByTestId('quest-clear')).not.toBeInTheDocument();
  });
});

describe('Micro-Quest over an ordering exercise (lesson 32)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs(STUDENT);
    lessonsApi.start.mockResolvedValue(questProgress({ lesson_id: 32 }));
    lessonsApi.getById.mockResolvedValue(mockOrderingLesson);
    lessonsApi.getProgress.mockResolvedValue(questProgress({ lesson_id: 32 }));
  });

  async function reachQuest(user: ReturnType<typeof userEvent.setup>) {
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    await waitFor(() => expect(screen.getByTestId('match-pairs')).toBeInTheDocument());
    for (const id of ['log', 'diff', 'show', 'head_parent']) {
      await user.click(screen.getByTestId(`match-left-${id}`));
      await user.click(screen.getByTestId(`match-right-${id}`));
    }
    await user.click(screen.getByTestId('blueprint-check'));
    await user.click(await screen.findByTestId('blueprint-continue'));
  }

  it('renders the ordering answer widget in the Quest stage, in its starting shuffle', async () => {
    const user = userEvent.setup();
    await openLesson('32');
    await reachQuest(user);

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    const list = screen.getByTestId('ordering-list');
    expect(list).toBeInTheDocument();
    expect(screen.getAllByTestId(/^ordering-item-/)).toHaveLength(4);
  });

  it('submits the reordered option ids through the same exercise API and shows Quest Clear', async () => {
    exercisesApi.submit.mockResolvedValue(
      questSubmitResponse({
        is_correct: true,
        xp_earned: 10,
        is_completed: true,
        lesson_completed: true,
      }),
    );
    const user = userEvent.setup();
    await openLesson('32');
    await reachQuest(user);

    // Move each item into its correct position using the up arrow, the same
    // selection-sort-by-move-up technique the blueprint's own tests use.
    const correctIds = [9001, 9002, 9003, 9004];
    for (let target = 0; target < correctIds.length; target++) {
      for (let guard = 0; guard < correctIds.length + 2; guard++) {
        const item = screen.getByTestId(`ordering-item-${correctIds[target]}`);
        const items = screen.getAllByTestId(/^ordering-item-/);
        const position = items.indexOf(item);
        if (position === target) break;
        await user.click(item.querySelector('button')!); // "move up"
      }
    }

    await user.click(screen.getByTestId('submit-answer'));

    await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
    const [exerciseId, payload] = exercisesApi.submit.mock.calls[0];
    expect(exerciseId).toBe(1543);
    expect(payload.ordered_option_ids).toEqual(correctIds);

    expect(await screen.findByTestId('quest-clear')).toBeInTheDocument();
    expect(screen.getByTestId('quest-clear-xp')).toHaveTextContent('10');
  });

  it('persists the reached Quest stage across a reload', async () => {
    const user = userEvent.setup();
    await openLesson('32');
    await reachQuest(user);
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());

    cleanup();
    await openLesson('32');

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    expect(screen.queryByTestId('match-pairs')).not.toBeInTheDocument();
  });
});
