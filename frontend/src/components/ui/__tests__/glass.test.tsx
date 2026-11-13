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

/** A top-level declaration block, by its opening selector or at-rule. */
function cssBlock(opening: string): string {
  const start = css.indexOf(`${opening} {`);
  if (start === -1) throw new Error(`${opening} block not found in index.css`);
  return css.slice(start, css.indexOf('\n}', start));
}

/** A custom property's declared value inside one block. */
function tokenIn(block: string, name: string): string {
  const m = block.match(new RegExp(`${name}\\s*:\\s*([^;]+);`));
  if (!m) throw new Error(`${name} not declared in that block`);
  return m[1].trim();
}

/** Resolve one level of `var(--x)` against a block of colour declarations. */
function resolveVar(value: string, colours: string): string {
  const m = value.match(/^var\((--[\w-]+)\)$/);
  return m ? tokenIn(colours, m[1]) : value;
}

/** WCAG relative luminance of a #rrggbb colour. */
function luminance(hex: string): number {
  const h = hex.replace('#', '');
  const ch = [0, 2, 4]
    .map((i) => parseInt(h.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
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

/**
 * `.bg-grid-pattern` sets `opacity` on the element (index.css), and opacity
 * applies to the whole subtree. Put it on a container that holds content and
 * every wire and node inside renders at 0.05 -- which is exactly what the
 * Circuit Lab and the Visual Programming canvas were doing, measured in a
 * browser at `ownOpacity: "0.05"` with each child at `effectiveOpacity: 0.05`.
 *
 * So the rule is: the grid is always its own childless, decorative layer.
 */
describe('Spatial Glass: the grid never wraps content', () => {
  it('the stylesheet rule is opacity-based, which is why this matters', () => {
    // If this ever stops being true the childless requirement can relax --
    // but then this whole describe block should go, not just this assertion.
    expect(cssRule('.bg-grid-pattern')).toMatch(/opacity:/);
  });

  it('the circuit lab grid is a childless, aria-hidden layer', () => {
    render(<CircuitCanvas {...circuitProps} />);
    const grid = screen.getByTestId('circuit-canvas-grid');
    expect(grid.className).toContain('bg-grid-pattern');
    expect(grid.getAttribute('aria-hidden')).toBe('true');
    expect(grid.children.length, 'the grid layer must stay childless').toBe(0);
    // Without this the canvas's own onClick stops clearing the selection:
    // it only fires when `e.target === e.currentTarget`.
    expect(grid.className).toContain('pointer-events-none');
  });

  it('the canvas itself no longer carries the grid class', () => {
    render(<CircuitCanvas {...circuitProps} />);
    expect(screen.getByTestId('circuit-canvas-background').className).not.toContain(
      'bg-grid-pattern',
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

/**
 * The secondary button's hover and press.
 *
 * They were `hover:bg-bg-quaternary active:bg-bg-tertiary` utilities and
 * never painted: `.glass-flat` sets background-color unlayered in index.css,
 * which beats `@layer utilities` whatever the specificity. Measured in
 * Chromium with forced pseudo-states before the fix -- rest, :hover and
 * :active were byte-identical in both themes, so the control had no pointer
 * feedback at all.
 *
 * jsdom does not do this cascade, so these pin the contract: the component
 * opts into `.glass-interactive`, and that class really does declare both
 * states in the stylesheet.
 */
describe('Spatial Glass: interactive glass has real hover and press', () => {
  it('the secondary button opts in, and carries no dead state utilities', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const el = screen.getByRole('button');
    expect(el.className).toContain('glass-interactive');
    // The utilities these replaced could never win against .glass-flat, so
    // their return would be a silent regression to no feedback at all.
    expect(el.className).not.toMatch(/\bhover:bg-/);
    expect(el.className).not.toMatch(/\bactive:bg-/);
  });

  it('declares a hover fill and a press fill, distinct from each other', () => {
    const hover = cssRule('.glass-interactive:hover:not(:disabled)');
    const press = cssRule('.glass-interactive:active:not(:disabled)');
    expect(hover).toMatch(/background-color:\s*var\(--glass-hover\)/);
    expect(press).toMatch(/background-color:\s*var\(--glass-press\)/);
    expect(hover).not.toEqual(press);
  });

  it('both state tokens are defined in both themes', () => {
    // Dark-only behaviour lives in token VALUES, not a component branch, so
    // each token must resolve in light as well -- an undefined custom
    // property would drop the declaration and silently restore the bug.
    for (const token of ['--glass-hover', '--glass-press']) {
      const occurrences = css.match(new RegExp(`${token}:`, 'g')) ?? [];
      expect(occurrences.length, `${token} must be declared in light and dark`).toBe(2);
    }
  });

  /**
   * Press must read at least as strong as hover, in both themes.
   *
   * This shipped inverted in light: the fills were inherited from the Button
   * variant's own `hover:bg-bg-quaternary active:bg-bg-tertiary`, and on the
   * light ramp tertiary (#E4EAF3) is LIGHTER than quaternary (#D6E0EC) -- so
   * pressing made the surface lighter than hovering and the press read as a
   * release. `outline` and `ghost` have always had it the other way round.
   */
  it('light: hover darkens off the resting surface, and press darkens further', () => {
    const root = cssBlock(':root');
    const palette = cssBlock('@theme');
    const hover = luminance(resolveVar(tokenIn(root, '--glass-hover'), palette));
    const press = luminance(resolveVar(tokenIn(root, '--glass-press'), palette));
    // Light glass resolves --glass-base to the opaque elevated surface.
    const rest = luminance(tokenIn(palette, '--color-bg-elevated'));

    expect(hover, 'hover must be darker than the resting surface').toBeLessThan(rest);
    expect(press, 'press must be at least as strong as hover').toBeLessThan(hover);
  });

  it('dark: press is a heavier fill than hover', () => {
    const dark = cssBlock('[data-theme="dark"]');
    const alpha = (value: string) => {
      const m = value.match(/\/\s*([\d.]+)\s*\)/);
      if (!m) throw new Error(`no alpha channel in "${value}"`);
      return parseFloat(m[1]);
    };
    expect(
      alpha(tokenIn(dark, '--glass-press')),
      'press must be at least as strong as hover',
    ).toBeGreaterThan(alpha(tokenIn(dark, '--glass-hover')));
  });

  it('only opts-in elements get the states -- never Card\'s default', () => {
    // .glass-flat is Card's default variant, so folding hover into it would
    // light up every list-rendered card under the pointer.
    const { container } = render(<Card>content</Card>);
    expect(container.firstElementChild!.className).toContain('glass-flat');
    expect(container.firstElementChild!.className).not.toContain('glass-interactive');
  });
});
