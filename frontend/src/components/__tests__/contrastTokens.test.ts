import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

/**
 * Real contrast ratios, computed from the declared token values.
 *
 * This is a genuine WCAG calculation rather than a string check: it resolves
 * each token through its `var()` chain to a hex value and ratios the pair. It
 * runs in vitest because every pair asserted here is OPAQUE on both sides, so
 * the maths is exact and needs no renderer.
 *
 * What it deliberately does NOT cover: anything translucent composited over an
 * ambient field or a glass fill -- dark's badge pills are
 * `color-mix(..., transparent)` over a drifting backdrop, and no static
 * calculation can predict that. Those are measured from rendered pixels in a
 * browser instead, and the numbers live in docs/spatial-glass-plan.md.
 *
 * Both failures this pins were real and measured:
 *   - light status badges: a dark-mode recipe reused in light put a 400-step
 *     foreground on a pale pill -- 1.02:1 in situ for `completed`.
 *   - dark --color-text-quaternary: 4.46:1 on --color-bg-elevated, which is
 *     where it actually renders (the FALSE label on a Circuit Lab node).
 */

const css = readFileSync(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../index.css'),
  'utf-8',
);

/** A top-level declaration block, by its opening selector or at-rule. */
function block(opening: string): string {
  const start = css.indexOf(`${opening} {`);
  if (start === -1) throw new Error(`${opening} not found in index.css`);
  return css.slice(start, css.indexOf('\n}', start));
}

const THEME = block('@theme');
const LIGHT = block(':root');
const DARK = block('[data-theme="dark"]');

/** A custom property's declared value, searching the given blocks in order. */
function declared(name: string, blocks: string[]): string {
  for (const b of blocks) {
    const m = b.match(new RegExp(`${name}\\s*:\\s*([^;]+);`));
    if (m) return m[1].trim();
  }
  throw new Error(`${name} not declared`);
}

/** Resolve a token through its var() chain to a literal value. */
function resolve(name: string, blocks: string[], depth = 0): string {
  if (depth > 8) throw new Error(`${name}: var() chain too deep`);
  const value = declared(name, blocks);
  const m = value.match(/^var\((--[\w-]+)\)$/);
  return m ? resolve(m[1], blocks, depth + 1) : value;
}

function rgb(hex: string): [number, number, number] {
  const h = hex.trim().replace('#', '');
  if (!/^[0-9a-fA-F]{6}$/.test(h)) throw new Error(`not an opaque hex colour: "${hex}"`);
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16)) as [number, number, number];
}

function luminance(c: [number, number, number]): number {
  const f = c.map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2];
}

function ratio(fg: string, bg: string): number {
  const [hi, lo] = [luminance(rgb(fg)), luminance(rgb(bg))].sort((a, b) => b - a);
  return (hi + 0.05) / (lo + 0.05);
}

const FLOOR = 4.5; // normal-size body text

describe('contrast: light status badges clear the floor', () => {
  // Light resolves these to opaque ramp steps, so the ratio is exact.
  const HUES = ['success', 'primary', 'accent', 'warning'] as const;

  it.each(HUES)('%s badge is readable in light', (hue) => {
    const fg = resolve(`--badge-${hue}-fg`, [LIGHT, THEME]);
    const bg = resolve(`--badge-${hue}-bg`, [LIGHT, THEME]);
    const r = ratio(fg, bg);
    expect(
      r,
      `--badge-${hue}-fg ${fg} on --badge-${hue}-bg ${bg} is ${r.toFixed(2)}:1, below ${FLOOR}:1`,
    ).toBeGreaterThanOrEqual(FLOOR);
  });

  it('dark keeps a translucent pill, which only a browser can measure', () => {
    // Pinned so a well-meaning "simplification" to an opaque light value in
    // the dark block is caught here rather than in a screenshot.
    for (const hue of HUES) {
      expect(declared(`--badge-${hue}-bg`, [DARK])).toContain('color-mix');
      expect(declared(`--badge-${hue}-fg`, [DARK])).toContain('-400');
    }
  });
});

describe('contrast: text-quaternary clears every surface it lands on', () => {
  // It renders on code and canvas surfaces, not on glass: the one glass call
  // site (StatusBadge's unearned branch) is unreachable, since both callers
  // pass earned={true}.
  const DARK_SURFACES = [
    '--color-bg-primary',
    '--color-bg-secondary',
    '--color-bg-tertiary',
    '--color-bg-elevated',
    '--color-bg-code',
  ];

  it.each(DARK_SURFACES)('dark: readable on %s', (surface) => {
    const fg = resolve('--color-text-quaternary', [DARK, THEME]);
    const bg = resolve(surface, [DARK, THEME]);
    const r = ratio(fg, bg);
    expect(
      r,
      `--color-text-quaternary ${fg} on ${surface} ${bg} is ${r.toFixed(2)}:1, below ${FLOOR}:1`,
    ).toBeGreaterThanOrEqual(FLOOR);
  });

  it('light: readable on the page and elevated surfaces', () => {
    const fg = resolve('--color-text-quaternary', [LIGHT, THEME]);
    for (const surface of ['--color-bg-primary', '--color-bg-elevated']) {
      const r = ratio(fg, resolve(surface, [LIGHT, THEME]));
      expect(r, `light text-quaternary on ${surface} is ${r.toFixed(2)}:1`).toBeGreaterThanOrEqual(FLOOR);
    }
  });
});

describe('contrast: the guard itself works', () => {
  it('computes a known ratio correctly', () => {
    // Black on white is 21:1 exactly; if this drifts the maths is wrong and
    // every assertion above is meaningless.
    expect(ratio('#000000', '#ffffff')).toBeCloseTo(21, 5);
    expect(ratio('#ffffff', '#ffffff')).toBeCloseTo(1, 5);
  });

  it('refuses a non-opaque value rather than guessing', () => {
    expect(() => rgb('color-mix(in oklab, red 30%, transparent)')).toThrow(/opaque hex/);
  });
});
