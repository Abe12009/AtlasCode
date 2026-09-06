"""Cross-dialect ``INSERT ... ON CONFLICT DO NOTHING``.

SQLAlchemy's dialect-specific ``insert()`` helpers (``sqlalchemy.dialects.sqlite.insert``
vs ``sqlalchemy.dialects.postgresql.insert``) return statement objects tied to
that dialect's compiler -- a statement built with the SQLite helper cannot be
compiled against a PostgreSQL connection, and vice versa. Both dialects expose
the same ``.on_conflict_do_nothing(index_elements=...)`` shape, so this picks
the constructor matching the engine actually configured (see
``app.core.config.Settings.database_url``), keeping every call site unchanged.
"""

from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert as _postgresql_insert
from sqlalchemy.dialects.sqlite import insert as _sqlite_insert

from app.db.session import engine


def conflict_insert(table):
    """Return the dialect-appropriate ``insert()`` construct for ``table``."""
    if engine.dialect.name == "postgresql":
        return _postgresql_insert(table)
    return _sqlite_insert(table)
