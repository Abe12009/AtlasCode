import pytest
from httpx import AsyncClient


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

    async def test_visual_starter(self, client: AsyncClient, test_user):
        for exercise_id in range(1, 20):
            response = await client.get(f"/visual/{exercise_id}/starter", headers=test_user["headers"])
            if response.status_code == 200:
                starter = response.json()
                assert "nodes" in starter
                assert "edges" in starter
                return
        pytest.skip("No visual exercise found")

    async def test_unauthenticated_visual(self, client: AsyncClient):
        response = await client.post("/visual/compile", json={"nodes": [], "edges": []})
        assert response.status_code == 401