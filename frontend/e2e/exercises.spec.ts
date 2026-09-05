import { test, expect, Page } from '@playwright/test';
import { registerNewUser } from './helpers';

/** Lesson 31 ("Version Control and Git") has exactly one exercise: a multiple
 * choice whose correct option is "Stages changes for commit". Phase 11
 * converted lesson 18 (this file's previous example) into a Micro-Quest, so
 * this file — which specifically exercises the *classic*, non-Micro-Quest
 * per-block lesson flow — moved to a lesson that stayed classic. */
const MCQ_LESSON = '/app/lessons/31';
const CORRECT_OPTION = 'Stages changes for commit';
const WRONG_OPTION = 'Commits changes permanently';

/** Lesson 1 ends with real Python code exercises (the sandbox path). */
const CODE_LESSON = '/app/lessons/1';

/** Click Next until the first exercise renders, whatever the block count. */
async function advanceToExercise(page: Page) {
  for (let i = 0; i < 12; i++) {
    const answered = await page.getByTestId('answer-panel').count();
    const coded = await page.getByTestId('terminal-panel').count();
    if (answered > 0 || coded > 0) return;
    await page.getByTestId('lesson-nav-next').click();
    await page.waitForTimeout(250);
  }
  throw new Error('never reached an exercise');
}

