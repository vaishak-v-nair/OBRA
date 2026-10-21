# ORBA · Stage 03

A local development workspace with real accounts, workspace permissions, manual invitations, persisted projects and one Product Manager planning agent. Chat creates a project; explicit generation requests use a configured Gemini model to produce a validated, editable product plan. Architecture/coding/QA agents, orchestration, GitHub, multiplayer, Skills installation and cloud execution remain later-stage work. Current verification and blockers are in [docs/VERIFICATION.md](docs/VERIFICATION.md).

Stage03 verdict remains **PARTIAL**. Stage03.3's current Gate A passed all 14 commands: **285 backend, 60 core browser and 33 controlled-provider browser tests**, with zero skips/retries. Explicit reviewed model/thinking choices, bounded input and original-run diagnostics are implemented; no paid generation occurred during this preparation. Three read-only model metadata GETs succeeded, which does not prove generation. The latest historical authorized B failed upstream504 after88.825s, with prior503/504 failures preserved. A separately authorized3.6Flash/minimal trial is proposed; the ignored runtime selection remains3.8Flash/LOW unchanged. [Current source fingerprint, actual commands and evidence](docs/VERIFICATION_STAGE033.md). New passwords remain 15-128 Unicode code points, preserving legacy login/sessions. No automatic retry, new agent or Stage04. Any next paid request needs fresh owner authorization.

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

## Product Manager setup and use

Preserve your existing root `.env`. If absent, copy `.env.example` there. Set a real **GEMINI_API_KEY** (or **ORBA_PM_API_KEY**) and an explicit **ORBA_PM_MODEL** from the reviewed choices below, available to your account. No model is chosen automatically; the Codex session's model/credentials do not configure ORBA. The API reads root `.env`, then `apps/api/.env` as an override, and process environment takes precedence. Check configuration offline before restarting. Never put runtime keys in `NEXT_PUBLIC_*`, frontend settings, source control or logs.

```dotenv
# In your ignored root .env; obtain your own credential. Do not paste secrets in reports.
GEMINI_API_KEY=your-runtime-key
ORBA_PM_MODEL=gemini-3.8-flash
ORBA_PM_THINKING_LEVEL=low
ORBA_PM_MAX_INPUT_BYTES=48000
ORBA_PM_TIMEOUT_SECONDS=90
ORBA_PM_MAX_OUTPUT_TOKENS=6000
ORBA_PM_MAX_CONCURRENT=1
ORBA_PM_ACCOUNT_ATTEMPTS_PER_HOUR=3
ORBA_PM_GLOBAL_ATTEMPTS_PER_HOUR=6
```

The owner explicitly selected **gemini-3.8-flash** on 2026-10-19; the ignored local configuration uses the conservative values above. There is still no automatic model default: other installations must explicitly choose a model available to their account. Official documentation and the recorded account metadata list confirm this exact model advertises generateContent; that does **not** establish generation availability. Only Google Gemini is implemented, through the pinned official `google-genai` SDK2.31.0. OpenAI and Model Hub routing are not implemented.

Stage03.3 limits new generation to these reviewed stable IDs (optional `models/` prefix). Model IDs are case-sensitive; surrounding whitespace is removed. Thinking values are trimmed/lowercased and default to `low`. No fallback, alias routing or automatic switch is implemented.

| ORBA_PM_MODEL | ORBA_PM_THINKING_LEVEL |
|---|---|
| `gemini-3.8-flash` | low, medium, high; minimal is rejected |
| `gemini-3.6-flash` | minimal, low, medium, high |
| `gemini-3.5-flash-lite` | minimal, low, medium, high |

Missing model/key is a supported setup state: sign-in, workspaces and projects still work. An invalid configured ID/level/numeric bound fails Settings validation and can prevent the entire API from starting until corrected. The offline command/help below gives safe static correction guidance without echoing supplied values. Inspect before restarting; no credential, session, hash, project or historical run is migrated or reset.

`ORBA_PM_MAX_INPUT_BYTES` defaults to48000, range8192-96000. It counts `len(UTF8(system prompt)) + len(UTF8(canonical provider-schema hint)) + len(UTF8(canonical input snapshot))`; canonical JSON sorts keys, keeps Unicode and uses compact separators. Equality is admitted; exceeding it returns422 `input_too_large` before creating a run or dispatching. This is a local content bound, **not** full HTTP wire size, measured provider tokens or a total bill ceiling. Separate saved-context/snapshot limits remain. Shorten the brief/instructions or exclude the saved plan as context; the UI retains input and existing approvals. Exact authorized request replay retains its original result/configuration even after limits/model change.

