import { test, expect } from '@playwright/test';
import { registerNewUser, expectAppShellVisible } from './helpers';

const VIEWPORTS: Array<{ name: string; width: number; height: number }> = [
  { name: '320x800', width: 320, height: 800 },
  { name: '375x812', width: 375, height: 812 },
  { name: '768x1024', width: 768, height: 1024 },
  { name: '1024x768', width: 1024, height: 768 },
  { name: '1440x900', width: 1440, height: 900 },
];

const PAGES = ['/app/dashboard', '/app/courses', '/app/courses/1', '/app/lessons/1', '/app/projects', '/app/projects/1'];

test.describe('Responsive behavior', () => {
  for (const vp of VIEWPORTS) {
    test(`viewport ${vp.name}: no horizontal overflow, nav usable, content visible`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);

      for (const path of PAGES) {
        await page.goto(path);
        await page.waitForTimeout(300);

        // No horizontal overflow: document scrollWidth must not exceed the viewport width
        // (a couple pixels of tolerance for scrollbar rendering).
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        expect(overflow, `Horizontal overflow of ${overflow}px on ${path} at ${vp.name}`).toBeLessThanOrEqual(2);

        // The AtlasCode home link (part of the header) stays visible and clickable at
        // every breakpoint, proving the nav didn't disappear or break.
        await expectAppShellVisible(page);
      }
    });
  }

  test('dropdowns stay inside the viewport at a narrow width', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await registerNewUser(page);
    await page.goto('/app/dashboard');

    const bell = page.getByRole('button', { name: /notifications/i });
    await bell.click();
    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();
    await page.waitForTimeout(200); // allow the edge-clamp effect to apply
    const box = await menu.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      expect(box.x).toBeGreaterThanOrEqual(-2);
      expect(box.x + box.width).toBeLessThanOrEqual(375 + 2);
    }
  });
});
