import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockVisualProgrammingExercise } from '../../test/setup.tsx';
import { exercisesApi, visualApi } from '../../api/services';

describe('Visual Programming Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('shows loading spinner initially', async () => {
    exercisesApi.getById.mockImplementation(() => new Promise(() => {}));
    visualApi.getStarter.mockImplementation(() => new Promise(() => {}));
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  it('displays exercise title and prompt', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Build a visual program/i })).toBeInTheDocument();
    });
  });

  it('shows node palette with all node types', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Start/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /End/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Variable/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Output/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /If/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Loop/i })).toBeInTheDocument();
    });
  });

  it('shows compile, run, and submit buttons', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Compile/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Run Program/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Submit Solution/i })).toBeInTheDocument();
    });
  });

  it('shows undo/redo buttons', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Undo/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Redo/i })).toBeInTheDocument();
    });
  });

  it('compiles visual program and shows code preview', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    // Provide starter data with nodes so the compile button is enabled
    visualApi.getStarter.mockResolvedValue(JSON.stringify({
      nodes: [
        { id: '1', type: 'start', position: { x: 100, y: 100 }, config: {} },
        { id: '2', type: 'output', position: { x: 300, y: 100 }, config: { value: 'hello' } }
      ],
      edges: [{ id: 'e1', source: '1', target: '2' }]
    }));
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Compile/i })).toBeInTheDocument();
    });
    
    await userEvent.click(screen.getByRole('button', { name: /Compile/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/Show Code/i)).toBeInTheDocument();
    });
    
    await userEvent.click(screen.getByRole('button', { name: /Show Code/i }));

    await waitFor(() => {
      // CodeMirror renders one line per DOM element, so the code is checked
      // via the editor's combined textContent rather than getByText (which
      // only matches within a single element).
      const editors = screen.getAllByTestId('code-editor');
      expect(editors.some((el) => /print.*Hello/.test(el.textContent || ''))).toBe(true);
    });
  });

  it('shows validation errors when compile fails', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    // Provide starter data with nodes so the compile button is enabled
    visualApi.getStarter.mockResolvedValue(JSON.stringify({
      nodes: [
        { id: '1', type: 'start', position: { x: 100, y: 100 }, config: {} },
        { id: '2', type: 'output', position: { x: 300, y: 100 }, config: { value: 'hello' } }
      ],
      edges: [{ id: 'e1', source: '1', target: '2' }]
    }));
    const compileSpy = vi.spyOn(visualApi, 'compile').mockResolvedValue({ 
      python_code: '', 
      is_valid: false, 
      errors: ['No start node found', 'Unreachable nodes detected'] 
    });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Compile/i })).toBeInTheDocument();
    });
    
    // Find the compile button and click it
    const compileButton = screen.getByRole('button', { name: /Compile/i });
    await userEvent.click(compileButton);
    
    // Wait for the compile mutation to complete - wait for compiling state to end
    await waitFor(() => {
      expect(screen.queryByText(/Compiling.../i)).not.toBeInTheDocument();
    }, { timeout: 15000 });
    
    // Check if the mock was called
    expect(compileSpy).toHaveBeenCalled();
    
    // Then wait for validation errors to appear
    await waitFor(() => {
      expect(screen.getByText(/Validation Errors/i)).toBeInTheDocument();
    }, { timeout: 15000 });
    
    await waitFor(() => {
      expect(screen.getByText(/No start node found/i)).toBeInTheDocument();
      expect(screen.getByText(/Unreachable nodes detected/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  }, 30000);

  it('shows clear canvas button', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Clear Canvas/i })).toBeInTheDocument();
    });
  });

  it('navigates back to courses', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });
    
    renderWithProviders(null, { exerciseId: '1' });
    
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Back/i })).toBeInTheDocument();
    });
  });

  it('shows breadcrumb navigation', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });

    renderWithProviders(null, { exerciseId: '1' });

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Course 1/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Lesson 1/i })).toBeInTheDocument();
    });
  });

  /**
   * `.bg-grid-pattern` sets `opacity` on the element (index.css), and opacity
   * applies to the whole subtree -- so a grid class on the node layer renders
   * every edge and node at 0.05. Measured in a browser before the fix. The
   * grid has to stay its own childless decorative layer.
   */
  it('renders the canvas grid as a childless, aria-hidden layer', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });

    renderWithProviders(null, { exerciseId: '1' });

    const grid = await screen.findByTestId('visual-canvas-grid');
    expect(grid.className).toContain('bg-grid-pattern');
    expect(grid.getAttribute('aria-hidden')).toBe('true');
    expect(grid.children.length, 'the grid layer must stay childless').toBe(0);
    // handleCanvasClick only clears the selection when
    // `e.target === e.currentTarget`, so the grid must not take clicks.
    expect(grid.className).toContain('pointer-events-none');
  });

  it('keeps the grid class off the layer that holds the nodes', async () => {
    exercisesApi.getById.mockResolvedValue(mockVisualProgrammingExercise);
    visualApi.getStarter.mockResolvedValue(null);
    visualApi.compile.mockResolvedValue({ python_code: 'print("Hello")', is_valid: true, errors: [] });

    renderWithProviders(null, { exerciseId: '1' });

    await screen.findByTestId('visual-canvas-grid');
    for (const el of document.querySelectorAll('.bg-grid-pattern')) {
      expect(el.children.length, 'no .bg-grid-pattern element may wrap content').toBe(0);
    }
  });
});