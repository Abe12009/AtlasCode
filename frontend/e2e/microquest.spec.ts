import { test, expect, Page } from '@playwright/test';
import { registerNewUser, trackPageHealth } from './helpers';

/**
 * Every Micro-Quest lesson, end to end, against the real backend and the real
 * database. Nothing in this file is mocked: every blueprint is solved through
 * the controls a student sees, every exercise is graded by the real grader,
 * and every XP figure is read back from /dashboard.
 *
 * Phases 8-10 (4 lessons):
 *   lesson  9  code_writing    + order_steps    15 XP
 *   lesson 36  multiple_choice + order_steps    10 XP
 *   lesson 12  prediction      + match_pairs    10 XP
 *   lesson 38  debugging       + spot_the_bug   15 XP
 *
 * Phase 11 (10 more lessons -- see app/seed/microquest_content_phase11.py
 * for why exactly these 10):
 *   lesson 16  code_writing    + match_pairs    10 XP
 *   lesson 13  code_writing    + order_steps    15 XP
 *   lesson 15  fill_blank      + spot_the_bug   10 XP
 *   lesson 18  multiple_choice + order_steps    10 XP
 *   lesson 23  multiple_choice + match_pairs    10 XP
 *   lesson 26  multiple_choice + match_pairs    10 XP
 *   lesson 29  code_writing    + spot_the_bug   15 XP
 *   lesson 45  multiple_choice + order_steps    10 XP
 *   lesson 47  multiple_choice + spot_the_bug   10 XP
 *   lesson 32  ordering        + match_pairs    10 XP
 */

type BlueprintPlan =
  | { kind: 'order_steps'; order: string[] }
  | { kind: 'match_pairs'; pairs: string[] }
  | { kind: 'spot_the_bug'; correctId: string; wrongId: string };

interface Quest {
  name: string;
  lessonId: number;
  xp: number;
  blueprint: BlueprintPlan;
  /** Fills in an answer the backend will reject. */
  answerWrong: (page: Page) => Promise<void>;
  /** Fills in the answer the backend accepts. */
  answerCorrect: (page: Page) => Promise<void>;
  /** Clicks whatever this exercise type calls "submit". */
  submit: (page: Page) => Promise<void>;
  /** A phrase that must appear in the hook, per language. */
  hookText: { en: RegExp; fr: RegExp; ar: RegExp };
}

const CODE_SOLUTION =
  'total = 0\nfor i in range(1, 21):\n    if i % 2 == 0:\n        total += i\nprint("Sum of evens:", total)';

/** Exercise 47's options are chosen by their visible text, never by id, so the
 * test picks the way a student picks. */
const ALGORITHM_CORRECT_OPTION = 'Runs forever';
const ALGORITHM_WRONG_OPTION = 'Finiteness';

async function clickOption(page: Page, text: string) {
  await page.getByRole('radio').first().waitFor();
  await page.locator('label', { hasText: text }).first().locator('input[type="radio"]').check();
}

async function submitCode(page: Page) {
  await page.getByRole('button', { name: /submit solution/i }).click();
}

async function submitAnswer(page: Page) {
  await page.getByTestId('submit-answer').click();
}

/** Fills an ordering exercise's fill-in-value blanks, by index, in order. */
function fillBlanks(exerciseId: number, values: string[]) {
  return async (page: Page) => {
    for (let i = 0; i < values.length; i++) {
      await page.locator(`#blank-${exerciseId}-${i}`).fill(values[i]);
    }
  };
}

/** Arranges an ordering exercise's items into the given order, by their
 * visible text — the same selection-sort-by-move-up technique solveBlueprint
 * uses for order_steps, just reading DOM position instead of a data
 * attribute, since ExerciseAnswerPanel's ordering-item elements carry a
 * numeric option id, not a stable slug. */
