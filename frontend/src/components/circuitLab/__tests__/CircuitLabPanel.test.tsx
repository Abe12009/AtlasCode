import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../test/setup.tsx';
import { CircuitLabPanel } from '../CircuitLabPanel';
import { circuitsApi } from '../../../api/services';
import type { Exercise, CircuitGraph } from '../../../types';

const mockedApi = vi.mocked(circuitsApi);

// A fully-wired AND circuit: in-a, in-b -> and1 -> out.
const AND_GRAPH: CircuitGraph = {
  nodes: [
    { id: 'in-a', type: 'input', position: { x: 20, y: 20 }, config: { name: 'a' } },
    { id: 'in-b', type: 'input', position: { x: 20, y: 140 }, config: { name: 'b' } },
    { id: 'gate-1', type: 'and', position: { x: 220, y: 80 }, config: {} },
    { id: 'out-1', type: 'output', position: { x: 420, y: 80 }, config: { name: 'out' } },
  ],
  edges: [
    { id: 'e1', source: 'in-a', target: 'gate-1', targetHandle: 'in0' },
    { id: 'e2', source: 'in-b', target: 'gate-1', targetHandle: 'in1' },
    { id: 'e3', source: 'gate-1', target: 'out-1' },
  ],
};

const EXERCISE: Exercise = {
  id: 42,
  exercise_type: 'circuit_lab',
  order: 1,
  xp_reward: 30,
  starter_code: JSON.stringify(AND_GRAPH),
  translations: [],
  options: [],
};

/** Mirrors the real backend's AND-gate propagation for the fixed AND_GRAPH,
 * keyed off whatever input_values the component actually sent. */
function evaluateAnd(inputValues: Record<string, boolean>) {
  const a = !!inputValues.a;
  const b = !!inputValues.b;
  const out = a && b;
  return Promise.resolve({
    values: { 'in-a': a, 'in-b': b, 'gate-1': out, 'out-1': out },
    outputs: { out },
    errors: [],
  });
}

beforeEach(() => {
  mockedApi.compile.mockReset();
  mockedApi.evaluate.mockReset();
  mockedApi.evaluate.mockImplementation((_graph, inputValues) => evaluateAnd(inputValues));
});

describe('CircuitLabPanel', () => {
  it('lights up the output pin only when both inputs are toggled true', async () => {
    const user = userEvent.setup();
    await renderWithProviders(
      <CircuitLabPanel exercise={EXERCISE} onSubmit={vi.fn()} onRun={vi.fn()} isSubmitting={false} isRunning={false} />
    );

    expect(await screen.findByText('FALSE')).toBeInTheDocument();

    const toggles = screen.getAllByRole('button', { name: /toggle/i });
    expect(toggles).toHaveLength(2);

    await user.click(toggles[0]);
    await user.click(toggles[1]);

    await waitFor(() => {
      expect(screen.getByText('TRUE')).toBeInTheDocument();
    });
  });

  it('compiles the graph and submits the resulting Python code', async () => {
    const onSubmit = vi.fn();
    mockedApi.compile.mockResolvedValue({
      python_code: 'def circuit(**inputs):\n    return {"out": inputs["a"] and inputs["b"]}',
      is_valid: true,
      errors: [],
    });

    const user = userEvent.setup();
    await renderWithProviders(
      <CircuitLabPanel exercise={EXERCISE} onSubmit={onSubmit} onRun={vi.fn()} isSubmitting={false} isRunning={false} />
    );

    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        exerciseId: 42,
        code: 'def circuit(**inputs):\n    return {"out": inputs["a"] and inputs["b"]}',
      });
    });
  });

  it('resets the canvas to the starter graph', async () => {
    const user = userEvent.setup();
    await renderWithProviders(
      <CircuitLabPanel exercise={EXERCISE} onSubmit={vi.fn()} onRun={vi.fn()} isSubmitting={false} isRunning={false} />
    );

    const toggles = screen.getAllByRole('button', { name: /toggle/i });
    await user.click(toggles[0]);
    await user.click(toggles[1]);
    await waitFor(() => expect(screen.getByText('TRUE')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /reset/i }));

    await waitFor(() => {
      expect(screen.getByText('FALSE')).toBeInTheDocument();
    });
  });
});
