import { Page, APIResponse, expect } from '@playwright/test';
import { resetAuthAttempts } from './reset-auth-attempts';

export function uniqueUser() {
  const id = `${Date.now()}${Math.floor(Math.random() * 10000)}`;
  return {
    username: `e2e_${id}`.slice(0, 20),
    email: `e2e_${id}@example.com`,
    password: 'TestPass123!',
  };
}

/** The lesson title as rendered by LessonHeader's <h1>.
 *
 * A bare getByText(title) also matches the breadcrumb copy of the same string
 * further up the page, so it fails strict mode with "resolved to 2 elements".
 * Assertions have to say which one they mean; the heading is the one that
 * proves the lesson actually rendered. */
export function lessonTitle(page: Page, title: string) {
  return page.getByRole('heading', { level: 1, name: title });
}

/**
 * Creates a brand-new user straight through the API and lands on the dashboard.
 *
 * Every logged-in spec needs *a* fresh account, not a rehearsal of the signup
 * form, and driving the real form ~100 times a run cost roughly 4s each and
 * re-broke the whole suite the last time Register.tsx grew a field. The form
 * itself stays covered by `registerThroughUiForm` below -- one test, on purpose.
 *
 * The token is written to localStorage under the same key api/client.ts reads
 * (`access_token`), which is the whole of what "being logged in" means here.
 */
export async function registerNewUser(page: Page) {
  const user = uniqueUser();

  const body = {
    username: user.username,
    email: user.email,
    password: user.password,
    preferred_language: 'en',
  };

  let response: APIResponse = await page.request.post('/api/auth/register', { data: body });

  // auth.py caps registrations per IP per hour, and a full run needs ~110 of
  // them -- an order of magnitude over the cap. Clearing the ledger once in
  // globalSetup cannot help: the run itself blows through the allowance well
  // before the hour is up. So the harness clears its own ledger at the moment
  // it trips its own limit, and tries again. The cap is never modified; a real
  // client hitting it still gets a 429.
  if (response.status() === 429) {
    resetAuthAttempts();
    response = await page.request.post('/api/auth/register', { data: body });
  }

  if (!response.ok()) {
    throw new Error(
      `registerNewUser: POST /api/auth/register returned ${response.status()} -- ${await response.text()}`,
    );
  }
  const { access_token: accessToken } = await response.json();

  // Layout.tsx shows the onboarding tour whenever has_completed_onboarding is
  // false, which it is for every account this helper makes. Its backdrop is a
  // full-screen aria-modal overlay, so it silently intercepts every click in
  // every logged-in spec -- tests fail as unexplained click timeouts rather
  // than as anything to do with the tour.
  const onboarding = await page.request.post('/api/auth/me/complete-onboarding', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!onboarding.ok()) {
    throw new Error(
      `registerNewUser: POST /api/auth/me/complete-onboarding returned ${onboarding.status()}`,
    );
  }

  // Seed storage before any app code runs, so the first render is already
  // authenticated and no redirect to /login races us.
  await page.addInitScript((token) => {
    localStorage.setItem('access_token', token);
  }, accessToken);

  await page.goto('/app/dashboard');
  await expect(page).toHaveURL(/\/app\/dashboard/, { timeout: 15000 });
  return user;
}

/** The real signup form, consent checkbox and all. Deliberately used by exactly
 * one test -- see registerNewUser above for why everything else skips it. */
export async function registerThroughUiForm(page: Page) {
  const user = uniqueUser();
  await page.goto('/register');
  await page.getByPlaceholder('Choose a username').fill(user.username);
  await page.getByPlaceholder('you@example.com').fill(user.email);
  await page.locator('#password').fill(user.password);
  await page.locator('#confirmPassword').fill(user.password);
  // Register.tsx refuses to submit without this (see its `agreedToTerms` guard),
  // so skipping it silently parks every logged-in journey on /register.
  await page.locator('#agreedToTerms').check();
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
