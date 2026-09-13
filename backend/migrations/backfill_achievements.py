"""Backfill achievements for every existing account's current progress.

WHY
---
Achievement award-checking (app.services.achievements) only runs from two
live trigger points -- exercise submission and project-task submission. Any
account with real historical progress from before this shipped (a 7-day
streak, level 10, lessons already completed, ...) would otherwise never
receive achievements it has already legitimately earned; it would have to
submit one more exercise or project task first just to trigger the check.

WHAT THIS DOES
--------------
For every user with a StudentProfile, runs the exact same
check_and_award_achievements() used by the live endpoints -- no separate
implementation to keep in sync, so this can never drift from what the app
itself considers "earned". Reuses that function's idempotency guarantee: an
account that already has a given achievement is left untouched, and running
this script multiple times is a no-op after the first.

SAFETY
------
* A SQLite database is copied to
  backup-before-achievements-backfill-<timestamp>.db beside the original
  before --apply writes anything. PostgreSQL is expected to be backed up by
  the provider's own snapshot mechanism.
* --check runs the real check for every account and reports exactly what
  would be awarded, then rolls back -- nothing is written.
* --apply commits the same result. Never edits or deletes anything besides
  what live award-checking already does: inserting UserAchievement /
  Notification rows and adding each achievement's xp_reward to
  StudentProfile.xp.

Usage:
    python migrations/backfill_achievements.py --check
    python migrations/backfill_achievements.py --apply
"""

from __future__ import annotations

import argparse
import asyncio
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Allow `python migrations/backfill_achievements.py` from the backend root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db.session import async_session_maker, engine  # noqa: E402
from app.models import StudentProfile, User  # noqa: E402
from app.services.achievements import check_and_award_achievements  # noqa: E402


def _sqlite_path(database_url: str) -> Path | None:
    marker = "sqlite+aiosqlite:///"
    if not database_url.startswith(marker):
        return None
    return Path(database_url[len(marker):]).resolve()


def _backup_sqlite(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = path.with_name(f"backup-before-achievements-backfill-{stamp}{path.suffix}")
    shutil.copy2(path, destination)
    return destination


async def run(apply: bool) -> int:
    settings = get_settings()
    print(f"Database: {settings.database_url.split('@')[-1]}")

    if apply:
        sqlite_file = _sqlite_path(settings.database_url)
        if sqlite_file is not None:
            backup = _backup_sqlite(sqlite_file)
            print(f"Backup written to {backup.name}" if backup else "No existing SQLite file to back up.")
        else:
            print("Non-SQLite database: no automatic backup taken. Make sure a provider snapshot exists.")

    total_awarded = 0
    accounts_affected = 0
    async with async_session_maker() as db:
        result = await db.execute(
            select(User.id, User.username, User.preferred_language, StudentProfile)
            .join(StudentProfile, StudentProfile.user_id == User.id)
        )
        rows = result.all()
        print(f"Checking {len(rows)} account(s)...")

        for user_id, username, preferred_language, profile in rows:
            earned = await check_and_award_achievements(
                db, user_id, profile, language=preferred_language
            )
            if earned:
                accounts_affected += 1
                total_awarded += len(earned)
                print(f"  {username}: {', '.join(a.title for a in earned)}")

        if apply:
            await db.commit()
            print(
                f"Applied. {total_awarded} achievement(s) newly awarded "
                f"across {accounts_affected} account(s)."
            )
        else:
            await db.rollback()
            print(
                f"Check only -- nothing written. {total_awarded} achievement(s) "
                f"would be newly awarded across {accounts_affected} account(s)."
            )

    await engine.dispose()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Report what would be awarded, write nothing.")
    group.add_argument("--apply", action="store_true", help="Award for real and commit.")
    args = parser.parse_args()
    return asyncio.run(run(apply=args.apply))


if __name__ == "__main__":
    raise SystemExit(main())
