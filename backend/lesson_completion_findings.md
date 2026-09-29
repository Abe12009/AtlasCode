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
