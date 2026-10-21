<!-- /autoplan restore point: C:/Users/vaish/.gstack/projects/OBRA/main-autoplan-restore-stage03.md -->
# ORBA Stage 03 implementation plan

Status: **PARTIAL**. Implementation and regression checks ran:102 backend,51 desktop/mobile/tablet browser and1 real provider-failure browser test passed. Genuine gemini-3.8-flash API generation passed, and the final standalone live browser generation/edit/reload/approval/isolation flow passed (1 in1.4m), with a fresh SQL audit. Earlier selector failures were corrected without removing assertions. The latest integrated Full still exited1 at its live API command on actual provider504 DEADLINE_EXCEEDED at90s. Six owner-credential generation attempts are recorded; no more calls were made. Actual results and blockers are authoritative in docs/VERIFICATION.md. Stage04 is excluded.

## Authority, checkpoint and observed baseline

The owner's Stage 03 request authorizes one real Product Manager planning agent. The owner explicitly approved a local checkpoint named `chore: checkpoint Stage 02 baseline`. Commit `e3fccd6` now preserves all 94 intended Stage 01/02 files. No remote is configured. Credentials, dependencies, build artifacts and browser reports are ignored. The initial staged whitespace check exited 2 on existing CRLF/trailing whitespace; the checkpoint preserves those bytes rather than rewriting prior work.

The fresh unchanged Stage 02 `pwsh -File scripts/verify.ps1` exited 0: 44 backend tests in 25.79s and 42 browser tests in 1.8m, including frozen dependencies, real PostgreSQL, migration/drift, Ruff, strict TypeScript, ESLint and production build. This is the regression baseline, not Stage 03 evidence. Stage 02 historical evidence remains separately archived.

Read AGENTS.md, README, architecture, roadmap and verification; inspected the API models/schemas/session/CSRF/role dependencies, project and workspace routes, both migrations, DB/test setup, Next route handler/client/project components, Playwright configuration and existing tests. Stage 02 source is the authority for reused behavior. The stale AGENTS restriction against starting Stage 03 is superseded by the owner's explicit Stage 03 request and will be updated with that authority.

`ORBA_PM_API_KEY` and `ORBA_PM_MODEL` are absent from process environment and apps/api/.env at intake. A pending question asks the owner to configure them locally, without sending a secret in chat. Codex's ChatGPT authentication is not an ORBA runtime credential. Live tests cannot pass until actual runtime configuration works.

Autoplan helper binaries are absent at their documented paths. Use interactive degraded defaults; no onboarding, telemetry, global memory edits, helper success or cross-model consensus is invented. UI and DX scope are both present. Reviews must finish sequentially CEO -> Design -> DX -> Eng. Each independent voice is identified by actual source/model family.

## Product outcome and boundaries

A user opens an authorized project, reviews a bounded brief and optional instructions, explicitly requests generation, waits for a real model call, reviews an attributed draft, edits requirements/stories/criteria, and explicitly approves one exact version. A later visit retrieves persisted data. No paid request occurs on project creation or page load.

Evidence means traceability to the supplied brief/context plus actual provider execution metadata. It does not mean external research or verified business facts. Model-suggested scope, assumptions and questions must be visibly distinct from supplied requirements. No commands, code, tool calls, repository instructions or generated links are executed.

One official Google GenAI SDK adapter is being implemented, matching the owner-provided GEMINI_API_KEY. No Architect/coding/QA agents, autonomous orchestration, GitHub automation, Skills intelligence, Model Hub, Redis/Celery/LangGraph, multiplayer, public deployment or database reset is in scope.

## Reuse and code boundaries

| Subproblem | Existing authority | Proposed extension |
|---|---|---|
| Sessions, identity, CSRF, Origin | orba/security.py, auth.py | Reuse Identity/csrf_guard unchanged |
| Current membership and write serialization | security.membership(lock=True), require_role | All PM writes lock workspace before checking current role |
| Authorized project lookup | orba/main.py get_project | Extract one reusable helper preserving existing private 404 semantics |
| DB lifecycle, safe errors | db.py, main.create_app | Small PM router/service/provider modules and safe PM error envelope |
| Schema migrations | Alembic versions, env.py | Additive Stage 03 migration, no rewrites of old rows |
| Protected UI, workspace selection | session.tsx, Shell/AuthGate | ProductPlan section inside the existing protected project detail |
| Native controls and theme | Button, globals.css | Labeled fieldsets/details/forms, existing semantic tokens |
| Same-origin transport | web API route + lib/api.ts | Add PUT; explicit bounded long-request timeout for PM generation only |
| Real verification | prepare_tests, pytest, Playwright, verify.ps1 | Preserve every old scenario; sequential test DB ownership |

## Proposed authoritative schema

Pydantic v2 is the contract. Reject extra fields, wrong types, whitespace-only text, excessive sizes and incomplete plans; do not turn arbitrary text into a plan. Use bounded strings/lists and explicit priority enums. Provider-supported strict JSON output is requested, then server validation always runs.

The document contains product name, summary, problem, solution, target users, goals, in/out scope, functional and nonfunctional requirements, product prerequisites, assumptions, risks, questions, confirmation items, epics, stories and Given/When/Then criteria. Each epic has a goal and priority. Each story has a stable local key, title, description, `As a ... I want ... so that ...` statement, priority, requirement references and dependency keys. Validate unique keys, real dependency/reference targets and cycles. Every story must have observable acceptance criteria.

Overview fields as well as requirements/epics/stories/criteria carry provenance: supplied brief/context, suggestion, assumption, or human edit. Supplied-source evidence must quote the actual identified immutable input; quotation membership does not establish semantic entailment or independent factual verification. Provider output cannot claim human editing, confirmation or approval. On save the server compares stable keyed nodes with the stored document and assigns human provenance/actual editor to changed/new nodes; unchanged nodes retain their real origin regardless of client claims. Missing target-user, solution or business detail is explicitly proposed/unknown and can produce clarification questions rather than fabricated certainty. Human review remains explicit.

Relational storage has one representation per concept:

* `product_manager_runs`: UUID, project/workspace/initiator/initiating-session FKs, status, client idempotency UUID, immutable explicit-client-input hash plus separate execution-snapshot hash and title/description/brief/instructions/context snapshot, provider, requested and returned model, prompt version/hash, created/start/completion/deadline times, provider response/request IDs when returned, nullable actual usage JSON, safe error category, internal diagnostic UUID/details. Uniqueness for project/initiator/client request ID and a partial unique index for one pending/running run per project. Enforce project/workspace agreement using a named composite FK/parent unique key, rather than unrelated FKs alone.
* `product_plans`: UUID, project FK, version, state draft/approved/superseded, optimistic revision, non-epic document fields in validated JSONB, nullable unique generating run FK, optional same-project source-plan FK and immutable source revision/hash/input evidence for human draft copying, durable copy-request UUID/hash scoped to project/creator, creator/editor, approval actor/time, created/updated times. Unique project/version and partial unique current approved project. Same-project composite FKs bind generating run and copy source; named origin/state/approval-metadata checks reject impossible combinations. The run's resulting plan ID is derived from this one-to-one FK, avoiding a circular duplicate reference. Generation and human-copy origins are explicitly distinguishable.
* `product_epics`: UUID, plan FK, local key, title, goal, priority, provenance, display order.
* `product_stories`: UUID, plan/epic FKs with a composite ownership constraint, plan-wide unique local key, title, statement, description, priority, requirement/dependency keys, provenance, display order.
* `product_acceptance_criteria`: UUID, plan/story composite ownership FK, stable plan-wide unique local key, Given/When/Then text, provenance, display order. Requirements, uncertainty and confirmation nodes also have stable plan-scoped keys; human dispositions record actual actor/reason/time. The extra plan IDs enforce ownership/uniqueness, not a competing document representation.