function arrangeOrdering(textsInOrder: string[]) {
  return async (page: Page) => {
    const items = page.getByTestId('ordering-list').locator('li');
    for (let target = 0; target < textsInOrder.length; target++) {
      for (let guard = 0; guard < textsInOrder.length + 2; guard++) {
        const count = await items.count();
        let currentIndex = -1;
        for (let i = 0; i < count; i++) {
          const text = await items.nth(i).innerText();
          if (text.includes(textsInOrder[target])) {
            currentIndex = i;
            break;
          }
        }
        if (currentIndex === target) break;
        await items.nth(currentIndex).locator('button').first().click(); // "move up"
        await page.waitForTimeout(60);
      }
    }
  };
}

const QUESTS: Record<string, Quest> = {
  code: {
    name: 'lesson 9 — code_writing + order_steps',
    lessonId: 9,
    xp: 15,
    blueprint: { kind: 'order_steps', order: ['init', 'visit', 'decide', 'update'] },
    answerWrong: async (page) => {
      await page.locator('textarea').first().fill('print("not even close")');
    },
    answerCorrect: async (page) => {
      await page.locator('textarea').first().fill(CODE_SOLUTION);
    },
    submit: submitCode,
    hookText: { en: /locker/i, fr: /casiers/i, ar: /الخزانات/ },
  },
  mcq: {
    name: 'lesson 36 — multiple_choice + order_steps',
    lessonId: 36,
    xp: 10,
    blueprint: {
      kind: 'order_steps',
      order: ['input', 'assume', 'compare', 'replace', 'output'],
    },
    answerWrong: async (page) => clickOption(page, ALGORITHM_WRONG_OPTION),
    answerCorrect: async (page) => clickOption(page, ALGORITHM_CORRECT_OPTION),
    submit: submitAnswer,
    hookText: { en: /tallest person/i, fr: /la plus grande/i, ar: /أطول شخص/ },
  },
  prediction: {
    name: 'lesson 12 — prediction + match_pairs',
    lessonId: 12,
    xp: 10,
    blueprint: {
      kind: 'match_pairs',
      pairs: ['local', 'global', 'parameter', 'return'],
    },
    answerWrong: async (page) => {
      await page.locator('#prediction-22').fill('Inside: 10\nOutside: 20');
    },
    answerCorrect: async (page) => {
      await page.locator('#prediction-22').fill('Inside: 20\nOutside: 10');
    },
    submit: submitAnswer,
    hookText: { en: /classmate/i, fr: /camarade/i, ar: /زميل/ },
  },
  debugging: {
    name: 'lesson 38 — debugging + spot_the_bug',
    lessonId: 38,
    xp: 15,
    blueprint: { kind: 'spot_the_bug', correctId: 'bound', wrongId: 'sorted' },
    answerWrong: async (page) => {
      await page.locator('textarea').first().fill('def binary_search(arr, target):\n    return None');
    },
    answerCorrect: async (page) => {
      await page
        .locator('textarea')
        .first()
        .fill(
          'def binary_search(arr, target):\n' +
            '    left, right = 0, len(arr) - 1\n' +
            '    while left <= right:\n' +
            '        mid = (left + right) // 2\n' +
            '        if arr[mid] == target:\n' +
            '            return mid\n' +
            '        elif arr[mid] < target:\n' +
            '            left = mid + 1\n' +
            '        else:\n' +
            '            right = mid - 1\n' +
            '    return -1',
        );
    },
    submit: submitCode,
    hookText: { en: /phone book/i, fr: /annuaire/i, ar: /دفتر هاتف/ },
  },

  // -------------------------------------------------------------------
  // Phase 11's ten additional lessons.
  // -------------------------------------------------------------------
  dictionaries: {
    name: 'lesson 16 — code_writing + match_pairs',
    lessonId: 16,
    xp: 10,
    blueprint: { kind: 'match_pairs', pairs: ['assign', 'get_safe', 'delete', 'membership'] },
    answerWrong: async (page) => {
      await page.locator('textarea').first().fill("print('nope')");
    },
    answerCorrect: async (page) => {
      await page
        .locator('textarea')
        .first()
        .fill(
          'product = {\n    "name": "Tagine",\n    "price": 150,\n    "in_stock": True\n}\n' +
            'product["price"] = 180\nprint(product)',
        );
    },
    submit: submitCode,
    hookText: { en: /contact list/i, fr: /carnet d'adresses/i, ar: /دفتر عناوين/ },
  },
  decomposition: {
    name: 'lesson 13 — code_writing + order_steps',
    lessonId: 13,
    xp: 15,
    blueprint: { kind: 'order_steps', order: ['state', 'split', 'write', 'combine'] },
    answerWrong: async (page) => {
      await page.locator('textarea').first().fill("print('nope')");
    },
    answerCorrect: async (page) => {
      await page
        .locator('textarea')
        .first()
        .fill(
          'def is_even(n):\n    return n % 2 == 0\n\n' +
            'def count_evens(numbers):\n    count = 0\n    for n in numbers:\n' +
            '        if is_even(n):\n            count += 1\n    return count\n\n' +
            'print(count_evens([1,2,3,4,5,6,7,8,9,10]))',
        );
    },
    submit: submitCode,
    hookText: { en: /40-line function/i, fr: /40 lignes/i, ar: /40 سطرًا/ },
  },
  tuplesSets: {
    name: 'lesson 15 — fill_blank + spot_the_bug',
    lessonId: 15,
    xp: 10,
    blueprint: { kind: 'spot_the_bug', correctId: 'editable', wrongId: 'immutable' },
    answerWrong: fillBlanks(26, ['1', '2', 'green']),
    answerCorrect: fillBlanks(26, ['10', '20', 'blue']),
    submit: submitAnswer,
    hookText: { en: /exam dates/i, fr: /dates d'examen/i, ar: /تواريخ الامتحانات/ },
  },
  howWebWorks: {
    name: 'lesson 18 — multiple_choice + order_steps',
    lessonId: 18,
    xp: 10,
    blueprint: { kind: 'order_steps', order: ['send', 'process', 'respond', 'render'] },
    answerWrong: async (page) => clickOption(page, 'Stores all website data'),
    answerCorrect: async (page) => clickOption(page, 'Requests and displays web pages'),
    submit: submitAnswer,
    hookText: { en: /web address/i, fr: /adresse web/i, ar: /عنوان موقع/ },
  },
  selectors: {
    name: 'lesson 23 — multiple_choice + match_pairs',
    lessonId: 23,
    xp: 10,
    blueprint: {
      kind: 'match_pairs',
      pairs: ['class_sel', 'id_sel', 'hover_sel', 'descendant_sel'],
    },
    answerWrong: async (page) => clickOption(page, 'nav > a'),
    answerCorrect: async (page) => clickOption(page, 'nav a'),
    submit: submitAnswer,
    hookText: { en: /stylesheet has one rule/i, fr: /feuille de style a une règle/i, ar: /ورقة الأنماط/ },
  },
  databasesTables: {
    name: 'lesson 26 — multiple_choice + match_pairs',
    lessonId: 26,
    xp: 10,
    blueprint: { kind: 'match_pairs', pairs: ['row', 'column', 'pk', 'fk'] },
    answerWrong: async (page) => clickOption(page, 'A column that can be empty'),
    answerCorrect: async (page) => clickOption(page, 'A unique identifier for each row'),
    submit: submitAnswer,
    hookText: { en: /student records/i, fr: /dossiers des élèves/i, ar: /سجلات تلاميذ/ },
  },
  sortingGrouping: {
    name: 'lesson 29 — code_writing + spot_the_bug',
    lessonId: 29,
    xp: 15,
    blueprint: {
      kind: 'spot_the_bug',
      correctId: 'having_before',
      wrongId: 'where_first',
    },
    answerWrong: async (page) => {
      await page.locator('textarea').first().fill('SELECT * FROM nowhere;');
    },
    answerCorrect: async (page) => {
      await page
        .locator('textarea')
        .first()
        .fill('SELECT city, AVG(age) as avg_age\nFROM students\nGROUP BY city\nHAVING COUNT(*) >= 1;');
    },
    submit: submitCode,
    hookText: { en: /average grade per class/i, fr: /moyenne des notes par classe/i, ar: /معدّل النقط لكل قسم/ },
  },
  memoryStorage: {
    name: 'lesson 45 — multiple_choice + order_steps',
    lessonId: 45,
    xp: 10,
    blueprint: { kind: 'order_steps', order: ['registers', 'cache', 'ram', 'disk'] },
    answerWrong: async (page) => clickOption(page, 'SSD'),
    answerCorrect: async (page) => clickOption(page, 'RAM'),
    submit: submitAnswer,
    hookText: { en: /under a nanosecond/i, fr: /nanoseconde/i, ar: /نانوثانية/ },
  },
  networksInternet: {
    name: 'lesson 47 — multiple_choice + spot_the_bug',
    lessonId: 47,
    xp: 10,
    blueprint: {
      kind: 'spot_the_bug',
      correctId: 'private_direct',
      wrongId: 'dns',
    },
    answerWrong: async (page) => clickOption(page, 'UDP'),
    answerCorrect: async (page) => clickOption(page, 'TCP'),
    submit: submitAnswer,
    hookText: { en: /school's wifi/i, fr: /wifi d'une école/i, ar: /شبكة WiFi/ },
  },
  commitsHistory: {
    name: 'lesson 32 — ordering + match_pairs',
    lessonId: 32,
    xp: 10,
    blueprint: { kind: 'match_pairs', pairs: ['log', 'diff', 'show', 'head_parent'] },
    answerWrong: arrangeOrdering([
      'git log --oneline',
      'git commit -m "Initial commit"',
      'git add .',
      'git init',
    ]),
    answerCorrect: arrangeOrdering([
      'git init',
      'git add .',
      'git commit -m "Initial commit"',
      'git log --oneline',
    ]),
    submit: submitAnswer,
    hookText: { en: /200 commits/i, fr: /200 commits/i, ar: /200 تسجيلة/ },
  },
};

const ALL_QUESTS = Object.values(QUESTS);

function lessonPath(quest: Quest) {
  return `/app/lessons/${quest.lessonId}`;
}

/** Solves whichever blueprint the lesson ships, using only the controls the UI
 * exposes — no direct state access, no shortcuts. */
async function solveBlueprint(page: Page, quest: Quest) {
  await expect(page.getByTestId('blueprint')).toBeVisible();

  if (quest.blueprint.kind === 'order_steps') {
    const order = quest.blueprint.order;
    for (let target = 0; target < order.length; target++) {
      for (let guard = 0; guard < order.length + 2; guard++) {
        const item = page.getByTestId(`blueprint-step-${order[target]}`);
        const position = Number(await item.getAttribute('data-position'));
        if (position === target) break;
        await item.locator('button').first().click(); // "move up"
        await page.waitForTimeout(60);
      }
    }
  } else if (quest.blueprint.kind === 'match_pairs') {
    for (const id of quest.blueprint.pairs) {
      await page.getByTestId(`match-left-${id}`).click();
      await page.getByTestId(`match-right-${id}`).click();
    }
  } else {
    const item = page.getByTestId(`spot-bug-statement-${quest.blueprint.correctId}`);
    await item.locator('input').check();
  }
  await page.getByTestId('blueprint-check').click();
}

/** A complete but deliberately wrong blueprint attempt. */
async function failBlueprint(page: Page, quest: Quest) {
  await expect(page.getByTestId('blueprint')).toBeVisible();
  if (quest.blueprint.kind === 'order_steps') {
    // The steps start shuffled and never start solved, so checking straight
    // away is a genuine wrong answer.
    await page.getByTestId('blueprint-check').click();
    return;
  }
  if (quest.blueprint.kind === 'spot_the_bug') {
    const item = page.getByTestId(`spot-bug-statement-${quest.blueprint.wrongId}`);
    await item.locator('input').check();
    await page.getByTestId('blueprint-check').click();
    return;
  }
  const pairs = quest.blueprint.pairs;
  for (let i = 0; i < pairs.length; i++) {
    await page.getByTestId(`match-left-${pairs[i]}`).click();
    await page.getByTestId(`match-right-${pairs[(i + 1) % pairs.length]}`).click();
  }
  await page.getByTestId('blueprint-check').click();
}

async function readXp(page: Page): Promise<number> {
  const dashboard = await page.evaluate(async () => {
    const res = await fetch('http://localhost:8000/dashboard', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    return res.json();
  });
  return dashboard.profile.xp as number;
}

async function readLessonStatus(page: Page, lessonId: number): Promise<string> {
  return page.evaluate(async (id) => {
    const res = await fetch(`http://localhost:8000/lessons/${id}/progress`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    return (await res.json()).status as string;
  }, lessonId);
}

/** Every Micro-Quest stage key this browser is holding, and its value. */
async function storedStages(page: Page): Promise<Record<string, string>> {
  return page.evaluate(() => {
    const out: Record<string, string> = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i) as string;
      if (key.startsWith('atlascode.microquest.stage')) out[key] = localStorage.getItem(key) as string;
    }
    return out;
  });
}

async function openQuest(page: Page, quest: Quest) {
  await page.goto(lessonPath(quest));
  await expect(page.getByTestId('micro-quest')).toBeVisible({ timeout: 15000 });
}

async function reachQuestStage(page: Page, quest: Quest) {
  await openQuest(page, quest);
  await page.getByTestId('hook-continue').click();
  await solveBlueprint(page, quest);
  await page.getByTestId('blueprint-continue').click();
  await expect(page.getByTestId('quest-stage')).toBeVisible();
}

// ---------------------------------------------------------------------------
// The full journey, once per exercise type / blueprint type combination.
// ---------------------------------------------------------------------------

for (const quest of ALL_QUESTS) {
  test.describe(`Micro-Quest: ${quest.name}`, () => {
    test('Hook -> Blueprint -> real exercise -> real XP -> Quest Clear -> reload', async ({
      page,
    }) => {
      test.setTimeout(150000);
      await registerNewUser(page);

      expect(await readXp(page)).toBe(0);

      // 1. Hook.
      await openQuest(page, quest);
      await expect(page.getByTestId('quest-stage-hook')).toHaveAttribute('data-status', 'current');
      await expect(page.getByTestId('quest-hook')).toContainText(quest.hookText.en);
      await page.getByTestId('hook-continue').click();
      await expect(page.getByTestId('quest-stage-blueprint')).toHaveAttribute(
        'data-status',
        'current',
      );

      // 2. Blueprint: a real wrong attempt first, then the right one.
      // Each blueprint kind phrases its own rejection differently (order_steps
      // and match_pairs both happen to say "not"; spot_the_bug instead names
      // the statement actually true) — this matches all of them.
      await failBlueprint(page, quest);
      await expect(page.getByTestId('blueprint-feedback')).toContainText(/not|actually true/i);
      await expect(page.getByTestId('blueprint-continue')).toHaveCount(0);
      expect(await readXp(page), 'the blueprint must never award XP').toBe(0);

      if (quest.blueprint.kind === 'match_pairs') {
        await page.getByTestId('match-reset').click();
      }
      await solveBlueprint(page, quest);
      await expect(page.getByTestId('blueprint-feedback')).toBeVisible();
      await page.getByTestId('blueprint-continue').click();
      await expect(page.getByTestId('quest-stage-quest')).toHaveAttribute('data-status', 'current');

      // 3. The exercise, graded by the real backend: wrong first, then right.
      await expect(page.getByTestId('quest-stage')).toBeVisible();
      await quest.answerWrong(page);
      await quest.submit(page);
      await expect(page.getByTestId('exercise-result')).toContainText(/incorrect/i, {
        timeout: 20000,
      });
      expect(await readXp(page)).toBe(0);
      expect(await readLessonStatus(page, quest.lessonId)).not.toBe('completed');

      await quest.answerCorrect(page);
      await quest.submit(page);

      // 4. Quest Clear, showing the XP the backend actually awarded.
      const clear = page.getByTestId('quest-clear');
      await expect(clear).toBeVisible({ timeout: 20000 });
      await expect(clear).toContainText(/quest clear/i);
      await expect(page.getByTestId('quest-clear-xp')).toContainText(String(quest.xp));
      await expect(page.getByTestId('quest-stage-complete')).toHaveAttribute(
        'data-status',
        'current',
      );
      await expect.poll(async () => await readXp(page), { timeout: 15000 }).toBe(quest.xp);
      expect(await readLessonStatus(page, quest.lessonId)).toBe('completed');

      // 5. Reload: the completed state survives, and no XP is paid twice.
      await page.reload();
      await expect(page.getByTestId('quest-clear')).toBeVisible({ timeout: 15000 });
      await expect(page.getByTestId('quest-clear-xp')).toContainText(String(quest.xp));
      expect(await readXp(page)).toBe(quest.xp);

      // 6. And it still survives with nothing left in localStorage: completion
      //    is the backend's to state, not the browser's to remember.
      await page.evaluate(() => {
        for (let i = localStorage.length - 1; i >= 0; i--) {
          const key = localStorage.key(i) as string;
          if (key.startsWith('atlascode.microquest.stage')) localStorage.removeItem(key);
        }
      });
      await page.reload();
      await expect(page.getByTestId('quest-clear')).toBeVisible({ timeout: 15000 });
      expect(await readXp(page)).toBe(quest.xp);
    });
  });
}

// ---------------------------------------------------------------------------
// Stage persistence across reloads.
// ---------------------------------------------------------------------------

test.describe('Micro-Quest stage survives a reload', () => {
  test('a student who reached the Blueprint comes back to the Blueprint', async ({ page }) => {
    test.setTimeout(90000);
    await registerNewUser(page);
    const quest = QUESTS.code;

    await openQuest(page, quest);
    await page.getByTestId('hook-continue').click();
    await expect(page.getByTestId('blueprint')).toBeVisible();

    await page.reload();
    await expect(page.getByTestId('blueprint')).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId('quest-hook')).toHaveCount(0);
    await expect(page.getByTestId('quest-stage-blueprint')).toHaveAttribute(
      'data-status',
      'current',
    );
  });

  test('a student who reached the Quest is not asked to solve the blueprint again', async ({
    page,
  }) => {
    test.setTimeout(90000);
    await registerNewUser(page);
    const quest = QUESTS.prediction;

    await reachQuestStage(page, quest);

    await page.reload();
    await expect(page.getByTestId('quest-stage')).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId('quest-stage-quest')).toHaveAttribute('data-status', 'current');
    await expect(page.getByTestId('match-pairs')).toHaveCount(0);
  });

  test('each Micro-Quest lesson keeps its own position', async ({ page }) => {
    test.setTimeout(120000);
    await registerNewUser(page);

    await reachQuestStage(page, QUESTS.code);

    // A different Micro-Quest starts at its own Hook, untouched by the first.
    await openQuest(page, QUESTS.mcq);
    await expect(page.getByTestId('quest-hook')).toBeVisible();

    // And going back to the first one resumes exactly where it was left.
    await openQuest(page, QUESTS.code);
    await expect(page.getByTestId('quest-stage')).toBeVisible();

    const stored = await storedStages(page);
    expect(Object.keys(stored).length).toBeGreaterThanOrEqual(2);
    expect(Object.keys(stored).some((key) => key.endsWith(':9'))).toBe(true);
    expect(Object.keys(stored).some((key) => key.endsWith(':36'))).toBe(true);
  });

  test('the stored value is a stage and nothing else', async ({ page }) => {
    await registerNewUser(page);
    await openQuest(page, QUESTS.code);
    await page.getByTestId('hook-continue').click();
    await expect(page.getByTestId('blueprint')).toBeVisible();

    const stored = await storedStages(page);
    const values = Object.values(stored).map((raw) => JSON.parse(raw));
    expect(values).toContainEqual({ v: 1, stage: 'blueprint' });
  });
});

