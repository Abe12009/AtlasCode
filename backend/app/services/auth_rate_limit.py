"""Rate limiting for /auth/login and /auth/register -- both reachable with
no account and no session, the same reason app.services.password_reset
counts rows in a table rather than a per-user counter.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import AuthAttempt


async def check_and_log_login_rate_limit(
    db: AsyncSession, email: str, ip_address: str | None
) -> bool:
    """Log this attempt, then report whether the email or IP is over its
    hourly limit. Logging happens before the check, and for every email
    (real or not), so the counters look identical whether or not an account
    exists -- the rate limit itself must never become an enumeration oracle.
    """
    settings = get_settings()
    db.add(AuthAttempt(kind="login", email=email, ip_address=ip_address))
    await db.flush()

    cutoff = datetime.utcnow() - timedelta(hours=1)

    email_count = await db.scalar(
        select(func.count(AuthAttempt.id)).where(
            AuthAttempt.kind == "login",
            AuthAttempt.email == email,
            AuthAttempt.created_at >= cutoff,
        )
    )
    if email_count > settings.auth_login_rate_limit_per_email_per_hour:
        return False

    if ip_address:
        ip_count = await db.scalar(
            select(func.count(AuthAttempt.id)).where(
                AuthAttempt.kind == "login",
                AuthAttempt.ip_address == ip_address,
                AuthAttempt.created_at >= cutoff,
            )
        )
        if ip_count > settings.auth_login_rate_limit_per_ip_per_hour:
            return False

    return True


async def check_and_log_register_rate_limit(
    db: AsyncSession, email: str, ip_address: str | None
) -> bool:
    """Per-IP only: email uniqueness already stops the same address from
    registering twice, so the thing worth capping is one IP creating many
    accounts, not one email being attempted repeatedly.
    """
    settings = get_settings()
    db.add(AuthAttempt(kind="register", email=email, ip_address=ip_address))
    await db.flush()

    if not ip_address:
        return True

    cutoff = datetime.utcnow() - timedelta(hours=1)
    ip_count = await db.scalar(
        select(func.count(AuthAttempt.id)).where(
            AuthAttempt.kind == "register",
            AuthAttempt.ip_address == ip_address,
            AuthAttempt.created_at >= cutoff,
        )
    )
    return ip_count <= settings.auth_register_rate_limit_per_ip_per_hour
