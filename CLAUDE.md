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
- Never chain `git stash` with `&&`/`;`. A `push` that fails on a bad pathspec leaves the `pop` to run anyway and apply someone else's stash, which has already conflicted `package-lock.json` here. To compare against `main`, commit the WIP on a branch, or use `git worktree`/`git checkout <ref> -- <paths>`.

## Running e2e when 8000 is busy

`frontend/vite.config.ts` proxies `/api` to `ATLASCODE_API_ORIGIN`, defaulting
to `http://127.0.0.1:8000`. Since F24 that is the only port in the harness --
every in-page `fetch` is a relative `/api/...` through the proxy -- so moving
the backend is one env var, not a sweep.

```powershell
# 1. backend off 8000
cd backend; uvicorn app.main:app --reload --port 8010

# 2. vite on its usual 5173, proxying /api to 8010
cd frontend; $env:ATLASCODE_API_ORIGIN = 'http://127.0.0.1:8010'; npm run dev

# 3. e2e against that vite -- `webServer.reuseExistingServer: true` in
#    playwright.config.ts is what makes Playwright reuse it instead of
#    starting a second one
cd frontend; npx playwright test e2e/microquest.spec.ts
```

bash: `ATLASCODE_API_ORIGIN=http://127.0.0.1:8010 npm run dev`. Confirm the
proxy before spending a suite on it -- `curl http://localhost:5173/api/health`
must answer `{"status":"ok"}`.

`baseURL` in `playwright.config.ts` is hardcoded `http://localhost:5173`, so
vite has to be on 5173. The trap is that `reuseExistingServer` cuts both ways:
a dev server already parked on 5173 **without** the env var is reused as-is and
502s every `/api` call, with no hint that the port knob was ignored. Restart
that server rather than adding a second one on 5174, which Playwright will
never look at.

## Production and data

- Never touch production or a production `DATABASE_URL` from an agent session. A production write needs a Render snapshot, a `pg_dump`, a read-only `--check` dry run the user reviews, and explicit approval.
- Seeding is insert-only and keyed by slug, so editing a seed file changes no existing database. Schema changes go in the additive migrations in `backend/app/db/migrations.py` (`ADD COLUMN`, `CREATE INDEX IF NOT EXISTS`) — nothing there drops or rewrites.
- `backend/app/db/session.py` enables `PRAGMA foreign_keys=ON` for SQLite; `backend/tests/conftest.py` builds its own engine without it. A test can pass a write that Postgres would reject.

## Working style

- Propose before building anything architecturally significant. When the brief conflicts with the code, stop and report rather than guess.
- Never claim something works without running it. Report what was seen versus not seen, and list what stays unverified.
- Frontend: follow the Spatial Glass rules in `frontend/src/index.css` — glass classes, the blur budget, and logical Tailwind utilities (`ps`/`pe`, `start`/`end`), since the app is EN/FR/AR and has to mirror under RTL.
