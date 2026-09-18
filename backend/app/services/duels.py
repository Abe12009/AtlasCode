"""Duel Arena domain logic: matchmaking (join_queue) and, below it,
submission grading + winner resolution (submit_solution).

== Matchmaking ==

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

== Winner resolution ==

Same technique, same reason: submit_solution's "first correct submission
wins" is a single atomic conditional UPDATE ("... WHERE status='active'"),
verified by rowcount, not a read-then-write. Two students submitting
correct solutions within milliseconds of each other both attempt this
UPDATE; the database allows exactly one of them to actually change the
row, and that request is the one that reports back "you won" -- the other
reports "opponent won first" from the very same, single statement's
outcome. No in-memory locking, no trusting whichever request the
application happens to handle first.
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
    DuelStatusEnum,
    DuelSubmissionAttempt,
    Exercise,
)
from app.services.code_executor import ExecutionResult, execute_code, validate_python_code

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


class NotAParticipant(Exception):
    """The requesting user isn't one of this duel's two participants."""


class DuelNotActive(Exception):
    """The duel doesn't accept submissions right now -- already completed
    (someone won, or it timed out), or past its ends_at (finalized to
    'completed' as a side effect of this exception being raised, so the
    next person to touch it sees the already-settled state rather than
    re-discovering the timeout)."""


@dataclass
class SubmitResult:
    is_correct: bool
    passed_count: int
    total_count: int
    #: True only for the exact submission whose atomic UPDATE actually won
    #: the race -- see the module docstring. A correct-but-too-late
    #: submission has is_correct=True, won=False.
    won: bool
    duel_status: str
    winner_user_id: Optional[int]


def _pass_counts(exec_result: ExecutionResult) -> tuple[int, int]:
    """Uniform (passed, total) regardless of whether test_code decomposed
    into a per-assertion checklist (Step 3) or fell back to a single
    whole-block pass/fail -- the latter is just treated as one test case,
    same as it reads to a student either way."""
    if exec_result.test_results is not None:
        total = len(exec_result.test_results)
        passed = sum(1 for r in exec_result.test_results if r.passed)
        return passed, total
    return (1, 1) if exec_result.success else (0, 1)


async def best_pass_counts(db: AsyncSession, duel_id: int, user_id: int) -> tuple[int, int]:
    """The participant's best attempt so far in this duel, not their most
    recent one -- a student experimenting with a worse version after a
    better one shouldn't make their own (or their opponent's view of their)
    displayed progress regress."""
    result = await db.execute(
        select(DuelSubmissionAttempt)
        .where(DuelSubmissionAttempt.duel_id == duel_id, DuelSubmissionAttempt.user_id == user_id)
        .order_by(DuelSubmissionAttempt.passed_count.desc(), DuelSubmissionAttempt.submitted_at.asc())
        .limit(1)
    )
    best = result.scalar_one_or_none()
    if best is None:
        return 0, 0
    return best.passed_count, best.total_count


async def submit_solution(db: AsyncSession, duel_id: int, user_id: int, code: str) -> SubmitResult:
    duel = await db.get(Duel, duel_id)
    if duel is None:
        raise DuelNotActive()

    participant = (
        await db.execute(
            select(DuelParticipant).where(
                DuelParticipant.duel_id == duel_id, DuelParticipant.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if participant is None:
        raise NotAParticipant()

    now = datetime.utcnow()
    if duel.status != DuelStatusEnum.active or now >= duel.ends_at:
        # Lazily finalize an expired-but-still-'active' duel the first time
        # anyone touches it past ends_at -- atomically, so two late
        # submitters racing each other can't both believe they're the one
        # who closed it out (there's no winner either way here, but the
        # same discipline applies: exactly one conditional UPDATE, not a
        # read-then-write two players could both act on).
        await db.execute(
            update(Duel)
            .where(Duel.id == duel_id, Duel.status == DuelStatusEnum.active)
            .values(status=DuelStatusEnum.completed, ended_at=now)
        )
        await db.commit()
        raise DuelNotActive()

    duel_problem = await db.get(DuelProblem, duel.duel_problem_id)
    exercise = await db.get(Exercise, duel_problem.exercise_id)

    validation = validate_python_code(code)
    if not validation.is_valid:
        exec_result = ExecutionResult(success=False, output="", error="; ".join(validation.errors), execution_time=0.0)
    else:
        exec_result = execute_code(code, exercise.test_code)

    passed_count, total_count = _pass_counts(exec_result)
    is_correct = exec_result.success

    db.add(
        DuelSubmissionAttempt(
            duel_id=duel_id,
            user_id=user_id,
            code=code,
            passed_count=passed_count,
            total_count=total_count,
            is_correct=is_correct,
        )
    )
    await db.commit()

    won = False
    if is_correct:
        claim = await db.execute(
            update(Duel)
            .where(Duel.id == duel_id, Duel.status == DuelStatusEnum.active)
            .values(status=DuelStatusEnum.completed, winner_user_id=user_id, ended_at=datetime.utcnow())
        )
        await db.commit()
        won = claim.rowcount == 1

    await db.refresh(duel)
    return SubmitResult(
        is_correct=is_correct,
        passed_count=passed_count,
        total_count=total_count,
        won=won,
        duel_status=duel.status.value,
        winner_user_id=duel.winner_user_id,
    )
