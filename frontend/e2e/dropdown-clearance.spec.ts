import { test, expect, Page } from '@playwright/test';
import { registerNewUser } from './helpers';

/**
 * Where a bottom-placed Dropdown panel lands, measured.
 *
 * 4d184e0 made the panel clear its nearest fixed/sticky ancestor instead of its
 * trigger, so a header menu stops overlapping the header's lower edge and the
 * two blurs stop compositing. That is right for a BAR the trigger sits in and
 * wrong for a container that merely encloses it: the mobile menu's own header
 * is `fixed` and extends 73px below the language trigger, which put the panel
 * 142px from it (measured, 375x812, EN and AR).
 */

/** The three header menus, in DOM order within <header>. */
const HEADER_MENUS = ['language switcher', 'notification bell', 'user menu'];

async function useLanguage(page: Page, lang: string) {
  await page.addInitScript((l) => localStorage.setItem('i18nextLng', l), lang);
}

/** Geometry of the open panel belonging to the nth `aria-haspopup` trigger. */
async function placement(page: Page, selector: string, nth: number) {
  return page.evaluate(({ selector, nth }) => {
    const trigger = document.querySelectorAll<HTMLElement>(selector)[nth];
    const wrapper = trigger.closest('.relative.inline-block')!;
    const panel = wrapper.querySelector<HTMLElement>('[role="menu"]')!;
    const header = document.querySelector('header')!;
    return {
      triggerBottom: trigger.getBoundingClientRect().bottom,
      // The panel's own computed viewport coordinate. Deliberately the inline
      // style and not getBoundingClientRect(): the panel is `position: fixed`,
      // and inside the mobile menu an ancestor carries `backdrop-filter`, which
      // makes that ancestor the containing block -- so the rendered rect is the
      // computed value plus the menu's origin, and comparing it to the trigger
      // would be comparing two different coordinate spaces.
      computedTop: parseFloat(panel.style.top),
      panelTop: panel.getBoundingClientRect().top,
      headerBottom: header.getBoundingClientRect().bottom,
    };
  }, { selector, nth });
}

async function openMenu(page: Page, selector: string, nth: number) {
  await page.evaluate(({ selector, nth }) => {
    document.querySelectorAll<HTMLElement>(selector)[nth].click();
  }, { selector, nth });
  await page.waitForTimeout(400);
}

for (const lang of ['en', 'ar']) {
  test.describe(`Dropdown clearance (${lang})`, () => {
    test(`header menus clear the header with no overlap (${lang})`, async ({ page }) => {
      await page.setViewportSize({ width: 1440, height: 900 });
      await useLanguage(page, lang);
      await registerNewUser(page);
      await page.goto('/app/dashboard');
      await expect(page.locator('header button[aria-haspopup="true"]')).toHaveCount(3);

      for (const [nth, name] of HEADER_MENUS.entries()) {
        await openMenu(page, 'header button[aria-haspopup="true"]', nth);
        const { panelTop, headerBottom, triggerBottom } = await placement(
          page, 'header button[aria-haspopup="true"]', nth,
        );
        // The whole point of 4d184e0: the panel starts at or below the header's
        // bottom edge, never inside it. Measured 73 vs 65 for all three.
        expect(
          Math.max(0, headerBottom - panelTop),
          `${name} (${lang}) overlaps the header by ${headerBottom - panelTop}px ` +
            `(panel top ${panelTop}, header bottom ${headerBottom}, trigger bottom ${triggerBottom})`,
        ).toBe(0);
        await openMenu(page, 'header button[aria-haspopup="true"]', nth);
      }
    });

    test(`a menu inside the mobile menu stays with its trigger (${lang})`, async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 });
      await useLanguage(page, lang);
      await registerNewUser(page);
      await page.goto('/app/dashboard');

      await page.locator('button[aria-controls="mobile-menu"]').click();
      await expect(page.locator('#mobile-menu')).toBeVisible();

      const selector = '#mobile-menu button[aria-haspopup="true"]';
      await openMenu(page, selector, 0);
      const { computedTop, triggerBottom } = await placement(page, selector, 0);

      // 8px offset + at most the 24px of bar slack the clearance is allowed.
      // Before the clearance was restricted this read 556 against a trigger
      // bottom of 475 -- the enclosing header's bottom, 81px away.
      expect(
        computedTop - triggerBottom,
        `language menu (${lang}) was placed ${computedTop - triggerBottom}px below its ` +
          `trigger (panel top ${computedTop}, trigger bottom ${triggerBottom})`,
      ).toBeLessThanOrEqual(32);
    });
  });
}
