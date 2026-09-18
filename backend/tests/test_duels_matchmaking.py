"""Duel Arena matchmaking: app.services.duels.join_queue.

The rigor bar here (per explicit review feedback): don't just prove the
single-request case is correct -- prove the atomic-claim design is actually
safe when many join_queue() calls race each other concurrently, each on its
own DB session (mirroring separate real HTTP requests), the same way
test_code_executor.py proved the grading engine handles real content shapes
rather than only the shapes it was designed around.
"""

import asyncio
import uuid

import pytest
from sqlalchemy import select, update

from app.models import (
    DifficultyEnum,
    Duel,
    DuelParticipant,
    DuelProblem,
    DuelQueueEntry,
    DuelQueueStatusEnum,
    User,
)
from app.services.duels import AlreadyInQueue, NoDuelProblemAvailable, join_queue


async def _make_user(db_session) -> int:
    suffix = uuid.uuid4().hex[:10]
    user = User(email=f"duelmm_{suffix}@example.com", username=f"duelmm_{suffix}")
    db_session.add(user)
    await db_session.flush()
    return user.id


@pytest.fixture(autouse=True)
async def _clean_duel_queue(db_session):
    """The test DB is session-scoped (see conftest.py's setup_database) and
    every test in this file shares the same fixed difficulty pools
    (beginner/intermediate/advanced) -- a 'waiting' entry left behind by one
    test (e.g. a user nobody ever came along to match) would otherwise leak
    into the next test and get matched against an unrelated, unexpected
    partner. Clear the slate before each test so pool state is only ever
    whatever that test itself creates."""
    await db_session.execute(update(DuelQueueEntry).values(duel_id=None))
    await db_session.execute(DuelParticipant.__table__.delete())
    await db_session.execute(DuelQueueEntry.__table__.delete())
    await db_session.execute(Duel.__table__.delete())
    await db_session.commit()
    yield


class TestBasicSequentialMatching:
    async def test_first_joiner_waits_second_joiner_matches_them(self, db_session):
        user_a = await _make_user(db_session)
        user_b = await _make_user(db_session)
        await db_session.commit()

        result_a = await join_queue(db_session, user_a, DifficultyEnum.beginner)
        assert result_a.status == "waiting"
        assert result_a.duel_id is None

        result_b = await join_queue(db_session, user_b, DifficultyEnum.beginner)
        assert result_b.status == "matched"
        assert result_b.duel_id is not None

        # A's own entry must have been flipped to matched, same duel.
        entry_a = (
            await db_session.execute(select(DuelQueueEntry).where(DuelQueueEntry.id == result_a.queue_entry_id))
        ).scalar_one()
        assert entry_a.status == DuelQueueStatusEnum.matched
        assert entry_a.duel_id == result_b.duel_id

        participants = (
            await db_session.execute(select(DuelParticipant).where(DuelParticipant.duel_id == result_b.duel_id))
        ).scalars().all()
        assert {p.user_id for p in participants} == {user_a, user_b}

    async def test_different_difficulty_pools_never_match_each_other(self, db_session):
        user_a = await _make_user(db_session)
        user_b = await _make_user(db_session)
        await db_session.commit()

        result_a = await join_queue(db_session, user_a, DifficultyEnum.beginner)
        result_b = await join_queue(db_session, user_b, DifficultyEnum.advanced)

        assert result_a.status == "waiting"
        assert result_b.status == "waiting"  # not matched -- different pools


class TestSelfMatchAndDuplicateGuards:
    async def test_a_user_can_never_match_their_own_waiting_entry(self, db_session):
        user_a = await _make_user(db_session)
        await db_session.commit()

        result_1 = await join_queue(db_session, user_a, DifficultyEnum.beginner)
        assert result_1.status == "waiting"

        # Same user, same pool, while their first entry is still waiting --
        # must never "match" against themselves.
        with pytest.raises(AlreadyInQueue):
            await join_queue(db_session, user_a, DifficultyEnum.beginner)

        # No duel was created, no self-participant duel exists.
        duels = (await db_session.execute(select(Duel))).scalars().all()
        assert duels == []

    async def test_rejoining_after_being_matched_is_a_fresh_wait_not_an_error(self, db_session):
        user_a = await _make_user(db_session)
        user_b = await _make_user(db_session)
        await db_session.commit()

        await join_queue(db_session, user_a, DifficultyEnum.beginner)
        await join_queue(db_session, user_b, DifficultyEnum.beginner)  # matches A

        # A is now 'matched', not 'waiting' -- joining again is a brand new
        # queue entry, not blocked by the partial unique index.
        result = await join_queue(db_session, user_a, DifficultyEnum.beginner)
        assert result.status == "waiting"


class TestNoDuelProblemAvailable:
    async def test_joining_a_pool_with_no_active_problems_fails_before_writing_anything(self, db_session):
        user_a = await _make_user(db_session)
        await db_session.commit()

        # Empty out the beginner pool for this test only.
        await db_session.execute(
            update(DuelProblem).where(DuelProblem.difficulty == DifficultyEnum.beginner).values(is_active=False)
        )
        await db_session.commit()

        with pytest.raises(NoDuelProblemAvailable):
            await join_queue(db_session, user_a, DifficultyEnum.beginner)

        entries = (
            await db_session.execute(select(DuelQueueEntry).where(DuelQueueEntry.user_id == user_a))
        ).scalars().all()
        assert entries == []  # fail-fast: never left waiting in an unmatchable pool


