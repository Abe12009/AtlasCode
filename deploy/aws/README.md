# AtlasCode on AWS — EC2 + RDS + S3/CloudFront

This is the AWS deployment target, alongside (not replacing) the existing
Render/Vercel config (`render.yaml`, `frontend/vercel.json` — both untouched,
left in the repo). Nothing here provisions anything by itself; every step
below is run by you, in the console or CLI.

---

## 1. What already carries over unmodified

| Piece | Status |
|---|---|
| `DATABASE_URL` → async psycopg driver rewrite (`backend/app/core/config.py`) | Works unmodified. RDS PostgreSQL is wire-compatible standard Postgres — the same `postgresql+psycopg://user:pass@host:5432/dbname` URL that pointed at Render's Postgres points at an RDS endpoint. No code change. |
| `psycopg[binary]==3.2.13` in `requirements.txt` | Already the async driver RDS needs. No change. |
| `init_db()` (create_all + additive migrations) and `python -m app.seed` | DB-agnostic — both run through the same SQLAlchemy async engine/session regardless of what's behind `DATABASE_URL`. No change. |
| `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Host/port were already CLI args, not hardcoded (built for Render's `$PORT`). Same command works on EC2 with a fixed port (e.g. 8000) behind nginx. No change. |
| `CORS_ORIGINS` | Already env-driven (`backend/app/core/config.py`, accepts JSON array or comma-separated string). Just set it to the new CloudFront/custom frontend domain instead of the Vercel URL — no code change. |
| `VITE_API_URL` | Already a build-time Vite env var (`frontend/src/api/client.ts`), no Vercel-specific mechanism involved. Point it at the new backend domain at build time — no code change. |
| Firebase backend config (`FIREBASE_PROJECT_ID`) | Public value, verified via Google's public keys — no secret to relocate. No change. |
| `boto3` / AWS SDK | Not used anywhere in the app (the only "boto3" hit in the codebase is an unrelated sandboxed-code-execution blocklist string). Not needed for this deployment. |

**One honest caveat, not a code issue:** this repo has no CI or docker-compose
that exercises the app against a real PostgreSQL instance — the test suite
runs against SQLite, and I don't have Docker available in this environment to
spin up a local Postgres to verify against. There's no Postgres-specific SQL
anywhere in the models (plain SQLAlchemy Core types throughout), so I'd
expect it to work unmodified, but the first real test is: **after RDS is up,
run `python -m app.seed` against it before pointing production traffic at
it** (Step 2 below) — that alone will surface any real incompatibility
immediately and cheaply, before going further.

**Nothing else needed changing.** No new files were required to make the
*application* AWS-compatible — everything below is infrastructure config
(systemd, nginx, this README) that didn't exist before, because the app was
never run on plain EC2 before.

---

## 2. RDS PostgreSQL

- **Engine version:** PostgreSQL 16.x (current stable, fully supported by
  SQLAlchemy 2.0 + psycopg 3). Not literally tested against this repo per the
  caveat above — verify with the seed run in step 5 below before relying on it.
- **Instance class:** `db.t4g.micro` (ARM/Graviton, cheapest burstable class
  with decent burst credits) — this is a low-traffic learning app, not a
  workload that needs more. `db.t3.micro` is the x86 equivalent if you'd
  rather not deal with ARM (no practical difference for this app; RDS handles
  the architecture, it doesn't affect your code at all).
- **Storage:** 20 GB gp3 (RDS minimum), single-AZ (skip Multi-AZ — it roughly
  doubles cost and this app doesn't need that availability tier yet).
- **Public accessibility:** **No.** Place it in a private subnet (or a public
  subnet with "Publicly accessible" set to No — either works, private subnet
  is cleaner). Its security group should allow inbound **5432 from the EC2
  instance's security group only** (reference the SG by ID, not a CIDR range)
  — nothing else, no 0.0.0.0/0 anywhere on this port.
- **VPC:** Same VPC as the EC2 instance (default VPC is fine for a setup this
  small), so the SG-to-SG reference works.
- **DB name / master username:** your choice, e.g. `atlascode` / `atlascode`.
  Store the master password in Secrets Manager or just note it — it becomes
  part of `DATABASE_URL`, which itself lives in Parameter Store per Step 6.

**Resulting `DATABASE_URL`:**
```
postgresql+psycopg://<username>:<password>@<rds-endpoint>:5432/<dbname>
```
(`<rds-endpoint>` is the RDS instance's endpoint hostname from the console,
e.g. `atlascode-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com` — no `postgres://`
rewriting needed since you're writing the already-correct scheme directly.)

