from collections.abc import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()

#: Explicit pool sizing, applied only for Postgres -- SQLite's aiosqlite
#: dialect uses NullPool by default and rejects pool_size/max_overflow
#: outright (there's nothing to pool against a single local file). Kept
#: conservative for Postgres -- pool_size + max_overflow=10 total
#: connections -- because production currently runs on Render's free-tier
#: Postgres, which has its own low max_connections ceiling this app must
#: share with nothing else guaranteed. pool_recycle=300 recycles idle
#: connections before a managed Postgres provider silently drops them
#: itself, which otherwise surfaces as an "SSL connection closed
#: unexpectedly" error on the next checkout. Revisit both numbers if/when
#: the hosting tier changes -- a paid Postgres plan's higher connection
#: ceiling would make a larger pool worth having.
_engine_kwargs = {"echo": settings.debug}
if not settings.database_url.startswith("sqlite"):
    _engine_kwargs.update(pool_size=5, max_overflow=5, pool_recycle=300)

engine = create_async_engine(settings.database_url, **_engine_kwargs)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

if engine.sync_engine.dialect.name == "sqlite":
    # SQLite does not enforce foreign keys by default -- without this, every
    # ondelete="CASCADE"/"SET NULL" in app.models is silently inert. Postgres
    # (production) enforces FKs natively and doesn't support this pragma.
    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_fk_enforcement(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Create any missing tables, then apply additive column migrations.

    `create_all` never alters an existing table, so a deployed database would
    otherwise be left without columns added since it was created. The migration
    pass is additive-only and idempotent — see app.db.migrations.
    """
    from app.db.migrations import run_additive_migrations

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await run_additive_migrations(conn)