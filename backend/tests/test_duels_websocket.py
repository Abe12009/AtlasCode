"""Duel Arena WebSocket layer: the auth-ticket handshake and the live
connection itself.

Explicit focus per review feedback: verify the ticket flow end-to-end --
mint via REST, connect with it, and confirm a stale/reused/missing/
wrong-duel ticket is rejected cleanly, not just the happy path. See
tests/conftest.py's `duel_ws` fixture docstring for why this uses
httpx-ws rather than starlette's own TestClient (a pinned-version
incompatibility in this environment, not a design choice).
"""

import asyncio
import uuid

import pytest
from httpx import AsyncClient
from httpx_ws import WebSocketDisconnect
from sqlalchemy import select, update

from app.models import Duel, DuelParticipant, DuelProblem, DuelQueueEntry, Exercise, User
from app.services.duel_tickets import mint_ticket


async def _rejected_close_code(connect_cm) -> int:
    """Attempts a WebSocket connection expected to be rejected, returning
    the close code. httpx-ws's ASGIWebSocketTransport propagates the
    rejection as a bare WebSocketDisconnect in some call shapes and as an
    ExceptionGroup wrapping one in others (an anyio task-group boundary
    detail, not something these tests should need to know the shape of) --
    this normalizes both so every rejection test can assert on a plain
    close code."""
    try:
        async with connect_cm as ws:
            pytest.fail("connection succeeded; expected it to be rejected")
    except WebSocketDisconnect as e:
        return e.code
    except BaseException as e:
        if hasattr(e, "exceptions"):
            for sub in e.exceptions:  # type: ignore[attr-defined]
                if isinstance(sub, WebSocketDisconnect):
                    return sub.code
        raise


@pytest.fixture(autouse=True)
async def _clean_duel_state(db_session):
    await db_session.execute(update(DuelQueueEntry).values(duel_id=None))
    await db_session.execute(DuelParticipant.__table__.delete())
    await db_session.execute(DuelQueueEntry.__table__.delete())
    from app.models import DuelSubmissionAttempt
    await db_session.execute(DuelSubmissionAttempt.__table__.delete())
    await db_session.execute(Duel.__table__.delete())
    await db_session.commit()
    yield


async def _matched_duel(client: AsyncClient, test_user, second_user, difficulty="beginner"):
    await client.post("/duels/queue", headers=test_user["headers"], json={"difficulty": difficulty})
    second = await client.post(
        "/duels/queue", headers=second_user["headers"], json={"difficulty": difficulty}
    )
    return second.json()["duel_id"]


async def _reference_solution(db_session, duel_id: int) -> str:
    duel = await db_session.get(Duel, duel_id)
    duel_problem = await db_session.get(DuelProblem, duel.duel_problem_id)
    exercise = await db_session.get(Exercise, duel_problem.exercise_id)
    return exercise.solution_code


class TestTicketHandshakeHappyPath:
    async def test_mint_then_connect_succeeds(self, client: AsyncClient, duel_ws, test_user, second_user):
        duel_id = await _matched_duel(client, test_user, second_user)

        ticket_response = await client.post(f"/duels/{duel_id}/ticket", headers=test_user["headers"])
        assert ticket_response.status_code == 200
        ticket = ticket_response.json()["ticket"]

        async with duel_ws(f"/duels/ws/{duel_id}?ticket={ticket}") as ws:
            # A successful accept() is the assertion itself -- reaching this
            # line without WebSocketDisconnect means the handshake worked.
            pass

    async def test_a_connected_socket_receives_the_opponents_progress_broadcast(
        self, client: AsyncClient, duel_ws, test_user, second_user, db_session
    ):
        duel_id = await _matched_duel(client, test_user, second_user)

        ticket_response = await client.post(f"/duels/{duel_id}/ticket", headers=test_user["headers"])
        ticket = ticket_response.json()["ticket"]

        async with duel_ws(f"/duels/ws/{duel_id}?ticket={ticket}") as ws:
            # second_user (the opponent from test_user's point of view)
            # submits a wrong solution -- test_user's socket should be
            # pushed a progress update, never the code itself.
            await client.post(
                f"/duels/{duel_id}/submit",
                headers=second_user["headers"],
                json={"code": "this is not a real solution"},
            )
            message = await ws.receive_json()
            assert message["type"] == "opponent_progress"
            assert "passed_count" in message and "total_count" in message
            assert "code" not in message


