import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders, mockProfile } from '../../test/setup.tsx';
import { mockMicroQuestLesson, questProgress } from '../../test/microQuestFixtures';
import { questStageKey } from '../../components/microquest/questStage';
import { authApi, lessonsApi } from '../../api/services';

const STUDENT = {
  id: 7,
  email: 'amina@example.com',
  username: 'amina',
  preferred_language: 'en',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
};

/**
 * A 403 from GET /lessons/{id}/progress is the sequence gate, not an answer
 * about this lesson. It used to count as "settled" (`isSuccess || isError`),
 * so the stage machine started on a locked lesson and wrote a resume point
 * for it. The locked *screen* belongs to LessonDetail, which gates on
 * GET /lessons/{id} before this component renders at all -- so what is
 * asserted here is that the quest simply does not start.
 */
describe('Micro-Quest treats a 403 on progress as locked', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    authApi.getMe.mockResolvedValue(STUDENT);
    authApi.getProfile.mockResolvedValue({ ...mockProfile, user_id: STUDENT.id });
    lessonsApi.start.mockResolvedValue(questProgress());
    lessonsApi.getById.mockResolvedValue(mockMicroQuestLesson);
  });

  it('does not settle the stage machine, so no resume point is written', async () => {
    lessonsApi.getProgress.mockRejectedValue({
      response: { status: 403, data: { detail: 'Lesson is locked.' } },
    });

    await renderWithProviders(null as never, {
      initialLanguage: 'en',
      authToken: 'a-token',
      lessonId: String(mockMicroQuestLesson.id),
    });

    const key = questStageKey(String(STUDENT.id), mockMicroQuestLesson.id);
    await waitFor(() => expect(screen.getByTestId('micro-quest')).toBeInTheDocument());
    // Settled would have restored a stage and persisted it; locked must not.
    expect(localStorage.getItem(key)).toBeNull();
  });

  it('still settles on a non-403 failure, which says nothing about access', async () => {
    lessonsApi.getProgress.mockRejectedValue({ response: { status: 500, data: {} } });

    await renderWithProviders(null as never, {
      initialLanguage: 'en',
      authToken: 'a-token',
      lessonId: String(mockMicroQuestLesson.id),
    });

    const key = questStageKey(String(STUDENT.id), mockMicroQuestLesson.id);
    await waitFor(() => expect(localStorage.getItem(key)).not.toBeNull());
  });
});
