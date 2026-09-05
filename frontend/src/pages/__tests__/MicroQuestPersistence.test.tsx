import { describe, it, expect, vi, beforeEach } from 'vitest';
import { cleanup, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockProfile } from '../../test/setup.tsx';
import {
  mockMicroQuestLesson,
  mockMatchPairsLesson,
  mockSpotTheBugLesson,
  questProgress,
  questSubmitResponse,
} from '../../test/microQuestFixtures';
import { questStageKey } from '../../components/microquest/questStage';
import { authApi, lessonsApi, exercisesApi } from '../../api/services';

const STUDENT = {
  id: 7,
  email: 'amina@example.com',
  username: 'amina',
  preferred_language: 'en',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
};
const OTHER_STUDENT = { ...STUDENT, id: 8, email: 'yassine@example.com', username: 'yassine' };

/** Renders the lesson the way the app does for a signed-in student. Calling it
 * again after cleanup() is this suite's stand-in for a browser reload: the
 * component tree is thrown away and rebuilt, and only what the backend and
 * localStorage hold survives. */
async function openLesson(options: { lessonId?: string; language?: string } = {}) {
  return renderWithProviders(null as never, {
    initialLanguage: options.language ?? 'en',
    authToken: 'a-token',
    lessonId: options.lessonId ?? '9',
  });
}

function signedInAs(user: typeof STUDENT) {
  authApi.getMe.mockResolvedValue(user);
  authApi.getProfile.mockResolvedValue({ ...mockProfile, user_id: user.id });
}

async function solveOrderStepsBlueprint(user: ReturnType<typeof userEvent.setup>) {
  await waitFor(() => expect(screen.getByTestId('blueprint')).toBeInTheDocument());
  const correctOrder = ['init', 'visit', 'decide', 'update'];
  for (let target = 0; target < correctOrder.length; target++) {
    for (let guard = 0; guard < correctOrder.length + 2; guard++) {
      const item = screen.getByTestId(`blueprint-step-${correctOrder[target]}`);
      if (Number(item.getAttribute('data-position')) === target) break;
      await user.click(item.querySelector('button') as HTMLButtonElement);
    }
  }
  await user.click(screen.getByTestId('blueprint-check'));
}

describe('Micro-Quest stage persistence', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs(STUDENT);
    lessonsApi.start.mockResolvedValue(questProgress());
    lessonsApi.getById.mockResolvedValue(mockMicroQuestLesson);
    lessonsApi.getProgress.mockResolvedValue(questProgress());
  });

  it('returns to the Blueprint after a reload once the student has reached it', async () => {
    const user = userEvent.setup();
    await openLesson();

    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    await waitFor(() =>
      expect(localStorage.getItem(questStageKey('7', 9))).toContain('blueprint'),
    );

    cleanup();
    await openLesson();

    await waitFor(() => expect(screen.getByTestId('blueprint')).toBeInTheDocument());
    expect(screen.queryByTestId('quest-hook')).not.toBeInTheDocument();
    expect(screen.getByTestId('quest-stage-blueprint')).toHaveAttribute('data-status', 'current');
  });

  it('returns to the Quest after a reload, without re-solving the blueprint', async () => {
    const user = userEvent.setup();
    await openLesson();

    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    await solveOrderStepsBlueprint(user);
    await user.click(await screen.findByTestId('blueprint-continue'));
    await waitFor(() => expect(localStorage.getItem(questStageKey('7', 9))).toContain('quest'));

    cleanup();
    await openLesson();

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    expect(screen.getByTestId('quest-stage-quest')).toHaveAttribute('data-status', 'current');
  });

  it('stores only the stage — never the student answer', async () => {
    const user = userEvent.setup();
    await openLesson();
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));

    await waitFor(() => expect(localStorage.getItem(questStageKey('7', 9))).toBeTruthy());
    expect(JSON.parse(localStorage.getItem(questStageKey('7', 9)) as string)).toEqual({
      v: 1,
      stage: 'blueprint',
    });
  });
});

