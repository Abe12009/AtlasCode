"""Add the Micro-Quest blocks for the reference lesson (lesson 9).

WHY
---
Lesson 9, "Problem Solving with Control Flow", becomes the first Micro-Quest.
It was chosen because it has exactly one exercise (#18, code_writing, 15 XP,
graded by the real sandbox), so quest completion coincides with genuine lesson
completion and real XP; and because its subject is a *pattern* -- initialise,
loop, compare, update -- which an interactive blueprint can teach without any
syntax.

WHAT THIS DOES
--------------
1. ALTER TABLE lesson_blocks ADD COLUMN config TEXT   (additive, nullable)
2. INSERT three new blocks for lesson 9 -- hook, blueprint, exam_tip -- plus
   their en/fr/ar translation rows.

Nothing existing is updated or deleted. The hook takes order 0, which is free,
so the lesson's current blocks (orders 1-3) keep their order and their ids.
Every other lesson is untouched and keeps rendering exactly as before.

Usage:
    python migrations/add_microquest_lesson9.py --check
    python migrations/add_microquest_lesson9.py --apply
    python migrations/add_microquest_lesson9.py --rollback
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
LESSON_ID = 9

from app.seed.microquest_lesson9 import MICROQUEST_BLOCKS  # noqa: E402


def column_exists(conn, table: str, column: str) -> bool:
    return any(row[1] == column for row in conn.execute(f"PRAGMA table_info({table})"))


def existing_microquest_blocks(conn):
    return list(
        conn.execute(
            "select id, block_type, `order` from lesson_blocks "
            "where lesson_id = ? and block_type in ('hook', 'blueprint', 'exam_tip') "
            "order by `order`",
            (LESSON_ID,),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    write = args.apply or args.rollback
    conn = sqlite3.connect(DB if write else f"file:{DB}?mode=ro", uri=not write)
    conn.row_factory = sqlite3.Row

    has_config = column_exists(conn, "lesson_blocks", "config")
    present = existing_microquest_blocks(conn)

    print(f"lesson_blocks.config column present : {has_config}")
    print(f"Micro-Quest blocks on lesson {LESSON_ID}      : {len(present)}")
    for row in present:
        print(f"    id={row['id']} {row['block_type']} order={row['order']}")

    existing_orders = [
        r["order"] for r in conn.execute(
            "select `order` from lesson_blocks where lesson_id = ?", (LESSON_ID,)
        )
    ]
    print(f"existing block orders on lesson {LESSON_ID}   : {sorted(existing_orders)}")

    if args.rollback:
        ids = [r["id"] for r in present]
        if not ids:
            print("\nNothing to roll back.")
            return 0
        marks = ",".join("?" * len(ids))
        n_tr = conn.execute(
            f"delete from lesson_block_translations where block_id in ({marks})", ids
        ).rowcount
        n_bl = conn.execute(f"delete from lesson_blocks where id in ({marks})", ids).rowcount
        conn.commit()
        print(f"\nRemoved {n_bl} blocks and {n_tr} translation rows.")
        return 0

    if not args.apply:
        todo = [b for b in MICROQUEST_BLOCKS
                if b["block_type"] not in {r["block_type"] for r in present}]
        print(f"\nWould add column: {not has_config}")
        print(f"Would insert {len(todo)} block(s): {[b['block_type'] for b in todo]}")
        print("Dry run. Re-run with --apply.")
        return 0

    if not has_config:
        conn.execute("ALTER TABLE lesson_blocks ADD COLUMN config TEXT")
        print("\nAdded column lesson_blocks.config")

    already = {r["block_type"] for r in present}
    inserted = 0
    for block in MICROQUEST_BLOCKS:
        if block["block_type"] in already:
            print(f"  {block['block_type']}: already present, skipped")
            continue
        cursor = conn.execute(
            "insert into lesson_blocks (lesson_id, block_type, `order`, content, code_example, config) "
            "values (?, ?, ?, ?, ?, ?)",
            (
                LESSON_ID,
                block["block_type"],
                block["order"],
                block["content"],
                None,
                json.dumps(block["config"], ensure_ascii=False) if block.get("config") else None,
            ),
        )
        block_id = cursor.lastrowid
        for language, text in block["translations"].items():
            conn.execute(
                "insert into lesson_block_translations (block_id, language, content, code_example) "
                "values (?, ?, ?, ?)",
                (block_id, language, text, None),
            )
        inserted += 1
        print(f"  inserted {block['block_type']} as block id={block_id} (order {block['order']})")
    conn.commit()

    print(f"\nInserted {inserted} Micro-Quest block(s).")
    print("Verification:")
    for row in existing_microquest_blocks(conn):
        langs = [
            r["language"] for r in conn.execute(
                "select language from lesson_block_translations where block_id = ? order by language",
                (row["id"],),
            )
        ]
        print(f"    id={row['id']} {row['block_type']} order={row['order']} languages={langs}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
