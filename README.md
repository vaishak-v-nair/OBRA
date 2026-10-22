# ORBA · Stage 04

A local development workspace with real accounts, workspace permissions, persisted projects and product/architecture planning. An approved Product Plan can feed an explicit Architect request, producing a technical proposal and a PostgreSQL task dependency DAG for human review. No task is executed. Coding/QA agents, orchestration, GitHub, multiplayer, Skills installation and cloud execution remain later-stage work. Stage04 is **VERIFIED** on source `f6a3a687...`: the authorized single Gemini request and complete browser/SQL review flow passed on 2026-10-22. Current evidence is in [docs/VERIFICATION.md](docs/VERIFICATION.md) and the [live A/B/C report](docs/VERIFICATION_STAGE041_LIVE.md). Further paid attempts require fresh authorization.

Stage03's historical **VERIFIED** source is `661f2828...`, checkpointed at `1aeb882cf9e788948df5ca5eac52e2a682a1f487`. Its actual285 backend/60 regression/33 controlled browser tests and one genuine Gemini3.6/minimal flow remain documented in the [immutable Stage03 A/B/C report](docs/VERIFICATION_STAGE033_LIVE.md). That evidence does not certify the new Architect implementation. Historical503/504 failures and credentials are preserved. New passwords remain15–128 Unicode code points, preserving legacy login/sessions. No additional paid generation or Stage04 commit is authorized.

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

## Architect setup and use

Apply additive migration `7dd7671f9417`, then open an existing project. Approve the
actual Product Plan first. Architecture and Task Graph share one saved proposal and
one local editor. Generate is an explicit usage-triggering action. No provider call
occurs on page load, switching views, graph editing, saving, copying or approval.

Set `ORBA_ARCHITECT_MODEL` explicitly; it never inherits the PM model. The optional
`ORBA_ARCHITECT_API_KEY` overrides the existing resolved PM/Gemini credential only
when nonempty. Process environment overrides API dotenv, which overrides root dotenv.
Keep credentials server-side and preserve existing runtime files. The root template
lists thinking, timeout, output and complete-input-byte bounds. Offline setup check:

```powershell
uv run --directory apps/api python -m scripts.check_architect_config
```

Configured exits0, missing configuration exits1/BLOCKED, invalid settings exits2.
Only explicit `--check-model` performs one bounded metadata GET; readiness never
proves generation or quota. Current account access and Architect schema acceptance
remain unverified until the authorized live flow. Defaults:90s provider,95s transport,
100s outer;6000 combined output/thinking tokens;96000 UTF8 content bytes including
prompt, projected schema and full approved source. Oversized sources fail without
truncation. Existing PM-named concurrency/hourly controls count both planning agents.

Member/Admin/Owner may generate and edit drafts; only Admin/Owner approve exact saved
versions/revisions. Viewers inspect. Dependencies use prerequisite -> dependent.
Roots are ready only within the planning model; every task is unexecuted. Cycles,
missing/self/duplicate/cross-owner edges and invalid source references are rejected.
Coverage means structural linkage, not semantic completeness. Missing coverage needs
an exact documented exception and explicit approver disposition. Blocking decisions
and inherited source confirmations cannot be silently erased. Approved versions are
immutable; free draft copies retain their original source and do not rebase it.

## Verification

Stop this checkout's development Next server first (shared `.next/dev/lock`). All
backend/browser/fixture/experiment operations use guarded loopback `orba_test` and
must run sequentially. Development data and credentials are never reset.

```powershell
pwsh -NoProfile -File scripts/verify.ps1
uv run --directory apps/api python -m scripts.architect_verification summary
```

Gate A is unpaid: test PostgreSQL, frozen dependencies/peers, Alembic upgrade/drift,
all backend tests, Ruff/format, strict TypeScript, ESLint, production build, all prior
regression and PM controlled browser cases, plus Architect controlled browser cases
on desktop/mobile/tablet. Every runtime key alias and both model choices are blanked
before dotenv loading. Test factories replace only their labeled model dependency;
auth/API/PostgreSQL/browser remain real. No skip, xfail, retry or missing baseline
identity can pass. Frozen dependency/image acquisition may require network access.

Stage04 receipts are create-once under `docs/evidence/stage04`; they bind stage/agent,
source and prompt/schema policy, commands, actual native exits, reports and artifact
hashes. The legacy runner/process ownership helpers are reused. Historical Stage03
receipts and its own live command remain historical and cannot certify Architect.
The original285 backend/60 regression/33 controlled identities stay mandatory along
with new tests. Gate C refuses absent, stale, failed or controlled B and exits2/PARTIAL.

## Unpaid Architect browser preflight (Stage04.1)

The first live Architect attempt failed before generation: project creation had
persisted, but the test reloaded Chat before confirming the project route. The
repair waits for the exact route, loaded project/workspace identity, saved PRD
ID/version/revision, actual UI approval, API and independent read-only SQL evidence,
then reloads that project and stops at the Architect entry point.

```powershell
pwsh -NoProfile -File scripts/verify-architect-preflight.ps1
pwsh -NoProfile -File scripts/verify-architect-preflight.ps1 -Mode navigation
```