test.describe('Micro-Quest stage storage cannot mislead the app', () => {
  test('a corrupt stored value falls back to the Hook without breaking the page', async ({
    page,
  }) => {
    test.setTimeout(90000);
    const health = trackPageHealth(page);
    await registerNewUser(page);
    const quest = QUESTS.code;

    await openQuest(page, quest);
    await page.getByTestId('hook-continue').click();
    await expect(page.getByTestId('blueprint')).toBeVisible();

    // Everything a hand-edited or half-written value could look like.
    for (const corrupt of ['wat', '[]', '{"v":1}', '{"v":1,"stage":"banana"}', '']) {
      await page.evaluate((value) => {
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i) as string;
          if (key.startsWith('atlascode.microquest.stage')) localStorage.setItem(key, value);
        }
      }, corrupt);
      await page.reload();
      await expect(page.getByTestId('quest-hook'), `corrupt value ${corrupt}`).toBeVisible({
        timeout: 15000,
      });
    }
    health.assertNoFailures();
  });

  test('a missing stored value falls back to the Hook', async ({ page }) => {
    await registerNewUser(page);
    await openQuest(page, QUESTS.code);
    await page.getByTestId('hook-continue').click();
    await expect(page.getByTestId('blueprint')).toBeVisible();

    // Clear the remembered stage only — clearing the access token as well
    // would be testing logout, not a missing stage.
    await page.evaluate(() => {
      for (let i = localStorage.length - 1; i >= 0; i--) {
        const key = localStorage.key(i) as string;
        if (key.startsWith('atlascode.microquest.stage')) localStorage.removeItem(key);
      }
    });
    await page.reload();
    await expect(page.getByTestId('quest-hook')).toBeVisible({ timeout: 15000 });
  });

  test('a hand-written "complete" does not conjure a Quest Clear', async ({ page }) => {
    test.setTimeout(90000);
    await registerNewUser(page);
    const quest = QUESTS.code;

    await reachQuestStage(page, quest);
    await page.evaluate(() => {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i) as string;
        if (key.startsWith('atlascode.microquest.stage')) {
          localStorage.setItem(key, JSON.stringify({ v: 1, stage: 'complete' }));
        }
      }
    });
    await page.reload();

    // The backend never graded anything, so the student lands back on the
    // exercise — not on a congratulations screen with an invented XP figure.
    await expect(page.getByTestId('quest-stage')).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId('quest-clear')).toHaveCount(0);
    expect(await readXp(page)).toBe(0);
  });
});

