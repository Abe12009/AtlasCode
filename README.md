# AtlasCode

A complete computer science learning platform: interactive lessons, exercises,
projects, and a curriculum organized into sections (Programming, Data
Structures & Algorithms, Computer Systems, Networking, Databases, Software
Engineering, AI & Machine Learning, Cybersecurity).

- **Frontend:** React + Vite + TypeScript → deploys to **Vercel**
- **Backend:** FastAPI + SQLAlchemy (async) → deploys to **Render**
- **Database:** SQLite locally, **PostgreSQL** in production
- **Auth:** AtlasCode's own email/password, plus optional **Firebase**
  (Google/GitHub sign-in, password reset)

---

## 1. Run locally

**Backend**

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate   # or `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
copy .env.example .env      # cp .env.example .env on macOS/Linux — the defaults work as-is for local dev
uvicorn app.main:app --reload --port 8000
```

**Seed the local database** (safe to rerun — see [§8](#8-migrations--seeding)):

```bash
python -m app.seed
```

**Frontend** (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite's dev server proxies `/api` to
`http://127.0.0.1:8000` (see `frontend/vite.config.ts`), so no `VITE_API_URL`
is needed locally.

**Run tests:**

```bash
cd backend && python -m pytest -q
cd frontend && npm test -- --run && npx tsc --noEmit && npm run build
```

---

## 2. Create a PostgreSQL database

