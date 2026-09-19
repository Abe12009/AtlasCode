import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../test/setup.tsx';
import { CircuitCanvas } from '../CircuitCanvas';
import type { CircuitGraph } from '../../../types';

// Two unconnected pins -- the wiring gesture itself (click output port, then
// input port) is what's under test here, not propagation/grading (covered by
// CircuitLabPanel.test.tsx with an already-wired starter graph).
const UNWIRED_GRAPH: CircuitGraph = {
  nodes: [
    { id: 'in-a', type: 'input', position: { x: 20, y: 20 }, config: { name: 'a' } },
    { id: 'out-1', type: 'output', position: { x: 300, y: 20 }, config: { name: 'out' } },
  ],
  edges: [],
};

describe('CircuitCanvas', () => {
  it('wires an output port to an input port on click-then-click, without the background-click handler undoing it', async () => {
    // Regression test: the canvas's "click empty background to deselect"
    // handler used to fire on every bubbled click -- including a port
    // button's own click -- which reset connectingFrom back to null in the
    // same tick handleOutputPortClick set it, making it impossible to ever
    // complete a connection. Fixed by gating that handler on
    // e.target === e.currentTarget.
    const onChange = vi.fn();
    const user = userEvent.setup();

    await renderWithProviders(
      <CircuitCanvas
        graph={UNWIRED_GRAPH}
        onChange={onChange}
        values={{}}
        inputToggles={{}}
        onToggleInput={vi.fn()}
        errors={[]}
      />
    );

    await user.click(screen.getByRole('button', { name: /output port/i }));
    await user.click(screen.getByRole('button', { name: /input port/i }));

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({
        edges: [expect.objectContaining({ source: 'in-a', target: 'out-1', targetHandle: 'in0' })],
      })
    );
  });

  it('cancels the pending connection when the empty canvas background is clicked', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    await renderWithProviders(
      <CircuitCanvas
        graph={UNWIRED_GRAPH}
        onChange={onChange}
        values={{}}
        inputToggles={{}}
        onToggleInput={vi.fn()}
        errors={[]}
      />
    );

    await user.click(screen.getByRole('button', { name: /output port/i }));
    // Click empty canvas background (not a node/port) -- should cancel, not connect.
    await user.click(screen.getByTestId('circuit-canvas-background'));
    await user.click(screen.getByRole('button', { name: /input port/i }));

    expect(onChange).not.toHaveBeenCalled();
  });
});
