import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Page } from '@playwright/test';

// package.json sets "type": "module", so there is no __dirname here.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = path.resolve(HERE, '../../backend/atlascode.db');

/**
 * Seed one LessonProgress row per lesson, which is the exact thing the gate
 * already honours.
 *
 * `app/services/lesson_gating.py` computes the ceiling as
 * `max(last completed + 1, last touched)`, and documents the second term as
 * what "makes this safe to switch on retroactively -- any lesson the user
 * already has a row for stays reachable, whatever its status". So a `ready`
 * row is the smallest possible nudge: it does not mark anything completed, it
 * does not award XP, and it leaves the rule itself untouched.
 *
 * `INSERT OR IGNORE` against the (user, lesson) pair, so re-running is a
 * no-op and a lesson the user has genuinely started keeps its real status.
 */
const UNLOCK = `
import sqlite3, sys
from datetime import datetime, timezone

db, email, *lesson_ids = sys.argv[1:]
now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
con = sqlite3.connect(db)
try:
    row = con.execute("select id from users where email = ?", (email,)).fetchone()
    if row is None:
        print("no-user")
        raise SystemExit(0)
    user_id = row[0]
    seeded = 0
    for lesson_id in lesson_ids:
        existing = con.execute(
            "select 1 from lesson_progress where user_id = ? and lesson_id = ?",
            (user_id, int(lesson_id)),
        ).fetchone()
        if existing:
            continue
        con.execute(
            "insert into lesson_progress"
            " (user_id, lesson_id, status, xp_earned, current_block, created_at, updated_at)"
            " values (?, ?, 'ready', 0, 0, ?, ?)",
            (user_id, int(lesson_id), now, now),
        )
        seeded += 1
    con.commit()
    print(seeded)
except sqlite3.OperationalError as exc:
    # A fresh checkout may not have migrated yet; not a failure.
    print(f"skipped ({exc})")
finally:
    con.close()
`;

/**
 * Give one account a progress row for each lesson, so the sequential gate lets
 * it open them.
 *
 * This seeds harness state. It does not change the gate, which stays exactly
 * as production enforces it -- `lesson-locking.spec.ts` still drives the real
 * rule against an untouched account and must keep passing. Driven through
 * python rather than a node sqlite driver so e2e gains no dependency, the
 * same way `reset-auth-attempts.ts` does it.
 *
 * Returns false when no interpreter or database could be found, so callers can
 * decide whether that is fatal.
 */
export function unlockLessons(email: string, lessonIds: number[]): boolean {
  if (!existsSync(DB_PATH) || lessonIds.length === 0) return false;
  const args = [DB_PATH, email, ...lessonIds.map(String)];
  for (const binary of ['python', 'python3']) {
    try {
      execFileSync(binary, ['-c', UNLOCK, ...args], { encoding: 'utf8' });
      return true;
    } catch {
      // Try the next interpreter name before giving up.
    }
  }
  return false;
}

/**
 * The lesson each exercise belongs to, resolved from the API.
 *
 * Same approach as `lesson-locking.spec.ts`'s `firstCourseSequence()`:
 * read the real curriculum rather than hardcoding ids, so a seed reorder
 * retunes this instead of silently unlocking the wrong lesson. Relative URL
 * through the dev server's /api proxy, for the CORS reason that spec gives.
 */
export async function lessonIdsForExercises(
  page: Page,
  exerciseIds: number[],
): Promise<number[]> {
  return page.evaluate(async (wanted: number[]) => {
    const res = await fetch('/api/courses?language=en', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    const courses = (await res.json()) as {
      modules?: { lessons?: { id: number; exercises?: { id: number }[] }[] }[];
    }[];
    const found = new Set<number>();
    for (const course of courses) {
      for (const module of course.modules ?? []) {
        for (const lesson of module.lessons ?? []) {
          for (const exercise of lesson.exercises ?? []) {
            if (wanted.includes(exercise.id)) found.add(lesson.id);
          }
        }
      }
    }
    return [...found];
  }, exerciseIds);
}
