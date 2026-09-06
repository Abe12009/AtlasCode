"""Entry point for ``python -m app.seed``.

``app/seed`` is a package, so ``python -m app.seed`` needs this file to run
anything — without it, Python raises "No module named app.seed.__main__"
before ever reaching the seeding logic. Safe to run against any database,
any number of times: init_db() only creates missing tables/columns, and
seed_all() is idempotent (see app.seed.__init__).
"""

import asyncio

from app.db.session import init_db
from app.seed import seed_all


async def main() -> None:
    await init_db()
    await seed_all()


if __name__ == "__main__":
    asyncio.run(main())
