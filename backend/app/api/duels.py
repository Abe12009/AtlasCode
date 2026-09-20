"""Duel Arena endpoints: matchmaking, the WebSocket auth-ticket handshake,
the live duel connection, and submission/winner resolution.

Pairing lives in app.services.duels.join_queue, submission grading and
winner resolution in app.services.duels.submit_solution (the atomic-claim
logic for both) -- this module is the thin HTTP/WebSocket surface over
them. See app.services.duels' module docstring for the concurrency-safety
reasoning behind both, and app.services.duel_tickets / duel_realtime for
the WebSocket-specific auth and connection-registry pieces.
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import (
    Duel,
    DuelParticipant,
    DuelProblem,
    DuelQueueEntry,
    DuelQueueStatusEnum,
    DuelStatusEnum,
    Exercise,
    ExerciseTranslation,
    User,
)
from app.schemas import (
    DuelParticipantView,
    DuelQueueJoinRequest,
    DuelQueueStatusResponse,
    DuelStateResponse,
    DuelSubmitRequest,
    DuelSubmitResponse,
    DuelTicketResponse,
)
from app.services.duel_realtime import connection_manager
from app.services.duel_tickets import consume_ticket, mint_ticket
from app.services.duels import (
    AlreadyInQueue,
    DuelNotActive,
    NoDuelProblemAvailable,
    NotAParticipant,
    best_pass_counts,
    join_queue,
    submit_solution,
)

router = APIRouter(prefix="/duels", tags=["duels"])


@asynccontextmanager
async def _short_lived_db_session(websocket: WebSocket):
    """A fresh session for one DB operation inside the WebSocket handler,
    closed immediately after.

    `Depends(get_db)` is wrong here: FastAPI resolves a WebSocket route's
    dependencies once at connect time and holds them for the connection's
    entire lifetime, so a `db: AsyncSession = Depends(get_db)` parameter
    would tie up one pooled connection for the whole duel even though the
    receive loop between connect and disconnect does no DB work at all --
    with the pool's default size, on the order of a few dozen concurrent
    open duels would exhaust it and start starving every other request.

    Looks up the app's current `get_db` override (falling back to the real
    one) so tests that override `get_db` still get the isolated test
    session -- this mirrors what `Depends(get_db)` itself does under the
    hood, just invoked by hand, and repeatably, instead of once.
    """
    db_dependency = websocket.app.dependency_overrides.get(get_db, get_db)
    agen = db_dependency()
    session = await agen.__anext__()
    try:
        yield session
    finally:
        await agen.aclose()


@router.post("/queue", response_model=DuelQueueStatusResponse)
async def join_duel_queue(
    request: DuelQueueJoinRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await join_queue(db, current_user.id, request.difficulty)
    except NoDuelProblemAvailable:
        raise HTTPException(
            status_code=409,
            detail=f"No duel problems are available yet for difficulty={request.difficulty.value}.",
        )
    except AlreadyInQueue:
        raise HTTPException(status_code=409, detail="You're already in the queue.")

    return DuelQueueStatusResponse(status=result.status, duel_id=result.duel_id)


@router.get("/queue/status", response_model=DuelQueueStatusResponse)
async def get_duel_queue_status(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Polled by a client sitting in the queue (see the Step 4 architecture:
    polling here, not a WebSocket, since queue-wait latency isn't the part
    that needs to feel instant -- only the live duel itself does)."""
    result = await db.execute(
        select(DuelQueueEntry)
        .where(DuelQueueEntry.user_id == current_user.id)
        .order_by(DuelQueueEntry.joined_at.desc())
        .limit(1)
    )
    entry = result.scalar_one_or_none()

    if entry is None or entry.status == DuelQueueStatusEnum.cancelled:
        return DuelQueueStatusResponse(status="idle")
    if entry.status == DuelQueueStatusEnum.matched:
        return DuelQueueStatusResponse(status="matched", duel_id=entry.duel_id)
    return DuelQueueStatusResponse(status="waiting")