class TestTicketRejection:
    async def test_missing_ticket_is_rejected(self, client: AsyncClient, duel_ws, test_user, second_user):
        duel_id = await _matched_duel(client, test_user, second_user)
        # No `ticket` query param at all -- FastAPI's own required-param
        # validation rejects this before the handler ever runs, a
        # different failure mode than the others (a 4xx-style handshake
        # rejection, not our close(code=4401)) but still a clean refusal.
        with pytest.raises(Exception):
            async with duel_ws(f"/duels/ws/{duel_id}") as ws:
                pass

    async def test_garbage_ticket_is_rejected_with_the_auth_close_code(
        self, client: AsyncClient, duel_ws, test_user, second_user
    ):
        duel_id = await _matched_duel(client, test_user, second_user)
        code = await _rejected_close_code(duel_ws(f"/duels/ws/{duel_id}?ticket=not-a-real-ticket"))
        assert code == 4401

    async def test_a_ticket_cannot_be_reused_after_a_successful_connection(
        self, client: AsyncClient, duel_ws, test_user, second_user
    ):
        duel_id = await _matched_duel(client, test_user, second_user)
        ticket = (await client.post(f"/duels/{duel_id}/ticket", headers=test_user["headers"])).json()["ticket"]

        async with duel_ws(f"/duels/ws/{duel_id}?ticket={ticket}") as ws:
            pass  # first use succeeds and consumes the ticket

        code = await _rejected_close_code(duel_ws(f"/duels/ws/{duel_id}?ticket={ticket}"))
        assert code == 4401

    async def test_an_expired_ticket_is_rejected(
        self, client: AsyncClient, duel_ws, test_user, second_user, monkeypatch
    ):
        import app.services.duel_tickets as duel_tickets_module

        monkeypatch.setattr(duel_tickets_module, "TICKET_TTL_SECONDS", 0.01)
        duel_id = await _matched_duel(client, test_user, second_user)
        ticket = (await client.post(f"/duels/{duel_id}/ticket", headers=test_user["headers"])).json()["ticket"]

        import asyncio
        await asyncio.sleep(0.05)  # let it expire

        code = await _rejected_close_code(duel_ws(f"/duels/ws/{duel_id}?ticket={ticket}"))
        assert code == 4401

    async def test_a_ticket_minted_for_one_duel_does_not_work_for_another(
        self, client: AsyncClient, duel_ws, test_user, second_user, db_session
    ):
        duel_id = await _matched_duel(client, test_user, second_user)
        ticket = (await client.post(f"/duels/{duel_id}/ticket", headers=test_user["headers"])).json()["ticket"]

        # A second, unrelated duel the ticket was never minted for.
        suffix = uuid.uuid4().hex[:10]
        third = User(email=f"third_{suffix}@example.com", username=f"third_{suffix}")
        fourth = User(email=f"fourth_{suffix}@example.com", username=f"fourth_{suffix}")
        db_session.add_all([third, fourth])
        await db_session.commit()
        from app.services.duels import join_queue
        from app.models import DifficultyEnum
        await join_queue(db_session, third.id, DifficultyEnum.intermediate)
        other_result = await join_queue(db_session, fourth.id, DifficultyEnum.intermediate)
        other_duel_id = other_result.duel_id

        code = await _rejected_close_code(duel_ws(f"/duels/ws/{other_duel_id}?ticket={ticket}"))
        assert code == 4401

    async def test_mint_endpoint_refuses_a_non_participant(
        self, client: AsyncClient, test_user, second_user
    ):
        duel_id = await _matched_duel(client, test_user, second_user)
        suffix = uuid.uuid4().hex[:8]
        outsider_reg = await client.post(
            "/auth/register",
            json={
                "email": f"outsider_{suffix}@example.com",
                "username": f"outsider_{suffix}",
                "password": "password123",
                "preferred_language": "en",
            },
        )
        outsider_headers = {"Authorization": f"Bearer {outsider_reg.json()['access_token']}"}

        response = await client.post(f"/duels/{duel_id}/ticket", headers=outsider_headers)
        assert response.status_code == 403

    async def test_websocket_itself_refuses_a_non_participant_even_with_a_raw_ticket(
        self, client: AsyncClient, duel_ws, test_user, second_user, db_session
    ):
        """Defense in depth: even if a valid-shaped ticket existed for a
        non-participant (bypassing the mint endpoint's own check, simulated
        here by calling mint_ticket directly), the WebSocket handler's own
        participant check must still refuse the connection."""
        duel_id = await _matched_duel(client, test_user, second_user)

        suffix = uuid.uuid4().hex[:10]
        outsider = User(email=f"outsider2_{suffix}@example.com", username=f"outsider2_{suffix}")
        db_session.add(outsider)
        await db_session.commit()
        await db_session.refresh(outsider)

        raw_ticket = mint_ticket(outsider.id, duel_id)

        code = await _rejected_close_code(duel_ws(f"/duels/ws/{duel_id}?ticket={raw_ticket}"))
        assert code == 4403


