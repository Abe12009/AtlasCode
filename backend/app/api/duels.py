"""Duel Arena endpoints: matchmaking (queue join/status/cancel).

Pairing lives in app.services.duels.join_queue (the atomic-claim logic) --
this module is the thin HTTP surface over it. See app.services.duels'
module docstring for the concurrency-safety reasoning.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import DuelQueueEntry, DuelQueueStatusEnum
from app.schemas import DuelQueueJoinRequest, DuelQueueStatusResponse
from app.services.duels import AlreadyInQueue, NoDuelProblemAvailable, join_queue

router = APIRouter(prefix="/duels", tags=["duels"])


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
