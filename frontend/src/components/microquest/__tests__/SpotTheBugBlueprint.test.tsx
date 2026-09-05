import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../test/setup.tsx';
import { Blueprint } from '../Blueprint';
import { SpotTheBugBlueprint } from '../SpotTheBugBlueprint';
import { isSpotTheBugConfig } from '../types';
import type { SpotTheBugConfig } from '../types';

const CONFIG: SpotTheBugConfig = {
  kind: 'spot_the_bug',
  snippet: 'left, right = 0, len(arr)\nwhile left <= right:\n    mid = (left + right) // 2',
  statements: [
    {
      id: 'sorted',
      text: { en: 'Binary search requires the array to already be sorted.', fr: "La recherche binaire exige un tableau déjà trié.", ar: 'يتطلب البحث الثنائي أن تكون المصفوفة مرتّبة مسبقًا.' },
    },
    {
      id: 'halves',
      text: { en: 'Each comparison discards half of the remaining search space.', fr: 'Chaque comparaison élimine la moitié de l’espace de recherche restant.', ar: 'كل مقارنة تستبعد نصف مساحة البحث المتبقية.' },
    },
    {
      id: 'bound',
      text: { en: 'The initial right bound should be len(arr), not len(arr) - 1.', fr: 'La borne droite initiale doit être len(arr), pas len(arr) - 1.', ar: 'يجب أن يكون الحد الأيمن الابتدائي len(arr)، وليس len(arr) - 1.' },
    },
    {
      id: 'logn',
      text: { en: 'Binary search runs in O(log n) time.', fr: 'La recherche binaire s’exécute en O(log n).', ar: 'يعمل البحث الثنائي بزمن O(log n).' },
    },
  ],
  buggy_id: 'bound',
  success: {
    en: 'Exactly — the initial right bound must be the last valid index, len(arr) - 1.',
    fr: 'Exactement — la borne droite initiale doit être le dernier index valide, len(arr) - 1.',
    ar: 'بالضبط — يجب أن يكون الحد الأيمن الابتدائي هو آخر فهرس صالح، len(arr) - 1.',
  },
  hint: {
    en: 'Which one of these describes an off-by-one boundary, not a real property of the algorithm?',
    fr: "Laquelle décrit une erreur de décalage d'un cran, plutôt qu'une vraie propriété de l'algorithme ?",
    ar: 'أيها يصف خطأ إزاحة بمقدار واحد، لا خاصية حقيقية للخوارزمية؟',
  },
};

async function renderBlueprint(
  overrides: { language?: string; solved?: boolean; onSolved?: () => void } = {},
) {
  const onSolved = overrides.onSolved ?? vi.fn();
  const rendered = await renderWithProviders(
    <SpotTheBugBlueprint
      config={CONFIG}
      language={overrides.language ?? 'en'}
      solved={overrides.solved ?? false}
      onSolved={onSolved}
    />,
    { initialLanguage: overrides.language ?? 'en' },
  );
  return { onSolved, ...rendered };
}

describe('SpotTheBugBlueprint rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders every statement as a radio option', async () => {
    await renderBlueprint();
    const radios = screen.getAllByRole('radio');
    expect(radios).toHaveLength(4);
    expect(screen.getByText(/requires the array to already be sorted/i)).toBeInTheDocument();
    expect(screen.getByText(/runs in O\(log n\) time/i)).toBeInTheDocument();
  });

  it('renders the optional snippet through the shared LTR code block', async () => {
    await renderBlueprint();
    const snippet = screen.getByTestId('spot-bug-snippet');
    expect(snippet).toHaveAttribute('dir', 'ltr');
    expect(snippet).toHaveTextContent('while left <= right');
  });

  it('omits the snippet entirely when the config has none', async () => {
    const onSolved = vi.fn();
    await renderWithProviders(
      <SpotTheBugBlueprint
        config={{ ...CONFIG, snippet: undefined }}
        language="en"
        solved={false}
        onSolved={onSolved}
      />,
    );
    expect(screen.queryByTestId('spot-bug-snippet')).not.toBeInTheDocument();
  });

  it('starts with nothing selected and Check disabled', async () => {
    await renderBlueprint();
    expect(screen.getAllByRole('radio').every((r) => !(r as HTMLInputElement).checked)).toBe(true);
    expect(screen.getByTestId('blueprint-check')).toBeDisabled();
  });
});

