import { describe, it, expect, afterEach } from 'vitest';
import { pinnedBarBottom } from '../Dropdown';

/**
 * `pinnedBarBottom` is the geometry predicate behind the header clearance added
 * in 4d184e0: a bottom-placed panel is pushed past the bar its trigger sits in
 * so the two blurs do not composite. It must NOT fire for a fixed/sticky
 * ancestor that merely *contains* the trigger -- a `fixed inset-0` modal or a
 * `sticky` sidebar card -- because that bottom is hundreds of px lower and the
 * panel ends up at the foot of the viewport, or off it.
 *
 * Geometry is stubbed rather than laid out: jsdom has no layout, so rects are
 * the input to the predicate here. The same shapes were measured for real in
 * Chromium at 1280x800 -- modal trigger bottom 445 -> panel top 986, sticky
 * trigger bottom 137 -> panel top 662 -- and those numbers are what these
 * stubs reproduce.
 */
function rect(el: HTMLElement, top: number, bottom: number) {
  el.getBoundingClientRect = () =>
    ({ top, bottom, left: 0, right: 0, width: 0, height: bottom - top, x: 0, y: top, toJSON: () => ({}) }) as DOMRect;
}

/** container (position + vertical extent) wrapping a trigger at [top, bottom]. */
function nest(position: string, cTop: number, cBottom: number, tTop: number, tBottom: number) {
  const container = document.createElement('div');
  container.style.position = position;
  rect(container, cTop, cBottom);

  const trigger = document.createElement('button');
  rect(trigger, tTop, tBottom);

  container.appendChild(trigger);
  document.body.appendChild(container);
  return trigger;
}

afterEach(() => {
  document.body.innerHTML = '';
});

describe('pinnedBarBottom', () => {
  it('clears a header bar the trigger sits in', () => {
    // app header at 1440px, measured: trigger bottom 50, header bottom 65.
    expect(pinnedBarBottom(nest('fixed', 0, 65, 14, 50))).toBe(65);
  });

  it('ignores a fixed inset-0 modal that only contains the trigger', () => {
    // Overlay.tsx's scrim wrapper in an 800px viewport, measured in Chromium.
    expect(pinnedBarBottom(nest('fixed', 0, 800, 421, 445))).toBe(-Infinity);
  });

  it('ignores a sticky container that only contains the trigger', () => {
    // `sticky top-24` card, 600px tall, trigger near its top.
    expect(pinnedBarBottom(nest('sticky', 96, 696, 113, 137))).toBe(-Infinity);
  });

  it('still clears a sticky bar the trigger sits in', () => {
    expect(pinnedBarBottom(nest('sticky', 0, 56, 10, 46))).toBe(56);
  });

  it('is -Infinity with no pinned ancestor at all', () => {
    const trigger = document.createElement('button');
    rect(trigger, 10, 40);
    document.body.appendChild(trigger);
    expect(pinnedBarBottom(trigger)).toBe(-Infinity);
  });
});
