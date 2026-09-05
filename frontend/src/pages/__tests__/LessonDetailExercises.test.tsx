import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockLessons } from '../../test/setup.tsx';
import {
  mockMcqLesson,
  mockPredictionLesson,
  mockFillBlankLesson,
  submitResponse,
} from '../../test/mcqFixtures';
import { lessonsApi, exercisesApi } from '../../api/services';

/** Walk past the lesson's content blocks to the first exercise. */
async function goToFirstExercise(user: ReturnType<typeof userEvent.setup>, blockCount: number) {
  for (let i = 0; i < blockCount; i++) {
    const next = await screen.findByTestId('lesson-nav-next');
    await user.click(next);
  }
}

describe('LessonDetail exercise rendering by type', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    lessonsApi.start.mockResolvedValue({ id: 1, lesson_id: 61, status: 'in_progress' });
  });

  describe('multiple choice', () => {
    beforeEach(() => {
      lessonsApi.getById.mockResolvedValue(mockMcqLesson);
    });

    it('renders radio options, not a code editor', async () => {
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '61' });
      await goToFirstExercise(user, 1);

      await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());

      const radios = screen.getAllByRole('radio');
      expect(radios).toHaveLength(4);
      expect(screen.getByText('It extracts values into variables')).toBeInTheDocument();
      expect(screen.getByText('It sorts the array')).toBeInTheDocument();

      // The code editor must not be used for a multiple-choice exercise.
      expect(screen.queryByTestId('answer-panel')).toBeInTheDocument();
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
    });

    it('never receives the correct answer before submitting', async () => {
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '61' });
      await goToFirstExercise(user, 1);
      await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());

      for (const option of mockMcqLesson.exercises[0].options) {
        expect(option).not.toHaveProperty('is_correct');
      }
    });

    it('lets the student select exactly one option', async () => {
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '61' });
      await goToFirstExercise(user, 1);
      await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());

      const radios = screen.getAllByRole('radio') as HTMLInputElement[];
      await user.click(radios[1]);
      expect(radios[1].checked).toBe(true);

      await user.click(radios[3]);
      expect(radios[3].checked).toBe(true);
      expect(radios[1].checked).toBe(false);
    });

    it('submit is disabled until an option is chosen', async () => {
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '61' });
      await goToFirstExercise(user, 1);
      await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());

      expect(screen.getByTestId('submit-answer')).toBeDisabled();
      await user.click(screen.getAllByRole('radio')[0]);
      expect(screen.getByTestId('submit-answer')).toBeEnabled();
    });

    it('submits the selected option id, not code', async () => {
      exercisesApi.submit.mockResolvedValue(submitResponse({ is_correct: true, xp_earned: 10, is_completed: true, feedback: 'Correct answer!' }));
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '61' });
      await goToFirstExercise(user, 1);
      await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());

      await user.click(screen.getAllByRole('radio')[1]);
      await user.click(screen.getByTestId('submit-answer'));

      await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
      const [exerciseId, payload] = exercisesApi.submit.mock.calls[0];
      expect(exerciseId).toBe(601);
      expect(payload.selected_option_id).toBe(9002);
      expect(payload.code).toBeUndefined();
    });

    it('shows a success state with earned XP when the backend says correct', async () => {
      exercisesApi.submit.mockResolvedValue(
        submitResponse({ is_correct: true, xp_earned: 10, is_completed: true, feedback: 'Correct answer!', error: null }),
      );
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '61' });
      await goToFirstExercise(user, 1);
      await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());

      await user.click(screen.getAllByRole('radio')[1]);
      await user.click(screen.getByTestId('submit-answer'));

      const result = await screen.findByTestId('exercise-result');
      expect(result).toHaveTextContent(/correct/i);
      expect(result).toHaveTextContent('10');
      // A solved exercise locks its answer so it cannot be resubmitted by accident.
      expect(screen.getByTestId('submit-answer')).toBeDisabled();
    });

    it('shows an incorrect state with feedback and no XP', async () => {
      exercisesApi.submit.mockResolvedValue(submitResponse());
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '61' });
      await goToFirstExercise(user, 1);
      await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());

      await user.click(screen.getAllByRole('radio')[0]);
      await user.click(screen.getByTestId('submit-answer'));

      const result = await screen.findByTestId('exercise-result');
      expect(result).toHaveTextContent('That is not the right answer.');
      expect(result).not.toHaveTextContent(/\+?10 XP/);
      // Still answerable: an incorrect answer must not lock the exercise.
      expect(screen.getByTestId('submit-answer')).toBeEnabled();
    });
  });

  describe('prediction', () => {
    beforeEach(() => {
      lessonsApi.getById.mockResolvedValue(mockPredictionLesson);
    });

    it('renders a prediction textarea and submits the typed answer', async () => {
      exercisesApi.submit.mockResolvedValue(submitResponse({ is_correct: true, xp_earned: 10 }));
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '62' });
      await goToFirstExercise(user, 1);

      await waitFor(() => expect(screen.getByTestId('prediction')).toBeInTheDocument());
      const box = screen.getByRole('textbox');
      await user.type(box, 'Line 1');
      await user.click(screen.getByTestId('submit-answer'));

      await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
      const [, payload] = exercisesApi.submit.mock.calls[0];
      expect(payload.answer).toBe('Line 1');
      expect(payload.selected_option_id).toBeUndefined();
    });
  });

  describe('fill in the blank', () => {
    beforeEach(() => {
      lessonsApi.getById.mockResolvedValue(mockFillBlankLesson);
    });

    it('renders one input per blank and submits them in order', async () => {
      exercisesApi.submit.mockResolvedValue(submitResponse({ is_correct: true, xp_earned: 10 }));
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '63' });
      await goToFirstExercise(user, 1);

      await waitFor(() => expect(screen.getByTestId('fill-blank')).toBeInTheDocument());
      const inputs = screen.getAllByRole('textbox') as HTMLInputElement[];
      expect(inputs).toHaveLength(2);

      await user.type(inputs[0], 'Amine');
      await user.type(inputs[1], '19');
      await user.click(screen.getByTestId('submit-answer'));

      await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
      const [, payload] = exercisesApi.submit.mock.calls[0];
      expect(payload.blanks).toEqual(['Amine', '19']);
    });
  });

  describe('code exercises are unchanged', () => {
    it('still renders the code editor with Run and Submit', async () => {
      lessonsApi.getById.mockResolvedValue(mockLessons[0]);
      const user = userEvent.setup();
      await renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });

      await goToFirstExercise(user, mockLessons[0].blocks.length);

      await waitFor(() => expect(screen.queryByTestId('answer-panel')).not.toBeInTheDocument());
      expect(screen.getByTestId('terminal-panel')).toBeInTheDocument();
      // The editor toolbar and the button row both expose Run, hence getAll.
      expect(screen.getAllByRole('button', { name: /run code/i }).length).toBeGreaterThan(0);
    });
  });
});

