import React from 'react';
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../test/setup.tsx';
import { DebugTracePanel } from '../DebugTracePanel';
import type { TraceStep } from '../../../types';

const CODE = 'def double(x):\n    y = x + x\n    return y\n';

const TRACE: TraceStep[] = [
  { line: 1, locals: {} },
  { line: 2, locals: { x: 3 } },
  { line: 3, locals: { x: 3, y: 6 } },
];

describe('DebugTracePanel', () => {
  it('highlights the current step\'s line and shows its variables', async () => {
    await renderWithProviders(<DebugTracePanel code={CODE} trace={TRACE} />);

    expect(screen.getByTestId('trace-step-counter')).toHaveTextContent('1');
    // Step 0 has no locals yet.
    expect(screen.getByText(/no variables yet/i)).toBeInTheDocument();
  });

  it('steps forward and shows newly-introduced and changed variables', async () => {
    const user = userEvent.setup();
    await renderWithProviders(<DebugTracePanel code={CODE} trace={TRACE} />);

    await user.click(screen.getByRole('button', { name: /next step/i }));
    expect(screen.getByTestId('trace-var-x')).toHaveTextContent('3');

    await user.click(screen.getByRole('button', { name: /next step/i }));
    expect(screen.getByTestId('trace-var-y')).toHaveTextContent('6');
    // x is unchanged from the previous step, y is new -- both are shown either way.
    expect(screen.getByTestId('trace-var-x')).toHaveTextContent('3');
  });

  it('disables Previous on the first step and Next on the last step', async () => {
    const user = userEvent.setup();
    await renderWithProviders(<DebugTracePanel code={CODE} trace={TRACE} />);

    expect(screen.getByRole('button', { name: /previous step/i })).toBeDisabled();

    await user.click(screen.getByRole('button', { name: /next step/i }));
    await user.click(screen.getByRole('button', { name: /next step/i }));

    expect(screen.getByRole('button', { name: /next step/i })).toBeDisabled();
    expect(screen.getByTestId('trace-step-counter')).toHaveTextContent('3');
  });
});
