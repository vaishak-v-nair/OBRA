# ORBA · Stage 02

A local development workspace with real accounts, revocable server sessions, workspace permissions, manual invitations and persisted projects. Chat still creates a project from your description. AI agents, GitHub connections, multiplayer, Skills installation and cloud execution remain later-stage work.

## Prerequisites

Node.js 22+ (verified 26.7.0), pnpm 12.14.0, Python 3.12+ (verified uv-managed 3.14.4), uv, Docker Desktop/Linux containers. Ports: development 3000/8000/54329; tests 3001/8001/54330. Without global pnpm, replace each `pnpm` command with `npm exec --yes --package=pnpm@12.14.0 -- pnpm`.

## Install and migrate (PowerShell, repository root)

Stop any old Stage 01 API process before upgrading. Its unauthenticated routes must not run against the Stage 02 database. The ownership migration refuses to run while the local API port 8000 is listening. If using a custom backend port, set ORBA_API_PORT to that port before upgrading; this guard covers the local deployment, not an inventory of remote processes. Preserve the named development volume; do not reset/drop the database.

```powershell
pnpm install --frozen-lockfile
uv sync --locked --directory apps/api
docker compose -f infra/compose.yaml up -d --wait postgres
if (!(Test-Path apps/api/.env)) { Copy-Item apps/api/.env.example apps/api/.env }
if (!(Test-Path apps/web/.env.local)) { Copy-Item apps/web/.env.example apps/web/.env.local }
uv run --directory apps/api alembic upgrade head
uv run --directory apps/api alembic check
```

The development credentials in Compose are local-only. Existing projects are preserved in the restricted legacy workspace. Registering never grants access to them. The ownership migration is forward-only: use an operator-controlled offline backup restore if rollback is ever required, never serve the old API against the protected database.

## Start in two terminals

```powershell
uv run --directory apps/api uvicorn orba.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
```

```powershell
pnpm dev
```

Open **http://localhost:3000**, create an account, then create a workspace. The creator becomes Owner. API docs are at http://127.0.0.1:8000/docs, but write requests require the CSRF header and configured Origin. Health endpoints remain public. To use the production build locally, run `pnpm build`, then `pnpm --filter @orba/web start` with the API running.

