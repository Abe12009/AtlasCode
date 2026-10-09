"""Cover the visual-programming starter repair script.

Three layers: the decision logic (`needs_repair`), the corrected payloads, and
an end-to-end run of the real script against a throwaway SQLite file built to
contain the exact broken rows -- check, apply, re-apply, and a hand-edited row
that must survive.

The migration is deliberately NOT run against any real database here. It is a
manual operator script; see its docstring.
"""

import json

import pytest
from sqlalchemy import select

from app.models import Exercise, ExerciseTypeEnum, Lesson
from migrations.repair_visual_programming_positions import REPAIRS, needs_repair

# The exact shapes the three rows shipped with.
BROKEN_NO_POSITION = json.dumps(
    {
        "nodes": [
            {"id": "1", "type": "start", "config": {}},
            {"id": "2", "type": "loop", "config": {"var": "i", "times": "5"}},
        ],
        "edges": [{"source": "1", "target": "2"}],
    }
)
BROKEN_INVALID_JSON = '{"nodes": [{"id": "1", "config": {"value": "[Dog("Rex")]"}}], "edges": []}'


class TestNeedsRepair:
    def test_detects_nodes_without_a_position(self):
        should, reason = needs_repair(BROKEN_NO_POSITION)
        assert should is True
        assert "position" in reason

    def test_detects_unparseable_starter_code(self):
        should, reason = needs_repair(BROKEN_INVALID_JSON)
        assert should is True
        assert "not valid JSON" in reason

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_detects_an_empty_starter(self, value):
        should, _ = needs_repair(value)
        assert should is True

    def test_leaves_an_already_correct_graph_alone(self):
        good = json.dumps(
            {
                "nodes": [{"id": "1", "type": "start", "position": {"x": 40, "y": 50}, "config": {}}],
                "edges": [],
            }
        )
        should, reason = needs_repair(good)
        assert should is False, reason

    def test_leaves_a_hand_edited_layout_alone(self):
        """The guard that stops this clobbering later authoring.

        Someone repositioning these nodes by hand produces a graph that is
        valid but not what this script would write. It must be left exactly as
        it is.
        """
        hand_edited = json.dumps(
            {
                "nodes": [
                    {"id": "1", "type": "start", "position": {"x": 999, "y": 777}, "config": {}},
                    {"id": "2", "type": "loop", "position": {"x": 12.5, "y": 0}, "config": {}},
                ],
                "edges": [{"source": "1", "target": "2"}],
            }
        )
        should, reason = needs_repair(hand_edited)
        assert should is False, reason

    @pytest.mark.parametrize(
        "position",
        [None, "nope", {"x": 1}, {"x": "a", "y": "b"}, {"x": True, "y": False}],
        ids=["missing", "string", "partial", "non-numeric", "booleans"],
    )
    def test_detects_malformed_positions(self, position):
        node = {"id": "1", "type": "start", "config": {}}
        if position is not None:
            node["position"] = position
        should, _ = needs_repair(json.dumps({"nodes": [node], "edges": []}))
        assert should is True

    def test_is_idempotent_against_its_own_output(self):
        """Running the script twice must change nothing the second time.

        Every corrected payload has to be a graph `needs_repair` then declines
        to touch -- otherwise a second run would rewrite the rows again.
        """
        for key, corrected in REPAIRS.items():
            should, reason = needs_repair(corrected)
            assert should is False, f"{key} would be rewritten a second time: {reason}"


