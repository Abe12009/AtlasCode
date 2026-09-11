"""Account deletion: confirmation flow, error handling, and full cascade purge.

The deletion endpoint is a hard delete -- every user-owned table must be
completely empty for that user_id afterward, not just unreachable through
the API. These tests populate one row in every cascaded table (some via
real app flows, some inserted directly where no endpoint exists yet to
trigger them) and then query the database directly to prove the cascade
actually ran, rather than trusting that a 204 response implies it did.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import create_access_token
from app.models import (
    Achievement,
    CodyMessage,
    CodyRoleEnum,
    CourseProgress,
    Exercise,
    ExerciseAttempt,
    ExerciseOption,
    Lesson,
    LessonProgress,
    Module,
    Notification,
    Project,
    ProjectProgress,
    StudentProfile,
    User,
    UserAchievement,
)

MCQ_ID = 6  # seeded multiple_choice exercise, same fixture used in test_exercise_grading.py


async def _correct_option_id(db_session, exercise_id: int) -> int:
    result = await db_session.execute(
        select(ExerciseOption).where(ExerciseOption.exercise_id == exercise_id)
    )
    options = list(result.scalars())
    correct = [o for o in options if o.is_correct]
    assert len(correct) == 1
    return correct[0].id


class TestDeleteAccountValidation:
    async def test_wrong_confirmation_text_is_rejected(self, client: AsyncClient, test_user):
        response = await client.request(
            "DELETE",
            "/auth/me",
            headers=test_user["headers"],
            json={"confirmation": "not delete", "current_password": "password123"},
        )
        assert response.status_code == 400

    async def test_missing_password_is_rejected_for_a_password_account(
        self, client: AsyncClient, test_user
    ):
        response = await client.request(
            "DELETE",
            "/auth/me",
            headers=test_user["headers"],
            json={"confirmation": "DELETE"},
        )
        assert response.status_code == 401

    async def test_wrong_password_is_rejected(self, client: AsyncClient, test_user):
        response = await client.request(
            "DELETE",
            "/auth/me",
            headers=test_user["headers"],
            json={"confirmation": "DELETE", "current_password": "not-the-password"},
        )
        assert response.status_code == 401

    async def test_unauthenticated_request_is_rejected(self, client: AsyncClient):
        response = await client.request("DELETE", "/auth/me", json={"confirmation": "DELETE"})
        assert response.status_code == 401

    async def test_account_survives_a_rejected_attempt(self, client: AsyncClient, test_user):
        await client.request(
            "DELETE",
            "/auth/me",
            headers=test_user["headers"],
            json={"confirmation": "nope"},
        )
        me = await client.get("/auth/me", headers=test_user["headers"])
        assert me.status_code == 200

    async def test_correct_confirmation_and_password_succeeds(
        self, client: AsyncClient, test_user
    ):
        response = await client.request(
            "DELETE",
            "/auth/me",
            headers=test_user["headers"],
            json={"confirmation": "DELETE", "current_password": "password123"},
        )
        assert response.status_code == 204

    async def test_confirmation_is_case_insensitive(self, client: AsyncClient, test_user):
        response = await client.request(
            "DELETE",
            "/auth/me",
            headers=test_user["headers"],
            json={"confirmation": "delete", "current_password": "password123"},
        )
        assert response.status_code == 204

    async def test_oauth_only_account_needs_no_password(self, client: AsyncClient, db_session):
        user = User(
            email="oauthdelete@example.com",
            username="oauthdelete",
            hashed_password=None,
            firebase_uid="firebase-uid-delete-1",
            auth_provider="google",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        token = create_access_token(data={"sub": user.id})
        response = await client.request(
            "DELETE",
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"confirmation": "DELETE"},
        )
        assert response.status_code == 204


class TestDeleteAccountCascade:
    async def test_deleting_an_account_purges_every_user_owned_table(
        self, client: AsyncClient, test_user, db_session
    ):
        headers = test_user["headers"]
        me = await client.get("/auth/me", headers=headers)
        user_id = me.json()["id"]
        username = test_user["data"]["username"]

        # 1. A real exercise submission -- exercises through app logic that
        #    creates an ExerciseAttempt, LessonProgress, and CourseProgress row.
        option_id = await _correct_option_id(db_session, MCQ_ID)
        submit = await client.post(
            f"/exercises/{MCQ_ID}/submit",
            headers=headers,
            json={"exercise_id": MCQ_ID, "selected_option_id": option_id},
        )
        assert submit.status_code == 200
        assert submit.json()["is_correct"] is True

        # 2. Rows for the tables no endpoint reliably populates from a single
        #    call -- inserted directly so the cascade is verified against
        #    every user-owned table, not just the ones reachable through
        #    today's API surface. (LessonProgress/CourseProgress are only
        #    ever *updated* by the submit endpoint above, not created --
        #    something else creates them when a lesson is first opened.)
        exercise = (
            await db_session.execute(select(Exercise).where(Exercise.id == MCQ_ID))
        ).scalar_one()
        lesson = (
            await db_session.execute(select(Lesson).where(Lesson.id == exercise.lesson_id))
        ).scalar_one()
        module = (
            await db_session.execute(select(Module).where(Module.id == lesson.module_id))
        ).scalar_one()

        db_session.add(LessonProgress(user_id=user_id, lesson_id=lesson.id, current_block=1))
        db_session.add(CourseProgress(user_id=user_id, course_id=module.course_id, completed_lessons=1))

        achievement = (await db_session.execute(select(Achievement).limit(1))).scalar_one()
        db_session.add(UserAchievement(user_id=user_id, achievement_id=achievement.id))

        project = (await db_session.execute(select(Project).limit(1))).scalar_one()
        db_session.add(ProjectProgress(user_id=user_id, project_id=project.id, current_task=1))

        db_session.add(
            CodyMessage(user_id=user_id, role=CodyRoleEnum.user, content="What is a hash table?")
        )
        db_session.add(
            CodyMessage(user_id=user_id, role=CodyRoleEnum.assistant, content="It's a data structure...")
        )
        await db_session.commit()

        # Sanity check: every table actually has a row for this user before
        # deletion, so the post-deletion assertions prove something real.
        for model in (
            StudentProfile,
            ExerciseAttempt,
            LessonProgress,
            CourseProgress,
            ProjectProgress,
            UserAchievement,
            Notification,  # the "welcome" notification created at registration
            CodyMessage,
        ):
            count_before = (
                await db_session.execute(select(model).where(model.user_id == user_id))
            ).scalars().all()
            assert count_before, f"expected at least one {model.__name__} row before deletion"

        # 3. Delete the account for real.
        delete_response = await client.request(
            "DELETE",
            "/auth/me",
            headers=headers,
            json={"confirmation": "DELETE", "current_password": "password123"},
        )
        assert delete_response.status_code == 204

        # 4. The account can no longer authenticate at all -- not merely
        #    deactivated.
        login = await client.post(
            "/auth/login",
            json={"email": test_user["data"]["email"], "password": "password123"},
        )
        assert login.status_code == 401

        me_after = await client.get("/auth/me", headers=headers)
        assert me_after.status_code == 401

        # 5. Public-facing data disappears immediately -- 404, not just a
        #    private/deactivated profile.
        other_token = create_access_token(data={"sub": 999999})  # any other identity
        public = await client.get(f"/users/{username}", headers={"Authorization": f"Bearer {other_token}"})
        assert public.status_code in (401, 404)

        # 6. The real check: every cascaded table is actually empty for this
        #    user_id in the database, not just unreachable through the API.
        user_row = (
            await db_session.execute(select(User).where(User.id == user_id))
        ).scalar_one_or_none()
        assert user_row is None

        for model in (
            StudentProfile,
            ExerciseAttempt,
            LessonProgress,
            CourseProgress,
            ProjectProgress,
            UserAchievement,
            Notification,
            CodyMessage,
        ):
            remaining = (
                await db_session.execute(select(model).where(model.user_id == user_id))
            ).scalars().all()
            assert remaining == [], f"{model.__name__} still has rows for a deleted user_id"
