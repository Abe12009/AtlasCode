/**
 * Live mobile/narrow-viewport pass requested for the flows the existing
 * responsive*.spec.ts files don't already cover: the registration page
 * itself (not just what comes after it), the onboarding tour's mobile
 * fallback path, profile/settings, and the Cody chat bubble/panel.
 *
 * Playwright's page.setViewportSize genuinely resizes the layout viewport
 * (unlike the Chrome-extension automation tool used for a prior manual
 * pass, which reported success but never actually changed window.innerWidth)
 * -- every assertion below is verified against a real resized viewport.
 */
import { test, expect, type Page } from '@playwright/test';
import { registerNewUser, expectAppShellVisible } from './helpers';

const WIDTHS = [
  { name: '375x812', width: 375, height: 812 },
  { name: '768x1024', width: 768, height: 1024 },
];

const MIN_TAP_TARGET = 44;

async function assertNoHorizontalOverflow(page: Page, label: string) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow, `Horizontal overflow of ${overflow}px on ${label}`).toBeLessThanOrEqual(2);
}

/** A freshly registered account always starts with the onboarding tour
 * showing on the dashboard (has_completed_onboarding=false) -- its dimmed
 * backdrop correctly intercepts clicks on the page behind it (confirmed
 * separately in the "onboarding tour fallback" tests below), so any test
 * that needs to interact with the dashboard/profile/Cody bubble first must
 * dismiss it, the same as a real user would. */
async function dismissOnboardingIfPresent(page: Page) {
  const tour = page.getByRole('dialog', { name: /onboarding tour/i });
  // The tour mounts asynchronously after the post-registration user fetch
  // resolves, so an immediate isVisible() check races it and reports false
  // moments before it actually appears -- wait briefly for it instead of
  // checking once.
  const appeared = await tour
    .waitFor({ state: 'visible', timeout: 3000 })
    .then(() => true)
    .catch(() => false);
  if (appeared) {
    await tour.getByRole('button', { name: /skip/i }).click();
    await expect(tour).not.toBeVisible();
  }
}

async function assertTapTargetsReachable(page: Page, locator: ReturnType<Page['locator']>, label: string) {
  const count = await locator.count();
  for (let i = 0; i < count; i++) {
    const el = locator.nth(i);
    if (!(await el.isVisible())) continue;
    const box = await el.boundingBox();
    if (!box) continue;
    expect(box.width, `${label} tap target #${i} width`).toBeGreaterThanOrEqual(MIN_TAP_TARGET - 4);
    expect(box.height, `${label} tap target #${i} height`).toBeGreaterThanOrEqual(MIN_TAP_TARGET - 4);
  }
}

test.describe('Mobile pass: registration page', () => {
  for (const vp of WIDTHS) {
    test(`registration form fits and is usable at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto('/register');
      await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
      await assertNoHorizontalOverflow(page, `/register at ${vp.name}`);

      // The submit button and both OAuth buttons are the primary tap targets
      // on this page; they must be comfortably tappable, not just visible.
      await assertTapTargetsReachable(
        page,
        page.getByRole('button', { name: /create account|google|github/i }),
        `/register at ${vp.name}`,
      );
    });
  }
});

test.describe('Mobile pass: onboarding tour fallback', () => {
  for (const vp of WIDTHS) {
    test(`onboarding tour shows a centered fallback (no spotlight) at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      // A freshly registered account starts with has_completed_onboarding=false,
      // so the tour auto-starts on landing at the dashboard -- no DB setup needed.
      await registerNewUser(page);

      const tour = page.getByRole('dialog', { name: /onboarding tour/i });
      await expect(tour).toBeVisible({ timeout: 10000 });
      await assertNoHorizontalOverflow(page, `onboarding tour at ${vp.name}`);

      // Below the 1024px desktop breakpoint OnboardingTour skips the
      // spotlight cutout entirely (isDesktop is false, so targetSelector is
      // null) -- confirm the caption card itself still renders fully inside
      // the viewport instead of relying on a spotlight rect to position it.
      const skip = tour.getByRole('button', { name: /skip/i });
      const next = tour.getByRole('button', { name: /^next$/i });
      await expect(skip).toBeVisible();
      await expect(next).toBeVisible();
      const skipBox = await skip.boundingBox();
      const nextBox = await next.boundingBox();
      for (const box of [skipBox, nextBox]) {
        expect(box).not.toBeNull();
        if (box) {
          expect(box.x).toBeGreaterThanOrEqual(0);
          expect(box.x + box.width).toBeLessThanOrEqual(vp.width + 2);
        }
      }

      // Step through once (this step navigates to /app/courses) and confirm
      // the fallback still holds together after a route change mid-tour.
      await next.click();
      await expect(page).toHaveURL(/\/app\/courses/);
      await assertNoHorizontalOverflow(page, `onboarding tour step 2 at ${vp.name}`);
      await expect(tour.getByRole('button', { name: /skip/i })).toBeVisible();

      await tour.getByRole('button', { name: /skip/i }).click();
      await expect(tour).not.toBeVisible();
    });
  }
});

