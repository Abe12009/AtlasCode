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
