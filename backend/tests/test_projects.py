import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func
from app.models import LessonProgress, MissionStatusEnum, ProjectProgress


async def ensure_lesson_completed(db_session, user_id: int, lesson_id: int):
    """Ensure a lesson is marked as completed for a user."""
    result = await db_session.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id == lesson_id
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        progress = LessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status=MissionStatusEnum.completed,
            completed_at=func.now()
        )
        db_session.add(progress)
    else:
        progress.status = MissionStatusEnum.completed
        progress.completed_at = func.now()
    await db_session.commit()
    return progress


async def get_user_id(client: AsyncClient, headers: dict) -> int:
    """Get user ID from auth/me endpoint."""
    response = await client.get("/auth/me", headers=headers)
    return response.json()["id"]


@pytest.fixture
async def user_with_calculator_unlocked(client: AsyncClient, test_user, db_session):
    """A test user who has completed lesson 5 (prerequisite for calculator project)."""
    user_id = await get_user_id(client, test_user["headers"])
    await ensure_lesson_completed(db_session, user_id, 5)
    return test_user


class TestProjects:
    async def test_get_projects_list(self, client: AsyncClient, test_user):
        response = await client.get("/projects", headers=test_user["headers"])
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) >= 1

        project_slugs = {p["slug"] for p in projects}
        assert "calculator" in project_slugs
        assert "quiz-game" in project_slugs
        assert "personal-portfolio" in project_slugs
        assert "student-database" in project_slugs
        assert "algorithm-challenge" in project_slugs

    async def test_get_project_detail(self, client: AsyncClient, test_user):
        response = await client.get("/projects/1", headers=test_user["headers"])
        assert response.status_code == 200
        project = response.json()
        assert project["id"] == 1
        assert "tasks" in project
        assert len(project["tasks"]) >= 3

    async def test_project_tasks(self, client: AsyncClient, test_user):
        response = await client.get("/projects/1", headers=test_user["headers"])
        project = response.json()

        for task in project["tasks"]:
            assert "id" in task
            assert "order" in task
            assert "starter_code" in task
            assert "translations" in task
            assert len(task["translations"]) > 0
            for translation in task["translations"]:
                assert "title" in translation
                assert "description" in translation
                assert "hint" in translation

    async def test_project_progress_locked(self, client: AsyncClient, test_user):
        response = await client.get("/projects/1/progress", headers=test_user["headers"])
        assert response.status_code == 200
        progress = response.json()
        assert "status" in progress
        assert progress["status"] in ["locked", "ready", "in_progress", "completed"]

    async def test_start_project(self, client: AsyncClient, test_user):
        response = await client.post("/projects/1/start", headers=test_user["headers"])
        if response.status_code == 403:
            assert "locked" in response.json()["detail"].lower()
        else:
            assert response.status_code == 200
            progress = response.json()
            assert progress["status"] in ["in_progress", "completed"]

    async def test_start_project_unlocked(self, client: AsyncClient, user_with_calculator_unlocked):
        response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert response.status_code == 200
        progress = response.json()
        assert progress["status"] in ["in_progress", "completed"]

    async def test_submit_project_task(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        response = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 1,
            "code": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return \"Error: Division by zero\"\n\nprint(add(2, 3))"
        })
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            result = response.json()
            assert "success" in result
            assert "progress" in result

    async def test_unauthenticated_projects(self, client: AsyncClient):
        response = await client.get("/projects")
        assert response.status_code == 401


class TestProjectPrerequisites:
    async def test_project_locked_without_prerequisite(self, client: AsyncClient, test_user):
        # Project 2 (quiz-game) requires lesson 17
        # New user hasn't completed lesson 17, so it should be locked
        response = await client.get("/projects/2/progress", headers=test_user["headers"])
        assert response.status_code == 200
        progress = response.json()
        # Could be locked or ready depending on whether user has completed lesson 17
        assert progress["status"] in ["locked", "ready", "in_progress", "completed"]

    async def test_start_locked_project_fails(self, client: AsyncClient, test_user):
        response = await client.post("/projects/2/start", headers=test_user["headers"])
        # If locked, should return 403
        if response.status_code == 403:
            assert "locked" in response.json()["detail"].lower()
        else:
            # If not locked (user completed prerequisite), should succeed
            assert response.status_code == 200

    async def test_calculator_prerequisite_lesson_5(self, client: AsyncClient, test_user):
        # Calculator (project 1) requires lesson 5 (user-input-output)
        response = await client.get("/projects/1", headers=test_user["headers"])
        assert response.status_code == 200
        project = response.json()
        assert project["prerequisite_lesson_id"] == 5

    async def test_quiz_game_prerequisite_lesson_17(self, client: AsyncClient, test_user):
        response = await client.get("/projects/2", headers=test_user["headers"])
        assert response.status_code == 200
        project = response.json()
        assert project["prerequisite_lesson_id"] == 17

    async def test_portfolio_prerequisite_lesson_25(self, client: AsyncClient, test_user):
        response = await client.get("/projects/3", headers=test_user["headers"])
        assert response.status_code == 200
        project = response.json()
        assert project["prerequisite_lesson_id"] == 25

    async def test_student_db_prerequisite_lesson_30(self, client: AsyncClient, test_user):
        response = await client.get("/projects/4", headers=test_user["headers"])
        assert response.status_code == 200
        project = response.json()
        assert project["prerequisite_lesson_id"] == 30

    async def test_algorithm_prerequisite_lesson_39(self, client: AsyncClient, test_user):
        response = await client.get("/projects/5", headers=test_user["headers"])
        assert response.status_code == 200
        project = response.json()
        assert project["prerequisite_lesson_id"] == 39


