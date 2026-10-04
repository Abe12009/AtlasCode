import { test, expect, Page } from '@playwright/test';
import { registerNewUser } from './helpers';

/**
 * Verifies that every course the backend serves actually renders in the real
 * UI, and that course detail pages open with real modules.
 *
 * Deliberately NOT a hardcoded title list any more. This file used to carry
 * one ('JavaScript', 'C', 'C++', 'Frontend Development', 'Computer Systems',
 * 'Databases', ...) plus a parallel id->title map for the detail pages, both
 * written against a 15-course curriculum. The seed has since been reorganised
 * to 25 courses and most of those titles no longer exist, while the ids moved
 * under the old names -- id 7 was 'JavaScript' and is now 'Computational
 * Thinking', id 11 was 'C' and is now 'Algorithms & Complexity'. So the test
 * was asserting a curriculum that had not existed for some time, and a fresh
 * hardcoded list would simply go stale again at the next reseed.
 *
 * Reading the list from the API instead is not tautological: the assertion is
 * that the *UI renders what the backend serves*. That still catches a
 * section-grouping bug that silently drops courses, a card that renders
 * without its title, or a detail route that 404s. Only the "which curriculum
 * exists" question moves out of the test, and that question belongs to the
 * seed, not here.
 */

type CatalogCourse = { id: number; title: string };

/** The course list exactly as the app's own client fetches it. */
async function fetchCatalog(page: Page): Promise<CatalogCourse[]> {
  const courses = await page.evaluate(async () => {
    const res = await fetch('http://localhost:8000/courses?language=en', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    if (!res.ok) throw new Error(`GET /courses returned ${res.status}`);
    return res.json();
  });
  return (courses as Array<{ id: number; translations: Array<{ title: string }> }>).map((c) => ({
    id: c.id,
    title: c.translations[0]?.title ?? '',
  }));
}

/**
 * A spread sample, so runtime stays bounded as the curriculum grows while
 * still covering the whole id range rather than only the oldest courses.
 */
function sample<T>(items: T[], max: number): T[] {
  if (items.length <= max) return items;
  const step = (items.length - 1) / (max - 1);
  return Array.from({ length: max }, (_, i) => items[Math.round(i * step)]);
}

test.describe('Course catalog', () => {
  test('every course the API serves is visible on the courses page', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/courses');

    const catalog = await fetchCatalog(page);
    // A smoke floor, not an exact count: catches the API serving an almost
    // empty catalog, without breaking every time a course is added or retired.
    expect(catalog.length, 'the seeded catalog should not be nearly empty').toBeGreaterThan(10);
    const untitled = catalog.filter((c) => c.title === '');
    expect(
      untitled,
      `courses with no English title: ${untitled.map((c) => c.id).join(', ')}`,
    ).toEqual([]);

    // Wait for the first card before reading page text, so this does not race
    // rendering. Scoped to the heading: several locked cards name another
    // course in their "Complete <course> first" prerequisite line, so a bare
    // text match is ambiguous and fails strict mode.
    await expect(page.getByRole('heading', { name: catalog[0].title, exact: true })).toBeVisible({
      timeout: 15000,
    });

    const bodyText = await page.locator('body').innerText();
    const missing = catalog.filter((c) => !bodyText.includes(c.title));
    expect(
      missing,
      `served by the API but absent from the catalog UI: ${missing
        .map((c) => `${c.id} "${c.title}"`)
        .join(', ')}`,
    ).toEqual([]);
  });

  test('course detail pages open and show real modules', async ({ page }) => {
    // Several sequential course pages do not fit the default 30s budget, so
    // the run would otherwise fail at whichever course it reached when time
    // ran out rather than on any real defect.
    test.setTimeout(120000);
    await registerNewUser(page);
    await page.goto('/app/courses');

    const catalog = await fetchCatalog(page);
    expect(catalog.length).toBeGreaterThan(0);

    for (const course of sample(catalog, 12)) {
      await page.goto(`/app/courses/${course.id}`);
      // level: 1 specifically -- the course title is the page's <h1>, while a
      // module inside the course can carry the same name in an <h3> (course 4
      // "Git & GitHub" has exactly such a module), which makes an unleveled
      // heading match ambiguous. Same reason helpers.ts's lessonTitle() pins
      // level 1.
      await expect(
        page.getByRole('heading', { level: 1, name: course.title, exact: true }),
        `course ${course.id} "${course.title}" should open its detail page`,
      ).toBeVisible({ timeout: 10000 });
      // Every course must show at least one real module (not an empty shell).
      await expect(
        page.locator('text=/leçons|lessons|Lessons/i').first(),
        `course ${course.id} "${course.title}" should list real modules`,
      ).toBeVisible();
    }
  });
});
