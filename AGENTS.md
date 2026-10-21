# ORBA engineering contract

Stage authority is the owner's request. Stage03 is authorized: one real Product Manager planning agent, using the owner's Gemini runtime credential and the official Google GenAI SDK. Preserve Stage01/02 project data, authentication and workspace isolation. Do not start Stage04 or other agents automatically. No public deployment, destructive operations, credential changes, or external messages without owner authorization.

## Truth and verification

- Never claim success from files existing. Execute the implementation and relevant checks.
- Never fabricate terminal output, screenshots, API responses, DB records, agents, test results or evidence.
- No dummy success states, fake authentication, fake AI agents, fake GitHub services or fake Skills installation.
- Tests exercise application code. Isolated unit tests may use justified, explicitly identified mocks. Stage03.1 also explicitly authorizes labeled test-only controlled-provider deterministic integration/browser tests; all auth/API/PostgreSQL/browser behavior remains real, and these never prove live model success. A skipped test is not passed.
- Preserve real command failures and fix their causes. Never weaken assertions, disable checks or remove tests to get green.
- If a required dependency cannot be reached, report BLOCKED with actual error and missing dependency. Distinguish implemented, planned, blocked and verified.
- Mandatory checks must pass before a VERIFIED verdict. Otherwise use PARTIAL, BLOCKED or FAILED. Update docs/VERIFICATION.md with commands, exit statuses, counts and limitations.
- Test cleanup is allowed only against the guarded isolated `orba_test` database and role. Never clear development project data. Do not run backend and E2E tests simultaneously: both use this test database.

## Architecture and development

Use Next.js App Router, strict TypeScript, Tailwind, shadcn/ui, Lucide; FastAPI, Pydantic v2, SQLAlchemy 2, Alembic and PostgreSQL. Use pnpm and uv with committed lockfiles. Select current compatible stable releases; document compatibility exceptions. Do not substitute SQLite. Alembic migrations are the schema authority; no startup create_all.

Keep business API behavior in apps/api; apps/web is the UI. Semantic theme tokens live in globals.css. Shared creation logic lives in ProjectForm. Use native controls and existing helpers before adding abstractions or dependencies. No empty shared packages.

Handle invalid input, missing records, database failure, loading, empty and error states. Keep drafts on save failures. Never automatically retry a POST. Do not log credentials or project descriptions in error logs. Bind local services and database ports to loopback. Do not claim production security certification. Stage 02 must enforce real authentication and workspace isolation.

Required verification: migrated real test PostgreSQL; persistence/list/retrieve/invalid/not-found/readiness tests; actual browser creation -> detail -> reload -> list; meaningful negative paths; lint; strict typecheck; production build. See README.md and docs/TEST_PLAN.md. Browser/device emulation does not establish native-device or all-browser compatibility.

## Stage 02 security rules

- New credentials use the shared NewPassword type:15-128 Unicode code points, no normalization/truncation or composition rules; whitespace-only new values remain invalid. Login stays1-128 for existing credentials. Future change/reset fields must reuse NewPassword; do not add such workflows implicitly. Never bulk rewrite hashes, force resets or revoke sessions for a policy rollout. Preserve normal presented-session rotation and eligible parameter rehash. Keep browser paste intact and validate bounds explicitly.

- FastAPI alone authenticates. Use Argon2id and hashed opaque PostgreSQL sessions; no hardcoded users, auth bypass, browser-stored authority or client-trusted ownership.
- All cookie-authenticated writes require validated Origin and CSRF. Start Uvicorn with --no-proxy-headers. Never log passwords, hashes, cookie/session/CSRF/invitation tokens.
- Every resource request validates current membership. All membership, invitation and project writes lock the workspace before role checks. Preserve the final Owner; Admins only manage Member/Viewer. Invitation acceptance must be atomic, email-bound, expiry/revocation/use checked, and recheck inviter privilege.
- Never assign legacy projects to the first registrant. Preserve every original field. Legacy ownership is restricted; only scripts.claim_legacy with explicit IDs and --apply may transfer data. No public claim endpoint. No production database reset or migration downgrade to avoid complexity.
- Keep the intentionally incorrect authorization experiment outside normal test discovery. Its actual exit1 is expected and must never be called a passing production test. Mandatory suites must contain no skips, xfail or dummy drivers.
- Use same-origin Next API proxy without duplicating auth. SessionStorage may hold selected-workspace preference and Stage03's nonsecret account/project-scoped request/copy UUID references; never credentials, briefs or authentication authority. Never render protected content until session checks succeed. Manual invitation sharing is not email delivery.
- Run scripts/verify.ps1 plus relevant schema/migration/auth/role/tenant/legacy and browser tests. Stage02 baseline is checkpoint e3fccd6. Preserve the owner's ignored .env; never print, commit or replace credentials.

## Stage03 PM rules

