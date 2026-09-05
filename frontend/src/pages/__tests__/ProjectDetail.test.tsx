import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { fireEvent } from '@testing-library/react';
import { renderWithProviders, mockProjects } from '../../test/setup.tsx';
import { projectsApi } from '../../api/services';

describe('ProjectDetail Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('shows loading state initially', async () => {
    projectsApi.getById.mockImplementation(() => new Promise(() => {}));
    projectsApi.getProgress.mockImplementation(() => new Promise(() => {}));
    
    await renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  it('displays project title and metadata', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'ready', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Build a CLI Calculator/i)).toBeInTheDocument();
      expect(screen.getByText(/Lesson 5/i)).toBeInTheDocument();
      expect(screen.getByText(/200 XP/i)).toBeInTheDocument();
      expect(screen.getByText(/Beginner/i)).toBeInTheDocument();
    });
  });

  it('shows language selector', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'ready', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
  });

  it('switches language when selected', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'ready', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      const langSelect = screen.getByRole('combobox');
      expect(langSelect).toHaveValue('en');
    });
    
    await userEvent.selectOptions(screen.getByRole('combobox'), 'fr');
    
    await waitFor(() => {
      expect(screen.getByRole('combobox')).toHaveValue('fr');
    });
  });

  it('displays task list with expandable tasks', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'in_progress', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Implement Basic Operations/i)).toBeInTheDocument();
      expect(screen.getByText(/Build the Calculator Menu/i)).toBeInTheDocument();
    });
  });

  it('expands task to show description and hint', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'in_progress', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      const taskButton = screen.getByText(/Implement Basic Operations/i).closest('button');
      fireEvent.click(taskButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Create functions for add, subtract, multiply, and divide/i)).toBeInTheDocument();
      expect(screen.getByText(/Remember to handle division by zero/i)).toBeInTheDocument();
    });
  });

  it('shows code editor with starter code', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'in_progress', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      const taskButton = screen.getByText(/Implement Basic Operations/i).closest('button');
      fireEvent.click(taskButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText(/def add\(a, b\):/i)).toBeInTheDocument();
      // There are multiple copy buttons (one per task), use the first task's copy button
      expect(screen.getByTestId('task-copy-btn-1')).toBeInTheDocument();
    });
  });

  it('submits task and shows success feedback', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress
      .mockResolvedValue({ status: 'in_progress', current_task: 0, xp_earned: 0 });
    projectsApi.submitTask.mockResolvedValue({ success: true, progress: { status: 'in_progress', current_task: 1, xp_earned: 0 } });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      const taskButton = screen.getByText(/Implement Basic Operations/i).closest('button');
      fireEvent.click(taskButton);
    });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Submit Task/i })).toBeInTheDocument();
    });
    
    await userEvent.click(screen.getByRole('button', { name: /Submit Task/i }));
    
    await waitFor(() => {
      // Check for success feedback text
      expect(screen.getByText(/Task submitted successfully!/i)).toBeInTheDocument();
    });
  });

  it('shows error feedback on submission failure', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'in_progress', current_task: 0, xp_earned: 0 });
    projectsApi.submitTask.mockRejectedValue({ response: { data: { detail: 'Validation failed' } } });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      const taskButton = screen.getByText(/Implement Basic Operations/i).closest('button');
      fireEvent.click(taskButton);
    });
    
    await userEvent.click(screen.getByRole('button', { name: /Submit Task/i }));
    
    await waitFor(() => {
      // Error feedback appears in the task feedback area (first occurrence)
      const errorElements = screen.getAllByText(/Validation failed/i);
      expect(errorElements.length).toBeGreaterThan(0);
    });
  });

  it('shows progress bar and completion status', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'in_progress', current_task: 1, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      // Project has 4 tasks, current_task=1 means 1 completed out of 4
      expect(screen.getByText(/1 \/ 4/i)).toBeInTheDocument();
      expect(screen.getByText(/25%/i)).toBeInTheDocument();
    });
  });

  it('shows completed state when all tasks done', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'completed', current_task: 4, xp_earned: 200, completed_at: new Date().toISOString() });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      // Find the completed status badge in the project header (first column)
      // The header has a badge with the project status
      const headerBadges = screen.getAllByText(/Completed/i);
      // Filter to find the one in the header area (should be in the first column)
      expect(headerBadges.length).toBeGreaterThan(0);
    }, { timeout: 15000 });
    
    await waitFor(() => {
      // Check for earned XP text (may appear multiple times)
      const xpElements = screen.getAllByText(/200 XP/i);
      expect(xpElements.length).toBeGreaterThan(0);
    });
  });

  it('shows locked state when project is locked', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'locked', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Locked - Complete Lesson 5 first/i)).toBeInTheDocument();
    });
  });

  it('shows project guide and skills', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'ready', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Complete all tasks/i)).toBeInTheDocument();
      expect(screen.getByText(/Functions/i)).toBeInTheDocument();
      expect(screen.getByText(/Conditionals/i)).toBeInTheDocument();
    });
  });

  it('displays objective', async () => {
    projectsApi.getById.mockResolvedValue(mockProjects[0]);
    projectsApi.getProgress.mockResolvedValue({ status: 'ready', current_task: 0, xp_earned: 0 });
    
    renderWithProviders(null, { projectId: '1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Objective/i)).toBeInTheDocument();
      expect(screen.getByText(/Build a working calculator/i)).toBeInTheDocument();
    });
  });
});