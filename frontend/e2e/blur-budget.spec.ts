import { test, expect, Page } from '@playwright/test';
import { registerNewUser } from './helpers';

/**
 * The Spatial Glass blur budget, measured rather than reasoned about.
 *
 * index.css: "at most TWO blurred layers overlapping at any point on screen."
 * That is a per-POINT limit, not a per-page count, so this samples a grid and
 * at each point counts how many elements under it have a computed
 * backdrop-filter. `elementsFromPoint` returns the whole hit stack including
 * ancestors, which is what the compositor actually has to process there.
 *
 * It caught a real regression once: with a modal open the count was 3 --
 * the overlay scrim spanned the viewport and stacked on top of the fixed
 * header and whatever glass card sat underneath.
 *
 * Deliberately uses only surfaces a brand-new account can reach. An earlier
 * version opened a lesson, which depends on sequential lesson unlocking and
 * fails for a fresh user with a 403.
 */

const BUDGET = 2;

/** Max overlapping backdrop-filter layers over a grid, plus the worst stack. */
async function maxBlurDepth(page: Page) {
  return page.evaluate((step) => {
    let max = 0;
    let worst: string[] = [];
    let at: { x: number; y: number } | null = null;
    for (let y = 4; y < window.innerHeight; y += step) {
      for (let x = 4; x < window.innerWidth; x += step) {
        const stack = document
          .elementsFromPoint(x, y)
          .filter((el) => getComputedStyle(el).backdropFilter !== 'none');
        if (stack.length > max) {
          max = stack.length;
          at = { x, y };
          worst = stack.map((el) => {
            const cls = (el.getAttribute('class') || '')
              .split(' ')
              .filter((c) => /glass|backdrop-blur/.test(c))
              .join('.');
            return `${el.tagName.toLowerCase()}${cls ? '.' + cls : ''}`;
          });
        }
      }
    }
    return { max, worst, at };
  }, 24);
}

/**
 * The same count, but across the whole scroll range rather than at one offset.
 *
 * The budget is a per-point limit at any moment, and a fixed blurred header
 * means the worst moment is mid-scroll: content with its own blur passes
 * UNDER the header and the stack grows by one. Sampling only scroll 0 cannot
 * see that, which is exactly how phase 7's census recorded Landing at 1 while
 * it actually composites 3 at scrollY 1350.
 *
 * Steps are viewport/4 so nothing taller than a quarter-screen can slip
 * between two samples, and the last step is clamped to the bottom so the
 * range is fully covered rather than overshot.
 */
async function sweepMaxBlurDepth(page: Page) {
  const { scrollHeight, innerHeight } = await page.evaluate(() => ({
    scrollHeight: document.documentElement.scrollHeight,
    innerHeight: window.innerHeight,
  }));
  const step = Math.floor(innerHeight / 4);
  const end = Math.max(0, scrollHeight - innerHeight);
  let best = { max: 0, worst: [] as string[], at: null as { x: number; y: number } | null };
  let atScrollY = 0;
  let maxScrollY = 0;
  let samples = 0;

  for (let target = 0; ; target += step) {
    const clamped = Math.min(target, end);
    await page.evaluate((t) => window.scrollTo(0, t), clamped);
    await page.waitForTimeout(140);
    const reached = await page.evaluate(() => Math.round(window.scrollY));
    maxScrollY = Math.max(maxScrollY, reached);
    samples += 1;
    const here = await maxBlurDepth(page);
    if (here.max > best.max) {
      best = here;
      atScrollY = reached;
    }
    if (clamped >= end) break;
  }

  return { ...best, atScrollY, maxScrollY, samples, scrollHeight, innerHeight };
}

/**
 * Sweep one surface and hold it to the budget.
 *
 * `minRatio` is the precondition that stops the assertion passing vacuously:
 * a page that does not scroll cannot produce the under-the-header overlap
 * this test exists to catch, so the spec states per surface how much scroll
 * it expects and fails if the page ever stops providing it.
 *
 * Only Landing gets a real ratio. Measured at 1440x900 on a brand-new
 * account: landing 4.65, dashboard 1.60 (1.20 on a slower load -- content
 * height moves with what has rendered, so pinning 1.5 here would be flaky),
 * course detail 1.22, courses 1.03, lesson 1 1.08. Those three genuinely
 * barely scroll, so `1.0` means "must scroll at all" and the sweep is held
 * non-vacuous instead by covering the whole range and proving it sampled
 * real glass.
 */
async function expectSweepWithinBudget(
  page: Page,
  label: string,
  { minRatio }: { minRatio: number },
) {
  const r = await sweepMaxBlurDepth(page);
  const ratio = r.scrollHeight / r.innerHeight;
  const where = `${label} [sh=${r.scrollHeight} inner=${r.innerHeight} ratio=${ratio.toFixed(2)} samples=${r.samples}]`;

  expect(
    ratio,
    `${where}: the page must be taller than ${minRatio}x the viewport or this sweep proves ` +
      `nothing -- there is no scroll for a blurred layer to pass under the header in.`,
  ).toBeGreaterThan(minRatio);

  // The sweep has to have actually moved, and the sampler has to have found
  // real glass. Either one at zero means the sweep measured nothing.
  expect(r.maxScrollY, `${where}: the sweep never left scroll 0`).toBeGreaterThan(0);
  expect(
    r.max,
    `${where}: found no backdrop-filter anywhere, so dark/glass is not actually on`,
  ).toBeGreaterThanOrEqual(1);

  expect(
    r.max,
    `${where}: ${r.max} overlapping blurred layers at scrollY ${r.atScrollY}, point ` +
      `(${r.at?.x},${r.at?.y}) -- [${r.worst.join(' | ')}]. Budget is ${BUDGET}.`,
  ).toBeLessThanOrEqual(BUDGET);
}

