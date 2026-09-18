"""Duel Arena data model: the schema itself, before any matchmaking/API/
WebSocket logic exists on top of it (see the Step 4 build plan -- data model
first). These are plain ORM tests against db_session, not HTTP, since
there's no API layer yet to exercise.

Exercise 1 (code_writing, "Hello, World!") is the same stable fixture other
suites use (see test_exercise_grading.py's CODE_ID).
"""

import uuid

import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import (
    Duel,
    DuelParticipant,
    DuelProblem,
    DuelQueueEntry,
    DuelQueueStatusEnum,
    DuelStatusEnum,
    DuelSubmissionAttempt,
    DifficultyEnum,
    User,
)
from app.seed.duel_problems import DUEL_PROBLEMS, seed_duel_problems

CODE_EXERCISE_ID = 1


async def _real_user_ids(db_session, n=2):
    """Creates n fresh User rows directly (not via /auth/register -- these
    tests exercise the duel schema itself, not auth), each with a unique
    email/username so tests don't depend on registration order or leftover
    rows from other test files sharing the session-scoped test DB."""
    ids = []
    for _ in range(n):
        suffix = uuid.uuid4().hex[:10]
        user = User(email=f"duel_{suffix}@example.com", username=f"duel_{suffix}")
        db_session.add(user)
        await db_session.flush()
        ids.append(user.id)
    return ids


class TestDuelProblem:
    async def test_curated_problem_references_a_real_exercise(self, db_session):
        problem = DuelProblem(exercise_id=CODE_EXERCISE_ID, difficulty=DifficultyEnum.beginner)
        db_session.add(problem)
        await db_session.commit()
        await db_session.refresh(problem)

        assert problem.id is not None
        assert problem.is_active is True  # default -- curated in, not silently excluded
        assert problem.exercise_id == CODE_EXERCISE_ID

    async def test_not_every_exercise_is_a_duel_problem_by_default(self, db_session):
        # The whole point of curation: creating an Exercise elsewhere in the
        # app must never implicitly create a matching DuelProblem row.
        result = await db_session.execute(
            select(DuelProblem).where(DuelProblem.exercise_id == 999999)
        )
        assert result.scalar_one_or_none() is None


class TestDuelAndParticipants:
    async def test_a_duel_has_exactly_two_participants_with_a_shared_problem(self, db_session):
        problem = DuelProblem(exercise_id=CODE_EXERCISE_ID, difficulty=DifficultyEnum.beginner)
        db_session.add(problem)
        await db_session.flush()

        user_a, user_b = await _real_user_ids(db_session)
        now = datetime.utcnow()
        duel = Duel(duel_problem_id=problem.id, started_at=now, ends_at=now + timedelta(minutes=10))
        db_session.add(duel)
        await db_session.flush()

        db_session.add_all([
            DuelParticipant(duel_id=duel.id, user_id=user_a, is_connected=True),
            DuelParticipant(duel_id=duel.id, user_id=user_b, is_connected=True),
        ])
        await db_session.commit()
        await db_session.refresh(duel)

        assert duel.status == DuelStatusEnum.active  # default -- a created duel is live immediately
        assert duel.winner_user_id is None
        result = await db_session.execute(
            select(DuelParticipant).where(DuelParticipant.duel_id == duel.id)
        )
        participants = result.scalars().all()
        assert len(participants) == 2
        assert {p.user_id for p in participants} == {user_a, user_b}

    async def test_a_user_cannot_be_added_to_the_same_duel_twice(self, db_session):
        problem = DuelProblem(exercise_id=CODE_EXERCISE_ID, difficulty=DifficultyEnum.beginner)
        db_session.add(problem)
        await db_session.flush()

        user_a, _ = await _real_user_ids(db_session)
        now = datetime.utcnow()
        duel = Duel(duel_problem_id=problem.id, started_at=now, ends_at=now + timedelta(minutes=10))
        db_session.add(duel)
        await db_session.flush()

        db_session.add(DuelParticipant(duel_id=duel.id, user_id=user_a))
        await db_session.commit()

        db_session.add(DuelParticipant(duel_id=duel.id, user_id=user_a))
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_deleting_a_duel_cascades_to_its_participants_and_submissions(self, db_session):
        problem = DuelProblem(exercise_id=CODE_EXERCISE_ID, difficulty=DifficultyEnum.beginner)
        db_session.add(problem)
        await db_session.flush()

        user_a, user_b = await _real_user_ids(db_session)
        now = datetime.utcnow()
        duel = Duel(duel_problem_id=problem.id, started_at=now, ends_at=now + timedelta(minutes=10))
        db_session.add(duel)
        await db_session.flush()
        duel_id = duel.id

        db_session.add_all([
            DuelParticipant(duel_id=duel_id, user_id=user_a),
            DuelParticipant(duel_id=duel_id, user_id=user_b),
            DuelSubmissionAttempt(
                duel_id=duel_id, user_id=user_a, code="print('hi')",
                passed_count=0, total_count=1, is_correct=False,
            ),
        ])
        await db_session.commit()

        await db_session.delete(duel)
        await db_session.commit()

        participants = (
            await db_session.execute(select(DuelParticipant).where(DuelParticipant.duel_id == duel_id))
        ).scalars().all()
        submissions = (
            await db_session.execute(select(DuelSubmissionAttempt).where(DuelSubmissionAttempt.duel_id == duel_id))
        ).scalars().all()
        assert participants == []
        assert submissions == []


