# CLAUDE.md

Working rules for this repo. Setup, deploy and seeding live in [README.md](README.md); this is only what is easy to get wrong.

## Lockfiles

- Never delete or regenerate a `package-lock.json`. Deleting one re-resolves every `^` range at once, quietly pulling production dependencies forward along with whatever you meant to bump. Edit the manifest, install, keep the lockfile.
- Never `--force` or `--legacy-peer-deps`. `frontend/package.json` carries a deliberate `overrides` block with its reasoning inline; read it before touching anything Firebase.
- Scope a bump: `npm update <pkg> --package-lock-only` in the right folder, then check the diff touches only that package and say which changes are dev vs prod.
- `npm update --package-lock-only` with no package name crashes npm 10: arborist dies inside `#loadPeerSet` with `Cannot read properties of null (reading 'edgesOut')`, in `frontend/` and at the repo root alike. Run that one as `npx -y npm@11 update --package-lock-only`. Naming a single package avoids it; `npm audit fix --package-lock-only` is unaffected.
- The repo-root `package.json` is devDependencies only, no scripts. `frontend/` holds the app's dependencies and scripts.

## CI and git

- Work on a branch and open a PR. Every commit on `main` is a PR merge.
- `.github/workflows/tests.yml` runs two jobs on a PR: `backend` (bare `pytest` from `backend/` — `pytest.ini` sets `pythonpath` and `testpaths`) and `frontend` (`npm ci`, `npx tsc -b`, `npm test`, `npx vite build`). Both must pass.
- `security-scan.yml` runs on every PR too, but is not a required check.
- Do not commit without an explicit instruction, and never push — the user pushes from their own terminal.

## Production and data

- Never touch production or a production `DATABASE_URL` from an agent session. A production write needs a Render snapshot, a `pg_dump`, a read-only `--check` dry run the user reviews, and explicit approval.
- Seeding is insert-only and keyed by slug, so editing a seed file changes no existing database. Schema changes go in the additive migrations in `backend/app/db/migrations.py` (`ADD COLUMN`, `CREATE INDEX IF NOT EXISTS`) — nothing there drops or rewrites.
- `backend/app/db/session.py` enables `PRAGMA foreign_keys=ON` for SQLite; `backend/tests/conftest.py` builds its own engine without it. A test can pass a write that Postgres would reject.

## Working style

- Propose before building anything architecturally significant. When the brief conflicts with the code, stop and report rather than guess.
- Never claim something works without running it. Report what was seen versus not seen, and list what stays unverified.
- Frontend: follow the Spatial Glass rules in `frontend/src/index.css` — glass classes, the blur budget, and logical Tailwind utilities (`ps`/`pe`, `start`/`end`), since the app is EN/FR/AR and has to mirror under RTL.
