import React from 'react';
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../../test/setup.tsx';
import { GitTerminal, type TerminalEntry } from '../GitTerminal';

describe('GitTerminal', () => {
  it('renders a normal command\'s output exactly once', async () => {
    const history: TerminalEntry[] = [
      { command: 'git init', output: 'Initialized empty Git repository.', error: null },
    ];
    await renderWithProviders(<GitTerminal history={history} onCommand={() => {}} />);

    const matches = screen.getAllByText('Initialized empty Git repository.');
    expect(matches).toHaveLength(1);
  });

  it('renders a conflict\'s message exactly once, not duplicated across the plain and warning blocks', async () => {
    // Regression test: entry.error === 'conflict' reuses entry.output as the
    // warning-colored message (see GitTerminal's docstring) -- the plain
    // output block used to render unconditionally on `entry.output` being
    // truthy, so a conflict's text appeared twice.
    const conflictText = "CONFLICT: content conflict in config.py\nFix conflicts and then run 'git add <file>' and 'git commit'.";
    const history: TerminalEntry[] = [
      { command: 'git merge feature/staging-debug', output: conflictText, error: 'conflict' },
    ];
    await renderWithProviders(<GitTerminal history={history} onCommand={() => {}} />);

    const matches = screen.getAllByText((_, element) => element?.textContent === conflictText);
    expect(matches).toHaveLength(1);
  });

  it('renders a real error message (not a conflict) in its own block, separate from output', async () => {
    const history: TerminalEntry[] = [
      { command: 'git commit -m "x"', output: '', error: 'Nothing to commit -- stage changes with \'git add\' first.' },
    ];
    await renderWithProviders(<GitTerminal history={history} onCommand={() => {}} />);

    expect(screen.getByText(/Nothing to commit/)).toBeInTheDocument();
  });
});
