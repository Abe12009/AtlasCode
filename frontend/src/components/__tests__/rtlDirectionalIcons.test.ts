import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

/**
 * A directional icon has to mirror under `dir="rtl"`.
 *
 * A chevron that means "open this" points the way the reader is going, so in
 * Arabic it points left. Left unmirrored it points back at the text it came
 * from, which is the same class of defect as a physical margin: invisible in
 * English, wrong in Arabic.
 *
 * Three mechanisms count as mirrored, because the repo has all three:
 *   - `rtl:-scale-x-100` on the icon (what phase 6b added)
 *   - an `isRTL ? <ChevronRight/> : <ChevronLeft/>` component swap
 *   - `isRTL && 'rotate-180'` on the icon
 *
 * Only horizontally-directional icons are scanned. `ChevronDown`/`ChevronUp`
 * are vertical and must NOT be flipped; media controls, checkmarks, close and
 * plus/minus carry no reading direction at all, so they are out of scope
 * rather than allowlisted.
 */

const SRC = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

/** Horizontally-directional icons, plus the metaphor icons under review. */
const DIRECTIONAL = [
  'ArrowLeft', 'ArrowRight', 'ArrowUpRight', 'ArrowDownRight',
  'ChevronLeft', 'ChevronRight', 'ChevronsLeft', 'ChevronsRight',
  'MoveLeft', 'MoveRight', 'CornerDownLeft', 'CornerDownRight',
  'ExternalLink', 'Send', 'LogOut', 'LogIn', 'Reply', 'Undo', 'Redo',
];

const MIRRORED = /rtl:-scale-x-100|rotate-180/;

/**
 * Each `<Icon ... />` opening tag, whole.
 *
 * Brace-aware: these icons are nearly always passed as a prop
 * (`leftIcon={<ArrowRight className="…" />}`) or sit inside a ternary, so the
 * tag is surrounded by braces and often contains `{cn(...)}` in its own
 * className. A `<Icon[^>]*>` regex stops at the first `>` it meets -- which
 * can be one inside a nested element or a `=>` in a prop -- and would read
 * the wrong text. Walk instead, ending the tag on a `>` at brace depth 0.
 */
function iconTags(text: string, icon: string): { tag: string; index: number }[] {
  const found: { tag: string; index: number }[] = [];
  const needle = `<${icon}`;
  for (let i = text.indexOf(needle); i !== -1; i = text.indexOf(needle, i + 1)) {
    // `<ChevronRight` must not match `<ChevronRightSomething`.
    const after = text[i + needle.length];
    if (after && /[A-Za-z0-9_]/.test(after)) continue;
    let depth = 0;
    let quote: string | null = null;
    for (let j = i; j < text.length; j++) {
      const c = text[j];
      if (quote) {
        if (c === quote && text[j - 1] !== '\\') quote = null;
        continue;
      }
      if (c === '"' || c === "'" || c === '`') { quote = c; continue; }
      if (c === '{') depth++;
      else if (c === '}') depth--;
      else if (c === '>' && depth === 0) { found.push({ tag: text.slice(i, j + 1), index: i }); break; }
    }
  }
  return found;
}

/** file -> icon -> why it does not mirror. */
const ALLOWLIST: Record<string, Record<string, string>> = {
  'components/CodyChatPanel.tsx': {
    Send: 'paper-plane send button -- a transmit metaphor, not navigation; reserved for a product decision (F16)',
  },
  'pages/ProjectDetail.tsx': {
    ExternalLink: 'opens an external URL -- the arrow is a "leaves the app" metaphor; reserved for a product decision (F16)',
  },
  'components/Layout.tsx': {
    LogOut: 'exit metaphor in a menu, not a next/back affordance',
  },
  'pages/Profile.tsx': {
    LogOut: 'exit metaphor in a menu, not a next/back affordance',
  },
};

describe('RTL: directional icons mirror', () => {
  const files = readdirSync(SRC, { recursive: true, encoding: 'utf-8' }).filter(
    (f) => f.endsWith('.tsx') && !f.includes('__tests__'),
  );

  it('scans a meaningful number of files', () => {
    // Guards the guard: a bad path would make the assertion below vacuous.
    expect(files.length).toBeGreaterThan(50);
  });

  it('finds no directional icon that stays put in Arabic', () => {
    const offenders: string[] = [];
    for (const file of files) {
      const rel = file.split(path.sep).join('/');
      const text = readFileSync(path.join(SRC, file), 'utf-8');
      const allowed = ALLOWLIST[rel] ?? {};
      for (const icon of DIRECTIONAL) {
        if (icon in allowed) continue;
        for (const { tag, index } of iconTags(text, icon)) {
          if (MIRRORED.test(tag)) continue;
          // An `isRTL ? <ChevronRight/> : <ChevronLeft/>` swap mirrors by
          // choosing the icon, so the tag itself carries no marker -- look at
          // the line the tag starts on.
          const lineStart = text.lastIndexOf('\n', index) + 1;
          let lineEnd = text.indexOf('\n', index);
          if (lineEnd === -1) lineEnd = text.length;
          if (text.slice(lineStart, lineEnd).includes('isRTL')) continue;
          offenders.push(`${rel}: ${icon}`);
        }
      }
    }
    expect(
      [...new Set(offenders)].sort(),
      'a directional icon must mirror under dir="rtl" -- add `rtl:-scale-x-100` ' +
        'to its className, or an ALLOWLIST entry with a reason:',
    ).toEqual([]);
  });

  it('a horizontal hover nudge mirrors with its icon', () => {
    // `group-hover:translate-x-1` slides the arrow toward the reader. Left
    // alone it slides the wrong way in Arabic, so each one is paired
    // ltr:/rtl: rather than left unqualified.
    const offenders: string[] = [];
    for (const file of files) {
      const rel = file.split(path.sep).join('/');
      const text = readFileSync(path.join(SRC, file), 'utf-8');
      // Tokenise, then inspect whole class tokens. Matching the utility with
      // a lookbehind does not work: `(?:group-)?` lets the match start at
      // `hover:` inside `ltr:group-hover:translate-x-1`, so the lookbehind
      // sees `group-` and the already-correct pair reports as an offender.
      for (const token of text.match(/[A-Za-z0-9:_\-./[\]]+/g) ?? []) {
        if (!token.includes('hover:') || !token.includes('translate-x-')) continue;
        if (token.startsWith('ltr:') || token.startsWith('rtl:')) continue;
        offenders.push(`${rel}: ${token}`);
      }
    }
    expect(
      [...new Set(offenders)].sort(),
      'an unqualified horizontal hover translate slides the wrong way in RTL -- ' +
        'pair it as ltr:…/rtl:…:',
    ).toEqual([]);
  });

  it('every allowlist entry carries a reason', () => {
    for (const [file, icons] of Object.entries(ALLOWLIST)) {
      for (const [icon, reason] of Object.entries(icons)) {
        expect(reason.length, `${file} / ${icon} needs a real reason`).toBeGreaterThan(20);
      }
    }
  });
});
