import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { Button } from '../Button';
import { Card } from '../Card';
import { CodeEditor, TerminalPanel } from '../CodeEditor';
import { CircuitCanvas } from '../../circuitLab/CircuitCanvas';
import type { CircuitGraph } from '../../../types';

const css = readFileSync(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../index.css'),
  'utf-8',
);

/** The declaration block of a rule, by exact selector.
 *
 * Anchored on `selector + ' {'` so `.no-glass` cannot match `.no-glass-foo`,
 * and so the `.no-blur` lookup does not land inside `.no-glass`'s block. */
function cssRule(selector: string): string {
  const start = css.indexOf(`${selector} {`);
  if (start === -1) throw new Error(`${selector} not found in index.css`);
  return css.slice(start, css.indexOf('}', start));
}

const EMPTY_GRAPH: CircuitGraph = { nodes: [], edges: [] };

/** CircuitCanvas's required props, none of which these tests exercise. */
const circuitProps = {
  graph: EMPTY_GRAPH,
  onChange: () => {},
  values: {},
  inputToggles: {},
  onToggleInput: () => {},
  errors: [],
};

/**
 * Spatial Glass guardrails.
 *
 * jsdom does not implement backdrop-filter or resolve custom properties
 * through a real cascade, so these assert the *contract* -- which element
 * carries which class, and what the stylesheet says those classes do --
 * rather than computed pixels. Composited contrast and real blur counts are
 * measured separately against a browser.
 */
describe('Spatial Glass: code surfaces never get translucency', () => {
  it('the code editor frame carries no-glass', () => {
    const { container } = render(<CodeEditor value="print('hi')" onChange={() => {}} />);
    const frame = container.querySelector('.no-glass');
    expect(frame, 'CodeEditor must carry .no-glass').not.toBeNull();
  });

  it('the terminal panel carries no-glass', () => {
    render(<TerminalPanel output="ok" data-testid="terminal-panel" />);
    expect(screen.getByTestId('terminal-panel').className).toContain('no-glass');
  });

  it('neither code surface carries a glass class', () => {
    const { container } = render(
      <>
        <CodeEditor value="x = 1" onChange={() => {}} />
        <TerminalPanel output="ok" data-testid="terminal-panel" />
      </>,
    );
    // A glass class anywhere on these frames would put the page behind them
    // underneath syntax-highlighted text.
    for (const el of container.querySelectorAll('.no-glass')) {
      expect(el.className).not.toMatch(/\bglass-surface\b|\bglass-flat\b|\bglass-raised\b/);
    }
  });

  it('.no-glass forces an opaque, unblurred surface in the stylesheet', () => {
    const rule = cssRule('.no-glass');
    expect(rule).toContain('--color-bg-code');
    // !important is load-bearing: this has to beat a glass utility on the
    // same element, and a silent regression is the failure it guards.
    expect(rule).toMatch(/background-color:[^;]*!important/);
    expect(rule).toMatch(/background-image:\s*none\s*!important/);
    expect(rule).toMatch(/backdrop-filter:\s*none\s*!important/);
  });
});

/**
 * `.no-blur` is the half of the old `.no-glass` that every work surface needs:
 * never composite the page behind it. It exists separately because the Circuit
 * Lab canvas needs exactly that and nothing else -- it paints its own ground
 * and its own grid, both of which `.no-glass` would overwrite.
 */
describe('Spatial Glass: .no-blur is the guard without the opaque ground', () => {
  it('kills backdrop-filter and nothing else', () => {
    const rule = cssRule('.no-blur');
    expect(rule).toMatch(/backdrop-filter:\s*none\s*!important/);
    expect(rule).toMatch(/-webkit-backdrop-filter:\s*none\s*!important/);
    // The whole point of the split: it must leave the caller's own background
    // alone, or the Circuit Lab grid and its 50% ground go with it.
    expect(rule, '.no-blur must not touch background-color').not.toMatch(/background-color/);
    expect(rule, '.no-blur must not touch background-image').not.toMatch(/background-image/);
  });

  it('the circuit lab canvas carries it', () => {
    render(<CircuitCanvas {...circuitProps} />);
    expect(screen.getByTestId('circuit-canvas-background').className).toContain('no-blur');
  });

  it('the circuit lab canvas carries no glass class', () => {
    render(<CircuitCanvas {...circuitProps} />);
    expect(screen.getByTestId('circuit-canvas-background').className).not.toMatch(
      /\bglass-surface\b|\bglass-flat\b|\bglass-raised\b/,
    );
  });
});

