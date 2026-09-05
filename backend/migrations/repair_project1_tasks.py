"""Repair project 1 (CLI Calculator) tasks 2-4 to match app/seed/projects.py.

WHY
---
The live database holds an older generation of tasks 2-4:

  * starter_code is an interactive ``calculator()`` built on ``input()``, which
    the code sandbox forbids outright, so a student's answer can never run;
  * validation_code is a bare ``print("...")``, so *any* submission passes.

app/seed/projects.py has since defined these as testable pure functions
(``calculate``, ``process_operations``, ``safe_calculate``) with real
assertions. Task 1 already matches the seed and is left alone.

SAFETY
------
This rewrites only ``project_tasks.starter_code`` and ``validation_code`` for
project 1, orders 2-4. It touches no user row. The script refuses to run if any
user has real progress on project 1, and writes a reversible SQL backup of the
rows it is about to change before changing them.

Usage:
    python migrations/repair_project1_tasks.py --check     # report only
    python migrations/repair_project1_tasks.py --apply     # back up, then apply
    python migrations/repair_project1_tasks.py --restore <backup.sql>
"""

import argparse
import ast
import datetime
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.dirname(HERE)
DB = os.path.join(BACKEND, "atlascode.db")
SEED = os.path.join(BACKEND, "app", "seed", "projects.py")
TARGET_ORDERS = (2, 3, 4)


def seed_tasks() -> dict[int, dict[str, str]]:
    """Extract project1's ProjectTask starter/validation code from the seed."""
    tree = ast.parse(open(SEED, encoding="utf-8").read())
    found: dict[int, dict[str, str]] = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "ProjectTask"):
            continue
        kw = {k.arg: k.value for k in node.keywords}
        project = kw.get("project_id")
        if not (isinstance(project, ast.Attribute) and getattr(project.value, "id", "") == "project1"):
            continue
        order = ast.literal_eval(kw["order"])
        found[order] = {
            "starter_code": ast.literal_eval(kw["starter_code"]),
            "validation_code": ast.literal_eval(kw["validation_code"]),
        }
    return found


def progress_at_risk(conn) -> list[tuple]:
    """Any project-1 progress row that a rewrite could invalidate."""
    return list(
        conn.execute(
            """select id, user_id, status, current_task, xp_earned
               from project_progress
               where project_id = 1
                 and (status <> 'locked'
                      or current_task > 0
                      or xp_earned > 0
                      or (code_snapshot is not null and trim(code_snapshot) <> '')
                      or completed_at is not null)"""
        )
    )


def sql_literal(value) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def write_backup(conn, rows) -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(HERE, f"backup-project1-tasks-{stamp}.sql")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("-- Reversible backup of project_tasks rows before repair.\n")
        fh.write("-- Apply with: python migrations/repair_project1_tasks.py --restore <this file>\n")
        for row in rows:
            fh.write(
                "UPDATE project_tasks SET starter_code = {starter}, validation_code = {validation} "
                "WHERE id = {tid};\n".format(
                    starter=sql_literal(row["starter_code"]),
                    validation=sql_literal(row["validation_code"]),
                    tid=row["id"],
                )
            )
    return path


def report(conn, seed) -> list:
    rows = list(
        conn.execute(
            'select id, "order", starter_code, validation_code from project_tasks '
            "where project_id = 1 order by \"order\""
        )
    )
    differing = []
    for row in rows:
        want = seed.get(row["order"])
        if not want:
            print(f"  task id={row['id']} order={row['order']}: no seed counterpart, skipped")
            continue
        same_starter = (row["starter_code"] or "") == want["starter_code"]
        same_validation = (row["validation_code"] or "") == want["validation_code"]
        status = "matches seed" if (same_starter and same_validation) else "DIFFERS"
        print(
            f"  task id={row['id']} order={row['order']}: {status} "
            f"(starter_matches={same_starter}, validation_matches={same_validation})"
        )
        if row["order"] in TARGET_ORDERS and not (same_starter and same_validation):
            differing.append(row)
    return differing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the repair")
    parser.add_argument("--check", action="store_true", help="report only (default)")
    parser.add_argument("--restore", metavar="BACKUP_SQL", help="undo using a backup file")
    args = parser.parse_args()

    if args.restore:
        statements = open(args.restore, encoding="utf-8").read()
        conn = sqlite3.connect(DB)
        conn.executescript(statements)
        conn.commit()
        conn.close()
        print(f"Restored from {args.restore}")
        return 0

    seed = seed_tasks()
    conn = sqlite3.connect(DB if args.apply else f"file:{DB}?mode=ro", uri=not args.apply)
    conn.row_factory = sqlite3.Row

    print("Project 1 task comparison against app/seed/projects.py:")
    differing = report(conn, seed)

    risky = progress_at_risk(conn)
    total = conn.execute("select count(*) from project_progress where project_id=1").fetchone()[0]
    print(f"\nproject_progress rows for project 1: {total}")
    print(f"rows with real progress (would be at risk): {len(risky)}")
    for row in risky[:10]:
        print(f"    progress id={row['id']} user={row['user_id']} status={row['status']} "
              f"task={row['current_task']} xp={row['xp_earned']}")

    if not differing:
        print("\nNothing to repair.")
        return 0

    if not args.apply:
        print(f"\n{len(differing)} task(s) would be repaired. Re-run with --apply.")
        return 0

    if risky:
        print("\nREFUSING TO APPLY: users have real progress on project 1.")
        print("Repairing would invalidate work already submitted against the old tasks.")
        return 1

    backup = write_backup(conn, differing)
    print(f"\nBackup written to {backup}")

    for row in differing:
        want = seed[row["order"]]
        conn.execute(
            "update project_tasks set starter_code = ?, validation_code = ? where id = ?",
            (want["starter_code"], want["validation_code"], row["id"]),
        )
        print(f"  repaired task id={row['id']} order={row['order']}")
    conn.commit()

    print("\nVerification after repair:")
    report(conn, seed)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
