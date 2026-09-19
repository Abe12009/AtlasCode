import pytest
from httpx import AsyncClient

from app.core.config import get_settings

settings = get_settings()


class TestAuth:
    async def test_register_success(self, client: AsyncClient):
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "preferred_language": "en"
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        user_data = {
            "email": test_user["data"]["email"],
            "username": "different",
            "password": "password123",
            "preferred_language": "en"
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        user_data = {
            "email": "different@example.com",
            "username": test_user["data"]["username"],
            "password": "password123",
            "preferred_language": "en"
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_login_success(self, client: AsyncClient, test_user):
        credentials = {
            "email": test_user["data"]["email"],
            "password": test_user["data"]["password"]
        }
        response = await client.post("/auth/login", json=credentials)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_incorrect_password(self, client: AsyncClient, test_user):
        credentials = {
            "email": test_user["data"]["email"],
            "password": "wrongpassword"
        }
        response = await client.post("/auth/login", json=credentials)
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        credentials = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        response = await client.post("/auth/login", json=credentials)
        assert response.status_code == 401

    async def test_login_rate_limit_per_email(self, client: AsyncClient, test_user, monkeypatch):
        monkeypatch.setattr(settings, "auth_login_rate_limit_per_email_per_hour", 2)
        credentials = {"email": test_user["data"]["email"], "password": "wrongpassword"}
        for _ in range(2):
            response = await client.post("/auth/login", json=credentials)
            assert response.status_code == 401
        response = await client.post("/auth/login", json=credentials)
        assert response.status_code == 429

    async def test_register_rate_limit_per_ip(self, client: AsyncClient, db_session, monkeypatch):
        # httpx's ASGITransport reports every test request as the same fixed
        # IP, so earlier tests in this session-scoped-DB suite have already
        # logged AuthAttempt rows against it -- clear those first so this
        # test's own count starts from zero, regardless of test order.
        from sqlalchemy import delete
        from app.models import AuthAttempt
        await db_session.execute(delete(AuthAttempt).where(AuthAttempt.kind == "register"))
        await db_session.commit()

        monkeypatch.setattr(settings, "auth_register_rate_limit_per_ip_per_hour", 2)
        for i in range(2):
            response = await client.post("/auth/register", json={
                "email": f"ratelimit{i}@example.com",
                "username": f"ratelimit{i}",
                "password": "password123",
                "preferred_language": "en",
            })
            assert response.status_code == 200
        response = await client.post("/auth/register", json={
            "email": "ratelimit-overflow@example.com",
            "username": "ratelimitoverflow",
            "password": "password123",
            "preferred_language": "en",
        })
        assert response.status_code == 429

    async def test_get_me_authenticated(self, client: AsyncClient, test_user):
        response = await client.get("/auth/me", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["data"]["email"]
        assert data["username"] == test_user["data"]["username"]

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/auth/me")
        assert response.status_code == 401

    async def test_update_me(self, client: AsyncClient, test_user):
        response = await client.patch("/auth/me", headers=test_user["headers"], json={
            "username": "updateduser"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updateduser"

    async def test_get_profile(self, client: AsyncClient, test_user):
        response = await client.get("/auth/profile", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "xp" in data
        assert "level" in data

    async def test_invalid_token(self, client: AsyncClient):
        response = await client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401

    async def test_isolation_between_users(self, client: AsyncClient, test_user, second_user):
        response1 = await client.get("/auth/me", headers=test_user["headers"])
        response2 = await client.get("/auth/me", headers=second_user["headers"])
        assert response1.json()["id"] != response2.json()["id"]