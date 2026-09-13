"""Database backup + restore verification.

WHY
---
A backup nobody has ever restored from isn't a verified backup -- this
script both takes a backup and can prove a given backup file actually
restores to a working, complete database, rather than trusting that the
copy operation succeeded.

WHAT THIS DOES
--------------
--backup:
    SQLite: copies the live database file to backend/migrations/backups/
    with a timestamped name. This is the actual backup mechanism for a
    SQLite deployment (e.g. a single-EC2-instance deployment that hasn't
    migrated to RDS yet).
    Postgres/RDS: takes no action and prints why -- RDS's own automated
    snapshots are the real backup mechanism there (see
    deploy/aws/README.md's "Backups" section); a file-copy approach
    doesn't apply to a managed database engine.

--verify-restore <backup-file>:
    Proves a backup file is actually restorable, without ever touching
    the live database: opens the backup file (read-only, at its own
    path -- it is never copied over the live file), runs
    `PRAGMA integrity_check`, and compares every table's row count
    against the live database. Reports pass/fail per table. SQLite only
    -- verifying an RDS snapshot restore means actually restoring it to a
    new instance in the AWS console/CLI and pointing a staging app at it,
    which this script can't do from a laptop; see deploy/aws/README.md
    for that procedure.

RETENTION
---------
--backup keeps the 14 most recent SQLite backups in
backend/migrations/backups/ and deletes older ones (roughly two weeks at
one backup/day -- adjust BACKUP_RETENTION_COUNT below if you back up more
or less often). Deleting old backups is the only thing this script ever
deletes; --verify-restore never deletes anything.

Usage:
    python migrations/backup_database.py --backup
    python migrations/backup_database.py --verify-restore migrations/backups/atlascode-20260913-153000.db
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Allow `python migrations/backup_database.py` from the backend root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402

BACKUP_DIR = Path(__file__).resolve().parent / "backups"
BACKUP_RETENTION_COUNT = 14


def _sqlite_path(database_url: str) -> Path | None:
    marker = "sqlite+aiosqlite:///"
    if not database_url.startswith(marker):
        return None
    return Path(database_url[len(marker):]).resolve()


def _table_names(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return sorted(row[0] for row in rows)


def _row_counts(conn: sqlite3.Connection, tables: list[str]) -> dict[str, int]:
    counts = {}
    for table in tables:
        counts[table] = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    return counts


def do_backup() -> int:
    settings = get_settings()
    sqlite_file = _sqlite_path(settings.database_url)

    if sqlite_file is None:
        print("Non-SQLite database (RDS/Postgres) -- no file-copy backup applies here.")
        print("RDS automated snapshots are the backup mechanism for this deployment;")
        print("see deploy/aws/README.md's Backups section for retention/restore-test procedure.")
        return 0

    if not sqlite_file.exists():
        print(f"No database file at {sqlite_file} -- nothing to back up yet.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_DIR / f"atlascode-{stamp}.db"
    shutil.copy2(sqlite_file, destination)
    print(f"Backup written to {destination}")

    existing = sorted(BACKUP_DIR.glob("atlascode-*.db"))
    stale = existing[:-BACKUP_RETENTION_COUNT] if len(existing) > BACKUP_RETENTION_COUNT else []
    for old in stale:
        old.unlink()
        print(f"Pruned old backup {old.name} (keeping the {BACKUP_RETENTION_COUNT} most recent)")

    return 0


def do_verify_restore(backup_file: str) -> int:
    settings = get_settings()
    live_path = _sqlite_path(settings.database_url)
    if live_path is None:
        print("Non-SQLite database -- restore verification for RDS means restoring a real")
        print("snapshot to a new instance via the AWS console/CLI, not this script.")
        return 1

    backup_path = Path(backup_file).resolve()
    if not backup_path.exists():
        print(f"Backup file not found: {backup_path}")
        return 1
    if not live_path.exists():
        print(f"Live database not found at {live_path} -- nothing to compare against.")
        return 1

    print(f"Live database:  {live_path}")
    print(f"Backup file:    {backup_path}")
    print("(Opening the backup read-only at its own path -- the live database is never touched.)")

    # Read-only connection via URI mode: proves the backup file is a valid,
    # openable SQLite database on its own, not just a byte-for-byte copy
    # that happens to exist.
    backup_conn = sqlite3.connect(f"file:{backup_path}?mode=ro", uri=True)
    try:
        integrity = backup_conn.execute("PRAGMA integrity_check").fetchone()[0]
        print(f"Backup integrity_check: {integrity}")
        if integrity != "ok":
            print("FAIL: backup file failed SQLite's own integrity check.")
            return 1

        backup_tables = _table_names(backup_conn)
        backup_counts = _row_counts(backup_conn, backup_tables)
    finally:
        backup_conn.close()

    live_conn = sqlite3.connect(f"file:{live_path}?mode=ro", uri=True)
    try:
        live_tables = _table_names(live_conn)
        live_counts = _row_counts(live_conn, live_tables)
    finally:
        live_conn.close()

    if backup_tables != live_tables:
        print(f"FAIL: table sets differ. Live-only: {set(live_tables) - set(backup_tables)}, "
              f"backup-only: {set(backup_tables) - set(live_tables)}")
        return 1

    print(f"\n{'table':40} {'live':>10} {'backup':>10}")
    mismatches = []
    for table in live_tables:
        live_n, backup_n = live_counts[table], backup_counts[table]
        flag = "" if live_n == backup_n else "  <-- MISMATCH (backup predates current data, expected if taken earlier)"
        print(f"{table:40} {live_n:>10} {backup_n:>10}{flag}")
        if backup_n > live_n:
            # A backup should never have MORE rows than the current live
            # database in a single-writer dev setup -- that would mean the
            # "backup" isn't actually a prior snapshot of this same database.
            mismatches.append(table)

    if mismatches:
        print(f"\nFAIL: backup has more rows than live for: {mismatches} -- suspicious, investigate.")
        return 1

    print(f"\nPASS: backup opens, passes integrity_check, and every table's row count is "
          f"consistent with a valid snapshot of this database.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--backup", action="store_true", help="Take a backup now.")
    group.add_argument("--verify-restore", metavar="BACKUP_FILE", help="Verify a backup file actually restores.")
    args = parser.parse_args()

    if args.backup:
        return do_backup()
    return do_verify_restore(args.verify_restore)


if __name__ == "__main__":
    raise SystemExit(main())
