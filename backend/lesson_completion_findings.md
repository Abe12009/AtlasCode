# Finding: exercise submit does not complete a lesson unless `/start` ran first

Observed 2026-09-29 while verifying the achievement share cards. **Not fixed,
not chased** — written down to be looked at as its own task.

## What was seen

Submitting the correct answer to lesson 31's *only* exercise, straight through
the API, awarded the exercise XP but left the lesson untouched:

| | XP total | `lesson_progress.status` | `completed_at` | achievements |
|---|---|---|---|---|
| `POST /exercises/42/submit` alone | 10 | `ready` | `null` | none |
| `POST /lessons/31/start` **then** submit | **60** | **`completed`** | set | `first-lesson` |

Both runs used a brand-new account, and `submit` returned `200` with
`is_correct: true` and `xp_earned: 10` either way. The difference is entirely
in what happens *around* the award.

60 = 10 (exercise 42) + 50 (lesson 31's own `xp_reward`), which is exactly what
the seed predicts.

## Why

`app/api/exercises.py:203` guards the whole completion block:

```python
lesson_progress = lesson_progress_result.scalar_one_or_none()
if lesson_progress:
    ...
    if correct_count >= total_exercises and total_exercises > 0:
        lesson_progress.status = MissionStatusEnum.completed
        profile.completed_lessons += 1
        # lesson_completed notification, course progress, achievements
```

The `LessonProgress` row is created by `POST /lessons/{id}/start`, which the UI
calls when a lesson is opened. With no row, `if lesson_progress:` is false and
the entire branch is skipped silently — no completed status, no
`completed_lessons` increment, no `lesson_completed` notification, no course
progress roll-up, no achievement, and no lesson XP. The request still returns
`200`, so nothing signals that half the work did not happen.

## What this is and is not

It is **not** a defect in the completion logic, and it is not reachable through
the UI, which always starts a lesson before showing its exercises. The open
question is whether `submit` should be resilient to the row being absent
(create-or-get) rather than silently doing nothing, given it returns success
either way.

Worth a look because anything that is not the first-party web UI — a future
mobile client, an integration, a support script replaying a submission — would
hit this and see a plausible-looking `200`.

## Correction to an earlier note

An earlier observation in this work described this as "10 XP awarded, zero
lesson completion, zero achievement unlock" and implied the completion path
might be broken. That was an artifact of the probe skipping `/start`; the
table above is the accurate version.

---

# Proposal: make `submit` correct on its own (not built — separate task)

Two options were considered: reject with `400 "lesson not started"`, or have
`submit` create the missing row the way `start` does.

**Recommendation: auto-create the row.** Reject-with-400 guards a condition that
does not mean what it appears to mean.

## Why 400 is the weaker option

A `LessonProgress` row is not a permission, and its absence is not evidence that
the user skipped anything. Two separate endpoints already create one as a side
effect, via the same helper:

- `lessons.py:158` `POST /lessons/{id}/start` — with status `in_progress`
- `lessons.py:153` `GET /lessons/{id}/progress` — with status `ready`

So merely *reading* a lesson's progress is enough to satisfy the check. A 400
would therefore reject a caller who submitted without ever looking at progress,
while happily accepting one who did nothing more than `GET` it. That is not a
meaningful distinction to enforce, and it would turn a currently-working (if
incomplete) call into a hard failure for no safety gain.

Worth stating plainly: `start` is **not** a gate. It runs no prerequisite or
lock check — it creates the row and advances status. Auto-creating in `submit`
therefore bypasses no authorization whatsoever, which is the usual reason to
prefer rejecting over repairing.

## What auto-create would involve

`lessons.py:34` already has the exact primitive, and its docstring shows the
race has been thought about:

```python
async def _get_or_create_lesson_progress(db, user_id, lesson_id, initial_status)
```

It uses `INSERT ... ON CONFLICT DO NOTHING` against `uq_user_lesson`, so two
concurrent submissions cannot produce the 500 that a naive select-then-insert
would. `submit` would call it with `MissionStatusEnum.in_progress` in place of
the current `scalar_one_or_none()`, and the existing `if lesson_progress:`
guard at `exercises.py:203` disappears — the row is always there.

The helper is private to `lessons.py`; it would move somewhere shared
(`app/services/`) rather than be imported across API modules.

Cost: roughly a handful of lines, one moved function, and a test that submitting
without `/start` completes the lesson and awards the lesson XP.

## Adjacent, deliberately out of scope

`submit` performs **no** lock or prerequisite check today, in either ordering —
confirmed by reading the handler. Auto-create neither introduces nor worsens
that, but if lessons are meant to be gated, that gate is missing from this
endpoint regardless of which option above is chosen. That is its own question.
