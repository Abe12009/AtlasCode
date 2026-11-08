"""All-time XP leaderboard.

Opt-in by construction: a user appears only while `users.profile_visibility`
is "public", which defaults to "private" (see app/db/migrations.py) and is
changed by the student themselves through PATCH /auth/me. There is no
separate leaderboard flag to keep in sync -- the same switch that makes a
profile viewable is the one that lists it here, so a student can never be
surprised to find themselves ranked on a page they never opted into.

What a row carries is a strict subset of what GET /users/{username} already
shows for the same account: username, avatar, level, XP. Never an email, a
real name, a streak or a join date.
"""

import base64
import binascii
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Integer, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import StudentProfile, User
from app.schemas import LeaderboardEntry, LeaderboardMe, LeaderboardResponse

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

#: How far down the board anyone may page. Rank 500 is already far past the
#: point where a position means anything to the person holding it, and the
#: cap is what stops the keyset walk from becoming an unbounded crawl of the
#: whole user table. `me.rank` is exact regardless -- it is one COUNT, not a
#: walk -- so a student ranked 900th still sees 900.
MAX_DEPTH = 500

DEFAULT_LIMIT = 25
MAX_LIMIT = 100

#: Longest cursor accepted. A real one is ~20 characters; this only has to be
#: generous enough never to reject one while refusing a payload built to be
#: expensive to decode. Enforced by FastAPI (422) before any decoding runs.
MAX_CURSOR_LENGTH = 128

#: Every integer in a cursor must fit a signed 64-bit column. Python ints are
#: arbitrary precision, so without this a cursor carrying 10**400 reaches the
#: database: SQLite shrugs, but PostgreSQL rejects an out-of-range bigint and
#: the request becomes a 500 instead of the 400 it is.
INT64_MAX = 2**63 - 1


def _sort_xp():
    """The ordering key: XP, with NULL strictly last.

    `student_profiles.xp` is nullable (`Column(Integer, default=0)` applies
    only to rows this app inserts), and the two databases disagree about
    where NULLs land: SQLite sorts them as the smallest value, PostgreSQL
    puts them first on a DESC sort. Coalescing to -1 settles it in one place
    for both, and keeps the keyset comparison below plain integer arithmetic
    instead of three-valued logic.

    -1 is safe as the sentinel because XP only ever increases -- nothing in
    the codebase subtracts from it -- so no real profile can collide with it.
    """
    return func.coalesce(StudentProfile.xp, -1)


def _listed():
    """Who appears on the board at all.

    Public *and* active: a suspended account keeps its XP but stops being
    shown, the same rule the rest of the app applies to a disabled user.
    """
    return and_(User.profile_visibility == "public", User.is_active.is_(True))