test('one student never sees another student’s Micro-Quest position', async ({ page }) => {
  test.setTimeout(150000);
  await registerNewUser(page);
  await reachQuestStage(page, QUESTS.code);
  const afterFirst = await storedStages(page);
  expect(Object.keys(afterFirst)).toHaveLength(1);

  // Sign out through the UI, then sign a different student in on the same
  // browser, with the first student's entry still sitting in localStorage.
  await page.goto('/app/dashboard');
  await page.getByRole('button', { name: 'Profile' }).first().click();
  await page.getByRole('menuitem', { name: 'Logout' }).click();
  await expect(page).toHaveURL(/\/login$/, { timeout: 15000 });

  await registerNewUser(page);
  await page.goto('/app/lessons/9');
  await expect(page.getByTestId('micro-quest')).toBeVisible({ timeout: 15000 });
  await expect(page.getByTestId('quest-hook')).toBeVisible();
  await expect(page.getByTestId('quest-stage')).toHaveCount(0);

  // The first student's position is scoped to them and still intact.
  const afterSecond = await storedStages(page);
  for (const [key, value] of Object.entries(afterFirst)) {
    expect(afterSecond[key]).toBe(value);
  }
  expect(Object.keys(afterSecond).length).toBeGreaterThan(Object.keys(afterFirst).length);
});

