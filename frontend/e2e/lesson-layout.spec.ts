import { test, expect, Page } from '@playwright/test';
import { registerNewUser } from './helpers';

/**
 * Regression coverage for the two Phase 10 bugs:
 *
 *   1. A lesson page (`h-screen` under Layout's `pt-20 pb-8` header offset)
 *      rendered ~7rem taller than the space it was actually given, pushing
 *      its own bottom controls (Hook Continue, Blueprint Check, Submit)
 *      below the fold on any viewport short enough that the overflow wasn't
 *      obviously scrollable. Fixed by sizing the lesson root to
 *      `calc(100dvh - 7rem)` instead (`src/lib/layout.ts`).
 *
 *   2. Under Arabic RTL, code containers (`<pre>`, the code editor, the
 *      terminal) inherited `direction: rtl` from `<html dir="rtl">` and
 *      visually right-aligned/reversed Python, SQL and shell snippets. Fixed
 *      by forcing `dir="ltr"` on every code-display component
 *      (`CodeBlock.tsx`, `CodeEditor.tsx`'s editor and terminal).
 */

const VIEWPORTS = [
  { name: '320x551', width: 320, height: 551 },
  { name: '320x800', width: 320, height: 800 },
  { name: '375x812', width: 375, height: 812 },
  { name: '768x1024', width: 768, height: 1024 },
  { name: '1024x768', width: 1024, height: 768 },
  { name: '1440x900', width: 1440, height: 900 },
];

/**
 * Proves a control is *reachable*: scrolls it into view the same way a real
 * click would (Playwright's own `.click()` already does this before acting),
 * then asserts it actually landed inside the viewport.
 *
 * This is deliberately not "already visible without scrolling" — the Hook's
 * content is short and always fits, but the Blueprint stage's reading blocks
 * plus its puzzle can legitimately be taller than a short viewport, and the
 * lesson's own inner region (`overflow-y-auto`) is supposed to scroll to
 * reach it. That is correct, existing behavior, not the bug.
 *
 * The bug this guards is different: under `h-screen`, the lesson claimed 7rem
 * more height than Layout actually gave it, so content past that self-drawn,
 * `overflow-hidden` boundary was genuinely unreachable — no amount of
 * scrolling, real or automated, could bring it into the viewport. Asserting
 * "after scrolling into view, the element is inside the viewport" fails under
 * that bug and passes under the fix.
 */
async function reachable(page: Page, locator: ReturnType<Page['getByTestId']>, viewport: { width: number; height: number }) {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  expect(box, 'element has no box (not rendered?)').not.toBeNull();
  if (!box) return;
  expect(box.y, 'top edge above the viewport after scrolling into view').toBeGreaterThanOrEqual(-2);
  expect(box.y + box.height, 'bottom edge below the viewport after scrolling into view').toBeLessThanOrEqual(
    viewport.height + 2,
  );
  expect(box.x).toBeGreaterThanOrEqual(-2);
  expect(box.x + box.width).toBeLessThanOrEqual(viewport.width + 2);
}

test.describe('Lesson layout: bottom controls stay reachable at every required viewport', () => {
  for (const vp of VIEWPORTS) {
    test(`Micro-Quest lesson 9: Hook Continue is visible and clickable at ${vp.name}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);
      await page.goto('/app/lessons/9');
      await expect(page.getByTestId('micro-quest')).toBeVisible({ timeout: 15000 });

      const continueButton = page.getByTestId('hook-continue');
      await expect(continueButton).toBeVisible();
      await reachable(page, continueButton, vp);

      // Not just "in the DOM" — actually clickable at its own coordinates,
      // which is exactly what "below the fold and unreachable" would break.
      await continueButton.click();
      await expect(page.getByTestId('blueprint')).toBeVisible({ timeout: 10000 });

      const checkButton = page.getByTestId('blueprint-check');
      await expect(checkButton).toBeVisible();
      await reachable(page, checkButton, vp);
      await checkButton.click();
      await expect(page.getByTestId('blueprint-feedback')).toBeVisible();
    });

    test(`classic lesson 1: Next control is visible and clickable at ${vp.name}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);
      await page.goto('/app/lessons/1');
      await expect(page.getByText('What Is Programming?')).toBeVisible({ timeout: 15000 });

      const next = page.getByTestId('lesson-nav-next');
      await expect(next).toBeVisible();
      await reachable(page, next, vp);

      await next.click();
      await expect(page.getByTestId('lesson-nav-prev')).toBeEnabled();
    });
  }

  test('the lesson root does not rely on 100vh sized independently of the header offset', async ({
    page,
  }) => {
    // A direct assertion of the actual fix, not just its symptom: the lesson
    // root's rendered height must equal the viewport minus Layout's header
    // reservation (pt-20 + pb-8 = 7rem), never the full 100vh Layout never
    // gave it.
    await page.setViewportSize({ width: 375, height: 667 });
    await registerNewUser(page);
    await page.goto('/app/lessons/9');
    await expect(page.getByTestId('micro-quest')).toBeVisible({ timeout: 15000 });

    const measurements = await page.evaluate(() => {
      const root = document.querySelector('[dir][class*="overflow-hidden"]');
      const rootFontSizePx = parseFloat(getComputedStyle(document.documentElement).fontSize);
      return {
        rootHeight: root ? root.getBoundingClientRect().height : null,
        rootFontSizePx,
      };
    });
    expect(measurements.rootHeight).not.toBeNull();
    // 7rem, at whatever the root font size actually is here — index.css drops
    // it to 14px below a 640px-wide viewport, and this asserts the fix stays
    // correct at that breakpoint too rather than assuming a fixed 16px.
    const headerReservationPx = measurements.rootFontSizePx * 7;
    expect(measurements.rootHeight as number).toBeLessThanOrEqual(667 - headerReservationPx + 2);
  });
});

