import pytest
from httpx import AsyncClient


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