async function readXp(page: Page): Promise<number> {
  const dashboard = await page.evaluate(async () => {
    const res = await fetch('http://localhost:8000/dashboard', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    return res.json();
  });
  return dashboard.profile.xp as number;
}

async function readNotificationTypes(page: Page): Promise<string[]> {
  const notifications = await page.evaluate(async () => {
    const res = await fetch('http://localhost:8000/notifications?limit=50', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    return res.json();
  });
  return (notifications as Array<{ type: string }>).map((n) => n.type);
}

test.describe('Multiple-choice exercises end to end', () => {
  test('wrong answer gives no XP, correct answer completes the lesson, and it survives a refresh', async ({
    page,
  }) => {
    test.setTimeout(90000);
    await registerNewUser(page);

    await page.goto(MCQ_LESSON);
    await expect(page.getByText('Version Control and Git')).toBeVisible({ timeout: 15000 });

    // 1. Reach the real MCQ. It must be radio buttons, not a code editor.
    await advanceToExercise(page);
    await expect(page.getByTestId('mcq-options')).toBeVisible();
    await expect(page.getByRole('radio')).toHaveCount(4);
    await expect(page.getByTestId('terminal-panel')).toHaveCount(0);
    await expect(page.getByText(CORRECT_OPTION)).toBeVisible();

    const xpBefore = await readXp(page);
    expect(xpBefore).toBe(0);

    // 2 & 3. An incorrect option is reported incorrect and awards no XP.
    await page.getByText(WRONG_OPTION).click();
    await page.getByTestId('submit-answer').click();

    const result = page.getByTestId('exercise-result');
    await expect(result).toBeVisible();
    await expect(result).toContainText(/incorrect/i);
    expect(await readXp(page)).toBe(xpBefore);
    expect(await readNotificationTypes(page)).not.toContain('xp_earned');

    // 4 & 5. The correct option completes it and awards the configured XP.
    await page.getByText(CORRECT_OPTION).click();
    await page.getByTestId('submit-answer').click();
    await expect(result).toContainText(/correct/i, { timeout: 15000 });
    await expect(result).not.toContainText(/incorrect/i);

    await expect.poll(async () => await readXp(page), { timeout: 15000 }).toBe(10);

    // 8. Notifications: exactly one XP notification, plus lesson completion,
    // because this lesson's only exercise is now solved.
    await expect
      .poll(async () => (await readNotificationTypes(page)).filter((t) => t === 'xp_earned').length, {
        timeout: 15000,
      })
      .toBe(1);
    const types = await readNotificationTypes(page);
    expect(types.filter((t) => t === 'lesson_completed')).toHaveLength(1);

    // 6 & 7. State is the backend's, so a reload preserves it.
    await page.reload();
    await page.waitForTimeout(800);
    expect(await readXp(page)).toBe(10);

    const status = await page.evaluate(async () => {
      const res = await fetch('http://localhost:8000/lessons/31/progress', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      return (await res.json()).status;
    });
    expect(status).toBe('completed');
  });

  test('resubmitting a solved question awards no further XP or notification', async ({ page }) => {
    test.setTimeout(90000);
    await registerNewUser(page);
    await page.goto(MCQ_LESSON);
    await expect(page.getByText('Version Control and Git')).toBeVisible({ timeout: 15000 });
    await advanceToExercise(page);

    await page.getByText(CORRECT_OPTION).click();
    await page.getByTestId('submit-answer').click();
    await expect(page.getByTestId('exercise-result')).toContainText(/correct/i, { timeout: 15000 });
    await expect.poll(async () => await readXp(page), { timeout: 15000 }).toBe(10);

    // The UI locks a solved question, and the API would award nothing anyway.
    await expect(page.getByTestId('submit-answer')).toBeDisabled();

    const direct = await page.evaluate(async () => {
      const res = await fetch('http://localhost:8000/exercises/42/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ exercise_id: 42, selected_option_id: 38 }),
      });
      return res.json();
    });
    expect(direct.is_correct).toBe(true);
    expect(direct.xp_earned).toBe(0);
    expect(await readXp(page)).toBe(10);
    expect((await readNotificationTypes(page)).filter((t) => t === 'xp_earned')).toHaveLength(1);
  });

  test('the page never receives which option is correct before submitting', async ({ page }) => {
    await registerNewUser(page);
    const payload = await page.evaluate(async () => {
      const res = await fetch('http://localhost:8000/lessons/31', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      return res.text();
    });
    expect(payload).not.toContain('is_correct');
    expect(payload).not.toContain('validation_config');
    expect(payload).not.toContain('solution_code');
    expect(payload).not.toContain('test_code');
    // The options themselves are still delivered, so they can be displayed.
    expect(payload).toContain(CORRECT_OPTION);
  });

  test('MCQ options render translated and RTL in Arabic', async ({ page }) => {
    await registerNewUser(page);
    await page.goto('/app/dashboard');
    await page.locator('button', { hasText: /English|Français|العربية/i }).first().click();
    await page.getByRole('menuitem', { name: /العربية/i }).click();
    await page.waitForTimeout(400);

    await page.goto(MCQ_LESSON);
    await page.waitForTimeout(800);
    expect(await page.evaluate(() => document.documentElement.dir)).toBe('rtl');

    await advanceToExercise(page);
    await expect(page.getByTestId('mcq-options')).toBeVisible();
    await expect(page.getByRole('radio')).toHaveCount(4);
    await expect(page.getByTestId('submit-answer')).toContainText('إرسال الإجابة');

    // Options are Arabic, not the English text.
    await expect(page.getByText(CORRECT_OPTION)).toHaveCount(0);

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(2);
  });

  for (const vp of [
    { name: '320x800', width: 320, height: 800 },
    { name: '375x812', width: 375, height: 812 },
    { name: '768x1024', width: 768, height: 1024 },
    { name: '1024x768', width: 1024, height: 768 },
    { name: '1440x900', width: 1440, height: 900 },
  ]) {
    test(`MCQ answer UI is usable at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);
      await page.goto(MCQ_LESSON);
      await expect(page.getByText('Version Control and Git')).toBeVisible({ timeout: 15000 });
      await advanceToExercise(page);

      await expect(page.getByTestId('mcq-options')).toBeVisible();
      const radios = page.getByRole('radio');
      await expect(radios).toHaveCount(4);

      // Every option stays inside the viewport.
      for (let i = 0; i < 4; i++) {
        const box = await radios.nth(i).boundingBox();
        expect(box).not.toBeNull();
        if (box) {
          expect(box.x).toBeGreaterThanOrEqual(-2);
          expect(box.x + box.width).toBeLessThanOrEqual(vp.width + 2);
        }
      }

      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(overflow, `MCQ caused ${overflow}px overflow at ${vp.name}`).toBeLessThanOrEqual(2);

      // It is genuinely answerable at this width.
      await page.getByText(CORRECT_OPTION).click();
      await expect(page.getByTestId('submit-answer')).toBeEnabled();
      await page.getByTestId('submit-answer').click();
      await expect(page.getByTestId('exercise-result')).toContainText(/correct/i, { timeout: 15000 });
    });
  }
});

test.describe('Code exercises still work end to end', () => {
  test('a real Python exercise runs in the sandbox and awards XP once', async ({ page }) => {
    test.setTimeout(90000);
    await registerNewUser(page);
    await page.goto(CODE_LESSON);
    await expect(page.getByText('What Is Programming?')).toBeVisible({ timeout: 15000 });

    // Lesson 1 has 3 content blocks before its first (code) exercise.
    await advanceToExercise(page);
    await expect(page.getByTestId('terminal-panel')).toBeVisible();
    await expect(page.getByTestId('answer-panel')).toHaveCount(0);

    const editor = page.locator('textarea').first();
    await editor.fill('print("Hello, World!")');
    await page.getByRole('button', { name: /^run( code)?$/i }).first().click();
    await expect(page.locator('body')).toContainText('Hello, World!', { timeout: 20000 });

    await page.getByRole('button', { name: /submit solution/i }).first().click();
    await expect(page.getByTestId('exercise-result')).toContainText(/correct/i, { timeout: 20000 });
    await expect.poll(async () => await readXp(page), { timeout: 15000 }).toBe(10);

    // Resubmitting the same correct solution must not award XP again.
    await page.getByRole('button', { name: /submit solution/i }).first().click();
    await page.waitForTimeout(1500);
    expect(await readXp(page)).toBe(10);
    expect((await readNotificationTypes(page)).filter((t) => t === 'xp_earned')).toHaveLength(1);
  });

  test('an incorrect Python solution is rejected and awards no XP', async ({ page }) => {
    await registerNewUser(page);
    await page.goto(CODE_LESSON);
    await expect(page.getByText('What Is Programming?')).toBeVisible({ timeout: 15000 });
    await advanceToExercise(page);

    const editor = page.locator('textarea').first();
    await editor.fill('print("this is not the expected output")');
    await page.getByRole('button', { name: /submit solution/i }).first().click();

    await expect(page.getByTestId('exercise-result')).toContainText(/incorrect/i, { timeout: 20000 });
    expect(await readXp(page)).toBe(0);
  });
});
