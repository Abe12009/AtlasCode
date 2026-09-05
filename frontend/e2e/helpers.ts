import { Page, expect } from '@playwright/test';

export function uniqueUser() {
  const id = `${Date.now()}${Math.floor(Math.random() * 10000)}`;
  return {
    username: `e2e_${id}`.slice(0, 20),
    email: `e2e_${id}@example.com`,
    password: 'TestPass123!',
  };
}

/** Registers a brand-new user through the real UI and lands on the dashboard. */
export async function registerNewUser(page: Page) {
  const user = uniqueUser();
  await page.goto('/register');
  await page.getByPlaceholder('Choose a username').fill(user.username);
  await page.getByPlaceholder('you@example.com').fill(user.email);
  await page.locator('#password').fill(user.password);
  await page.locator('#confirmPassword').fill(user.password);
  await page.getByRole('button', { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/app\/dashboard/, { timeout: 15000 });
  return user;
}

/** The header logo link has aria-label="Home" (i18n common.home), not "AtlasCode" —
 * its visible text. Use this instead of matching the link by accessible name. */
export async function expectAppShellVisible(page: Page) {
  await expect(page.getByText('AtlasCode', { exact: true }).first()).toBeVisible({ timeout: 10000 });
}

export async function loginUser(page: Page, email: string, password: string) {
  await page.goto('/login');
  await page.locator('#email').fill(email);
  await page.locator('#password').fill(password);
  await page.getByRole('button', { name: /^sign in$/i }).click();
  await expect(page).toHaveURL(/\/app\/dashboard/, { timeout: 15000 });
}

/** Attach console/network failure collectors. Call assertNoFailures() at the end of the test. */
export function trackPageHealth(page: Page) {
  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Chrome extension noise is not an application error.
      if (text.includes('chrome-extension://')) return;
      consoleErrors.push(text);
    }
  });

  page.on('pageerror', (err) => {
    consoleErrors.push(`Uncaught exception: ${err.message}`);
  });

  page.on('response', (res) => {
    const url = res.url();
    if (!url.includes('localhost:8000') && !url.includes('localhost:5173')) return;
    if (res.status() >= 400) {
      failedRequests.push(`${res.status()} ${res.request().method()} ${url}`);
    }
  });

  return {
    consoleErrors,
    failedRequests,
    assertNoFailures() {
      expect(consoleErrors, `Unexpected console errors:\n${consoleErrors.join('\n')}`).toEqual([]);
      expect(failedRequests, `Unexpected failed requests:\n${failedRequests.join('\n')}`).toEqual([]);
    },
  };
}
