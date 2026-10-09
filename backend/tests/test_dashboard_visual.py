import pytest
from httpx import AsyncClient
from sqlalchemy import select


class TestDashboard:
    async def test_dashboard_loads(self, client: AsyncClient, test_user):
        response = await client.get("/dashboard", headers=test_user["headers"])
        assert response.status_code == 200
        dashboard = response.json()
        
        assert "user" in dashboard
        assert "profile" in dashboard
        assert "course_progress" in dashboard
        assert "recent_achievements" in dashboard

    async def test_dashboard_xp_level(self, client: AsyncClient, test_user):
        response = await client.get("/dashboard", headers=test_user["headers"])
        dashboard = response.json()
        
        assert dashboard["profile"]["xp"] >= 0
        assert dashboard["profile"]["level"] >= 1
        assert dashboard["profile"]["streak"] >= 0

    async def test_dashboard_course_progress(self, client: AsyncClient, test_user):
        response = await client.get("/dashboard", headers=test_user["headers"])
        dashboard = response.json()
        
        assert isinstance(dashboard["course_progress"], list)
        for cp in dashboard["course_progress"]:
            assert "course_id" in cp
            assert "completed_lessons" in cp
            assert "total_lessons" in cp
            assert "progress_percent" in cp

    async def test_dashboard_current_mission(self, client: AsyncClient, test_user):
        response = await client.get("/dashboard", headers=test_user["headers"])
        dashboard = response.json()
        
        if dashboard["current_mission"]:
            mission = dashboard["current_mission"]
            assert "id" in mission
            assert "title" in mission["translations"][0]

    async def test_unauthenticated_dashboard(self, client: AsyncClient):
        response = await client.get("/dashboard")
        assert response.status_code == 401

    async def test_course_progress_carries_the_course_title(self, client: AsyncClient, test_user):
        # GET .../progress lazily creates the CourseProgress row on first fetch.
        progress_response = await client.get("/courses/1/progress", headers=test_user["headers"])
        assert progress_response.status_code == 200

        response = await client.get("/dashboard", headers=test_user["headers"])
        dashboard = response.json()
        row = next(cp for cp in dashboard["course_progress"] if cp["course_id"] == 1)
        assert row["title"]  # resolved, not the bare numeric id the frontend used to show

    async def test_current_mission_carries_its_course_and_module_titles(self, client: AsyncClient, test_user):
        start_response = await client.post("/lessons/1/start", headers=test_user["headers"])
        assert start_response.status_code == 200

        response = await client.get("/dashboard", headers=test_user["headers"])
        dashboard = response.json()
        assert dashboard["current_mission"]["id"] == 1
        assert dashboard["current_mission_course_title"]
        assert dashboard["current_mission_module_title"]

    async def test_no_current_mission_means_no_titles(self, client: AsyncClient, second_user):
        # A fresh account that never started a lesson has no current_mission_id.
        response = await client.get("/dashboard", headers=second_user["headers"])
        dashboard = response.json()
        assert dashboard["current_mission"] is None
        assert dashboard["current_mission_course_title"] is None
        assert dashboard["current_mission_module_title"] is None