describe('Micro-Quest completion is the backend’s to decide', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs(STUDENT);
    lessonsApi.start.mockResolvedValue(questProgress());
    lessonsApi.getById.mockResolvedValue(mockMicroQuestLesson);
  });

  it('shows Quest Clear on reload when the backend says the lesson is complete', async () => {
    lessonsApi.getProgress.mockResolvedValue(
      questProgress({ status: 'completed', xp_earned: 15, completed_at: '2026-09-04T10:00:00Z' }),
    );
    await openLesson();

    const clear = await screen.findByTestId('quest-clear');
    expect(clear).toHaveTextContent(/quest clear/i);
    expect(screen.getByTestId('quest-clear-xp')).toHaveTextContent('15');
    expect(screen.getByTestId('quest-stage-complete')).toHaveAttribute('data-status', 'current');
  });

  it('still shows it completed after localStorage is cleared', async () => {
    lessonsApi.getProgress.mockResolvedValue(
      questProgress({ status: 'completed', xp_earned: 15 }),
    );
    localStorage.removeItem(questStageKey('7', 9));

    await openLesson();
    expect(await screen.findByTestId('quest-clear')).toBeInTheDocument();
  });

  it('overrides a stale localStorage stage that says the lesson is unfinished', async () => {
    localStorage.setItem(questStageKey('7', 9), JSON.stringify({ v: 1, stage: 'hook' }));
    lessonsApi.getProgress.mockResolvedValue(
      questProgress({ status: 'completed', xp_earned: 15 }),
    );

    await openLesson();
    expect(await screen.findByTestId('quest-clear')).toBeInTheDocument();
    expect(screen.queryByTestId('quest-hook')).not.toBeInTheDocument();
  });

  it('refuses a completion localStorage invents on its own', async () => {
    // Writing "complete" by hand must not conjure a Quest Clear screen, nor an
    // XP figure, for an exercise the backend never graded.
    localStorage.setItem(questStageKey('7', 9), JSON.stringify({ v: 1, stage: 'complete' }));
    lessonsApi.getProgress.mockResolvedValue(questProgress({ status: 'in_progress', xp_earned: 0 }));

    await openLesson();
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    expect(screen.queryByTestId('quest-clear')).not.toBeInTheDocument();
  });

  it('reports the XP the backend banked, not the zero a repeat submission earns', async () => {
    lessonsApi.getProgress.mockResolvedValue(
      questProgress({ status: 'completed', xp_earned: 15 }),
    );
    exercisesApi.submit.mockResolvedValue(
      questSubmitResponse({ is_correct: true, xp_earned: 0, is_completed: true }),
    );
    await openLesson();

    expect(await screen.findByTestId('quest-clear-xp')).toHaveTextContent('15');
  });
});

describe('Micro-Quest storage is scoped to one student and one lesson', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    lessonsApi.start.mockResolvedValue(questProgress());
    lessonsApi.getProgress.mockResolvedValue(questProgress());
  });

  it('does not show one student’s position to the next student on the machine', async () => {
    signedInAs(STUDENT);
    lessonsApi.getById.mockResolvedValue(mockMicroQuestLesson);
    localStorage.setItem(questStageKey('7', 9), JSON.stringify({ v: 1, stage: 'quest' }));

    await openLesson();
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());

    cleanup();
    signedInAs(OTHER_STUDENT);
    await openLesson();

    // The other student starts where every student starts.
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    expect(screen.queryByTestId('quest-stage')).not.toBeInTheDocument();
    // And the first student's position is untouched, waiting for them.
    expect(localStorage.getItem(questStageKey('7', 9))).toContain('quest');
  });

  it('keeps each Micro-Quest lesson on its own position', async () => {
    signedInAs(STUDENT);
    localStorage.setItem(questStageKey('7', 9), JSON.stringify({ v: 1, stage: 'quest' }));

    lessonsApi.getById.mockResolvedValue(mockMatchPairsLesson);
    await openLesson({ lessonId: '12' });

    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    expect(screen.queryByTestId('quest-stage')).not.toBeInTheDocument();
  });
});