The dated [Stage03.3 investigation and model comparison](docs/STAGE033_PROVIDER_RELIABILITY.md) separates upstream failure evidence from hypotheses, documents current prices/lifecycle and recommends3.6/minimal only as a future bounded trial. The owner's ignored3.8 configuration remains unchanged. Metadata visibility, reduced grammar and controlled tests do not prove improved live latency, planning quality or quota.

Run these from `E:\BrosKi\OBRA` (the repository root). Metadata checking requires no Docker/API/browser and sends no project data. `uv --directory apps/api` changes the child cwd; from an existing apps/api shell omit that option.

| Command | Meaning / exit |
|---|---|
| `uv run --directory apps/api python -m scripts.check_pm_config` | Offline only: configured0, missing1, invalid settings2; never proves access |
| `uv run --directory apps/api python -m scripts.check_pm_config --check-model` | Explicit one read-only SDK models.get GET; ready_for_attempt0, every non-ready state2; zero generation/token-count requests |
| `uv run --directory apps/api python -m scripts.check_pm_config --help` | Offline help0; unknown options2 before reading Settings |

Readiness distinguishes missing/invalid configuration, unsupported model metadata for this operation/account, credential problems, temporary unavailability, rate limits, timeouts and unknown evidence. It uses10s HTTP/server and12s outer deadlines with SDK attempts1/transport retries0, no pagination or model switch. Positive exact-model metadata plus the selected model's reviewed structured-output documentation means **ready for a separately authorized attempt**, never generation/grammar/quota/persistence proof. Unreviewed configured IDs now fail closed before a GET; incomplete metadata remains unknown. Missing fields and safe errors never become ready; `live_generation_verified` is always false. See [Stage03.3 plan](docs/STAGE033_PLAN.md), [test plan](docs/STAGE033_TEST_PLAN.md) and [actual evidence](docs/VERIFICATION.md).

