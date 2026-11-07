import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { Dashboard } from '../Dashboard';
import { renderWithProviders } from '../../test/setup.tsx';
import { dashboardApi, coursesApi } from '../../api/services';
import type { DashboardData } from '../../types';

const mockedDashboard = vi.mocked(dashboardApi);
const mockedCourses = vi.mocked(coursesApi);

/**
 * The quest map is built from GET /courses/{id} -- real lesson ids, real
 * statuses -- for the one course the map represents. It used to be built from
 * the dashboard's lesson *counts*, numbering nodes 1..total with a status
 * re-derived from completed_lessons and a `path` of /app/lessons/{course}-{i}
 * that matched no route.
 */
function dashboardData(overrides: Partial<DashboardData> = {}): DashboardData {
  return {
    user: { id: 1, email: 'a@example.com', username: 'ada', preferred_language: 'en', is_active: true, created_at: new Date().toISOString() },
    profile: { id: 1, name: 'Ada', xp: 100, level: 2, streak: 1, completed_lessons: 1, completed_projects: 0, current_mission_id: null },
    weekly: { week_start: new Date().toISOString(), xp: 10, lessons_completed: 1, projects_completed: 0, levels_gained: 0, active_days: 1, has_activity: true },
    current_mission: null,
    current_mission_course_title: null,
    current_mission_module_title: null,
    course_progress: [],
    recent_achievements: [],
    current_project: null,
    ...overrides,
  } as DashboardData;
}

function courseWithLessons() {
  return {
    id: 42,
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
          { id: 101, slug: 'a', order: 1, difficulty: 'beginner', estimated_minutes: 20, xp_reward: 50, is_project: false, status: 'completed', translations: [{ language: 'en', title: 'What Is Programming?' }], blocks: [], exercises: [] },
          { id: 102, slug: 'b', order: 2, difficulty: 'beginner', estimated_minutes: 25, xp_reward: 60, is_project: false, status: 'current', translations: [{ language: 'en', title: 'Variables and Values' }], blocks: [], exercises: [] },
        ],
      },
      {
        id: 2,
        slug: 'control-flow',
        order: 2,
        translations: [{ language: 'en', title: 'Control Flow' }],
        lessons: [
          { id: 103, slug: 'c', order: 1, difficulty: 'intermediate', estimated_minutes: 30, xp_reward: 70, is_project: false, status: 'locked', translations: [{ language: 'en', title: 'Branching' }], blocks: [], exercises: [] },
        ],
      },
    ],
  };
}

const IN_PROGRESS_ROW = {
  course_id: 42,
  completed_lessons: 1,
  total_lessons: 3,
  progress_percent: 33,
  title: 'Python Foundations',
};

describe('Dashboard quest nodes', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockedCourses.getById.mockResolvedValue(courseWithLessons() as any);
  });

  it('builds nodes from the real lessons of the in-progress course', async () => {
    mockedDashboard.get.mockResolvedValue(dashboardData({ course_progress: [IN_PROGRESS_ROW] }));

    await renderWithProviders(<Dashboard />, { initialLanguage: 'en' });

    await waitFor(() => {
      expect(screen.getByText('What Is Programming?')).toBeInTheDocument();
    });
    expect(screen.getByText('Variables and Values')).toBeInTheDocument();
    // Crosses the module boundary: one sequence per course, not per module.
    expect(screen.getByText('Branching')).toBeInTheDocument();
    expect(mockedCourses.getById).toHaveBeenCalledWith(42, 'en');
  });

  it('labels each node with the status the backend reported', async () => {
    mockedDashboard.get.mockResolvedValue(dashboardData({ course_progress: [IN_PROGRESS_ROW] }));

    await renderWithProviders(<Dashboard />, { initialLanguage: 'en' });

    await waitFor(() => {
      expect(screen.getByLabelText('What Is Programming?, Completed')).toBeInTheDocument();
    });
    expect(screen.getByLabelText('Variables and Values, In progress')).toBeInTheDocument();
    expect(screen.getByLabelText('Branching, Locked')).toBeInTheDocument();
  });

  it('renders no fake lesson links', async () => {
    mockedDashboard.get.mockResolvedValue(dashboardData({ course_progress: [IN_PROGRESS_ROW] }));

    const { container } = await renderWithProviders(<Dashboard />, { initialLanguage: 'en' });

    await waitFor(() => expect(screen.getByText('Branching')).toBeInTheDocument());
    const hrefs = Array.from(container.querySelectorAll('a')).map((a) => a.getAttribute('href') ?? '');
    // The dead /app/lessons/42-1 shape is gone, and nodes are still not links.
    expect(hrefs.some((h) => /\/app\/lessons\/\d+-\d+/.test(h))).toBe(false);
    expect(hrefs).not.toContain('/app/lessons/101');
  });

  it('prefers the course of the current mission', async () => {
    mockedDashboard.get.mockResolvedValue(
      dashboardData({
        current_mission_course_title: 'Second Course',
        course_progress: [
          IN_PROGRESS_ROW,
          { course_id: 99, completed_lessons: 0, total_lessons: 4, progress_percent: 0, title: 'Second Course' },
        ],
      }),
    );

    await renderWithProviders(<Dashboard />, { initialLanguage: 'en' });

    await waitFor(() => {
      expect(mockedCourses.getById).toHaveBeenCalledWith(99, 'en');
    });
    expect(mockedCourses.getById).not.toHaveBeenCalledWith(42, 'en');
  });

  it('falls back to the first unfinished course when the mission course has no progress row', async () => {
    mockedDashboard.get.mockResolvedValue(
      dashboardData({
        current_mission_course_title: 'A Course With No Progress Row',
        course_progress: [
          { course_id: 7, completed_lessons: 3, total_lessons: 3, progress_percent: 100, title: 'Finished' },
          IN_PROGRESS_ROW,
        ],
      }),
    );

    await renderWithProviders(<Dashboard />, { initialLanguage: 'en' });

    await waitFor(() => {
      expect(mockedCourses.getById).toHaveBeenCalledWith(42, 'en');
    });
  });

  it('shows an empty state and fetches no course when nothing is started', async () => {
    mockedDashboard.get.mockResolvedValue(dashboardData({ course_progress: [] }));

    await renderWithProviders(<Dashboard />, { initialLanguage: 'en' });

    await waitFor(() => {
      expect(screen.getByTestId('quest-board-empty')).toBeInTheDocument();
    });
    expect(screen.getByTestId('quest-board-empty')).toHaveTextContent(/No courses started yet/i);
    expect(mockedCourses.getById).not.toHaveBeenCalled();
  });

  it('treats a lesson with no status as available, never locked', async () => {
    mockedCourses.getById.mockResolvedValue({
      ...courseWithLessons(),
      modules: [
        {
          id: 1,
          slug: 'getting-started',
          order: 1,
          translations: [{ language: 'en', title: 'Getting Started' }],
          lessons: [
            { id: 201, slug: 'x', order: 1, difficulty: 'beginner', estimated_minutes: 10, xp_reward: 10, is_project: false, translations: [{ language: 'en', title: 'Statusless' }], blocks: [], exercises: [] },
          ],
        },
      ],
    } as any);
    mockedDashboard.get.mockResolvedValue(
      dashboardData({
        course_progress: [{ ...IN_PROGRESS_ROW, completed_lessons: 0, total_lessons: 1, progress_percent: 0 }],
      }),
    );

    await renderWithProviders(<Dashboard />, { initialLanguage: 'en' });

    await waitFor(() => {
      expect(screen.getByLabelText('Statusless, Available')).toBeInTheDocument();
    });
  });
});