**First-boot sequence once the instance is reachable from EC2:**
```bash
# from the EC2 instance, inside the backend venv, with DATABASE_URL set to the RDS URL above
python -m app.seed
```
This runs `init_db()` (create_all + additive migrations) then the idempotent
`seed_all()`. Safe to re-run.

---

## 3. EC2 backend hosting

### Instance
- **Type:** `t4g.micro` (ARM/Graviton, 2 vCPU burstable, cheapest general
  option) or `t3.micro` if you'd rather stay x86 for tooling familiarity.
  Either is plenty for this app's traffic.
- **AMI:** Amazon Linux 2023 (has `dnf`, current OpenSSL/Python packaging,
  well-supported).
- **Storage:** 8–10 GB gp3 root volume is enough (no local DB file in
  production — that lives in RDS).

### Security group
| Port | Source | Purpose |
|---|---|---|
| 22 | **Your IP only** (`x.x.x.x/32`) | SSH |
| 80 | 0.0.0.0/0 | HTTP → redirected to HTTPS by nginx/certbot |
| 443 | 0.0.0.0/0 | HTTPS (public app traffic) |

No port 8000 (the app's own port) open to anything but `127.0.0.1` — nginx is
the only thing that talks to uvicorn; nothing external reaches it directly.

### Process manager
`deploy/aws/atlascode-backend.service` — a systemd unit running uvicorn
directly (2 workers, `--host 0.0.0.0 --port 8000`, bound to localhost only in
practice since the SG blocks external access to 8000). `Restart=on-failure`
handles crashes; systemd's default enablement handles reboots. No gunicorn —
it's not currently a dependency, and plain `uvicorn --workers N` plus
systemd's own restart policy is sufficient at this scale. (If you outgrow
this, gunicorn-managed uvicorn workers is the natural next step — flagging it
as a future option, not doing it now.)

Install:
```bash
sudo cp deploy/aws/atlascode-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now atlascode-backend
sudo systemctl status atlascode-backend
journalctl -u atlascode-backend -f   # tail logs
```

### nginx + TLS
`deploy/aws/nginx-atlascode.conf` — reverse proxy to `127.0.0.1:8000`.

**TLS approach: Let's Encrypt/certbot directly on the instance, not
ALB+ACM.** Reasoning: this is a single EC2 instance with no load-balancing or
multi-AZ need — an ALB adds a fixed ~$16–20/mo charge (Section 8) purely for
TLS termination you can get for free via certbot, plus one more moving part
to manage. If this ever grows into multiple instances or needs the extra
health-check/failover machinery an ALB provides, revisit then; for "smallest
viable app," certbot on the instance is strictly cheaper and simpler.

```bash
sudo dnf install -y nginx
sudo cp deploy/aws/nginx-atlascode.conf /etc/nginx/conf.d/atlascode.conf
# edit the server_name in that file to your real domain first
sudo nginx -t && sudo systemctl enable --now nginx

sudo dnf install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
# certbot edits the nginx config in place to add the 443 block + 80->443 redirect,
# and installs its own renewal timer (systemctl list-timers | grep certbot)
```

This requires `api.yourdomain.com` (or whatever subdomain you use) to already
have a DNS A/AAAA record pointing at the EC2 instance's Elastic IP before you
run certbot (it validates domain ownership over HTTP).

### Environment variables — two options

**Option A — `.env` file (simpler, do this first if you want to move fast):**
- Put it at `/etc/atlascode/atlascode.env`, same keys as
  `backend/.env.example` but with real production values.
- `sudo chown atlascode:atlascode /etc/atlascode/atlascode.env && sudo chmod 600 ...`
  — readable only by the service's own user, never committed anywhere.
- Reference it via `EnvironmentFile=` in the systemd unit (already set).

**Option B — AWS Systems Manager Parameter Store (more secure, recommended):**
- Store each value as a `SecureString` parameter under a prefix, e.g.
  `/atlascode/prod/database_url`, `/atlascode/prod/secret_key`, etc.
