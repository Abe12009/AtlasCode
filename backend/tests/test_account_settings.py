"""Password change, avatar (upload + generated), and public profile privacy.

None of these should let a user act on someone else's account, leak private
data, or accept unvalidated image input.
"""

import base64

import pytest
from httpx import AsyncClient

# The smallest possible valid PNG (1x1, transparent) — real image bytes, not a
# placeholder string, so mime-sniffing-adjacent checks have something real to
# decode.
_TINY_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)
_TINY_PNG_DATA_URL = f"data:image/png;base64,{base64.b64encode(_TINY_PNG_BYTES).decode()}"


class TestChangePassword:
    async def test_correct_current_password_changes_it(self, client: AsyncClient, test_user):
        response = await client.post(
            "/auth/change-password",
            headers=test_user["headers"],
            json={"current_password": "password123", "new_password": "newpassword456"},
        )
        assert response.status_code == 204

        # Old password no longer works, new one does.
        old = await client.post(
            "/auth/login",
            json={"email": test_user["data"]["email"], "password": "password123"},
        )
        assert old.status_code == 401

        new = await client.post(
            "/auth/login",
            json={"email": test_user["data"]["email"], "password": "newpassword456"},
        )
        assert new.status_code == 200

    async def test_wrong_current_password_is_rejected(self, client: AsyncClient, second_user):
        response = await client.post(
            "/auth/change-password",
            headers=second_user["headers"],
            json={"current_password": "not-the-password", "new_password": "newpassword456"},
        )
        assert response.status_code == 401

    async def test_unauthenticated_request_is_rejected(self, client: AsyncClient):
        response = await client.post(
            "/auth/change-password",
            json={"current_password": "password123", "new_password": "newpassword456"},
        )
        assert response.status_code == 401

    async def test_oauth_only_account_cannot_change_a_password_it_does_not_have(
        self, client: AsyncClient, db_session
    ):
        from sqlalchemy import select
        from app.core.security import create_access_token
        from app.models import User

        # An account with no hashed_password, as a Firebase-only sign-in would have.
        user = User(
            email="oauthonly@example.com",
            username="oauthonly",
            hashed_password=None,
            firebase_uid="firebase-uid-1",
            auth_provider="google",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        token = create_access_token(data={"sub": user.id})
        response = await client.post(
            "/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "anything", "new_password": "newpassword456"},
        )
        assert response.status_code == 400


class TestAvatarUpload:
    async def test_valid_png_is_accepted(self, client: AsyncClient, test_user):
        response = await client.post(
            "/auth/me/avatar",
            headers=test_user["headers"],
            json={"data_url": _TINY_PNG_DATA_URL},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["avatar_type"] == "upload"
        assert body["avatar_image_data"] == _TINY_PNG_DATA_URL

    async def test_disallowed_mime_type_is_rejected(self, client: AsyncClient, test_user):
        svg_data_url = "data:image/svg+xml;base64," + base64.b64encode(b"<svg></svg>").decode()
        response = await client.post(
            "/auth/me/avatar",
            headers=test_user["headers"],
            json={"data_url": svg_data_url},
        )
        assert response.status_code == 400

    async def test_malformed_data_url_is_rejected(self, client: AsyncClient, test_user):
        response = await client.post(
            "/auth/me/avatar",
            headers=test_user["headers"],
            json={"data_url": "not-a-data-url-at-all-but-long-enough-to-pass-min-length"},
        )
        assert response.status_code == 400

    async def test_oversized_image_is_rejected(self, client: AsyncClient, test_user):
        # 600KB of raw bytes, well over the 500KB server-side cap, so the
        # cap is enforced on decoded size and not merely trusted from the client.
        big_bytes = b"\x00" * 600_000
        data_url = "data:image/png;base64," + base64.b64encode(big_bytes).decode()
        response = await client.post(
            "/auth/me/avatar",
            headers=test_user["headers"],
            json={"data_url": data_url},
        )
        assert response.status_code == 400

    async def test_unauthenticated_upload_is_rejected(self, client: AsyncClient):
        response = await client.post("/auth/me/avatar", json={"data_url": _TINY_PNG_DATA_URL})
        assert response.status_code == 401


class TestGeneratedAvatarConfig:
    async def test_setting_avatar_config_then_switching_to_generated_works(
        self, client: AsyncClient, test_user
    ):
        config = await client.patch(
            "/auth/me",
            headers=test_user["headers"],
            json={"avatar_config": '{"skinTone": "3", "hair": "short"}'},
        )
        assert config.status_code == 200

        switch = await client.patch(
            "/auth/me", headers=test_user["headers"], json={"avatar_type": "generated"}
        )
        assert switch.status_code == 200
        assert switch.json()["avatar_type"] == "generated"

    async def test_invalid_json_config_is_rejected(self, client: AsyncClient, test_user):
        response = await client.patch(
            "/auth/me",
            headers=test_user["headers"],
            json={"avatar_config": "{not valid json"},
        )
        assert response.status_code == 400

    async def test_cannot_switch_to_generated_before_building_one(
        self, client: AsyncClient, second_user
    ):
        response = await client.patch(
            "/auth/me", headers=second_user["headers"], json={"avatar_type": "generated"}
        )
        assert response.status_code == 400


class TestPublicProfilePrivacy:
    async def test_profile_defaults_to_private(self, client: AsyncClient, test_user):
        me = await client.get("/auth/me", headers=test_user["headers"])
        assert me.json()["profile_visibility"] == "private"

    async def test_private_profile_is_not_visible_to_other_users(
        self, client: AsyncClient, test_user, second_user
    ):
        response = await client.get(
            f"/users/{test_user['data']['username']}", headers=second_user["headers"]
        )
        assert response.status_code == 404

    async def test_private_profile_is_visible_to_its_owner(self, client: AsyncClient, test_user):
        response = await client.get(
            f"/users/{test_user['data']['username']}", headers=test_user["headers"]
        )
        assert response.status_code == 200

    async def test_public_profile_is_visible_to_other_users(
        self, client: AsyncClient, test_user, second_user
    ):
        toggle = await client.patch(
            "/auth/me", headers=test_user["headers"], json={"profile_visibility": "public"}
        )
        assert toggle.status_code == 200

        response = await client.get(
            f"/users/{test_user['data']['username']}", headers=second_user["headers"]
        )
        assert response.status_code == 200
        body = response.json()
        assert body["username"] == test_user["data"]["username"]
        assert set(body.keys()) == {
            "username",
            "avatar_url",
            "avatar_image_data",
            "avatar_config",
            "avatar_type",
            "level",
            "xp",
            "streak",
            "member_since",
            "achievements",
        }

    async def test_nonexistent_user_is_404(self, client: AsyncClient, test_user):
        response = await client.get("/users/no-such-user-abc123", headers=test_user["headers"])
        assert response.status_code == 404

    async def test_unauthenticated_request_is_rejected(self, client: AsyncClient, test_user):
        response = await client.get(f"/users/{test_user['data']['username']}")
        assert response.status_code == 401
