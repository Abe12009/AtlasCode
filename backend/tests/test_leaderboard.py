"""GET /leaderboard: who is listed, in what order, and what leaks.

Every test builds its own users and profiles as temporary rows and removes
them in a `finally`, because the test database is session-scoped and shared
with ~740 other tests -- and because the board is global, so a row left
behind would show up in someone else's page and change their ranks.
"""

import base64

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select, update

from app.core.security import get_password_hash
from app.models import StudentProfile, User


def _b64(raw: str) -> str:
    """Encode a cursor body the way the endpoint does, for probing."""
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


async def _make_user(
    db_session,
    username: str,
    xp,
    *,
    visibility: str = "public",
    is_active: bool = True,
    level: int = 1,
) -> User:
    """A listed-by-default account with a chosen XP (None is allowed)."""
    user = User(
        email=f"{username}@example.com",
        username=username,
        hashed_password=get_password_hash("password123"),
        preferred_language="en",
        profile_visibility=visibility,
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    db_session.add(StudentProfile(user_id=user.id, xp=xp, level=level))
    await db_session.commit()
    if xp is None:
        # `StudentProfile.xp` is `Column(Integer, default=0)`, and SQLAlchemy
        # applies a Python-side default to an attribute that is None at flush
        # -- so constructing the row with xp=None stores 0, not NULL. A real
        # NULL has to be written past the ORM, which is also the only way one
        # gets there in production: the app itself never writes one.
        await db_session.execute(
            update(StudentProfile)
            .where(StudentProfile.user_id == user.id)
            .values(xp=None)
        )
        await db_session.commit()
    return user


async def _cleanup(db_session, users: list[User]) -> None:
    for user in users:
        await db_session.execute(
            delete(StudentProfile).where(StudentProfile.user_id == user.id)
        )
        await db_session.execute(delete(User).where(User.id == user.id))
    await db_session.commit()


async def _usernames(client: AsyncClient, headers: dict, **params) -> list[str]:
    response = await client.get("/leaderboard", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return [entry["username"] for entry in response.json()["entries"]]


class TestLeaderboardListing:
    async def test_orders_by_xp_descending(
        self, client: AsyncClient, test_user, db_session
    ):
        made = []
        try:
            made = [
                await _make_user(db_session, "lb_low", 10),
                await _make_user(db_session, "lb_high", 900_000),
                await _make_user(db_session, "lb_mid", 5_000),
            ]
            names = await _usernames(client, test_user["headers"], limit=100)
            assert names.index("lb_high") < names.index("lb_mid") < names.index("lb_low")
        finally:
            await _cleanup(db_session, made)

    async def test_null_xp_sorts_last(
        self, client: AsyncClient, test_user, db_session
    ):
        """`student_profiles.xp` is nullable, and SQLite and PostgreSQL
        disagree about where NULLs land on a DESC sort -- SQLite treats them
        as smallest, PostgreSQL puts them first. The endpoint coalesces, so
        a NULL is strictly last either way, behind even a zero.
        """
        made = []
        try:
            made = [
                await _make_user(db_session, "lb_null", None),
                await _make_user(db_session, "lb_zero", 0),
                await _make_user(db_session, "lb_some", 7),
            ]
            stored = (
                await db_session.execute(
                    select(StudentProfile.xp).where(
                        StudentProfile.user_id == made[0].id
                    )
                )
            ).scalar_one()
            assert stored is None, "the probe must actually hold NULL, not 0"

            names = await _usernames(client, test_user["headers"], limit=100)
            assert names.index("lb_some") < names.index("lb_zero") < names.index("lb_null")
            # And it is reported as 0, not null, to the client.
            response = await client.get(
                "/leaderboard", headers=test_user["headers"], params={"limit": 100}
            )
            row = next(e for e in response.json()["entries"] if e["username"] == "lb_null")
            assert row["xp"] == 0
        finally:
            await _cleanup(db_session, made)

    async def test_private_and_suspended_users_are_excluded(
        self, client: AsyncClient, test_user, db_session
    ):
        made = []
        try:
            made = [
                await _make_user(db_session, "lb_public", 1_000),
                await _make_user(db_session, "lb_private", 2_000, visibility="private"),
                await _make_user(db_session, "lb_suspended", 3_000, is_active=False),
            ]
            names = await _usernames(client, test_user["headers"], limit=100)
            assert "lb_public" in names
            # Both are excluded despite having more XP than the listed one.
            assert "lb_private" not in names
            assert "lb_suspended" not in names
        finally:
            await _cleanup(db_session, made)

    async def test_a_row_carries_nothing_beyond_rank_name_avatar_level_xp(
        self, client: AsyncClient, test_user, db_session
    ):
        """The response is the contract: a leaked email or real name here is
        visible to every signed-in user at once."""
        made = []
        try:
            made = [await _make_user(db_session, "lb_fields", 4_242)]
            response = await client.get(
                "/leaderboard", headers=test_user["headers"], params={"limit": 100}
            )
            row = next(
                e for e in response.json()["entries"] if e["username"] == "lb_fields"
            )
            assert set(row) == {
                "rank",
                "username",
                "avatar_url",
                "avatar_image_data",
                "avatar_config",
                "avatar_type",
                "level",
                "xp",
            }
            serialized = response.text
            assert "lb_fields@example.com" not in serialized
            assert "hashed_password" not in serialized
            assert "streak" not in serialized
        finally:
            await _cleanup(db_session, made)

    async def test_a_deleted_account_vanishes_from_the_board(
        self, client: AsyncClient, test_user, db_session
    ):
        """StudentProfile has ondelete=CASCADE on user_id, and the board is an
        inner join -- so removing the account removes the row, with no
        leaderboard-specific cleanup to forget."""
        made = [await _make_user(db_session, "lb_doomed", 50_000)]
        assert "lb_doomed" in await _usernames(client, test_user["headers"], limit=100)

        await _cleanup(db_session, made)
        assert "lb_doomed" not in await _usernames(client, test_user["headers"], limit=100)


class TestLeaderboardPagination:
    async def test_tied_xp_is_stable_across_pages(
        self, client: AsyncClient, test_user, db_session
    ):
        """Every probe shares one XP value, so only the user_id tie-break
        separates them. Without it the two pages could overlap or skip --
        the classic keyset failure on a non-unique sort column.
        """
        made = []
        try:
            made = [await _make_user(db_session, f"lb_tie_{i}", 777_000) for i in range(6)]
            first = await client.get(
                "/leaderboard", headers=test_user["headers"], params={"limit": 3}
            )
            page_one = [e["username"] for e in first.json()["entries"]]
            cursor = first.json()["next_cursor"]
            assert cursor

            second = await client.get(
                "/leaderboard",
                headers=test_user["headers"],
                params={"limit": 3, "cursor": cursor},
            )
            page_two = [e["username"] for e in second.json()["entries"]]

            assert set(page_one).isdisjoint(page_two), "a row appeared on both pages"
            ranks = [e["rank"] for e in first.json()["entries"]] + [
                e["rank"] for e in second.json()["entries"]
            ]
            assert ranks == sorted(ranks), "ranks must keep counting across pages"
            assert len(set(ranks)) == len(ranks), "a rank was handed out twice"

            # Repeating the same request returns the same page.
            again = await client.get(
                "/leaderboard",
                headers=test_user["headers"],
                params={"limit": 3, "cursor": cursor},
            )
            assert [e["username"] for e in again.json()["entries"]] == page_two
        finally:
            await _cleanup(db_session, made)

    async def test_ranks_continue_across_a_page_boundary(
        self, client: AsyncClient, test_user, db_session
    ):
        made = []
        try:
            made = [
                await _make_user(db_session, f"lb_rank_{i}", 900_000 - i)
                for i in range(4)
            ]
            first = await client.get(
                "/leaderboard", headers=test_user["headers"], params={"limit": 2}
            )
            assert [e["rank"] for e in first.json()["entries"]] == [1, 2]
            second = await client.get(
                "/leaderboard",
                headers=test_user["headers"],
                params={"limit": 2, "cursor": first.json()["next_cursor"]},
            )
            assert [e["rank"] for e in second.json()["entries"]] == [3, 4]
        finally:
            await _cleanup(db_session, made)

    async def test_depth_is_capped(self, client: AsyncClient, test_user, monkeypatch, db_session):
        """Paging stops at MAX_DEPTH rather than crawling every user.

        The cap is lowered for the test instead of seeding 500 accounts --
        the behaviour under test is "stop at the cap", not the number itself.
        """
        from app.api import leaderboard

        monkeypatch.setattr(leaderboard, "MAX_DEPTH", 3)
        made = []
        try:
            made = [
                await _make_user(db_session, f"lb_deep_{i}", 800_000 - i)
                for i in range(5)
            ]
            first = await client.get(
                "/leaderboard", headers=test_user["headers"], params={"limit": 2}
            )
            assert [e["rank"] for e in first.json()["entries"]] == [1, 2]

            second = await client.get(
                "/leaderboard",
                headers=test_user["headers"],
                params={"limit": 2, "cursor": first.json()["next_cursor"]},
            )
            # Rank 3 is the last one allowed; there is no page after it.
            assert [e["rank"] for e in second.json()["entries"]] == [3]
            assert second.json()["next_cursor"] is None
        finally:
            await _cleanup(db_session, made)

    @pytest.mark.parametrize(
        "label,cursor",
        [
            ("plain text", "not-a-cursor"),
            ("truncated", _b64("100:5:2")[:4]),
            ("non-base64 symbols", "!!!!@@@@"),
            ("too few fields", _b64("100:5")),
            ("too many fields", _b64("1:2:3:4")),
            ("non-numeric fields", _b64("a:b:c")),
            ("non-utf8 payload", base64.urlsafe_b64encode(bytes.fromhex("fffefd")).decode()),
            ("whitespace", "   "),
            # Syntactically perfect, semantically impossible. These used to be
            # accepted and handed back negative or zero rank numbers.
            ("negative everything", _b64("-10:-5:-3")),
            ("negative rank", _b64("100:5:-9999")),
            ("zero rank", _b64("100:5:0")),
            ("zero user id", _b64("100:0:3")),
            ("xp below the NULL sentinel", _b64("-2:5:3")),
            # Python ints are unbounded; a bigint column is not. SQLite
            # shrugs at 2**63, PostgreSQL raises -- which would be a 500.
            ("just over int64", _b64(f"1:1:{2 ** 63}")),
            ("xp over int64", _b64(f"{2 ** 63}:1:1")),
        ],
    )
    async def test_a_bad_cursor_is_a_400_never_a_500(
        self, client: AsyncClient, test_user, label, cursor
    ):
        response = await client.get(
            "/leaderboard", headers=test_user["headers"], params={"cursor": cursor}
        )
        assert response.status_code == 400, f"{label}: {response.status_code}"

    async def test_an_oversized_cursor_is_refused_before_decoding(
        self, client: AsyncClient, test_user
    ):
        """Length is capped by FastAPI, so a payload built to be expensive to
        decode never reaches the decoder."""
        response = await client.get(
            "/leaderboard", headers=test_user["headers"], params={"cursor": "A" * 5_000}
        )
        assert response.status_code == 422

    async def test_the_sentinel_and_the_empty_cursor_are_valid(
        self, client: AsyncClient, test_user
    ):
        """-1 is the NULL-XP sentinel, so it is a legitimate cursor value; an
        empty cursor simply means the first page."""
        assert (
            await client.get(
                "/leaderboard",
                headers=test_user["headers"],
                params={"cursor": _b64("-1:5:3")},
            )
        ).status_code == 200
        assert (
            await client.get(
                "/leaderboard", headers=test_user["headers"], params={"cursor": ""}
            )
        ).status_code == 200

    @pytest.mark.parametrize(
        "limit", [0, -1, -999_999, 101, 10**9, 10**20, "abc", "", "1.5"]
    )
    async def test_limit_is_bounded(self, client: AsyncClient, test_user, limit):
        response = await client.get(
            "/leaderboard", headers=test_user["headers"], params={"limit": limit}
        )
        assert response.status_code == 422


class TestLeaderboardMe:
    async def test_me_is_returned_for_an_unlisted_caller(
        self, client: AsyncClient, test_user, db_session
    ):
        """An unlisted student still learns where they stand -- that is what
        makes the join control an informed choice rather than a leap.

        Measured as a delta rather than an absolute rank: the test database
        is shared, so how many listed accounts already exist is not this
        test's business. Two accounts with more XP must push the caller down
        exactly two places.
        """
        before = (await client.get("/leaderboard", headers=test_user["headers"])).json()
        assert before["me"]["is_listed"] is False  # the fixture account is private

        made = []
        try:
            made = [
                await _make_user(db_session, "lb_ahead_a", 10_000_000),
                await _make_user(db_session, "lb_ahead_b", 9_000_000),
            ]
            after = (await client.get("/leaderboard", headers=test_user["headers"])).json()
            assert after["me"]["rank"] == before["me"]["rank"] + 2
            assert after["me"]["is_listed"] is False
            # Unlisted: present in `me`, absent from everyone's `entries`.
            names = [e["username"] for e in after["entries"]]
            assert test_user["data"]["username"] not in names
        finally:
            await _cleanup(db_session, made)

    async def test_joining_and_leaving_changes_listing(
        self, client: AsyncClient, test_user, db_session
    ):
        """PATCH /auth/me is the join control -- the same switch that makes a
        profile viewable. There is no separate leaderboard opt-in to drift."""
        headers = test_user["headers"]
        username = test_user["data"]["username"]

        assert username not in await _usernames(client, headers, limit=100)
        assert (await client.get("/leaderboard", headers=headers)).json()["me"][
            "is_listed"
        ] is False

        join = await client.patch(
            "/auth/me", headers=headers, json={"profile_visibility": "public"}
        )
        assert join.status_code == 200
        joined = await client.get("/leaderboard", headers=headers, params={"limit": 100})
        assert joined.json()["me"]["is_listed"] is True
        assert username in [e["username"] for e in joined.json()["entries"]]

        leave = await client.patch(
            "/auth/me", headers=headers, json={"profile_visibility": "private"}
        )
        assert leave.status_code == 200
        left = await client.get("/leaderboard", headers=headers, params={"limit": 100})
        assert left.json()["me"]["is_listed"] is False
        assert username not in [e["username"] for e in left.json()["entries"]]

    async def test_my_rank_matches_my_row_when_i_am_listed(
        self, client: AsyncClient, test_user, db_session
    ):
        """The counted rank and the paged rank are two different queries;
        they must agree, or the own-row highlight lands on the wrong line."""
        headers = test_user["headers"]
        profile = (
            await db_session.execute(
                select(StudentProfile).join(User).where(
                    User.username == test_user["data"]["username"]
                )
            )
        ).scalar_one()
        original_xp = profile.xp
        try:
            # Enough XP to sit at rank 1 whatever else the shared database
            # holds, so "my row" is findable on the first page.
            profile.xp = 99_000_000
            await db_session.commit()
            await client.patch(
                "/auth/me", headers=headers, json={"profile_visibility": "public"}
            )

            body = (
                await client.get("/leaderboard", headers=headers, params={"limit": 5})
            ).json()
            mine = next(
                e
                for e in body["entries"]
                if e["username"] == test_user["data"]["username"]
            )
            assert mine["rank"] == body["me"]["rank"] == 1
            assert mine["xp"] == body["me"]["xp"] == 99_000_000
        finally:
            await client.patch(
                "/auth/me", headers=headers, json={"profile_visibility": "private"}
            )
            profile.xp = original_xp
            await db_session.commit()

    async def test_unauthenticated_access_is_refused(self, client: AsyncClient):
        assert (await client.get("/leaderboard")).status_code == 401


class TestLeaderboardIndex:
    """The index the board's `me.rank` COUNT depends on.

    `run_additive_migrations` creates indexes best-effort and swallows the
    exception (see its `except Exception: logger.warning`), so a statement
    that does not parse would never fail a boot, a test or a deploy -- it
    would just quietly leave the index missing. That is exactly the failure
    this guards.
    """

    async def test_every_index_statement_applies_to_a_fresh_schema(self):
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        from app.db.migrations import INDEXES
        from app.models import Base

        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                for name, statement in INDEXES:
                    # No try/except here on purpose: unlike production, a bad
                    # statement must fail loudly.
                    await conn.execute(text(statement))
                existing = (
                    await conn.execute(
                        text("SELECT name FROM sqlite_master WHERE type='index'")
                    )
                ).scalars().all()
            for name, _ in INDEXES:
                assert name in existing, f"{name} did not get created"
        finally:
            await engine.dispose()

    async def test_the_leaderboard_index_matches_the_query_ordering(self):
        """An index on the raw column cannot serve an ordering on an
        expression over it. The first version of this index was
        `(xp DESC, user_id)` while the query sorts by `coalesce(xp, -1)`, and
        SQLite's query planner used it for neither leaderboard query.
        """
        from app.db.migrations import INDEXES

        statement = dict(INDEXES)["ix_student_profiles_xp"]
        assert "coalesce(xp, -1)" in statement, statement
        assert "user_id" in statement