def _encode_cursor(sort_xp: int, user_id: int, next_rank: int) -> str:
    """Opaque continuation token: where to resume, and at what rank.

    The rank travels in the cursor because keyset pagination has no OFFSET to
    count from -- page 2 has to be told it starts at 26, or every page would
    restart its numbering at 1.
    """
    raw = f"{sort_xp}:{user_id}:{next_rank}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(cursor: str) -> tuple[int, int, int]:
    """Parse a cursor, or 400. Never trusted: it arrives from the client.

    Every failure mode lands on one 400: not base64, not UTF-8, the wrong
    number of fields, not integers, or integers outside the range a real
    cursor can hold. The range check is the load-bearing one -- the rest
    would raise on their own, but a syntactically perfect cursor saying
    "resume at rank -9999" used to be accepted and hand back negative rank
    numbers, and one saying 10**400 used to reach the database.
    """
    try:
        padding = "=" * (-len(cursor) % 4)
        sort_xp, user_id, next_rank = (
            base64.urlsafe_b64decode(cursor + padding).decode().split(":")
        )
        values = (int(sort_xp), int(user_id), int(next_rank))
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    sort_xp_value, user_id_value, next_rank_value = values
    # -1 is the NULL-XP sentinel (see _sort_xp), so it is the floor; ids and
    # ranks are 1-based.
    if not (
        -1 <= sort_xp_value <= INT64_MAX
        and 1 <= user_id_value <= INT64_MAX
        and 1 <= next_rank_value <= INT64_MAX
    ):
        raise HTTPException(status_code=400, detail="Invalid cursor")
    return values


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    cursor: Optional[str] = Query(None, max_length=MAX_CURSOR_LENGTH),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """One page of the all-time board, plus the caller's own standing."""
    sort_xp = _sort_xp()

    start_rank = 1
    conditions = [_listed()]
    if cursor:
        cursor_xp, cursor_user_id, start_rank = _decode_cursor(cursor)
        # Strictly after (cursor_xp, cursor_user_id) in `sort_xp DESC,
        # user_id ASC` order. Spelled out rather than as a row comparison,
        # which SQLite does not support.
        conditions.append(
            or_(
                sort_xp < cursor_xp,
                and_(sort_xp == cursor_xp, User.id > cursor_user_id),
            )
        )

    if start_rank > MAX_DEPTH:
        remaining = 0
    else:
        remaining = MAX_DEPTH - start_rank + 1

    rows = []
    if remaining > 0:
        # One extra row, purely to learn whether a next page exists without
        # running a second count query.
        page_size = min(limit, remaining)
        result = await db.execute(
            select(
                User.id,
                User.username,
                User.avatar_url,
                User.avatar_image_data,
                User.avatar_config,
                User.avatar_type,
                StudentProfile.level,
                StudentProfile.xp,
                sort_xp.label("sort_xp"),
            )
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .where(*conditions)
            .order_by(sort_xp.desc(), User.id.asc())
            .limit(page_size + 1)
        )
        rows = result.all()

    has_more = len(rows) > min(limit, remaining)
    page = rows[: min(limit, remaining)] if remaining > 0 else []

    entries = [
        LeaderboardEntry(
            rank=start_rank + offset,
            username=row.username,
            avatar_url=row.avatar_url,
            avatar_image_data=row.avatar_image_data,
            avatar_config=row.avatar_config,
            avatar_type=row.avatar_type or "upload",
            level=row.level or 1,
            xp=row.xp or 0,
        )
        for offset, row in enumerate(page)
    ]

    next_cursor = None
    if has_more and page:
        next_rank = start_rank + len(page)
        if next_rank <= MAX_DEPTH:
            last = page[-1]
            next_cursor = _encode_cursor(last.sort_xp, last.id, next_rank)

    return LeaderboardResponse(
        entries=entries,
        me=await _me(db, current_user),
        next_cursor=next_cursor,
    )


async def _me(db: AsyncSession, current_user: User) -> LeaderboardMe:
    """The caller's own standing, listed or not.

    Returned unconditionally so an unlisted student can see what joining
    would show them as, and so their own row can be marked in a page they do
    appear in. The rank is counted, not paged to, so it stays exact past
    MAX_DEPTH.
    """
    profile_result = await db.execute(
        select(StudentProfile.xp, StudentProfile.level).where(
            StudentProfile.user_id == current_user.id
        )
    )
    profile = profile_result.first()
    my_xp = (profile.xp if profile else None) or 0
    my_level = (profile.level if profile else None) or 1
    my_sort_xp = profile.xp if profile and profile.xp is not None else -1

    sort_xp = _sort_xp()
    # Everyone listed who sorts strictly ahead of me, under the same
    # ordering. Counting the people in front is the definition of a rank, and
    # it holds whether or not I am one of the listed rows myself.
    ahead_result = await db.execute(
        select(func.count())
        .select_from(User)
        .join(StudentProfile, StudentProfile.user_id == User.id)
        .where(
            _listed(),
            User.id != current_user.id,
            or_(
                sort_xp > my_sort_xp,
                and_(sort_xp == my_sort_xp, User.id < current_user.id),
            ),
        )
    )
    ahead = ahead_result.scalar_one()

    return LeaderboardMe(
        rank=ahead + 1,
        xp=my_xp,
        level=my_level,
        is_listed=current_user.profile_visibility == "public"
        and bool(current_user.is_active),
    )
