"""In-app feedback: submission, rate limiting, and the staff-gated listing."""

from sqlalchemy import select

from app.core.config import get_settings
from app.models import FeedbackSubmission, User

settings = get_settings()


async def _make_staff(db_session, username: str) -> None:
    result = await db_session.execute(select(User).where(User.username == username))
    user = result.scalar_one()
    user.is_staff = True
    await db_session.commit()


class TestSubmitFeedback:
    async def test_authenticated_submission_succeeds_and_is_scoped_to_the_user(
        self, client, test_user, db_session
    ):
        response = await client.post(
            "/feedback",
            headers=test_user["headers"],
            json={"category": "bug", "message": "the run button does nothing", "page_path": "/app/dashboard"},
        )
        assert response.status_code == 204

        result = await db_session.execute(
            select(FeedbackSubmission).order_by(FeedbackSubmission.id.desc())
        )
        row = result.scalars().first()
        assert row.message == "the run button does nothing"
        assert row.category.value == "bug"
        assert row.page_path == "/app/dashboard"
        assert row.user_agent is not None

        user_result = await db_session.execute(
            select(User).where(User.username == test_user["data"]["username"])
        )
        assert row.user_id == user_result.scalar_one().id

    async def test_anonymous_submission_succeeds_with_no_user_id(self, client, db_session):
        response = await client.post(
            "/feedback",
            json={"category": "suggestion", "message": "add dark mode to the code editor"},
        )
        assert response.status_code == 204

        result = await db_session.execute(
            select(FeedbackSubmission).order_by(FeedbackSubmission.id.desc())
        )
        row = result.scalars().first()
        assert row.user_id is None
        assert row.message == "add dark mode to the code editor"

    async def test_default_category_is_other(self, client, test_user):
        response = await client.post(
            "/feedback", headers=test_user["headers"], json={"message": "just a note"}
        )
        assert response.status_code == 204

    async def test_rate_limit_per_user(self, client, test_user, monkeypatch):
        monkeypatch.setattr(settings, "feedback_rate_limit_per_hour", 2)

        for _ in range(2):
            response = await client.post(
                "/feedback", headers=test_user["headers"], json={"message": "spam attempt"}
            )
            assert response.status_code == 204

        response = await client.post(
            "/feedback", headers=test_user["headers"], json={"message": "one too many"}
        )
        assert response.status_code == 429

    async def test_rate_limit_does_not_affect_a_different_user(
        self, client, test_user, second_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "feedback_rate_limit_per_hour", 1)

        first = await client.post(
            "/feedback", headers=test_user["headers"], json={"message": "hit my own limit"}
        )
        assert first.status_code == 204

        second = await client.post(
            "/feedback", headers=second_user["headers"], json={"message": "different user, fresh limit"}
        )
        assert second.status_code == 204


class TestAdminFeedbackEndpoint:
    async def test_staff_can_list_feedback(self, client, test_user, db_session):
        await _make_staff(db_session, test_user["data"]["username"])
        await client.post(
            "/feedback", headers=test_user["headers"], json={"category": "bug", "message": "listed by staff"}
        )

        response = await client.get("/admin/feedback", headers=test_user["headers"])
        assert response.status_code == 200
        messages = [row["message"] for row in response.json()]
        assert "listed by staff" in messages

    async def test_non_staff_gets_404_not_403(self, client, second_user):
        response = await client.get("/admin/feedback", headers=second_user["headers"])
        assert response.status_code == 404
