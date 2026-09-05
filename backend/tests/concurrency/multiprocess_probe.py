"""Multi-process SQLite concurrency probe.

Phase 5 fixed the lesson/project progress race for concurrent requests inside a
single process. This probe answers the separate question the previous phases
explicitly did NOT establish: what happens when several OS processes write to
the same SQLite file at once.

It NEVER touches atlascode.db. It builds a throwaway database in a temp
directory, starts a real uvicorn server with several worker processes against
it, and drives genuinely concurrent traffic at the endpoints that were racing.

Run:  python tests/concurrency/multiprocess_probe.py [--workers 4] [--clients 24]
"""

import argparse
import asyncio
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BACKEND)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def build_database(db_path: str) -> None:
    """Create and seed an isolated database, never the production one."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.models import Base
    from app.seed import seed_all

    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    await seed_all(maker)
    await engine.dispose()


def wait_for_health(port: int, timeout: float = 90.0) -> bool:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    return False


async def drive(port: int, clients: int) -> dict:
    import uuid

    import httpx

    base = f"http://127.0.0.1:{port}"
    report: dict = {}

    async with httpx.AsyncClient(base_url=base, timeout=120) as client:
        suffix = uuid.uuid4().hex[:8]
        register = await client.post(
            "/auth/register",
            json={
                "email": f"conc_{suffix}@example.com",
                "username": f"conc_{suffix}",
                "password": "password123",
                "preferred_language": "en",
            },
        )
        register.raise_for_status()
        headers = {"Authorization": f"Bearer {register.json()['access_token']}"}

        # 1. Concurrent lesson starts for the same user + lesson.
        starts = await asyncio.gather(
            *[client.post("/lessons/1/start", headers=headers) for _ in range(clients)],
            return_exceptions=True,
        )
        report["lesson_start"] = summarize(starts)

        # 2. Concurrent progress reads (these auto-create the row too).
        reads = await asyncio.gather(
            *[client.get("/lessons/2/progress", headers=headers) for _ in range(clients)],
            return_exceptions=True,
        )
        report["lesson_progress_read"] = summarize(reads)

        # 3. Concurrent project starts.
        project = await asyncio.gather(
            *[client.get("/projects/1/progress", headers=headers) for _ in range(clients)],
            return_exceptions=True,
        )
        report["project_progress_read"] = summarize(project)

        # 4. Mixed write traffic from many clients at once.
        mixed = await asyncio.gather(
            *[client.post("/lessons/3/start", headers=headers) for _ in range(clients)],
            *[client.get("/lessons/3/progress", headers=headers) for _ in range(clients)],
            return_exceptions=True,
        )
        report["mixed"] = summarize(mixed)

    return report


def summarize(results) -> dict:
    codes: dict = {}
    ids = set()
    errors = []
    for item in results:
        if isinstance(item, Exception):
            errors.append(f"{type(item).__name__}: {item}")
            continue
        codes[item.status_code] = codes.get(item.status_code, 0) + 1
        if item.status_code == 200:
            try:
                ids.add(item.json().get("id"))
            except ValueError:
                pass
    return {"status_codes": codes, "distinct_row_ids": sorted(i for i in ids if i is not None),
            "transport_errors": errors[:5], "transport_error_count": len(errors)}


def count_duplicates(db_path: str) -> dict:
    import sqlite3

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    q = lambda sql: conn.execute(sql).fetchone()[0]
    out = {
        "lesson_progress_rows": q("select count(*) from lesson_progress"),
        "duplicate_user_lesson": q(
            "select count(*) from (select user_id, lesson_id from lesson_progress "
            "group by 1,2 having count(*) > 1)"
        ),
        "project_progress_rows": q("select count(*) from project_progress"),
        "duplicate_user_project": q(
            "select count(*) from (select user_id, project_id from project_progress "
            "group by 1,2 having count(*) > 1)"
        ),
        "integrity_check": q("pragma integrity_check"),
    }
    conn.close()
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--clients", type=int, default=24)
    args = parser.parse_args()

    tmpdir = tempfile.mkdtemp(prefix="atlascode-conc-")
    db_path = os.path.join(tmpdir, "concurrency.db").replace("\\", "/")
    print(f"Isolated database: {db_path}")
    print("(atlascode.db is never opened by this probe)\n")

    try:
        print("Seeding isolated database...")
        asyncio.run(build_database(db_path))

        port = free_port()
        env = dict(os.environ)
        env["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "127.0.0.1", "--port", str(port),
            "--workers", str(args.workers), "--log-level", "info",
        ]
        print(f"Starting uvicorn with {args.workers} worker processes on port {port}...")
        log_path = os.path.join(tmpdir, "server.log")
        log = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=BACKEND, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            if not wait_for_health(port):
                print("Server did not become healthy; cannot establish multi-process behaviour.")
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                log.close()
                print("--- server log (tail) ---")
                print(open(log_path, encoding="utf-8").read()[-3000:])
                return 2

            print(f"Server healthy. Driving {args.clients} concurrent clients per scenario.\n")
            report = asyncio.run(drive(port, args.clients))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
            log.close()

        print("=" * 62)
        for scenario, data in report.items():
            print(f"{scenario}:")
            print(f"    status codes      : {data['status_codes']}")
            print(f"    distinct row ids  : {data['distinct_row_ids']}")
            print(f"    transport errors  : {data['transport_error_count']}")
            for err in data["transport_errors"]:
                print(f"        {err}")

        print("\nDatabase after the run:")
        dup = count_duplicates(db_path)
        for key, value in dup.items():
            print(f"    {key:26} {value}")

        non_200 = any(
            code != 200 for data in report.values() for code in data["status_codes"]
        )
        duplicated = dup["duplicate_user_lesson"] or dup["duplicate_user_project"]
        transport = any(data["transport_error_count"] for data in report.values())

        print()
        if duplicated:
            print("RESULT: duplicate progress rows were created across processes.")
            return 1
        if non_200 or transport:
            print("RESULT: no duplicate rows, but some requests failed under multi-process load.")
            print("        See the status codes above; SQLite serialises writers with a lock,")
            print("        and a writer that waits longer than the busy timeout gets an error.")
            return 1
        print("RESULT: no duplicates, no failed requests across separate worker processes.")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        print(f"\nRemoved {tmpdir}")


if __name__ == "__main__":
    raise SystemExit(main())
