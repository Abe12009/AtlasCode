import { test, expect } from '@playwright/test';
import { registerNewUser } from './helpers';

test.describe('Accessibility basics', () => {
  test('buttons have accessible names on the dashboard', async ({ page }) => {
    await registerNewUser(page);
    await expect(page.getByRole('link', { name: /^Courses$/i })).toBeVisible({ timeout: 10000 });
    const buttons = page.getByRole('button');
    const count = await buttons.count();
    expect(count).toBeGreaterThan(0);
    for (let i = 0; i < count; i++) {
      const name = await buttons.nth(i).getAttribute('aria-label');
      const text = await buttons.nth(i).innerText().catch(() => '');
      expect(
        Boolean(name) || text.trim().length > 0,
        `Button at index ${i} has neither visible text nor an aria-label`
      ).toBeTruthy();
    }
  });

  test('login and register form inputs have associated labels', async ({ page }) => {
    await page.goto('/register');
    await expect(page.getByPlaceholder('Choose a username')).toBeVisible({ timeout: 10000 });
    const inputs = page.locator('input:not([type="hidden"])');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);
    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      let hasLabel = Boolean(ariaLabel);
      if (!hasLabel && id) {
        hasLabel = (await page.locator(`label[for="${id}"]`).count()) > 0;
      }
      expect(hasLabel, `Input #${i} (id="${id}") has no associated <label> or aria-label`).toBeTruthy();
    }
  });

  test('main navigation is keyboard accessible', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/dashboard');
    await expect(page.getByRole('link', { name: /^Courses$/i })).toBeVisible({ timeout: 10000 });

    // Tab from the top of the page and confirm focus lands on a real, visible element
    // with a visible focus outline (not focus-trapped or invisible).
    await page.keyboard.press('Tab');
    const activeTag = await page.evaluate(() => document.activeElement?.tagName);
    expect(activeTag).toBeTruthy();
    const outline = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement;
      const style = window.getComputedStyle(el);
      return style.outlineStyle !== 'none' || style.boxShadow !== 'none';
    });
    expect(outline).toBeTruthy();

    // Courses link is reachable and activatable via keyboard (Enter).
    const coursesLink = page.getByRole('link', { name: /^Courses$/i });
    await coursesLink.focus();
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL(/\/app\/courses$/);
  });

  test('the notification dropdown can be opened with the keyboard', async ({ page }) => {
    await registerNewUser(page);
    const bell = page.getByRole('button', { name: /notifications/i });
    await bell.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('menu')).toBeVisible({ timeout: 5000 });
  });
});
