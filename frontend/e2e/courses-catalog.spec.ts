import { test, expect } from '@playwright/test';
import { registerNewUser } from './helpers';

// Verifies all 15 real courses (5 preserved + 10 newly seeded) appear via the real UI,
// by checking meaningful titles rather than a hardcoded DOM count.
const EXPECTED_COURSE_TITLES = [
  'Python Foundations',
  'Web Fundamentals',
  'SQL & Databases',
  'Git & GitHub',
  'CS Fundamentals',
  'Databases',
  'JavaScript',
  'Frontend Development',
  'Backend Development',
  'Full Stack Development',
  'C++', // check before 'C' since 'C' is a substring
  'Data Structures & Algorithms',
  'Computer Systems',
  'Networking',
];

test.describe('Course catalog', () => {
  test('all required courses are visible on the courses page', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/courses');
    await expect(page.getByText('Python Foundations')).toBeVisible({ timeout: 15000 });

    const bodyText = await page.locator('body').innerText();
    for (const title of EXPECTED_COURSE_TITLES) {
      expect(bodyText, `Expected course "${title}" to be listed`).toContain(title);
    }
    // 'C' as a standalone course card title (not a substring match)
    await expect(page.getByRole('heading', { name: 'C', exact: true })).toBeVisible();
  });

  test('course detail pages open and show real modules for representative courses', async ({ page }) => {
    // Twelve sequential course pages do not fit the default 30s budget; it was
    // already taking ~28s, so the run failed at whichever course it happened to
    // reach when time ran out rather than on any real defect.
    test.setTimeout(120000);
    await registerNewUser(page);

    const courseIdsAndTitles: Array<[number, string]> = [
      [1, 'Python Foundations'],
      [7, 'JavaScript'],
      [3, 'SQL & Databases'],
      [6, 'Databases'],
      [8, 'Frontend Development'],
      [9, 'Backend Development'],
      [10, 'Full Stack Development'],
      [11, 'C'],
      [12, 'C++'],
      [13, 'Data Structures & Algorithms'],
      [14, 'Computer Systems'],
      [15, 'Networking'],
    ];

    for (const [id, title] of courseIdsAndTitles) {
      await page.goto(`/app/courses/${id}`);
      await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible({ timeout: 10000 });
      // Every course must show at least one real module (not an empty shell).
      await expect(page.locator('text=/leçons|lessons|Lessons/i').first()).toBeVisible();
    }
  });
});
