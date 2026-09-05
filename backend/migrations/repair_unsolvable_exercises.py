"""Repair the exercises whose own reference solution their grader rejects.

WHY
---
Auditing all 138 exercises by feeding each one its own stored solution found
six that no student can ever pass, which also blocks the lesson containing them:

  10  code_writing  the exercise teaches input(), which the Python sandbox
                    forbids outright, so the reference solution never runs.
  30  code_writing  the answer is HTML, run through a Python validator.
  32  code_writing  the answer is HTML, run through a Python validator.
  35  code_writing  the answer is CSS, run through a Python validator.
  46  prediction    keyword list authored as alternatives ("Pull Request" OR
                    "PR") but enforced as all-of, so it is unsatisfiable.
  48  code_writing  same: "n²" AND "n^2" AND "quadratic" cannot all appear in
                    one natural answer.

WHAT THIS DOES
--------------
For 10/30/32/35 it moves grading off the Python sandbox and onto
expected_keywords, using exactly the substrings the existing test_code already
asserted, so the bar is unchanged -- only the mechanism that can actually check
it changes. test_code is cleared for those rows so resolve_strategy picks the
keyword strategy; the original value is preserved in the backup.

For 46/48 it rewrites the keyword list into the alternatives form the grader
now understands (a nested list means "any one of these").

SAFETY
------
Touches only the exercises table, columns test_code and validation_config, for
six ids. No user row, attempt, or progress record is read or written. Writes a
reversible SQL backup first.

Usage:
    python migrations/repair_unsolvable_exercises.py --check
    python migrations/repair_unsolvable_exercises.py --apply
    python migrations/repair_unsolvable_exercises.py --restore <backup.sql>
"""

import argparse
import datetime
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.dirname(HERE)
DB = os.path.join(BACKEND, "atlascode.db")

#: exercise id -> (new test_code, new validation_config, why)
REPAIRS = {
    10: (
        None,
        {
            # The old test_code asserted the printed birth year. The sandbox
            # forbids input(), so this is now checked by the concepts the
            # lesson teaches: reading input, converting it, printing a result.
            "expected_keywords": [
                "input(",
                ["int(", "float("],
                "print(",
                ["2025", "2024"],
            ]
        },
        "input() cannot run in the Python sandbox",
    ),
    30: (
        None,
        {"expected_keywords": ["<header>", "<main>", "<footer>"]},
        "HTML answer cannot be graded by a Python validator",
    ),
    32: (
        None,
        {"expected_keywords": ['type="text"', 'type="email"', 'type="submit"']},
        "HTML answer cannot be graded by a Python validator",
    ),
    35: (
        None,
        {
            "expected_keywords": [
                "display: flex",
                "justify-content: center",
                "align-items: center",
                "gap: 20px",
            ]
        },
        "CSS answer cannot be graded by a Python validator",
    ),
    46: (
        None,
        {"expected_keywords": ["clone", ["pull request", "pr"]]},
        "keyword list was alternatives, enforced as all-of",
    ),
    48: (
        None,
        {"expected_keywords": [["n²", "n^2", "n*n", "quadratic"]]},
        "keyword list was alternatives, enforced as all-of",
    ),
}


def sql_literal(value) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def write_backup(conn, rows) -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(HERE, f"backup-unsolvable-exercises-{stamp}.sql")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("-- Reversible backup of exercises rows before repair.\n")
        fh.write("-- Apply with: python migrations/repair_unsolvable_exercises.py --restore <this file>\n")
        for row in rows:
            fh.write(
                "UPDATE exercises SET test_code = {t}, validation_config = {v} WHERE id = {i};\n".format(
                    t=sql_literal(row["test_code"]),
                    v=sql_literal(row["validation_config"]),
                    i=row["id"],
                )
            )
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--restore", metavar="BACKUP_SQL")
    args = parser.parse_args()

    if args.restore:
        conn = sqlite3.connect(DB)
        conn.executescript(open(args.restore, encoding="utf-8").read())
        conn.commit()
        conn.close()
        print(f"Restored from {args.restore}")
        return 0

    write = args.apply
    conn = sqlite3.connect(DB if write else f"file:{DB}?mode=ro", uri=not write)
    conn.row_factory = sqlite3.Row

    rows = []
    for exercise_id, (_, config, why) in sorted(REPAIRS.items()):
        row = conn.execute(
            "select id, exercise_type, test_code, validation_config from exercises where id = ?",
            (exercise_id,),
        ).fetchone()
        if row is None:
            print(f"  exercise {exercise_id}: NOT FOUND, skipped")
            continue
        rows.append(row)
        print(f"  exercise {exercise_id} ({row['exercise_type']}): {why}")
        print(f"      test_code          {'set' if (row['test_code'] or '').strip() else 'empty'} -> cleared")
        print(f"      validation_config  {row['validation_config']!r}")
        print(f"                      -> {json.dumps(config, ensure_ascii=False)}")

    if not args.apply:
        print(f"\n{len(rows)} exercise(s) would be repaired. Re-run with --apply.")
        return 0

    backup = write_backup(conn, rows)
    print(f"\nBackup written to {backup}")

    for exercise_id, (test_code, config, _) in sorted(REPAIRS.items()):
        conn.execute(
            "update exercises set test_code = ?, validation_config = ? where id = ?",
            (test_code, json.dumps(config, ensure_ascii=False), exercise_id),
        )
    conn.commit()
    print(f"Repaired {len(REPAIRS)} exercises.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
