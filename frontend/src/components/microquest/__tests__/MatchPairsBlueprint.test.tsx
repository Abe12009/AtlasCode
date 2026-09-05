import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../test/setup.tsx';
import { Blueprint } from '../Blueprint';
import { MatchPairsBlueprint } from '../MatchPairsBlueprint';
import { shuffledRight } from '../shuffleRight';
import { isMatchPairsConfig, isOrderStepsConfig } from '../types';
import type { MatchPairsConfig } from '../types';

const CONFIG: MatchPairsConfig = {
  kind: 'match_pairs',
  pairs: [
    {
      id: 'loop',
      left: { en: 'for loop', fr: 'boucle for', ar: 'حلقة for' },
      right: {
        en: 'repeats instructions',
        fr: 'répète des instructions',
        ar: 'تكرّر التعليمات',
      },
    },
    {
      id: 'branch',
      left: { en: 'if statement', fr: 'instruction if', ar: 'تعليمة if' },
      right: { en: 'makes a decision', fr: 'prend une décision', ar: 'تتخذ قرارًا' },
    },
    {
      id: 'variable',
      left: { en: 'variable', fr: 'variable', ar: 'متغيّر' },
      right: { en: 'stores a value', fr: 'stocke une valeur', ar: 'يخزّن قيمة' },
    },
    {
      id: 'function',
      left: { en: 'function', fr: 'fonction', ar: 'دالة' },
      right: {
        en: 'groups reusable code',
        fr: 'regroupe du code réutilisable',
        ar: 'تجمع شيفرة قابلة لإعادة الاستعمال',
      },
    },
  ],
  success: {
    en: 'Every pair is right.',
    fr: 'Chaque paire est juste.',
    ar: 'كل زوج صحيح.',
  },
  hint: {
    en: 'Read the right-hand phrase first.',
    fr: "Lisez d'abord la phrase de droite.",
    ar: 'اقرأ العبارة على اليمين أولًا.',
  },
};

const PAIR_IDS = CONFIG.pairs.map((pair) => pair.id);

/** Connect every left item to the right item it belongs with. */
async function matchCorrectly(user: ReturnType<typeof userEvent.setup>) {
  for (const id of PAIR_IDS) {
    await user.click(screen.getByTestId(`match-left-${id}`));
    await user.click(screen.getByTestId(`match-right-${id}`));
  }
}

/** Connect every left item to somebody else's right item. Rotating by one
 * guarantees not a single connection is right. */
async function matchIncorrectly(user: ReturnType<typeof userEvent.setup>) {
  for (let i = 0; i < PAIR_IDS.length; i++) {
    await user.click(screen.getByTestId(`match-left-${PAIR_IDS[i]}`));
    await user.click(screen.getByTestId(`match-right-${PAIR_IDS[(i + 1) % PAIR_IDS.length]}`));
  }
}

async function renderBlueprint(
  overrides: { language?: string; solved?: boolean; onSolved?: () => void } = {},
) {
  const onSolved = overrides.onSolved ?? vi.fn();
  const rendered = await renderWithProviders(
    <MatchPairsBlueprint
      config={CONFIG}
      language={overrides.language ?? 'en'}
      solved={overrides.solved ?? false}
      onSolved={onSolved}
    />,
    { initialLanguage: overrides.language ?? 'en' },
  );
  return { onSolved, ...rendered };
}

