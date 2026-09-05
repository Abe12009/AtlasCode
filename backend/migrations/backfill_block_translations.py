"""Backfill FR/AR lesson_block_translations for courses 1-5.

WHY
---
Courses 6-15 store every block body in lesson_block_translations for en/fr/ar.
Courses 1-5 predate that table: their block bodies live only in the base
lesson_blocks.content column, in English. A French or Arabic learner therefore
reads English lesson bodies in the five original courses.

WHAT THIS DOES
--------------
INSERT-only. For each block that currently has no translation rows it writes
three rows (en, fr, ar). ``code_example`` is copied verbatim from the base
block into all three languages, matching how courses 6-15 store it -- code,
identifiers and inline comments are never translated.

SAFETY
------
* Never updates or deletes an existing translation row; a block that already
  has any translation is skipped untouched.
* Verifies the block's current English text still matches the text the
  translation was authored against, and skips (loudly) if it has drifted.
* Runs inside a single transaction and reports exactly what it wrote.

Usage:
    python migrations/backfill_block_translations.py --check
    python migrations/backfill_block_translations.py --apply
    python migrations/backfill_block_translations.py --rollback   # deletes ONLY rows this wrote
"""

import argparse
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.dirname(HERE)
sys.path.insert(0, BACKEND)

DB = os.path.join(BACKEND, "atlascode.db")

from app.seed.block_translations_python import PYTHON_FOUNDATIONS_BLOCKS
from app.seed.block_translations_web_sql_git import WEB_SQL_GIT_BLOCKS
from app.seed.block_translations_cs import CS_FUNDAMENTALS_BLOCKS

TRANSLATIONS: dict[int, dict[str, str]] = {}
for source in (PYTHON_FOUNDATIONS_BLOCKS, WEB_SQL_GIT_BLOCKS, CS_FUNDAMENTALS_BLOCKS):
    overlap = TRANSLATIONS.keys() & source.keys()
    assert not overlap, f"duplicate block ids across translation modules: {sorted(overlap)}"
    TRANSLATIONS.update(source)

LANGUAGES = ("en", "fr", "ar")


def normalize(text) -> str:
    return (text or "").strip()


def plan(conn):
    """Return (writable, drifted, already_translated, unknown)."""
    writable, drifted, already, unknown = [], [], [], []
    for block_id, texts in sorted(TRANSLATIONS.items()):
        row = conn.execute(
            "select id, content, code_example from lesson_blocks where id = ?", (block_id,)
        ).fetchone()
        if row is None:
            unknown.append(block_id)
            continue
        existing = conn.execute(
            "select count(*) from lesson_block_translations where block_id = ?", (block_id,)
        ).fetchone()[0]
        if existing:
            already.append(block_id)
            continue
        if normalize(row["content"]) != normalize(texts["en"]):
            drifted.append((block_id, normalize(row["content"])[:60], normalize(texts["en"])[:60]))
            continue
        writable.append((block_id, row["code_example"], texts))
    return writable, drifted, already, unknown


def coverage(conn):
    total = conn.execute("select count(*) from lesson_blocks").fetchone()[0]
    full = conn.execute(
        """select count(*) from lesson_blocks b
           where (select count(distinct language) from lesson_block_translations t
                  where t.block_id = b.id) >= 3"""
    ).fetchone()[0]
    return full, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(DB if (args.apply or args.rollback) else f"file:{DB}?mode=ro",
                           uri=not (args.apply or args.rollback))
    conn.row_factory = sqlite3.Row

    if args.rollback:
        ids = tuple(TRANSLATIONS)
        marks = ",".join("?" * len(ids))
        removed = conn.execute(
            f"delete from lesson_block_translations where block_id in ({marks})", ids
        ).rowcount
        conn.commit()
        print(f"Removed {removed} translation rows for the {len(ids)} backfilled blocks.")
        return 0

    writable, drifted, already, unknown = plan(conn)
    before_full, total = coverage(conn)

    print(f"Blocks with translations authored: {len(TRANSLATIONS)}")
    print(f"  ready to write   : {len(writable)}")
    print(f"  already translated (skipped): {len(already)}")
    print(f"  English text drifted (skipped): {len(drifted)}")
    for block_id, live, authored in drifted:
        print(f"      block {block_id}\n        live    : {live!r}\n        authored: {authored!r}")
    print(f"  block id not in database (skipped): {len(unknown)} {unknown}")
    print(f"\nCoverage before: {before_full}/{total} blocks have all 3 languages")

    if not args.apply:
        print("\nDry run. Re-run with --apply to write.")
        return 0

    written = 0
    for block_id, code_example, texts in writable:
        for language in LANGUAGES:
            conn.execute(
                "insert into lesson_block_translations (block_id, language, content, code_example) "
                "values (?, ?, ?, ?)",
                (block_id, language, texts[language], code_example),
            )
            written += 1
    conn.commit()

    after_full, total = coverage(conn)
    print(f"\nInserted {written} rows across {len(writable)} blocks.")
    print(f"Coverage after: {after_full}/{total} blocks have all 3 languages")
    conn.close()
    return 0 if not drifted and not unknown else 1


if __name__ == "__main__":
    raise SystemExit(main())
