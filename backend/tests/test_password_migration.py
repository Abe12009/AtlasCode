"""Password hashing migration safety.

Every pre-existing account stores a sha256_crypt hash at 535000 rounds, which
costs seconds to verify. New hashes use PBKDF2-HMAC-SHA256; legacy hashes must
keep working forever and upgrade only on a *successful* login.
"""

import pytest
from httpx import AsyncClient
from passlib.context import CryptContext
from sqlalchemy import select

from app.core.security import (
    get_password_hash,
    password_needs_upgrade,
    verify_and_upgrade_password,
    verify_password,
)
from app.models import User

#: Reproduces exactly what the 709 existing rows contain.
LEGACY = CryptContext(schemes=["sha256_crypt"], sha256_crypt__default_rounds=535000)
LEGACY_PASSWORD = "password123"


class TestHashConfiguration:
    def test_new_hashes_use_pbkdf2_sha256(self):
        assert get_password_hash("whatever").startswith("$pbkdf2-sha256$600000$")

    def test_new_hashes_are_not_flagged_for_upgrade(self):
        assert password_needs_upgrade(get_password_hash("whatever")) is False

    def test_legacy_hashes_are_flagged_for_upgrade(self):
        assert password_needs_upgrade(LEGACY.hash(LEGACY_PASSWORD)) is True

    def test_hashing_is_salted_so_two_hashes_differ(self):
        assert get_password_hash("same") != get_password_hash("same")

    def test_hash_never_contains_the_plaintext(self):
        secret = "SuperSecretValue123"
        assert secret not in get_password_hash(secret)


class TestLegacyHashesStillAuthenticate:
    def test_legacy_hash_verifies(self):
        assert verify_password(LEGACY_PASSWORD, LEGACY.hash(LEGACY_PASSWORD)) is True

    def test_legacy_hash_rejects_a_wrong_password(self):
        assert verify_password("wrong", LEGACY.hash(LEGACY_PASSWORD)) is False


class TestUpgradeOnSuccessfulVerifyOnly:
    def test_correct_password_returns_an_upgraded_hash(self):
        is_valid, upgraded = verify_and_upgrade_password(
            LEGACY_PASSWORD, LEGACY.hash(LEGACY_PASSWORD)
        )
        assert is_valid is True
        assert upgraded is not None
        assert upgraded.startswith("$pbkdf2-sha256$")
        # The upgraded hash must authenticate the same password.
        assert verify_password(LEGACY_PASSWORD, upgraded) is True

    def test_wrong_password_returns_no_upgrade(self):
        is_valid, upgraded = verify_and_upgrade_password(
            "definitely-wrong", LEGACY.hash(LEGACY_PASSWORD)
        )
        assert is_valid is False
        assert upgraded is None

    def test_an_already_current_hash_is_not_rewritten(self):
        is_valid, upgraded = verify_and_upgrade_password(
            LEGACY_PASSWORD, get_password_hash(LEGACY_PASSWORD)
        )
        assert is_valid is True
        assert upgraded is None


class TestLoginMigratesStoredHashes:
    async def test_login_upgrades_a_legacy_hash_in_place(
        self, client: AsyncClient, test_user, db_session
    ):
        """A real account whose stored hash is legacy migrates on next login."""
        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()

        # Put the account back on the legacy scheme, as the 709 real rows are.
        legacy_hash = LEGACY.hash(test_user["data"]["password"])
        user.hashed_password = legacy_hash
        await db_session.commit()

        response = await client.post(
            "/auth/login",
            json={
                "email": test_user["data"]["email"],
                "password": test_user["data"]["password"],
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

        await db_session.refresh(user)
        assert user.hashed_password != legacy_hash
        assert user.hashed_password.startswith("$pbkdf2-sha256$")
        # The account still authenticates afterwards.
        again = await client.post(
            "/auth/login",
            json={
                "email": test_user["data"]["email"],
                "password": test_user["data"]["password"],
            },
        )
        assert again.status_code == 200

    async def test_failed_login_leaves_the_stored_hash_untouched(
        self, client: AsyncClient, test_user, db_session
    ):
        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()

        legacy_hash = LEGACY.hash(test_user["data"]["password"])
        user.hashed_password = legacy_hash
        await db_session.commit()

        response = await client.post(
            "/auth/login",
            json={"email": test_user["data"]["email"], "password": "not-the-password"},
        )
        assert response.status_code == 401

        await db_session.refresh(user)
        assert user.hashed_password == legacy_hash, "a failed login must not rewrite the hash"

    async def test_a_legacy_account_can_log_in_at_all(
        self, client: AsyncClient, test_user, db_session
    ):
        """The migration must never lock an existing user out."""
        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()
        user.hashed_password = LEGACY.hash(test_user["data"]["password"])
        await db_session.commit()

        response = await client.post(
            "/auth/login",
            json={
                "email": test_user["data"]["email"],
                "password": test_user["data"]["password"],
            },
        )
        assert response.status_code == 200

    async def test_registration_stores_no_plaintext(
        self, client: AsyncClient, test_user, db_session
    ):
        result = await db_session.execute(
            select(User).where(User.email == test_user["data"]["email"])
        )
        user = result.scalar_one()
        assert test_user["data"]["password"] not in user.hashed_password
        assert user.hashed_password.startswith("$pbkdf2-sha256$")