class TestVisualProgramming:
    async def test_compile_valid_graph(self, client: AsyncClient, test_user):
        response = await client.post("/visual/compile", headers=test_user["headers"], json={
            "nodes": [
                {"id": "1", "type": "start", "config": {}},
                {"id": "2", "type": "variable", "config": {"name": "x", "value": "10"}},
                {"id": "3", "type": "output", "config": {"value": "x"}},
                {"id": "4", "type": "end", "config": {}}
            ],
            "edges": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "4"}
            ]
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is True
        assert "python_code" in result
        assert "x = 10" in result["python_code"]
        assert "print(x)" in result["python_code"]

    async def test_compile_invalid_graph_no_start(self, client: AsyncClient, test_user):
        response = await client.post("/visual/compile", headers=test_user["headers"], json={
            "nodes": [
                {"id": "1", "type": "variable", "config": {"name": "x", "value": "10"}},
                {"id": "2", "type": "output", "config": {"value": "x"}},
            ],
            "edges": [
                {"source": "1", "target": "2"}
            ]
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    async def test_compile_multiple_start(self, client: AsyncClient, test_user):
        response = await client.post("/visual/compile", headers=test_user["headers"], json={
            "nodes": [
                {"id": "1", "type": "start", "config": {}},
                {"id": "2", "type": "start", "config": {}},
                {"id": "3", "type": "end", "config": {}}
            ],
            "edges": [
                {"source": "1", "target": "3"}
            ]
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is False
        assert any("Multiple start nodes" in e for e in result["errors"])

    async def test_compile_unreachable_nodes(self, client: AsyncClient, test_user):
        response = await client.post("/visual/compile", headers=test_user["headers"], json={
            "nodes": [
                {"id": "1", "type": "start", "config": {}},
                {"id": "2", "type": "variable", "config": {"name": "x", "value": "10"}},
                {"id": "3", "type": "variable", "config": {"name": "y", "value": "20"}},
                {"id": "4", "type": "end", "config": {}}
            ],
            "edges": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "4"}
            ]
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is False
        assert any("Unreachable nodes" in e for e in result["errors"])

    async def test_every_visual_starter_is_renderable(
        self, client: AsyncClient, test_user, db_session
    ):
        """Every visual_programming starter must parse AND carry positions.

        The previous version of this test looped ids 1..20, asserted only that
        `nodes` and `edges` keys existed, and `return`ed on the first 200 -- so
        it checked exactly one exercise, never looked at `position`, and passed
        while all three seeded graphs were broken:

          * 15 and 20 shipped every node without a `position`, and the editor
            does arithmetic on `node.position.x` -- it threw during render and
            blanked the page.
          * 54's starter_code was invalid JSON (a Python escaping bug), so the
            endpoint's except-JSONDecodeError served an empty graph and its
            starter never loaded at all.

        So this walks every one of them, does not return early, and asserts the
        properties that actually make a graph renderable.
        """
        from app.models import Exercise, ExerciseTypeEnum

        result = await db_session.execute(
            select(Exercise.id)
            .where(Exercise.exercise_type == ExerciseTypeEnum.visual_programming)
            .order_by(Exercise.id)
        )
        exercise_ids = list(result.scalars().all())
        assert exercise_ids, "seed should contain visual_programming exercises"

        failures: list[str] = []
        for exercise_id in exercise_ids:
            response = await client.get(
                f"/visual/{exercise_id}/starter", headers=test_user["headers"]
            )
            if response.status_code != 200:
                failures.append(f"exercise {exercise_id}: HTTP {response.status_code}")
                continue
            starter = response.json()

            # An unparseable starter_code is indistinguishable from an empty
            # one here -- the endpoint swallows JSONDecodeError and returns
            # {"nodes": [], "edges": []} -- so an empty graph IS the failure.
            if not starter.get("nodes"):
                failures.append(
                    f"exercise {exercise_id}: no nodes "
                    "(starter_code is empty or does not parse)"
                )
                continue

            for node in starter["nodes"]:
                position = node.get("position")
                if not isinstance(position, dict):
                    failures.append(f"exercise {exercise_id} node {node.get('id')!r}: no position")
                    continue
                for axis in ("x", "y"):
                    value = position.get(axis)
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        failures.append(
                            f"exercise {exercise_id} node {node.get('id')!r}: "
                            f"position.{axis} is {value!r}, not a number"
                        )

            node_ids = {n.get("id") for n in starter["nodes"]}
            for edge in starter.get("edges", []):
                if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
                    failures.append(f"exercise {exercise_id}: edge {edge} references a missing node")

        assert not failures, "unrenderable visual starters:\n  " + "\n  ".join(failures)

    async def test_unauthenticated_visual(self, client: AsyncClient):
        response = await client.post("/visual/compile", json={"nodes": [], "edges": []})
        assert response.status_code == 401