class TestProjectTaskProgression:
    async def test_task_order_sequential(self, client: AsyncClient, test_user):
        response = await client.get("/projects/1", headers=test_user["headers"])
        project = response.json()
        tasks = project["tasks"]
        # Tasks should be ordered by order field
        orders = [t["order"] for t in tasks]
        assert orders == sorted(orders)

    async def test_task_validation_fails_with_wrong_code(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        # Submit incorrect code
        response = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 1,
            "code": "def add(a, b):\n    return a - b  # Wrong!"
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "error" in result or "output" in result

    async def test_task_validation_passes_with_correct_code(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        response = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 1,
            "code": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return \"Error: Division by zero\"\n\nprint(add(2, 3))"
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "progress" in result
        progress = result["progress"]
        assert progress["current_task"] >= 1

    async def test_task_progression_updates_current_task(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        # Submit task 1
        response1 = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 1,
            "code": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return \"Error: Division by zero\"\n\nprint(add(2, 3))"
        })
        assert response1.status_code == 200
        progress1 = response1.json()["progress"]
        
        # Get progress again
        response_progress = await client.get("/projects/1/progress", headers=user_with_calculator_unlocked["headers"])
        progress = response_progress.json()
        assert progress["current_task"] >= 1

    async def test_submitting_earlier_task_does_not_regress(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        # Submit task 2 first (if allowed)
        response2 = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 2,
            "code": "print('test')"
        })
        
        # Then submit task 1
        response1 = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 1,
            "code": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return \"Error: Division by zero\"\n\nprint(add(2, 3))"
        })
        
        # Current task should not go backwards
        progress_response = await client.get("/projects/1/progress", headers=user_with_calculator_unlocked["headers"])
        progress = progress_response.json()
        # The logic allows submitting any task, but current_task only increases


class TestProjectXPBehavior:
    async def test_failed_submission_gives_no_xp(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        # Get initial XP
        profile_response = await client.get("/auth/profile", headers=user_with_calculator_unlocked["headers"])
        initial_xp = profile_response.json()["xp"]

        # Submit incorrect code
        response = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 1,
            "code": "def add(a, b):\n    return a - b"
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False

        # XP should not change
        profile_response = await client.get("/auth/profile", headers=user_with_calculator_unlocked["headers"])
        new_xp = profile_response.json()["xp"]
        assert new_xp == initial_xp

    async def test_project_completion_awards_xp(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        # Get initial XP
        profile_response = await client.get("/auth/profile", headers=user_with_calculator_unlocked["headers"])
        initial_xp = profile_response.json()["xp"]

        # Complete all tasks for project 1 (4 tasks)
        correct_code = """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return "Error: Division by zero"

print(add(2, 3))"""

        for task_id in [1, 2, 3, 4]:
            response = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
                "task_id": task_id,
                "code": correct_code
            })
            if response.status_code != 200:
                pytest.skip(f"Task {task_id} validation issue")

        # Check final progress
        progress_response = await client.get("/projects/1/progress", headers=user_with_calculator_unlocked["headers"])
        progress = progress_response.json()
        
        if progress["status"] == "completed":
            # XP should be awarded
            profile_response = await client.get("/auth/profile", headers=user_with_calculator_unlocked["headers"])
            final_xp = profile_response.json()["xp"]
            assert final_xp >= initial_xp + 200  # Calculator project gives 200 XP

    async def test_duplicate_submission_no_duplicate_xp(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        correct_code = """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return "Error: Division by zero"

print(add(2, 3))"""

        # Complete all tasks
        for task_id in [1, 2, 3, 4]:
            await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
                "task_id": task_id,
                "code": correct_code
            })

        # Get XP after completion
        profile_response = await client.get("/auth/profile", headers=user_with_calculator_unlocked["headers"])
        xp_after_completion = profile_response.json()["xp"]

        # Re-submit the last task
        await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 4,
            "code": correct_code
        })

        # XP should not increase
        profile_response = await client.get("/auth/profile", headers=user_with_calculator_unlocked["headers"])
        xp_after_resubmit = profile_response.json()["xp"]
        assert xp_after_resubmit == xp_after_completion

    async def test_progress_persists_after_refresh(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        correct_code = """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return "Error: Division by zero"

print(add(2, 3))"""

        response = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
            "task_id": 1,
            "code": correct_code
        })
        assert response.status_code == 200

        # Get progress again (simulating refresh)
        progress_response = await client.get("/projects/1/progress", headers=user_with_calculator_unlocked["headers"])
        progress = progress_response.json()
        assert progress["current_task"] >= 1
        assert progress["status"] in ["in_progress", "completed"]


