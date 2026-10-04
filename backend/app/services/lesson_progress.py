from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.compat import conflict_insert
from app.models import LessonProgress, MissionStatusEnum


async def get_or_create_lesson_progress(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
    initial_status: MissionStatusEnum,
    *,
    commit: bool = True,
) -> LessonProgress:
    """Idempotently obtain this user's progress row for a lesson.

    A plain "select, then insert if missing" races: two concurrent requests can
    both see no row and both insert, and the loser fails the uq_user_lesson
    constraint with a 500. Letting the database resolve the conflict instead
    makes the loser's insert a no-op, so both requests read back the same
    single row. An existing row is never modified here.

    Lives here rather than in `app/api/lessons.py` because `exercises.py`
    needs it too (exercise submission creates the row it completes), and an
    API module importing another API module's private helper is the wrong
    direction for that dependency.

    `commit=False` leaves the insert pending in the caller's transaction.
    Exercise submission needs that: it builds an attempt row, XP, a streak
    update and a notification into one atomic commit at the end of the
    handler, and committing here instead would split that in two. A failure
    after the split would leave the XP awarded but the lesson not completed,
    and a retry would then see `previous_success` and skip the completion
    block for good -- the precise half-done state this whole change exists to
    remove. Endpoints that call this with nothing else pending (lesson
    `/start`, `/progress`) keep the default and commit here.
    """
    stmt = (
        conflict_insert(LessonProgress)
        .values(user_id=user_id, lesson_id=lesson_id, status=initial_status)
        .on_conflict_do_nothing(index_elements=["user_id", "lesson_id"])
    )
    await db.execute(stmt)
    if commit:
        await db.commit()
    else:
        # Make the row readable by the select below without ending the
        # caller's transaction.
        await db.flush()

    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    return result.scalar_one()