describe('Exercise answer UI internationalization', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    lessonsApi.start.mockResolvedValue({ id: 1, lesson_id: 61, status: 'in_progress' });
    lessonsApi.getById.mockResolvedValue(mockMcqLesson);
  });

  it.each([
    ['en', /submit answer/i],
    ['fr', /valider la réponse/i],
    ['ar', /إرسال الإجابة/],
  ])('renders the submit button in %s', async (language, label) => {
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: language, lessonId: '61' });
    await goToFirstExercise(user, 1);

    await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());
    expect(screen.getByTestId('submit-answer')).toHaveTextContent(label);
  });

  it('renders every option and control in Arabic', async () => {
    // document.dir is set by the app shell, which this page-level render does
    // not mount; the real RTL document is asserted in the Playwright i18n spec.
    const user = userEvent.setup();
    await renderWithProviders(null, { initialLanguage: 'ar', lessonId: '61' });
    await goToFirstExercise(user, 1);

    await waitFor(() => expect(screen.getByTestId('mcq-options')).toBeInTheDocument());
    expect(screen.getAllByRole('radio')).toHaveLength(4);
    expect(screen.getByTestId('submit-answer')).toHaveTextContent(/إرسال الإجابة/);
    // Option text still renders (these options are English-only in the fixture).
    expect(screen.getByText('It sorts the array')).toBeInTheDocument();
  });
});
