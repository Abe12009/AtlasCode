import { useCallback, useEffect, useState } from 'react';
import { furthestStage, isQuestStage, type QuestStage } from './types';

/** Bumping the version retires every previously stored value at once, which is
 * what we want if the stage vocabulary ever changes. */
const STORAGE_PREFIX = 'atlascode.microquest.stage.v1';

/** localStorage is per-origin, so the key has to carry *who* as well as *what*:
 * without the user segment, the next student to sign in on a shared computer
 * would inherit the previous one's Micro-Quest position. */
export function questStageKey(userKey: string, lessonId: number | string): string {
  return `${STORAGE_PREFIX}:${userKey}:${lessonId}`;
}

/**
 * The furthest stage this browser remembers for one lesson, or null.
 *
 * Everything here is defensive on purpose: the value is user-writable, may
 * have been written by an older build, and reading localStorage at all throws
 * in a browser configured to block site data. A bad value simply means
 * "nothing remembered" — never an exception that takes the lesson down.
 */
export function readStoredStage(key: string): QuestStage | null {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    if (typeof parsed !== 'object' || parsed === null) return null;
    const stage = (parsed as { stage?: unknown }).stage;
    return isQuestStage(stage) ? stage : null;
  } catch {
    return null;
  }
}

/** Store the stage and nothing else: no answers, no code, no identity. */
export function writeStoredStage(key: string, stage: QuestStage): void {
  try {
    localStorage.setItem(key, JSON.stringify({ v: 1, stage }));
  } catch {
    // Private mode, a full quota, or site data blocked outright. Losing the
    // resume point is not worth breaking the lesson over.
  }
}

/**
 * Reconcile what the browser remembers with what the server knows.
 *
 * The server owns completion. A stored 'complete' the server does not confirm
 * is therefore not trusted — honouring it would show Quest Clear, and an XP
 * figure, for an exercise that was never graded. Such a claim is downgraded to
 * 'quest', which is as far as the student demonstrably got.
 */
export function resolveStage(stored: QuestStage | null, isCompleted: boolean): QuestStage {
  if (isCompleted) return 'complete';
  if (stored === 'complete') return 'quest';
  return stored ?? 'hook';
}

interface StageState {
  /** The storage key `stage` belongs to. Carried in state so a write can never
   * land under a key the value was not computed for. */
  key: string;
  stage: QuestStage;
  /** True once localStorage and the server's progress have been folded in. */
  restored: boolean;
}

interface UseQuestStageOptions {
  lessonId: number | string;
  /** Stable identity of the signed-in student; 'anon' when there is none. */
  userKey: string;
  /** Straight from the backend's lesson progress. Always wins. */
  isCompleted: boolean;
  /** False while auth or progress is still loading — nothing is read or
   * written until we know which student we are looking at. */
  ready: boolean;
}

/**
 * The Micro-Quest's current stage, restored across reloads.
 *
 * Server-side lesson and exercise progress stays the source of truth for
 * completion and XP. This remembers only how far through the *presentation*
 * the student had got, so a reload does not drop them back at the Hook.
 */
export function useQuestStage({ lessonId, userKey, isCompleted, ready }: UseQuestStageOptions) {
  const key = questStageKey(userKey, lessonId);
  const [state, setState] = useState<StageState>({ key, stage: 'hook', restored: false });

  useEffect(() => {
    if (!ready) return;
    const restored = resolveStage(readStoredStage(key), isCompleted);
    // This is exactly the case an effect is for: two external systems
    // (localStorage and the server's progress row) are being folded into
    // render state, and neither is knowable during render.
    // oxlint-disable-next-line react/set-state-in-effect
    setState((prev) =>
      prev.key === key
        ? // Never move a student backwards: they may already have clicked past
          // the Hook while the progress request was still in flight.
          { key, stage: furthestStage(prev.stage, restored), restored: true }
        : // A different student (or lesson) now owns this component. Their
          // stage starts from their own storage, never from the last one's.
          { key, stage: restored, restored: true },
    );
  }, [key, ready, isCompleted]);

  useEffect(() => {
    if (!state.restored) return;
    writeStoredStage(state.key, state.stage);
  }, [state]);

  const advanceTo = useCallback(
    (next: QuestStage) => {
      setState((prev) =>
        prev.key === key
          ? { ...prev, stage: furthestStage(prev.stage, next) }
          : { key, stage: next, restored: false },
      );
    },
    [key],
  );

  return { stage: state.key === key ? state.stage : 'hook', advanceTo };
}
