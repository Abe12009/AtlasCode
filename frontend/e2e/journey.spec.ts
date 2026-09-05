import { test, expect } from '@playwright/test';
import { registerNewUser, trackPageHealth } from './helpers';

// Full primary journey against the real running frontend + backend, one continuous
// authenticated session: Landing -> Register -> Dashboard -> Courses -> Course detail
// -> Lesson -> run/submit a real Python exercise -> XP verification -> refresh does not
// re-award XP -> reopening preserves progress -> Projects -> Profile.

test.describe('Primary user journey', () => {
  test('landing page loads with real content', async ({ page }) => {
    const health = trackPageHealth(page);
    await page.goto('/');
    await expect(page.locator('body')).toContainText(/AtlasCode/i);
    health.assertNoFailures();
  });

  test('register -> dashboard -> course -> lesson -> exercise -> XP -> projects -> profile', async ({ page }) => {
    const health = trackPageHealth(page);

    // Landing -> Register -> Dashboard
    const user = await registerNewUser(page);
    await expect(page.getByText(user.username).first()).toBeVisible();

    // Dashboard shows real, translated content (regression check for leaked i18n keys)
    await expect(page.locator('body')).not.toContainText('dashboard.quest_board');
    await expect(page.locator('body')).not.toContainText('dashboard.days');

    // Dashboard -> Courses
    await page.getByRole('link', { name: /^Courses$/i }).click();
    await expect(page).toHaveURL(/\/app\/courses$/);
    await expect(page.getByText('Python Foundations')).toBeVisible();

    // Courses -> Course detail (Python Foundations, course id 1)
    await page.getByText('Python Foundations').click();
    await expect(page).toHaveURL(/\/app\/courses\/1$/);
    await expect(page.getByText('Getting Started')).toBeVisible();

    // Expand first module -> open first lesson ("What Is Programming?")
    await page.getByText('Getting Started').click();
    const firstLessonLink = page.getByRole('link', { name: /What Is Programming\?/i }).first();
    await expect(firstLessonLink).toBeVisible();
    await firstLessonLink.click();
    await expect(page).toHaveURL(/\/app\/lessons\/\d+$/);

    // Jump directly to the first exercise via the lesson sidebar (more reliable than
    // repeatedly clicking Next through every content block).
    await page.getByRole('button', { name: /^Exercise 1$/i }).click();

    const runButton = page.getByRole('button', { name: /Run Code/i }).last();
    await expect(runButton).toBeVisible({ timeout: 10000 });

    // RUN the starter Python code and verify real output comes back from the sandbox
    await runButton.click();
    await expect(page.getByText(/Hello, World!/i).first()).toBeVisible({ timeout: 15000 });

    // SUBMIT the exercise and verify a real XP-earning response
    const submitButton = page.getByRole('button', { name: /Submit Solution/i });
    await submitButton.click();
    await expect(page.getByText(/Correct!/i).first()).toBeVisible({ timeout: 15000 });

    // Read XP on the dashboard right after the first correct submission.
    await page.goto('/app/dashboard');
    await expect(page.getByText(/^XP$/)).toBeVisible();
    const xpAfterFirstSubmit = await readXp(page);
    expect(xpAfterFirstSubmit).toBeGreaterThan(0);

    // Lesson-level progress must now show a real, non-locked state on the course detail
    // page — regression check for the bug where status was hardcoded by list position
    // instead of real backend progress. The lesson has 3 exercises; only exercise 1 is
    // solved so far, so it is "current" (in progress), not yet "Completed".
    await page.goto('/app/courses/1');
    await page.getByText('Getting Started').click();
    await expect(page.getByText(/^Current$/i).first()).toBeVisible({ timeout: 10000 });

    // A plain reload must not change XP (no accidental re-award just from viewing the page).
    await page.reload();
    await page.waitForTimeout(500);

    // Reopen the same lesson and resubmit the identical, already-correct solution: XP must
    // NOT increase a second time for a solution already scored correct once.
    await firstLessonLinkReopen(page);
    await page.getByRole('button', { name: /^Exercise 1$/i }).click();
    await page.getByRole('button', { name: /Run Code/i }).last().click();
    await expect(page.getByText(/Hello, World!/i).first()).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Submit Solution/i }).click();
    await expect(page.getByText(/Correct!/i).first()).toBeVisible({ timeout: 15000 });

    await page.goto('/app/dashboard');
    const xpAfterSecondSubmit = await readXp(page);
    expect(xpAfterSecondSubmit).toBe(xpAfterFirstSubmit);

    health.assertNoFailures();

    // Projects flow
    await page.goto('/app/projects');
    await expect(page.getByText('Build a CLI Calculator')).toBeVisible();
    await page.getByText('Build a CLI Calculator').click();
    await expect(page).toHaveURL(/\/app\/projects\/\d+$/);

    // Profile flow
    await page.goto('/app/profile');
    await expect(page.getByText(user.username).first()).toBeVisible();
    await expect(page.getByText(user.email).first()).toBeVisible();

    health.assertNoFailures();
  });
});

async function readXp(page: import('@playwright/test').Page): Promise<number> {
  const xpLabel = page.getByText(/^XP$/).first();
  const card = xpLabel.locator('..');
  const text = await card.innerText();
  const match = text.match(/\d+/);
  if (!match) throw new Error(`Could not parse XP from card text: "${text}"`);
  return Number(match[0]);
}

async function firstLessonLinkReopen(page: import('@playwright/test').Page) {
  await page.goto('/app/courses/1');
  await page.getByText('Getting Started').click();
  const link = page.getByRole('link', { name: /What Is Programming\?/i }).first();
  await link.click();
}