test.describe('Mobile pass: profile/settings', () => {
  for (const vp of WIDTHS) {
    test(`profile settings tab fits at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);
      await dismissOnboardingIfPresent(page);
      await page.goto('/app/profile');
      await expectAppShellVisible(page);

      await page.getByRole('button', { name: /^settings$/i }).click();
      await expect(page.getByRole('heading', { name: /feedback/i })).toBeVisible();
      await assertNoHorizontalOverflow(page, `/app/profile settings tab at ${vp.name}`);

      // Privacy radios and the language select are the tab's real controls;
      // they must not be clipped or squeezed below a tappable size.
      const radios = page.locator('input[type="radio"]');
      const radioCount = await radios.count();
      expect(radioCount).toBeGreaterThan(0);
      for (let i = 0; i < radioCount; i++) {
        await expect(radios.nth(i)).toBeVisible();
      }

      await expect(page.getByRole('button', { name: /delete account/i })).toBeVisible();
    });
  }
});

test.describe('Mobile pass: Cody bubble and panel', () => {
  for (const vp of WIDTHS) {
    test(`Cody bubble opens a panel that fits at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await registerNewUser(page);
      await dismissOnboardingIfPresent(page);
      await page.goto('/app/dashboard');

      const bubble = page.getByRole('button', { name: /open cody chat/i });
      await expect(bubble).toBeVisible();

      const bubbleBox = await bubble.boundingBox();
      expect(bubbleBox).not.toBeNull();
      if (bubbleBox) {
        // The bubble itself must be a comfortable tap target and fully
        // on-screen, not clipped by the narrower viewport.
        expect(bubbleBox.width).toBeGreaterThanOrEqual(MIN_TAP_TARGET - 4);
        expect(bubbleBox.height).toBeGreaterThanOrEqual(MIN_TAP_TARGET - 4);
        expect(bubbleBox.x).toBeGreaterThanOrEqual(0);
        expect(bubbleBox.x + bubbleBox.width).toBeLessThanOrEqual(vp.width + 2);
      }

      await bubble.click();
      const panel = page.getByRole('dialog', { name: /cody chat/i });
      await expect(panel).toBeVisible();

      const panelBox = await panel.boundingBox();
      expect(panelBox).not.toBeNull();
      if (panelBox) {
        // PANEL_WIDTH is a fixed 360px with a calc(100vw - 2rem) max-width --
        // at 375px viewport width that max-width clause is load-bearing.
        expect(panelBox.x).toBeGreaterThanOrEqual(-1);
        expect(panelBox.x + panelBox.width).toBeLessThanOrEqual(vp.width + 2);
        expect(panelBox.y).toBeGreaterThanOrEqual(0);
        expect(panelBox.y + panelBox.height).toBeLessThanOrEqual(vp.height + 2);
      }
      await assertNoHorizontalOverflow(page, `Cody panel open at ${vp.name}`);

      // The bubble itself relabels to "Close Cody chat" while open, so scope
      // to the panel's own close button rather than page.getByRole, which
      // would ambiguously match both.
      await panel.getByRole('button', { name: /close cody chat/i }).click();
      await expect(panel).not.toBeVisible();
    });
  }
});