class TestConcurrentJoins:
    """The scenario explicitly called out for extra rigor: real concurrent
    requests, not just sequential calls that happen to be correct in
    isolation. Each simulated "request" gets its own DB session, exactly
    like separate real HTTP requests would."""

    async def test_two_concurrent_joiners_never_corrupt_state_even_if_they_dont_pair(
        self, db_session, db_session_factory
    ):
        # Users must exist (and be committed) before the concurrent phase,
        # via the ordinary single session.
        user_a = await _make_user(db_session)
        user_b = await _make_user(db_session)
        await db_session.commit()

        async def _join(user_id):
            async with db_session_factory() as session:
                return await join_queue(session, user_id, DifficultyEnum.intermediate)

        result_a, result_b = await asyncio.gather(_join(user_a), _join(user_b))

        statuses = sorted([result_a.status, result_b.status])
        # Only the CLAIMING side of a pair ever gets status="matched" back --
        # the claimed partner's own call already returned "waiting" before
        # the pairing happened (its in-memory result is stale relative to
        # the DB row a moment later), so a successful pairing between
        # exactly two concurrent joiners shows up as ["matched", "waiting"],
        # not ["matched", "matched"]. The other valid outcome is the
        # documented rare edge case: neither could see the other's
        # not-yet-committed row, so both became separate waiters.
        # ["matched", "matched"] must never happen -- that would mean both
        # sides somehow claimed each other, i.e. two duels for one pair.
        assert statuses in (["matched", "waiting"], ["waiting", "waiting"]), statuses

        if statuses == ["matched", "waiting"]:
            matched_result = result_a if result_a.status == "matched" else result_b
            async with db_session_factory() as session:
                participants = (
                    await session.execute(
                        select(DuelParticipant).where(DuelParticipant.duel_id == matched_result.duel_id)
                    )
                ).scalars().all()
                assert {p.user_id for p in participants} == {user_a, user_b}
                assert len(participants) == 2  # never 1 (self-match) or >2 (duplicate join)

    async def test_many_concurrent_joiners_produce_zero_corruption_and_mostly_pair_up(
        self, db_session, db_session_factory
    ):
        # A real stress test: this is what would actually catch a
        # check-then-act race in the pairing logic -- a naive
        # "SELECT waiting, then separately INSERT/UPDATE" implementation
        # would very plausibly double-book a waiting user into two duels
        # under this many concurrent callers, or leave orphaned/duplicate
        # rows. The atomic-claim design should produce zero corruption
        # regardless of how the database interleaves these.
        n = 12
        user_ids = []
        for _ in range(n):
            user_ids.append(await _make_user(db_session))
        await db_session.commit()

        async def _join(user_id):
            async with db_session_factory() as session:
                return await join_queue(session, user_id, DifficultyEnum.advanced)

        results = await asyncio.gather(*(_join(uid) for uid in user_ids))

        matched = [r for r in results if r.status == "matched"]
        waiting = [r for r in results if r.status == "waiting"]
        assert len(matched) + len(waiting) == n

        # Invariant 1: every user appears in at most one DuelParticipant row
        # across every duel created in this run -- no double-booking.
        async with db_session_factory() as session:
            all_participants = (
                await session.execute(
                    select(DuelParticipant).where(DuelParticipant.user_id.in_(user_ids))
                )
            ).scalars().all()
        participant_user_ids = [p.user_id for p in all_participants]
        assert len(participant_user_ids) == len(set(participant_user_ids)), (
            "a user was placed in more than one duel -- double-booked by a race"
        )

        # Invariant 2: no duel has the same user as both of its participants.
        duel_ids = {p.duel_id for p in all_participants}
        async with db_session_factory() as session:
            for duel_id in duel_ids:
                duel_participants = (
                    await session.execute(select(DuelParticipant).where(DuelParticipant.duel_id == duel_id))
                ).scalars().all()
                assert len(duel_participants) == 2, f"duel {duel_id} has {len(duel_participants)} participants"
                assert duel_participants[0].user_id != duel_participants[1].user_id, (
                    f"duel {duel_id} matched a user with themselves"
                )

        # Invariant 3: real pairing actually happened in bulk -- this isn't
        # just "nothing corrupted", it's "the logic paired people up".
        # Ground truth is the DB's participant rows, not the in-memory
        # `results` list: only the *claiming* half of each pair gets
        # status="matched" back from join_queue -- the claimed partner's
        # own call already returned status="waiting" before the pairing
        # happened, so counting `matched` results would undercount by
        # exactly half of every real pair. With 12 simultaneous joiners,
        # expect the overwhelming majority to actually end up in a
        # DuelParticipant row (allow slack for the documented rare-
        # collision edge case, but a healthy majority is the signal that
        # the claim logic is doing real work, not silently leaving
        # everyone an unpaired waiter).
        assert len(participant_user_ids) >= n - 4, (
            f"only {len(participant_user_ids)}/{n} joiners ended up in a duel -- "
            "pairing logic may not be working"
        )
