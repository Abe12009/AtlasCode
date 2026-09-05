import { test, expect } from '@playwright/test';
import { registerNewUser, expectAppShellVisible } from './helpers';

test.describe('Routing', () => {
  test('logged-out user hitting a protected route is redirected to login', async ({ page }) => {
    await page.goto('/app/dashboard');
    await expect(page).toHaveURL(/\/login$/, { timeout: 10000 });
  });

  test('logged-out user can reach public routes directly', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/$/);
    await page.goto('/login');
    await expect(page).toHaveURL(/\/login$/);
    await page.goto('/register');
    await expect(page).toHaveURL(/\/register$/);
  });

  test('logged-in user visiting /login or /register is redirected to the app, not stuck in a loop', async ({ page }) => {
    await registerNewUser(page);

    await page.goto('/login');
    await expect(page).toHaveURL(/\/app\/dashboard$/, { timeout: 10000 });

    await page.goto('/register');
    await expect(page).toHaveURL(/\/app\/dashboard$/, { timeout: 10000 });

    // Revisit dashboard directly: must stay put, not bounce back to landing (regression
    // test for the PublicRoute redirect-to-/dashboard bug that was previously fixed).
    await page.goto('/app/dashboard');
    await page.waitForTimeout(500);
    await expect(page).toHaveURL(/\/app\/dashboard$/);
  });

  test('all main app routes load for a logged-in user', async ({ page }) => {
    await registerNewUser(page);

    const routes = ['/app/dashboard', '/app/courses', '/app/courses/1', '/app/projects', '/app/projects/1', '/app/profile'];
    for (const route of routes) {
      await page.goto(route);
      await expect(page).toHaveURL(new RegExp(route.replace(/\//g, '\\/') + '$'));
      // The app must render its own shell for every route, not an error boundary.
      await expectAppShellVisible(page);
    }
  });

  test('a lesson route loads for a logged-in user', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/lessons/1');
    await expect(page).toHaveURL(/\/app\/lessons\/1$/);
    await expectAppShellVisible(page);
  });

  test('unknown route redirects to landing instead of crashing', async ({ page }) => {
    await page.goto('/this-route-does-not-exist');
    await expect(page).toHaveURL(/\/$/, { timeout: 10000 });
  });
});
