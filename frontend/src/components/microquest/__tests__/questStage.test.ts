import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import {
  questStageKey,
  readStoredStage,
  resolveStage,
  writeStoredStage,
} from '../questStage';
import { furthestStage, isQuestStage } from '../types';

describe('questStageKey', () => {
  beforeEach(() => localStorage.clear());

  it('separates two students on the same browser', () => {
    expect(questStageKey('7', 9)).not.toBe(questStageKey('8', 9));
  });

  it('separates two lessons for the same student', () => {
    expect(questStageKey('7', 9)).not.toBe(questStageKey('7', 12));
  });

  it('is stable for the same student and lesson', () => {
    expect(questStageKey('7', 9)).toBe(questStageKey('7', 9));
  });
});

describe('readStoredStage', () => {
  const key = questStageKey('7', 9);

  beforeEach(() => localStorage.clear());
  afterEach(() => vi.restoreAllMocks());

  it('returns null when nothing was ever stored', () => {
    expect(readStoredStage(key)).toBeNull();
  });

  it('round trips a stage that was written', () => {
    writeStoredStage(key, 'quest');
    expect(readStoredStage(key)).toBe('quest');
  });

  it('stores the stage and nothing else — no answers, no identity', () => {
    writeStoredStage(key, 'quest');
    expect(JSON.parse(localStorage.getItem(key) as string)).toEqual({ v: 1, stage: 'quest' });
  });

  // Every one of these is a value a student could put there by hand, or that an
  // older build could have left behind. None may throw.
  it.each([
    ['not json at all', 'wat'],
    ['a bare string', '"quest"'],
    ['an array', '[]'],
    ['null', 'null'],
    ['an object with no stage', '{"v":1}'],
    ['a stage that does not exist', '{"v":1,"stage":"banana"}'],
    ['a numeric stage', '{"v":1,"stage":3}'],
    ['an empty string', ''],
  ])('treats %s as nothing remembered', (_label, raw) => {
    localStorage.setItem(key, raw);
    expect(readStoredStage(key)).toBeNull();
  });

  it('survives a browser that refuses to hand over site data', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('The operation is insecure.', 'SecurityError');
    });
    expect(readStoredStage(key)).toBeNull();
  });
});

describe('writeStoredStage', () => {
  const key = questStageKey('7', 9);

  beforeEach(() => localStorage.clear());
  afterEach(() => vi.restoreAllMocks());

  it('does not throw when storage is full or blocked', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('Quota exceeded.', 'QuotaExceededError');
    });
    expect(() => writeStoredStage(key, 'quest')).not.toThrow();
  });
});

describe('resolveStage', () => {
  it('starts at the hook when nothing is remembered', () => {
    expect(resolveStage(null, false)).toBe('hook');
  });

  it('restores the remembered stage', () => {
    expect(resolveStage('blueprint', false)).toBe('blueprint');
    expect(resolveStage('quest', false)).toBe('quest');
  });

  it('lets the server complete a lesson the browser has forgotten', () => {
    expect(resolveStage(null, true)).toBe('complete');
  });

  it('lets the server complete a lesson the browser thinks is unfinished', () => {
    expect(resolveStage('hook', true)).toBe('complete');
    expect(resolveStage('blueprint', true)).toBe('complete');
  });

  it('refuses a completion the server has not confirmed', () => {
    // Otherwise anyone could write "complete" into localStorage and be shown a
    // Quest Clear screen, with an XP figure, for work never graded.
    expect(resolveStage('complete', false)).toBe('quest');
  });
});

describe('furthestStage', () => {
  it('never moves a student backwards', () => {
    expect(furthestStage('quest', 'hook')).toBe('quest');
    expect(furthestStage('hook', 'quest')).toBe('quest');
    expect(furthestStage('blueprint', 'blueprint')).toBe('blueprint');
    expect(furthestStage('complete', 'quest')).toBe('complete');
  });
});

describe('isQuestStage', () => {
  it('accepts exactly the four stages', () => {
    expect(['hook', 'blueprint', 'quest', 'complete'].every(isQuestStage)).toBe(true);
  });

  it('rejects anything else', () => {
    expect([undefined, null, 3, {}, [], '', 'HOOK', 'done'].some(isQuestStage)).toBe(false);
  });
});
