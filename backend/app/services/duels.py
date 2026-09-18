"""Duel Arena domain logic: matchmaking (join_queue).

The core correctness requirement: two students joining the same difficulty
pool at nearly the same moment must land in exactly one shared duel --
never a duplicate duel, never matched with themselves, never silently lost.

The pairing logic is a single atomic conditional UPDATE (claim a waiting
row, verified by rowcount), the same technique the Step 4 architecture
proposal used for submission-race resolution ("UPDATE duels SET winner=...
WHERE status='active'"). There is no separate "check if someone is
waiting" query followed by a separate "claim them" write -- that
check-then-act gap is exactly what would let two concurrent joiners both
believe they found the same free partner. Here, the SELECT that picks a
candidate and the UPDATE that claims it are one statement; a second,
truly-concurrent UPDATE targeting the same row is forced by the database's
own row-level write semantics to wait, then re-evaluate against the
already-claimed state and affect zero rows. This holds on both target
databases: Postgres (production, real MVCC row locking on UPDATE) and
SQLite (dev/test, whose single-writer model makes it trivially true).

Documented, accepted limitation: if two joins are so close together that
neither's UPDATE can see the other's not-yet-committed INSERT, both become
separate waiters rather than pairing with each other immediately. This is
not corruption -- no duplicate duel, no self-match -- it just means that
specific pair doesn't necessarily match each other; each will pair
correctly with the next joiner in their pool. Closing this last sliver
would need a Postgres-only serializing lock (e.g. pg_advisory_xact_lock)
that has no SQLite equivalent, which would break local dev/test entirely
for a race that's already both rare and self-healing. Not worth it for v1.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DifficultyEnum,
    Duel,
    DuelParticipant,
    DuelProblem,
    DuelQueueEntry,
    DuelQueueStatusEnum,
)

#: Fixed match length. Tunable later; not worth deliberating over now (see
#: Step 4 approval).
DUEL_DURATION = timedelta(minutes=10)


class NoDuelProblemAvailable(Exception):
    """No active DuelProblem exists for the requested difficulty -- the
    curated pool is empty for that tier. Raised before any queue row is
    written, so joining never leaves someone waiting in an unmatchable
    pool."""

    def __init__(self, difficulty: DifficultyEnum):
        self.difficulty = difficulty
        super().__init__(f"No duel problems available for difficulty={difficulty.value}")


class AlreadyInQueue(Exception):
    """Raised when a user already has a 'waiting' entry -- either an
    ordinary duplicate join-queue click, or the rare case where a genuinely
    concurrent duplicate request loses the race to the partial unique index
    (uq_one_waiting_entry_per_user) at commit time. Either way this is a
    normal, expected outcome for the caller to handle, not a server error."""


@dataclass
class JoinQueueResult:
    status: str  # "waiting" | "matched"
    queue_entry_id: int
    duel_id: Optional[int] = None


async def _pick_duel_problem(db: AsyncSession, difficulty: DifficultyEnum) -> Optional[DuelProblem]:
    result = await db.execute(
        select(DuelProblem)
        .where(DuelProblem.difficulty == difficulty, DuelProblem.is_active.is_(True))
        .order_by(func.random())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def join_queue(db: AsyncSession, user_id: int, difficulty: DifficultyEnum) -> JoinQueueResult:
    """Joins (or is immediately matched into) the queue for `difficulty`.

    Commits internally -- this is a complete unit of work, not a step meant
    to be composed into a larger transaction, since the atomic claim below
    has to be its own statement for the rowcount check to mean anything.
    """
    # Fail fast: never let someone sit in a pool that has no problem to
    # actually duel over.
    if await _pick_duel_problem(db, difficulty) is None:
        raise NoDuelProblemAvailable(difficulty)

    # The atomic claim. Picks the longest-waiting *other* user's entry in
    # this pool and flips it to 'matched' in one statement -- see the module
    # docstring for why this, and not a separate SELECT-then-UPDATE, is what
    # actually makes this safe under concurrency.
    candidate_ids = (
        select(DuelQueueEntry.id)
        .where(
            DuelQueueEntry.status == DuelQueueStatusEnum.waiting,
            DuelQueueEntry.difficulty == difficulty,
            DuelQueueEntry.user_id != user_id,
        )
        .order_by(DuelQueueEntry.joined_at.asc())
        .limit(1)
    )
    claim = await db.execute(
        update(DuelQueueEntry)
        .where(
            DuelQueueEntry.id.in_(candidate_ids),
            DuelQueueEntry.status == DuelQueueStatusEnum.waiting,
        )
        .values(status=DuelQueueStatusEnum.matched)
        .returning(DuelQueueEntry.id, DuelQueueEntry.user_id)
    )
    claimed_row = claim.first()

    if claimed_row is None:
        # No one else waiting in this pool right now (or another request
        # claimed them a moment earlier) -- become the waiter.
        entry = DuelQueueEntry(user_id=user_id, difficulty=difficulty, status=DuelQueueStatusEnum.waiting)
        db.add(entry)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise AlreadyInQueue() from e
        await db.refresh(entry)
        return JoinQueueResult(status="waiting", queue_entry_id=entry.id)

    partner_entry_id, partner_user_id = claimed_row

    # Genuinely paired with partner_user_id -- create the duel. Re-pick a
    # problem here rather than reusing the earlier existence check's result:
    # this call is the one that actually creates the Duel row, so this pick
    # is the one both players get.
    problem = await _pick_duel_problem(db, difficulty)
    assert problem is not None, "existence was already confirmed above"

    now = datetime.utcnow()
    duel = Duel(duel_problem_id=problem.id, started_at=now, ends_at=now + DUEL_DURATION)
    db.add(duel)
    await db.flush()  # need duel.id for the participants/queue-entry links below

    db.add_all([
        DuelParticipant(duel_id=duel.id, user_id=user_id),
        DuelParticipant(duel_id=duel.id, user_id=partner_user_id),
    ])

    # My own queue entry never existed (I matched immediately rather than
    # ever sitting in 'waiting'), so it's created directly in the matched
    # state -- not inserted as waiting and then flipped, which would
    # needlessly re-open the same race this function exists to avoid.
    my_entry = DuelQueueEntry(
        user_id=user_id,
        difficulty=difficulty,
        status=DuelQueueStatusEnum.matched,
        duel_id=duel.id,
    )
    db.add(my_entry)
    await db.execute(
        update(DuelQueueEntry).where(DuelQueueEntry.id == partner_entry_id).values(duel_id=duel.id)
    )
    await db.commit()
    await db.refresh(my_entry)
    return JoinQueueResult(status="matched", queue_entry_id=my_entry.id, duel_id=duel.id)
