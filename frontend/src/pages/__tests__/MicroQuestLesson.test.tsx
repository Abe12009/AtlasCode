import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../test/setup.tsx';
import { mockMicroQuestLesson, questSubmitResponse } from '../../test/microQuestFixtures';
import { lessonsApi, exercisesApi } from '../../api/services';

async function passHook(user: ReturnType<typeof userEvent.setup>) {
  await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
  await user.click(screen.getByTestId('hook-continue'));
}

/** Puts the blueprint steps in the correct order via the up/down controls,
 * whatever their starting (shuffled) arrangement. Selection-sort by
 * repeatedly moving the step that belongs at each position up into place;
 * moving one step up only swaps it with its immediate neighbour, so this
 * converges regardless of the starting shuffle. */
async function solveBlueprint(user: ReturnType<typeof userEvent.setup>) {
  await waitFor(() => expect(screen.getByTestId('blueprint')).toBeInTheDocument());
  const correctOrder = ['init', 'visit', 'decide', 'update'];

  for (let target = 0; target < correctOrder.length; target++) {
    for (let guard = 0; guard < correctOrder.length + 2; guard++) {
      const item = screen.getByTestId(`blueprint-step-${correctOrder[target]}`);
      const position = Number(item.getAttribute('data-position'));
      if (position === target) break;
      const moveUpButton = item.querySelector('button') as HTMLButtonElement;
      await user.click(moveUpButton);
    }
  }
  await user.click(screen.getByTestId('blueprint-check'));
}

