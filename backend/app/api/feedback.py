"""Free-text bug reports / suggestions, reachable from Settings.

Submission is scoped to the requesting user when authenticated (user_id is
set from the token, never trusted from the request body) -- anonymous
submission is supported at the schema/DB level for a future logged-out
entry point, but every current entry point in the frontend requires being
signed in, so in practice every row today carries a user_id.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_user_optional
from app.db.session import get_db
from app.models import FeedbackSubmission, User
from app.schemas import FeedbackCreateRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


async def _submissions_this_hour(db: AsyncSession, user_id: int | None, ip_address: str | None) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=1)
    if user_id is not None:
        condition = FeedbackSubmission.user_id == user_id
    else:
        condition = FeedbackSubmission.ip_address == ip_address
    result = await db.execute(
        select(func.count(FeedbackSubmission.id)).where(
            condition,
            FeedbackSubmission.created_at >= cutoff,
        )
    )
    return result.scalar_one()


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def submit_feedback(
    payload: FeedbackCreateRequest,
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    sent_this_hour = await _submissions_this_hour(
        db, current_user.id if current_user else None, ip_address
    )
    if sent_this_hour >= get_settings().feedback_rate_limit_per_hour:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You've sent a lot of feedback recently. Please try again in a bit.",
        )

    db.add(
        FeedbackSubmission(
            user_id=current_user.id if current_user else None,
            category=payload.category,
            message=payload.message,
            page_path=payload.page_path,
            user_agent=request.headers.get("user-agent"),
            ip_address=ip_address,
        )
    )
    await db.commit()
    return None
