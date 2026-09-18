"""Duel Arena submission grading and winner resolution
(app.services.duels.submit_solution).

Mirrors test_duels_matchmaking.py's rigor: the sequential/single-request
cases are the easy part. The real requirement -- explicitly called out for
extra scrutiny -- is that two students submitting correct solutions within
milliseconds of each other must resolve to exactly one winner via the
atomic "UPDATE duels SET winner=... WHERE status='active'", not a
read-then-write race.

Duel problems are picked randomly from the curated pool by join_queue, so
these tests fetch the actual assigned exercise's stored solution_code
rather than hardcoding one -- the same "use the real reference solution"
approach test_code_executor.py's audit used, and it means these tests stay
correct regardless of which pool exercise gets picked.
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
    DuelStatusEnum,
    Exercise,
    User,
)
from app.services.duels import DuelNotActive, NotAParticipant, join_queue, submit_solution


async def _make_user(db_session) -> int:
    suffix = uuid.uuid4().hex[:10]
    user = User(email=f"duelsub_{suffix}@example.com", username=f"duelsub_{suffix}")
    db_session.add(user)
    await db_session.flush()
    return user.id


@pytest.fixture(autouse=True)
async def _clean_duel_state(db_session):
    """Same reasoning as the matchmaking/API test files: the session-scoped
    test DB shares fixed difficulty pools across every test in the suite."""
    await db_session.execute(update(DuelQueueEntry).values(duel_id=None))
    await db_session.execute(DuelParticipant.__table__.delete())
    await db_session.execute(DuelQueueEntry.__table__.delete())
    from app.models import DuelSubmissionAttempt
    await db_session.execute(DuelSubmissionAttempt.__table__.delete())
    await db_session.execute(Duel.__table__.delete())
    await db_session.commit()
    yield


async def _matched_pair(db_session, difficulty=DifficultyEnum.beginner):
    user_a = await _make_user(db_session)
    user_b = await _make_user(db_session)
    await db_session.commit()
    await join_queue(db_session, user_a, difficulty)
    result_b = await join_queue(db_session, user_b, difficulty)
    return user_a, user_b, result_b.duel_id


async def _reference_solution(db_session, duel_id: str) -> str:
    duel = await db_session.get(Duel, duel_id)
    duel_problem = await db_session.get(DuelProblem, duel.duel_problem_id)
    exercise = await db_session.get(Exercise, duel_problem.exercise_id)
    return exercise.solution_code


class TestBasicSubmission:
    async def test_wrong_submission_does_not_win(self, db_session):
        user_a, user_b, duel_id = await _matched_pair(db_session)
        result = await submit_solution(db_session, duel_id, user_a, "this is not valid code at all !!!")
        assert result.is_correct is False
        assert result.won is False
        assert result.duel_status == "active"

    async def test_correct_submission_wins_and_completes_the_duel(self, db_session):
        user_a, user_b, duel_id = await _matched_pair(db_session)
        solution = await _reference_solution(db_session, duel_id)

        result = await submit_solution(db_session, duel_id, user_a, solution)
        assert result.is_correct is True
        assert result.won is True
        assert result.duel_status == "completed"
        assert result.winner_user_id == user_a

        duel = await db_session.get(Duel, duel_id)
        assert duel.status == DuelStatusEnum.completed
        assert duel.winner_user_id == user_a
        assert duel.ended_at is not None

    async def test_a_correct_submission_after_the_duel_already_ended_does_not_win(self, db_session):
        user_a, user_b, duel_id = await _matched_pair(db_session)
        solution = await _reference_solution(db_session, duel_id)

        await submit_solution(db_session, duel_id, user_a, solution)  # a wins

        with pytest.raises(DuelNotActive):
            await submit_solution(db_session, duel_id, user_b, solution)

        duel = await db_session.get(Duel, duel_id)
        assert duel.winner_user_id == user_a  # unchanged

    async def test_a_non_participant_cannot_submit(self, db_session):
        _, _, duel_id = await _matched_pair(db_session)
        outsider = await _make_user(db_session)
        await db_session.commit()

        with pytest.raises(NotAParticipant):
            await submit_solution(db_session, duel_id, outsider, "print(1)")

    async def test_submitting_to_an_expired_duel_finalizes_it_with_no_winner(self, db_session):
        user_a, user_b, duel_id = await _matched_pair(db_session)
        # Force the duel into the past without touching submit_solution's
        # own logic -- simulates real time having elapsed.
        from datetime import datetime, timedelta
        await db_session.execute(
            update(Duel).where(Duel.id == duel_id).values(ends_at=datetime.utcnow() - timedelta(seconds=1))
        )
        await db_session.commit()

        solution = await _reference_solution(db_session, duel_id)
        with pytest.raises(DuelNotActive):
            await submit_solution(db_session, duel_id, user_a, solution)

        duel = await db_session.get(Duel, duel_id)
        assert duel.status == DuelStatusEnum.completed
        assert duel.winner_user_id is None


class TestConcurrentWinnerResolution:
    """The scenario called out for extra rigor: two genuinely concurrent
    correct submissions, not sequential ones."""

    async def test_two_simultaneous_correct_submissions_resolve_to_exactly_one_winner(
        self, db_session, db_session_factory
    ):
        user_a, user_b, duel_id = await _matched_pair(db_session)
        solution = await _reference_solution(db_session, duel_id)

        async def _submit(user_id):
            async with db_session_factory() as session:
                return await submit_solution(session, duel_id, user_id, solution)

        result_a, result_b = await asyncio.gather(_submit(user_a), _submit(user_b))

        # Both were genuinely correct -- both know it via is_correct=True --
        # but exactly one of them actually won the race.
        assert result_a.is_correct is True
        assert result_b.is_correct is True
        assert [result_a.won, result_b.won].count(True) == 1, (
            "expected exactly one winner from two simultaneous correct submissions"
        )

        # And the database agrees with whichever result claimed the win --
        # no split-brain between what a request was told and what's stored.
        winner_result = result_a if result_a.won else result_b
        async with db_session_factory() as session:
            duel = await session.get(Duel, duel_id)
            assert duel.status == DuelStatusEnum.completed
            assert duel.winner_user_id == winner_result.winner_user_id
            assert duel.winner_user_id in (user_a, user_b)

    async def test_many_repeated_simultaneous_races_never_produce_two_winners(
        self, db_session, db_session_factory
    ):
        # Run the race several times over fresh duels -- a check-then-act
        # bug in the winner UPDATE wouldn't necessarily manifest on every
        # single run, the same way the matchmaking race didn't always
        # manifest as a naive double-booking on the first try.
        for _ in range(8):
            user_a, user_b, duel_id = await _matched_pair(db_session)
            solution = await _reference_solution(db_session, duel_id)

            async def _submit(user_id):
                async with db_session_factory() as session:
                    return await submit_solution(session, duel_id, user_id, solution)

            result_a, result_b = await asyncio.gather(_submit(user_a), _submit(user_b))
            assert [result_a.won, result_b.won].count(True) == 1

            duel = await db_session.get(Duel, duel_id)
            assert duel.status == DuelStatusEnum.completed
            assert duel.winner_user_id in (user_a, user_b)
