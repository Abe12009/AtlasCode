import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Courses } from '../Courses';
import { renderWithProviders, mockCourses } from '../../test/setup.tsx';
import { coursesApi } from '../../api/services';

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

  it('shows course difficulty and estimated time', async () => {
    coursesApi.getAll.mockResolvedValue(mockCourses);
    
    renderWithProviders(<Courses />);
    
    await waitFor(() => {
      expect(screen.getByText(/~30 min\/lesson/i)).toBeInTheDocument();
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

  it('displays course order badge', async () => {
    coursesApi.getAll.mockResolvedValue(mockCourses);
    
    renderWithProviders(<Courses />);
    
    await waitFor(() => {
      expect(screen.getByText(/Course #1/i)).toBeInTheDocument();
    });
  });
});