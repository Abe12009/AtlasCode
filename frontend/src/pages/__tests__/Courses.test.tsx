import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Courses } from '../Courses';
import { renderWithProviders, mockCourses } from '../../test/setup.tsx';
import { coursesApi, dashboardApi } from '../../api/services';

describe('Courses Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('shows loading state initially', async () => {
    coursesApi.getAll.mockImplementation(() => new Promise(() => {}));
    
    await renderWithProviders(<Courses />);
    
    await waitFor(() => {
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  it('displays list of courses', async () => {
    coursesApi.getAll.mockResolvedValue(mockCourses);
    
    renderWithProviders(<Courses />);
    
    await waitFor(() => {
      expect(screen.getByText(/Python Foundations/i)).toBeInTheDocument();
      expect(screen.getByText(/Learn Python basics/i)).toBeInTheDocument();
    });
  });

  it('shows course cards with skills', async () => {
    coursesApi.getAll.mockResolvedValue(mockCourses);
    
    renderWithProviders(<Courses />);
    
    await waitFor(() => {
      expect(screen.getByText(/Variables/i)).toBeInTheDocument();
      expect(screen.getByText(/Functions/i)).toBeInTheDocument();
      expect(screen.getByText(/Loops/i)).toBeInTheDocument();
    });
  });

  it('shows course difficulty', async () => {
    coursesApi.getAll.mockResolvedValue(mockCourses);

    renderWithProviders(<Courses />);

    await waitFor(() => {
      expect(screen.getByText(/Beginner/i)).toBeInTheDocument();
    });
  });

  it('navigates to course detail on click', async () => {
    coursesApi.getAll.mockResolvedValue(mockCourses);
    
    renderWithProviders(<Courses />);
    
    await waitFor(() => {
      const courseLink = screen.getByRole('link', { name: /Python Foundations/i });
      expect(courseLink).toHaveAttribute('href', '/app/courses/1');
    });
  });

  it('shows error state when API fails', async () => {
    coursesApi.getAll.mockRejectedValue(new Error('Network error'));
    
    renderWithProviders(<Courses />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to load courses/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no courses available', async () => {
    coursesApi.getAll.mockResolvedValue([]);
    
    renderWithProviders(<Courses />);
    
    await waitFor(() => {
      expect(screen.getByText(/No courses available/i)).toBeInTheDocument();
      expect(screen.getByText(/Check back later/i)).toBeInTheDocument();
    });
  });

  it('groups courses under a section heading', async () => {
    coursesApi.getAll.mockResolvedValue(mockCourses);

    renderWithProviders(<Courses />);

    await waitFor(() => {
      // No section_id on the mock course, so it renders under the
      // unsectioned "Foundations" group heading (distinct from the course's
      // own "Python Foundations" title).
      expect(screen.getByRole('heading', { level: 2, name: 'Foundations' })).toBeInTheDocument();
    });
  });

  /**
   * The completed treatment is a state attribute, not a utility.
   *
   * It used to be `border-success-500/30 bg-success-500/5` on the Card, and
   * neither painted: the Card's glass class sets background-color and border
   * unlayered in index.css, so a finished course looked exactly like an
   * untouched one. Measured in Chromium before the fix -- the completed card
   * and a plain one returned identical computed values.
   */
  describe('a completed course is marked for the stylesheet', () => {
    const completedDashboard = (completed: number, total: number) => ({
      course_progress: [
        { course_id: 1, completed_lessons: completed, total_lessons: total, progress_percent: (completed / total) * 100 },
      ],
    });

    it('carries data-state="completed" when every lesson is done', async () => {
      coursesApi.getAll.mockResolvedValue(mockCourses);
      dashboardApi.get.mockResolvedValue(completedDashboard(3, 3));

      renderWithProviders(<Courses />);

      await waitFor(() => {
        expect(document.querySelector('[data-state="completed"]')).not.toBeNull();
      });
    });

    it('does not mark a partly-finished course', async () => {
      coursesApi.getAll.mockResolvedValue(mockCourses);
      dashboardApi.get.mockResolvedValue(completedDashboard(1, 3));

      renderWithProviders(<Courses />);

      await waitFor(() => expect(screen.getByText(/Python Foundations/i)).toBeInTheDocument());
      expect(document.querySelector('[data-state="completed"]')).toBeNull();
    });

    it('passes no background or border utility to the card', async () => {
      coursesApi.getAll.mockResolvedValue(mockCourses);
      dashboardApi.get.mockResolvedValue(completedDashboard(3, 3));

      renderWithProviders(<Courses />);
      const marked = await waitFor(() => {
        const el = document.querySelector('[data-state="completed"]');
        expect(el).not.toBeNull();
        return el!;
      });
      // Their return would be silent: they cannot beat the glass class, so
      // nothing would change on screen and the state would stop painting.
      expect(marked.className).not.toMatch(/\bbg-success-/);
      expect(marked.className).not.toMatch(/\bborder-success-/);
      expect(marked.className).not.toMatch(/\bborder-border-primary\//);
    });
  });
});