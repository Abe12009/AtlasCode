import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Projects } from '../Projects';
import { renderWithProviders, mockProjects } from '../../test/setup.tsx';
import { projectsApi } from '../../api/services';

describe('Projects Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('shows loading state initially', async () => {
    projectsApi.getAll.mockImplementation(() => new Promise(() => {}));
    
    await renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  it('displays list of projects', async () => {
    projectsApi.getAll.mockResolvedValue(mockProjects);
    projectsApi.getProgress.mockResolvedValue({ project_id: 1, status: 'locked', current_task: 0, xp_earned: 0, code_snapshot: null });
    
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText(/Build a CLI Calculator/i)).toBeInTheDocument();
    });
  });

  it('shows project prerequisite badge', async () => {
    projectsApi.getAll.mockResolvedValue(mockProjects);
    projectsApi.getProgress.mockResolvedValue({ project_id: 1, status: 'locked', current_task: 0, xp_earned: 0, code_snapshot: null });
    
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText(/Requires Lesson 5/i)).toBeInTheDocument();
    });
  });

  it('displays project difficulty and task count', async () => {
    projectsApi.getAll.mockResolvedValue(mockProjects);
    projectsApi.getProgress.mockResolvedValue({ project_id: 1, status: 'locked', current_task: 0, xp_earned: 0, code_snapshot: null });
    
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText(/4 tasks/i)).toBeInTheDocument();
      expect(screen.getByText(/Beginner/i)).toBeInTheDocument();
    });
  });

  it('navigates to project detail on click', async () => {
    projectsApi.getAll.mockResolvedValue(mockProjects);
    projectsApi.getProgress.mockResolvedValue({ project_id: 1, status: 'locked', current_task: 0, xp_earned: 0, code_snapshot: null });
    
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      const projectLink = screen.getByRole('link', { name: /Build a CLI Calculator/i });
      expect(projectLink).toHaveAttribute('href', '/app/projects/1');
    });
  });

  it('shows error state when API fails', async () => {
    projectsApi.getAll.mockRejectedValue(new Error('Network error'));
    
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText(/Something went wrong. Please try again./i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no projects available', async () => {
    projectsApi.getAll.mockResolvedValue([]);
    
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText(/No projects available/i)).toBeInTheDocument();
      expect(screen.getByText(/Complete prerequisite lessons to unlock/i)).toBeInTheDocument();
    });
  });

  it('displays project skills', async () => {
    projectsApi.getAll.mockResolvedValue(mockProjects);
    projectsApi.getProgress.mockResolvedValue({ project_id: 1, status: 'locked', current_task: 0, xp_earned: 0, code_snapshot: null });
    
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText(/Functions/i)).toBeInTheDocument();
      expect(screen.getByText(/Conditionals/i)).toBeInTheDocument();
      expect(screen.getByText(/User Input/i)).toBeInTheDocument();
    });
  });
});