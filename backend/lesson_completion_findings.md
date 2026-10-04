# Backend findings: lesson completion and exercise submission

Two independent findings from 2026-09-29, turned up while verifying the
achievement share cards. They are separate concerns with separate fates — #2 is
not answered by shipping #1.

| # | Finding | Status |
|---|---|---|
| 1 | `submit` silently skips lesson completion when no progress row exists | **Fixed 2026-10-03** |
| 2 | Lesson access is advisory where project access is enforced | **Resolved as "no change"** — the premise was understated; see below |

---

## 1. `submit` does not complete a lesson unless a progress row already exists

### What was seen

Submitting the correct answer to lesson 31's *only* exercise, straight through
the API, awarded the exercise XP but left the lesson untouched:

| | XP total | `lesson_progress.status` | `completed_at` | achievements |
|---|---|---|---|---|
| `POST /exercises/42/submit` alone | 10 | `ready` | `null` | none |
| `POST /lessons/31/start` **then** submit | **60** | **`completed`** | set | `first-lesson` |

Both runs used a brand-new account, and `submit` returned `200` with
`is_correct: true` and `xp_earned: 10` either way. The difference is entirely in
what happens *around* the award.

60 = 10 (exercise 42) + 50 (lesson 31's own `xp_reward`), which is exactly what
the seed predicts.

### Why

`app/api/exercises.py:203` guarded the whole completion block (pre-fix):

```python
lesson_progress = lesson_progress_result.scalar_one_or_none()
if lesson_progress:
    ...
    if correct_count >= total_exercises and total_exercises > 0:
        lesson_progress.status = MissionStatusEnum.completed
        profile.completed_lessons += 1
        # lesson_completed notification, course progress, achievements
```

With no row, `if lesson_progress:` is false and the entire branch is skipped
silently — no completed status, no `completed_lessons` increment, no
`lesson_completed` notification, no course progress roll-up, no achievement, and
no lesson XP. The request still returns `200`, so nothing signals that half the
work did not happen.

Not reachable through the web UI, which always opens a lesson first. It would be
reachable by anything that is not the first-party client — a future mobile app,
an integration, a support script replaying a submission — and each would see a
plausible-looking `200`.

### Fixed (2026-10-03)

`_get_or_create_lesson_progress` moved from `app/api/lessons.py` to
`app/services/lesson_progress.py` as `get_or_create_lesson_progress`, and
`submit` now calls it with `MissionStatusEnum.in_progress` where it used to do
`scalar_one_or_none()`. The `if lesson_progress:` guard is gone, so the
completion block always runs.

One thing the original plan missed: the helper committed, and `submit` is
deliberately a single transaction (`record_activity` and `create_notification`
both leave committing to the caller, and there is exactly one `db.commit()` at
the end). Calling it as-is would have split the handler in two, so that a
failure between the halves left the exercise XP awarded but the lesson not
completed — and a retry would then see `previous_success` and skip completion
for good, which is a worse version of the bug being fixed. The helper therefore
takes `commit=False`; `/start` and `/progress`, which have nothing pending,
keep the committing default.

Also guarded `profile.completed_lessons += 1`, whose siblings were already
guarded (`if profile:` for xp, `if cp:` for course progress). It was
unreachable without a progress row before; auto-create reaches it for a
profile-less user.

Tests in `tests/test_lessons.py`: completion without `/start` creates the row
and completes the lesson, the existing `/start`-first path is unchanged, and a
resubmission does not double-count. The first was confirmed to fail against
pre-fix code with `submit should have created the progress row`.

**Correction to the table above.** The `60` is `10` (exercise) + `50` from the
*first-lesson achievement*, not "lesson 31's own `xp_reward`" as originally
written. `Lesson.xp_reward` is never credited to `profile.xp` anywhere in the
backend — `achievements.py:133` is the only place that adds a reward to a
profile. Whether lesson `xp_reward` is meant to be awarded at all is a separate
open question, untouched here.

### Decision: auto-create the row (as approved)

Rejecting with `400 "lesson not started"` was the alternative. It was rejected
because **a `LessonProgress` row is not a permission**. Two endpoints already
create one as a side effect, through the same helper:

- `lessons.py:128` `POST /lessons/{id}/start` — status `in_progress`
- `lessons.py:117` `GET /lessons/{id}/progress` — status `ready`

So merely *reading* progress satisfies the check. A 400 would reject a caller
who submitted without ever reading progress while admitting one who did nothing
but `GET` it — a guard in appearance only.

The usual reason to prefer rejecting over repairing is that repairing might
bypass an authorization check. It does not here; see finding #2 for why, and
note that #2 remains true either way.

**Shape of the work.** The primitive already existed (then at `lessons.py:34`,
now `services/lesson_progress.py:8`), and its
docstring shows the race was thought through:

```python
async def _get_or_create_lesson_progress(db, user_id, lesson_id, initial_status)
```

It uses `INSERT ... ON CONFLICT DO NOTHING` against `uq_user_lesson`, so two
concurrent submissions cannot produce the 500 a naive select-then-insert would.
`submit` calls it with `MissionStatusEnum.in_progress` in place of the current
`scalar_one_or_none()`, and the `if lesson_progress:` guard disappears — the row
is always there.

The helper is private to `lessons.py` and **moves to `app/services/`** rather
than being imported across API modules.

Cost: a handful of lines, one moved function, and a test that submitting without
`/start` completes the lesson and awards the lesson XP.

---

## 2. Lesson access is advisory; project access is enforced

**Its own finding, and shipping #1 does not answer it.** Recorded separately so
it is not assumed handled once auto-create lands.

`submit` performs no lock or prerequisite check — but that turns out to be
consistent with the rest of the lesson API rather than an isolated omission.
`MissionStatusEnum.locked` on a lesson is a display hint, not a gate:

- `lessons.py:95` — `GET /lessons/{id}` **clears** a locked status: `if progress
  and progress.status == MissionStatusEnum.locked: progress.status = ready`.
  Fetching a lesson unlocks it.
- `lessons.py:139` — `POST /lessons/{id}/start` promotes `locked` straight to
  `in_progress`.
- `exercises.py` — submission checks neither lock nor prerequisite.

Projects are the opposite, and enforce properly:

- `projects.py:138` — `403 "Project is locked. Complete prerequisite
  lessons/projects first."`
- `projects.py:173` — `403 "Project is locked"` on task submission.

So a client can reach and complete any lesson in any order, while the equivalent
move on a project is refused. That may well be deliberate — lessons browsable,
projects gated — but the two subsystems currently disagree, and the lesson-side
`locked` state advertises an enforcement that does not exist.

### Resolved 2026-10-03: no change, and the premise was understated

Re-checked before adding a lock check to `submit`. Lesson locking is not merely
advisory — it is **unreachable**, so a check would have been dead code:

- `Lesson` has **no prerequisite column**. `Project` has
  `prerequisite_lesson_id` and `prerequisite_project_id`; a lesson has only
  `order`. `_check_project_unlocked` reads columns that do not exist on a
  lesson, so there was no existing gating logic to reuse.
- There is exactly **one** `LessonProgress` creation site
  (`services/lesson_progress.py`), and every caller passes an explicit status —
  `ready` from `/progress`, `in_progress` from `/start` and now from `submit`.
  So no *API* path exercises the model's `default=locked`. (A direct ORM
  insert does — `test_account_deletion.py` was building one that way — but
  that is test setup, not a reachable application state.) Nothing in the seed
  or any migration writes a progress row.
