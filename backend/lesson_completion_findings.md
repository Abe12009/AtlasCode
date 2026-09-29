# Backend findings: lesson completion and exercise submission

Two independent findings from 2026-09-29, turned up while verifying the
achievement share cards. **Neither is built.** They are separate concerns with
separate fates — #2 is not answered by shipping #1.

| # | Finding | Status |
|---|---|---|
| 1 | `submit` silently skips lesson completion when no progress row exists | Decision approved, not built |
| 2 | Lesson access is advisory where project access is enforced | Open, undecided |

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

With no row, `if lesson_progress:` is false and the entire branch is skipped
silently — no completed status, no `completed_lessons` increment, no
`lesson_completed` notification, no course progress roll-up, no achievement, and
no lesson XP. The request still returns `200`, so nothing signals that half the
work did not happen.

Not reachable through the web UI, which always opens a lesson first. It would be
reachable by anything that is not the first-party client — a future mobile app,
an integration, a support script replaying a submission — and each would see a
plausible-looking `200`.

### Decision: auto-create the row (approved, not yet built)

Rejecting with `400 "lesson not started"` was the alternative. It was rejected
because **a `LessonProgress` row is not a permission**. Two endpoints already
create one as a side effect, through the same helper:

- `lessons.py:158` `POST /lessons/{id}/start` — status `in_progress`
- `lessons.py:153` `GET /lessons/{id}/progress` — status `ready`

So merely *reading* progress satisfies the check. A 400 would reject a caller
who submitted without ever reading progress while admitting one who did nothing
but `GET` it — a guard in appearance only.

The usual reason to prefer rejecting over repairing is that repairing might
bypass an authorization check. It does not here; see finding #2 for why, and
note that #2 remains true either way.

**Shape of the work.** `lessons.py:34` already has the primitive, and its
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

- `lessons.py:126` — `GET /lessons/{id}` **clears** a locked status: `if progress
  and progress.status == MissionStatusEnum.locked: progress.status = ready`.
  Fetching a lesson unlocks it.
- `lessons.py:170` — `POST /lessons/{id}/start` promotes `locked` straight to
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

**Open question:** should lessons be gated like projects, or should lesson
`locked` be renamed/retired so it stops implying a guarantee it does not make?
Deciding this is a product call, not a bug fix, which is why it is not bundled
with #1.

---

## Correction to an earlier note

An earlier observation during this work described finding #1 as "10 XP awarded,
zero lesson completion, zero achievement unlock" and implied the completion path
was broken. That was an artifact of the probe skipping `/start`; the table in #1
is the accurate version.