- Give the EC2 instance an IAM role with a policy scoped to that prefix:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": ["ssm:GetParametersByPath", "kms:Decrypt"],
      "Resource": "*"
    }]
  }
  ```
  (tighten `Resource` to the specific parameter ARNs / KMS key ARN once you
  know them — the wildcard above is a starting point, not a final policy).
- `deploy/aws/fetch-env-from-ssm.sh` pulls those parameters and writes them to
  the same `/etc/atlascode/atlascode.env` path Option A uses, with the same
  file permissions — wire it into a boot-time step (systemd `ExecStartPre=`
  on the backend unit, or a one-shot unit that runs before it) if you want it
  refreshed automatically.
- Nothing in this repo runs that script automatically — it's provided, not
  wired in, since that's an infra decision (see Section 9).

**Recommendation:** Option B. It avoids a plaintext secret ever sitting on
disk outside of the brief moment the fetch script writes it, gives you
audit-logged access via CloudTrail, and rotation doesn't require re-copying a
file by hand. Option A is fine to start with if you want the fastest path to
a working deployment and plan to move to B shortly after.

---

## 4. CORS

No code change — `CORS_ORIGINS` in the backend env is already a plain env var
consumed by `backend/app/core/config.py`. Set it to the CloudFront domain (or
your custom frontend domain) instead of the old Vercel URL, e.g.:
```
CORS_ORIGINS=https://d1234abcd.cloudfront.net
```
or, once you have a custom domain on the frontend:
```
CORS_ORIGINS=https://app.yourdomain.com
```

---

## 5. Frontend — S3 + CloudFront

**Recommended: private S3 bucket + CloudFront Origin Access Control (OAC)**,
not a public bucket — this keeps the bucket itself inaccessible from the
internet; only CloudFront (using OAC's signed requests) can read from it.

### S3
1. Create a bucket (name doesn't need to be public-facing, e.g.
   `atlascode-frontend-prod`). Leave "Block all public access" **ON** (the
   default) — OAC doesn't need it off.
2. No static-website-hosting mode needed (that's the public-bucket path);
   plain bucket + CloudFront origin is the private path.
3. Upload the Vite build output (`frontend/dist/`) to the bucket root on each
   deploy (`aws s3 sync frontend/dist/ s3://atlascode-frontend-prod/ --delete`).

### CloudFront
1. Create a distribution with the S3 bucket as origin, **Origin access
   control settings (recommended)** — CloudFront will generate the bucket
   policy for you to paste into the S3 bucket permissions (a one-time step
   the console walks you through).
2. Default root object: `index.html`.
3. **SPA routing fix** (equivalent to the old `vercel.json` rewrite) — under
   **Error pages**, add two custom error responses:
   | HTTP error code | Response page path | HTTP response code |
   |---|---|---|
   | 403 | `/index.html` | 200 |
   | 404 | `/index.html` | 200 |
   This is what makes `/app/dashboard` survive a hard refresh instead of
   404ing — CloudFront serves `index.html` for any path S3 doesn't have, and
   React Router takes it from there client-side.
4. Attach a TLS cert via ACM (**must be in `us-east-1`** regardless of where
   everything else lives — CloudFront only accepts ACM certs from that
   region) if you're using a custom domain; the default `*.cloudfront.net`
   domain already has HTTPS with no extra cert needed if you're fine with
   that URL for now.

### `VITE_API_URL`
Same mechanism as before — a build-time env var, nothing Vercel-specific
about it. Set it wherever you run `npm run build` (CI environment, or your
shell before building locally) to the new backend URL:
```
VITE_API_URL=https://api.yourdomain.com
```

### Cache invalidation on every deploy
After each `s3 sync`, invalidate at minimum `/index.html` (it references the
hashed JS/CSS bundle filenames, so if it's cached stale, users keep loading
an old app shell pointing at bundles that may no longer exist):
```bash
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/index.html"
```
The hashed asset files (`/assets/*-<hash>.js`) don't need invalidation — a
new build produces new filenames, so old cached ones are simply never
requested again.

---

## 6. Secrets

Nothing is hardcoded — grep confirms the only secret-shaped default is
`backend/app/core/config.py`'s `INSECURE_DEFAULT_SECRET_KEY`, which is an
intentional, obviously-named fallback for local dev, not a real secret;
production always overrides `SECRET_KEY` via env.

Values that need to live somewhere other than the repo:
| Value | Where |
|---|---|
| `SECRET_KEY` | Parameter Store (`SecureString`) or `.env` per Section 3 |
| `DATABASE_URL` (with the real RDS password embedded) | Same |
| `FIREBASE_PROJECT_ID` | Same, though it's a public value — fine either way |

Consistent with Section 3's recommendation: Parameter Store `SecureString`
entries, pulled via `fetch-env-from-ssm.sh` into the same `.env`-shaped file
the systemd unit already expects.

---

## 7. Dependencies

No AWS SDK needed for this deployment — the app doesn't call any AWS API
directly. `boto3` would only become relevant if you later move avatar photo
storage from base64-in-the-database to S3 (a real thing worth doing
eventually — base64-in-Postgres bloats row size and query performance — but
it's a separate, out-of-scope feature: it'd touch the upload endpoint, the DB
schema, and the frontend rendering path. Flagging it, not doing it here.)

---

## 8. Tests