- The read path defaults the other way: `courses.py` maps status with
  `.get(db_status, "available")`, so a lesson with no row renders *available*.
- Live dev DB: `lesson_progress` is 31 completed / 384 in_progress / 1 ready —
  **0 locked of 416**. `project_progress` has 76 locked rows, so projects
  really do lock.
- The client cannot produce it either: `Dashboard.tsx` initialises
  `let status = 'locked'` and then overwrites it in every branch, ending in a
  catch-all `else status = 'available'`.

So the two subsystems do not actually disagree about enforcement — only the
lesson `locked` *vocabulary* implies a gate that no code can enter.
`tests/test_lessons.py::TestLessonLockIsNotEnforced` pins that premise: if
lesson gating is ever built, it fails and points here.

**Still a product call, deliberately not taken:** gate lessons like projects
(needs a `prerequisite_lesson_id` column, a migration, seed values, and it
stops lessons being browsable in any order), or retire the lesson `locked`
state so it stops advertising enforcement that was never there. Not bundled
with #1, and not guessed.

---

## Correction to an earlier note

An earlier observation during this work described finding #1 as "10 XP awarded,
zero lesson completion, zero achievement unlock" and implied the completion path
was broken. That was an artifact of the probe skipping `/start`; the table in #1
is the accurate version.
