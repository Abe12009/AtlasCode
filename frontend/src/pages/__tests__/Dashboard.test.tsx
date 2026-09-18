import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Dashboard } from '../Dashboard';
import { renderWithProviders } from '../../test/setup.tsx';
import { dashboardApi } from '../../api/services';
import type { DashboardData } from '../../types';

const mockedApi = vi.mocked(dashboardApi);

function buildDashboard(overrides: Partial<DashboardData> = {}): DashboardData {
  return {
    user: { id: 1, email: 'a@example.com', username: 'ada', preferred_language: 'en', is_active: true, created_at: new Date().toISOString() } as any,
    profile: {
      id: 1,
      name: 'Ada',
      xp: 420,
      level: 3,
      streak: 5,
      completed_lessons: 12,
      completed_projects: 2,
      current_mission_id: null,
    },
    weekly: {
      week_start: new Date().toISOString(),
      xp: 30,
      lessons_completed: 2,
      projects_completed: 1,
      levels_gained: 0,
      active_days: 3,
      has_activity: true,
    },
    current_mission: null,
    current_mission_course_title: null,
    current_mission_module_title: null,
    course_progress: [],
    recent_achievements: [],
    current_project: null,
    ...overrides,
  };
}

describe('Dashboard page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows the 4 target stats: courses in progress, projects completed, day streak, total XP', async () => {
    mockedApi.get.mockResolvedValue(
      buildDashboard({
        course_progress: [
          { course_id: 1, completed_lessons: 2, total_lessons: 10, progress_percent: 20, title: 'Python Foundations' },
          { course_id: 2, completed_lessons: 10, total_lessons: 10, progress_percent: 100, title: 'Finished Course' },
        ],
      })
    );
    await renderWithProviders(<Dashboard />);

    expect(await screen.findByText('Courses in Progress')).toBeInTheDocument();
    // Only course 1 is strictly between 0 and 100 -- course 2 is done and
    // shouldn't count as "in progress".
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('Projects Completed')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('Day Streak')).toBeInTheDocument();
    expect(screen.getByText('5 days')).toBeInTheDocument();
    expect(screen.getByText('Total XP')).toBeInTheDocument();
    expect(screen.getByText('420')).toBeInTheDocument();
  });

  it('shows a dynamic percent-based subtitle when a course is in progress', async () => {
    mockedApi.get.mockResolvedValue(
      buildDashboard({
        current_mission: { id: 7, slug: 'x', order: 1, difficulty: 'beginner', estimated_minutes: 20, xp_reward: 50, is_project: false, translations: [{ language: 'en', title: 'Loops', story: 'A story', objective: null, skills: 'Loops, Iteration' }], blocks: [], exercises: [] } as any,
        current_mission_course_title: 'Python Foundations',
        current_mission_module_title: 'Control Flow',
        course_progress: [
          { course_id: 1, completed_lessons: 4, total_lessons: 10, progress_percent: 40, title: 'Python Foundations' },
        ],
      })
    );
    await renderWithProviders(<Dashboard />);

    expect(await screen.findByText(/You're 40% through Python Foundations/)).toBeInTheDocument();
  });

  it('falls back to a generic subtitle for a brand-new account with no course progress', async () => {
    mockedApi.get.mockResolvedValue(buildDashboard());
    await renderWithProviders(<Dashboard />);

    expect(await screen.findByText('Continue your coding journey')).toBeInTheDocument();
  });

  it('renders the Continue Learning card with course title, module subtitle, and a progress bar, with story/skills collapsed by default', async () => {
    mockedApi.get.mockResolvedValue(
      buildDashboard({
        current_mission: {
          id: 7,
          slug: 'x',
          order: 1,
          difficulty: 'beginner',
          estimated_minutes: 20,
          xp_reward: 50,
          is_project: false,
          translations: [{ language: 'en', title: 'Loops', story: 'Once upon a bug...', objective: null, skills: 'Loops, Iteration' }],
          blocks: [],
          exercises: [],
        } as any,
        current_mission_course_title: 'Python Foundations',
        current_mission_module_title: 'Control Flow',
        course_progress: [
          { course_id: 1, completed_lessons: 4, total_lessons: 10, progress_percent: 40, title: 'Python Foundations' },
        ],
      })
    );
    const user = userEvent.setup();
    await renderWithProviders(<Dashboard />);

    expect((await screen.findAllByText('Python Foundations')).length).toBeGreaterThan(0);
    expect(screen.getByText('Control Flow')).toBeInTheDocument();
    expect(screen.getByText('Continue lesson')).toBeInTheDocument();
    expect(screen.queryByText('Once upon a bug...')).not.toBeInTheDocument();
    expect(screen.queryByText('Loops')).not.toBeInTheDocument();

    await user.click(screen.getByTestId('dashboard-story-toggle'));
    expect(screen.getByText('Once upon a bug...')).toBeInTheDocument();
    expect(screen.getByText('Iteration')).toBeInTheDocument();

    await user.click(screen.getByTestId('dashboard-story-toggle'));
    expect(screen.queryByText('Once upon a bug...')).not.toBeInTheDocument();
  });

  it('shows real course titles (not raw numeric ids) in the progress list', async () => {
    mockedApi.get.mockResolvedValue(
      buildDashboard({
        course_progress: [
          { course_id: 1, completed_lessons: 2, total_lessons: 10, progress_percent: 20, title: 'Python Foundations' },
        ],
      })
    );
    await renderWithProviders(<Dashboard />);

    expect(await screen.findByText('Python Foundations')).toBeInTheDocument();
    expect(screen.queryByText(/^Course 1$/)).not.toBeInTheDocument();
  });
});