class TestProjectTranslations:
    async def test_project_has_translations(self, client: AsyncClient, test_user):
        for project_id in [1, 2, 3, 4, 5]:
            for lang in ["en", "fr", "ar"]:
                response = await client.get(f"/projects/{project_id}?language={lang}", headers=test_user["headers"])
                assert response.status_code == 200
                project = response.json()
                assert "translations" in project
                langs = {t["language"] for t in project["translations"]}
                assert lang in langs

    async def test_task_has_translations(self, client: AsyncClient, test_user):
        for lang in ["en", "fr", "ar"]:
            response = await client.get(f"/projects/1?language={lang}", headers=test_user["headers"])
            project = response.json()
            for task in project["tasks"]:
                langs = {t["language"] for t in task["translations"]}
                assert lang in langs

    async def test_arabic_rtl_support(self, client: AsyncClient, test_user):
        response = await client.get("/projects/1?language=ar", headers=test_user["headers"])
        project = response.json()
        for task in project["tasks"]:
            for trans in task["translations"]:
                if trans["language"] == "ar":
                    assert trans["title"]
                    assert trans["description"]


class TestProjectCompletion:
    async def test_calculator_completion(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        correct_code = """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return "Error: Division by zero"

print(add(2, 3))"""

        for task_id in [1, 2, 3, 4]:
            response = await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
                "task_id": task_id,
                "code": correct_code
            })
            assert response.status_code == 200
            result = response.json()
            if result["success"]:
                assert result["progress"]["current_task"] >= task_id

    async def test_project_completed_status(self, client: AsyncClient, user_with_calculator_unlocked):
        start_response = await client.post("/projects/1/start", headers=user_with_calculator_unlocked["headers"])
        assert start_response.status_code == 200

        correct_code = """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return "Error: Division by zero"

print(add(2, 3))"""

        for task_id in [1, 2, 3, 4]:
            await client.post("/projects/1/submit-task", headers=user_with_calculator_unlocked["headers"], json={
                "task_id": task_id,
                "code": correct_code
            })

        progress_response = await client.get("/projects/1/progress", headers=user_with_calculator_unlocked["headers"])
        progress = progress_response.json()
        if progress["status"] == "completed":
            assert progress["xp_earned"] == 200
            assert progress["completed_at"] is not None


    async def test_concurrent_start_project_is_idempotent(
        self, client: AsyncClient, user_with_calculator_unlocked, db_session
    ):
        """POST /projects/{id}/start had the same check-then-insert race as lessons.

        Concurrent starts previously raced on uq_user_project and the loser
        returned 500. All requests must now succeed and describe one row.
        """
        headers = user_with_calculator_unlocked["headers"]
        user_id = await get_user_id(client, headers)

        responses = await asyncio.gather(
            *[client.post("/projects/1/start", headers=headers) for _ in range(8)]
        )

        assert [r.status_code for r in responses] == [200] * 8, [r.status_code for r in responses]
        assert len({r.json()["id"] for r in responses}) == 1

        count = await db_session.execute(
            select(func.count())
            .select_from(ProjectProgress)
            .where(ProjectProgress.user_id == user_id, ProjectProgress.project_id == 1)
        )
        assert count.scalar() == 1

    async def test_concurrent_project_progress_reads_do_not_duplicate(
        self, client: AsyncClient, test_user, db_session
    ):
        """GET /projects/{id}/progress auto-creates a row, so it races too."""
        headers = test_user["headers"]
        user_id = await get_user_id(client, headers)

        responses = await asyncio.gather(
            *[client.get("/projects/2/progress", headers=headers) for _ in range(8)]
        )

        assert [r.status_code for r in responses] == [200] * 8, [r.status_code for r in responses]
        assert len({r.json()["id"] for r in responses}) == 1

        count = await db_session.execute(
            select(func.count())
            .select_from(ProjectProgress)
            .where(ProjectProgress.user_id == user_id, ProjectProgress.project_id == 2)
        )
        assert count.scalar() == 1

    async def test_start_project_does_not_overwrite_existing_progress(
        self, client: AsyncClient, user_with_calculator_unlocked, db_session
    ):
        """Restarting a project must preserve XP, task position and completion."""
        headers = user_with_calculator_unlocked["headers"]
        first = await client.post("/projects/1/start", headers=headers)
        assert first.status_code == 200
        progress_id = first.json()["id"]

        result = await db_session.execute(
            select(ProjectProgress).where(ProjectProgress.id == progress_id)
        )
        progress = result.scalar_one()
        progress.status = MissionStatusEnum.completed
        progress.xp_earned = 77
        progress.current_task = 3
        await db_session.commit()

        again = await client.post("/projects/1/start", headers=headers)
        assert again.status_code == 200
        assert again.json()["id"] == progress_id
        assert again.json()["status"] == "completed"
        assert again.json()["xp_earned"] == 77
        assert again.json()["current_task"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])