- One real configured provider only; no canned generated PRDs, fake runs, automatic paid generation, tool execution or orchestration. A run succeeds only after a genuine response passes Pydantic validation and the complete relational draft commits atomically.
- Real-model API and browser verification are both mandatory for VERIFIED. Isolated provider doubles prove unit/error handling only; authored database fixtures are not model evidence. Missing model/credential/access is BLOCKED for live scope. Core-only success is not full verification.
- Preserve historical Full/standalone outcomes; Stage03.1 uses independent Gate A/B/C with source/profile-bound immutable receipts. Do not dispatch a paid request until Gate A passes, diagnostics are reviewed, the command is ready, and the owner explicitly authorizes that next attempt. Normal verify.ps1 is Gate A; verify-live.ps1 requires -AllowPaid. Preserve separate outcomes for the historical integrated Full command and standalone live checks. A later successful model/browser call does not erase a failed Full run. Test resets clear local admission counters; track paid verification attempts across resets and stop bounded verification loops. Current Stage03 acceptance evidence and remaining provider-availability blocker are in docs/VERIFICATION.md. The next explicitly authorized Stage03.1 attempt returned upstream503 UNAVAILABLE and exited1; do not retry it without fresh authorization.
- Release the authentication transaction before the model call. Use durable idempotency/deadlines, short transactions, workspace locks, current original-session checks and fenced terminal transitions. Never overwrite success with failure after an uncertain commit or retry a POST automatically.
- Draft edits use exact revisions and server-owned provenance; Owner/Admin approval binds exact version/revision/actor/time. Keep approved versions immutable. Blocking confirmations require recorded human disposition; preserve transitive uncertainty and source snapshots.
- Runtime credentials stay server-side. Root .env is permitted for local runtime configuration; API-specific .env can override it. Model selection must be explicit. Provider configuration is not proof of successful generation.
- The owner selected gemini-3.8-flash and requested quota-conscious use. Local configuration permits one concurrent generation with 6000 output tokens, three attempts/user/hour and six globally/hour. Provider project/tier quotas are separate and unknown; no automatic retry, continuation or generation on page load. Keep live verification calls small and sequential; preserve actual quota failures.
- Preserve safe actual failure reasons/metadata, never raw secrets, provider bodies or user briefs in logs. Keep the intentionally wrong-success experiment separate and record its actual exit1. Stop after Stage03.


## Stage03.1 reliability contract

- No automatic model retry. Retain unknown request UUIDs for GET-only recovery; exact own terminal-run confirmation precedes explicit new-UUID Retry. Authoritative pre-admission rejection must not invent a terminal run. Restore input only by explicit authorized GET; never store briefs/tokens in browser storage.
- ORBA_PM_TIMEOUT_SECONDS is the server/model budget, transport adds5s and the outer envelope10s. Logs distinguish upstream HTTP504 from local/transport/proxy timeout. Stored timings stop before terminal commit; log acknowledged commit separately. Do not claim this fixes upstream availability.
- Gate A empties both key aliases and model, binds migrations/drift/tests to guarded orba_test, preserves all baseline identities and rejects missing/skip/xfail/flaky/retried reports. Test factory overrides only the model dependency and refuses development DSNs; no production fake-provider flag.
- Gate B uses one actual browser generation, fresh draft and approval SQL graph/hash audits and real isolation checks. Explicit opt-in/current A/config required; no duplicate paid probe. Old successful live evidence cannot certify changed source. Gate C refuses absent/stale/controlled evidence. Do not rewrite historical failed attempts or automatically commit the owner's uncommitted Stage03 work.

## Stage03.2 provider readiness

- `scripts.check_pm_config` is offline by default. `--check-model` explicitly performs at most one bounded official SDK metadata GET with no generation, token-count request, retry, pagination or database mutation. Metadata readiness never proves model execution, schema acceptance, quota, latency or persistence. Preserve unknown results and safe Settings/provider errors without printing inputs, bodies, headers or keys. Never switch the owner's model automatically.
- B records a native read-only readiness command and strict attempt/source/profile/A-receipt-hash linkage before its single model-backed browser flow. Subordinate preflight and Gate C validate artifacts without external requests. The test-only browser allowance forwards one generation POST and aborts subsequent POSTs before dispatch; any blocked duplicate fails B. These controls are not a distributed production quota.
- Preparation/Gate A/read-only model inspection is authorized for Stage03.2. STOP for fresh explicit owner authorization before any next paid generation. Historical503/504 and failed live receipts remain immutable; no metadata or controlled-provider test can change PARTIAL into VERIFIED.

## Stage03.3 explicit model policy

- New generation allows only reviewed gemini-3.8-flash, gemini-3.6-flash or gemini-3.5-flash-lite, with optional models/ prefix. ORBA_PM_THINKING_LEVEL defaults low; minimal is valid only for3.6/3.5 Flash-Lite. Share the policy across Settings/readiness/adapter; reject incompatible copied settings before SDK dispatch. No automatic switch, alias fallback, retry or paid continuation. Preserve the owner's ignored3.8 configuration until an explicitly authorized selection change.
- ORBA_PM_MAX_INPUT_BYTES defaults48000 (8192-96000): sum UTF8 lengths of system prompt, canonical projected schema and canonical snapshot. Equality passes; reject oversized new requests before admission and handle invalid Unicode at the earlier request-hash boundary. This is not provider tokens or a dollar ceiling. Resolve exact authorized replay before applying a new cap/context snapshot; never restamp historical diagnostics/models/approvals.
- ProductDocument/graph/source validation remain the authoritative full contract. pm-v2 removes only optional human-owned generation hints and keeps every PRD field; retain pm-v1 for history. Persist original nonsecret generation_configuration and merge terminal diagnostics. New A/B profile binds thinking, byte cap and projected-schema hash; per-model metadata docs must match the exact selected policy.
- Keep startup/CLI configuration errors input-hidden, all baseline identities mandatory, and new coverage additive. Stage03.3 preparation/read-only metadata/GateA is authorized, not paid generation. Stop for a fresh concrete one-request authorization after A passes. Upstream503/504 cause is not proven by grammar size or thinking settings; do not claim a local uptime/latency fix or use old B to certify changed source.