Browser requests use `/api/v1/...` on the web origin. Next.js forwards them to the server-only `API_URL` (default http://127.0.0.1:8000). It forwards cookies/Origin/CSRF, preserves Set-Cookie, disables caching and does no authentication of its own. Remove any obsolete NEXT_PUBLIC_API_URL setting; it is no longer used. Keep the browser origin exactly localhost:3000 unless changing WEB_ORIGIN to match.

## Authentication and configuration

FastAPI is the sole authority. Emails are trimmed/case-folded and validated; passwords are not trimmed and must contain 12–128 characters. Argon2id salts every password hash. PostgreSQL sessions store SHA-256 hashes of 256-bit opaque random tokens. No browser-readable storage contains authentication credentials.

Session cookies are host-only, HttpOnly, SameSite=Lax, explicitly expiring. Logout revokes the DB record; login/register rotates the cookie and revokes the presented active session. GET `/api/v1/auth/me` validates account status, token hash, expiration and revocation.

| API setting | Default / behavior |
|---|---|
| DATABASE_URL | Local dev PostgreSQL at 54329 |
| WEB_ORIGIN | http://localhost:3000; exact Origin required on every write |
| COOKIE_SECURE | false for local HTTP; **must be true for HTTPS** (startup rejects HTTPS/false) |
| SESSION_COOKIE | orba_session |
| SESSION_LIFETIME_SECONDS | 604800 (7 days), bounded 60–2592000 |
| INVITATION_LIFETIME_SECONDS | 172800 (2 days), bounded 60–604800 |
| LOGIN_MAX_ATTEMPTS | 5 per normalized email per window; shared peer-IP budget is 20× this |
| LOGIN_WINDOW_SECONDS | 900 |
| Web API_URL | Server-only backend URL, port 8000 in development |

For authenticated writes, the client fetches `/api/v1/auth/csrf` and sends its session-bound HMAC token as `X-CSRF-Token`. Login/registration use an HttpOnly, random pre-auth cookie paired with that endpoint's response token. Both patterns require the exact configured Origin; SameSite alone is not the defense. Missing, stale and malformed tokens are rejected. Do not log these values.

Login/registration attempts are persisted in PostgreSQL and serialized with advisory transaction locks per account and peer IP. Failures consume attempts; successful attempts also consume budget. Old rows are cleaned on new attempts. This is a basic local limiter, not a certified internet abuse defense. Start Uvicorn with **--no-proxy-headers** so caller-controlled forwarded headers cannot change the peer identity. Behind the local proxy the IP bucket is deliberately shared. A full limiter can also lock out legitimate users; password reset/recovery and operator unlock UX are not implemented.

## Workspace permissions

| Role | View | Create/edit projects | Invite | Manage roles |
|---|---|---|---|---|
| Owner | Yes | Yes | Admin/Member/Viewer | All; final Owner protected |
| Admin | Yes | Yes | Member/Viewer | Member/Viewer only |
| Member | Yes | Yes | No | No |
| Viewer | Yes | No | No | No |

Only Owners can promote an existing member to Owner; invitations cannot grant Owner. Admins cannot change themselves, other Admins or Owners. Membership and invitation writes plus project writes lock the workspace row before re-reading the caller's role. Concurrent final-owner demotions and repeated invitation acceptance are tested against real PostgreSQL. Unauthorized private project/workspace lookups return the same 404 shape as missing resources.

Select a workspace in the sidebar. The selected ID in sessionStorage is a preference only, validated against the server list; it grants no access. Changing account/workspace/route clears protected component state. Projects require an authorized workspace_id on create and list. Detail UUIDs and PATCH edits are checked server-side; creator_id cannot be supplied by the client. The original title/description bounds and created status remain.

## Manual invitations

Open Workspaces → Workspace settings. Owners/Admins can create an email-bound invitation with an allowed role. **No email is sent.** The authorized creation response returns its link once; copy/share it privately. Listing never returns the token or link again. Tokens are random, hashed in storage, expiring and single-use. Links put the token in a URL fragment to keep it out of HTTP access logs/referrers. Sign-in/sign-up retains it in a fragment, without accepting an arbitrary redirect URL.

The recipient must authenticate with the invited email, then explicitly accept. Acceptance locks the workspace then the invitation, rechecks the inviter's current authority, and atomically adds the unique membership and consumes the invitation. Wrong email, expired/revoked/used token, duplicate membership or revoked inviter privilege is rejected. Authorized users can revoke a pending invitation. Expired is computed from expires_at; accepted/revoked status and timestamps are persisted. Role and removal actions have confirmation dialogs and backend checks.

## Explicit legacy claiming (local operator only)

The fixed restricted legacy workspace is `00000000-0000-0000-0000-000000000001`, has no members and is excluded from web access. There is no public claim endpoint. A local operator with database access can inspect unclaimed IDs:

```powershell
docker compose -f infra/compose.yaml exec -T postgres psql -U orba -d orba -c "SELECT id,title FROM projects WHERE workspace_id='00000000-0000-0000-0000-000000000001';"
```

Register and create the intended target workspace first. Obtain its ID and existing Owner ID from authenticated `/api/v1/workspaces` and `/api/v1/auth/me`, or inspect them locally with psql. Substitute explicit UUIDs below (repeat --project for additional selected IDs):

```powershell
uv run --directory apps/api python -m scripts.claim_legacy --workspace WORKSPACE_UUID --owner OWNER_UUID --project PROJECT_UUID
uv run --directory apps/api python -m scripts.claim_legacy --workspace WORKSPACE_UUID --owner OWNER_UUID --project PROJECT_UUID --apply
```

The first command is a dry run. The second commits only if every selected project is still legacy and the target has that Owner. UUIDs, titles, descriptions, status and timestamps remain unchanged. Mixed/invalid selections fail atomically; already-claimed records cannot be moved again by this command. The local database credentials and terminal access define operator authority, not a web user privilege.

## Verification

```powershell
pnpm --filter @orba/web exec playwright install chromium
pwsh -File scripts/verify.ps1
```

The existing script now includes frozen pnpm install, peer check, Alembic upgrade/drift, real backend tests, Ruff check/format, strict typecheck, ESLint, production build and real browser E2E. It captures native stdout and exit codes in docs/evidence/verification-transcript.txt. Test migrations run automatically. Cleanup refuses anything except the guarded orba_test role/database at port 54330; only test records are cleared. Run backend/E2E sequentially. Existing ports 3001/8001 cause E2E startup rejection, not service reuse.

Backend tests and E2E use real migrated PostgreSQL, real handlers and real browser sessions. No mocks, hardcoded identities or fake responses. Stage 01 tests are retained with authenticated workspace setup. Desktop/mobile/tablet use Chromium device emulation. Network traces are disabled because they record passwords/session cookies; safe home screenshots remain explicit tests. Do not publish old failure traces containing ephemeral test credentials.

Run the deliberately incorrect expectation separately:

```powershell
uv run --directory apps/api pytest -q tests/experiments/unauthorized_success_experiment.py
```

It must exit **1** with `assert 404 == 200`. That is an explicitly expected-failure experiment; it is not discovered by the mandatory passing suite and uses no xfail/skip/green wrapper.

## Limits

Suitable for the current local development scope, **not certified production-secure**. No verified email ownership, password recovery, MFA/passkeys, SSO/OAuth, durable security audit store, production TLS/reverse-proxy configuration, distributed deployment certification, automatic session cleanup worker or penetration test. Registration's duplicate-email response can disclose that an address is registered. No real-time permission push; subsequent protected requests enforce current permissions. Logout clears protected local state immediately; if the server cannot be reached, the UI explicitly warns that revocation is unconfirmed and does not claim the session was revoked. There is no server-side project idempotency guarantee after an uncertain write. Existing TypeScript 6.0.3 / ESLint 9.39.5 compatibility pins remain documented in architecture; 9.x is npm-deprecated until current Next lint plugins support 10.

See docs/ARCHITECTURE.md, docs/STAGE02_PLAN.md, docs/STAGE02_TEST_PLAN.md and docs/VERIFICATION.md. Stage 01 evidence is archived in docs/VERIFICATION_STAGE01.md. No Stage 03 work is authorized.