describe('MatchPairsBlueprint rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders both columns, one entry per pair', async () => {
    await renderBlueprint();
    await waitFor(() => expect(screen.getByTestId('match-pairs')).toBeInTheDocument());

    expect(screen.getAllByTestId(/^match-left-/)).toHaveLength(4);
    expect(screen.getAllByTestId(/^match-right-/)).toHaveLength(4);
    expect(screen.getByText('for loop')).toBeInTheDocument();
    expect(screen.getByText('groups reusable code')).toBeInTheDocument();
  });

  it('does not present the right column already lined up with the left one', async () => {
    // Otherwise the puzzle solves itself by matching row against row.
    await renderBlueprint();
    const rightOrder = screen
      .getAllByTestId(/^match-right-/)
      .map((node) => node.getAttribute('data-testid'));
    expect(rightOrder).not.toEqual(PAIR_IDS.map((id) => `match-right-${id}`));
  });

  it('starts with nothing connected and the check button unavailable', async () => {
    await renderBlueprint();
    expect(screen.getByTestId('match-progress')).toHaveTextContent('0 of 4');
    expect(screen.getByTestId('blueprint-check')).toBeDisabled();
    expect(screen.queryByTestId('blueprint-feedback')).not.toBeInTheDocument();
  });
});

describe('MatchPairsBlueprint interaction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('connects a left item to a right item in two taps', async () => {
    const user = userEvent.setup();
    await renderBlueprint();

    await user.click(screen.getByTestId('match-left-loop'));
    expect(screen.getByTestId('match-left-loop')).toHaveAttribute('aria-pressed', 'true');

    await user.click(screen.getByTestId('match-right-loop'));
    expect(screen.getByTestId('match-left-loop')).toHaveAttribute('data-connected', '1');
    expect(screen.getByTestId('match-right-loop')).toHaveAttribute('data-connected', '1');
    expect(screen.getByTestId('match-progress')).toHaveTextContent('1 of 4');
  });

  it('connects in either direction — right first works too', async () => {
    const user = userEvent.setup();
    await renderBlueprint();

    await user.click(screen.getByTestId('match-right-variable'));
    await user.click(screen.getByTestId('match-left-variable'));
    expect(screen.getByTestId('match-left-variable')).toHaveAttribute('data-connected', '1');
  });

  it('disconnects a pair when a connected item is tapped again', async () => {
    const user = userEvent.setup();
    await renderBlueprint();

    await user.click(screen.getByTestId('match-left-loop'));
    await user.click(screen.getByTestId('match-right-loop'));
    expect(screen.getByTestId('match-progress')).toHaveTextContent('1 of 4');

    await user.click(screen.getByTestId('match-left-loop'));
    expect(screen.getByTestId('match-progress')).toHaveTextContent('0 of 4');
    expect(screen.getByTestId('match-left-loop')).toHaveAttribute('data-connected', '');
  });

  it('only offers the check once every pair is connected', async () => {
    const user = userEvent.setup();
    await renderBlueprint();

    for (const id of PAIR_IDS.slice(0, 3)) {
      await user.click(screen.getByTestId(`match-left-${id}`));
      await user.click(screen.getByTestId(`match-right-${id}`));
    }
    expect(screen.getByTestId('match-progress')).toHaveTextContent('3 of 4');
    expect(screen.getByTestId('blueprint-check')).toBeDisabled();

    const last = PAIR_IDS[3];
    await user.click(screen.getByTestId(`match-left-${last}`));
    await user.click(screen.getByTestId(`match-right-${last}`));
    expect(screen.getByTestId('match-progress')).toHaveTextContent('4 of 4');
    expect(screen.getByTestId('blueprint-check')).toBeEnabled();
  });
});

