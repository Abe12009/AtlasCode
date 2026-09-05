import { test, expect } from '@playwright/test';
import { registerNewUser, trackPageHealth } from './helpers';

async function openBell(page: import('@playwright/test').Page) {
  const bell = page.getByRole('button', { name: /notifications/i });
  await bell.click();
  return bell;
}

function unreadBadgeText(page: import('@playwright/test').Page) {
  return page.locator('button[aria-label*="otification"] span.bg-error-500');
}

test.describe('Notifications (real, backend-backed)', () => {
  test('bell shows a real unread badge, opens a real panel with content, and can be closed', async ({ page }) => {
    const health = trackPageHealth(page);
    await registerNewUser(page); // registration itself creates a real "welcome" notification

    // A brand-new account has exactly one real notification (welcome) — badge shows "1".
    await expect(unreadBadgeText(page)).toHaveText('1', { timeout: 10000 });

    const bell = await openBell(page);
    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/welcome to atlascode/i)).toBeVisible();

    await page.mouse.click(20, 20);
    await expect(menu).toBeHidden({ timeout: 5000 });
    health.assertNoFailures();
    void bell;
  });

  test('a real user action (completing an exercise) creates a real notification and increases the unread count', async ({ page }) => {
    await registerNewUser(page);
    await expect(unreadBadgeText(page)).toHaveText('1', { timeout: 10000 }); // welcome only

    // Real action: open lesson 1, jump to its first exercise, run + submit real Python code.
    await page.goto('/app/lessons/1');
    await page.getByRole('button', { name: /^Exercise 1$/i }).click();
    await page.getByRole('button', { name: /Run Code/i }).last().click();
    await expect(page.getByText(/Hello, World!/i).first()).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Submit Solution/i }).click();
    await expect(page.getByText(/Correct!/i).first()).toBeVisible({ timeout: 15000 });

    // The unread count must increase for the real xp_earned notification just created.
    await expect(unreadBadgeText(page)).toHaveText('2', { timeout: 10000 });

    await openBell(page);
    const menu = page.getByRole('menu');
    await expect(menu.getByText(/you earned 10 xp/i)).toBeVisible({ timeout: 5000 });
  });

  test('clicking an unread notification marks it read and decreases the unread count; refresh preserves it', async ({ page }) => {
    await registerNewUser(page);
    await expect(unreadBadgeText(page)).toHaveText('1', { timeout: 10000 });

    await openBell(page);
    const menu = page.getByRole('menu');
    const item = menu.getByRole('menuitem').first();
    await item.click();

    // Badge disappears entirely once everything is read.
    await expect(unreadBadgeText(page)).toHaveCount(0, { timeout: 10000 });

    // Refresh: read state must persist (it's backend-backed, not client-only state).
    await page.reload();
    await expect(unreadBadgeText(page)).toHaveCount(0, { timeout: 10000 });
  });

  test('mark all as read clears the unread badge', async ({ page }) => {
    await registerNewUser(page);

    // Generate a second real notification so there is something to bulk-clear.
    await page.goto('/app/lessons/1');
    await page.getByRole('button', { name: /^Exercise 1$/i }).click();
    await page.getByRole('button', { name: /Run Code/i }).last().click();
    await expect(page.getByText(/Hello, World!/i).first()).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Submit Solution/i }).click();
    await expect(page.getByText(/Correct!/i).first()).toBeVisible({ timeout: 15000 });
    await expect(unreadBadgeText(page)).toHaveText('2', { timeout: 10000 });

    await openBell(page);
    await page.getByText(/mark all as read/i).click();

    await expect(unreadBadgeText(page)).toHaveCount(0, { timeout: 10000 });
    await page.reload();
    await expect(unreadBadgeText(page)).toHaveCount(0, { timeout: 10000 });
  });

  test('notifications remain inside the viewport on a narrow screen', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await registerNewUser(page);
    await openBell(page);
    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();
    await page.waitForTimeout(200);
    const box = await menu.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      expect(box.x).toBeGreaterThanOrEqual(-2);
      expect(box.x + box.width).toBeLessThanOrEqual(375 + 2);
    }
  });

  test('notifications render translated in French', async ({ page }) => {
    await registerNewUser(page);
    const langTrigger = page.locator('button', { hasText: /English/i }).first();
    await langTrigger.click();
    await page.getByRole('menuitem', { name: /Français/i }).click();
    await expect(page.getByText('Bienvenue')).toBeVisible({ timeout: 10000 });

    await openBell(page);
    const menu = page.getByRole('menu');
    await expect(menu.getByText(/Bienvenue sur AtlasCode/i)).toBeVisible({ timeout: 5000 });
  });

  test('a second user never sees the first user notifications', async ({ page, browser }) => {
    await registerNewUser(page);
    await expect(unreadBadgeText(page)).toHaveText('1', { timeout: 10000 });

    // Second, fully independent browser context = second real user session.
    const context2 = await browser.newContext();
    const page2 = await context2.newPage();
    await registerNewUser(page2);
    await expect(unreadBadgeText(page2)).toHaveText('1', { timeout: 10000 });

    await openBell(page2);
    const menu2 = page2.getByRole('menu');
    const items2 = await menu2.getByRole('menuitem').count();
    expect(items2).toBe(1); // only their own welcome notification, never user 1's

    await context2.close();
  });
});
