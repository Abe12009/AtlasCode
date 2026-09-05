import { test, expect } from '@playwright/test';
import { registerNewUser } from './helpers';

const NARROW = [
  { name: '320x800', width: 320, height: 800 },
  { name: '375x812', width: 375, height: 812 },
  { name: '768x1024', width: 768, height: 1024 },
];

test.describe('Responsive usability', () => {
  for (const vp of NARROW) {
    test(`mobile navigation opens and navigates at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);
      await page.goto('/app/dashboard');

      const toggle = page.getByRole('button', { name: /open menu/i });
      await expect(toggle).toBeVisible();
      await toggle.click();

      const menu = page.locator('#mobile-menu');
      await expect(menu).toBeVisible();

      // The menu must stay inside the viewport.
      const box = await menu.boundingBox();
      expect(box).not.toBeNull();
      if (box) {
        expect(box.x).toBeGreaterThanOrEqual(-2);
        expect(box.x + box.width).toBeLessThanOrEqual(vp.width + 2);
      }

      await menu.getByRole('link', { name: /courses/i }).click();
      await expect(page).toHaveURL(/\/app\/courses$/);
      await expect(page.getByRole('button', { name: /open menu/i })).toBeVisible();
    });
  }

  for (const vp of [{ name: '320x800', width: 320, height: 800 }, { name: '375x812', width: 375, height: 812 }, { name: '1440x900', width: 1440, height: 900 }]) {
    test(`lesson code editor stays usable at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);

      // Lesson 1 step 2 is a code block; its last step is a code exercise.
      await page.goto('/app/lessons/1');
      await expect(page.getByText('What Is Programming?')).toBeVisible({ timeout: 15000 });

      // Walk to the first exercise, which renders the editable editor.
      for (let i = 0; i < 3; i++) {
        await page.getByRole('button', { name: /^next$/i }).first().click();
        await page.waitForTimeout(250);
      }

      const editor = page.locator('textarea').first();
      await expect(editor).toBeVisible();
      await editor.click();
      await editor.fill('print("hello from e2e")');
      await expect(editor).toHaveValue('print("hello from e2e")');

      // The editor must not push the page wider than the viewport.
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(overflow, `Editor caused ${overflow}px overflow at ${vp.name}`).toBeLessThanOrEqual(2);

      // Run produces real output from the backend terminal panel.
      await page.getByRole('button', { name: /^run( code)?$/i }).first().click();
      await expect(page.locator('body')).toContainText('hello from e2e', { timeout: 20000 });
    });
  }

  test('project page stays usable at 320x800', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 800 });
    await registerNewUser(page);
    await page.goto('/app/projects/1');
    await expect(page.locator('body')).toContainText(/Calculator/i, { timeout: 15000 });

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(2);
  });
});
