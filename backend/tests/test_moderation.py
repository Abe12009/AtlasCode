"""Reporting and the minimal staff/admin moderation endpoints."""

from sqlalchemy import select

from app.models import Report, User


async def _make_staff(db_session, username: str) -> None:
    result = await db_session.execute(select(User).where(User.username == username))
    user = result.scalar_one()
    user.is_staff = True
    await db_session.commit()


class TestReportUser:
    async def test_reporting_a_public_profile_succeeds(self, client, test_user, second_user):
        await client.patch(
            "/auth/me", headers=test_user["headers"], json={"profile_visibility": "public"}
        )

        response = await client.post(
            f"/users/{test_user['data']['username']}/report",
            headers=second_user["headers"],
            json={"reason": "harassment", "details": "left a rude comment"},
        )
        assert response.status_code == 204

    async def test_reporting_yourself_is_allowed_and_pointless(self, client, test_user):
        response = await client.post(
            f"/users/{test_user['data']['username']}/report",
            headers=test_user["headers"],
            json={"reason": "other"},
        )
        assert response.status_code == 204

    async def test_reporting_a_private_profile_404s(self, client, test_user, second_user):
        # test_user defaults to private (never toggled public in this test).
        response = await client.post(
            f"/users/{test_user['data']['username']}/report",
            headers=second_user["headers"],
            json={"reason": "spam"},
        )
        assert response.status_code == 404

    async def test_reporting_a_nonexistent_user_404s(self, client, second_user):
        response = await client.post(
            "/users/no-such-user-at-all/report",
            headers=second_user["headers"],
            json={"reason": "spam"},
        )
        assert response.status_code == 404

    async def test_rate_limit_per_reporter(self, client, test_user, second_user):
        await client.patch(
            "/auth/me", headers=test_user["headers"], json={"profile_visibility": "public"}
        )
        for _ in range(5):
            response = await client.post(
                f"/users/{test_user['data']['username']}/report",
                headers=second_user["headers"],
                json={"reason": "spam"},
            )
            assert response.status_code == 204

        response = await client.post(
            f"/users/{test_user['data']['username']}/report",
            headers=second_user["headers"],
            json={"reason": "spam"},
        )
        assert response.status_code == 429


class TestAdminAccessControl:
    async def test_non_staff_user_gets_404_not_403(self, client, test_user):
        """404, not 403 -- a non-staff account probing for admin routes
        learns nothing about whether they exist."""
        response = await client.get("/admin/reports", headers=test_user["headers"])
        assert response.status_code == 404

    async def test_unauthenticated_request_is_rejected(self, client):
        response = await client.get("/admin/reports")
        assert response.status_code == 401


class TestAdminReportReview:
    async def test_staff_can_list_and_resolve_reports(
        self, client, test_user, second_user, db_session
    ):
        await client.patch(
            "/auth/me", headers=test_user["headers"], json={"profile_visibility": "public"}
        )
        await client.post(
            f"/users/{test_user['data']['username']}/report",
            headers=second_user["headers"],
            json={"reason": "inappropriate_username"},
        )
        await _make_staff(db_session, second_user["data"]["username"])

        listing = await client.get("/admin/reports", headers=second_user["headers"])
        assert listing.status_code == 200
        open_reports = listing.json()
        assert any(r["reported_username"] == test_user["data"]["username"] for r in open_reports)
        report_id = next(r["id"] for r in open_reports if r["reported_username"] == test_user["data"]["username"])

        resolved = await client.post(
            f"/admin/reports/{report_id}/resolve",
            headers=second_user["headers"],
            json={"resolution_note": "Warned the user."},
        )
        assert resolved.status_code == 200
        body = resolved.json()
        assert body["status"] == "resolved"
        assert body["resolution_note"] == "Warned the user."

        still_open = await client.get("/admin/reports", headers=second_user["headers"])
        assert not any(r["id"] == report_id for r in still_open.json())


class TestAdminUserActions:
    async def test_suspend_blocks_further_requests_immediately(
        self, client, test_user, second_user, db_session
    ):
        await _make_staff(db_session, second_user["data"]["username"])
        me = await client.get("/auth/me", headers=test_user["headers"])
        target_id = me.json()["id"]

        suspend = await client.post(f"/admin/users/{target_id}/suspend", headers=second_user["headers"])
        assert suspend.status_code == 204

        blocked = await client.get("/auth/me", headers=test_user["headers"])
        assert blocked.status_code == 403
        assert blocked.json()["detail"] == "This account has been disabled"

    async def test_reinstate_restores_access(self, client, test_user, second_user, db_session):
        await _make_staff(db_session, second_user["data"]["username"])
        me = await client.get("/auth/me", headers=test_user["headers"])
        target_id = me.json()["id"]

        await client.post(f"/admin/users/{target_id}/suspend", headers=second_user["headers"])
        reinstate = await client.post(f"/admin/users/{target_id}/reinstate", headers=second_user["headers"])
        assert reinstate.status_code == 204

        restored = await client.get("/auth/me", headers=test_user["headers"])
        assert restored.status_code == 200

    async def test_clear_avatar_nulls_every_avatar_field(self, client, test_user, second_user, db_session):
        await _make_staff(db_session, second_user["data"]["username"])
        upload = await client.post(
            "/auth/me/avatar",
            headers=test_user["headers"],
            json={
                "data_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            },
        )
        assert upload.status_code == 200

        me = await client.get("/auth/me", headers=test_user["headers"])
        target_id = me.json()["id"]

        cleared = await client.post(f"/admin/users/{target_id}/clear-avatar", headers=second_user["headers"])
        assert cleared.status_code == 204

        after = await client.get("/auth/me", headers=test_user["headers"])
        body = after.json()
        assert body["avatar_image_data"] is None
        assert body["avatar_url"] is None
        assert body["avatar_config"] is None