describe('SpotTheBugBlueprint interaction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('selects exactly one statement at a time, like any radio group', async () => {
    const user = userEvent.setup();
    await renderBlueprint();

    await user.click(screen.getByTestId('spot-bug-statement-sorted').querySelector('input')!);
    await user.click(screen.getByTestId('spot-bug-statement-logn').querySelector('input')!);

    const checked = screen.getAllByRole('radio').filter((r) => (r as HTMLInputElement).checked);
    expect(checked).toHaveLength(1);
    expect(checked[0]).toHaveAttribute('value', 'logn');
  });

  it('rejects a true statement mistaken for the bug, with a hint', async () => {
    const user = userEvent.setup();
    const { onSolved } = await renderBlueprint();

    await user.click(screen.getByTestId('spot-bug-statement-halves').querySelector('input')!);
    await user.click(screen.getByTestId('blueprint-check'));

    const feedback = await screen.findByTestId('blueprint-feedback');
    expect(feedback).toHaveTextContent(/actually true/i);
    expect(feedback).toHaveTextContent(/off-by-one boundary/i);
    expect(onSolved).not.toHaveBeenCalled();
  });

  it('accepts the actually-buggy statement and reports it once', async () => {
    const user = userEvent.setup();
    const { onSolved } = await renderBlueprint();

    await user.click(screen.getByTestId('spot-bug-statement-bound').querySelector('input')!);
    await user.click(screen.getByTestId('blueprint-check'));

    // `solved` is owned by the parent (MicroQuestLesson): it flips to true and
    // is passed back down only after `onSolved` fires, which is what this
    // asserts — the same contract MatchPairsBlueprint and BlueprintOrderSteps
    // follow, so the success alert itself is exercised in the "renders the
    // success alert when the parent says it is solved" case below.
    await waitFor(() => expect(onSolved).toHaveBeenCalledTimes(1));
  });

  it('renders the authored success line once the parent marks it solved', async () => {
    await renderBlueprint({ solved: true });
    const feedback = await screen.findByTestId('blueprint-feedback');
    expect(feedback).toHaveTextContent(/last valid index/i);
  });

  it('lets a student change their mind after a wrong pick and then succeed', async () => {
    const user = userEvent.setup();
    const { onSolved } = await renderBlueprint();

    await user.click(screen.getByTestId('spot-bug-statement-sorted').querySelector('input')!);
    await user.click(screen.getByTestId('blueprint-check'));
    await screen.findByTestId('blueprint-feedback');

    await user.click(screen.getByTestId('spot-bug-statement-bound').querySelector('input')!);
    expect(screen.queryByTestId('blueprint-feedback')).not.toBeInTheDocument();

    await user.click(screen.getByTestId('blueprint-check'));
    await waitFor(() => expect(onSolved).toHaveBeenCalledTimes(1));
  });

  it('locks the radios once solved', async () => {
    await renderBlueprint({ solved: true });
    for (const radio of screen.getAllByRole('radio')) {
      expect(radio).toBeDisabled();
    }
    expect(screen.queryByTestId('blueprint-check')).not.toBeInTheDocument();
  });
});

describe('SpotTheBugBlueprint internationalization', () => {
  beforeEach(() => localStorage.clear());

  it('renders French statement text', async () => {
    await renderBlueprint({ language: 'fr' });
    expect(await screen.findByText(/exige un tableau déjà trié/i)).toBeInTheDocument();
    expect(screen.getByTestId('blueprint-check')).toHaveTextContent(/vérifier la réponse/i);
  });

  it('renders Arabic statement text', async () => {
    await renderBlueprint({ language: 'ar' });
    expect(await screen.findByText(/يتطلب البحث الثنائي/)).toBeInTheDocument();
    expect(screen.getByTestId('spot-bug-statements').textContent).toMatch(/[؀-ۿ]/);
  });

  it('keeps the snippet LTR even in Arabic', async () => {
    await renderBlueprint({ language: 'ar' });
    expect(screen.getByTestId('spot-bug-snippet')).toHaveAttribute('dir', 'ltr');
  });
});

describe('Blueprint dispatch for spot_the_bug', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders the spot-the-bug puzzle for kind spot_the_bug', async () => {
    await renderWithProviders(
      <Blueprint config={CONFIG} language="en" solved={false} onSolved={vi.fn()} />,
    );
    expect(await screen.findByTestId('spot-bug-statements')).toBeInTheDocument();
  });

  it.each([
    ['fewer than three statements', { kind: 'spot_the_bug', statements: [{ id: 'a', text: { en: 'A' } }, { id: 'b', text: { en: 'B' } }], buggy_id: 'a' }],
    ['a buggy_id that names no statement', { kind: 'spot_the_bug', statements: [{ id: 'a', text: { en: 'A' } }, { id: 'b', text: { en: 'B' } }, { id: 'c', text: { en: 'C' } }], buggy_id: 'zz' }],
    ['duplicate statement ids', { kind: 'spot_the_bug', statements: [{ id: 'a', text: { en: 'A' } }, { id: 'a', text: { en: 'A2' } }, { id: 'c', text: { en: 'C' } }], buggy_id: 'a' }],
    ['a statement missing localized text', { kind: 'spot_the_bug', statements: [{ id: 'a' }, { id: 'b', text: { en: 'B' } }, { id: 'c', text: { en: 'C' } }], buggy_id: 'b' }],
  ])('degrades gracefully for %s and unlocks the quest anyway', async (_label, config) => {
    const onSolved = vi.fn();
    await renderWithProviders(
      <Blueprint config={config as never} language="en" solved={false} onSolved={onSolved} />,
    );

    const fallback = await screen.findByTestId('blueprint-unsupported');
    expect(fallback).toHaveTextContent(/could not be loaded/i);
    expect(screen.queryByTestId('spot-bug-statements')).not.toBeInTheDocument();
    await waitFor(() => expect(onSolved).toHaveBeenCalled());
  });
});

describe('spot_the_bug config guard', () => {
  it('accepts the reference config', () => {
    expect(isSpotTheBugConfig(CONFIG as never)).toBe(true);
  });

  it('accepts a config with no snippet', () => {
    expect(isSpotTheBugConfig({ ...CONFIG, snippet: undefined } as never)).toBe(true);
  });

  it.each([
    ['a non-string snippet', { ...CONFIG, snippet: 42 }],
    ['fewer than three statements', { ...CONFIG, statements: CONFIG.statements.slice(0, 2) }],
    ['a buggy_id absent from the statements', { ...CONFIG, buggy_id: 'nope' }],
    ['duplicate statement ids', { ...CONFIG, statements: [CONFIG.statements[0], CONFIG.statements[0], CONFIG.statements[1]] }],
  ])('rejects %s', (_label, config) => {
    expect(isSpotTheBugConfig(config as never)).toBe(false);
  });
});
