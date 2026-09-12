"""Password reset by email: /auth/forgot-password and /auth/reset-password."""

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest

from app.core.config import get_settings
from app.core.security import create_access_token
from app.services import password_reset as password_reset_service

settings = get_settings()


@pytest.fixture(autouse=True)
def _email_configured(monkeypatch):
    """Every test in this file runs as if Resend were configured, unless a
    test explicitly overrides it (see test_forgot_password_email_not_configured).
    """
    monkeypatch.setattr(settings, "resend_api_key", "re_test_key")
    yield


@pytest.fixture
def mock_send_email(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("app.api.auth.send_password_reset_email", mock)
    return mock


class TestForgotPassword:
    async def test_existing_local_password_user_sends_email(self, client, test_user, mock_send_email):
        response = await client.post(
            "/auth/forgot-password", json={"email": test_user["data"]["email"]}
        )
        assert response.status_code == 204
        mock_send_email.assert_awaited_once()
        called_email, called_url = mock_send_email.await_args.args
        assert called_email == test_user["data"]["email"]
        assert "/reset-password?token=" in called_url

    async def test_unknown_email_gives_same_response_and_sends_nothing(self, client, mock_send_email):
        response = await client.post(
            "/auth/forgot-password", json={"email": "nobody-here@example.com"}
        )
        assert response.status_code == 204
        mock_send_email.assert_not_awaited()

    async def test_federated_only_account_sends_nothing(self, client, db_session, mock_send_email):
        from app.models import AuthProviderEnum, User

        user = User(
            email="federated-only@example.com",
            username="federated_only_user",
            hashed_password=None,
            firebase_uid="firebase-uid-123",
            auth_provider=AuthProviderEnum.google.value,
        )
        db_session.add(user)
        await db_session.commit()

        response = await client.post(
            "/auth/forgot-password", json={"email": "federated-only@example.com"}
        )
        assert response.status_code == 204
        mock_send_email.assert_not_awaited()

    async def test_email_not_configured_returns_503(self, client, test_user, mock_send_email, monkeypatch):
        monkeypatch.setattr(settings, "resend_api_key", "")
        response = await client.post(
            "/auth/forgot-password", json={"email": test_user["data"]["email"]}
        )
        assert response.status_code == 503
        mock_send_email.assert_not_awaited()

    async def test_rate_limit_per_email(self, client, test_user, mock_send_email, monkeypatch):
        monkeypatch.setattr(settings, "password_reset_rate_limit_per_email_per_hour", 2)
        email = test_user["data"]["email"]
        for _ in range(2):
            response = await client.post("/auth/forgot-password", json={"email": email})
            assert response.status_code == 204
        response = await client.post("/auth/forgot-password", json={"email": email})
        assert response.status_code == 429


class TestResetPassword:
    async def test_valid_token_resets_password_and_old_password_stops_working(
        self, client, test_user, db_session
    ):
        from sqlalchemy import select

        from app.models import User

        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()
        token = password_reset_service.create_password_reset_token(user)

        response = await client.post(
            "/auth/reset-password", json={"token": token, "new_password": "brand-new-password-1"}
        )
        assert response.status_code == 204

        old_login = await client.post(
            "/auth/login",
            json={"email": test_user["data"]["email"], "password": test_user["data"]["password"]},
        )
        assert old_login.status_code == 401

        new_login = await client.post(
            "/auth/login",
            json={"email": test_user["data"]["email"], "password": "brand-new-password-1"},
        )
        assert new_login.status_code == 200

    async def test_expired_token_rejected(self, client, test_user, db_session):
        from sqlalchemy import select

        from app.models import User

        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()
        expired_token = create_access_token(
            data={
                "sub": user.id,
                "purpose": "password_reset",
                "pwf": password_reset_service._password_fingerprint(user.hashed_password),
            },
            expires_delta=timedelta(minutes=-1),
        )

        response = await client.post(
            "/auth/reset-password",
            json={"token": expired_token, "new_password": "another-new-password-1"},
        )
        assert response.status_code == 400

    async def test_tampered_token_rejected(self, client, test_user, db_session):
        from sqlalchemy import select

        from app.models import User

        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()
        token = password_reset_service.create_password_reset_token(user)
        tampered = token[:-1] + ("a" if token[-1] != "a" else "b")

        response = await client.post(
            "/auth/reset-password", json={"token": tampered, "new_password": "another-new-password-1"}
        )
        assert response.status_code == 400

    async def test_token_cannot_be_reused_after_password_already_changed(
        self, client, test_user, db_session
    ):
        from sqlalchemy import select

        from app.models import User

        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()
        token = password_reset_service.create_password_reset_token(user)

        first = await client.post(
            "/auth/reset-password", json={"token": token, "new_password": "first-new-password-1"}
        )
        assert first.status_code == 204

        second = await client.post(
            "/auth/reset-password", json={"token": token, "new_password": "second-new-password-1"}
        )
        assert second.status_code == 400

    async def test_reset_token_cannot_be_used_as_a_session_token(self, client, test_user, db_session):
        """Security regression: a single-purpose reset token must never
        authenticate a normal request, even though it's minted by the same
        create_access_token used for real session tokens.
        """
        from sqlalchemy import select

        from app.models import User

        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()
        token = password_reset_service.create_password_reset_token(user)

        response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
