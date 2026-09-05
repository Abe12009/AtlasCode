"""Add Micro-Quest blocks to lessons 12 and 36 (the second and third reference quests).

WHY THESE TWO
-------------
Phase 8 proved the Micro-Quest on one lesson whose exercise is code_writing.
Phase 9 has to prove the same architecture over *different* exercise types and
*different* blueprint interactions, so the two additions are:

  lesson 36  "What Is an Algorithm?"      exercise 47, multiple_choice, 10 XP
             blueprint kind: order_steps

  lesson 12  "Scope and Function Design"  exercise 22, prediction, 10 XP
             blueprint kind: match_pairs   <- the new interaction

Both were picked from the existing curriculum, not invented: each already has
exactly one exercise, so solving it completes the lesson and the Quest Clear
screen reflects real, backend-awarded XP; and each already grades cleanly
through the existing grader (option / expected_output). No exercise, option,
translation or lesson row is created, edited or deleted by this migration.

WHAT THIS DOES
--------------
INSERT three lesson_blocks per lesson -- hook, blueprint, exam_tip -- plus
their en/fr/ar rows in lesson_block_translations. Nothing else.

There is NO schema change: lesson_blocks.config already exists (it was added by
add_microquest_lesson9.py) and the stage a student has reached is remembered in
the browser's localStorage, not in the database.

Both lessons currently hold blocks at orders 1, 2 and 3, so the hook takes the
free order 0 and the blueprint and exam tip take 4 and 5. No existing row is
renumbered and every existing id is preserved.

Usage:
    python migrations/add_microquest_lessons_12_36.py --check
    python migrations/add_microquest_lessons_12_36.py --apply
    python migrations/add_microquest_lessons_12_36.py --rollback
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

from app.seed.microquest_content import MICROQUEST_BY_SLUG  # noqa: E402

#: lesson slug -> the exercise the quest ends in, purely so --check can show
#: that the target really is the lesson we think it is.
EXPECTED = {
    "what-is-algorithm": ("multiple_choice", 47),
    "scope-and-function-design": ("prediction", 22),
}

BLOCK_TYPES = ("hook", "blueprint", "exam_tip")


def lesson_id_for(conn, slug: str) -> int:
    row = conn.execute("select id from lessons where slug = ?", (slug,)).fetchone()
    if row is None:
        raise SystemExit(f"lesson with slug {slug!r} not found; refusing to guess")
    return row["id"]


def microquest_blocks(conn, lesson_id: int):
    return list(
        conn.execute(
            "select id, block_type, `order` from lesson_blocks "
            "where lesson_id = ? and block_type in ('hook', 'blueprint', 'exam_tip') "
            "order by `order`",
            (lesson_id,),
        )
    )


def describe(conn, slug: str) -> int:
    lesson_id = lesson_id_for(conn, slug)
    print(f"\n--- {slug} (lesson {lesson_id}) ---")

    orders = sorted(
        r["order"]
        for r in conn.execute("select `order` from lesson_blocks where lesson_id = ?", (lesson_id,))
    )
    print(f"    existing block orders : {orders}")

    exercises = list(
        conn.execute(
            "select id, exercise_type, xp_reward from exercises where lesson_id = ? order by id",
            (lesson_id,),
        )
    )
    for row in exercises:
        print(f"    exercise id={row['id']} type={row['exercise_type']} xp={row['xp_reward']}")
    want_type, want_id = EXPECTED[slug]
    if len(exercises) != 1 or exercises[0]["id"] != want_id or exercises[0]["exercise_type"] != want_type:
        raise SystemExit(
            f"lesson {lesson_id} no longer looks like the chosen reference lesson "
            f"(expected exactly one {want_type} exercise, id {want_id}); refusing to touch it"
        )

    present = microquest_blocks(conn, lesson_id)
    print(f"    Micro-Quest blocks    : {len(present)}")
    for row in present:
        print(f"        id={row['id']} {row['block_type']} order={row['order']}")
    return lesson_id


def insert_blocks(conn, lesson_id: int, slug: str) -> int:
    already = {r["block_type"] for r in microquest_blocks(conn, lesson_id)}
    inserted = 0
    for block in MICROQUEST_BY_SLUG[slug]:
        if block["block_type"] in already:
            print(f"    {block['block_type']}: already present, skipped")
            continue
        cursor = conn.execute(
            "insert into lesson_blocks (lesson_id, block_type, `order`, content, code_example, config) "
            "values (?, ?, ?, ?, ?, ?)",
            (
                lesson_id,
                block["block_type"],
                block["order"],
                block["content"],
                None,
                json.dumps(block["config"], ensure_ascii=False),
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
        print(f"    inserted {block['block_type']} as block id={block_id} (order {block['order']})")
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    write = args.apply or args.rollback
    conn = sqlite3.connect(DB if write else f"file:{DB}?mode=ro", uri=not write)
    conn.row_factory = sqlite3.Row

    has_config = any(r[1] == "config" for r in conn.execute("PRAGMA table_info(lesson_blocks)"))
    print(f"Database: {DB}")
    print(f"lesson_blocks.config column present: {has_config}")
    if not has_config:
        raise SystemExit(
            "lesson_blocks.config is missing. Run migrations/add_microquest_lesson9.py --apply "
            "first; this migration adds no columns."
        )

    lesson_ids = {slug: describe(conn, slug) for slug in MICROQUEST_BY_SLUG}

    if args.rollback:
        removed_blocks = removed_translations = 0
        for slug, lesson_id in lesson_ids.items():
            ids = [r["id"] for r in microquest_blocks(conn, lesson_id)]
            if not ids:
                continue
            marks = ",".join("?" * len(ids))
            removed_translations += conn.execute(
                f"delete from lesson_block_translations where block_id in ({marks})", ids
            ).rowcount
            removed_blocks += conn.execute(
                f"delete from lesson_blocks where id in ({marks})", ids
            ).rowcount
        conn.commit()
        print(f"\nRemoved {removed_blocks} blocks and {removed_translations} translation rows.")
        return 0

    if not args.apply:
        todo = {
            slug: [
                b["block_type"]
                for b in MICROQUEST_BY_SLUG[slug]
                if b["block_type"] not in {r["block_type"] for r in microquest_blocks(conn, lesson_id)}
            ]
            for slug, lesson_id in lesson_ids.items()
        }
        print(f"\nWould insert: {todo}")
        print("Dry run. Re-run with --apply.")
        return 0

    total = 0
    for slug, lesson_id in lesson_ids.items():
        print(f"\napplying to {slug} (lesson {lesson_id}):")
        total += insert_blocks(conn, lesson_id, slug)
    conn.commit()

    print(f"\nInserted {total} Micro-Quest block(s).")
    print("Verification:")
    for slug, lesson_id in lesson_ids.items():
        for row in microquest_blocks(conn, lesson_id):
            langs = [
                r["language"]
                for r in conn.execute(
                    "select language from lesson_block_translations where block_id = ? order by language",
                    (row["id"],),
                )
            ]
            kind = None
            raw = conn.execute(
                "select config from lesson_blocks where id = ?", (row["id"],)
            ).fetchone()["config"]
            if raw:
                kind = json.loads(raw).get("kind")
            print(
                f"    lesson {lesson_id} id={row['id']} {row['block_type']} "
                f"order={row['order']} kind={kind} languages={langs}"
            )
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