Google documents structured outputs and a 65,536-token output maximum for this model; ORBA caps each local response at 6,000 tokens and explicitly requests its supported low thinking level. Request/token/day quotas are project- and tier-specific; the active values must be checked in AI Studio, and are not inferred from the model catalog. Local hourly admission controls are additional application limits, not claims about remaining provider quota. Gate B uses one small real browser generation, authenticated API checks, and independent draft/approval SQL audits; it does not make a duplicate paid API probe. There are no automatic retries or paid continuations. Failed attempts and justified compatibility reruns are recorded separately. A 429 is a recorded failed run and requires an explicit later action. See [model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

Create/open a project and review its **Product Plan** section. Refine the generation brief, optionally add instructions, and explicitly choose **Generate Product Plan**. This is a paid-capable request; no generation occurs on project creation, page load, reload or status checks. Viewers can read; Member/Admin/Owner can generate/edit/copy drafts; **Owner/Admin** can approve. AI output is always a draft. Review its source excerpts, suggestions, assumptions, epics, stories and Given/When/Then criteria. Edit fields and save to PostgreSQL. Resolve or defer blocking confirmations with a reason before approving the exact saved version/revision. Approval records the actor/time and makes that version immutable. Create a free human draft copy to propose corrections without calling the provider. Earlier approvals remain in history.

No provider configured, invalid credentials, rate limits, timeouts and invalid output produce honest setup/errors. Run history contains actual persisted states; no intermediate agent steps are invented. **Check status** uses GET only. A request reference in sessionStorage stores a nonsecret, account/project-scoped UUID only; it is not authentication or a saved brief. A disconnect may leave bounded server work running and usage may already be incurred. There is no resume, takeover or automatic retry. Unknown outcomes offer GET-only recovery. After an exact own failed/interrupted run is confirmed, **Retry generation** rechecks it and starts one fresh UUID/run only on user action. The brief/instructions stay in page memory; **Restore submitted brief** explicitly retrieves an authorized snapshot after reload. Confirmed server-side rejection before admission permits a new explicit submission. Existing approved plans remain unchanged. Inspect status/versions before another request. Save conflicts preserve local edits and offer the latest saved revision for comparison. Unsaved edits are in page memory; leaving a page can discard them (reload/close warns). API authority is rechecked at publication using the original session, not a replacement login.

The provider receives this project's title/description, the submitted brief/instructions and only explicitly selected same-project plan context. User briefs are untrusted data. Generated text never executes tools/code. Unresolved context blockers cannot be silently erased by regeneration. Source excerpts prove textual traceability, not semantic/business truth; humans must review requirements.

Browser requests use `/api/v1/...` on the web origin. Next.js forwards them to the server-only `API_URL` (default http://127.0.0.1:8000). It forwards cookies/Origin/CSRF, preserves Set-Cookie, disables caching and does no authentication of its own. Remove any obsolete NEXT_PUBLIC_API_URL setting; it is no longer used. Keep the browser origin exactly localhost:3000 unless changing WEB_ORIGIN to match.

## Authentication and configuration

FastAPI is the sole authority. Emails are trimmed/case-folded and validated. Newly registered passwords require **15-128 Unicode code points**; existing-password login retains **1-128**, so previously valid12-character credentials still work. Passphrases, spaces, pasted/password-manager values and Unicode are supported without character-class requirements. Passwords are never trimmed, normalized or silently truncated; whitespace-only new passwords remain rejected. The form rejects over-limit input intact instead of clipping it. Argon2id salts every password hash. PostgreSQL sessions store SHA-256 hashes of 256-bit opaque random tokens. No browser-readable storage contains authentication credentials.

This policy update performs no migration, bulk hash rewrite, session revocation or forced reset. Normal login still rotates a presented session and may upgrade eligible Argon2 parameters after verifying the existing credential. The shared `NewPassword` Pydantic type in `apps/api/orba/schemas.py` is mandatory for future new-password/change/reset request fields; current-password verification must keep its separate policy. Password-change and reset workflows are not implemented in this stage. The generated API schema publishes registration15/128 and login1/128 bounds.

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

Stop this checkout's development Next.js server before browser verification: ports3000/3001 share `.next/dev/lock`. Keep development data/volume intact. All backend/browser/fixture/experiment commands share guarded `orba_test` at loopback54330; run them sequentially. Frozen installs/images may need network access, but Gate A never depends on an external AI call.

```powershell
npm exec --yes --package=pnpm@12.14.0 -- pnpm --filter @orba/web exec playwright install chromium
pwsh -NoProfile -File scripts/verify.ps1
uv run --directory apps/api python -m scripts.verification summary
```

**Gate A** is the default normal workflow (`-Scope Core` is an alias). It starts only test-postgres, verifies frozen locks/peers, migrates/checks the guarded test database, runs all backend tests, Ruff, TypeScript, ESLint, production build, and the entire desktop/mobile/tablet regression plus controlled-provider recovery browser suites. Both key aliases/model are explicitly empty in child environments, preventing dotenv fallback. Controlled provider behavior is clearly labeled and test-only; auth/API/PostgreSQL/browser remain real. Test-only authored reports/doubles never count as live model evidence.

Each gate creates a unique directory under `docs/evidence/stage031`, with command argv/log/exit/duration, create-once receipt, start/end source manifest and artifact hashes. The verifier rejects incomplete/skipped/xfail/retried/flaky reports and missing baseline identities. `latest-A.json`/`latest-B.json` point to receipts without rewriting historical attempts. Source identity includes tracked and relevant nonignored untracked app/test/script/config/lock files; dotenv secrets, build/dependency outputs, docs and evidence are excluded. The live nonsecret execution profile additionally records model/prompt/schema/SDK and timeout/output/admission bounds. Local owner-controlled files are not a hostile-machine attestation.

**Gate B** requires a current passing A, configured runtime Gemini key/model, and explicit authorization for one paid-capable attempt. Do not run the following until authorized:

```powershell
# Proposed Stage03.3 trial only; these shell overrides do not edit .env.
# Fresh owner authorization must cover this explicitly selected model.
$env:ORBA_PM_MODEL = 'gemini-3.6-flash'
$env:ORBA_PM_THINKING_LEVEL = 'minimal'
pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid
uv run --directory apps/api python -m scripts.verification summary
```

The existing ignored runtime configuration remains `gemini-3.8-flash` with LOW thinking. The proposed model is a reviewed alternative, not an automatic fallback or a demonstrated reliability fix. See the dated [model comparison and bounded cost calculation](docs/STAGE033_PROVIDER_RELIABILITY.md) before authorizing the trial. Keep the configured 6,000 combined output/thinking tokens, 90s server/model budget, 95s transport, 100s local envelope and one concurrent generation. A model change does not rewrite earlier runs or approved plans.

It records two native commands: one fresh read-only metadata readiness check, then one real browser Generate -> draft API/independent SQL -> edit/reload -> approve/reload -> independent SQL -> unrelated404 journey using the same generated plan. Readiness is bound to the exact A receipt/hash, source, profile, attempt and command times; subordinate preflight and Gate C validate without refetching metadata. Non-ready metadata blocks before generation. A test-only browser transport allowance forwards the first generation POST and aborts every second POST before dispatch; any attempted duplicate fails B. This is not a distributed production quota. SDK/transport/continuation retries stay disabled. Missing opt-in/config/A is BLOCKED/nonzero before dispatch. Provider/validation/persistence/browser failure is nonzero and preserved; authorization is consumed by that attempt, with no automatic retry. A wrapper invocation without `-AllowPaid` only records a BLOCKED preflight. `-Scope Full` exits2 with replacement instructions. Low-level live commands require deliberate opt-in/current A and cannot certify B alone. The old real invalid-key diagnostic remains outside A and requires ORBA_EXTERNAL_FAILURE_OPT_IN=1; normal failure tests use labeled doubles.

Gate C (`summary`) revalidates required commands, native exits, actual structured test results, source/profile identity and artifact hashes. A PASS+B PASS for current source is eligible for VERIFIED; absent, blocked, failed, stale or controlled B is not. Summary exits2 while unverified. Historical failures and live successes remain historical and are never backfilled with a new fingerprint.

Manual deterministic commands (clear runtime key/model variables in that shell, or prefer Gate A's automatic safe profile):

```powershell
$env:ORBA_PM_API_KEY=''; $env:GEMINI_API_KEY=''; $env:ORBA_PM_MODEL=''
uv run --directory apps/api pytest -q
npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e
npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:controlled
```

Fresh per-attempt test artifacts cannot overwrite earlier Stage03 evidence. Browser traces remain off to avoid credentials/cookies in traces. Chromium desktop/mobile/tablet emulation does not establish native-device or all-browser compatibility. Gate runners use an advisory local lock and bounded owned command trees; manually launched test commands must also respect the shared database boundary.

Run the deliberately incorrect expectation separately:

```powershell
uv run --directory apps/api pytest -q tests/experiments/unauthorized_success_experiment.py
uv run --directory apps/api pytest -q tests/experiments/pm_failed_run_success_experiment.py
```

Both must exit **1**: the first incorrectly expects `404 == 200`; the second incorrectly expects an actually failed, unconfigured PM run to be `succeeded`. These are explicit expected-failure experiments, outside normal discovery. Neither is a passing production test; no xfail/skip/green stub is used.

## Limits

Suitable for the current local development scope, **not certified production-secure**. No verified email ownership, password recovery, MFA/passkeys, SSO/OAuth, durable security audit store, production TLS/reverse-proxy configuration, distributed deployment certification, automatic session cleanup worker or penetration test. Registration's duplicate-email response can disclose that an address is registered. No real-time permission push; subsequent protected requests enforce current permissions. Logout clears protected local state immediately; if the server cannot be reached, the UI explicitly warns that revocation is unconfirmed and does not claim the session was revoked. There is no server-side project idempotency guarantee after an uncertain write. Existing TypeScript 6.0.3 / ESLint 9.39.5 compatibility pins remain documented in architecture; 9.x is npm-deprecated until current Next lint plugins support 10.

PM requests are synchronous and bounded (timeout 5–180s, output 512–16000 tokens); the SDK performs one attempt with automatic continuation, retries and function calling disabled. Default local admission: one active run per project, two globally, five attempts/account/hour, twenty globally/hour. The owner's current runtime limits are stricter: one globally, three attempts/account/hour and six globally/hour. PostgreSQL locks coordinate local API workers; this is not a distributed orchestration platform. Lease expiry marks interrupted runs without resuming them. A valid paid response can be discarded after session/permission/lease expiry. Actual dollar costs are not fabricated from missing usage; the dated comparison calculates only the published output-token component and explains billing uncertainty. No cancellation/billing guarantee, semantic truth guarantee, automatic recovery, architect or execution agent is claimed.

See [architecture](docs/ARCHITECTURE.md), [Stage03 plan](docs/STAGE03_PLAN.md), [test plan](docs/STAGE03_TEST_PLAN.md) and [current verification](docs/VERIFICATION.md). Historical evidence is preserved in `docs/VERIFICATION_STAGE01.md` and `docs/VERIFICATION_STAGE02.md`. Stop after Stage03.