class TestCorrectedPayloads:
    def test_every_payload_parses_and_is_fully_positioned(self):
        for key, corrected in REPAIRS.items():
            graph = json.loads(corrected)
            assert graph["nodes"], key
            for node in graph["nodes"]:
                position = node["position"]
                assert isinstance(position["x"], (int, float)) and not isinstance(position["x"], bool), key
                assert isinstance(position["y"], (int, float)) and not isinstance(position["y"], bool), key

    def test_every_payload_fits_the_canvas(self):
        # Canvas measures 642x600 and a node is 180x60; a node whose right or
        # bottom edge falls outside spills past the visible panel.
        for key, corrected in REPAIRS.items():
            for node in json.loads(corrected)["nodes"]:
                assert node["position"]["x"] + 180 <= 642, f"{key} node {node['id']} overflows right"
                assert node["position"]["y"] + 60 <= 600, f"{key} node {node['id']} overflows bottom"

    def test_no_edge_references_a_missing_node(self):
        for key, corrected in REPAIRS.items():
            graph = json.loads(corrected)
            ids = {n["id"] for n in graph["nodes"]}
            for edge in graph["edges"]:
                assert edge["source"] in ids and edge["target"] in ids, f"{key}: {edge}"


class TestTargetsResolve:
    """The (slug, type, order) keys must match real rows.

    Keyed on slug rather than id on purpose, but a wrong slug or order fails
    silently -- the script just reports NOT FOUND and repairs nothing. This
    catches that. (Two of the three keys were wrong on the first draft.)
    """

    async def test_each_repair_key_matches_exactly_one_exercise(self, db_session):
        for slug, type_name, order in REPAIRS:
            result = await db_session.execute(
                select(Exercise.id)
                .join(Lesson, Lesson.id == Exercise.lesson_id)
                .where(
                    Lesson.slug == slug,
                    Exercise.exercise_type == ExerciseTypeEnum(type_name),
                    Exercise.order == order,
                )
            )
            matched = list(result.scalars().all())
            assert len(matched) == 1, (
                f"({slug!r}, {type_name}, {order}) matched {len(matched)} exercises: {matched}"
            )

    async def test_the_keys_cover_every_visual_programming_exercise(self, db_session):
        """If a new visual exercise is seeded, this repair stops being complete."""
        result = await db_session.execute(
            select(Exercise.id).where(Exercise.exercise_type == ExerciseTypeEnum.visual_programming)
        )
        assert len(list(result.scalars().all())) == len(REPAIRS)