Any managed PostgreSQL works (Render's own, Supabase, Neon, RDS, ...). You
need a connection string in one of these forms:

```
postgresql://user:password@host:5432/dbname
postgres://user:password@host:5432/dbname
```

The backend normalizes either form to the async `psycopg` driver
automatically (see `backend/app/core/config.py`) — you never need to add
`+psycopg` yourself.

If using Render's managed Postgres, `render.yaml` already wires this up: it
provisions an `atlascode-db` instance and injects its connection string as
`DATABASE_URL` on the backend service automatically.

---

## 3. Required environment variables

### Backend (`backend/.env.example`)

| Variable | Required | Notes |
|---|---|---|
| `APP_NAME` | no | Defaults to `AtlasCode` |
| `DEBUG` | **yes in prod** | Must be `false` in production — the app refuses to start with `DEBUG=false` and the default `SECRET_KEY` |
| `DATABASE_URL` | yes | SQLite locally, PostgreSQL in production (see above) |
| `SECRET_KEY` | **yes in prod** | JWT signing key. Generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ALGORITHM` | no | Defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | no | Defaults to 43200 (30 days) |
| `CORS_ORIGINS` | **yes in prod** | JSON array or comma-separated list of allowed frontend origins. Must include your Vercel URL. Never `*` |
| `FIREBASE_PROJECT_ID` | optional | Only needed for Google/GitHub sign-in and Firebase password reset. Public value — no secret involved |

### Frontend (`frontend/.env.example`)

| Variable | Required | Notes |
|---|---|---|
| `VITE_API_URL` | **yes in prod** | Your Render backend's base URL, no trailing slash, no `/api` suffix. Leave unset locally |
| `VITE_FIREBASE_API_KEY` | optional | |
| `VITE_FIREBASE_AUTH_DOMAIN` | optional | |
| `VITE_FIREBASE_PROJECT_ID` | optional | Must match the backend's `FIREBASE_PROJECT_ID` |
| `VITE_FIREBASE_STORAGE_BUCKET` | optional | |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | optional | |
| `VITE_FIREBASE_APP_ID` | optional | |
| `VITE_SOCIAL_INSTAGRAM` / `VITE_SOCIAL_X` / `VITE_SOCIAL_GITHUB` | optional | Landing page footer links |
| `VITE_CONTACT_EMAIL` | optional | Contact page fallback address |

All Firebase variables above are the **exact names the code reads** — see
`backend/app/core/config.py` and `frontend/src/config/firebase.ts`.

**Never commit a real `.env` file.** Only `.env.example` (placeholders) is
tracked — see [§9](#9-git--secrets).

---

## 4. Deploy the backend to Render

1. Push this repository to GitHub (you do this yourself — see [§10](#10-what-you-still-need-to-do)).
2. In Render: **New → Blueprint**, point it at the repo. It reads `render.yaml`
   at the repo root and provisions:
   - A web service rooted at `backend/` (`rootDir: backend`)
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health check: `/health`
   - A managed PostgreSQL database, wired to `DATABASE_URL` automatically
   - `SECRET_KEY` auto-generated
3. Set the two variables Render leaves for you (`sync: false` in `render.yaml`):
   - `CORS_ORIGINS` — your Vercel URL, e.g. `https://atlascode.vercel.app`
   - `FIREBASE_PROJECT_ID` — only if you want Google/GitHub sign-in
4. Deploy. Render builds and boots the service; `/health` should return
   `{"status": "ok"}`.
5. Seed the curriculum once (see [§8](#8-migrations--seeding)) — Render's
   dashboard has a **Shell** tab for this on the deployed service.

If not using Blueprints, configure the same values manually in the Render
dashboard: **Root Directory** `backend`, **Build Command**
`pip install -r requirements.txt`, **Start Command**
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`, **Health Check Path**
`/health`, plus the environment variables from [§3](#3-required-environment-variables).

---

## 5. Deploy the frontend to Vercel

1. **New Project** → import this repository.
2. **Root Directory:** `frontend` (must be set explicitly — this is what
   keeps Vercel from ever trying to run the backend).
3. **Framework Preset:** Vite (auto-detected). Build command `npm run build`,
   output directory `dist` (Vercel's Vite preset defaults are already correct).
4. `frontend/vercel.json` already provides the SPA rewrite
   (`/(.*) → /index.html`) so client-side routes like `/app/dashboard`,
   `/app/courses/:id`, `/app/u/:username` work on direct load/refresh, not
   just client-side navigation.
5. Set environment variables from [§3](#3-required-environment-variables):
   at minimum `VITE_API_URL` (your Render backend URL). Add the
   `VITE_FIREBASE_*` ones if you want Google/GitHub sign-in.
6. Deploy.

---

## 6. Configure Firebase (optional — only for Google/GitHub sign-in)

The app works fully on email/password without Firebase. If you want
Google/GitHub sign-in or Firebase-hosted password reset:

1. Create a project at [console.firebase.google.com](https://console.firebase.google.com).
2. **Project settings → General → Your apps → Web app** — copy the config
   values into the `VITE_FIREBASE_*` variables on Vercel, and the project ID
   alone into `FIREBASE_PROJECT_ID` on Render.
3. **Authentication → Sign-in method**: enable **Email/Password**, **Google**,
   and **GitHub** (if you want it — see below for the extra step it needs).
4. **Authentication → Settings → Authorized domains**: add your Vercel domain
   (e.g. `atlascode.vercel.app`) and any custom domain you attach. `localhost`
   is authorized by default for local dev.
5. **GitHub provider only:** register an OAuth App at
   github.com/settings/developers with callback URL
   `https://<your-firebase-project-id>.firebaseapp.com/__/auth/handler`, then
   paste its Client ID/Secret into the GitHub provider's settings in the
   Firebase console.
6. The backend verifies every Firebase ID token's signature against Google's
   published public keys — no Firebase Admin SDK credential or service-account
   key is ever needed or should be committed.

---

## 7. Configure CORS

`CORS_ORIGINS` on the backend accepts either a JSON array or a plain
comma-separated string:

```
CORS_ORIGINS=https://atlascode.vercel.app,https://your-custom-domain.com
```

It must list every origin the frontend is actually served from. It is never
`*` in production — `backend/app/core/config.py` has no wildcard fallback,
and CORS is not configurable to allow one at runtime.

---

## 8. Migrations & seeding

There is no Alembic migration chain. Schema management is two safe,
idempotent steps, both re-runnable with no data loss:

1. **Schema** — `Base.metadata.create_all()` runs automatically on every
   backend startup: it creates any missing table, and only that (never alters
   or drops an existing one). A small, hand-written **additive-migrations**
   pass (`backend/app/db/migrations.py`) also runs on every startup to add any
   column a table gained since it was first created (`ALTER TABLE ... ADD
   COLUMN`, skipped if the column already exists). Nothing here ever drops,
   renames, or rewrites a column, so existing users/XP/progress are untouched.

2. **Curriculum seeding** — run once per environment, and safe to rerun any
   number of times:

   ```bash
   python -m app.seed
   ```

   Every course/module/lesson/section/achievement is keyed by a unique slug
   and skipped if it already exists (`get_or_create_*` throughout
   `backend/app/seed/`), so this converges: a fully-seeded database is a
   no-op, a partially-seeded one only fills the gaps, and it never duplicates
   or destroys anything — including a database with real students on it.

To apply the additive migrations deliberately (with a backup step first, for
SQLite) without booting the whole app:

```bash
python -m migrations.apply_additive_migrations
```

---

## 9. Git & secrets

`.gitignore` excludes `.env`, `.env.*` (with `.env.example` explicitly
un-ignored), `*.db`/`*.sqlite*`, `__pycache__/`, `node_modules/`, `dist/`,
build/test artifacts, and editor files. Only `backend/.env.example` and
`frontend/.env.example` are tracked, and both contain placeholders only.

Before any commit, double-check `git status` and the diff of anything staged
— never commit a real API key, database password, Firebase config with a
real project's values, or JWT secret.

---

## 10. What you still need to do

This repository is prepared but **nothing has been deployed or pushed**. To
go live:

1. `git push` this repository to GitHub yourself.
2. Create the Render Blueprint (or manual service) — see [§4](#4-deploy-the-backend-to-render).
3. Set `CORS_ORIGINS` and (optionally) `FIREBASE_PROJECT_ID` on Render.
4. Import the project on Vercel with **Root Directory = `frontend`** — see [§5](#5-deploy-the-frontend-to-vercel).
5. Set `VITE_API_URL` (and optionally the Firebase variables) on Vercel.
6. Run `python -m app.seed` once against the production database (Render's
   Shell tab) to populate the curriculum.
7. If using Firebase: complete the console configuration in [§6](#6-configure-firebase-optional--only-for-googlegithub-sign-in).
8. Verify: load the Vercel URL, register an account, browse a course, confirm
   `https://your-backend.onrender.com/health` returns `{"status":"ok"}`.
