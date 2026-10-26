# ORBA engineering contract

## Stage05B authority (supersedes older stage boundaries)

- Owner authorizes durable scheduling, scoped worker credentials, leases, fencing
  and immutable handoff receipts only. Preserve checkpoint ab7c7ac and all prior
  evidence and90excluded files. No commit/push/discard, AI call or Stage05C/D/06.
- OrchestrationTask execution remains awaiting_executor/cancelled. A claim, ack,
  heartbeat or manifest is never code execution or verified completion. No worker
  completion API, executor or generated-command execution is permitted.
- PostgreSQL coordination precedes workspace/project/run and worker/lease locks.
  Recheck DB time and current credential after waiting. Flush tentative writes,
  then apply the final locked credential/clock publication guard;no ORM mutation
  may follow it before commit. Publication is not later HTTP arrival. Same-key claim recovery is
  durable; unknown POST outcomes never silently mint a new request or retry.
- Immutable snapshots remain authoritative. New dispatch and handoff admission
  revalidates current approved source and DAG. Preack recovery is bounded; postack
  expiration/release/revocation requires reconciliation, never auto redispatch.
- Worker authentication is dedicated hashed opaque Bearer credentials provisioned
  by a local operator; no public self-registration or browser-auth impersonation.
  Credentials belong in exclusive private files outside the repository, not logs,
  evidence, manifests, browser storage or ordinary command output.
- New Stage05B gates bind new fingerprints under docs/evidence/stage05b. Historical
  Stage05A proof-v2 remains strict and immutable. No paid provider or fake executor
  evidence. Never run backend and browser suites concurrently against orba_test.

## Stage05A authority (supersedes older stage stop boundaries below)

- Owner authorizes the deterministic orchestration foundation only. Preserve
  Stage04 checkpoint bb880486bf7d8441cc6415f4dc6d6085a731151b, historical evidence
  and the nine excluded untracked files. No commit/push/discard or paid model call.
- No scheduler, executor registration/claim, handoff, task execution, QA or
  completion API. Overall Stage05 remains IN PROGRESS. Do not start05B or06.
- Runs bind exact approved architecture/PRD IDs, versions, revisions and hashes;
  revalidate current approval, strict source/coverage/DAG and human dispositions
  under existing workspace/project locks. Canonical snapshots are immutable.
- Edges remain prerequisite -> dependent. Reuse task_graph.analyze. Root
  eligibility is separate from execution_status=awaiting_executor. No task may
  become running, successful or verified-complete in05A. Cancelled is terminal.
- Creation and task/edge/event publication share one transaction. Idempotency is
  project+actor+request UUID; conflicting inputs409, exact replay200, creation201.
  Resolve authorized replay before new-source checks. No automatic POST retry.
- Central guarded transitions increment revision; run lock serializes event
  sequence. Definitions/edges and events are immutable via DB triggers. No event
  writer API. Original session and current workspace roles fence every mutation.
- SessionStorage may retain account/workspace/project-scoped nonsecret request
  UUID and exact architecture ID/version/revision references for GET recovery
  and explicitly requested same-key retry. Never credentials, briefs or snapshots.
- Normal scripts/verify.ps1 runs Stage05A Gate A, retaining every Stage01–04
  regression. Separate scripts/verify-orchestration-local.ps1 runs local Gate B;
  no AI or fake executor is required or permitted. Both bind the same source and
  local contract under docs/evidence/stage05a. Stage04's excluded gate.lock stays
  untouched. Controlled source fixtures are authored data, not generation proof.
- Local Gate B proof-v2 requires strict UUID/integer/hash/record types and actual
  nonempty SQL tasks, dependencies (zero edges allowed), canonical source and full
  lifecycle events. Reconcile SQL/API/graph/source identities and checksum; absent
  values, coercion, normalization or claimed counts never substitute for records.
  Historical proof-v1 receipts stay immutable and cannot certify repaired source.
- The isolated orchestration_completion_experiment.py intentionally asserts
  verified completion; actual pytest exit1 is required, outside normal discovery.
  Never run backend and browser suites concurrently against orba_test.