@router.post("/queue/cancel", response_model=DuelQueueStatusResponse)
async def cancel_duel_queue(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Leaves the queue. Only affects a still-'waiting' entry -- once
    matched, leaving is a duel-forfeit concern (the WebSocket/real-time
    step), not a queue concern."""
    await db.execute(
        update(DuelQueueEntry)
        .where(
            DuelQueueEntry.user_id == current_user.id,
            DuelQueueEntry.status == DuelQueueStatusEnum.waiting,
        )
        .values(status=DuelQueueStatusEnum.cancelled)
    )
    await db.commit()
    return DuelQueueStatusResponse(status="idle")


async def _get_participant_or_403(db: AsyncSession, duel_id: int, user_id: int) -> DuelParticipant:
    participant = (
        await db.execute(
            select(DuelParticipant).where(
                DuelParticipant.duel_id == duel_id, DuelParticipant.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if participant is None:
        raise HTTPException(status_code=403, detail="You're not a participant of this duel.")
    return participant


@router.post("/{duel_id}/ticket", response_model=DuelTicketResponse)
async def mint_duel_ticket(
    duel_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mints the short-lived, single-use ticket the client exchanges for a
    WebSocket connection -- see app.services.duel_tickets. An ordinary
    authenticated REST call, so it goes through the normal Authorization
    header, unlike the WebSocket upgrade that follows it."""
    await _get_participant_or_403(db, duel_id, current_user.id)
    return DuelTicketResponse(ticket=mint_ticket(current_user.id, duel_id))


@router.get("/{duel_id}", response_model=DuelStateResponse)
async def get_duel_state(
    duel_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Full current state -- used for the initial page load and for a
    reconnecting client's resync before it re-attaches its WebSocket (see
    the Step 4 architecture: never trust the socket alone to have carried
    every state change while it was closed)."""
    duel = await db.get(Duel, duel_id)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel not found.")

    me_participant = await _get_participant_or_403(db, duel_id, current_user.id)
    opponent_participant = (
        await db.execute(
            select(DuelParticipant).where(
                DuelParticipant.duel_id == duel_id, DuelParticipant.user_id != current_user.id
            )
        )
    ).scalar_one()

    duel_problem = await db.get(DuelProblem, duel.duel_problem_id)
    exercise = await db.get(Exercise, duel_problem.exercise_id)
    translation = (
        await db.execute(
            select(ExerciseTranslation).where(
                ExerciseTranslation.exercise_id == exercise.id,
                ExerciseTranslation.language == current_user.preferred_language,
            )
        )
    ).scalar_one_or_none()

    me_user = await db.get(User, current_user.id)
    opponent_user = await db.get(User, opponent_participant.user_id)
    me_passed, me_total = await best_pass_counts(db, duel_id, current_user.id)
    opp_passed, opp_total = await best_pass_counts(db, duel_id, opponent_participant.user_id)

    return DuelStateResponse(
        id=duel.id,
        status=duel.status.value,
        started_at=duel.started_at,
        ends_at=duel.ends_at,
        ended_at=duel.ended_at,
        winner_user_id=duel.winner_user_id,
        problem_prompt=translation.prompt if translation else "",
        problem_starter_code=exercise.starter_code,
        me=DuelParticipantView(
            user_id=me_user.id,
            username=me_user.username,
            is_connected=connection_manager.is_connected(duel_id, me_user.id),
            passed_count=me_passed,
            total_count=me_total,
        ),
        opponent=DuelParticipantView(
            user_id=opponent_user.id,
            username=opponent_user.username,
            is_connected=connection_manager.is_connected(duel_id, opponent_user.id),
            passed_count=opp_passed,
            total_count=opp_total,
        ),
    )


@router.post("/{duel_id}/submit", response_model=DuelSubmitResponse)
async def submit_duel_solution(
    duel_id: int,
    request: DuelSubmitRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await submit_solution(db, duel_id, current_user.id, request.code)
    except NotAParticipant:
        raise HTTPException(status_code=403, detail="You're not a participant of this duel.")
    except DuelNotActive:
        raise HTTPException(status_code=409, detail="This duel is no longer active.")

    # Push to the opponent, never the submitter's own code -- see
    # duel_realtime's module docstring. The submitter gets their own full
    # result back in this very response; they don't need the broadcast.
    if result.won:
        await connection_manager.broadcast_to_all(
            duel_id,
            {"type": "duel_ended", "winner_user_id": current_user.id, "reason": "solved"},
        )
    elif result.duel_status == DuelStatusEnum.active.value:
        # Only push a progress update while the duel is still genuinely
        # live -- a correct-but-too-late or post-timeout submission has
        # nothing new to tell an opponent who already knows it's over.
        await connection_manager.broadcast_to_opponent(
            duel_id,
            current_user.id,
            {
                "type": "opponent_progress",
                "passed_count": result.passed_count,
                "total_count": result.total_count,
            },
        )

    return DuelSubmitResponse(
        is_correct=result.is_correct,
        passed_count=result.passed_count,
        total_count=result.total_count,
        won=result.won,
        duel_status=result.duel_status,
        winner_user_id=result.winner_user_id,
    )


@router.websocket("/ws/{duel_id}")
async def duel_websocket(
    websocket: WebSocket,
    duel_id: int,
    ticket: str,
):
    """The live channel: after connecting, a client only ever RECEIVES
    application messages (opponent_progress / opponent_connected /
    opponent_disconnected / duel_ended) -- submissions go through the
    ordinary POST /duels/{id}/submit above, not this socket, so there's no
    inbound message format to parse or validate here. The receive loop
    below exists purely to detect the client closing the connection.

    No `db: AsyncSession = Depends(get_db)` parameter here on purpose --
    see _short_lived_db_session's docstring. Each of the two DB operations
    below (connect, disconnect) opens and closes its own session instead of
    holding one pooled connection for the whole duel."""
    user_id = consume_ticket(ticket, duel_id)
    if user_id is None:
        await websocket.close(code=4401)
        return

    async with _short_lived_db_session(websocket) as db:
        participant = (
            await db.execute(
                select(DuelParticipant).where(
                    DuelParticipant.duel_id == duel_id, DuelParticipant.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        if participant is None:
            await websocket.close(code=4403)
            return

        await connection_manager.connect(duel_id, user_id, websocket)
        participant.is_connected = True
        participant.disconnected_at = None
        await db.commit()
    await connection_manager.broadcast_to_opponent(duel_id, user_id, {"type": "opponent_connected"})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(duel_id, user_id)
        # A fresh session again: the `participant` object above belongs to
        # a session that's already been closed, so it can't be reused to
        # persist a change here -- re-fetch it in this session instead.
        async with _short_lived_db_session(websocket) as db:
            participant = (
                await db.execute(
                    select(DuelParticipant).where(
                        DuelParticipant.duel_id == duel_id, DuelParticipant.user_id == user_id
                    )
                )
            ).scalar_one_or_none()
            if participant is not None:
                participant.is_connected = False
                participant.disconnected_at = datetime.utcnow()
                await db.commit()
        await connection_manager.broadcast_to_opponent(duel_id, user_id, {"type": "opponent_disconnected"})
