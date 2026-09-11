from datetime import datetime, timedelta

import logging

import httpx
from openrouter import errors as openrouter_errors
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import CodyMessage, CodyRoleEnum, User
from app.schemas import CodyChatRequest, CodyChatResponse, CodyMessageResponse
from app.services.cody import CodyNotConfiguredError, get_reply

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cody", tags=["cody"])


async def _messages_sent_this_hour(db: AsyncSession, user_id: int) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(func.count(CodyMessage.id)).where(
            CodyMessage.user_id == user_id,
            CodyMessage.role == CodyRoleEnum.user,
            CodyMessage.created_at >= cutoff,
        )
    )
    return result.scalar_one()


@router.post("/chat", response_model=CodyChatResponse)
async def chat(
    payload: CodyChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cody isn't configured on this server yet.",
        )

    sent_this_hour = await _messages_sent_this_hour(db, current_user.id)
    if sent_this_hour >= settings.cody_rate_limit_per_hour:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "You've hit Cody's hourly message limit. "
                "Take a short break and try again in a bit."
            ),
        )

    history_result = await db.execute(
        select(CodyMessage)
        .where(CodyMessage.user_id == current_user.id)
        .order_by(CodyMessage.created_at.desc())
        .limit(settings.cody_history_context_size)
    )
    # Fetched newest-first for the LIMIT to bite the right end; the model
    # needs them back in chronological order.
    history = list(reversed(history_result.scalars().all()))

    user_message = CodyMessage(
        user_id=current_user.id,
        role=CodyRoleEnum.user,
        content=payload.message,
    )
    db.add(user_message)

    try:
        reply = await get_reply(db, current_user, history, payload.message)
    except CodyNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cody isn't configured on this server yet.",
        )
    except (
        openrouter_errors.OpenRouterError,
        openrouter_errors.NoResponseError,
        httpx.HTTPError,
    ):
        # Never leak the provider's raw error (could include request
        # internals) to the client -- log it server-side and hand back a
        # generic, friendly failure instead. OpenRouterError covers HTTP
        # error-status responses (bad gateway, rate limit, auth, etc.) and
        # response-validation failures; NoResponseError and httpx.HTTPError
        # cover network-level failures (timeouts, connection errors), which
        # the SDK's own HTTP layer doesn't wrap -- it lets them propagate as
        # raw httpx exceptions.
        logger.exception("Cody: OpenRouter API call failed for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cody is having trouble answering right now. Please try again shortly.",
        )

    assistant_message = CodyMessage(
        user_id=current_user.id,
        role=CodyRoleEnum.assistant,
        content=reply.content,
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return CodyChatResponse(
        reply=CodyMessageResponse.model_validate(assistant_message),
        messages_remaining_this_hour=max(
            0, settings.cody_rate_limit_per_hour - sent_this_hour - 1
        ),
    )


@router.get("/messages", response_model=list[CodyMessageResponse])
async def list_messages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CodyMessage)
        .where(CodyMessage.user_id == current_user.id)
        .order_by(CodyMessage.created_at.asc())
    )
    return result.scalars().all()
