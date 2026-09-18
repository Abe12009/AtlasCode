"""HTTP surface over app.services.duels -- the endpoint wiring, status
codes, and response shapes. The pairing/concurrency logic itself is
covered directly against join_queue() in test_duels_matchmaking.py; these
confirm the API layer built on top of it behaves correctly for a single
real client.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.models import DifficultyEnum, Duel, DuelParticipant, DuelProblem, DuelQueueEntry


@pytest.fixture(autouse=True)
async def _clean_duel_queue(db_session):
    """Same reasoning as test_duels_matchmaking.py's fixture of the same
    name: the test DB is session-scoped and shares the fixed
    beginner/intermediate/advanced pools across every test file, so a
    leftover 'waiting' entry from another file's last test (or an earlier
    test in this one) must not leak into this test's expectations."""
    await db_session.execute(update(DuelQueueEntry).values(duel_id=None))
    await db_session.execute(DuelParticipant.__table__.delete())
    await db_session.execute(DuelQueueEntry.__table__.delete())
    await db_session.execute(Duel.__table__.delete())
    await db_session.commit()
    yield


class TestJoinQueue:
    async def test_first_join_waits(self, client: AsyncClient, test_user):
        response = await client.post(
            "/duels/queue", headers=test_user["headers"], json={"difficulty": "beginner"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "waiting"
        assert body["duel_id"] is None

    async def test_second_join_matches_the_first(self, client: AsyncClient, test_user, second_user):
        first = await client.post(
            "/duels/queue", headers=test_user["headers"], json={"difficulty": "beginner"}
        )
        second = await client.post(
            "/duels/queue", headers=second_user["headers"], json={"difficulty": "beginner"}
        )
        assert first.json()["status"] == "waiting"
        assert second.status_code == 200
        assert second.json()["status"] == "matched"
        assert second.json()["duel_id"] is not None

    async def test_joining_twice_while_waiting_is_a_409_not_a_crash(self, client: AsyncClient, test_user):
        first = await client.post(
            "/duels/queue", headers=test_user["headers"], json={"difficulty": "intermediate"}
        )
        assert first.status_code == 200
        again = await client.post(
            "/duels/queue", headers=test_user["headers"], json={"difficulty": "intermediate"}
        )
        assert again.status_code == 409

    async def test_unauthenticated_join_rejected(self, client: AsyncClient):
        response = await client.post("/duels/queue", json={"difficulty": "beginner"})
        assert response.status_code == 401

    async def test_a_pool_with_no_active_problems_returns_409(
        self, client: AsyncClient, test_user, db_session
    ):
        await db_session.execute(
            update(DuelProblem).where(DuelProblem.difficulty == DifficultyEnum.advanced).values(is_active=False)
        )
        await db_session.commit()

        response = await client.post(
            "/duels/queue", headers=test_user["headers"], json={"difficulty": "advanced"}
        )
        assert response.status_code == 409

        # Restore so other tests sharing this session-scoped DB aren't affected.
        await db_session.execute(
            update(DuelProblem).where(DuelProblem.difficulty == DifficultyEnum.advanced).values(is_active=True)
        )
        await db_session.commit()


class TestQueueStatus:
    async def test_idle_before_ever_joining(self, client: AsyncClient, second_user):
        response = await client.get("/duels/queue/status", headers=second_user["headers"])
        assert response.status_code == 200
        assert response.json()["status"] == "idle"

    async def test_reflects_waiting_then_matched(self, client: AsyncClient, test_user, second_user):
        await client.get("/duels/queue/status", headers=test_user["headers"])  # idle baseline, no side effect

        join = await client.post(
            "/duels/queue", headers=test_user["headers"], json={"difficulty": "beginner"}
        )
        assert join.json()["status"] == "waiting"

        status_while_waiting = await client.get("/duels/queue/status", headers=test_user["headers"])
        assert status_while_waiting.json()["status"] == "waiting"

        await client.post("/duels/queue", headers=second_user["headers"], json={"difficulty": "beginner"})

        status_after_match = await client.get("/duels/queue/status", headers=test_user["headers"])
        assert status_after_match.json()["status"] == "matched"
        assert status_after_match.json()["duel_id"] is not None

    async def test_unauthenticated_status_rejected(self, client: AsyncClient):
        response = await client.get("/duels/queue/status")
        assert response.status_code == 401


class TestCancelQueue:
    async def test_cancelling_a_waiting_entry_goes_back_to_idle(self, client: AsyncClient, test_user):
        await client.post("/duels/queue", headers=test_user["headers"], json={"difficulty": "intermediate"})

        cancel = await client.post("/duels/queue/cancel", headers=test_user["headers"])
        assert cancel.status_code == 200
        assert cancel.json()["status"] == "idle"

        status = await client.get("/duels/queue/status", headers=test_user["headers"])
        assert status.json()["status"] == "idle"

    async def test_cancelling_frees_the_user_to_join_again(self, client: AsyncClient, test_user):
        await client.post("/duels/queue", headers=test_user["headers"], json={"difficulty": "intermediate"})
        await client.post("/duels/queue/cancel", headers=test_user["headers"])

        rejoin = await client.post(
            "/duels/queue", headers=test_user["headers"], json={"difficulty": "intermediate"}
        )
        assert rejoin.status_code == 200
        assert rejoin.json()["status"] == "waiting"

    async def test_unauthenticated_cancel_rejected(self, client: AsyncClient):
        response = await client.post("/duels/queue/cancel")
        assert response.status_code == 401
