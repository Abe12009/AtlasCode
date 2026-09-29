import { describe, it, expect } from 'vitest';
import { SHARE_FORMATS, wrapLines } from '../shareCard';

/** One char ~= one unit, so the widths below read as character counts. */
const measure = (s: string) => s.length;

describe('share card title wrapping', () => {
  it('keeps a short title on one line', () => {
    expect(wrapLines('First Lesson', 20, measure)).toEqual(['First Lesson']);
  });

  it('breaks between words rather than mid-word', () => {
    expect(wrapLines('Seven Day Streak Champion', 12, measure)).toEqual([
      'Seven Day',
      'Streak',
      'Champion',
    ]);
  });

  it('keeps a word that is longer than the whole line', () => {
    // Nothing to break on, so it has to survive intact: dropping it would
    // silently truncate someone's achievement title on the shared image.
    expect(wrapLines('Internationalisation', 5, measure)).toEqual(['Internationalisation']);
  });

  it('always returns at least one line', () => {
    // The line count multiplies into the stack height; zero would centre the
    // whole card against the wrong figure.
    expect(wrapLines('', 100, measure)).toHaveLength(1);
  });
});

describe('share formats', () => {
  it('offers a square post and a 9:16 story, both 1080 wide', () => {
    expect(SHARE_FORMATS.post).toEqual({ width: 1080, height: 1080 });
    expect(SHARE_FORMATS.story).toEqual({ width: 1080, height: 1920 });
    expect(SHARE_FORMATS.story.height / SHARE_FORMATS.story.width).toBeCloseTo(16 / 9, 2);
  });
});
