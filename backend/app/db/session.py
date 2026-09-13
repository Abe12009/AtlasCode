from collections.abc import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug)
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