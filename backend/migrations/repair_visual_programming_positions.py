"""Repair the visual-programming starter graphs in a deployed database.

WHY
---
Three seeded exercises shipped graphs the editor could not render:

  * Two carry nodes with no ``position`` at all. The editor does arithmetic on
    ``node.position.x`` while laying out edges, so the page threw during render
    and went blank -- served with a 200, so nothing that only checks status
    codes noticed.
  * One ("polymorphism", in CS Fundamentals) has ``starter_code`` that is not
    valid JSON: it was authored as a Python single-quoted literal containing
    ``\\"`` escapes, which produce *bare* quotes inside the JSON string. The
    API's ``except JSONDecodeError`` returns an empty graph, so that exercise's
    starter has never loaded at all. It only looked healthy because it failed
    earlier than the other two.

The seed is already fixed (see app/seed/base.py visual_graph), but seeding only
ever INSERTS: ``get_or_create_lesson`` returns early when the lesson exists and
exercises are built only on the create path, so a database that already has
these lessons keeps the broken rows forever. This script is how the fix reaches
one.

Note the client is defensive now too (frontend/src/lib/visualGraph.ts gives any
position-less node a fallback position), so a database that never runs this is
not broken -- it just shows the fallback cascade instead of the authored
layout. The exception is the unparseable graph, which has no nodes to fall back
on and stays empty until this runs.

WHAT THIS DOES
--------------
Rewrites ``exercises.starter_code`` for the three rows, matched by LESSON SLUG
plus exercise type and order -- never by id. Ids are assignment-order artefacts
and differ between environments; the ids that are 15/20/54 locally are not
necessarily those rows anywhere else.

Conditional and idempotent:

  * A row is rewritten only if its current ``starter_code`` still matches the
    broken shape -- unparseable, or parseable with at least one node missing a
    usable position. Anything already correct, or edited by hand since, is
    reported and left alone.
  * Running it a second time therefore changes nothing.

SAFETY
------
* Touches one column, ``exercises.starter_code``, on at most three rows. No
  user, attempt, progress or XP row is read or written.
* --check reports exactly what would change and writes nothing.
* A SQLite database is copied to backup-before-vp-positions-<timestamp>.db
  beside the original before --apply writes. PostgreSQL is expected to be
  backed up by the provider's own snapshot mechanism; this says so rather than
  pretending it took one.
* Goes through the app's own engine (``DATABASE_URL``) rather than raw
  sqlite3, unlike the older repair scripts here -- production is PostgreSQL and
  a sqlite3-only script could never be run against it.

DOES NOT RUN AUTOMATICALLY. app.db.session.init_db runs only the additive
COLUMN migrations in app/db/migrations.py at startup; that module's docstring
deliberately excludes anything that rewrites data. A deploy will not pick this
up -- an operator has to run it.

Usage:
    python migrations/repair_visual_programming_positions.py --check
    python migrations/repair_visual_programming_positions.py --apply
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Allow `python migrations/repair_visual_programming_positions.py` from the backend root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db.session import async_session_maker  # noqa: E402
from app.models import Exercise, ExerciseTypeEnum, Lesson  # noqa: E402
from app.seed.base import visual_graph  # noqa: E402

#: Two-column layout: the canvas is 642x600 and nodes are 180x60, so these two
#: columns' right edges (220, 510) both land inside it.
COL_A, COL_B = 40, 330
ROW_1, ROW_2, ROW_3 = 50, 230, 410


def _at(x: int, y: int) -> dict:
    return {"x": x, "y": y}


#: (lesson slug, exercise type, exercise order) -> corrected starter graph.
#: Keyed on slug rather than id on purpose -- see WHAT THIS DOES. Lesson
#: slugs are unique per module rather than globally, so the key could in
#: principle be ambiguous; checked against the schema, each of these three
#: slugs resolves to exactly one lesson and no (slug, order) pair collides
#: among visual_programming exercises. The query below takes .first() and
#: the --check output names the id it matched, so an ambiguous match in
#: some other environment is visible before --apply.
REPAIRS: dict[tuple[str, str, int], str] = {
    ("loops", "visual_programming", 2): visual_graph(
        [
            {"id": "1", "type": "start", "position": _at(COL_A, ROW_1), "config": {}},
            {"id": "2", "type": "loop", "position": _at(COL_B, ROW_1), "config": {"var": "i", "times": "5"}},
            {"id": "3", "type": "output", "position": _at(COL_A, ROW_2), "config": {"value": "i"}},
            {"id": "4", "type": "end", "position": _at(COL_B, ROW_2), "config": {}},
        ],
        [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
            {"source": "3", "target": "4"},
        ],
    ),
    ("functions", "visual_programming", 2): visual_graph(
        [
            {"id": "1", "type": "start", "position": _at(COL_A, ROW_1), "config": {}},
            {"id": "2", "type": "function", "position": _at(COL_B, ROW_1), "config": {"name": "double", "params": "x"}},
            {"id": "3", "type": "return", "position": _at(COL_A, ROW_2), "config": {"value": "x * 2"}},
            {"id": "4", "type": "output", "position": _at(COL_B, ROW_2), "config": {"value": "double(5)"}},
            {"id": "5", "type": "end", "position": _at(COL_A, ROW_3), "config": {}},
        ],
        [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
            {"source": "2", "target": "4"},
            {"source": "4", "target": "5"},
        ],
    ),
    # Verified against the schema: slug is "inheritance-polymorphism" and
    # this exercise is order 1, not 2 -- guessing either would have silently
    # matched nothing and reported "NOT FOUND".
    ("inheritance-polymorphism", "visual_programming", 1): visual_graph(
        [
            {"id": "1", "type": "start", "position": _at(COL_A, ROW_1), "config": {}},
            {
                "id": "2",
                "type": "variable",
                "position": _at(COL_B, ROW_1),
                "config": {"name": "animals", "value": '[Dog("Rex"), Cat("Whiskers")]'},
            },
            {"id": "3", "type": "loop", "position": _at(COL_A, ROW_2), "config": {"var": "a", "times": "len(animals)"}},
            {
                "id": "4",
                "type": "output",
                "position": _at(COL_B, ROW_2),
                "config": {"value": 'a.name + " says " + a.speak()'},
            },
            {"id": "5", "type": "end", "position": _at(COL_A, ROW_3), "config": {}},
        ],
        [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
            {"source": "3", "target": "4"},
            {"source": "4", "target": "5"},
        ],
    ),
}


def needs_repair(starter_code: str | None) -> tuple[bool, str]:
    """Is this row still the broken shape? Returns (needs_repair, reason).

    Deliberately narrow: only an unparseable graph, or one whose nodes lack a
    usable position, is rewritten. Anything else -- including a graph somebody
    has since laid out by hand -- is left exactly as it is.
    """
    if not starter_code or not starter_code.strip():
        return True, "starter_code is empty"
    try:
        graph = json.loads(starter_code)
    except (json.JSONDecodeError, TypeError):
        return True, "starter_code is not valid JSON"
    if not isinstance(graph, dict):
        return True, "starter_code is not an object"
    nodes = graph.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return True, "graph has no nodes"
    for node in nodes:
        if not isinstance(node, dict):
            return True, "graph contains a non-object node"
        position = node.get("position")
        if not isinstance(position, dict):
            return True, f"node {node.get('id')!r} has no position"
        for axis in ("x", "y"):
            value = position.get(axis)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return True, f"node {node.get('id')!r} position.{axis} is {value!r}"
    return False, "already has usable positions"


def _sqlite_path(database_url: str) -> Path | None:
    marker = "sqlite+aiosqlite:///"
    if not database_url.startswith(marker):
        return None
    return Path(database_url[len(marker):]).resolve()


def _backup_sqlite(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = path.with_name(f"backup-before-vp-positions-{stamp}{path.suffix}")
    shutil.copy2(path, destination)
    return destination


async def run(apply: bool) -> int:
    settings = get_settings()
    print(f"Database: {settings.database_url.split('@')[-1]}")

    if apply:
        sqlite_file = _sqlite_path(settings.database_url)
        if sqlite_file is not None:
            backup = _backup_sqlite(sqlite_file)
            print(f"Backup written to {backup.name}" if backup else "No existing SQLite file to back up.")
        else:
            print("Non-SQLite database: no automatic backup taken. Make sure a provider snapshot exists.")

    repaired = skipped = missing = 0
    async with async_session_maker() as db:
        for (slug, type_name, order), corrected in REPAIRS.items():
            result = await db.execute(
                select(Exercise)
                .join(Lesson, Lesson.id == Exercise.lesson_id)
                .where(
                    Lesson.slug == slug,
                    Exercise.exercise_type == ExerciseTypeEnum(type_name),
                    Exercise.order == order,
                )
            )
            exercise = result.scalars().first()
            if exercise is None:
                print(f"  lesson {slug!r} {type_name} #{order}: NOT FOUND, skipped")
                missing += 1
                continue

            should, reason = needs_repair(exercise.starter_code)
            label = f"  lesson {slug!r} (exercise id {exercise.id})"
            if not should:
                print(f"{label}: {reason}, left untouched")
                skipped += 1
                continue

            print(f"{label}: {reason} -> rewriting")
            if apply:
                exercise.starter_code = corrected
            repaired += 1

        if apply:
            await db.commit()

    verb = "Repaired" if apply else "Would repair"
    print(f"\n{verb} {repaired} exercise(s); {skipped} already correct; {missing} not found.")
    if not apply and repaired:
        print("Re-run with --apply to write.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="report what would change; write nothing")
    group.add_argument("--apply", action="store_true", help="write the corrected graphs")
    args = parser.parse_args()
    return asyncio.run(run(apply=args.apply))


if __name__ == "__main__":
    raise SystemExit(main())
