import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

/**
 * The app is EN/FR/AR and mirrors under `dir="rtl"`, so spacing, alignment,
 * insets and corner radii have to be logical (`ms`/`me`, `ps`/`pe`,
 * `start`/`end`, `text-start`/`text-end`, `border-s`/`border-e`,
 * `rounded-ss`/`rounded-se`) rather than physical. A physical utility is
 * invisible in English and silently wrong in Arabic, which is exactly the
 * kind of thing no other test here catches.
 *
 * Physical is still correct in three cases, so each is allowlisted below with
 * a reason rather than excluded by a blanket pattern:
 *   - inside a `dir="ltr"` container (code never mirrors)
 *   - symmetric geometry (`left-1/2` centring, `left-0 right-0` pairs)
 *   - a named-direction API, where "left" is the caller's chosen placement
 *
 * Scope note: the allowlist is keyed on file + utility, not on a line, because
 * line numbers drift. So a NEW physical `text-left` added to a file already
 * allowlisted for `text-left` would not be caught. Catching that would need
 * per-element dir tracking; this guard is aimed at the common case of a
 * physical utility appearing in a file that has none today.
 */

const SRC = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

/** Physical utilities that have a logical counterpart. */
const PHYSICAL =
  /(?:^|[\s'"`])(-?(?:ml|mr|pl|pr)-[\w./[\]]+|text-(?:left|right)|-?(?:left|right)-[\w./[\]]+|border-[lr](?:-[\w./[\]]+)?|rounded-(?:[lr]|tl|tr|bl|br)(?:-[\w./[\]]+)?|-?translate-x-[\w./[\]]+)(?=$|[\s'"`])/g;

/**
 * Every `className` value in a file, as source text.
 *
 * Brace-aware on purpose. A className is often `className={cn('a', flag &&
 * 'b')}` spanning several lines and containing nested braces and quotes; a
 * `className="[^"]*"` regex matches none of those and a `{[^}]*}` one stops at
 * the first inner `}`. So walk instead: quoted values read to their closing
 * quote, braced values to the brace that balances, ignoring braces that sit
 * inside a string.
 */
function classNameValues(text: string): string[] {
  const out: string[] = [];
  const NEEDLE = 'className=';
  for (let i = text.indexOf(NEEDLE); i !== -1; i = text.indexOf(NEEDLE, i + 1)) {
    let j = i + NEEDLE.length;
    const open = text[j];
    if (open === '"' || open === "'") {
      const end = text.indexOf(open, j + 1);
      if (end !== -1) out.push(text.slice(j + 1, end));
      continue;
    }
    if (open !== '{') continue;
    let depth = 0;
    let quote: string | null = null;
    for (let k = j; k < text.length; k++) {
      const c = text[k];
      if (quote) {
        if (c === quote && text[k - 1] !== '\\') quote = null;
        continue;
      }
      if (c === '"' || c === "'" || c === '`') { quote = c; continue; }
      if (c === '{') depth++;
      else if (c === '}') {
        depth--;
        if (depth === 0) { out.push(text.slice(j + 1, k)); break; }
      }
    }
  }
  return out;
}

/** file -> utility -> why physical is correct here. */
const ALLOWLIST: Record<string, Record<string, string>> = {
  'components/ExerciseAnswer.tsx': {
    'text-left': 'inside dir="ltr" test-output and code blocks -- code never mirrors',
  },
  'components/breakTheCode/DebugTracePanel.tsx': {
    'text-left': 'inside the dir="ltr" <pre> source listing',
    'border-l-2': 'current-line marker inside the same dir="ltr" <pre>',
  },
  'components/ui/CodeBlock.tsx': {
    'text-left': 'the block sets dir="ltr" itself -- see its own comment',
  },
  'components/QuestNode.tsx': {
    'left-1/2': 'centring, paired with -translate-x-1/2; symmetric',
    '-translate-x-1/2': 'centring half-offset; symmetric',
  },
  'components/AchievementToast.tsx': {
    'left-1/2': 'centred toast stack; symmetric',
    '-translate-x-1/2': 'centring half-offset; symmetric',
  },
  'components/Layout.tsx': {
    'left-0': 'paired with right-0 on the full-width fixed header; symmetric',
    'right-0': 'paired with left-0 on the full-width fixed header; symmetric',
  },
  'components/ui/Dropdown.tsx': {
    'left-0': 'alignment already branches on isRTL; the pair is symmetric',
    'right-0': 'alignment already branches on isRTL; the pair is symmetric',
    'left-1/2': 'centre alignment, paired with -translate-x-1/2',
    '-translate-x-1/2': 'centring half-offset; symmetric',
    'ml-2': 'named-direction API: position="right" means physically right',
    'mr-2': 'named-direction API: position="left" means physically left',
    'left-full': 'named-direction API placement',
    'right-full': 'named-direction API placement',
  },
  'components/ui/Feedback.tsx': {
    'left-1/2': 'tooltip centring, paired with -translate-x-1/2',
    '-translate-x-1/2': 'centring half-offset; symmetric',
    'ml-2': 'named-direction API: position="right"',
    'mr-2': 'named-direction API: position="left"',
    'left-full': 'named-direction API placement',
    'right-full': 'named-direction API placement',
    'border-l-[5px]': 'CSS-triangle arrow geometry for the "left" placement',
    'border-r-[5px]': 'CSS-triangle arrow geometry for the "right" placement',
  },
  'components/ui/Overlay.tsx': {
    'left-0': 'named-direction API placement, paired with right-0',
    'right-0': 'named-direction API placement, paired with left-0',
    'left-1/2': 'centre placement, paired with -translate-x-1/2',
    '-translate-x-1/2': 'centring half-offset; symmetric',
  },
  // Both canvases position nodes with a JS-computed `style={{ left: x }}`
  // coordinate space, and the wire endpoints are computed against the same
  // left-based coordinates (circuitLayout.ts / getHandlePosition). Mirroring
  // the markup inside a node would move the port away from the wire that
  // attaches to it, so these stay physical deliberately.
  'components/circuitLab/CircuitNodeView.tsx': {
    '-translate-x-1/2': 'port centring in the JS-positioned canvas coordinate space',
    'translate-x-0.5': 'input toggle knob travel, in the same non-mirroring space',
    'translate-x-5': 'input toggle knob travel, in the same non-mirroring space',
  },
  'components/VisualNode.tsx': {
    'ml-auto': 'port dot in the JS-positioned canvas space; must stay where the wire attaches',
  },
  'pages/Login.tsx': {
    '-right-1': 'accent dot on the AtlasCode logo mark -- a brand mark does not mirror',
  },
  'pages/Register.tsx': {
    '-right-1': 'accent dot on the AtlasCode logo mark -- a brand mark does not mirror',
  },
  'pages/DuelArena.tsx': {
    'text-right': 'paired with flex-row-reverse in the two-sided arena header; needs a live duel to verify, so left unchanged rather than guessed',
  },
  'pages/Landing.tsx': {
    'text-left': 'inside the dir="ltr" <pre> code sample',
    'left-0': 'paired with right-0 on full-width fixed/absolute bands; symmetric',
    'right-0': 'paired with left-0 on full-width fixed/absolute bands; symmetric',
    'left-1/2': 'hero glow centring, paired with -translate-x-1/2',
    '-translate-x-1/2': 'decorative blob offset; Tailwind has no logical translate -- deferred with the Landing convergence phase',
    'translate-x-1/2': 'decorative blob offset; same deferral',
  },
};

describe('RTL: spacing and alignment use logical utilities', () => {
  const files = readdirSync(SRC, { recursive: true, encoding: 'utf-8' }).filter(
    (f) => f.endsWith('.tsx') && !f.includes('__tests__'),
  );

  it('scans a meaningful number of files', () => {
    // Guards the guard: a broken path would make every assertion below vacuous.
    expect(files.length).toBeGreaterThan(50);
  });

  it('finds no unexplained physical direction utility', () => {
    const offenders: string[] = [];
    for (const file of files) {
      const rel = file.split(path.sep).join('/');
      const allowed = ALLOWLIST[rel] ?? {};
      for (const value of classNameValues(readFileSync(path.join(SRC, file), 'utf-8'))) {
        for (const m of value.matchAll(PHYSICAL)) {
          const util = m[1];
          if (util in allowed) continue;
          offenders.push(`${rel}: ${util}`);
        }
      }
    }
    expect(
      [...new Set(offenders)].sort(),
      'physical utilities do not mirror under dir="rtl" -- use the logical form, ' +
        'or add an ALLOWLIST entry with a reason:',
    ).toEqual([]);
  });

  it('every allowlist entry carries a reason', () => {
    for (const [file, utils] of Object.entries(ALLOWLIST)) {
      for (const [util, reason] of Object.entries(utils)) {
        expect(reason.length, `${file} / ${util} needs a real reason`).toBeGreaterThan(20);
      }
    }
  });
});