describe('Micro-Quest survives a hostile or unavailable localStorage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs(STUDENT);
    lessonsApi.start.mockResolvedValue(questProgress());
    lessonsApi.getById.mockResolvedValue(mockMicroQuestLesson);
    lessonsApi.getProgress.mockResolvedValue(questProgress());
  });

  it.each([
    ['not JSON', 'wat'],
    ['an array', '[]'],
    ['an object with no stage', '{"v":1}'],
    ['a stage that does not exist', '{"v":1,"stage":"banana"}'],
    ['an empty string', ''],
  ])('falls back to the Hook when the stored value is %s', async (_label, raw) => {
    localStorage.setItem(questStageKey('7', 9), raw);

    await openLesson();
    expect(await screen.findByTestId('quest-hook')).toBeInTheDocument();
  });

  it('renders and advances normally when storage throws on every access', async () => {
    const user = userEvent.setup();
    // A browser set to block site data throws on the accessor itself. The
    // token has to keep working, because that is not what is being simulated.
    localStorage.setItem('access_token', 'a-token');
    const realGetItem = Storage.prototype.getItem;
    const getItem = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(function (
      this: Storage,
      key: string,
    ) {
      if (key === 'access_token') return realGetItem.call(this, key);
      throw new DOMException('The operation is insecure.', 'SecurityError');
    });
    const realSetItem = Storage.prototype.setItem;
    const setItem = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(function (
      this: Storage,
      key: string,
      value: string,
    ) {
      if (key === 'access_token') return realSetItem.call(this, key, value);
      throw new DOMException('The operation is insecure.', 'SecurityError');
    });

    try {
      await openLesson();
      await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
      await user.click(screen.getByTestId('hook-continue'));
      expect(await screen.findByTestId('blueprint')).toBeInTheDocument();
    } finally {
      // Restore the two spies only: vi.restoreAllMocks() would also strip the
      // default implementations the shared API mocks rely on.
      getItem.mockRestore();
      setItem.mockRestore();
    }
  });

  it('starts at the Hook when the backend progress request fails outright', async () => {
    lessonsApi.getProgress.mockRejectedValue(new Error('network down'));

    await openLesson();
    expect(await screen.findByTestId('quest-hook')).toBeInTheDocument();
  });
});

describe('Micro-Quest over a match_pairs blueprint and a prediction exercise', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs(STUDENT);
    lessonsApi.start.mockResolvedValue(questProgress({ lesson_id: 12 }));
    lessonsApi.getById.mockResolvedValue(mockMatchPairsLesson);
    lessonsApi.getProgress.mockResolvedValue(questProgress({ lesson_id: 12 }));
  });

  async function reachQuest(user: ReturnType<typeof userEvent.setup>) {
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    await waitFor(() => expect(screen.getByTestId('match-pairs')).toBeInTheDocument());
    for (const id of ['local', 'global', 'parameter', 'return']) {
      await user.click(screen.getByTestId(`match-left-${id}`));
      await user.click(screen.getByTestId(`match-right-${id}`));
    }
    await user.click(screen.getByTestId('blueprint-check'));
    await user.click(await screen.findByTestId('blueprint-continue'));
  }

  it('runs the identical Hook -> Blueprint -> Quest flow', async () => {
    const user = userEvent.setup();
    await openLesson({ lessonId: '12' });
    await reachQuest(user);

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    // A prediction is answered, not run: the answer widget replaces the editor.
    expect(screen.getByTestId('prediction')).toBeInTheDocument();
    expect(screen.queryByTestId('terminal-panel')).not.toBeInTheDocument();
    expect(screen.getByTestId('exam-tip')).toHaveTextContent(/reading a global/i);
  });

  it('submits a prediction through the same exercise API and shows Quest Clear', async () => {
    exercisesApi.submit.mockResolvedValue(
      questSubmitResponse({
        is_correct: true,
        xp_earned: 10,
        is_completed: true,
        lesson_completed: true,
      }),
    );
    const user = userEvent.setup();
    await openLesson({ lessonId: '12' });
    await reachQuest(user);

    await user.type(
      screen.getByLabelText(/your prediction/i),
      'Inside: 20\nOutside: 10',
    );
    await user.click(screen.getByTestId('submit-answer'));

    await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
    const [exerciseId, payload] = exercisesApi.submit.mock.calls[0];
    expect(exerciseId).toBe(1222);
    expect(payload.answer).toBe('Inside: 20\nOutside: 10');

    expect(await screen.findByTestId('quest-clear')).toBeInTheDocument();
    expect(screen.getByTestId('quest-clear-xp')).toHaveTextContent('10');
  });

  it('renders the match_pairs blueprint in French and in Arabic', async () => {
    const user = userEvent.setup();
    await openLesson({ lessonId: '12', language: 'fr' });
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    expect(await screen.findByText('Variable locale')).toBeInTheDocument();

    cleanup();
    localStorage.clear();
    await openLesson({ lessonId: '12', language: 'ar' });
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    expect(await screen.findByText('متغيّر محلي')).toBeInTheDocument();
  });
});