describe('MicroQuestLesson', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    lessonsApi.start.mockResolvedValue({ id: 1, lesson_id: 9, status: 'in_progress' });
    lessonsApi.getById.mockResolvedValue(mockMicroQuestLesson);
  });

  it('renders the Local Hook first, with a real-world scenario and a challenge', async () => {
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });

    const hook = await screen.findByTestId('quest-hook');
    expect(hook).toHaveTextContent(/even-numbered locker/i);
    expect(hook).toHaveTextContent(/add up only the numbers it wants/i);
    expect(hook).toHaveTextContent(/combine a loop with a condition/i);
  });

  it('shows the progress indicator with Hook as the current stage', async () => {
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await waitFor(() => expect(screen.getByTestId('quest-progress')).toBeInTheDocument());
    expect(screen.getByTestId('quest-stage-hook')).toHaveAttribute('data-status', 'current');
    expect(screen.getByTestId('quest-stage-blueprint')).toHaveAttribute('data-status', 'upcoming');
  });

  it('advances to the Blueprint stage after the hook', async () => {
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);

    await waitFor(() => expect(screen.getByTestId('blueprint')).toBeInTheDocument());
    expect(screen.getByTestId('quest-stage-blueprint')).toHaveAttribute('data-status', 'current');
    expect(screen.getByTestId('quest-stage-hook')).toHaveAttribute('data-status', 'done');
  });

  it('the blueprint has four orderable steps and a check button', async () => {
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);

    await waitFor(() => expect(screen.getByTestId('blueprint-steps')).toBeInTheDocument());
    expect(screen.getByText('Start a total at zero')).toBeInTheDocument();
    expect(screen.getByText('If it is, add it to the total')).toBeInTheDocument();
    expect(screen.getByTestId('blueprint-check')).toBeInTheDocument();
  });

  it('gives feedback and does not advance on an incorrect blueprint order', async () => {
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);
    await waitFor(() => expect(screen.getByTestId('blueprint')).toBeInTheDocument());

    // The steps start shuffled (never already correct), so checking immediately
    // must fail.
    await user.click(screen.getByTestId('blueprint-check'));

    const feedback = await screen.findByTestId('blueprint-feedback');
    expect(feedback).toHaveTextContent(/not quite/i);
    // No "continue to quest" button yet — the puzzle is not solved.
    expect(screen.queryByTestId('blueprint-continue')).not.toBeInTheDocument();
    // The quest exercise itself must not appear yet either.
    expect(screen.queryByTestId('quest-stage')).not.toBeInTheDocument();
  });

  it('unlocks the quest once the blueprint is arranged correctly', async () => {
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);
    await solveBlueprint(user);

    const feedback = await screen.findByTestId('blueprint-feedback');
    expect(feedback).toHaveTextContent(/pattern/i);
    const continueButton = await screen.findByTestId('blueprint-continue');

    await user.click(continueButton);
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    expect(screen.getByTestId('quest-stage-quest')).toHaveAttribute('data-status', 'current');
  });

  it('shows the real exercise (code editor) after the blueprint, with the exam tip', async () => {
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);
    await solveBlueprint(user);
    await user.click(await screen.findByTestId('blueprint-continue'));

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    expect(screen.getByText(/sum of all even numbers/i)).toBeInTheDocument();
    expect(screen.getByTestId('terminal-panel')).toBeInTheDocument();
    expect(screen.getByTestId('exam-tip')).toHaveTextContent(/indented under a for or if/i);
  });

  it('submits through the existing exercise submission API, unmodified', async () => {
    exercisesApi.submit.mockResolvedValue(
      questSubmitResponse({ is_correct: true, xp_earned: 15, is_completed: true, lesson_completed: true }),
    );
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);
    await solveBlueprint(user);
    await user.click(await screen.findByTestId('blueprint-continue'));
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /submit solution/i }));

    await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
    const [exerciseId, payload] = exercisesApi.submit.mock.calls[0];
    expect(exerciseId).toBe(918);
    expect(payload.exercise_id).toBe(918);
  });

  it('shows Quest Clear with the exact XP the backend returned, after a correct submission', async () => {
    exercisesApi.submit.mockResolvedValue(
      questSubmitResponse({ is_correct: true, xp_earned: 15, is_completed: true, lesson_completed: true }),
    );
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);
    await solveBlueprint(user);
    await user.click(await screen.findByTestId('blueprint-continue'));
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /submit solution/i }));

    const clear = await screen.findByTestId('quest-clear');
    expect(clear).toHaveTextContent(/quest clear/i);
    expect(screen.getByTestId('quest-clear-xp')).toHaveTextContent('15');
    expect(screen.getByTestId('quest-stage-complete')).toHaveAttribute('data-status', 'current');
  });

  it('does not show Quest Clear on an incorrect submission', async () => {
    exercisesApi.submit.mockResolvedValue(questSubmitResponse({ is_correct: false, xp_earned: 0 }));
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '9' });
    await passHook(user);
    await solveBlueprint(user);
    await user.click(await screen.findByTestId('blueprint-continue'));
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /submit solution/i }));

    await screen.findByTestId('exercise-result');
    expect(screen.queryByTestId('quest-clear')).not.toBeInTheDocument();
  });
});

describe('MicroQuestLesson internationalization', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    lessonsApi.start.mockResolvedValue({ id: 1, lesson_id: 9, status: 'in_progress' });
    lessonsApi.getById.mockResolvedValue(mockMicroQuestLesson);
  });

  it('renders the hook in French', async () => {
    await renderWithProviders(null, { initialLanguage: 'fr', lessonId: '9' });
    const hook = await screen.findByTestId('quest-hook');
    expect(hook).toHaveTextContent(/casiers pairs/i);
    expect(hook).toHaveTextContent(/additionner seulement les nombres voulus/i);
  });

  it('renders the hook in Arabic with RTL-appropriate content', async () => {
    await renderWithProviders(null, { initialLanguage: 'ar', lessonId: '9' });
    const hook = await screen.findByTestId('quest-hook');
    expect(hook.textContent).toMatch(/[؀-ۿ]/);
  });

  it('translates the progress stage labels', async () => {
    await renderWithProviders(null, { initialLanguage: 'fr', lessonId: '9' });
    await waitFor(() => expect(screen.getByTestId('quest-progress')).toBeInTheDocument());
    expect(screen.getByTestId('quest-progress')).toHaveTextContent(/mise en situation/i);
  });
});
