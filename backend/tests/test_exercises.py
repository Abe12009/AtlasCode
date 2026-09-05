import pytest
from httpx import AsyncClient


class TestExercises:
    async def test_get_exercise_detail(self, client: AsyncClient, test_user):
        response = await client.get("/exercises/1", headers=test_user["headers"])
        assert response.status_code == 200
        exercise = response.json()
        assert exercise["id"] == 1
        assert "exercise_type" in exercise
        assert "translations" in exercise

    async def test_exercise_run_code_writing(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert "is_correct" in result
        assert "output" in result
        assert "xp_earned" in result
        assert result["xp_earned"] == 0

    async def test_exercise_submit_first_time(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert result["xp_earned"] > 0

    async def test_exercise_submit_duplicate_no_xp(self, client: AsyncClient, test_user):
        # First submit - should earn XP
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert result["xp_earned"] > 0
        first_xp = result["xp_earned"]
        
        # Second submit with same correct code - should NOT earn XP again
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert result["xp_earned"] == 0

    async def test_exercise_submit_incorrect(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Wrong")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert result["xp_earned"] == 0

    async def test_multiple_choice_exercise(self, client: AsyncClient, test_user):
        response = await client.get("/exercises/1", headers=test_user["headers"])
        exercise = response.json()
        
        if exercise["exercise_type"] == "multiple_choice":
            assert "options" in exercise
            assert len(exercise["options"]) > 0

    async def test_prediction_exercise(self, client: AsyncClient, test_user):
        for exercise_id in range(1, 20):
            response = await client.get(f"/exercises/{exercise_id}", headers=test_user["headers"])
            if response.status_code == 200:
                exercise = response.json()
                if exercise["exercise_type"] == "prediction":
                    assert "translations" in exercise
                    return
        pytest.skip("No prediction exercise found")

    async def test_fill_blank_exercise(self, client: AsyncClient, test_user):
        for exercise_id in range(1, 20):
            response = await client.get(f"/exercises/{exercise_id}", headers=test_user["headers"])
            if response.status_code == 200:
                exercise = response.json()
                if exercise["exercise_type"] == "fill_blank":
                    assert "translations" in exercise
                    return
        pytest.skip("No fill_blank exercise found")

    async def test_ordering_exercise(self, client: AsyncClient, test_user):
        for exercise_id in range(1, 20):
            response = await client.get(f"/exercises/{exercise_id}", headers=test_user["headers"])
            if response.status_code == 200:
                exercise = response.json()
                if exercise["exercise_type"] == "ordering":
                    assert "translations" in exercise
                    return
        pytest.skip("No ordering exercise found")

    async def test_debugging_exercise(self, client: AsyncClient, test_user):
        for exercise_id in range(1, 20):
            response = await client.get(f"/exercises/{exercise_id}", headers=test_user["headers"])
            if response.status_code == 200:
                exercise = response.json()
                if exercise["exercise_type"] == "debugging":
                    assert "translations" in exercise
                    return
        pytest.skip("No debugging exercise found")

    async def test_visual_programming_exercise(self, client: AsyncClient, test_user):
        for exercise_id in range(1, 20):
            response = await client.get(f"/exercises/{exercise_id}", headers=test_user["headers"])
            if response.status_code == 200:
                exercise = response.json()
                if exercise["exercise_type"] == "visual_programming":
                    assert "translations" in exercise
                    return
        pytest.skip("No visual_programming exercise found")

    async def test_unauthenticated_exercise(self, client: AsyncClient):
        response = await client.get("/exercises/1")
        assert response.status_code == 401

    async def test_invalid_exercise_id(self, client: AsyncClient, test_user):
        response = await client.get("/exercises/99999", headers=test_user["headers"])
        assert response.status_code == 404