Re-ran both suites after this pass (no application code was touched, so this
is a "confirm nothing regressed" run, not a response to any code change):

- **Frontend** (`npm test -- --run`): **233 passed / 233**, 19 test files, 0
  failures.
- **Backend** (`python -m pytest -q`): **512 passed, 3 skipped**, 0 failures.

(Both suites still run against the local SQLite default — this doesn't
exercise the RDS path, per the caveat in Section 1.)

---

## 9. Decisions needed from you before going further

1. **Domain names** — do you have a domain for the backend (`api.yourdomain.com`)
   and/or frontend (`app.yourdomain.com`), or starting with the raw
   `*.cloudfront.net` URL and bare EC2 Elastic IP for now? Changes the ACM /
   certbot / DNS steps.
2. **Env var delivery: Option A (.env file) vs. Option B (Parameter Store)** —
   recommended B, but A is faster to stand up first. Your call in Section 3.
3. **ARM (t4g/db.t4g) vs. x86 (t3/db.t3)** — ARM is marginally cheaper for
   identical specs; no code-level reason to prefer either for this app.
4. **RDS engine version** — 16.x recommended as current stable; confirm no
   objection given the "not literally tested against real Postgres in this
   repo" caveat in Section 1.
5. Nothing else blocks finalizing config — the two files in `deploy/aws/`
   are ready to use once you've made the above calls (they don't hardcode
   any domain-specific values except the placeholder `server_name` in the
   nginx config, which needs your real domain before running certbot).

---

## Deployment order (once you've made the calls above)

1. **RDS**: create the instance (Section 2), note the endpoint, don't make it
   publicly accessible.
2. **EC2**: launch the instance (Section 3), attach a security group allowing
   RDS's SG to reach it (or rather — attach EC2's SG as the *source* on RDS's
   inbound rule), assign/allocate an Elastic IP.
3. On EC2: install Python 3.12 (match `backend/.python-version`), clone the
   repo to `/opt/atlascode`, create the venv, `pip install -r requirements.txt`.
4. Set up env vars (Option A or B, Section 3) with the real `DATABASE_URL`
   pointing at RDS.
5. Run `python -m app.seed` once, by hand, to confirm the RDS path actually
   works end-to-end (this is the real verification step from Section 1's
   caveat) and to populate the curriculum content.
6. Install and start the systemd unit (Section 3) — confirm `curl
   127.0.0.1:8000/health` works locally on the instance.
7. Install nginx, point DNS at the instance's Elastic IP, run certbot
   (Section 3) — confirm `https://api.yourdomain.com/health` works externally.
8. **S3 + CloudFront**: create the bucket, build the frontend with the real
   `VITE_API_URL` (Section 5), sync to S3, create the distribution with OAC +
   the SPA error-page rule, wait for it to deploy (~5–15 min).
9. Set the backend's `CORS_ORIGINS` to the CloudFront/custom frontend domain
   (Section 4), restart `atlascode-backend`.
10. Smoke-test end to end: load the CloudFront/custom URL, register a user,
    confirm it round-trips through the real backend/RDS.

---

## 10. Rough monthly cost (smallest viable setup, us-east-1, ballpark not a quote)

| Item | Est. monthly |
|---|---|
| EC2 `t4g.micro` (on-demand, running 24/7) | ~$6 |
| EBS 10 GB gp3 | ~$1 |
| RDS `db.t4g.micro`, single-AZ, 20 GB gp3 | ~$13 |
| Elastic IP (free while attached to a running instance) | $0 |
| S3 (a few hundred MB of built assets + requests) | <$1 |
| CloudFront (low-traffic app, first 1 TB/month has a free tier for the first 12 months) | ~$0–2 |
| Route 53 hosted zone, if you use a custom domain | ~$0.50 |
| ACM certificate | $0 (free) |
| Let's Encrypt certificate | $0 (free) |
| **Total** | **roughly $20–25/mo** |

(A 12-month-old AWS account's Free Tier can knock the EC2/RDS numbers close
to $0 for the first year on a `t3.micro`/`db.t3.micro` combo instead — worth
checking eligibility before assuming the table above.)

---

## 11. Confirmation

- Only files added this pass: `deploy/aws/README.md`,
  `deploy/aws/atlascode-backend.service`, `deploy/aws/nginx-atlascode.conf`,
  `deploy/aws/fetch-env-from-ssm.sh`. No existing application code, curriculum,
  avatar, or UI files were touched.
- `render.yaml` and `frontend/vercel.json` are untouched, still in the repo.
- No AWS resources were created, no `aws` CLI provisioning commands were run,
  nothing was pushed, nothing was deployed.