Both commands are unpaid. They use the real Next/FastAPI/authentication/CSRF and
isolated PostgreSQL stack with a **test-only generation-denying API factory**. It
loads no runtime key. Its labeled configuration sentinel only enables inspection
of the entry control; it is not provider readiness. Browser context guards,
server denial before provider dependencies, dependency tripwires and independent
zero-run SQL checks prevent a successful-looking model operation. No generated
architecture is fabricated. Every invocation saves a unique receipt; an unexpected
generation attempt fails, even when blocked. These commands do not update Gate B.

Full Gate A includes the new navigation/approval regressions on desktop, mobile
and tablet alongside every existing test. For repeatability assessment, run five
separate default preflight commands sequentially, each with its own clean guarded
test database setup and receipt; a later pass never erases an earlier failure.
Do not run backend and browser verification simultaneously.

**Paid Gate B requires fresh authorization.** Its previous pre-dispatch failure
remains in [the historical live report](docs/VERIFICATION_STAGE04_LIVE.md). After
fresh explicit owner authorization only, the proposed bounded profile is:

```powershell
$env:ORBA_ARCHITECT_MODEL = 'gemini-3.6-flash'
$env:ORBA_ARCHITECT_THINKING_LEVEL = 'minimal'
$env:ORBA_ARCHITECT_TIMEOUT_SECONDS = '90'
$env:ORBA_ARCHITECT_MAX_OUTPUT_TOKENS = '6000'
$env:ORBA_PM_MAX_CONCURRENT = '1'
pwsh -NoProfile -File scripts/verify-architect-live.ps1 -AllowPaid
```

No dotenv is edited by these overrides. The command requires current passing A,
explicit selection/key and one-worker/zero-retry/one-generation limits. It checks
metadata, creates a clearly human-authored compact source in guarded test storage,
approves that source through the real UI, and sends ONE Architect request. It reuses
that response for validation, independent SQL/hash/graph/coverage inspection, browser
rendering, human criterion editing/reload, exact approval/reload and outsider404.
Phase1 shares the unpaid setup helper and keeps generation closed until all source
approval/reload/SQL checks pass. Phase2 permits one Architect POST. Phase3 closes
generation and reuses that artifact. The source fixture is not PM model evidence.
Additional PM/Architect generation POSTs
are blocked before forwarding and fail B. Failure stops the command; no fallback,
automatic model switch or retry exists. Actual usage is recorded when returned; no
cost or response metadata is invented. These local receipts are operational evidence,
not hostile-machine attestation or production security certification.

The isolated deliberately incorrect assertion is separate from normal discovery:

```powershell
uv run --directory apps/api python -m scripts.architect_false_success
# Underlying pytest must exit1; the wrapper records and validates that expected failure.
```

The older authorization and PM wrong-success experiments remain unchanged. Browser
traces stay off to avoid recording secrets. Chromium device emulation does not prove
native-device or all-browser support. See [current verification](docs/VERIFICATION.md),
[Architect design/API reference](docs/ARCHITECTURE_STAGE04.md) and the preserved
[Stage03 checkpoint report](docs/VERIFICATION_STAGE033_CHECKPOINT.md).

## Limits

Suitable for the current local development scope, **not certified production-secure**. No verified email ownership, password recovery, MFA/passkeys, SSO/OAuth, durable security audit store, production TLS/reverse-proxy configuration, distributed deployment certification, automatic session cleanup worker or penetration test. Registration's duplicate-email response can disclose that an address is registered. No real-time permission push; subsequent protected requests enforce current permissions. Logout clears protected local state immediately; if the server cannot be reached, the UI explicitly warns that revocation is unconfirmed and does not claim the session was revoked. There is no server-side project idempotency guarantee after an uncertain write. Existing TypeScript 6.0.3 / ESLint 9.39.5 compatibility pins remain documented in architecture; 9.x is npm-deprecated until current Next lint plugins support 10.

PM requests are synchronous and bounded (timeout 5–180s, output 512–16000 tokens); the SDK performs one attempt with automatic continuation, retries and function calling disabled. Default local admission: one active run per project, two globally, five attempts/account/hour, twenty globally/hour. The owner's current runtime limits are stricter: one globally, three attempts/account/hour and six globally/hour. PostgreSQL locks coordinate local API workers; this is not a distributed orchestration platform. Lease expiry marks interrupted runs without resuming them. A valid paid response can be discarded after session/permission/lease expiry. Actual dollar costs are not fabricated from missing usage; the dated comparison calculates only the published output-token component and explains billing uncertainty. No cancellation/billing guarantee, semantic truth guarantee, automatic recovery, task execution or orchestration is claimed. The Architect proposes technical plans only.

See [architecture](docs/ARCHITECTURE.md), [Stage03 plan](docs/STAGE03_PLAN.md), [test plan](docs/STAGE03_TEST_PLAN.md) and [current verification](docs/VERIFICATION.md). Historical evidence is preserved in `docs/VERIFICATION_STAGE01.md` and `docs/VERIFICATION_STAGE02.md`. Stop after Stage04; live Architect verification still requires fresh authorization.

