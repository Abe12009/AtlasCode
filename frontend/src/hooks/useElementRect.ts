import { useEffect, useState } from 'react';

/** Tracks a DOM element's viewport-relative bounding box by CSS selector,
 * re-measuring on resize. Returns null while the selector is null/absent or
 * the element doesn't exist -- callers treat that as "no target" rather than
 * an error, since it's a normal state (e.g. a mobile viewport intentionally
 * skipping a selector that only exists in the desktop layout). */
export function useElementRect(selector: string | null): DOMRect | null {
  const [rect, setRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    if (!selector) {
      setRect(null);
      return;
    }

    function measure() {
      const el = selector ? document.querySelector(selector) : null;
      setRect(el ? el.getBoundingClientRect() : null);
    }

    measure();
    window.addEventListener('resize', measure);
    // One retry shortly after mount: a step change can land on this selector
    // in the same tick a web-font swap or icon reflow nudges its box.
    const timeout = window.setTimeout(measure, 50);
    return () => {
      window.removeEventListener('resize', measure);
      window.clearTimeout(timeout);
    };
  }, [selector]);

  return rect;
}