// ---------------------------------------------------------------------------
// Languages.
// ---------------------------------------------------------------------------

async function switchLanguage(page: Page, label: RegExp) {
  await page.goto('/app/dashboard');
  await page.locator('button', { hasText: /English|Français|العربية/i }).first().click();
  await page.getByRole('menuitem', { name: label }).click();
  await page.waitForTimeout(400);
}

for (const language of [
  { code: 'fr', label: /Français/i },
  { code: 'ar', label: /العربية/i },
] as const) {
  test(`every Micro-Quest renders in ${language.code}`, async ({ page }) => {
    test.setTimeout(150000);
    await registerNewUser(page);
    await switchLanguage(page, language.label);

    for (const quest of ALL_QUESTS) {
      await openQuest(page, quest);
      await expect(
        page.getByTestId('quest-hook'),
        `${quest.name} hook in ${language.code}`,
      ).toContainText(quest.hookText[language.code]);

      if (language.code === 'ar') {
        expect(await page.evaluate(() => document.documentElement.dir)).toBe('rtl');
      }

      // The stage rail is translated and still in Hook -> ... -> Complete order.
      const stages = await page
        .getByTestId('quest-progress')
        .locator('[data-testid^="quest-stage-"]')
        .evaluateAll((nodes) => nodes.map((n) => n.getAttribute('data-testid')));
      expect(stages).toEqual([
        'quest-stage-hook',
        'quest-stage-blueprint',
        'quest-stage-quest',
        'quest-stage-complete',
      ]);

      await page.getByTestId('hook-continue').click();
      await expect(page.getByTestId('blueprint')).toBeVisible();

      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(overflow, `${quest.name} blueprint overflow in ${language.code}`).toBeLessThanOrEqual(
        2,
      );

      await solveBlueprint(page, quest);
      await page.getByTestId('blueprint-continue').click();
      await expect(page.getByTestId('quest-stage')).toBeVisible();
      const questOverflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(questOverflow, `${quest.name} quest overflow in ${language.code}`).toBeLessThanOrEqual(
        2,
      );
    }
  });
}

