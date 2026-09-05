import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, NotificationTypeEnum


async def create_notification(
    db: AsyncSession,
    user_id: int,
    type: NotificationTypeEnum,
    data: Optional[dict] = None,
) -> Notification:
    """Create a notification. Does not commit — caller controls the transaction
    boundary so this can be created in the same commit as the event that caused it."""
    notification = Notification(
        user_id=user_id,
        type=type,
        data=json.dumps(data) if data else None,
    )
    db.add(notification)
    return notification
