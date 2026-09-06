"""Avatar upload and generated-avatar config.

None of these should let a user act on someone else's account or accept
unvalidated image input.
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
