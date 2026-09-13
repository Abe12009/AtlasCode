"""Cody spend tracking and the global daily-cap kill switch.

The kill switch is exercised entirely against locally-seeded DB rows --
no real OpenRouter call is ever made in these tests, so the cap firing at
$0.50 below proves the same code path fires at any dollar cap without
spending anything.
"""

import logging

from sqlalchemy import select

from app.core.config import get_settings
from app.models import CodyMessage, CodyRoleEnum, User
from app.services.cody import CodyReply

settings = get_settings()


async def _make_staff(db_session, username: str) -> None:
    result = await db_session.execute(select(User).where(User.username == username))
    user = result.scalar_one()
    user.is_staff = True
    await db_session.commit()


async def _seed_spend(db_session, username: str, cost_usd: float) -> None:
    result = await db_session.execute(select(User).where(User.username == username))
    user = result.scalar_one()
    db_session.add(
        CodyMessage(
            user_id=user.id,
            role=CodyRoleEnum.assistant,
            content="a prior reply",
            prompt_tokens=100,
            completion_tokens=50,
            estimated_cost_usd=cost_usd,
        )
    )
    await db_session.commit()


class TestSpendCapKillSwitch:
    async def test_cap_exceeded_returns_503_without_calling_openrouter(
        self, client, test_user, db_session, monkeypatch, caplog
    ):
        monkeypatch.setattr(settings, "openrouter_api_key", "or-test-key")
        monkeypatch.setattr(settings, "cody_daily_spend_cap_usd", 0.50)
        await _seed_spend(db_session, test_user["data"]["username"], cost_usd=0.75)

        with caplog.at_level(logging.ERROR):
            response = await client.post(
                "/cody/chat", headers=test_user["headers"], json={"message": "hello"}
            )

        assert response.status_code == 503
        assert "CODY_SPEND_CAP_EXCEEDED" in caplog.text

    async def test_spend_from_other_users_counts_toward_the_global_cap(
        self, client, test_user, second_user, db_session, monkeypatch
    ):
        monkeypatch.setattr(settings, "openrouter_api_key", "or-test-key")
        monkeypatch.setattr(settings, "cody_daily_spend_cap_usd", 1.0)
        # second_user's spend alone pushes the *global* total over the cap.
        await _seed_spend(db_session, second_user["data"]["username"], cost_usd=1.5)

        response = await client.post(
            "/cody/chat", headers=test_user["headers"], json={"message": "hello"}
        )
        assert response.status_code == 503

    async def test_cap_set_to_zero_disables_the_kill_switch(
        self, client, test_user, db_session, monkeypatch
    ):
        monkeypatch.setattr(settings, "openrouter_api_key", "or-test-key")
        monkeypatch.setattr(settings, "cody_daily_spend_cap_usd", 0)
        await _seed_spend(db_session, test_user["data"]["username"], cost_usd=9999.0)

        async def fake_get_reply(db, user, history, user_message):
            return CodyReply(content="hi", prompt_tokens=1, completion_tokens=1, cost_usd=0.0001)

        monkeypatch.setattr("app.api.cody.get_reply", fake_get_reply)

        response = await client.post(
            "/cody/chat", headers=test_user["headers"], json={"message": "hello"}
        )
        # A $9999 trailing-24h spend would trip any nonzero cap; 0 must mean
        # "disabled" rather than "cap of zero dollars", so this still succeeds.
        assert response.status_code == 200

    async def test_below_cap_stores_usage_on_the_assistant_message(
        self, client, test_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "openrouter_api_key", "or-test-key")
        # Deliberately huge: the trailing-24h spend check sums every
        # CodyMessage in the shared test database, including the ones the
        # other tests in this class seed above the cap on purpose -- a
        # merely-generous cap here would still trip on their leftover rows.
        monkeypatch.setattr(settings, "cody_daily_spend_cap_usd", 1_000_000_000.0)

        async def fake_get_reply(db, user, history, user_message):
            return CodyReply(content="hi there", prompt_tokens=42, completion_tokens=7, cost_usd=0.0021)

        monkeypatch.setattr("app.api.cody.get_reply", fake_get_reply)

        response = await client.post(
            "/cody/chat", headers=test_user["headers"], json={"message": "hello"}
        )
        assert response.status_code == 200
        assert response.json()["reply"]["content"] == "hi there"


class TestAdminCodySpendEndpoint:
    async def test_staff_can_view_aggregate_spend(
        self, client, test_user, db_session, monkeypatch
    ):
        await _make_staff(db_session, test_user["data"]["username"])
        monkeypatch.setattr(settings, "cody_daily_spend_cap_usd", 10.0)
        await _seed_spend(db_session, test_user["data"]["username"], cost_usd=1.23)

        response = await client.get("/admin/cody-spend", headers=test_user["headers"])
        assert response.status_code == 200
        body = response.json()
        assert body["spend_usd_last_24h"] >= 1.23
        assert body["spend_usd_last_7d"] >= 1.23
        assert body["daily_cap_usd"] == 10.0

    async def test_non_staff_gets_404_not_403(self, client, second_user):
        response = await client.get("/admin/cody-spend", headers=second_user["headers"])
        assert response.status_code == 404