class TestDuelSubmissionAttempt:
    async def test_records_the_full_grading_result_for_one_submission(self, db_session):
        problem = DuelProblem(exercise_id=CODE_EXERCISE_ID, difficulty=DifficultyEnum.beginner)
        db_session.add(problem)
        await db_session.flush()

        user_a, _ = await _real_user_ids(db_session)
        now = datetime.utcnow()
        duel = Duel(duel_problem_id=problem.id, started_at=now, ends_at=now + timedelta(minutes=10))
        db_session.add(duel)
        await db_session.flush()

        attempt = DuelSubmissionAttempt(
            duel_id=duel.id,
            user_id=user_a,
            code="print('Hello, World!')",
            passed_count=1,
            total_count=1,
            is_correct=True,
        )
        db_session.add(attempt)
        await db_session.commit()
        await db_session.refresh(attempt)

        assert attempt.is_correct is True
        assert attempt.passed_count == attempt.total_count == 1
        # The row keeps the real code server-side for audit purposes -- this
        # is a DB-layer fact, not a claim about what any API response
        # serializes; the "never send opponent code to the client" guarantee
        # lives in the API layer built on top of this table, not here.
        assert attempt.code == "print('Hello, World!')"


class TestDuelQueueEntry:
    async def test_a_fresh_queue_entry_starts_waiting_with_no_duel_yet(self, db_session):
        user_a, _ = await _real_user_ids(db_session)
        entry = DuelQueueEntry(user_id=user_a, difficulty=DifficultyEnum.beginner)
        db_session.add(entry)
        await db_session.commit()
        await db_session.refresh(entry)

        assert entry.status == DuelQueueStatusEnum.waiting
        assert entry.duel_id is None

    async def test_matching_sets_status_and_links_the_duel(self, db_session):
        problem = DuelProblem(exercise_id=CODE_EXERCISE_ID, difficulty=DifficultyEnum.beginner)
        db_session.add(problem)
        await db_session.flush()

        user_a, user_b = await _real_user_ids(db_session)
        now = datetime.utcnow()
        duel = Duel(duel_problem_id=problem.id, started_at=now, ends_at=now + timedelta(minutes=10))
        db_session.add(duel)
        await db_session.flush()

        entry_a = DuelQueueEntry(user_id=user_a, difficulty=DifficultyEnum.beginner)
        entry_b = DuelQueueEntry(user_id=user_b, difficulty=DifficultyEnum.beginner)
        db_session.add_all([entry_a, entry_b])
        await db_session.flush()

        entry_a.status = DuelQueueStatusEnum.matched
        entry_a.duel_id = duel.id
        entry_b.status = DuelQueueStatusEnum.matched
        entry_b.duel_id = duel.id
        await db_session.commit()

        await db_session.refresh(entry_a)
        await db_session.refresh(entry_b)
        assert entry_a.duel_id == entry_b.duel_id == duel.id
        assert entry_a.status == DuelQueueStatusEnum.matched


class TestDuelProblemSeeder:
    """The curated pool itself. setup_database (session-scoped, see
    conftest.py) already runs the real seed_all() once, which includes
    seed_duel_problems -- these confirm that run actually produced the
    curated rows, and that the seeder is safe to run again (idempotent) and
    safe against a stale/missing exercise id (skips, doesn't crash)."""

    async def test_the_real_session_seed_produced_every_curated_problem(self, db_session):
        result = await db_session.execute(select(DuelProblem))
        seeded = {p.exercise_id: p.difficulty for p in result.scalars().all()}
        for exercise_id, difficulty in DUEL_PROBLEMS:
            assert exercise_id in seeded, f"exercise_id={exercise_id} was not seeded"
            assert seeded[exercise_id] == difficulty

    async def test_rerunning_the_seeder_adds_nothing_new(self, db_session):
        before = (await db_session.execute(select(DuelProblem))).scalars().all()
        added = await seed_duel_problems(db_session)
        await db_session.commit()
        after = (await db_session.execute(select(DuelProblem))).scalars().all()

        assert added == 0
        assert len(after) == len(before)

    async def test_a_nonexistent_exercise_id_is_skipped_not_a_crash(self, db_session, monkeypatch):
        import app.seed.duel_problems as duel_problems_module

        monkeypatch.setattr(
            duel_problems_module,
            "DUEL_PROBLEMS",
            ((999999, DifficultyEnum.beginner),),
        )
        added = await seed_duel_problems(db_session)
        await db_session.commit()

        assert added == 0
        result = await db_session.execute(
            select(DuelProblem).where(DuelProblem.exercise_id == 999999)
        )
        assert result.scalar_one_or_none() is None
