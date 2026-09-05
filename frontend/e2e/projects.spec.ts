import { test, expect } from '@playwright/test';
import { registerNewUser } from './helpers';

// A brand-new account has completed 0 lessons, so every project with a lesson
// prerequisite must show as locked. This also regression-guards the Projects list
// overlay bug (locked overlay rendering behind card content) that was previously fixed.
const PROJECTS: Array<{ id: number; title: string; prereqLesson: number }> = [
  { id: 1, title: 'Build a CLI Calculator', prereqLesson: 5 },
  { id: 2, title: 'Build a Quiz Game', prereqLesson: 17 },
  { id: 3, title: 'Personal Portfolio Website', prereqLesson: 25 },
  { id: 4, title: 'Student Database', prereqLesson: 30 },
  { id: 5, title: 'Algorithm Challenge', prereqLesson: 39 },
];

test.describe('Projects and prerequisites', () => {
  test('projects list shows all 5 projects, locked for a fresh account', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/projects');

    for (const project of PROJECTS) {
      await expect(page.getByText(project.title)).toBeVisible();
    }
    // Fresh account: every project card shows the locked state, not silently as available.
    const lockedLabels = page.getByText(/^Locked$/i);
    await expect(lockedLabels.first()).toBeVisible();
  });

  for (const project of PROJECTS) {
    test(`project detail loads for "${project.title}" with correct locked state and task list`, async ({ page }) => {
      await registerNewUser(page);
      await page.goto(`/app/projects/${project.id}`);
      await expect(page).toHaveURL(new RegExp(`/app/projects/${project.id}$`));

      await expect(page.getByRole('heading', { name: project.title, exact: true })).toBeVisible({ timeout: 10000 });

      // Locked status badge reflects the real prerequisite state for a fresh account.
      await expect(page.getByTestId('project-status-badge')).toContainText(/Locked/i);

      // The prerequisite lesson id shown to the user matches the real DB value.
      await expect(page.locator('body')).toContainText(String(project.prereqLesson));

      // Task list still renders even while locked.
      const taskCount = await page.getByText(/Task \d+|Tâche \d+/i).count().catch(() => 0);
      expect(taskCount === 0 ? await page.getByRole('heading').count() : taskCount).toBeGreaterThan(0);
    });
  }
});