describe('Spatial Glass: list-rendered cards must not blur', () => {
  it('the default card variant is non-blurred glass', () => {
    const { container } = render(<Card>content</Card>);
    const el = container.firstElementChild!;
    expect(el.className).toContain('glass-flat');
    expect(el.className).not.toContain('glass-surface');
  });

  it('the interactive variant -- what list-rendered cards use -- is non-blurred', () => {
    // Courses renders 25 of these on one 5000px page; 25 live backdrop-filters
    // is the case the rollout plan ruled out.
    const { container } = render(<Card variant="interactive">content</Card>);
    expect(container.firstElementChild!.className).toContain('glass-flat');
    expect(container.firstElementChild!.className).not.toContain('glass-surface');
  });

  it('blur is opt-in via the explicit glass variant', () => {
    const { container } = render(<Card variant="glass">content</Card>);
    expect(container.firstElementChild!.className).toContain('glass-surface');
  });

  it('only the opt-in classes carry backdrop-filter in the stylesheet', () => {
    // .glass-flat and .glass-raised-flat must never gain one.
    const flat = css.slice(css.indexOf('.glass-surface,'), css.indexOf('.glass-surface {'));
    expect(flat).not.toContain('backdrop-filter');
  });
});

describe('Spatial Glass: RTL-safe paint', () => {
  it('the glass fill and button gradient are vertical, never angled', () => {
    // Paint does not mirror under dir="rtl", so an angled gradient would run
    // backwards in Arabic. Vertical (180deg) and radial are safe.
    const gradients = css.match(/--(?:glass-fill|btn-primary-gradient[a-z-]*):[^;]+;/g) ?? [];
    expect(gradients.length).toBeGreaterThan(0);
    for (const g of gradients) {
      if (g.includes('linear-gradient')) {
        expect(g, `${g} must be 180deg`).toContain('180deg');
      }
    }
  });

  it('glass shadows have no horizontal offset', () => {
    const shadows = css.match(/--glass-shadow[a-z-]*:[^;]+;/g) ?? [];
    expect(shadows.length).toBeGreaterThan(0);
    for (const decl of shadows) {
      const body = decl.slice(decl.indexOf(':') + 1);
      for (const layer of body.split(/,(?![^(]*\))/)) {
        // The first length in a box-shadow layer is the horizontal offset.
        // Match a bare `0` too -- `0 16px ...` is the common spelling, and a
        // px-only regex would skip it and check the vertical offset instead.
        const first = layer.trim().replace(/^inset\s+/, '').match(/^-?[\d.]+(?:px)?/);
        if (first) {
          expect(
            parseFloat(first[0]),
            `horizontal offset in "${layer.trim()}" must be 0 so it mirrors under RTL`,
          ).toBe(0);
        }
      }
    }
  });
});

describe('Spatial Glass: the primary gradient defers to a caller background', () => {
  it('applies the design-system gradient by default', () => {
    render(<Button>Go</Button>);
    expect(screen.getByRole('button').className).toContain('btn-primary-gradient');
  });

  it('stands aside when the caller paints its own background', () => {
    // Regression: .btn-primary-gradient is unlayered CSS, which beats every
    // Tailwind utility regardless of order, so without this the accent CTAs in
    // ExerciseAnswer / ExercisePanel / CircuitLabPanel / GitQuestPanel all
    // turned from orange to blue.
    render(
      <Button className="bg-gradient-to-r from-accent-700 to-accent-800">Submit Solution</Button>,
    );
    const el = screen.getByRole('button');
    expect(el.className).not.toContain('btn-primary-gradient');
    expect(el.className).toContain('from-accent-700');
  });

  it('only primary gets the gradient', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const el = screen.getByRole('button');
    expect(el.className).not.toContain('btn-primary-gradient');
    // Secondary is glass, and non-blurred so it can sit inside a glass card.
    expect(el.className).toContain('glass-flat');
  });
});
