import { test, expect } from '@playwright/test';
import { registerNewUser } from './helpers';

/**
 * Regression cover for the Visual Programming white-screen.
 *
 * Exercises 15 and 20 ship starter graphs whose nodes have no `position`.
 * The editor read `node.position.x` while laying out edges, threw during
 * render, and left a blank page -- served with a 200, so nothing that only
 * checks status codes would notice.
 *
 * The pageerror listener is the point of these tests: a blank page still
 * "loads", so asserting on visible content alone would have passed against
 * the bug for the DOM-free parts. Both the content and the absence of a
 * thrown error have to hold.
 */
const BROKEN_STARTER_EXERCISES = [15, 20];

for (const exerciseId of BROKEN_STARTER_EXERCISES) {
  test(`visual programming exercise ${exerciseId} renders without a page error`, async ({ page }) => {
    const pageErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(String(e)));

    await registerNewUser(page);
    await page.goto(`/app/visual/${exerciseId}`);

    // The palette and the canvas are the two halves of the editor; a render
    // throw takes out both.
    await expect(page.locator('button[draggable="true"]').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('#visual-canvas-wrapper')).toBeVisible();

    // The boundary's fallback must NOT be showing.
    await expect(page.getByTestId('route-error')).toHaveCount(0);

    expect(
      pageErrors,
      `page threw while rendering /app/visual/${exerciseId}: ${pageErrors.join(' | ')}`,
    ).toEqual([]);
  });
}

test('a starter graph without positions still lays its nodes out on the canvas', async ({ page }) => {
  const pageErrors: string[] = [];
  page.on('pageerror', (e) => pageErrors.push(String(e)));

  await registerNewUser(page);
  await page.goto('/app/visual/15');
  await expect(page.locator('#visual-canvas-wrapper')).toBeVisible({ timeout: 15000 });

  // Exercise 15's starter graph is four nodes. They must be placed at
  // distinct coordinates rather than piled at the origin, which is the
  // difference between "renders" and "is usable".
  const positioned = await page.locator('#visual-canvas-wrapper [style*="left"]').evaluateAll((els) =>
    els
      .map((e) => (e as HTMLElement).style.left + ',' + (e as HTMLElement).style.top)
      .filter((s) => s !== ','),
  );
  expect(positioned.length, 'starter nodes should render').toBeGreaterThan(0);
  expect(new Set(positioned).size, 'node positions should be distinct').toBe(positioned.length);
  expect(pageErrors).toEqual([]);
});
