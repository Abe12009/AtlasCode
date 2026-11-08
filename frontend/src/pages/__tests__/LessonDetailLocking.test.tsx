import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders, mockLessons } from '../../test/setup.tsx';
import { lessonsApi, coursesApi } from '../../api/services';

const mockedLessons = vi.mocked(lessonsApi);
const mockedCourses = vi.mocked(coursesApi);

/** What axios hands a rejected call. */
function httpError(status: number, detail?: string) {
  return { response: { status, data: detail ? { detail } : {} } };
}

const LOCKED_DETAIL = 'Lesson is locked. Complete the preceding lesson in this course first.';

/** One course whose lesson 2 is locked behind lesson 1 -- the shape
 * GET /courses returns now that it reports real status. */
const catalog = [
  {
    id: 7,
    slug: 'python-basics',
    order: 1,
    difficulty: 'beginner',
    translations: [{ language: 'en', title: 'Python Foundations' }],
    modules: [
      {
        id: 1,
        slug: 'getting-started',
        order: 1,
        translations: [{ language: 'en', title: 'Getting Started' }],
        lessons: [
          { id: 1, slug: 'one', order: 1, difficulty: 'beginner', estimated_minutes: 30, xp_reward: 50, is_project: false, status: 'current', translations: [{ language: 'en', title: 'One' }], blocks: [], exercises: [] },
          { id: 2, slug: 'two', order: 2, difficulty: 'beginner', estimated_minutes: 30, xp_reward: 50, is_project: false, status: 'locked', translations: [{ language: 'en', title: 'Two' }], blocks: [], exercises: [] },
        ],
      },
    ],
  },
];

describe('LessonDetail locked vs not found', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockedLessons.start.mockResolvedValue({} as any);
    mockedCourses.getAll.mockResolvedValue(catalog as any);
  });

  it('renders the locked state, not "not found", when the lesson 403s', async () => {
    mockedLessons.getById.mockRejectedValue(httpError(403, LOCKED_DETAIL));

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '2' });

    await waitFor(() => {
      expect(screen.getByTestId('lesson-locked-title')).toBeInTheDocument();
    });
    expect(screen.getByText(/This lesson is locked/i)).toBeInTheDocument();
    expect(screen.queryByText(/Lesson not found/i)).not.toBeInTheDocument();
  });

  it('offers the course and the lesson that unlocks it', async () => {
    mockedLessons.getById.mockRejectedValue(httpError(403, LOCKED_DETAIL));

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '2' });

    // Resolved from the catalog: lesson 1 is the one in progress, course 7 is
    // the course lesson 2 sits in.
    await waitFor(() => {
      expect(screen.getByTestId('locked-unlocking-lesson')).toHaveAttribute('href', '/app/lessons/1');
    });
    expect(screen.getByTestId('locked-back-to-course')).toHaveAttribute('href', '/app/courses/7');
  });

  it('falls back to the catalog link when the lesson is in no known course', async () => {
    mockedLessons.getById.mockRejectedValue(httpError(403, LOCKED_DETAIL));
    mockedCourses.getAll.mockResolvedValue([] as any);

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '2' });

    await waitFor(() => {
      expect(screen.getByTestId('lesson-locked-title')).toBeInTheDocument();
    });
    expect(screen.queryByTestId('locked-unlocking-lesson')).not.toBeInTheDocument();
    expect(screen.queryByTestId('locked-back-to-course')).not.toBeInTheDocument();
    expect(screen.getByText(/Back to Courses/i)).toBeInTheDocument();
  });

  it('still renders "not found" for a 404', async () => {
    mockedLessons.getById.mockRejectedValue(httpError(404, 'Lesson not found'));

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '999' });

    await waitFor(() => {
      expect(screen.getByText(/Lesson not found/i)).toBeInTheDocument();
    });
    expect(screen.queryByTestId('lesson-locked-title')).not.toBeInTheDocument();
  });

  it('renders the locked state when only /start 403s', async () => {
    mockedLessons.getById.mockResolvedValue(mockLessons[0] as any);
    mockedLessons.start.mockRejectedValue(httpError(403, LOCKED_DETAIL));

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '1' });

    await waitFor(() => {
      expect(screen.getByTestId('lesson-locked-title')).toBeInTheDocument();
    });
  });
});

describe('LessonDetail surfaces /start failures', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockedCourses.getAll.mockResolvedValue(catalog as any);
    mockedLessons.getById.mockResolvedValue(mockLessons[0] as any);
  });

  it('shows the server reason for a non-403 start error, and still renders the lesson', async () => {
    mockedLessons.start.mockRejectedValue(httpError(500, 'Progress row could not be created'));

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '1' });

    await waitFor(() => {
      expect(screen.getByTestId('lesson-start-error')).toBeInTheDocument();
    });
    expect(screen.getByTestId('lesson-start-error')).toHaveTextContent(
      /Progress row could not be created/i,
    );
    // Not a locked state, and not a dead end: the lesson itself loaded.
    expect(screen.queryByTestId('lesson-locked-title')).not.toBeInTheDocument();
    expect(screen.getAllByText(/What Is Programming\?/i).length).toBeGreaterThan(0);
  });

  it('falls back to a generic message when the error carries no detail', async () => {
    mockedLessons.start.mockRejectedValue({ message: 'Network Error' });

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '1' });

    await waitFor(() => {
      expect(screen.getByTestId('lesson-start-error')).toBeInTheDocument();
    });
  });

  it('shows nothing when /start succeeds', async () => {
    mockedLessons.start.mockResolvedValue({} as any);

    renderWithProviders(null as any, { initialLanguage: 'en', lessonId: '1' });

    await waitFor(() => {
      expect(screen.getAllByText(/What Is Programming\?/i).length).toBeGreaterThan(0);
    });
    expect(screen.queryByTestId('lesson-start-error')).not.toBeInTheDocument();
  });
});
