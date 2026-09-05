import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.models import LessonProgress, MissionStatusEnum, User


class TestLessons:
    async def test_get_lesson_detail(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        assert response.status_code == 200
        lesson = response.json()
        assert lesson["id"] == 1
        assert "blocks" in lesson
        assert "exercises" in lesson
        assert "translations" in lesson
        assert len(lesson["blocks"]) > 0
        assert len(lesson["exercises"]) > 0

    async def test_lesson_blocks_render(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        lesson = response.json()
        
        block_types = {b["block_type"] for b in lesson["blocks"]}
        assert "text" in block_types or "code" in block_types
        
        for block in lesson["blocks"]:
            assert "id" in block
            assert "block_type" in block
            assert "order" in block

    async def test_lesson_exercises_render(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1", headers=test_user["headers"])
        lesson = response.json()
        
        for exercise in lesson["exercises"]:
            assert "id" in exercise
            assert "exercise_type" in exercise
            assert "order" in exercise
            assert "xp_reward" in exercise
            assert "translations" in exercise
            assert len(exercise["translations"]) > 0

    async def test_lesson_progress(self, client: AsyncClient, test_user):
        response = await client.get("/lessons/1/progress", headers=test_user["headers"])
        assert response.status_code == 200
        progress = response.json()
        assert progress["lesson_id"] == 1
        assert "status" in progress

    async def test_start_lesson(self, client: AsyncClient, test_user):
        response = await client.post("/lessons/1/start", headers=test_user["headers"])
        assert response.status_code == 200
        progress = response.json()
        assert progress["status"] in ["in_progress", "completed"]

    async def test_concurrent_start_lesson_is_idempotent(
        self, client: AsyncClient, test_user, db_session
    ):
        """Reproduces the race: many simultaneous starts of the same lesson.

        Each request gets its own session, so they genuinely interleave. Before
        the fix the losers raised UNIQUE constraint failed on
        (user_id, lesson_id) and returned 500.
        """
        responses = await asyncio.gather(
            *[client.post("/lessons/2/start", headers=test_user["headers"]) for _ in range(8)]
        )

        assert [r.status_code for r in responses] == [200] * 8, [r.status_code for r in responses]

        # All requests must describe the same single row.
        ids = {r.json()["id"] for r in responses}
        assert len(ids) == 1, ids
        for r in responses:
            assert r.json()["lesson_id"] == 2
            assert r.json()["status"] in ("in_progress", "completed")

        user_result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user_id = user_result.scalar_one().id

        count = await db_session.execute(
            select(func.count())
            .select_from(LessonProgress)
            .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == 2)
        )
        assert count.scalar() == 1

    async def test_concurrent_progress_reads_do_not_duplicate(
        self, client: AsyncClient, test_user, db_session
    ):
        """GET /progress auto-creates a row too, so it has the same race."""
        responses = await asyncio.gather(
            *[client.get("/lessons/3/progress", headers=test_user["headers"]) for _ in range(8)]
        )

        assert [r.status_code for r in responses] == [200] * 8, [r.status_code for r in responses]
        assert len({r.json()["id"] for r in responses}) == 1

        user_result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user_id = user_result.scalar_one().id

        count = await db_session.execute(
            select(func.count())
            .select_from(LessonProgress)
            .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == 3)
        )
        assert count.scalar() == 1

    async def test_start_lesson_does_not_overwrite_existing_progress(
        self, client: AsyncClient, test_user, db_session
    ):
        """Restarting a lesson must preserve earned XP, position and completion."""
        first = await client.post("/lessons/4/start", headers=test_user["headers"])
        assert first.status_code == 200
        progress_id = first.json()["id"]

        result = await db_session.execute(
            select(LessonProgress).where(LessonProgress.id == progress_id)
        )
        progress = result.scalar_one()
        progress.status = MissionStatusEnum.completed
        progress.xp_earned = 42
        progress.current_block = 3
        await db_session.commit()

        again = await client.post("/lessons/4/start", headers=test_user["headers"])
        assert again.status_code == 200
        assert again.json()["id"] == progress_id
        assert again.json()["status"] == "completed"
        assert again.json()["xp_earned"] == 42
        assert again.json()["current_block"] == 3

    async def test_unauthenticated_lesson(self, client: AsyncClient):
        response = await client.get("/lessons/1")
        assert response.status_code == 401

    async def test_multiple_lessons_from_different_courses(self, client: AsyncClient, test_user):
        lesson_ids = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45]
        
        for lesson_id in lesson_ids:
            response = await client.get(f"/lessons/{lesson_id}", headers=test_user["headers"])
            if response.status_code == 200:
                lesson = response.json()
                assert "blocks" in lesson
                assert "exercises" in lesson