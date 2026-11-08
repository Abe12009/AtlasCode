import { test, expect, Page } from '@playwright/test';
import { registerNewUser } from './helpers';

/**
 * Sequential lesson unlocking, end to end.
 *
 * The backend gates a gated course's lessons (app/services/lesson_gating.py):
 * a lesson opens once the one before it is completed, so a brand-new account
 * may open the first lesson of a course and nothing after it. This walks what
 * a student actually sees: the locked row on the course page, and a pasted
 * deep link to a locked lesson.
 *
 * Resolved from the API rather than hardcoded ids, so a seed reorder retunes
 * the expectations instead of silently testing the wrong lesson.
 */
async function firstCourseSequence(page: Page) {
  return page.evaluate(async () => {
    // Relative, through the dev server's /api proxy: an absolute
    // http://localhost:8000 URL is a cross-origin request and depends on the
    // backend's CORS_ORIGINS listing whichever port Vite happened to take.
    const res = await fetch('/api/courses?language=en', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    const courses = await res.json();
    const course = courses.find(
      (c: { modules?: { lessons?: unknown[] }[] }) =>
        (c.modules ?? []).flatMap((m) => m.lessons ?? []).length >= 2,
    );
    const lessons = (course.modules ?? []).flatMap(
      (m: { lessons?: { id: number; status?: string }[] }) => m.lessons ?? [],
    );
    return {
      courseId: course.id as number,
      first: lessons[0] as { id: number; status?: string },
      second: lessons[1] as { id: number; status?: string },
    };
  });
}

test.describe('sequential lesson unlocking', () => {
  test('a locked lesson is not a link, and its deep link explains itself', async ({ page }) => {
    await registerNewUser(page);

    const { courseId, first, second } = await firstCourseSequence(page);
    // The gate's own verdict, before any UI is involved.
    expect(second.status).toBe('locked');

    await page.goto(`/app/courses/${courseId}`);

    // Expand the first module so its lesson rows render.
    await page.getByRole('button').filter({ hasText: /lesson/i }).first().click();

    const openRow = page.getByTestId(`lesson-row-${first.id}`);
    const lockedRow = page.getByTestId(`lesson-row-${second.id}`);

    await expect(openRow).toBeVisible();
    await expect(openRow).toHaveAttribute('href', `/app/lessons/${first.id}`);

    // The locked row is inert: no href, announced as disabled, no tab stop.
    await expect(lockedRow).toBeVisible();
    await expect(lockedRow).toHaveAttribute('aria-disabled', 'true');
    expect(await lockedRow.getAttribute('href')).toBeNull();
    expect(await lockedRow.evaluate((el) => el.tagName)).not.toBe('A');
    await expect(lockedRow).toContainText(/opens after/i);

    // A pasted deep link to the locked lesson says "locked", not "not found",
    // and offers the lesson that opens it.
    await page.goto(`/app/lessons/${second.id}`);
    await expect(page.getByTestId('lesson-locked-title')).toBeVisible();
    await expect(page.getByText(/this lesson is locked/i)).toBeVisible();
    await expect(page.getByText(/lesson not found/i)).toHaveCount(0);

    const unlocking = page.getByTestId('locked-unlocking-lesson');
    await expect(unlocking).toBeVisible();
    await unlocking.click();
    await expect(page).toHaveURL(new RegExp(`/app/lessons/${first.id}$`));
  });
});
