import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockLessons } from '../../test/setup.tsx';
import { lessonsApi, exercisesApi } from '../../api/services';

describe('LessonDetail Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('shows loading state initially', async () => {
    lessonsApi.getById.mockImplementation(() => new Promise(() => {}));
    
    await renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    await waitFor(() => {
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  it('displays lesson title and metadata', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    await waitFor(() => {
      expect(screen.getByText(/What Is Programming?/i)).toBeInTheDocument();
      expect(screen.getByText(/30 min/i)).toBeInTheDocument();
      expect(screen.getByText(/Beginner/i)).toBeInTheDocument();
      expect(screen.getByText(/50 XP/i)).toBeInTheDocument();
    });
  });

  it('shows lesson blocks in sidebar navigation', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    await waitFor(() => {
      // Sidebar shows block types: Read (2x), Code (1x) for 3 blocks
      expect(screen.getAllByText(/Read/i)).toHaveLength(2);
      expect(screen.getByText(/Code/i)).toBeInTheDocument();
      // Exercises show as "Exercise 1", "Exercise 2", "Exercise 3"
      expect(screen.getByText(/Exercise 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Exercise 2/i)).toBeInTheDocument();
      expect(screen.getByText(/Exercise 3/i)).toBeInTheDocument();
    });
  });

  it('displays text block content', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Programming is giving instructions to a computer/i)).toBeInTheDocument();
    });
  });

  it('displays code example with copy button', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    // Navigate to block 1 (code block)
    await waitFor(() => {
      expect(screen.getByTestId('lesson-nav-next')).toBeInTheDocument();
    });
    await userEvent.click(screen.getByTestId('lesson-nav-next'));
    
    await waitFor(() => {
      expect(screen.getByText(/Your first program:/i)).toBeInTheDocument();
      expect(screen.getByText(/print\("Hello, World!"\)/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument();
    });
  });

  it('navigates between blocks with next/previous', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    await waitFor(() => {
      expect(screen.getByTestId('lesson-nav-next')).toBeInTheDocument();
      expect(screen.getByTestId('lesson-nav-prev')).toBeInTheDocument();
    });
    
    const nextButton = screen.getByTestId('lesson-nav-next');
    await userEvent.click(nextButton);
    
    await waitFor(() => {
      // Total includes exercises (3 blocks + 3 exercises = 6)
      expect(screen.getByText(/Block 2 of 6/i)).toBeInTheDocument();
    });
    
    // Go back
    const prevButton = screen.getByTestId('lesson-nav-prev');
    await userEvent.click(prevButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Block 1 of 6/i)).toBeInTheDocument();
    });
  });

  it('shows exercise view with code editor', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    exercisesApi.run.mockResolvedValue({ is_correct: true, xp_earned: 10, feedback: 'Correct!', output: 'Hello, World!', error: null });
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    // Navigate through 3 blocks to reach first exercise
    for (let i = 0; i < 3; i++) {
      await waitFor(() => {
        expect(screen.getByTestId('lesson-nav-next')).toBeInTheDocument();
      });
      await userEvent.click(screen.getByTestId('lesson-nav-next'));
    }
    
    await waitFor(() => {
      // After 3 blocks, we're at first exercise (index 3): "Exercise 1 of 6"
      expect(screen.getByText(/Exercise 1 of 6/i)).toBeInTheDocument();
      expect(screen.getByTestId('code-editor-run-btn')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /submit solution/i })).toBeInTheDocument();
    });
  });

  it('runs code and shows output', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    exercisesApi.run.mockResolvedValue({ is_correct: true, xp_earned: 10, feedback: 'Correct!', output: 'Hello, World!', error: null });
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    // Navigate through 3 blocks to reach first exercise
    for (let i = 0; i < 3; i++) {
      await waitFor(() => {
        expect(screen.getByTestId('lesson-nav-next')).toBeInTheDocument();
      });
      await userEvent.click(screen.getByTestId('lesson-nav-next'));
    }
    
    await waitFor(() => {
      expect(screen.getByTestId('code-editor-run-btn')).toBeInTheDocument();
    });
    
    await userEvent.click(screen.getByTestId('code-editor-run-btn'));
    
    await waitFor(() => {
      // Check for output text in TerminalPanel
      const terminalPanel = screen.getByTestId('terminal-panel');
      expect(terminalPanel).toBeInTheDocument();
      expect(within(terminalPanel).getByText('Hello, World!')).toBeInTheDocument();
    });
  });

  it('submits solution and awards XP', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    exercisesApi.submit.mockResolvedValue({ is_correct: true, xp_earned: 10, feedback: 'Correct!', output: 'Hello, World!', error: null });
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    // Navigate through 3 blocks to reach first exercise
    for (let i = 0; i < 3; i++) {
      await waitFor(() => {
        expect(screen.getByTestId('lesson-nav-next')).toBeInTheDocument();
      });
      await userEvent.click(screen.getByTestId('lesson-nav-next'));
    }
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /submit solution/i })).toBeInTheDocument();
    });
    
    await userEvent.click(screen.getByRole('button', { name: /submit solution/i }));
    
    await waitFor(() => {
      // XP badge shows "+10 XP" but may be in a badge component
      expect(screen.getByText(/10 XP/i)).toBeInTheDocument();
    });
  });

  it('shows hint when available', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    // Navigate through 3 blocks to reach first exercise
    for (let i = 0; i < 3; i++) {
      await waitFor(() => {
        expect(screen.getByTestId('lesson-nav-next')).toBeInTheDocument();
      });
      await userEvent.click(screen.getByTestId('lesson-nav-next'));
    }
    
    await waitFor(() => {
      expect(screen.getByText(/Use print\(\)/i)).toBeInTheDocument();
    });
  });

  it('shows error state when lesson not found', async () => {
    lessonsApi.getById.mockRejectedValue(new Error('Not found'));
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '999' });
    
    await waitFor(() => {
      expect(screen.getByText(/Lesson not found/i)).toBeInTheDocument();
    });
  });

  it('navigates back to courses', async () => {
    lessonsApi.getById.mockResolvedValue(mockLessons[0]);
    
    renderWithProviders(null, { initialLanguage: 'en', lessonId: '1' });
    
    await waitFor(() => {
      // Header has a link with ArrowLeft icon to /courses
      expect(screen.getByRole('link', { href: '/courses' })).toBeInTheDocument();
    });
  });
});