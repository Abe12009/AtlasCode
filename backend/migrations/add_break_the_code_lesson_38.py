"""Attach a Break-the-Code step-through trace to lesson 38's existing
debugging exercise (#49, the broken `binary_search`).

WHY THIS EXERCISE
------------------
Same reference lesson `add_microquest_lesson_38.py` already picked for the
Micro-Quest `spot_the_bug` blueprint, and for the same reason: of the three
lessons with a `debugging` exercise, #49 is the only one graded by the real
sandbox against real assertions on a genuinely broken algorithm (6 has two
exercises, which doesn't fit either feature's "exactly one" shape; 33 is a
fill-in-the-git-command exercise, not actually debugging code). Reusing it
here means the same buggy `binary_search` now has both a spot-the-bug warm-up
*and* a step-through trace, with no new content authored from scratch.

WHAT THIS DOES
--------------
UPDATEs exercises.validation_config for exercise id 49, setting it to
`{"trace": [...]}`, where the trace is recorded fresh from the exercise's own
`starter_code` (not retyped here) via app.services.trace_recorder.record_trace
-- so the trace is guaranteed to match the actual buggy code already in the
database, not a copy that could drift from it.

No schema change: exercises.validation_config already exists and is free-form
JSON (see app.services.exercise_grading.parse_validation_config). This
exercise's validation_config is currently empty (its grading comes from
test_code, not validation_config -- see resolve_strategy), so this is a pure
addition, not an overwrite of anything graded.

Usage:
    python migrations/add_break_the_code_lesson_38.py --check
    python migrations/add_break_the_code_lesson_38.py --apply
    python migrations/add_break_the_code_lesson_38.py --rollback
"""

import argparse
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.dirname(HERE)
sys.path.insert(0, BACKEND)

DB = os.path.join(BACKEND, "atlascode.db")
LESSON_SLUG = "searching-algorithms"
EXERCISE_ID = 49
#: A target that actually terminates (some inputs infinite-loop against this
#: exercise's specific bugs -- see app.services.trace_recorder's MAX_STEPS
#: safety net, which would otherwise fail this migration loudly).
ENTRY_CALL = "binary_search([1, 3, 5, 7, 9], 5)"

from app.services.trace_recorder import record_trace, trace_to_json  # noqa: E402


def describe(conn) -> sqlite3.Row:
    row = conn.execute(
        "select e.id, e.exercise_type, e.starter_code, e.validation_config, l.slug "
        "from exercises e join lessons l on l.id = e.lesson_id where e.id = ?",
        (EXERCISE_ID,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"exercise id {EXERCISE_ID} not found; refusing to guess")
    if row["slug"] != LESSON_SLUG or row["exercise_type"] != "debugging":
        raise SystemExit(
            f"exercise {EXERCISE_ID} no longer looks like the chosen reference exercise "
            f"(expected lesson {LESSON_SLUG!r}, type 'debugging'; got lesson {row['slug']!r}, "
            f"type {row['exercise_type']!r}); refusing to touch it"
        )
    print(f"\n--- exercise {EXERCISE_ID} ({LESSON_SLUG}) ---")
    print(f"    starter_code (first line): {row['starter_code'].splitlines()[0]!r}")
    existing = json.loads(row["validation_config"]) if row["validation_config"] else {}
    print(f"    validation_config keys: {list(existing.keys())}")
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    write = args.apply or args.rollback
    conn = sqlite3.connect(DB if write else f"file:{DB}?mode=ro", uri=not write)
    conn.row_factory = sqlite3.Row

    print(f"Database: {DB}")
    row = describe(conn)
    existing = json.loads(row["validation_config"]) if row["validation_config"] else {}

    if args.rollback:
        if "trace" not in existing:
            print("\nNo trace present. Nothing to roll back.")
            return 0
        remaining = {k: v for k, v in existing.items() if k != "trace"}
        conn.execute(
            "update exercises set validation_config = ? where id = ?",
            (json.dumps(remaining, ensure_ascii=False) if remaining else "", EXERCISE_ID),
        )
        conn.commit()
        print(f"\nRemoved trace from exercise {EXERCISE_ID}'s validation_config.")
        return 0

    if "trace" in existing:
        print(f"\nExercise {EXERCISE_ID} already has a trace. Nothing to do.")
        return 0

    result = record_trace(row["starter_code"], ENTRY_CALL)
    if not result.is_valid:
        raise SystemExit(f"trace recording failed for entry_call {ENTRY_CALL!r}: {result.error}")
    print(f"\nRecorded trace: {len(result.steps)} step(s) for entry_call {ENTRY_CALL!r}")

    if not args.apply:
        print("Dry run. Re-run with --apply.")
        return 0

    updated = {**existing, "trace": trace_to_json(result)}
    conn.execute(
        "update exercises set validation_config = ? where id = ?",
        (json.dumps(updated, ensure_ascii=False), EXERCISE_ID),
    )
    conn.commit()

    verify = conn.execute(
        "select validation_config from exercises where id = ?", (EXERCISE_ID,)
    ).fetchone()
    saved = json.loads(verify["validation_config"])
    print(f"\nSaved. validation_config now has {len(saved['trace'])} trace step(s).")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
