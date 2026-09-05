import { test, expect } from '@playwright/test';
import { registerNewUser } from './helpers';

async function openLanguageMenu(page: import('@playwright/test').Page) {
  const trigger = page.locator('button', { hasText: /English|Français|العربية/i }).first();
  await trigger.click();
}

async function switchLanguage(page: import('@playwright/test').Page, label: string | RegExp) {
  await openLanguageMenu(page);
  await page.getByRole('menuitem', { name: label }).click();
}

test.describe('Language switching', () => {
  test('EN -> FR -> AR across Dashboard, Courses, Course detail, Lesson', async ({ page }) => {
    await registerNewUser(page);

    // Start: English (default)
    await expect(page).toHaveURL(/\/app\/dashboard$/);
    let dir = await page.evaluate(() => document.documentElement.dir);
    let lang = await page.evaluate(() => document.documentElement.lang);
    expect(dir).toBe('ltr');
    expect(lang).toBe('en');

    // Switch to French
    await switchLanguage(page, /Français/i);
    await expect(page.getByText('Bienvenue')).toBeVisible({ timeout: 10000 });
    dir = await page.evaluate(() => document.documentElement.dir);
    lang = await page.evaluate(() => document.documentElement.lang);
    expect(dir).toBe('ltr');
    expect(lang).toBe('fr');

    await page.goto('/app/courses');
    await expect(page.getByText('Parcourir les cours')).toBeVisible();

    await page.goto('/app/courses/1');
    await expect(page.getByText('Contenu du cours')).toBeVisible();

    // Switch to Arabic and verify RTL
    await switchLanguage(page, /العربية/i);
    dir = await page.evaluate(() => document.documentElement.dir);
    lang = await page.evaluate(() => document.documentElement.lang);
    expect(dir).toBe('rtl');
    expect(lang).toBe('ar');

    await page.goto('/app/dashboard');
    // Arabic dashboard heading contains the Arabic word for "Welcome"
    await expect(page.locator('body')).toContainText('أهلاً');

    // Navigation must remain usable in RTL: Courses nav link is present and clickable.
    const coursesLink = page.getByRole('link', { name: 'الدورات', exact: true });
    await expect(coursesLink).toBeVisible();
    await coursesLink.click();
    await expect(page).toHaveURL(/\/app\/courses$/);

    // Lesson page in Arabic
    await page.goto('/app/lessons/1');
    dir = await page.evaluate(() => document.documentElement.dir);
    expect(dir).toBe('rtl');

    // No leaked/untranslated i18n keys anywhere visible
    const bodyText = await page.locator('body').innerText();
    expect(bodyText).not.toMatch(/[a-z_]+\.[a-z_]+\.[a-z_]+/); // dotted.key.pattern leak heuristic
  });

  test('selected language persists after a full page reload', async ({ page }) => {
    await registerNewUser(page);
    await switchLanguage(page, /العربية/i);
    let dir = await page.evaluate(() => document.documentElement.dir);
    expect(dir).toBe('rtl');

    await page.reload();
    await page.waitForTimeout(500);
    dir = await page.evaluate(() => document.documentElement.dir);
    const lang = await page.evaluate(() => document.documentElement.lang);
    expect(dir).toBe('rtl');
    expect(lang).toBe('ar');
  });
});
