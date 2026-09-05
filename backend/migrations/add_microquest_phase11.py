"""Add Micro-Quest blocks to the 10 lessons Phase 11 selects.

WHY THESE 10
------------
See ``app/seed/microquest_content_phase11.py``'s module docstring for the
full selection reasoning (why exactly these 10, and why all 10 come from the
5 courses ``seed_all()`` builds rather than the other 10 courses that only
exist in the live database). In short:

  16  Dictionaries                        code_writing     match_pairs
  13  Decomposition and Problem Solving   code_writing     order_steps
  15  Tuples and Sets                     fill_blank       spot_the_bug
  18  How the Web Works                   multiple_choice  order_steps
  23  Selectors and Properties            multiple_choice  match_pairs
  26  Databases and Tables                multiple_choice  match_pairs
  29  Sorting, Grouping and Aggregation   code_writing     spot_the_bug
  45  Memory and Storage                  multiple_choice  order_steps
  47  Networks and the Internet           multiple_choice  spot_the_bug
  32  Commits and History                 ordering         match_pairs

Every one of these was verified, before being selected, to: have exactly one
exercise (so solving it completes the lesson, matching the Quest flow's
`exercises[0]` assumption), carry existing reading blocks only at orders
1-3 (leaving 0/4/5 free), carry no existing Micro-Quest blocks, and not be
any project's prerequisite lesson.

WHAT THIS DOES
--------------
INSERT three lesson_blocks per lesson -- hook, blueprint, exam_tip -- plus
their en/fr/ar rows in lesson_block_translations: 30 blocks and 90
translation rows in total. Nothing else. No exercise, option, translation,
project or lesson row is created, edited or deleted.

There is NO schema change -- lesson_blocks.config already exists, and all
three blueprint kinds used here (order_steps, match_pairs, spot_the_bug)
already exist from Phases 9-10.

Usage:
    python migrations/add_microquest_phase11.py --check
    python migrations/add_microquest_phase11.py --apply
    python migrations/add_microquest_phase11.py --rollback
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

from app.seed.microquest_content_phase11 import MICROQUEST_BY_SLUG_PHASE11  # noqa: E402

#: slug -> (exercise_type, exercise_id) each lesson is expected to still have.
EXPECTED = {
    "dictionaries": ("code_writing", 27),
    "decomposition-problem-solving": ("code_writing", 23),
    "tuples-and-sets": ("fill_blank", 26),
    "how-web-works": ("multiple_choice", 29),
    "selectors-properties": ("multiple_choice", 34),
    "databases-and-tables": ("multiple_choice", 37),
    "sorting-grouping-aggregation": ("code_writing", 40),
    "memory-and-storage": ("multiple_choice", 56),
    "networks-internet": ("multiple_choice", 58),
    "commits-and-history": ("ordering", 43),
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
            f"lesson {lesson_id} ({slug}) no longer looks like the chosen reference lesson "
            f"(expected exactly one {want_type} exercise, id {want_id}); refusing to touch it"
        )

    present = microquest_blocks(conn, lesson_id)
    print(f"    Micro-Quest blocks    : {len(present)}")
    for row in present:
        print(f"        id={row['id']} {row['block_type']} order={row['order']}")
    if present:
        raise SystemExit(
            f"lesson {lesson_id} ({slug}) already has Micro-Quest blocks; "
            "refusing to insert duplicates. Use --rollback first if you meant to redo this."
        )
    return lesson_id


def insert_blocks(conn, lesson_id: int, slug: str) -> int:
    inserted = 0
    for block in MICROQUEST_BY_SLUG_PHASE11[slug]:
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

    integrity = conn.execute("pragma integrity_check").fetchone()[0]
    print(f"pragma integrity_check (before): {integrity}")
    if integrity != "ok" and not args.rollback:
        raise SystemExit(f"database integrity check failed before migration: {integrity!r}")

    if args.rollback:
        total_blocks = total_translations = 0
        for slug in MICROQUEST_BY_SLUG_PHASE11:
            lesson_id = lesson_id_for(conn, slug)
            ids = [r["id"] for r in microquest_blocks(conn, lesson_id)]
            if not ids:
                print(f"{slug}: nothing to roll back")
                continue
            marks = ",".join("?" * len(ids))
            n_tr = conn.execute(
                f"delete from lesson_block_translations where block_id in ({marks})", ids
            ).rowcount
            n_bl = conn.execute(f"delete from lesson_blocks where id in ({marks})", ids).rowcount
            total_blocks += n_bl
            total_translations += n_tr
            print(f"{slug}: removed {n_bl} blocks, {n_tr} translation rows")
        conn.commit()
        print(f"\nTotal removed: {total_blocks} blocks, {total_translations} translation rows.")
        return 0

    lesson_ids = {slug: describe(conn, slug) for slug in MICROQUEST_BY_SLUG_PHASE11}

    if not args.apply:
        print(f"\nWould insert 3 blocks x {len(lesson_ids)} lessons = {3 * len(lesson_ids)} blocks total")
        print("Dry run. Re-run with --apply.")
        return 0

    total = 0
    for slug, lesson_id in lesson_ids.items():
        print(f"\napplying to {slug} (lesson {lesson_id}):")
        total += insert_blocks(conn, lesson_id, slug)
    conn.commit()

    print(f"\nInserted {total} Micro-Quest block(s) across {len(lesson_ids)} lessons.")

    print("\nVerification:")
    for slug, lesson_id in lesson_ids.items():
        blocks = microquest_blocks(conn, lesson_id)
        assert len(blocks) == 3, f"{slug}: expected 3 blocks, found {len(blocks)}"
        for row in blocks:
            langs = [
                r["language"]
                for r in conn.execute(
                    "select language from lesson_block_translations where block_id = ? order by language",
                    (row["id"],),
                )
            ]
            assert langs == ["ar", "en", "fr"], f"{slug} block {row['id']}: languages {langs}"
            kind = None
            raw = conn.execute("select config from lesson_blocks where id = ?", (row["id"],)).fetchone()["config"]
            if raw:
                kind = json.loads(raw).get("kind")
            print(
                f"    lesson {lesson_id} ({slug}) id={row['id']} {row['block_type']} "
                f"order={row['order']} kind={kind} languages={langs}"
            )

    integrity_after = conn.execute("pragma integrity_check").fetchone()[0]
    fk_check = conn.execute("pragma foreign_key_check").fetchall()
    print(f"\npragma integrity_check (after): {integrity_after}")
    print(f"pragma foreign_key_check (after): {'ok' if not fk_check else fk_check}")
    if integrity_after != "ok" or fk_check:
        raise SystemExit("integrity check failed after migration -- investigate before trusting this data")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