// ---------------------------------------------------------------------------
// Viewports. One registration per viewport, all three quests inside it.
// ---------------------------------------------------------------------------

for (const viewport of [
  { name: '320x551', width: 320, height: 551 },
  { name: '320x800', width: 320, height: 800 },
  { name: '375x812', width: 375, height: 812 },
  { name: '768x1024', width: 768, height: 1024 },
  { name: '1024x768', width: 1024, height: 768 },
  { name: '1440x900', width: 1440, height: 900 },
]) {
  test(`every Micro-Quest is usable at ${viewport.name}`, async ({ page }) => {
    test.setTimeout(180000);
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await registerNewUser(page);

    for (const quest of ALL_QUESTS) {
      await openQuest(page, quest);

      const noOverflow = async (where: string) => {
        const overflow = await page.evaluate(
          () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
        );
        expect(overflow, `${quest.name} ${where} at ${viewport.name}`).toBeLessThanOrEqual(2);
      };
      const insideViewport = async (testId: string) => {
        const box = await page.getByTestId(testId).boundingBox();
        expect(box, `${testId} has no box at ${viewport.name}`).not.toBeNull();
        if (box) {
          expect(box.x).toBeGreaterThanOrEqual(-2);
          expect(box.x + box.width).toBeLessThanOrEqual(viewport.width + 2);
        }
      };

      await noOverflow('hook');
      await insideViewport('hook-continue');

      await page.getByTestId('hook-continue').click();
      await expect(page.getByTestId('blueprint')).toBeVisible();
      await noOverflow('blueprint');
      await insideViewport('blueprint-check');

      await solveBlueprint(page, quest);
      await page.getByTestId('blueprint-continue').click();
      await expect(page.getByTestId('quest-stage')).toBeVisible();
      await noOverflow('quest');
    }
  });
}