Root JSONB contains no duplicate epic/story/criterion tree. API serialization assembles the validated document from relational children. Snapshot copies are intentional immutable execution evidence, not competing current-plan state. All times are aware UTC. Parent/lookup/order indexes and FK constraints are named. Fetch related rows with bounded eager loading to avoid per-story queries.

## Generation lifecycle and concurrency

```text
authenticated request + Origin/CSRF + bounded input
  -> workspace lock -> recheck current write role -> authorized project snapshot
  -> same client key? replay stored run; changed input? 409
  -> active unexpired project run? 409
  -> commit pending run -> commit running + hard deadline
  -> release DB transaction -> await one real SDK request
  -> strict response/schema/provenance validation
  -> workspace lock -> recheck initiator privilege and run lease
  -> persist complete relational draft + run success in ONE commit

provider/config/schema failure -> failed run + safe diagnostic; no plan
cancelled process/request or expired lease -> interrupted; no late success
```

Do not hold workspace/DB locks while waiting for the provider. Async SDK calls use an outer total timeout and HttpRetryOptions(attempts=1) and automatic_continuation=False. DB phases use their own sessions, run outside the event loop when appropriate, and never share a Session concurrently. New calls have one durable idempotency key scoped to the initiating account/project; identical replay returns the existing result, payload mismatch returns 409. An explicit regeneration with a new key creates a new draft version. A partial unique index independently protects against multiple workers.

Use a normal synchronous FastAPI generation endpoint in its framework worker thread, keeping all SQLAlchemy phases sequential in that thread. The provider adapter opens one scoped Google GenAI async client inside a small `asyncio.run` boundary and applies an outer total deadline to its actual async call; no shared client crosses event loops. This uses the existing synchronous database stack and avoids a second ORM engine or an abandoned database worker. Provider latency occupies a worker thread but no DB connection; durable admission bounds actual model work. Core routes/health must remain responsive in verification. Browser disconnect cannot forcibly cancel a Python worker/provider request; original-session checks and persisted deadlines still govern publication. There is no background queue, durable resumption or remote cancellation guarantee.

Compare replays using the original canonical validated client-input hash (brief/instructions/explicit context identity/revision), before capturing fresh project state. Do not include current project text, current context content, prompt version or runtime model in that hash. Normalize whitespace only where the schema explicitly does so; omitted and empty optional instructions normalize consistently. The separate execution snapshot/hash records what was actually sent. A replay after project/configuration/context edits returns its original outcome; changed explicit input under the same key409. Copy replay uses a durable client UUID/hash and returns the original copy even after approval; a fresh copy needs an explicit new key.

Use a persisted deadline with a buffer for bounded DB finalization. A small lease reconciler and project/run reads mark expired active records interrupted. It does not resume work. One process must not interrupt another process's unexpired lease. Finalization checks that its run remains active and unexpired so a delayed response cannot become a second success. If the DB is unavailable while recording a failure, return unconfirmed persistence and let the lease expire; do not claim a saved failure. No remote request cancellation or provider-level exactly-once execution is promised.

Authorization is checked at the start and before committing the result, including the original unexpired/unrevoked session, active user and current membership/write role. Logging out, expiring/revoking the initiating session or removing/demoting its user during execution prevents publication. Snapshot actor/session IDs then release the existing authentication dependency's checked-out DB transaction before awaiting the SDK; fresh short sessions own subsequent phases. The provider may already have consumed tokens; record returned usage even when final authorization prevents publication. No authorization or model choice comes from generated content.

Publication linearizes in its final bounded transaction: lock workspace, then project/run/plan as needed, then original session/user; re-read current role, session revocation/expiry and active user using database UTC time before conditional publication. Logout already updates that session row, so row locking serializes it without introducing a reverse workspace dependency. If logout commits first, publication fails; if publication locks first, logout may briefly wait and then revokes subsequent access. Allocate every version under the same workspace/project lock. A terminal run cannot transition again; stale lease checks and conditional writes fence late work. Concurrent approval/Save/copy follows the same workspace->project->plan order. Expiry is evaluated at the publication authorization point, not promised as an atomic clock action at a later network acknowledgement.

Browser disconnect/navigation is best-effort continuation: a still-running request handler may finish after final authority checks. Actual handler cancellation/process loss marks interruption directly or by expired lease. No detached task or guaranteed remote billing cancellation is promised. Terminal states are immutable and failure recording is conditional on still-active state; an uncertain DB commit must not overwrite an already committed successful run with failed. Return unknown persistence when the DB cannot establish what committed.

Serialize short global admission before the workspace lock on generation starts, then release both before provider execution. Proposed defaults are two active generations globally, one per project, five admitted attempts/account/hour and twenty globally/hour; replay does not consume admission. Count admitted failures conservatively and expose only safe Retry-After, never another workspace's IDs/counts. Final numeric policy is taste C04. This is a bounded local attempt policy, not a provider-wide currency budget.

## Provider, prompt and safe diagnostics

Configuration follows Settings with server-only `ORBA_PM_API_KEY` (SecretStr), explicitly configured `ORBA_PM_MODEL`, timeout bounded to 5..180 seconds, and max output tokens bounded to 512..16000. Proposed defaults are 60 seconds and 6000 output tokens; model/key have no default. No custom client-controlled base URL or model override is accepted. A provider capability response exposes configuration completeness and nonsecret configured model/limits only.

Create a typed `ProductManagerModelProvider` boundary with one Gemini implementation, maintained official SDK pinned by uv.lock. Request strict JSON schema derived from Pydantic through stateless GenerateContent at the explicit official Gemini endpoint, no tools, bounded context/output and no automatic retries. Capture the response envelope/model/IDs/usage before separately validating output so a Pydantic failure does not discard returned execution evidence. Leave absent metadata null. Reject refusal, incomplete/truncated/empty output, malformed JSON and Pydantic/provenance failures. Do not invent cost, usage, identifiers or timestamps.

System prompt lives separately at a versioned path, with its version/hash saved on every run. User data is sent as a bounded data object, separate from system instructions. Optional prior-plan context is included only through an explicit authorized plan ID and immutable revision snapshot from the same project. No session cookie, password, API key, unrelated workspace, instructions from files or repository contents enter model context.

Catch named SDK authentication/permission/not-found/rate-limit/timeout/connection/status errors, validation errors and SQLAlchemy errors. Public responses contain safe actionable categories/messages and run/diagnostic reference only. Internal diagnostics preserve the actual exception type, safe provider code/status/request ID and schema error locations/types without raw headers, credentials, response bodies, brief text or stack traces. Logs use static event codes/UUIDs. Do not enable SDK HTTP debug logs or credential-bearing browser traces.