describe('MatchPairsBlueprint correctness', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('rejects a complete but wrong set of connections, with a hint', async () => {
    const user = userEvent.setup();
    const { onSolved } = await renderBlueprint();

    await matchIncorrectly(user);
    await user.click(screen.getByTestId('blueprint-check'));

    const feedback = await screen.findByTestId('blueprint-feedback');
    expect(feedback).toHaveTextContent(/not right yet/i);
    expect(feedback).toHaveTextContent(/read the right-hand phrase first/i);
    expect(onSolved).not.toHaveBeenCalled();
  });

  it('accepts the correct set of connections and reports it once', async () => {
    const user = userEvent.setup();
    const { onSolved } = await renderBlueprint();

    await matchCorrectly(user);
    await user.click(screen.getByTestId('blueprint-check'));

    expect(onSolved).toHaveBeenCalledTimes(1);
  });

  it('renders the success alert when the parent says it is solved', async () => {
    await renderBlueprint({ solved: true });
    const feedback = await screen.findByTestId('blueprint-feedback');
    expect(feedback).toHaveTextContent('Every pair is right.');
    // Solved is final: no check button, no way to undo the connections.
    expect(screen.queryByTestId('blueprint-check')).not.toBeInTheDocument();
    expect(screen.getByTestId('match-left-loop')).toBeDisabled();
  });

  it('lets a student start over after a wrong attempt and then succeed', async () => {
    const user = userEvent.setup();
    const { onSolved } = await renderBlueprint();

    await matchIncorrectly(user);
    await user.click(screen.getByTestId('blueprint-check'));
    await screen.findByTestId('blueprint-feedback');

    await user.click(screen.getByTestId('match-reset'));
    expect(screen.getByTestId('match-progress')).toHaveTextContent('0 of 4');
    expect(screen.queryByTestId('blueprint-feedback')).not.toBeInTheDocument();

    await matchCorrectly(user);
    await user.click(screen.getByTestId('blueprint-check'));
    expect(onSolved).toHaveBeenCalledTimes(1);
  });

  it('clears stale error feedback as soon as the student changes something', async () => {
    const user = userEvent.setup();
    await renderBlueprint();

    await matchIncorrectly(user);
    await user.click(screen.getByTestId('blueprint-check'));
    await screen.findByTestId('blueprint-feedback');

    await user.click(screen.getByTestId('match-left-loop'));
    expect(screen.queryByTestId('blueprint-feedback')).not.toBeInTheDocument();
  });
});

describe('MatchPairsBlueprint layout', () => {
  beforeEach(() => localStorage.clear());

  it('lays the two columns out side by side, each able to shrink and wrap', async () => {
    // jsdom does no layout, so what is asserted here is the contract that
    // makes 320px work; the pixel proof lives in the Playwright viewport runs.
    await renderBlueprint();
    expect(screen.getByTestId('match-pairs').className).toContain('grid-cols-2');
    for (const item of screen.getAllByTestId(/^match-(left|right)-/)) {
      expect(item.className).toContain('min-w-0');
      expect(item.className).toContain('break-words');
    }
  });
});

describe('MatchPairsBlueprint internationalization', () => {
  beforeEach(() => localStorage.clear());

  it('renders French pair text', async () => {
    await renderBlueprint({ language: 'fr' });
    expect(await screen.findByText('boucle for')).toBeInTheDocument();
    expect(screen.getByText('regroupe du code réutilisable')).toBeInTheDocument();
    expect(screen.getByTestId('blueprint-check')).toHaveTextContent(/vérifier les associations/i);
  });

  it('renders Arabic pair text', async () => {
    await renderBlueprint({ language: 'ar' });
    expect(await screen.findByText('تكرّر التعليمات')).toBeInTheDocument();
    expect(screen.getByTestId('match-pairs').textContent).toMatch(/[؀-ۿ]/);
  });

  it('falls back to English for a language the config does not carry', async () => {
    await renderBlueprint({ language: 'es' });
    expect(await screen.findByText('for loop')).toBeInTheDocument();
  });

  it('shows the same puzzle in every language', async () => {
    // The right column is seeded from the pair ids, so switching language must
    // not reshuffle the answers under the student.
    const ids = shuffledRight(CONFIG.pairs).map((pair) => pair.id);
    expect(shuffledRight(CONFIG.pairs).map((pair) => pair.id)).toEqual(ids);
    expect(ids).toHaveLength(CONFIG.pairs.length);
    expect(new Set(ids)).toEqual(new Set(PAIR_IDS));
  });
});