Stage authority is the owner's request. Stage04 is authorized: preserve the Product Manager and add one Architect planning agent plus a persisted task DAG, using the official Google GenAI SDK. Preserve Stage01/02 project data, authentication and workspace isolation. Do not start Stage05, task execution or other agents automatically. Stage04 paid generation requires fresh explicit owner authorization. No public deployment, destructive operations, credential changes, or external messages without owner authorization.

## Stage04 current authority (supersedes older stage stop boundaries below)

- Stage04.1 repairs browser setup only. No new paid generation is authorized; do not change provider/model/budgets. Await exact project route plus loaded project/workspace identity before reload; approve the exact saved PRD version/revision through the real UI and independently verify actor/time/hash in PostgreSQL. Existing AuthGate path/account/workspace fencing stays authoritative.
- Unpaid `scripts/verify-architect-preflight.ps1` uses only the guarded test factory, never runtime credentials. Its configuration sentinel is not readiness or generation proof. Browser-context denial, server denial before dependencies, provider tripwires and zero-run SQL checks are required. Unexpected attempts fail even if blocked. Shared Phase1 must pass before future explicitly authorized one-request Phase2; Phase3 never generates. Five clean standalone runs are independent evidence, never test retries or live Gate B.
- Preserve checkpoint `1aeb882cf9e788948df5ca5eac52e2a682a1f487` and all historical receipts. Stage04 work is uncommitted; no new commit/push without owner permission.
- Architect consumes the authoritative current approved same-project PRD, bound by ID/version/revision/hash. Recheck it before dispatch, atomic publication and approval. New unapproved PRDs do not stale the current agreement; a new approval does. Copies retain source, never silently rebase.
- Only strict validated proposals, relational tasks/dependencies/traces and actual provider metadata may persist as success. No code, tools, SQL, migrations or task execution from generated designs. All tasks remain proposed/needs clarification; dependency-ready is not implemented/tested/deployed.
- Edges are prerequisite -> dependent. Enforce missing/self/duplicate/cyclic/cross-owner rejection, deterministic order/impact, exact criterion parentage, all-contributor source prerequisites and structural coverage. Preserve inherited uncertainty outside model-owned text. Exact exceptions/blocking decisions need saved-revision human dispositions before Owner/Admin approval.
- Shared PM/Architect admission uses the existing PM-named limits. No DB transaction spans a model request. Retain original-session fencing, durable request UUIDs, one attempt/zero retries, bounded deadlines and honest stale/unknown outcomes. GET recovery never dispatches generation; explicit retry requires exact own terminal confirmation and a new UUID.
- Architect model selection is explicit via ORBA_ARCHITECT_MODEL; optional nonempty ORBA_ARCHITECT_API_KEY overrides the resolved server credential. Preserve the owner's dotenv. No model switch/fallback. Default budgets90/95/100s,6000 output/thinking tokens,96000 UTF8 content bytes; no truncation or paid continuation.
- Current unpaid Gate A is scripts/verify.ps1 (all prior regressions plus new Stage04 cases). Stage04 A/B/C use docs/evidence/stage04 and stage/agent/source/prompt/schema-bound receipts. PM's historical live proof never certifies Architect. Controlled model doubles remain test-only with real auth/API/PostgreSQL/browser.
- scripts/verify-architect-live.ps1 -AllowPaid requires fresh explicit owner authorization after A passes. One worker, at most one generation across the entire workflow, zero retries. Authored source setup is approved through the real UI without PM generation; reuse the single architecture for SQL/browser/edit/approval/isolation. Missing or failed B means PARTIAL.
- Keep the deliberately incorrect Architect success assertion isolated; its genuine pytest exit1 is expected and never a passing production test. Do not run backend and browser suites together against orba_test. Stop after deterministic Stage04 implementation; do not start Stage05.

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

- Public sign-up/sign-in controls stay disabled until initial client/session
  initialization finishes. Forms declare POST; never allow a missing client
  handler to submit credential fields through a native GET. Readiness is not
  authentication authority; FastAPI still validates every operation.

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