Official API references consulted: [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), [Responses API](https://developers.openai.com/api/reference/python/resources/responses/methods/create). These establish the structured-output/refusal boundary, not this account's model access or successful execution.

## API and permission contract

All routes are project-scoped and authenticated. Every lookup first authorizes the project; guessed cross-workspace run/plan IDs return the same private 404 as absent resources. Every write has Origin/CSRF protection. No internal diagnostic detail endpoint is exposed.

| Route | Permission / behavior |
|---|---|
| POST /projects/{id}/pm-runs | Owner/Admin/Member; brief, optional instructions/context plan, client request UUID; real success 201, completed replay 200, existing active replay 202, conflicting payload/active run 409, safe generation error with run ID |
| GET /projects/{id}/pm-runs | All current members; bounded paginated summaries and nonsecret configuration; required `?client_request_id=UUID` lookup filters to the current initiator for uncertain generation outcome |
| GET /projects/{id}/pm-runs/{run_id} | All current members; actual status/metadata/result plan reference, no raw diagnostics |
| GET /projects/{id}/pm-plans | All current members; bounded history summaries |
| GET /projects/{id}/pm-plans/{plan_id} | All current members; one complete validated document and actual version/approval metadata |
| PUT /projects/{id}/pm-plans/{plan_id} | Owner/Admin/Member; validated full draft plus expected revision; stale/approved/superseded edits 409 |
| POST /projects/{id}/pm-plans/{plan_id}/approve | Owner/Admin only; exact version + revision; full integrity validation; stale/incomplete/older-than-current approval rejected |
| POST /projects/{id}/pm-plans/{plan_id}/draft | Proposed taste C05: Owner/Admin/Member creates a human draft copy of a historical version, without a model call; explicit source/version/revision, workspace lock and duplicate-copy protection |

Approval permission is a documented policy choice: Members author drafts, Owners/Admins approve. New generation leaves existing approved content untouched. Approving a newer draft atomically supersedes the prior approved version without modifying its document or approval evidence. Approved/superseded content is immutable. Retain prior versions for authorized read and comparison; a full diff viewer is deferred. Draft edits increment revision and record editor; stale clients must review/reload, with local unsaved text preserved. Approval never autosaves or silently approves a different revision.

Blocking confirmation items must receive a human resolution or explicit reasoned deferral before approval; ordinary nonblocking questions/risks may remain disclosed. The provider cannot set those human dispositions. Approval accepts an exact artifact with its stated uncertainty, not a claim that assumptions became verified business facts. Show the captured project-input snapshot and detect subsequent title/description changes; do not imply an old plan incorporates them. An explicit human-copy draft provides corrections without another paid model request (C05); inherited content keeps its real origin and is not labeled newly AI-generated. The server returns an existing matching editable copy for duplicate copy submissions under the same lock rather than creating accidental copies.

Persisted blocking confirmations retain immutable original key/text/source. A client cannot omit, rekey, rewrite or downgrade them to bypass disposition. Human resolution/defer requires an actual actor/time and nonempty reason bound to the exact item; retirement preserves it in the plan's decision disclosure and copies. To correct an original blocking question, explicitly resolve/defer it and add a replacement. Ordinary nonblocking text remains editable. The server retains disposed/retired items even if a full PUT omits them, rejects omission of unresolved blockers, and never trusts client actor/timestamp fields. This is narrow confirmation evidence, not a general per-edit event store. C02 covers this explicit approval policy.

Engineering clarification: duplicate copy client keys return the original copy even if subsequently approved/superseded; they do not create or promise a currently editable copy. A new explicit copy key creates a new version. Copied source revision/hash/evidence remains immutable independently of later source-draft edits. Criteria/requirements/confirmations use stable plan-scoped identities, not positions, for human provenance and error targeting. Plan reads validate assembled structure and report safe corruption errors rather than silently repairing invalid rows. Approving a draft older than an already approved version is rejected; a different unapproved newer draft does not alone prevent reviewing an older valid draft.

GET pm-plans accepts an own-creator `copy_request_id=UUID` filter for exact copy recovery. List responses use the same bounded pagination envelope and safe summaries as runs, without full documents. Full plan responses include canonical content hash and actual last editor/revision, so Save reconciliation can confirm only exact matching evidence. Approval actor/time remain present on superseded versions. Provider capability is configuration completeness only; it performs no billable connectivity probe.

## Frontend interaction contract

Keep the existing project overview and editor. Add a Product Plan section with brief textarea initialized from the project's description, optional instructions, optional explicit context selection, Generate Product Plan action, configuration guidance, run history/status, plan version selector, actual model/usage metadata and draft/approved display. The title/description snapshot is separate from the generation brief; changing the latter does not silently overwrite the project description.

Render actual overview, scope/requirements, epics/stories/criteria, uncertainty and source labels. Default readers see the current approved version; a newer draft is clearly available separately and a completed generation can open its own draft explicitly. Use progressive disclosure with native details/fieldsets; keep mobile readable in one column and preserve semantic light/dark tokens. Empty state contains no sample/generated content. Generation loading says one actual request is in progress; no fictional thinking steps or decorative percentages. A model charge requires the explicit Generate action; project creation offers that next step only. Replace stale Stage 02/no-AI copy with accurate Stage 03 planning wording without claiming provider connectivity from configuration alone.

Provide labeled native editing controls for important overview fields, scope, epic/story text, priorities, dependencies and criteria, including add/remove controls within bounds. Mark edited requirement text as human edit. Save explicitly persists to PostgreSQL. Show revision conflicts without discarding local changes. Owner/Admin approval identifies version/revision in its confirmation and persists the real actor/time. Viewer sees readable plans and an explicit read-only permission explanation.

The artifact header is the visual anchor: selected version, saved revision, draft/approved state, source freshness and the permitted next action. Add a Product Plan jump link near the project heading. Keep reading, generation, editing, execution evidence and history as distinct views/disclosures within this section. A native bounded version select avoids a growing tab strip. Draft editing is inline project-local mode (taste D01); text origin labels with inspectable excerpts are preferred to a persistent source rail (taste D02). Use compact epic/story summaries with stable keys, priorities, criterion/error/blocker counts and section jumps so the maximum supported document remains navigable.

Explicit editor states are clean saved revision, unsaved changes, saving, conflict, outcome unknown and approved. Approval is enabled only for a confirmed clean saved revision. Its confirmation freezes version/revision; an edit or remote conflict invalidates it. Resolve or explicitly defer blocking confirmations through linked fields with recorded reasons before approval. Ordinary version/route navigation offers Save, Discard or Keep editing; account/workspace/auth loss always clears protected content immediately. On 409 retain the local buffer and fetch the latest server revision separately, without overwriting it. Reference-aware removal shows affected dependencies and requires repair rather than silently cascading content deletion.

Every ambiguous write has operation-specific GET reconciliation: generation by client request UUID/run, save by exact document/revision, approval by exact version/revision/approval record, and human copy by its stable source/copy request identity. Preserve structured error category, field paths, run/diagnostic references and safe Retry-After through the proxy/client. A failed status GET stays unknown; never convert reconnecting into another paid POST. Refresh permissions after a denial and clear data if membership is lost. Do not retry a write automatically.

Bind every request/write/polling completion and its global error side effects to the session generation/account/workspace that initiated it. An obsolete original-session401 must not dispatch session-expired into a newly authenticated account. CSRF fetch errors, Save/Approve/Generate/Copy outcomes and status checks follow the same guard as protected reads; obsolete responses are ignored. Browser tests must delay a genuine old-session result across logout/login and confirm the new account remains valid, without intercepted fake API responses.

New PM reading text is scoped to a readable 16px base while preserving the existing font, themes and shell. Desktop may use a compact outline beside a readable document; tablet/mobile use one column, with version/state before content and 44px action targets. Labeled fieldsets and native disclosures expose the hierarchy. Validation summary links open ancestors and focus stable field IDs, with aria-invalid/descriptions. Define focus after add/remove, failed saves and confirmations; polite announcements report changed status only. Both-theme, keyboard, nested-error, conflict and maximum-size coverage must run at existing desktop/mobile/tablet sizes. Avoid sticky actions obscuring the mobile keyboard or focused controls.

On timeout/network interruption, do not automatically POST again. Retain the client request ID in component memory, offer Check Status via authorized GET, and show persisted active/recent runs after reload. Pending status is based on the real request/run state. Changing project/workspace/account clears protected component state through the existing AuthGate. Ignore obsolete read responses and never flash protected data before authorization succeeds.

Extend proxy to PUT. Keep ordinary API timeouts unchanged; PM POST alone has a bounded timeout longer than the configured total provider deadline plus finalization buffer, with a fixed maximum consistent with Settings. Client error messages distinguish an unknown generation outcome from an unknown project save. Same-origin cookies/CSRF remain the sole browser authentication path.

## Verification obligations and truth boundaries

Preserve the original 44 backend and 42 browser cases and their behavioral guarantees. Extend the guarded orba_test cleanup for new FK tables. Run backend and browser suites sequentially. Add a populated Stage 02 -> Stage 03 migration test preserving users/members/projects/IDs/timestamps and repeated upgrade, plus drift check. Never reset development data.

Deterministic unit/error tests may use narrowly scoped, explicitly named provider doubles. They prove validation, lifecycle, persistence, permissions and error handling; they do not prove Gemini generation works. Use the real official SDK transport for controlled connection/configuration failure. Never add an environment-selectable fake provider to production application code.

Backend coverage includes all 20 owner-required scenarios, explicitly enumerated and mapped in [CEO review section 6](reviews/STAGE03_CEO.md#exact-owner-required-backend-coverage), plus refusal/incomplete/empty output, evidence quotes, dependency cycles, exact revision conflicts, idempotency payload mismatch, concurrent duplicate start, session/permission loss during generation, late finalization, process/lease interruption, transaction rollback, no secret fields, cross-project UUID mismatch and retained old auth/CSRF tests. Relationship/usage/approval assertions query a separate actual PostgreSQL session. The final engineering test artifact must repeat the complete case mapping and distinguish real provider evidence from every double/fixture boundary.

Separate live command requires actual runtime configuration, calls the actual configured provider with a small habit-tracker brief, validates content/quality invariants without exact expected wording, persists a draft in isolated test data, retrieves it through API/DB and writes sanitized model/response/usage/count evidence. It exits nonzero with BLOCKED if configuration is unavailable; no skip/xfail converts this into success.

At least one separately identified desktop live browser flow must click Generate, receive the real plan, edit a criterion, reload, approve the exact version, reload and verify persistence, and prove an unrelated user's exact UUID access is denied. Additional mobile/tablet PM states run alongside existing Chromium regressions. Live tests are explicitly invoked, bounded and serialized; no hidden model calls in ordinary regression fixtures. API live and browser live each require actual generation rather than reusing a canned plan.

Negative A: actual missing/invalid provider configuration or closed-loopback SDK connection causes a recorded failed run, useful UI error and no fabricated plan; existing approved plan/project fields are compared unchanged. Negative B: an explicitly labeled malformed-provider double reaches real validation, records failed status/diagnostic and persists no plan. Separate explicit-only expected-failure experiment incorrectly asserts succeeded and must actually exit 1. It is outside normal discovery and never counted as a passing production test.

Extend scripts/verify.ps1 with PM/core regressions, live API/browser checks and negative-path commands. The default mandatory workflow must not return a complete green verdict when credentials/live checks are missing. Preserve real exit codes and record not-run/blocked work. Do not run live retries automatically; explicit verification is bounded by the configured output limit. Costs remain unknown unless actual authoritative pricing is separately supplied.

## Developer setup and verification contract

One documented root entry point: `pwsh -File scripts/verify.ps1 -Mode Full` (default) retains Stage01/02 checks and additionally requires live PM API/browser generation and negative paths. `-Mode Core` explicitly runs deterministic regressions only and prints live API/browser NOT RUN; its successful exit never establishes Stage03 VERIFIED. Live files/configurations are outside normal discovery rather than skipped or xfailed. Full should preserve core results before reporting missing live credentials nonzero BLOCKED. Keep the incorrect-success experiment separately invoked and preserve its actual exit1 without counting it among passing production tests. These interfaces are proposed until implemented and executed.

README's golden path uses repository-root PowerShell: locked installs/conditional env copies/migration; server-only API key/model configuration and two service terminals; sign in/create workspace/create project/explicit Generate/edit/save/Owner-or-Admin approve/reload. No key or working model default is provided. Restart the API after changing runtime config; configuration completeness is not connectivity evidence. Show the existing npm-exec pnpm fallback and actual tested versions separately from wider unverified runtime ranges. The existing verification script upgrades the configured development schema; disclose that additive mutation and backup/stop/restart order, never reset or downgrade it. Readiness checks the required PM database schema, separately from provider configuration.

Strengthen test-target validation before *any* cleanup/migration: loopback host, exact54330 port, orba_test DB and orba_test role. Test rejection for unsafe targets without touching them. Extend cleanup for all new FK tables and preserve sequential DB ownership. Provider secrets enter the child API environment only, never browser build variables, response examples, command arguments or captured logs. Preserve caller cancellation signals alongside transport deadlines, without claiming remote billing cancellation.

History defaults20/max50 use deterministic timestamp/UUID ordering and summary payloads. Active-run GET polling uses bounded2s-to10s backoff, stops on terminal/auth loss/unmount and never starts another POST. API docs show authenticated Origin/CSRF prerequisites, typed error categories, idempotency/revision semantics and operation-specific GET recovery. README links schema/lifecycle, configuration, troubleshooting and verification within two links. Safe errors include a documentation anchor; do not echo raw input values or internal traces. Record local runtime/usage/quality measurements, with warm<=5min as an unmeasured target after prerequisites/deps/model access are ready; cold provisioning and key acquisition remain separately unmeasured. No external telemetry, hosted sandbox, general CLI/SDK, public support or Model Hub is added.

Run-list/recovery response is an envelope with `items`, `limit`, `offset`, `next_offset` and safe provider capability. A UUID-filtered recovery GET returns at most the current user's matching run in the authorized project: active/terminal actual state or an empty list. Empty means no persisted run observed at that instant, not proof a delayed request cannot arrive; the UI retains uncertainty and the same client key. Saved-draft reconciliation confirms only an exact expected-next revision/content hash/actor match; later differing revisions remain ambiguous because this stage has no per-edit audit store. Approval reconciliation uses the immutable exact version/revision/approval metadata, including later supersession. Human-copy reconciliation uses its persistent client request identity. Missing configuration, preflight failure before the write was sent, server rejection and unknown write outcome have distinct safe states.

## Implementation sequence and live checklist

- [x] Inspect Stage 02 authorities, Git, scope and test infrastructure.
- [x] Create owner-authorized checkpoint e3fccd6; no secrets/artifacts staged.
- [x] Execute unchanged Stage 02 verification (44 backend, 42 browser; exit 0).
- [x] Complete sequential CEO, Design, DX, Eng reviews and identified independent voices; outputs below preserve their actual source/family.
- [x] Owner explicitly instructed continued execution after checkpoint/review; proceed within Stage03 using recommended routine choices. No claim of individual taste-choice votes.
- [x] Execute contract/storage/additive migration checks, including populated Stage01/02 preservation and drift.
- [x] Implement and exercise official SDK adapter, versioned prompt and safe diagnostics; unit synthetic HTTP is labeled separately from live calls.
- [x] Exercise run lifecycle, lease/idempotency, authorization and actual PostgreSQL concurrency checks.
- [x] Exercise persisted draft editing/approval/history and immutable approved versions.
- [x] Add and run Product Plan UI, scoped long requests and truthful failure/recovery states.
- [x] Execute102 backend/51 core browser regressions and fix causes without weakening assertions.
- [x] Execute genuine successful API generation and complete live browser generation/edit/approval/isolation; preserve earlier failed attempts.
- [x] Execute actual provider rejection/timeout, isolated malformed output and separate incorrect-success experiment (actual exit1).
- [ ] Obtain a green mandatory integrated Full run. Latest invocation exited1 on actual provider504; standalone browser0 is recorded separately. Required docs reflect PARTIAL.
- [x] Stop work at Stage03 and report the unresolved acceptance gate; no Stage04 implementation.

## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|---|---|---|---|---|---|
| D01 | Intake | Preserve exact Stage 02 checkpoint bytes | Mechanical | Explicit | Owner approved commit; existing whitespace is baseline evidence | Unrelated formatting rewrite before checkpoint |
| D02 | Intake | Separate live evidence from doubles | Mechanical | Completeness | A real configured model/browser run is mandatory | Claiming SDK/unit fixtures prove live generation |
| D03 | Intake | Keep provider model/key without defaults | Mechanical | Explicit | Account access is unknown and runtime credentials absent | Reusing Codex authentication or guessing a model |
| P-D04 | Primary | Responses.create then independent validation | Mechanical | P1/P5 | Retain actual envelope/usage even when output fails | Parse helper that loses metadata before capture |
| P-D05 / C05 | CEO integration | Human draft-copy correction and captured-input freshness | Taste | P2 | Correct immutable plans without another paid call | Require regeneration for every correction |
| P-D06 | Baseline | Preserve historical evidence and format-validate external backup | Mechanical | P1 | Separate new regression record from old Stage02 proof | Overwrite historical records or reset dev data |

The linked phase audits add30 CEO,14 Design,12 DX and21 primary Eng resolution rows. CEO C-D09 implements the already-counted C02 choice; repeated endorsements do not create additional unique taste choices. Seven unique taste choices are C01–C05 and D01–D02. Later CLI dispositions and twelve explicit TODO deferrals are audited separately below before the gate.

| ID | Phase | Deferred item | Classification / principle | Reason / rejected alternative |
|---|---|---|---|---|
|F01| Cross-phase | Durable queue/resumption | Mechanical P3 | Measure bounded-request need first; reject new orchestration now |
|F02| Cross-phase | Full edit audit/semantic diff | Mechanical P3 | Preserve approved versions now; defer generalized change history |
|F03| Cross-phase | Retention/deletion/export policy | Mechanical P3 | Needs owner privacy/audit policy; no invented cleanup guarantee |
|F04| Cross-phase | Broad quality evaluation dataset | Mechanical P3 | Required bounded live rubric stays mandatory; larger claims need real authorized briefs |
|F05| Cross-phase | Architect/coding/QA agents | Mechanical Explicit | Stage04+ needs separate request |
|F06| Cross-phase | Full multi-provider Model Hub | Mechanical Explicit | One official adapter now; later stage only |
|F07| Cross-phase | GitHub/Skills/external research | Mechanical Explicit | New credentials/effects/source authority outside Stage03 |
|F08| Cross-phase | Multiplayer/canvas/cloud | Mechanical Explicit | Preserve present project UI; no execution authority |
|F09| Cross-phase | Dollar pricing/currency budgets | Mechanical P3 | Actual usage only; no authoritative price/currency policy |
|F10| Cross-phase | Production identity/email/deployment | Mechanical Explicit | Local scope, no certification/public release |
|F11| Cross-phase | Hosted playground/general clients/community | Mechanical P3 | Root local path first; no remote/support claims |
|F12| Cross-phase | Broad OS/native-device certification | Mechanical P3 | Current Chromium desktop/mobile/tablet remains required; no broader evidence |

[TODOS.md](../TODOS.md) gives all twelve deferrals What/Why/Context/Pros/Cons/Effort/Priority/Dependencies. No mandatory Stage03 acceptance check was deferred.


## Owner continuation and provider amendment

The owner explicitly instructed continued execution and supplied a root .env. It contains GEMINI_API_KEY, not an OpenAI credential. A real key-authenticated read-only Gemini model-catalog request returned HTTP200; this is not generation evidence. The initial missing-model gate is preserved in evidence/stage03-before-model-*. The owner subsequently chose gemini-3.8-flash and requested quota-conscious use. Its actual model metadata returned HTTP200. Local configuration now selects that model, one active generation,6000 output tokens,three attempts/user/hour and six globally/hour; provider project/tier RPM/TPM/RPD remain unknown. No model was silently defaulted and the existing key was preserved exactly. Root env loading accepts GEMINI_API_KEY/ORBA_PM_API_KEY with server-only SecretStr; an API-specific .env may override root settings. No key was printed or copied into source.

The prior OpenAI adapter proposal is superseded by ONE maintained official google-genai adapter (installed2.31.0/uv.lock), not a second provider. Existing CEO/Design/DX/Eng artifacts retain their historical review assumptions. Current contracts require native JSON schema plus server validation, actual model_version/response_id/usage_metadata, fixed official endpoint, SDK attempts1, automatic_continuation=False and automatic function calling disabled. The installed SDK defaults continuation to true, so explicitly disabling it is necessary to prevent hidden paid follow-up calls. The owner's continuation authorizes execution; it does not constitute fabricated product approval or individual recorded votes on seven planning choices. Recommended choices remain the implementation defaults; Stage04 stays excluded.

Early scaffold evidence (historical): strict schemas and relational models written; additive migration ab3987da8961 parents actual0febbe526f54, upgraded successfully and Alembic drift check exited0. Existing development data is still0 users/0 projects/1 restricted workspace; populated preservation tests were outstanding at that point and now pass. Fresh external backup C:/Users/vaish/AppData/Local/Temp/orba-stage03-start.dump has SHA2561711B57745A4167405456E11909E2F4B1D1B4110CDA2EF4D331357C86956DB8C. Docker was initially unavailable, then started from its actual per-user install and Compose returned both databases healthy. No Stage03 successful run/live browser is claimed.

## Review outputs

Full review artifacts are linked here and form part of this plan. Their registries, diagrams and per-decision audit rows are retained rather than reduced to unsupported green summaries. CEO, Design, DX and Eng ran in that order. Eng's final eight CLI dispositions and the Gemini amendment are linked in its full review. Review completion is not product verification; current execution evidence is in VERIFICATION.md.

### CEO phase complete

[Full CEO review](reviews/STAGE03_CEO.md) contains actual source audit; premises/alternatives/dream diagram; all eleven review sections; thirty error/rescue/failure paths; twenty-four interaction edges; exact twenty-case mapping; fifteen tasks; and thirty decision rows. Its 8.8/10 self-assessment rates the review document, not product execution. [Independent CLI voice](reviews/STAGE03_CEO_CLI.md) exited 0 and supplied six ranked blind spots. Both voices are Codex-family/fresh-context; Claude and cross-model consensus are unavailable and not claimed.

| CEO dimension | Subagent | CLI | Consensus/disposition |
|---|---|---|---|
| Premises | Conditional: short briefs cannot confirm facts | Unvalidated: insufficient-input semantics | Shared concern: label unknown/proposed overview and keep human review |
| Right problem | Human-owned project agreement | Partially defined usefulness rubric | Different emphasis: add an explicit live fidelity/usefulness rubric; no business outcome claim |
| Scope calibration | Bounded one-agent workflow with concrete caps proposed | Delivery risk until caps/review burden explicit | Shared concern: adopt numeric contract, validate in Eng/live tests |
| Alternatives | Three persistence/execution approaches examined | Manual preparation substitute not addressed | Different emphasis: AI drafts reduce blank-page work; human copy/edit remains available; no superiority claim |
| Competitive risk | Wedge is trustworthy continuity; market unproven | Chat + manual document remains plausible | Shared concern: no invented demand/competitive advantage; evaluate actual live artifacts |
| Six-month trajectory | Versioned agreement coherent with stated debt | Input freshness and paid correction path unclear | Difference resolved in plan: snapshot-change notice and proposed human-copy draft C05 |

Three shared-concern dimensions and three differing emphases were identified; none is an application PASS. No pair of voices requested changing the owner's stage structure, so there is no User Challenge. CEO required corrections have been incorporated above: provenance on overview fields, server-owned edit attribution, original-session final checks, released DB connections, explicit admission/lease recovery, approval blockers, snapshot freshness, meaningful live rubric and a cost-free correction proposal. Runtime provider access remains unproven.

Numeric contract proposed by CEO for engineering validation: brief 1..10,000 characters, instructions <=4,000, explicitly selected context <=20,000, serialized input <=48,000; POST <=256 KiB and PUT <=512 KiB actual streamed bytes; document <=80,000 characters/512 KiB; max8 epics/40 total stories/160 criteria/40 functional and20 nonfunctional requirements; labels <=200, prose <=2,000, each Given/When/Then <=500. Every epic/story is nonempty; references are bounded/unique/acyclic. Total caps dominate individual maxima; no silent truncation. Provider T<=180s, provisional 10s pending lease and T+30s running lease. Eng must settle the complete DB/body/admission/serialization timeout inequality before implementation; ordinary request behavior remains unchanged.

Engineering replaces the provisional timing values: pending lease20s; running leaseT+45s, set in the durable transition before the call. Proposed operational budget is preflight/body/auth<=40s, reservation/start<=2x15s, provider<=180s plus<=5s client cleanup, bounded validation<=5s, finalization<=15s, one failure/commit-reconciliation phase<=15s, serialization<=5s: total<=295s under a300s application operation deadline; PM-only proxy330s and client350s, plus separate existing10s CSRF fetch. Ordinary proxy15s/client20s stays unchanged. Before provider invocation reduce its allowed time to fit the remaining operation budget or reject without a call. Check the operation/lease deadline again in the conditional final transaction; no timer alone authorizes a late write.

Additional bounded schema details: literal schema_version1; all remaining collections max20 unless specifically bounded above, target users/goals max10, story dependency/requirement-reference lists max10 each, stable local keys max64. Criterion keys are unique within the plan and stable through reorder. Aggregate caps dominate individual limits. The configured output-token budget does not promise a maximum-size document; truncated/incomplete output fails without salvage. Validators use bounded keyed maps/linear graph traversal. History queries return summaries; complete reads eagerly assemble relational children in a fixed query envelope verified on the maximum authored fixture.

Use existing psycopg connect_timeout3s and finite pool_timeout2s. PM transactions set local lock_timeout1s, statement_timeout2s and PostgreSQL18 transaction_timeout10s, with a15s phase allowance including connection/pool wait and checks. Do not impose PM transaction settings on Alembic or unrelated Stage02 transactions. Per-statement timeout alone is insufficient. Generation remains a worker-thread HTTP operation; these are local application/DB budgets, not hard real-time guarantees under OS stalls or a blackholed database transport. No abandoned shared Session or second async engine is introduced. Verify real local timing/pool responsiveness and preserve unknown outcome if a commit acknowledgement is lost. Reconciliation scans only expired active rows in bounded batches every5s, plus authorized project reads; it never resumes a request or interrupts an unexpired lease.

Final CLI corrections make the timing inequality cover both transport hops: Next and ASGI each impose5s absolute streamed request-body deadlines and actual byte caps before buffering. Next's330s timer starts on proxy entry, not after request.text(). Its extra upload5 + API operation300 + response consumption10 =315s, below330s proxy and350s browser, with the existing10s CSRF acquisition separate. Provider consumption, client closure and scoped asyncio.run teardown are included inside the API budget. Bound actual decoded provider-envelope bytes to1MiB before JSON decoding, including error responses, using the resolved official SDK's supported streaming/transport APIs. Current official SDK documentation uses HTTPX2; inspect the pinned SDK rather than assume an HTTPX1 wrapper is compatible.

Final authority/lease queries use fresh `clock_timestamp()` after acquiring all locks; PostgreSQL now() reflects transaction start and is insufficient after lock waiting. Assign an original executor UUID at reservation. Pending and running commits require confirmed ownership before provider dispatch. If either acknowledgement is uncertain, return unknown without dispatch/takeover and let the lease reconcile; replay never resumes execution. Preserve all terminal states even if failure-record commit is uncertain. Forced real-DB schedules cover both logout orders, expiry while waiting, both start acknowledgements and copy/source/version races.

Version canonical hashes explicitly as `orba-pm-canonical-json-v1` alongside document schema/prompt versions. Store algorithm+value; replay uses the stored algorithm and immutable explicit inputs, not whatever serializer a future release defaults to. Content hash excludes mutable approval envelope metadata. Explicit prior-plan context carries its exact version/revision/hash, stable node IDs, original origin/uncertainty and human dispositions. Selecting or approving an earlier AI assumption does not make it a confirmed user requirement on regeneration; transitive attribution is validated/displayed and retained through copies. Source quotes prove textual membership only.

Actual migration authority is Stage01 `0001` -> Stage02 `0febbe526f54`; the additive Stage03 revision parents `0febbe526f54`. Populated migration tests target that real identifier, not a nonexistent `0002`. All original records/values remain untouched. These corrections are specified and unexecuted until implementation.

Final-gate taste choices: C01 relational children/root JSONB (recommended); C02 human resolution/reasoned deferral of blocking confirmations; C03 best-effort continuation on disconnect with honest cancellation/billing limits; C04 finite cross-project admission defaults; C05 human draft-copy corrections without another model call. C05 is a small in-scope versioning extension raised by the CLI maintenance finding, not an Architect/orchestration feature.

Additional primary audit resolutions: P-D04 use Responses.create + independent validation to retain actual metadata on invalid content (mechanical, P1/P5); P-D05 identify approved-input freshness and human-copy source distinctly (C05 taste, P2); P-D06 preserve real Stage02 baseline outputs separately and validate the external PostgreSQL backup format (mechanical, P1). Backup: C:/Users/vaish/AppData/Local/Temp/orba-stage02-before-stage03.dump,18,006 bytes,SHA25609059AB2FD5554160A6935E648FCCFD5C26ADDE73F8F6326AD59C67E15C4E193; pg_restore --list exited0. It was not restored over development data.

### Design phase complete

[Full Design review](reviews/STAGE03_DESIGN.md) contains all seven passes, twelve-row state matrix, eight-step emotional journey, ASCII layout, responsive/keyboard contract, fourteen audit decisions and five tasks. Its9/10 assessment grades the amended specification, not product execution. [Independent design voice](reviews/STAGE03_DESIGN_VOICE.md) and [CLI voice](reviews/STAGE03_DESIGN_CLI.md), exit0, each raised six concerns; both are same-family Codex voices, not cross-model evidence. Their seven-dimension litmus/disposition table is retained in the full review.

Required fixes are integrated into the frontend contract: exact clean-revision approval, unsaved-navigation choices, local409 recovery, reference-aware deletion, operation-specific GET reconciliation, typed actionable errors, source freshness, artifact hierarchy, nested error focus and maximum-size desktop/mobile/tablet coverage. Taste D01 recommends inline project-local editing over a separate page; D02 recommends text origin/excerpt disclosure over a persistent source rail. No User Challenge was raised.

The missing optional design helper required an HTML fallback. External design artifact: C:/Users/vaish/.gstack/projects/OBRA/designs/pm-stage03-20261019/product-plan-wireframe.html, served locally at http://127.0.0.1:3010/product-plan-wireframe.html. Actual Playwright captures at1280x1000 and390x844 cover both themes and assert no horizontal overflow. They are labeled DESIGN SKETCH with placeholder content/disabled business actions, and do not verify any PM API, AI response or editing functionality.

### DX phase complete

[Full DX review](reviews/STAGE03_DX.md) contains eight scored passes, nine-stage journey, persona/empathy narrative, source trace, primary-source reference benchmark, TTHW target, checklist, twelve audit decisions and five tasks. Specification mean6.25->8.75/10 is not a measured product rating. TTHW is unmeasured;<=5min is a warm target after prerequisites/dependencies/model access. [Independent voice](reviews/STAGE03_DX_INDEPENDENT.md) and [CLI voice](reviews/STAGE03_DX_CLI.md), exit0, each raised six issues; six shared concerns and no substantive disagreements/User Challenges. Both are Codex-family reviews, not cross-model proof. Supplemental source-review exposure and the CLI's unsupported configured-credential assumption are disclosed/corrected in the full review.

Required amendments are above: Full/Core verification interfaces and discovery separation, exact test target before cleanup, safe typed error/recovery contract including required own-client-key lookup, explicit unknown states, actual config aliases and PM schema readiness, documented additive dev migration, golden setup/restart path and measured-versus-target timing. Existing C04/C05 choices stay at the gate. No PM implementation or live provider execution has occurred. Eng must now review the final amended contract, numerical timeout/admission bounds, persistence authority, race/error paths and complete test map.

## Aggregated implementation tasks

The following unchecked items retain the original review estimates and proposed file names as a historical planning ledger. They are not current execution results. Actual implementation paths, tests, completed checks and the outstanding Full/provider gate are recorded in the checklist above and docs/VERIFICATION.md; no claim that every speculative test/performance target below ran is made.

The installed jq aggregator selected the latest run per phase, scoped to main and the last five commits, and exact-deduped component/sorted files/title. Actual result:32 source tasks (CEO15, Design5, Eng7, DX5). Similar obligations intentionally remain separate and overlap; these are not32 independent workstreams. Filenames/efforts are implementation proposals until executed. All tasks remain unchecked.

- [ ] **CEO-T1 (P1, human: 4–6h / agent-assisted: 1–2h) — PM contracts** — Freeze the versioned PM document, edit, provenance, confirmation and integrity contracts.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T1
  - Files: `apps/api/orba/pm_schemas.py`, `apps/api/tests/test_pm_contracts.py`
- [ ] **CEO-T10 (P1, human: 2–4h / agent-assisted: 45–90m) — Test database safety** — Harden guarded test cleanup and prove populated Stage 02 preservation.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T10
  - Files: `apps/api/scripts/prepare_tests.py`, `apps/api/tests/test_pm_migrations.py`
- [ ] **CEO-T11 (P1, human: 5–8h / agent-assisted: 1.5–3h) — PM backend verification** — Implement the exact 20-case backend map plus meaningful concurrency, security and negative-path coverage.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T11
  - Files: `apps/api/tests/test_pm_runs.py`, `apps/api/tests/test_pm_plans.py`, `apps/api/tests/test_pm_permissions.py`, `apps/api/tests/test_pm_errors.py`
- [ ] **CEO-T12 (P1, human: 3–5h / agent-assisted: 1–2h) — Core browser regression** — Add deterministic real browser PM states and retain existing responsive/project/team journeys.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T12
  - Files: `apps/web/tests/product-plans.spec.ts`, `apps/web/playwright.config.ts`
- [ ] **CEO-T13 (P1, human: 2–4h / agent-assisted: 45–90m plus live waits) — Live API evidence** — Provide and execute a separate real model API verification command.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T13
  - Files: `apps/api/scripts/verify_pm_live.py`
- [ ] **CEO-T14 (P1, human: 3–5h / agent-assisted: 1–2h plus live waits) — Live browser evidence** — Provide and execute a separately identified live-model browser journey.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T14
  - Files: `apps/web/playwright.live.config.ts`, `apps/web/tests-live/product-plan-live.spec.ts`
- [ ] **CEO-T15 (P1, human: 3–5h / agent-assisted: 1–2h) — Lifecycle and delivery evidence** — Complete lifecycle operations, integrated verification, truthful docs and the explicit wrong-success experiment.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T15
  - Files: `apps/api/orba/main.py`, `scripts/verify.ps1`, `apps/api/tests/experiments/pm_wrong_success_experiment.py`, `docs/VERIFICATION.md`
- [ ] **CEO-T2 (P1, human: 4–6h / agent-assisted: 1–2h) — PM persistence** — Add authoritative relational PM storage and a forward-only additive migration.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T2
  - Files: `apps/api/orba/models.py`, `apps/api/migrations/versions/0003_product_manager.py`
- [ ] **CEO-T3 (P1, human: 3–5h / agent-assisted: 1–2h) — PM provider** — Implement the sole official SDK adapter and safe capability configuration.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T3
  - Files: `apps/api/orba/pm_provider.py`, `apps/api/orba/config.py`, `apps/api/orba/prompts/product_manager_v1.txt`, `apps/api/uv.lock`
- [ ] **CEO-T4 (P1, human: 2–3h / agent-assisted: 30–60m) — PM authorization** — Extract the private project authorizer and add thin authenticated PM read/write routes.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T4
  - Files: `apps/api/orba/security.py`, `apps/api/orba/main.py`, `apps/api/orba/pm.py`
- [ ] **CEO-T5 (P1, human: 6–9h / agent-assisted: 2–3h) — PM lifecycle** — Implement bounded run reservation, admission, idempotency, provider phases and fenced finalization.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T5
  - Files: `apps/api/orba/pm_service.py`, `apps/api/orba/db.py`
- [ ] **CEO-T6 (P1, human: 4–6h / agent-assisted: 1–2h) — Plan mutation** — Implement full-draft CAS, server-derived human provenance, immutable approval and version history.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T6
  - Files: `apps/api/orba/pm_service.py`, `apps/api/orba/pm_schemas.py`
- [ ] **CEO-T7 (P1, human: 2–4h / agent-assisted: 45–90m) — API transport** — Extend same-origin transport with PUT, typed safe PM errors and bounded PM-only time/body options.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T7
  - Files: `apps/web/src/lib/api.ts`, `apps/web/src/app/api/v1/[...path]/route.ts`
- [ ] **CEO-T8 (P1, human: 4–6h / agent-assisted: 1–2h) — Plan reader** — Build the Product Plan reader/generation/history/recovery feature inside project detail.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T8
  - Files: `apps/web/src/components/product-plan.tsx`, `apps/web/src/app/projects/[id]/page.tsx`
- [ ] **CEO-T9 (P1, human: 5–8h / agent-assisted: 1.5–3h) — Plan editor** — Build the bounded native plan editor and exact approval interaction.
  - Source: ceo-review — docs/reviews/STAGE03_CEO.md implementation tasks T9
  - Files: `apps/web/src/components/product-plan-editor.tsx`, `apps/web/src/app/globals.css`
- [ ] **DS-T1 (P1, human: 0.5d / agent-assisted: 30–60m) — Plan reader** — Implement canonical reading order/version/source context; passes1/3
  - Source: design-review — docs/reviews/STAGE03_DESIGN.md implementation tasks DS-T1
  - Files: `apps/web/src/components/product-plan.tsx`, `apps/web/src/app/projects/[id]/page.tsx`
- [ ] **DS-T2 (P1, human: 1–2d / agent-assisted: 1–2h) — Plan editor** — Labeled nested editor, dirty tracking, safe structural edits; passes2/6
  - Source: design-review — docs/reviews/STAGE03_DESIGN.md implementation tasks DS-T2
  - Files: `apps/web/src/components/product-plan-editor.tsx`, `apps/web/src/app/globals.css`
- [ ] **DS-T3 (P1, human: 0.5–1d / agent-assisted: 30–60m) — API recovery** — Typed errors, unknown outcome, GET recovery, preserved approved content; pass2
  - Source: design-review — docs/reviews/STAGE03_DESIGN.md implementation tasks DS-T3
  - Files: `apps/web/src/lib/api.ts`, `apps/web/src/app/api/v1/[...path]/route.ts`, `apps/web/src/components/product-plan.tsx`
- [ ] **DS-T4 (P1, human: 0.5–1d / agent-assisted: 30–60m) — Approval and source evidence** — Exact saved revision/blockers/human-copy/freshness; passes3/7
  - Source: design-review — docs/reviews/STAGE03_DESIGN.md implementation tasks DS-T4
  - Files: `apps/api/orba/pm_service.py`, `apps/web/src/components/product-plan.tsx`
- [ ] **DS-T5 (P1, human: 1d / agent-assisted: 45–90m) — PM responsive accessibility** — Both themes, max-size/mobile/tablet/keyboard/error focus; passes4–6
  - Source: design-review — docs/reviews/STAGE03_DESIGN.md implementation tasks DS-T5
  - Files: `apps/web/src/app/globals.css`, `apps/web/tests/product-plans.spec.ts`
- [ ] **EN-T1 (P1, human: 1–2d / agent-assisted: 1–2h) — PM publication lifecycle** — Implement scalar-session release, logout-linearized publication and terminal fences; E-A01/02/05
  - Source: eng-review — docs/reviews/STAGE03_ENG.md implementation tasks EN-T1
  - Files: `apps/api/orba/pm_service.py`, `apps/api/orba/security.py`, `apps/api/orba/db.py`
- [ ] **EN-T2 (P1, human: 1–2d / agent-assisted: 1–2h) — PM ownership and identities** — Stable all-node identity, same-project constraints, dual input/snapshot hash and durable copy identity; E-A03/04/06
  - Source: eng-review — docs/reviews/STAGE03_ENG.md implementation tasks EN-T2
  - Files: `apps/api/orba/pm_schemas.py`, `apps/api/orba/models.py`, `apps/api/migrations/versions/0003_product_manager.py`
- [ ] **EN-T3 (P1, human: 1d / agent-assisted: 45–90m) — PM deadline boundary** — Enforce scoped SDK and complete phase/body/transport budgets; E-A07/E-P03
  - Source: eng-review — docs/reviews/STAGE03_ENG.md implementation tasks EN-T3
  - Files: `apps/api/orba/pm_provider.py`, `apps/api/orba/pm.py`, `apps/web/src/lib/api.ts`, `apps/web/src/app/api/v1/[...path]/route.ts`
- [ ] **EN-T4 (P1, human: 1d / agent-assisted: 45–90m) — Shared PM authority** — Share validators/authorizer/error shape and small reader/editor modules; E-Q01..04
  - Source: eng-review — docs/reviews/STAGE03_ENG.md implementation tasks EN-T4
  - Files: `apps/api/orba/pm_schemas.py`, `apps/api/orba/pm_service.py`, `apps/web/src/components/product-plan.tsx`, `apps/web/src/components/product-plan-editor.tsx`
- [ ] **EN-T5 (P1, human: 2–3d / agent-assisted: 2–4h plus live) — Complete PM verification** — Execute all32 coverage groups/all20 owner guarantees with honest fixtures/live boundaries; E-T01..05
  - Source: eng-review — docs/reviews/STAGE03_ENG.md implementation tasks EN-T5
  - Files: `apps/api/tests/test_pm_runs.py`, `apps/api/tests/test_pm_plans.py`, `apps/web/tests/product-plans.spec.ts`, `apps/web/tests-live/product-plan-live.spec.ts`
- [ ] **EN-T6 (P1, human: 1d / agent-assisted: 45–90m) — Test and migration safety** — Strict test target, populated preservation and Full/Core/expected-failure evidence; E-A08/E-T05
  - Source: eng-review — docs/reviews/STAGE03_ENG.md implementation tasks EN-T6
  - Files: `apps/api/scripts/prepare_tests.py`, `apps/api/tests/test_pm_migrations.py`, `scripts/verify.ps1`, `docs/VERIFICATION.md`
- [ ] **EN-T7 (P1, human: 0.5–1d / agent-assisted: 30–60m) — PM bounded data access** — Bound queries, graph cost, history and expired-run sweep; E-P01/02/04
  - Source: eng-review — docs/reviews/STAGE03_ENG.md implementation tasks EN-T7
  - Files: `apps/api/orba/pm_service.py`, `apps/api/orba/models.py`, `apps/api/tests/test_pm_plans.py`
- [ ] **DX-T1 (P1, human: 0.5d / agent-assisted: 30–60m) — Runtime onboarding** — Real-model golden path and troubleshooting; passes1/4
  - Source: devex-review — docs/reviews/STAGE03_DX.md implementation tasks DX-T1
  - Files: `README.md`, `apps/api/.env.example`, `apps/web/.env.example`
- [ ] **DX-T2 (P1, human: 0.5–1d / agent-assisted: 45–90m) — Safe API recovery** — Stable PM codes, fields, references and GET recovery; passes2/3
  - Source: devex-review — docs/reviews/STAGE03_DX.md implementation tasks DX-T2
  - Files: `apps/api/orba/pm.py`, `apps/web/src/lib/api.ts`, `apps/web/src/app/api/v1/[...path]/route.ts`
- [ ] **DX-T3 (P1, human: 0.5–1d / agent-assisted: 45–90m) — Verification entry point** — Strict test targets and Full/Core/live workflow; pass6
  - Source: devex-review — docs/reviews/STAGE03_DX.md implementation tasks DX-T3
  - Files: `apps/api/scripts/prepare_tests.py`, `scripts/verify.ps1`, `apps/web/playwright.live.config.ts`
- [ ] **DX-T4 (P1, human: 0.5d / agent-assisted: 30–60m) — Operator and contributor docs** — Migration guide, evidence boundaries and local contributor path; passes4/5/7
  - Source: devex-review — docs/reviews/STAGE03_DX.md implementation tasks DX-T4
  - Files: `README.md`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/VERIFICATION.md`
- [ ] **DX-T5 (P1, human: 0.5d / agent-assisted: 30–60m) — Live quality measurements** — Actual timing/usage/quality and honest blockers; pass8
  - Source: devex-review — docs/reviews/STAGE03_DX.md implementation tasks DX-T5
  - Files: `apps/api/scripts/verify_pm_live.py`, `apps/web/tests-live/product-plan-live.spec.ts`, `docs/VERIFICATION.md`