describe('Blueprint dispatch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders the matching puzzle for kind match_pairs', async () => {
    await renderWithProviders(
      <Blueprint config={CONFIG} language="en" solved={false} onSolved={vi.fn()} />,
    );
    expect(await screen.findByTestId('match-pairs')).toBeInTheDocument();
  });

  it('renders the ordering puzzle for kind order_steps', async () => {
    await renderWithProviders(
      <Blueprint
        config={{
          kind: 'order_steps',
          steps: [
            { id: 'a', label: { en: 'First' } },
            { id: 'b', label: { en: 'Second' } },
          ],
          correct_order: ['a', 'b'],
        }}
        language="en"
        solved={false}
        onSolved={vi.fn()}
      />,
    );
    expect(await screen.findByTestId('blueprint-steps')).toBeInTheDocument();
  });

  it.each([
    ['an unknown kind', { kind: 'draw_flowchart', nodes: [] }],
    ['a missing kind', { steps: [] }],
    ['a config that is not an object', null],
    ['order_steps with a correct_order that is not a permutation', {
      kind: 'order_steps',
      steps: [{ id: 'a', label: { en: 'First' } }, { id: 'b', label: { en: 'Second' } }],
      correct_order: ['a', 'zz'],
    }],
    ['match_pairs with a pair missing a side', {
      kind: 'match_pairs',
      pairs: [{ id: 'a', left: { en: 'A' } }, { id: 'b', left: { en: 'B' }, right: { en: 'b' } }],
    }],
  ])('degrades gracefully for %s and unlocks the quest anyway', async (_label, config) => {
    const onSolved = vi.fn();
    await renderWithProviders(
      <Blueprint config={config as never} language="en" solved={false} onSolved={onSolved} />,
    );

    const fallback = await screen.findByTestId('blueprint-unsupported');
    expect(fallback).toHaveTextContent(/could not be loaded/i);
    expect(screen.queryByTestId('match-pairs')).not.toBeInTheDocument();
    expect(screen.queryByTestId('blueprint-steps')).not.toBeInTheDocument();
    // A broken warm-up must never block the graded exercise behind it.
    await waitFor(() => expect(onSolved).toHaveBeenCalled());
  });
});

describe('blueprint config guards', () => {
  it('accepts the configs the reference lessons actually ship', () => {
    expect(isMatchPairsConfig(CONFIG as never)).toBe(true);
    expect(
      isOrderStepsConfig({
        kind: 'order_steps',
        steps: [
          { id: 'a', label: { en: 'First' } },
          { id: 'b', label: { en: 'Second' } },
        ],
        correct_order: ['a', 'b'],
      }),
    ).toBe(true);
  });

  it.each([
    ['a single pair', { kind: 'match_pairs', pairs: [{ id: 'a', left: { en: 'A' }, right: { en: 'a' } }] }],
    ['duplicate pair ids', {
      kind: 'match_pairs',
      pairs: [
        { id: 'a', left: { en: 'A' }, right: { en: 'a' } },
        { id: 'a', left: { en: 'B' }, right: { en: 'b' } },
      ],
    }],
    ['pairs that are not a list', { kind: 'match_pairs', pairs: 'loop' }],
    ['a pair with no id', { kind: 'match_pairs', pairs: [{ left: { en: 'A' }, right: { en: 'a' } }, { id: 'b', left: { en: 'B' }, right: { en: 'b' } }] }],
  ])('rejects match_pairs with %s', (_label, config) => {
    expect(isMatchPairsConfig(config as never)).toBe(false);
  });

  it.each([
    ['a single step', { kind: 'order_steps', steps: [{ id: 'a', label: { en: 'A' } }], correct_order: ['a'] }],
    ['a correct_order of the wrong length', {
      kind: 'order_steps',
      steps: [{ id: 'a', label: { en: 'A' } }, { id: 'b', label: { en: 'B' } }],
      correct_order: ['a'],
    }],
    ['a step with no label', {
      kind: 'order_steps',
      steps: [{ id: 'a' }, { id: 'b', label: { en: 'B' } }],
      correct_order: ['a', 'b'],
    }],
  ])('rejects order_steps with %s', (_label, config) => {
    expect(isOrderStepsConfig(config as never)).toBe(false);
  });
});