class TestConnectionLifecycle:
    async def test_disconnecting_marks_participant_disconnected_and_notifies_opponent(
        self, client: AsyncClient, duel_ws, test_user, second_user, db_session
    ):
        """Two sockets need to be open at once here (b has to be listening
        when a connects, and still listening when a disconnects), but the
        duel_ws fixture's connect() is only safe when each call's anyio
        task group opens and closes within a single task of its own (see
        the fixture's docstring) -- nesting two `async with duel_ws(...)`
        blocks in one task hits that same cross-scope conflict from the
        opposite direction. Running b and a as two concurrent asyncio
        tasks via gather keeps each connect() self-contained in its own
        task while still overlapping in wall-clock time."""
        duel_id = await _matched_duel(client, test_user, second_user)
        ticket_a = (await client.post(f"/duels/{duel_id}/ticket", headers=test_user["headers"])).json()["ticket"]
        ticket_b = (await client.post(f"/duels/{duel_id}/ticket", headers=second_user["headers"])).json()["ticket"]

        b_ready = asyncio.Event()
        messages = {}

        async def run_b():
            async with duel_ws(f"/duels/ws/{duel_id}?ticket={ticket_b}") as ws_b:
                b_ready.set()
                messages["connected"] = await ws_b.receive_json()
                messages["disconnected"] = await ws_b.receive_json()

        async def run_a():
            await b_ready.wait()
            async with duel_ws(f"/duels/ws/{duel_id}?ticket={ticket_a}") as ws_a:
                pass  # connect, then close immediately by exiting the block

        await asyncio.gather(run_b(), run_a())

        assert messages["connected"]["type"] == "opponent_connected"
        assert messages["disconnected"]["type"] == "opponent_disconnected"

        user_a = (
            await db_session.execute(select(User).where(User.username == test_user["data"]["username"]))
        ).scalar_one()
        participant_a = (
            await db_session.execute(
                select(DuelParticipant).where(
                    DuelParticipant.duel_id == duel_id, DuelParticipant.user_id == user_a.id
                )
            )
        ).scalar_one()
        assert participant_a.is_connected is False
        assert participant_a.disconnected_at is not None


class TestDuelEndedBroadcast:
    async def test_a_winning_submission_broadcasts_duel_ended_to_the_opponents_socket(
        self, client: AsyncClient, duel_ws, test_user, second_user, db_session
    ):
        duel_id = await _matched_duel(client, test_user, second_user)
        ticket_b = (await client.post(f"/duels/{duel_id}/ticket", headers=second_user["headers"])).json()["ticket"]
        solution = await _reference_solution(db_session, duel_id)

        async with duel_ws(f"/duels/ws/{duel_id}?ticket={ticket_b}") as ws_b:
            submit_response = await client.post(
                f"/duels/{duel_id}/submit", headers=test_user["headers"], json={"code": solution}
            )
            assert submit_response.status_code == 200
            assert submit_response.json()["won"] is True

            message = await ws_b.receive_json()
            assert message["type"] == "duel_ended"
            assert message["reason"] == "solved"
            assert message["winner_user_id"] == submit_response.json()["winner_user_id"]
