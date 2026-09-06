"""Apply pending additive column migrations to the configured database.

The app also does this on startup (see ``app.db.session.init_db``); this script
exists so an operator can run the same migration deliberately — with a backup
taken first — before deploying, and see exactly what changed.

    python -m migrations.apply_additive_migrations

Safety
------
* A SQLite database is copied to ``backup-before-migration-<timestamp>.db``
  beside the original before anything is altered. PostgreSQL is expected to be
  backed up by the provider's own snapshot mechanism; the script says so rather
  than pretending it took one.
* Only ``ALTER TABLE … ADD COLUMN`` and ``CREATE INDEX IF NOT EXISTS`` are
  issued. No table, column or row is ever dropped or rewritten, so existing
  users, XP, streaks, completed lessons and course progress are untouched.
* Re-running is a no-op.
"""

from __future__ import annotations

import asyncio
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Allow `python migrations/apply_additive_migrations.py` from the backend root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402
from app.db.migrations import run_additive_migrations  # noqa: E402
from app.db.session import Base, engine  # noqa: E402
from app import models  # noqa: E402,F401  (registers every table on Base)


def _sqlite_path(database_url: str) -> Path | None:
    marker = "sqlite+aiosqlite:///"
    if not database_url.startswith(marker):
        return None
    return Path(database_url[len(marker) :]).resolve()


def _backup_sqlite(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = path.with_name(f"backup-before-migration-{stamp}{path.suffix}")
    shutil.copy2(path, destination)
    return destination


async def main() -> int:
    settings = get_settings()
    database_url = settings.database_url
    print(f"Database: {database_url.split('@')[-1]}")

    sqlite_file = _sqlite_path(database_url)
    if sqlite_file is not None:
        backup = _backup_sqlite(sqlite_file)
        if backup:
            print(f"Backup written to {backup.name}")
        else:
            print("No existing SQLite file — it will be created.")
    else:
        print(
            "Non-SQLite database: no automatic backup taken. "
            "Make sure a provider snapshot exists before continuing."
        )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        applied = await run_additive_migrations(conn)

    if applied:
        print("Applied migrations:")
        for item in applied:
            print(f"  + {item}")
    else:
        print("Schema already up to date — nothing to do.")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
