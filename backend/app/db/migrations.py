"""Additive schema migrations that run on startup.

The project creates tables with ``Base.metadata.create_all``, which happily
creates *new* tables but never alters an existing one. That is fine until a
model gains a column: an already-deployed database keeps the old shape and
every query against the new column fails.

This module closes that gap for the only kind of change that is safe to apply
automatically — **adding a nullable/defaulted column to an existing table**.
Nothing here drops, renames, retypes or deletes anything, so it cannot destroy
user accounts, XP, streaks or progress. Anything more invasive belongs in a
reviewed, one-off script under ``backend/migrations/``.

Both SQLite and PostgreSQL accept ``ALTER TABLE … ADD COLUMN``; the statements
below stick to that common subset. Each is skipped when the column already
exists, so startup is idempotent and repeated deploys are no-ops.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddColumn:
    """One additive column migration."""

    table: str
    column: str
    #: Portable DDL type + constraints, e.g. ``VARCHAR(32) DEFAULT 'password'``.
    ddl: str
    #: Optional UPDATE run once, right after the column is added, to give
    #: existing rows a meaningful value.
    backfill: Optional[str] = None


#: Applied in order. Append new entries; never edit or remove a shipped one.
MIGRATIONS: tuple[AddColumn, ...] = (
    # --- Federated authentication -----------------------------------------
    AddColumn("users", "firebase_uid", "VARCHAR(128)"),
    AddColumn(
        "users",
        "auth_provider",
        "VARCHAR(32) DEFAULT 'password'",
        backfill="UPDATE users SET auth_provider = 'password' WHERE auth_provider IS NULL",
    ),
    AddColumn(
        "users",
        "email_verified",
        # `DEFAULT 0` is SQLite-only for a BOOLEAN column -- PostgreSQL rejects
        # an integer default against a boolean column. TRUE/FALSE are literals
        # both dialects accept.
        "BOOLEAN DEFAULT FALSE",
        backfill="UPDATE users SET email_verified = FALSE WHERE email_verified IS NULL",
    ),
    AddColumn("users", "avatar_url", "VARCHAR(512)"),
    AddColumn(
        "users",
        "timezone_offset_minutes",
        "INTEGER DEFAULT 0",
        backfill="UPDATE users SET timezone_offset_minutes = 0 WHERE timezone_offset_minutes IS NULL",
    ),
    AddColumn("users", "last_login_at", "TIMESTAMP"),
    # --- Streak history ----------------------------------------------------
    AddColumn(
        "student_profiles",
        "longest_streak",
        "INTEGER DEFAULT 0",
        # Existing accounts have no history to reconstruct from, so the best
        # honest starting point is the streak they are currently on.
        backfill="UPDATE student_profiles SET longest_streak = COALESCE(streak, 0) WHERE longest_streak IS NULL",
    ),
    # --- Curriculum roadmap metadata ---------------------------------------
    AddColumn(
        "courses",
        "stage",
        "INTEGER DEFAULT 1",
        backfill='UPDATE courses SET stage = 1 WHERE stage IS NULL',
    ),
    AddColumn("courses", "track", "VARCHAR(50)"),
    AddColumn(
        "courses",
        "difficulty",
        "VARCHAR(20) DEFAULT 'beginner'",
        backfill="UPDATE courses SET difficulty = 'beginner' WHERE difficulty IS NULL",
    ),
    AddColumn(
        "courses",
        "estimated_hours",
        "INTEGER DEFAULT 0",
        backfill="UPDATE courses SET estimated_hours = 0 WHERE estimated_hours IS NULL",
    ),
    AddColumn("courses", "icon", "VARCHAR(50)"),
    AddColumn("courses", "prerequisite_course_id", "INTEGER"),
    # --- Course catalog sections --------------------------------------------
    # The `sections`/`section_translations` tables themselves are new, so
    # create_all handles them on any database. Only this column, added to the
    # pre-existing `courses` table, needs an additive migration.
    AddColumn("courses", "section_id", "INTEGER"),
    # --- Account settings ----------------------------------------------------
    AddColumn(
        "users",
        "profile_visibility",
        "VARCHAR(20) DEFAULT 'private'",
        backfill="UPDATE users SET profile_visibility = 'private' WHERE profile_visibility IS NULL",
    ),
    AddColumn("users", "avatar_config", "TEXT"),
    AddColumn("users", "avatar_image_data", "TEXT"),
    AddColumn(
        "users",
        "avatar_type",
        "VARCHAR(20) DEFAULT 'upload'",
        backfill="UPDATE users SET avatar_type = 'upload' WHERE avatar_type IS NULL",
    ),
)

#: Indexes for the columns above. ``IF NOT EXISTS`` is supported by both
#: SQLite and PostgreSQL, so these are safe to re-run.
INDEXES: tuple[tuple[str, str], ...] = (
    ("ix_users_firebase_uid", "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_firebase_uid ON users (firebase_uid)"),
    ("ix_courses_stage", "CREATE INDEX IF NOT EXISTS ix_courses_stage ON courses (stage)"),
    ("ix_courses_section_id", "CREATE INDEX IF NOT EXISTS ix_courses_section_id ON courses (section_id)"),
)


async def run_additive_migrations(conn: AsyncConnection) -> list[str]:
    """Apply every pending additive migration. Returns what was applied."""
    applied: list[str] = []

    def _existing_columns(sync_conn, table: str) -> set[str]:
        inspector = inspect(sync_conn)
        if table not in inspector.get_table_names():
            return set()
        return {column["name"] for column in inspector.get_columns(table)}

    for migration in MIGRATIONS:
        columns = await conn.run_sync(_existing_columns, migration.table)
        if not columns:
            # Table does not exist yet — create_all will build it complete.
            continue
        if migration.column in columns:
            continue

        await conn.execute(
            text(f"ALTER TABLE {migration.table} ADD COLUMN {migration.column} {migration.ddl}")
        )
        if migration.backfill:
            await conn.execute(text(migration.backfill))
        applied.append(f"{migration.table}.{migration.column}")
        logger.info("Applied migration: added %s.%s", migration.table, migration.column)

    for name, statement in INDEXES:
        try:
            await conn.execute(text(statement))
        except Exception:  # pragma: no cover - index creation is best-effort
            # A pre-existing index with the same name but a different shape is
            # not worth failing startup over; log and continue.
            logger.warning("Could not ensure index %s", name, exc_info=True)

    return applied