class TestAgainstATemporaryDatabase:
    """End-to-end: run the real script against a throwaway SQLite file.

    The classes above test the predicate; this tests the script. It builds a
    database containing the exact broken rows, runs the script as a
    subprocess with DATABASE_URL pointed at it, and checks the full contract:
    --check writes nothing, --apply fixes the rows, a second --apply is a
    no-op, and a hand-edited row is never touched.

    A subprocess rather than importing run(): the script resolves its database
    from DATABASE_URL at import time through get_settings(), which is cached,
    so an in-process call would hit whatever the test session already opened.
    No real database is involved.
    """

    @staticmethod
    def _build(tmp_path):
        """A minimal schema holding the three target rows plus a decoy."""
        import sqlite3

        db = tmp_path / "repair_probe.db"
        conn = sqlite3.connect(db)
        conn.executescript(
            """
            CREATE TABLE courses (id INTEGER PRIMARY KEY, slug TEXT, "order" INTEGER);
            CREATE TABLE modules (id INTEGER PRIMARY KEY, course_id INTEGER, slug TEXT, "order" INTEGER);
            CREATE TABLE lessons (
                id INTEGER PRIMARY KEY, module_id INTEGER, slug TEXT, "order" INTEGER,
                difficulty TEXT, estimated_minutes INTEGER, xp_reward INTEGER,
                is_project BOOLEAN, project_id INTEGER
            );
            CREATE TABLE exercises (
                id INTEGER PRIMARY KEY, lesson_id INTEGER, exercise_type TEXT, "order" INTEGER,
                xp_reward INTEGER, starter_code TEXT, solution_code TEXT,
                test_code TEXT, validation_config TEXT
            );
            INSERT INTO courses VALUES (1, 'python-basics', 1);
            INSERT INTO modules VALUES (1, 1, 'basics', 1);
            """
        )
        rows = [
            (7, "loops", 2, BROKEN_NO_POSITION),
            (10, "functions", 2, BROKEN_NO_POSITION),
            (43, "inheritance-polymorphism", 1, BROKEN_INVALID_JSON),
        ]
        for lesson_id, slug, order, starter in rows:
            conn.execute(
                "INSERT INTO lessons VALUES (?,1,?,1,'beginner',30,50,0,NULL)", (lesson_id, slug)
            )
            conn.execute(
                "INSERT INTO exercises (lesson_id, exercise_type, \"order\", xp_reward, starter_code)"
                " VALUES (?, 'visual_programming', ?, 15, ?)",
                (lesson_id, order, starter),
            )
        # A decoy the script must never touch: right type, wrong lesson.
        conn.execute("INSERT INTO lessons VALUES (99,1,'unrelated',9,'beginner',30,50,0,NULL)")
        conn.execute(
            "INSERT INTO exercises (lesson_id, exercise_type, \"order\", xp_reward, starter_code)"
            " VALUES (99, 'visual_programming', 2, 15, ?)",
            (BROKEN_NO_POSITION,),
        )
        conn.commit()
        conn.close()
        return db

    @staticmethod
    def _starters(db):
        import sqlite3

        conn = sqlite3.connect(db)
        rows = conn.execute(
            "select l.slug, e.starter_code from exercises e join lessons l on l.id=e.lesson_id"
        ).fetchall()
        conn.close()
        return dict(rows)

    @staticmethod
    def _run(db, flag):
        import os
        import subprocess
        import sys
        from pathlib import Path

        backend = Path(__file__).resolve().parent.parent
        env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{db.as_posix()}"}
        return subprocess.run(
            [sys.executable, "migrations/repair_visual_programming_positions.py", flag],
            cwd=backend, env=env, capture_output=True, text=True, timeout=120,
        )

    def test_check_apply_reapply_and_leave_others_alone(self, tmp_path):
        db = self._build(tmp_path)
        before = self._starters(db)

        # --check must change nothing.
        check = self._run(db, "--check")
        assert check.returncode == 0, check.stderr
        assert "Would repair 3" in check.stdout, check.stdout
        assert self._starters(db) == before, "--check must not write"

        # --apply fixes the three targets.
        applied = self._run(db, "--apply")
        assert applied.returncode == 0, applied.stderr
        assert "Repaired 3" in applied.stdout, applied.stdout
        after = self._starters(db)
        for slug in ("loops", "functions", "inheritance-polymorphism"):
            graph = json.loads(after[slug])
            assert graph["nodes"], slug
            for node in graph["nodes"]:
                assert isinstance(node["position"]["x"], (int, float)), slug
                assert isinstance(node["position"]["y"], (int, float)), slug

        # The decoy in an unrelated lesson is untouched.
        assert after["unrelated"] == before["unrelated"]

        # Running again is a no-op.
        again = self._run(db, "--apply")
        assert again.returncode == 0, again.stderr
        assert "Repaired 0" in again.stdout, again.stdout
        assert "3 already correct" in again.stdout, again.stdout
        assert self._starters(db) == after, "second run must change nothing"

    def test_a_hand_edited_row_survives(self, tmp_path):
        import sqlite3

        db = self._build(tmp_path)
        hand = json.dumps(
            {
                "nodes": [{"id": "1", "type": "start", "position": {"x": 999, "y": 777}, "config": {}}],
                "edges": [],
            }
        )
        conn = sqlite3.connect(db)
        conn.execute(
            "update exercises set starter_code = ? where lesson_id = "
            "(select id from lessons where slug = 'loops')",
            (hand,),
        )
        conn.commit()
        conn.close()

        result = self._run(db, "--apply")
        assert result.returncode == 0, result.stderr
        assert self._starters(db)["loops"] == hand, "a hand-edited layout must not be clobbered"
        assert "left untouched" in result.stdout