/**
 * Pin dark. Glass is dark-only through the token values, so in light every
 * `.glass-*` surface resolves its blur to `none` and the only backdrop-filter
 * left is the header's raw Tailwind utility. A budget test that runs in light
 * therefore measures 1 everywhere and proves nothing -- which is exactly what
 * the first version of this spec did, since it never set a theme and the
 * headless default is light.
 */
async function useDarkTheme(page: Page) {
  await page.evaluate(() => localStorage.setItem('atlascode.theme', 'dark'));
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(700);
}

async function expectWithinBudget(page: Page, label: string) {
  const { max, worst, at } = await maxBlurDepth(page);
  expect(
    max,
    `${label}: ${max} overlapping blurred layers at (${at?.x},${at?.y}) -- ` +
      `[${worst.join(' | ')}]. Budget is ${BUDGET}.`,
  ).toBeLessThanOrEqual(BUDGET);
}

test.describe('Spatial Glass blur budget', () => {
  // Explicit, and wider than the project default. At 1280x720 the dashboard
  // reflows enough that the modal scrim no longer covers a blurred card, and
  // the over-budget stack this spec exists to catch simply does not occur --
  // the first version of this file passed against the known-bad code for
  // exactly that reason.
  test.use({ viewport: { width: 1440, height: 900 } });

  test('stays within budget on the main surfaces and overlay states', async ({ page }) => {
    await registerNewUser(page);

    await page.goto('/app/dashboard');
    await useDarkTheme(page);
    await expectWithinBudget(page, 'dashboard');

    await page.goto('/app/courses');
    await useDarkTheme(page);
    await expectWithinBudget(page, 'courses');

    await page.goto('/app/courses/1');
    await useDarkTheme(page);
    await expectWithinBudget(page, 'course detail');

    // A modal over the app shell is the case that was over budget: the scrim
    // covers the fixed header and every card already blurring beneath it.
    await page.goto('/app/dashboard');
    await useDarkTheme(page);
    // Scroll first, deliberately. The worst case is a blurred card sitting
    // under the fixed header; at scroll 0 the dashboard's cards start below
    // the header and never overlap it, so the state the budget cares about
    // simply does not arise and the assertion would pass vacuously.
    await page.evaluate(() => window.scrollTo(0, 400));
    await page.waitForTimeout(400);
    await page.getByRole('button', { name: /feedback/i }).last().click();
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Guards the guard: the budget assertion below is only meaningful if the
    // modal actually composites over something already blurred. If this ever
    // drops to 1 the surface has changed and the spec has stopped testing
    // the case, rather than the case having been fixed.
    const modal = await maxBlurDepth(page);
    expect(
      modal.max,
      `the modal state must stack at least two blurred layers, or this spec proves ` +
        `nothing. Saw ${modal.max} at (${modal.at?.x},${modal.at?.y}): [${modal.worst.join(' | ')}], ` +
        `viewport ${JSON.stringify(page.viewportSize())}`,
    ).toBeGreaterThanOrEqual(2);

    await expectWithinBudget(page, 'dashboard + modal');
  });

  test('stays within budget across the whole scroll range', async ({ page }) => {
    // The sweep is four full-page passes, each one scroll step at a time.
    test.setTimeout(180000);

    // Landing is public and is the surface the under-the-header overlap was
    // actually measured on, so it runs before any account exists.
    await page.goto('/');
    await useDarkTheme(page);
    await expectSweepWithinBudget(page, 'landing, swept', { minRatio: 1.5 });

    await registerNewUser(page);

    await page.goto('/app/dashboard');
    await useDarkTheme(page);
    await expectSweepWithinBudget(page, 'dashboard, swept', { minRatio: 1.0 });

    await page.goto('/app/courses');
    await useDarkTheme(page);
    await expectSweepWithinBudget(page, 'courses, swept', { minRatio: 1.0 });

    // Lesson 1 is the first lesson of the first course, so the sequential
    // gate lets a brand-new account open it without any seeded progress --
    // the same reason the rest of this file sticks to reachable surfaces.
    await page.goto('/app/lessons/1');
    await useDarkTheme(page);
    await page.waitForTimeout(600);
    await expectSweepWithinBudget(page, 'lesson 1, swept', { minRatio: 1.0 });
  });

  test('a dropdown over the header stays within budget', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/dashboard');
    await useDarkTheme(page);

    await page.getByRole('button', { name: /notification/i }).first().click();
    await page.waitForTimeout(500);
    await expectWithinBudget(page, 'dashboard + notification dropdown');
  });

  test('light mode blurs less than dark, never more', async ({ page }) => {
    // Glass is dark-only through the token values, so every glass surface
    // resolves its blur to `none` in light. A light count above dark means a
    // hardcoded blur has crept back in -- which is exactly what `.glass` and
    // `.glass-strong` used to do.
    await registerNewUser(page);

    await page.goto('/app/dashboard');
    await page.evaluate(() => localStorage.setItem('atlascode.theme', 'dark'));
    await page.reload();
    await page.waitForTimeout(900);
    const dark = await maxBlurDepth(page);

    await page.evaluate(() => localStorage.setItem('atlascode.theme', 'light'));
    await page.reload();
    await page.waitForTimeout(900);
    const light = await maxBlurDepth(page);

    expect(
      light.max,
      `light composited ${light.max} blurred layers vs dark's ${dark.max} ` +
        `-- [${light.worst.join(' | ')}]`,
    ).toBeLessThanOrEqual(dark.max);
  });
});
