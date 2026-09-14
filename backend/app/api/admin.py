"""Minimal moderation endpoints for staff accounts.

No admin UI yet -- these are protected backend endpoints a staff member
calls directly (curl/Postman/a script) until a UI is worth building. Every
route is gated by `get_current_staff_user`, which 404s (not 403) for a
non-staff account so the existence of the admin surface isn't disclosed to
someone probing for it.

Becoming staff has no signup flow: `UPDATE users SET is_staff = TRUE WHERE
id = <you>` directly against the database, the same "first admin" pattern
this project already uses for anything with no dedicated onboarding.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_staff_user
from app.db.session import get_db
from app.models import CodyMessage, FeedbackSubmission, Report, ReportStatusEnum, User
from app.schemas import CodySpendResponse, FeedbackResponse, ReportResolveRequest, ReportResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/reports", response_model=list[ReportResponse])
async def list_reports(
    report_status: ReportStatusEnum = Query(ReportStatusEnum.open, alias="status"),
    current_staff: User = Depends(get_current_staff_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report).where(Report.status == report_status).order_by(Report.created_at.desc())
    )
    return result.scalars().all()


@router.post("/reports/{report_id}/resolve", response_model=ReportResponse)
async def resolve_report(
    report_id: int,
    payload: ReportResolveRequest,
    current_staff: User = Depends(get_current_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Marks a report resolved with a note of what was done about it.

    Deliberately decoupled from actually suspending/reinstating/clearing an
    avatar -- those are separate endpoints below, so resolving a report
    doesn't have to imply exactly one specific action; a staff member picks
    whichever of them (if any) actually applies, then resolves the report
    with a note explaining the outcome.
    """
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = ReportStatusEnum.resolved
    report.resolution_note = payload.resolution_note
    report.resolved_by_user_id = current_staff.id
    report.resolved_at = datetime.utcnow()
    await db.commit()
    await db.refresh(report)
    return report


@router.post("/users/{user_id}/suspend", status_code=status.HTTP_204_NO_CONTENT)
async def suspend_user(
    user_id: int,
    current_staff: User = Depends(get_current_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Sets is_active=False. Every authenticated request from this account
    -- including one already carrying a valid, unexpired token -- then 403s
    at get_current_user, immediately and without the user needing to sign
    in again for it to take effect."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    return None


@router.post("/users/{user_id}/reinstate", status_code=status.HTTP_204_NO_CONTENT)
async def reinstate_user(
    user_id: int,
    current_staff: User = Depends(get_current_staff_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    await db.commit()
    return None


@router.post("/users/{user_id}/clear-avatar", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_avatar(
    user_id: int,
    current_staff: User = Depends(get_current_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Removes an uploaded photo, a federated provider photo, and a built
    cartoon avatar, resetting to the model's own default state."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.avatar_image_data = None
    user.avatar_url = None
    user.avatar_config = None
    user.avatar_type = "upload"
    await db.commit()
    return None


@router.get("/cody-spend", response_model=CodySpendResponse)
async def cody_spend(
    current_staff: User = Depends(get_current_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Aggregate Cody spend across all users, from OpenRouter's own
    per-call cost accounting (see app.services.cody.get_reply). Rows from
    before spend tracking shipped have a NULL estimated_cost_usd and are
    excluded, not counted as zero, so historical windows aren't understated
    silently."""
    now = datetime.utcnow()

    async def _sum_since(cutoff: datetime) -> float:
        result = await db.execute(
            select(func.coalesce(func.sum(CodyMessage.estimated_cost_usd), 0.0)).where(
                CodyMessage.created_at >= cutoff,
                CodyMessage.estimated_cost_usd.isnot(None),
            )
        )
        return result.scalar_one()

    return CodySpendResponse(
        spend_usd_last_24h=await _sum_since(now - timedelta(hours=24)),
        spend_usd_last_7d=await _sum_since(now - timedelta(days=7)),
        spend_usd_last_30d=await _sum_since(now - timedelta(days=30)),
        daily_cap_usd=get_settings().cody_daily_spend_cap_usd,
    )


@router.get("/feedback", response_model=list[FeedbackResponse])
async def list_feedback(
    current_staff: User = Depends(get_current_staff_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FeedbackSubmission).order_by(FeedbackSubmission.created_at.desc())
    )
    return result.scalars().all()
