"""HTTP surface over app.services.duels -- the endpoint wiring, status
codes, and response shapes. The pairing/concurrency logic itself is
covered directly against join_queue() in test_duels_matchmaking.py; these
confirm the API layer built on top of it behaves correctly for a single
real client.
"""

import uuid

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
    from app.models import DuelSubmissionAttempt
    await db_session.execute(DuelSubmissionAttempt.__table__.delete())
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


async def _matched_duel_id(client: AsyncClient, test_user, second_user, difficulty="beginner") -> int:
    await client.post("/duels/queue", headers=test_user["headers"], json={"difficulty": difficulty})
    second = await client.post("/duels/queue", headers=second_user["headers"], json={"difficulty": difficulty})
    return second.json()["duel_id"]


class TestDuelTicket:
    async def test_a_participant_can_mint_a_ticket(self, client: AsyncClient, test_user, second_user):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        response = await client.post(f"/duels/{duel_id}/ticket", headers=test_user["headers"])
        assert response.status_code == 200
        assert response.json()["ticket"]

    async def test_unauthenticated_ticket_mint_rejected(self, client: AsyncClient, test_user, second_user):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        response = await client.post(f"/duels/{duel_id}/ticket")
        assert response.status_code == 401


class TestDuelState:
    async def test_shows_both_participants_and_the_shared_problem(
        self, client: AsyncClient, test_user, second_user
    ):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        response = await client.get(f"/duels/{duel_id}", headers=test_user["headers"])
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "active"
        assert body["problem_prompt"]
        assert body["me"]["username"] == test_user["data"]["username"]
        assert body["opponent"]["username"] == second_user["data"]["username"]
        assert body["me"]["passed_count"] == 0
        assert body["opponent"]["passed_count"] == 0

    async def test_a_non_participant_cannot_view_duel_state(
        self, client: AsyncClient, test_user, second_user
    ):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        suffix = f"outsiderstate{uuid.uuid4().hex[:8]}"
        reg = await client.post(
            "/auth/register",
            json={
                "email": f"{suffix}@example.com",
                "username": suffix,
                "password": "password123",
                "preferred_language": "en",
            },
        )
        headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
        response = await client.get(f"/duels/{duel_id}", headers=headers)
        assert response.status_code == 403

    async def test_unauthenticated_state_rejected(self, client: AsyncClient, test_user, second_user):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        response = await client.get(f"/duels/{duel_id}")
        assert response.status_code == 401


class TestDuelSubmit:
    async def test_wrong_submission_is_reported_without_winning(
        self, client: AsyncClient, test_user, second_user
    ):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        response = await client.post(
            f"/duels/{duel_id}/submit",
            headers=test_user["headers"],
            json={"code": "not a real solution"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_correct"] is False
        assert body["won"] is False
        assert body["duel_status"] == "active"

    async def test_a_non_participant_cannot_submit(self, client: AsyncClient, test_user, second_user):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        suffix = f"outsidersubmit{uuid.uuid4().hex[:8]}"
        reg = await client.post(
            "/auth/register",
            json={
                "email": f"{suffix}@example.com",
                "username": suffix,
                "password": "password123",
                "preferred_language": "en",
            },
        )
        headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
        response = await client.post(f"/duels/{duel_id}/submit", headers=headers, json={"code": "print(1)"})
        assert response.status_code == 403

    async def test_unauthenticated_submit_rejected(self, client: AsyncClient, test_user, second_user):
        duel_id = await _matched_duel_id(client, test_user, second_user)
        response = await client.post(f"/duels/{duel_id}/submit", json={"code": "print(1)"})
        assert response.status_code == 401