describe('Micro-Quest over a spot_the_bug blueprint and a debugging exercise', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    signedInAs(STUDENT);
    lessonsApi.start.mockResolvedValue(questProgress({ lesson_id: 38 }));
    lessonsApi.getById.mockResolvedValue(mockSpotTheBugLesson);
    lessonsApi.getProgress.mockResolvedValue(questProgress({ lesson_id: 38 }));
  });

  async function reachQuest(user: ReturnType<typeof userEvent.setup>) {
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    await waitFor(() => expect(screen.getByTestId('spot-bug-statements')).toBeInTheDocument());
    await user.click(screen.getByTestId('spot-bug-statement-bound').querySelector('input')!);
    await user.click(screen.getByTestId('blueprint-check'));
    await user.click(await screen.findByTestId('blueprint-continue'));
  }

  it('runs the identical Hook -> Blueprint -> Quest flow with the third blueprint type', async () => {
    const user = userEvent.setup();
    await openLesson({ lessonId: '38' });
    await reachQuest(user);

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    // debugging is a code exercise: the editor and terminal appear, same as code_writing.
    expect(screen.getByTestId('terminal-panel')).toBeInTheDocument();
    expect(screen.getByTestId('exam-tip')).toHaveTextContent(/floor division/i);
  });

  it('does not advance past the blueprint on a wrong statement pick', async () => {
    const user = userEvent.setup();
    await openLesson({ lessonId: '38' });
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    await waitFor(() => expect(screen.getByTestId('spot-bug-statements')).toBeInTheDocument());

    await user.click(screen.getByTestId('spot-bug-statement-sorted').querySelector('input')!);
    await user.click(screen.getByTestId('blueprint-check'));

    expect(await screen.findByTestId('blueprint-feedback')).toHaveTextContent(/actually true/i);
    expect(screen.queryByTestId('blueprint-continue')).not.toBeInTheDocument();
    expect(screen.queryByTestId('quest-stage')).not.toBeInTheDocument();
  });

  it('submits debugging code through the same exercise API and shows Quest Clear', async () => {
    exercisesApi.submit.mockResolvedValue(
      questSubmitResponse({
        is_correct: true,
        xp_earned: 15,
        is_completed: true,
        lesson_completed: true,
      }),
    );
    const user = userEvent.setup();
    await openLesson({ lessonId: '38' });
    await reachQuest(user);

    await user.click(screen.getByRole('button', { name: /submit solution/i }));

    await waitFor(() => expect(exercisesApi.submit).toHaveBeenCalled());
    const [exerciseId] = exercisesApi.submit.mock.calls[0];
    expect(exerciseId).toBe(1349);

    expect(await screen.findByTestId('quest-clear')).toBeInTheDocument();
    expect(screen.getByTestId('quest-clear-xp')).toHaveTextContent('15');
  });

  it('persists the reached stage across a reload, same as every other blueprint type', async () => {
    const user = userEvent.setup();
    await openLesson({ lessonId: '38' });
    await reachQuest(user);
    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());

    cleanup();
    await openLesson({ lessonId: '38' });

    await waitFor(() => expect(screen.getByTestId('quest-stage')).toBeInTheDocument());
    expect(screen.queryByTestId('spot-bug-statements')).not.toBeInTheDocument();
  });

  it('renders the spot_the_bug blueprint in French and in Arabic, code kept LTR', async () => {
    const user = userEvent.setup();
    await openLesson({ lessonId: '38', language: 'fr' });
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    expect(await screen.findByText(/tableau déjà trié/i)).toBeInTheDocument();
    expect(screen.getByTestId('spot-bug-snippet')).toHaveAttribute('dir', 'ltr');

    cleanup();
    localStorage.clear();
    await openLesson({ lessonId: '38', language: 'ar' });
    await waitFor(() => expect(screen.getByTestId('quest-hook')).toBeInTheDocument());
    await user.click(screen.getByTestId('hook-continue'));
    expect(await screen.findByText(/مرتّبة/)).toBeInTheDocument();
    expect(screen.getByTestId('spot-bug-snippet')).toHaveAttribute('dir', 'ltr');
    expect(screen.getByTestId('spot-bug-snippet')).toHaveTextContent('left, right');
  });
});