test.describe('RTL code stays left-to-right', () => {
  test('a classic lesson’s code_example renders LTR under Arabic', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/dashboard');
    await page.locator('button', { hasText: /English|Français|العربية/i }).first().click();
    await page.getByRole('menuitem', { name: /العربية/i }).click();
    await page.waitForTimeout(400);

    await page.goto('/app/lessons/1');
    await expect(page.locator('body')).toContainText(/برمجة|Programming/i, { timeout: 15000 });
    expect(await page.evaluate(() => document.documentElement.dir)).toBe('rtl');

    // Walk to the code block (order 2).
    await page.getByTestId('lesson-nav-next').click();
    const editorRoot = page.locator('textarea').first().locator('xpath=ancestor::div[contains(@class,"bg-bg-code")][1]');
    await expect(editorRoot).toBeVisible();
    await expect(editorRoot).toHaveAttribute('dir', 'ltr');

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(2);
  });

  test('a Micro-Quest blueprint code snippet renders LTR under Arabic (spot_the_bug)', async ({
    page,
  }) => {
    await registerNewUser(page);
    await page.goto('/app/dashboard');
    await page.locator('button', { hasText: /English|Français|العربية/i }).first().click();
    await page.getByRole('menuitem', { name: /العربية/i }).click();
    await page.waitForTimeout(400);

    await page.goto('/app/lessons/38');
    await expect(page.getByTestId('micro-quest')).toBeVisible({ timeout: 15000 });
    expect(await page.evaluate(() => document.documentElement.dir)).toBe('rtl');

    await page.getByTestId('hook-continue').click();
    const snippet = page.getByTestId('spot-bug-snippet');
    await expect(snippet).toBeVisible();
    await expect(snippet).toHaveAttribute('dir', 'ltr');
    await expect(snippet).toContainText('left, right');

    // The prose around it stays RTL — only code is forced LTR.
    const dirValue = await snippet.evaluate((el) => getComputedStyle(el).direction);
    expect(dirValue).toBe('ltr');

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(2);
  });

  test('the code editor and terminal stay LTR under Arabic on a code_writing quest', async ({
    page,
  }) => {
    await registerNewUser(page);
    await page.goto('/app/dashboard');
    await page.locator('button', { hasText: /English|Français|العربية/i }).first().click();
    await page.getByRole('menuitem', { name: /العربية/i }).click();
    await page.waitForTimeout(400);

    await page.goto('/app/lessons/9');
    await expect(page.getByTestId('micro-quest')).toBeVisible({ timeout: 15000 });
    await page.getByTestId('hook-continue').click();
    await expect(page.getByTestId('blueprint')).toBeVisible();

    // Solve the order_steps blueprint to reach the code editor.
    const order = ['init', 'visit', 'decide', 'update'];
    for (let target = 0; target < order.length; target++) {
      for (let guard = 0; guard < order.length + 2; guard++) {
        const item = page.getByTestId(`blueprint-step-${order[target]}`);
        const position = Number(await item.getAttribute('data-position'));
        if (position === target) break;
        await item.locator('button').first().click();
        await page.waitForTimeout(60);
      }
    }
    await page.getByTestId('blueprint-check').click();
    await page.getByTestId('blueprint-continue').click();
    await expect(page.getByTestId('quest-stage')).toBeVisible();

    const editorRoot = page.locator('textarea').first().locator('xpath=ancestor::div[contains(@class,"bg-bg-code")][1]');
    await expect(editorRoot).toHaveAttribute('dir', 'ltr');

    const terminal = page.getByTestId('terminal-panel');
    await expect(terminal).toHaveAttribute('dir', 'ltr');
  });
});
