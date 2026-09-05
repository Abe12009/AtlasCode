import { test, expect, Page } from '@playwright/test';
import { registerNewUser } from './helpers';

async function switchLanguage(page: Page, label: RegExp) {
  await page.locator('button', { hasText: /English|Français|العربية/i }).first().click();
  await page.getByRole('menuitem', { name: label }).click();
  await page.waitForTimeout(400);
}

/** Lesson 61 (JavaScript > Arrays and Objects) has real EN/FR/AR block translations. */
const TRANSLATED_LESSON = '/app/lessons/61';

test.describe('Language switching does not disturb app state', () => {
  test('switching language keeps auth, lesson progress and the same document (no reload)', async ({ page }) => {
    await registerNewUser(page);

    // Start a lesson so there is real server-side progress to lose.
    await page.goto(TRANSLATED_LESSON);
    await expect(page.getByText('Arrays and Objects')).toBeVisible({ timeout: 15000 });

    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeTruthy();

    // Stamp the live document. A full page reload wipes this; a client-side
    // language change must not.
    await page.evaluate(() => { (window as unknown as { __i18nProbe?: number }).__i18nProbe = 1234; });

    await switchLanguage(page, /Français/i);

    const probe = await page.evaluate(() => (window as unknown as { __i18nProbe?: number }).__i18nProbe);
    expect(probe, 'Language switch triggered a full page reload').toBe(1234);

    // Auth survives.
    const tokenAfter = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(tokenAfter).toBe(token);
    await expect(page).toHaveURL(new RegExp('/app/lessons/61$'));

    // Progress survives: the API still reports a started lesson.
    const status = await page.evaluate(async () => {
      const res = await fetch('http://localhost:8000/lessons/61/progress', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      return (await res.json()).status;
    });
    expect(['ready', 'in_progress', 'completed']).toContain(status);
  });

  test('lesson body content is really translated in EN, FR and AR', async ({ page }) => {
    await registerNewUser(page);

    await page.goto(TRANSLATED_LESSON);
    await expect(page.locator('body')).toContainText('Arrays hold ordered lists', { timeout: 15000 });

    // The language selector lives in the app header, so switch from the
    // dashboard and come back to the lesson.
    await page.goto('/app/dashboard');
    await switchLanguage(page, /Français/i);
    await page.goto(TRANSLATED_LESSON);
    await expect(page.locator('body')).toContainText('Les tableaux contiennent des listes ordonnées', { timeout: 15000 });

    await page.goto('/app/dashboard');
    await switchLanguage(page, /العربية/i);
    await page.goto(TRANSLATED_LESSON);
    await expect(page.locator('body')).toContainText('تحتوي المصفوفات على قوائم مرتبة', { timeout: 15000 });
    expect(await page.evaluate(() => document.documentElement.dir)).toBe('rtl');
  });

  test('header controls keep their positions and dropdowns stay in-viewport in RTL', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/dashboard');

    const bellEn = page.getByRole('button', { name: /notifications/i });
    const ltrBox = await bellEn.boundingBox();
    expect(ltrBox).not.toBeNull();

    await switchLanguage(page, /العربية/i);
    expect(await page.evaluate(() => document.documentElement.dir)).toBe('rtl');

    // The bell's accessible name is itself translated in Arabic.
    const bellAr = page.getByRole('button', { name: 'الإشعارات' });
    // The bell stays in the header band (same vertical position), it does not
    // jump elsewhere on the page when direction flips.
    const rtlBox = await bellAr.boundingBox();
    expect(rtlBox).not.toBeNull();
    if (ltrBox && rtlBox) {
      expect(Math.abs(rtlBox.y - ltrBox.y)).toBeLessThanOrEqual(4);
    }

    // The dropdown stays fully inside the viewport in RTL.
    await bellAr.click();
    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();
    await page.waitForTimeout(200);
    const width = page.viewportSize()!.width;
    const box = await menu.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      expect(box.x).toBeGreaterThanOrEqual(-2);
      expect(box.x + box.width).toBeLessThanOrEqual(width + 2);
    }
  });

  test('no horizontal overflow in Arabic RTL at every required viewport', async ({ page }) => {
    // 25 page loads across 5 viewports needs more than the default budget.
    test.setTimeout(180000);
    await registerNewUser(page);
    await page.goto('/app/dashboard');
    await switchLanguage(page, /العربية/i);

    const viewports = [
      { width: 320, height: 800 },
      { width: 375, height: 812 },
      { width: 768, height: 1024 },
      { width: 1024, height: 768 },
      { width: 1440, height: 900 },
    ];
    const paths = ['/app/dashboard', '/app/courses', '/app/courses/7', TRANSLATED_LESSON, '/app/projects'];

    for (const vp of viewports) {
      await page.setViewportSize(vp);
      for (const path of paths) {
        await page.goto(path);
        await page.waitForTimeout(300);
        const overflow = await page.evaluate(
          () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
        );
        expect(overflow, `RTL horizontal overflow of ${overflow}px on ${path} at ${vp.width}x${vp.height}`)
          .toBeLessThanOrEqual(2);
      }
    }
  });
});
