import { test, expect, Page } from '@playwright/test';

/**
 * prefers-reduced-motion on the landing page.
 *
 * Two separate things have to hold, and both have been broken here before:
 *
 *  1. The entrance animations must actually exist. `.animate-fade-in` and its
 *     siblings were written as
 *     `animation: fadeIn var(--transition-normal) var(--animate-ease) both`,
 *     but `--transition-normal` is `200ms cubic-bezier(...)` -- duration AND
 *     easing -- so the shorthand carried two easing functions, was invalid,
 *     and the whole declaration was dropped. Every entrance animation in the
 *     app was silently inert, computing `animation-name: none`.
 *
 *  2. With them working, reduced motion must not leave content invisible.
 *     The global block collapsed `animation-duration` but not
 *     `animation-delay`, and these animations use `fill-mode: both` -- which
 *     includes `backwards`, pinning the element to the first keyframe
 *     (`opacity: 0`) for the whole delay. Landing staggers up to 500ms, so a
 *     reduced-motion visitor would have watched blank boxes pop in one by one.
 *
 * The precondition assertion below is what stops this spec passing vacuously:
 * if the animations go inert again, it fails rather than reporting a happy
 * "nothing staggers".
 */

const VIEWPORT = { width: 1440, height: 900 };

async function landing(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('atlascode.theme', 'dark');
    localStorage.setItem('i18nextLng', 'en');
  });
  await page.goto('/');
  // Longer than the largest delay on the page (500ms) plus its duration.
  await page.waitForTimeout(2000);
}

/** Every element carrying one of the entrance classes, with what it computes. */
async function entranceElements(page: Page) {
  return page.evaluate(() =>
    [...document.querySelectorAll('[class*="animate-fade-in"], [class*="animate-slide-up"], [class*="animate-scale-in"]')].map((el) => {
      const cs = getComputedStyle(el);
      return {
        name: cs.animationName,
        delayMs: (cs.animationDelay.split(',')[0] || '').trim(),
        durationMs: (cs.animationDuration.split(',')[0] || '').trim(),
        fill: cs.animationFillMode,
        opacity: Number(cs.opacity),
        inlineDelay: (el.getAttribute('style') || '').includes('animation-delay'),
        text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 24),
      };
    }),
  );
}

test.describe('prefers-reduced-motion on Landing', () => {
  test.use({ viewport: VIEWPORT });

  test('entrance animations exist at all (guards the guard)', async ({ page }) => {
    await landing(page);
    const els = await entranceElements(page);
    expect(els.length, 'landing should carry entrance-animated elements').toBeGreaterThan(5);
    const live = els.filter((e) => e.name !== 'none');
    expect(
      live.length,
      'every entrance class must resolve to a real animation -- `animation-name: none` means ' +
        'the shorthand is invalid again and the reduced-motion assertions below prove nothing',
    ).toBe(els.length);
    // And at least one of them is actually staggered, or there is no stagger to neutralise.
    expect(
      els.filter((e) => e.inlineDelay).length,
      'landing should still stagger some entrances, or this spec is testing nothing',
    ).toBeGreaterThan(0);
  });

  test.describe('with reduce emulated', () => {
    test('no entrance is delayed, and every one ends visible', async ({ page }) => {
      // emulateMedia rather than `test.use({ reducedMotion })`: nested
      // test.use did not take effect here, and the precondition below caught
      // it -- the test was measuring a normal-motion page and reporting on it.
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await landing(page);
      // Precondition: the emulation is actually on. Without this the whole
      // test can pass or fail for reasons that have nothing to do with the CSS.
      expect(
        await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches),
        'reduced motion is not being emulated, so this test proves nothing',
      ).toBe(true);

      const els = await entranceElements(page);
      expect(els.length).toBeGreaterThan(5);

      const delayed = els.filter((e) => e.delayMs !== '0s');
      expect(
        delayed.map((e) => `${e.text}: ${e.delayMs}`),
        'reduced motion must collapse every animation-delay to 0s',
      ).toEqual([]);

      // The real failure mode: `fill-mode: both` holds the element at the
      // first keyframe (opacity 0) for the length of the delay.
      const invisible = els.filter((e) => e.opacity < 0.99);
      expect(
        invisible.map((e) => `${e.text}: opacity ${e.opacity}`),
        'reduced motion must never leave an element stuck at its first keyframe',
      ).toEqual([]);
    });
  });

  test('without reduce, the staggered entrance is preserved', async ({ page }) => {
    // The fix must not flatten the designed animation for everyone else.
    await landing(page);
    const els = await entranceElements(page);
    expect(
      els.some((e) => e.delayMs !== '0s'),
      'a visitor without the preference should still get the staggered entrance',
    ).toBe(true);
    expect(els.every((e) => e.opacity > 0.99), 'nothing should be left invisible here either').toBe(true);
  });
});
