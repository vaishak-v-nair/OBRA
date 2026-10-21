# Stage 03 CEO review: one real Product Manager planning agent

Date: 2026-10-18. Reviewer: fresh-context Codex-family subagent. Mode: **SELECTIVE EXPANSION**. Status: **DONE_WITH_CONCERNS for this review; Stage 03 remains proposed and unverified.**

This review applies the explicitly invoked autoplan CEO methodology to `docs/STAGE03_PLAN.md`. The owner's Stage 03 request is the stage authority; Stage 04 remains excluded. Only this review file was written. No product code, main plan, credentials, database, global memory, or external messages were changed. The parent owns the subsequent CLI voice and the remaining sequential phases. This is one Codex-family review, not a Claude review, a live model test, or cross-model consensus.

Autoplan's six principles govern intermediate decisions: P1 completeness, P2 work within the blast radius, P3 pragmatic choice, P4 reuse, P5 explicit design, P6 action. Its duplicated-boilerplate skip list applies. The review-specific audit, Step 0A–0F, all eleven deep sections, registries, task synthesis, and quality assessment are included. The one-file assignment overrides helper JSONL, TODOS, global CEO-plan/log, promotion, and main-plan writes; their substantive contents are retained here for the parent's aggregation. No additional delegation or CLI review was run.

## Executive judgment

Proceed with the proposed bounded PM workflow after incorporating the decisions below. Its useful product outcome is an authorized teammate turning an idea into a reviewable, editable, explicitly approved project agreement that survives reload. The competitive wedge is trustworthy continuity between the supplied brief, a real model execution, human corrections, and the approved version. The number of generated sections or agent-like animations is not evidence of product value.

The strongest parts already exist: FastAPI authentication, private project lookup, workspace locking, PostgreSQL/Alembic authority, protected browser state, and real regression infrastructure. The plan should extend those seams. A generic agent platform, a new job system, or another auth authority would add risk without completing this stage.

The material concerns are: **live execution is blocked until actual ORBA runtime configuration works; provenance must be assigned by server authority at field level; the long-request/lease/transaction lifecycle needs exact limits; generation needs an admission budget across projects; approval must resolve explicit confirmation items; and live tests must remain distinguishable from the owner-authorized malformed-output double.** These are proposed requirements, not verified fixes.

## System audit: current code and evidence

The inspected authorities are root/web `AGENTS.md`, README, architecture/roadmap/verification/test documents, the proposed Stage 03 plan, current API models/schemas/config/database/auth/authorization/routes/migrations, guarded test preparation, backend test code, the browser API/proxy/session/project components, CSS, Playwright configuration, and browser suites.

| Observation | Concrete source | Consequence for Stage 03 |
|---|---|---|
| The only commit is `e3fccd6 chore: checkpoint Stage 02 baseline`; `git diff main --stat` and stash list are empty; no remote is configured. Stage 03 plan/evidence are untracked. | Actual `git log`, diff, stash, status, remote reads | Use file inspection plus the checkpoint. Empty tracked diff does not mean no work exists. No remote PR/CI result is claimed. |
| A recent-file ranking assigns one touch to every checkpointed source file. No source TODO/FIXME/HACK/XXX was found; hits were historical review prose. No TODOS, CLAUDE, DESIGN, or repo design document was found. | Read-only `rg`, Git history, file inventory | There is no useful hotspot history or inherited prompt-eval convention to assume. The roadmap remains the deferral authority. |
| The parent's fresh baseline is recorded as exit 0, 44 backend cases in 25.79s and 42 Chromium browser cases in 1.8m. The transcript tail independently contains `42 passed (1.8m)` and exit 0. | `docs/evidence/stage03-baseline.txt`; parent's execution report | This is Stage 02 regression evidence, not Stage 03/model evidence. This reviewer did not rerun tests. |
| The parent reports a local logical backup and zero users, one restricted workspace, zero development projects. | Parent's observed backup/count report, not independently re-executed here | Do not claim populated development-data preservation. Require a populated Stage 02 migration fixture in the guarded test DB. |
| Authentication is a request dependency using the shared SQLAlchemy Session. Workspace writes serialize through `membership(..., lock=True)`. | `security.py:68,84,102,118`; `db.py:21`; `main.py:157` | Reuse identity/CSRF/role checks. A long SDK await must not retain the authentication dependency's checked-out transaction/session. |
| `get_project` is nested inside `create_app`; it authorizes by membership join and excludes legacy workspaces. | `main.py:137` | Extract one helper with identical private 404 behavior. Do not duplicate a subtly different PM project authorizer. |
| Existing client/proxy timeouts are 20s/15s; CSRF acquisition adds up to 10s. PUT is not exported. | `web/src/lib/api.ts:15,20`; proxy `route.ts:15,24` | The proposed 60s–180s model call cannot work through unchanged transport. Scope timeout changes precisely and preserve ordinary requests. |
| `ApiError` preserves only status; generic POST failure tells users to check Projects for an uncertain save. | `web/src/lib/api.ts:9,22–30` | PM status/run/error codes need typed fields and PM-specific recovery text. Do not parse message strings or automatically POST again. |
| `AuthGate` keys state by account/workspace/path; session reads have generation guards. | `components/session.tsx:19–75` | Reuse clearing and stale-read patterns. PM callbacks need their own generation/plan/revision guards inside that boundary. |
| Project detail has a real overview/editor plus a future placeholder; ProjectForm says AI collaboration comes later. | project detail `page.tsx:17`; `project-form.tsx`; `shell.tsx` | Replace only the PM-specific placeholder/copy. Keep later agents and tools visibly unavailable. |
| Readiness references Stage 02 tables explicitly. Lifespan currently only disposes the engine. | `main.py:30,95` | Add PM schema readiness and owned SDK/reconciler cleanup while keeping liveness DB-independent and missing PM credentials separate from core readiness. |
| Test preparation truncates an explicit table set and validates DB/role, but does not enforce host/port. Existing migration tests create isolated schemas in that real DB. | `scripts/prepare_tests.py`; `tests/test_legacy.py:30`; `migrations/env.py` | Extend FK cleanup and strengthen the exact loopback test-target guard before adding more cleanup. Keep backend and browser runs sequential. |

Read-only audit command note: an initial inventory included a nonexistent root `tests` path; `rg` returned exit 1 with that path error. The corrected inventory used `apps/api/tests` and `apps/web/tests`. No application failure was inferred from the inventory error. No hidden helper success is claimed: the supplied intake already records absent autoplan helper binaries, and this review did not install or repair global tooling.

Taste references: `security.membership` is explicit about lock-before-role authority; `AuthGate` makes protected-state clearing visible; `prepare_tests` makes destructive-test intent explicit. Preserve those patterns. Avoid repeating the compressed, one-line JSX in the current detail/editor or the transport helper's operation-agnostic catch: a nested editor and asynchronous lifecycle need readable boundaries and specific recovery states.

### Landscape synthesis

**Layer 1 — established approach:** a brief becomes a specification, humans clarify missing decisions, then a stable agreement drives later work. **Layer 2 — current primary sources:** GitHub Spec Kit documents separate specification, clarification, planning, and consistency analysis; Atlassian markets Rovo across existing organizational knowledge and agents. A generic “AI writes a PRD” capability therefore offers little defensible distinction. [Spec Kit lifecycle](https://github.github.com/spec-kit/reference/agentic-sdd.html), [Rovo](https://www.atlassian.com/software/rovo).

**Layer 3 — inference:** ORBA should win this stage by making the agreement reliable inside its existing workspace model: source-bound statements, visible uncertainty, real execution metadata, human edits, exact approval, and durable retrieval. This review does not establish market demand, willingness to pay, or a competitive performance advantage. Those remain hypotheses; no analytics/customer research program is added to Stage 03.

## Step 0A — premise challenge

| Premise | Assessment | Decision and cost if wrong |
|---|---|---|
| A single PM planning agent is the right next stage. | Owner-directed and coherent with the current project-description workflow. | Accept. It produces a durable agreement before any later automation; no other agent role is needed. |
| The user wants a better product decision, rather than merely more generated text. | Reasonable but not empirically demonstrated. | Define acceptance around traceability, editability, unknowns, approval, and reload; document volume is not a success metric. **CEO-01.** |
| A model can reliably fill every field of a wide schema from a short brief. | Only structurally plausible; semantic completeness and configured model access are unproven. | Require honest unknowns and a compact live brief. Reject invented dates, audiences, success thresholds, and business claims. Prove provider/schema compatibility first. **CEO-02/03.** |
| An exact source quote establishes faithful provenance. | It proves quotation membership, not that the claimed requirement follows from it. | Validate quote/source binding mechanically and retain human semantic review. The UI must not call source-bound statements independently verified facts. **CEO-04.** |
| Approval can be meaningful while confirmation items remain unresolved. | Ambiguous in the plan; this can turn missing decisions into accidental commitments. | Proposed policy: every blocking confirmation must be resolved or explicitly deferred by a human with a reason before approval. General questions/risks can remain visible. **CEO-05, taste at final gate.** |
| Membership recheck alone defines long-running authorization. | Incomplete for revoked/expired sessions and disabled users. | Recheck original session/user plus membership before final publication; a model charge may already have happened. **CEO-06.** |
| A bounded synchronous request is enough for local scope. | Reasonable with hard timeouts, leases, no held DB connection, and truthful interruption recovery. | Keep this approach; no durable/resumable-worker promise. Specify disconnect semantics instead of hoping proxy cancellation is reliable. **CEO-07/08.** |
| Per-project uniqueness controls cost. | False across many projects/accounts. | Add PostgreSQL-based global/actor admission bounds without new infrastructure. This limits exposure; it is not a currency budget. **CEO-10.** |

Doing nothing preserves a dependable Stage 02 notebook with permissions. It fails the authorized next outcome: there is no real planning execution, structured agreement, or approval record. The reframing is “turn an idea into a human-owned project agreement,” with one model as an input. It avoids treating “agent installed” or “long JSON generated” as the product.

No finding in this single voice is called a two-model User Challenge. The questionable premises above travel to the parent's final gate as explicit concerns/taste decisions where applicable; this review does not pause the pipeline or override the owner's one-agent structure.

## Step 0B — what already exists

| Sub-problem | Existing leverage | Exact reuse boundary |
|---|---|---|
| Account, session, CSRF, exact Origin | `auth.py`, `security.py` | Real dependencies and opaque sessions; no PM-specific login or token authority. |
| Tenant/role checks and serialization | `membership`, `require_role`, workspace routes | All PM content writes and expiration transitions lock workspace before current-role decisions. Internal reconciler transitions are system maintenance, not Viewer write authority. |
| Private resource lookup | `main.get_project` | Shared helper authorizes project first; then constrain every run/plan/context lookup to that project. |
| Project creation, description, editing | `ProjectForm`, `ProjectEditor`, `Project` | Generation is an explicit later action. Snapshot title/description; never overwrite them from a generated plan. |
| Settings/database/session lifecycle | `config.py`, `db.py`, app lifespan | Optional PM configuration, short transaction phases, closed SDK client, sanitized DB errors. |
| Durable schema and preservation tests | Alembic, `test_legacy.py`, provided connection support | Additive new tables/indexes; populated upgrade and repeated-upgrade checks. |
| Protected UI and themes | SessionProvider/AuthGate, Button, semantic CSS | One embedded Product Plan feature with native controls; no new global state framework or theme system. |
| Same-origin transport | proxy route and `request<T>` | Add PUT, safe error metadata, bounded PM request options, no duplicated cookie/auth implementation. |
| Integration/browser proof | test fixtures, real PostgreSQL, Playwright/verify script | Reuse registration/workspace setup and sequential isolation; preserve original assertions. |

## Step 0C — dream state and delta

```text
CURRENT                         THIS STAGE                         12-MONTH IDEAL (not authorized)
Authenticated project           One PM execution                  Evidence-aware project decisions
description + roles      --->   -> attributed editable draft ---> -> approved artifacts drive later work
No PM execution                 -> human exact approval           -> explicit change-impact review
No plan agreement               -> persisted version history      -> measured quality across real projects
                                No downstream execution          -> auditable, governed integrations
```

The stage earns one trusted handoff artifact. It deliberately stops before implementing, researching, syncing, or orchestrating anything from that artifact. Future consumers can read a versioned contract without gaining authority to execute it. This is a trajectory diagram, not permission to begin Stage 04.

## Step 0C-bis — alternatives

| Approach | Completeness / effort | Risk | Pros | Cons / existing reuse |
|---|---|---|---|---|
| **A. Minimal document storage:** one run table and one validated JSONB plan tree, same synchronous provider flow and revision/approval rules | 9/10; human 4–6d / assisted 1.5–3d | Medium | Few schema seams; atomic document validation/save; satisfies the user-visible workflow | Nested relational relationship verification and future child lookups less direct; still needs all run/error/auth work. Reuses existing auth/proxy/Alembic. |
| **B. Focused relational plan, proposed:** root non-epic JSONB plus epic/story/criteria rows; one provider adapter, router/service, persisted lease | **10/10; human 6–9d / assisted 2–4d**, excluding account setup/live waits | Medium–high | Explicit child integrity, bounded loading, exact version approval, preservation of owner-required relationships | Larger migration/editor/serializer surface; must avoid a duplicate JSON tree. Reuses the same existing seams. |
| **C. Durable worker/orchestration platform:** queue, resumable jobs, provider plugins, event stream | 10/10 for this outcome; human 12–18d / assisted 5–8d | High | Survives disconnected callers; useful for a future multi-stage workload | Adds infra and distributed lifecycle without an authorized need; expands operational burden and Stage 04 temptation. Reuses little additional existing code. |

**Auto-decision: B**, because it is the most complete direct fit to the owner's explicit relationship/persistence requirements; C ties on current outcome but loses P5 simplicity and introduces out-of-scope infrastructure. A remains viable and close enough to record **TASTE C01**: relational children cost additional code but improve inspectable relationships. Estimates are planning ranges, not measured completion promises; real model latency, account setup, Windows process issues, and review cannot be compressed into those coding estimates.

## Step 0D — complexity, scope, and delight

The plan will touch well over eight files and more than two conceptual components. That is a real complexity smell, not automatically a reason to delete security/lifecycle work. Keep the minimum set: one provider adapter, one run/plan service, one thin router, one typed contract, additive models/migration, one feature UI with a bounded editor, and existing transport/test seams. Do not introduce a generic event bus, repository layer, schema registry service, provider factory framework, custom form library, or independent auth client. **CEO-21.**

The 10x vision is that a teammate can answer “what did we agree, who changed it, and which decision is still open?” in seconds. The in-stage increment is visible source labels and confirmation handling, not autonomous discovery. Platform potential lies in a stable, approved version ID and schema version; building its future consumers is deferred.

Each cherry-pick was evaluated separately using autoplan P2; none is an implicit owner approval of a later stage.

| # | Felt outcome and concrete proposal | Effort / risk | Decision |
|---|---|---|---|
| X1 | A teammate immediately sees the current approved agreement even when a newer draft exists: separate approved/draft labels and deliberate version selection. | Human 1h / assisted 15–30m; low; existing feature files | **Accept**, in blast radius. Prevents a draft from appearing to supersede approval. |
| X2 | After an interrupted request, one Check Status action recovers the actual run rather than charging again: display run reference and reuse the client key only for GET reconciliation. | Human 1–2h / assisted 30m; low | **Accept as completion of existing scope**, not a second history/retry mechanism. |
| X3 | Before approving, see precisely which confirmations remain: count open items and focus the first unresolved one. | Human 2–3h / assisted 45–60m; medium; 3–5 files | **Accept; TASTE C02**, with the explicit human-disposition policy in CEO-05. |
| X4 | A long draft feels navigable: native contents links, expandable epic groups, an explicit unsaved marker, and a saved revision status. | Human 1–2h / assisted 30m; low | **Accept**, within the PM UI; no new package or permanent sidebar. |
| X5 | Source information is understandable on demand: show the actual source quote and snapshot label beside an important statement. | Human 1–2h / assisted 30–45m; medium | **Accept**, already-required provenance made inspectable; no confidence percentages. |
| X6 | Show a full side-by-side semantic diff across plan versions. | Human 2d / assisted 0.5–1d; medium | **Defer**. Existing version retrieval is enough for this stage; semantics/identity need later design. |
| X7 | Push run completion through SSE/WebSockets and resume after process loss. | Human 3–5d / assisted 1–2d; high | **Defer**. Crosses infrastructure scope; bounded GET reconciliation is adequate locally. |
| X8 | Render token cost estimates/pricing or progress percentages. | Human 1d / assisted 2h; medium | **Reject**. No authoritative pricing or progress signal exists; actual usage may be null. |

## Step 0E — temporal interrogation

| Implementation point | Decision needed now | Resolved direction |
|---|---|---|
| Hour 1, foundations (assisted roughly 15–30m after setup) | What is a valid plan; how large; how do schema/version/source IDs work? | Freeze the bounded output/input contract and source provenance rules first; prove its exported schema against the actual configured model before extensive UI work. |
| Hours 2–3, core logic (assisted roughly 30–90m) | Which transaction owns the run; what if DB/SDK/timeouts or duplicate requests race? | Short independent transactions, immutable request hash, workspace lock plus admission serialization, hard deadline, terminal-state CAS, no automatic model retry. |
| Hours 4–5, integration (assisted roughly 45–120m) | What happens on proxy abort, logout, permission loss, stale PUT, and approval of an old revision? | Bounded best-effort completion after browser disconnect; actual task cancellation interrupts; final auth recheck; optimistic CAS; explicit approval policy. |
| Hour 6+, polish/tests (assisted 1–3h plus unavoidable live execution) | Can a huge nested plan be edited on mobile; what evidence makes it real? | Native progressive disclosure, source/revision labels, a maximum-size render check, exact 20-case map, separately invoked real API and browser generation, explicit negative/expected-failure evidence. |

These are interrogation landmarks, not a six-hour delivery estimate; the complete scope includes multiple days of human-equivalent implementation and verification. Missing runtime credentials cannot be replaced by faster coding.

## Step 0F — mode confirmation and incremental decisions

**SELECTIVE EXPANSION + approach B confirmed by autoplan rule.** The authorized scope remains one real PM planning agent. Expansions X1–X5 fit its existing files/direct importers and are correctness/usability completion; X3 and the persistence choice are surfaced as taste. No mode drift toward a platform or Stage 04 is approved.

| Decision | Classification | Principle | Choice / rejected alternative |
|---|---|---|---|
| C-D01 | Mechanical | P4 | Reuse current auth, CSRF, workspace locks and private project authorization; reject parallel authority. |
| C-D02 | Mechanical | P1/P6 | Keep actual runtime/model verification mandatory; absent credentials remain BLOCKED for live scope. |
| C-D03 / C01 | Taste | P1/P5 | Prefer relational children with root-only JSONB; retain whole-document JSONB as a viable alternative for final gate. |
| C-D04 | Mechanical | P5 | Keep bounded synchronous SDK execution; reject queue/orchestration infrastructure. |
| C-D05 | Mechanical | P1 | Define exact input/output/time/admission bounds before implementation; reject “bounded” without numbers. |
| C-D06 | Mechanical | P1/P4 | Make source identity and human provenance server-owned; reject client/provider claims of approval or human editing. |
| C-D07 / C02 | Taste | P1 | Require human disposition of blocking confirmations before approval; reject silent acceptance of open blockers. |
| C-D08 | Mechanical | P2 | Accept X1 approved/draft visibility, X2 recovery, X4 navigation, X5 inspectable sources. |
| C-D09 | Mechanical under C02 | P2 | Implement X3 confirmation navigation within the existing C02 policy choice; not a second independent taste decision. |
| C-D10 | Mechanical | P3/P5 | Defer X6 diff and X7 push/resumability; reject X8 invented pricing/progress. |

## 1. Architecture review

**Five material architecture findings: CEO-03, CEO-07, CEO-08, CEO-10, CEO-11.** The dependency direction is right: browser feature → same-origin proxy → FastAPI PM router → service/contract/provider → PostgreSQL/OpenAI. Keep generated text on the data side of that boundary; it must never select a model, change permissions, execute tools, or choose an application URL. The architecture becomes legible by giving the service explicit start, provider-call, finalization, save, approval, and reconciliation phases rather than one large branching route.

```text
BEFORE
  ProjectForm / project detail -> request<T> -> Next proxy -> FastAPI project routes
                                                           -> security + Session -> PostgreSQL

AFTER (new nodes marked *)
  AuthGate -> project detail -> ProductPlan* -> bounded native PlanEditor*
                                  |                     |
                           typed PM client* ------------+
                                  |
                    existing request/proxy (+PUT, PM-only limits)
                                  |
                       PM router* -- shared project authorizer
                                  |       security.csrf_guard / Identity / membership
                              PM service*
                   +--------------+-------------------+
                   |              |                   |
             PM contracts*   short DB phases     provider boundary*
              validate DAG    + run reconciler*    versioned prompt*
              source binding       |                   |
              full plan       PostgreSQL         official AsyncOpenAI*
                              Alembic head*       one real model request

  No SDK/auth key reaches browser. No DB session/lock crosses the SDK await.
```

The old request dependency can already start a SQL transaction during authentication. Merely committing a separate run transaction is insufficient if that dependency retains its connection while awaiting OpenAI. Extract only immutable actor/session IDs from initial checks, close/rollback that request session before the await, then open fresh sessions for final authorization and persistence. Never pass a live SQLAlchemy Session into concurrent tasks or return ORM objects that lazy-load after session close. Use DTOs at phase boundaries. **CEO-07, auto-decided.**

### Authoritative limits and storage invariants

The main plan says “bounded” without a complete numeric contract. Proposed values below are implementation inputs for engineering review, not measured capacity. Reject invalid input before provider invocation; do not truncate user content or silently remove generated fields to fit.

| Boundary | Proposed exact rule |
|---|---|
| Brief/instructions | Brief 1–10,000 non-whitespace characters; optional instructions max 4,000, absent/empty means none. Preserve original project title/description unchanged. |
| Optional context | Explicit same-project plan ID and revision; snapshot at most 20,000 characters; if the selected document exceeds the limit, explain and require a smaller/omitted context rather than silently clipping it. Total serialized user-data snapshot max 48,000 characters. |
| HTTP body | Generation max 256 KiB actual bytes; full-draft PUT max 512 KiB. Enforce while reading, not only via untrusted Content-Length. Bound error payloads too. |
| Output | At most 80,000 document characters / 512 KiB serialized bytes; max 8 epics, 40 stories total, 160 criteria total; every epic has ≥1 story and every story ≥1 observable criterion. Requirements max 40 functional + 20 nonfunctional; bounded overview lists max 20 each. Product title max 120; ordinary labels max 200; long prose max 2,000; each Given/When/Then max 500. Total caps dominate per-field maxima. |
| Structure | `schema_version=1`; strict types, finite enums, extra=forbid, aware server timestamps. Unique stable requirement/epic/story/criterion keys within the plan; bounded references; no self-dependencies, duplicate targets, missing keys, or cycles. Output cannot set PKs, actors, approval, execution metadata, or human provenance. |
| Lists/history | Default 50/max 100 summaries with deterministic timestamp+UUID ordering; no child trees, raw snapshots, or diagnostics in summary rows. |
| Provider | Explicit key/model; total provider timeout 5–180s; output cap 512–16,000 tokens, proposed default 6,000; no retries, tools, provider fallback, or arbitrary base URL. Maxima do not imply that a 6,000-token response can fill every maximum-size field. Compact output should leave honest questions instead of overflowing. |
| Time hierarchy | Proposed pending lease 10s; running deadline = DB start time + configured provider timeout + 30s finalization allowance. Admission work bounded separately; proxy PM limit 240s, browser PM limit 250s, CSRF acquisition remains 10s. Ordinary proxy/client limits stay 15s/20s. Engineering must validate the full worst-case inequality, including pool/lock wait and serialization, before adopting these numbers. |
| Database waits | Existing connect/statement timeouts are 3s/5s; add explicit finite pool wait and PM lock wait. Expired-lease fencing prevents late commit even if cancellation cannot immediately stop a synchronous DB operation. Do not claim a Python task timeout physically cancels a database thread. |

Prefer one canonical plan representation: root JSONB has no epics/stories/criteria tree; relational child rows hold it. Add named unique/check/FK/index constraints for project/version, run→plan one-to-one, local keys/order, valid status/revision, one current approved plan, and one active run. If runs duplicate workspace_id alongside project_id, enforce their agreement with a composite FK/unique key or derive workspace through Project; separate unrelated FKs do not prove agreement. Derive the resulting plan ID through the one generating-run FK as proposed. **CEO-11.**

```text
RUN (terminal transitions fenced by workspace lock + status/deadline CAS)
  new request -> pending -> running -> succeeded (exactly one complete draft)
                   |          |-----> failed (provider/validation/timeout)
                   |          +-----> interrupted (actual cancellation/expired lease)
                   +---------------> failed/interrupted (startup/config/expiry)

  succeeded/failed/interrupted --X--> running or a second success
  same client key -> inspect/replay the existing run; never invoke provider again
  new key -> explicit new request, subject to admission and active-run checks

PLAN
  generated draft vN,r1 -> save CAS -> draft vN,r2 ...
      | approve exact vN,rK, Owner/Admin, no open blockers
      v
  approved vN,rK -> superseded only when newer draft is approved atomically
      X save/edit approved or superseded content
  generating vN+1 does not transition vN and does not make vN+1 authoritative

CONFIRMATION
  model output -> open
  human edit -> resolved(reason) OR deferred(reason) -> may reopen explicitly
  model/provider cannot set a human disposition; approval cannot skip open blockers
```

The synchronous model call is a deliberate local tradeoff. Navigation/disconnect does not guarantee cancellation; a still-running server handler may finish and publish after final authorization. Actual handler cancellation/process loss may leave an interrupted run. No detached, untracked background task is introduced to promise completion. This policy is **TASTE C03** because owners may prefer “stop on disconnect,” but that preference cannot be guaranteed at the provider billing boundary. **CEO-08.**

At 10x local activity the first bottleneck is provider concurrency/latency, followed by thread/connection pressure and large document rendering. At 100x activity the single-process request model, quota policy, and history retention need revisiting; they are not certified at that scale. Add a short PostgreSQL-serialized admission decision: proposed maximum two active runs globally, one per project, and rolling successful-admission ceilings of 5/account/hour and 20/global/hour. Count admitted attempts, including failures; idempotent replay is free of a new slot. Configuration may lower limits, not silently disable them. The exact defaults are **TASTE C04**. A global advisory transaction lock must be acquired before workspace lock on starts, never in the reverse order; do not hold it while calling the provider. **CEO-10.**

Single points of failure are the configured provider/account, PostgreSQL, and the local API process. The intended behavior is visible unavailability, persisted failures where possible, and lease recovery; no fallback model or guaranteed recovery worker is added. New components should be operable without provider credentials for existing Stage 02 journeys. Rollback is forward-compatible code disable/revert with PM tables retained, not migration downgrade or development reset; Section 9 gives the sequence.

## 2. Error and rescue map

**CEO-17: extend safe error identity through the entire transport.** `ApiError` currently discards run IDs/error codes, and the generic POST network message refers to project creation. Preserve bounded public `code`, `run_id`, `diagnostic_id`, and field paths as typed optional data; PM UI selects actions from codes/status, not message text. A failure to parse an error body must still show a safe unknown outcome and keep the client key/draft. Error strings, raw upstream bodies, and Pydantic input/context objects must not be copied into diagnostics or logs.

The registry is a proposed rescue contract, not a claim that these PM handlers exist. “Y/P” means explicitly required and planned; every associated test remains unexecuted until implementation. Named domain exceptions below are proposed classes, not alleged installed SDK classes.

| # / method or path | What can go wrong / named exception | Rescued? / action | User sees / required test |
|---|---|---|---|
| E01 `start_run` body | Missing/wrong/blank/oversized input; FastAPI `RequestValidationError` | Y/P; structured 422 before admission/provider | Field error; no run/provider invocation; boundary integration |
| E02 bounded body reader | Body exceeds byte cap; proposed `PayloadTooLarge` | Y/P; 413, stop reading | Size guidance; direct/proxy boundary check |
| E03 auth/CSRF dependency | Missing session, revoked/expired session, wrong Origin/CSRF; `HTTPException` 401/403 | Y/P; existing guards; no provider | Sign-in/refresh/permission action; real handlers |
| E04 project/context lookup | Absent/cross-tenant/cross-project ID; `HTTPException` 404 | Y/P; identical private missing shape | Not found; no protected preview; exact UUID tests |
| E05 admission | Actor/global ceiling; proposed `GenerationAdmissionDenied` | Y/P; 429 with safe Retry-After; no new run or charge | Explain wait; cross-project concurrent admission |
| E06 `reserve_run` | Active project run; proposed `ActiveRunConflict` | Y/P; 409 and authorized run reference | Check existing run; independent-client race |
| E07 idempotency lookup | Same key, changed canonical input; proposed `IdempotencyConflict` | Y/P; 409, never re-execute | Use original run or deliberate new generation; mismatch test |
| E08 config check | Key/model absent or invalid local limits; proposed `ProviderNotConfigured` / Settings `ValidationError` | Y/P; explicit unavailable category; authorized failed run if DB can persist it | Local setup guidance without secret value; actual missing config |
| E09 SDK authentication | Invalid/revoked key; `openai.AuthenticationError` | Y/P; fail once, safe category/status/request ID only | Operator checks local credentials; no automatic retry |
| E10 SDK access/model | Unsupported/inaccessible model; `openai.PermissionDeniedError`, `NotFoundError`, `BadRequestError` | Y/P; fail once; distinguish access/schema/input safely | Model/configuration unavailable; actual live capability test |
| E11 SDK rate limit | Quota/throttle; `openai.RateLimitError` | Y/P; fail once, bounded safe retry timing if present | Explicit later attempt may charge; no hidden backoff/retry |
| E12 SDK transport | Real connection/DNS/TLS failure; `openai.APIConnectionError` | Y/P; terminal failed when saved | Connection failure with run reference; real closed-loopback/config Case A |
| E13 provider/outer deadline | `openai.APITimeoutError`, built-in `TimeoutError` from outer async timeout | Y/P; failed `provider_timeout`; no plan; no retry | Timed out, Check Status if persistence unconfirmed; deadline test |
| E14 SDK other status | `openai.APIStatusError`, `InternalServerError`, `APIResponseValidationError` where provided by pinned SDK | Y/P; safe named mapping; verify actual exported exception set after SDK pin | Provider failure category, no raw body; SDK-contract check |
| E15 response inspector | Refusal; proposed `ProviderRefusal` | Y/P; failed refusal; do not try to coerce it into a document | Model declined this request; no fabricated plan |
| E16 response inspector | Incomplete/truncated result; proposed `ProviderIncomplete` | Y/P; failed incomplete; no partial plan | Output limit reached/incomplete; deliberate revise request |
| E17 response parser | Empty output; proposed `ProviderEmpty`; invalid JSON `json.JSONDecodeError` | Y/P; separate categories, no repair call | No usable plan returned; isolated parser cases + named Case B |
| E18 contract validator | Pydantic `ValidationError` for extra fields/type/blank/missing data | Y/P; safe locations/types only, not `input`/`ctx` | Invalid plan; previous agreement unchanged; Case B |
| E19 semantic integrity | Bad source quote/key/reference/cycle; proposed `PlanIntegrityError` | Y/P; fail generation or reject save/approve | Specific safe field path and correction; validator tests |
| E20 request cancellation | `asyncio.CancelledError` (inherits BaseException) | Y/P; best-effort interrupted record; re-raise cancellation; never catch as success | Next GET shows interruption/active-until-expiry, possible consumed usage |
| E21 final authorization | Lost role/member/session/user status; proposed `GenerationAuthorizationLost` | Y/P; no plan; terminal failed/authorization-lost if recordable | Permission/session changed; content remains private; race test |
| E22 late finalization | Expired lease or terminal status; proposed `RunLeaseLost` | Y/P; no publish, preserve terminal state | Interrupted/failed; no second success; late-response fence |
| E23 DB phase | `sqlalchemy.exc.OperationalError`, `DBAPIError`, pool `TimeoutError` | Y/P; rollback; 503; if run outcome cannot be stored, explicitly unconfirmed | DB unavailable/unknown outcome; real unavailable DB + reconciliation |
| E24 constraint race | `IntegrityError` | Y/P; inspect named constraint in a fresh session after rollback; map known race to 409, unexpected integrity to sanitized 503 | Conflict or persistence failure; never leak SQL/parameters |
| E25 `save_draft` | Stale revision/immutable state; proposed `PlanRevisionConflict`, `PlanStateConflict` | Y/P; 409; no overwrite | Preserve local edit; reload separately; concurrent saves |
| E26 `approve_plan` | Open blockers/incomplete document; proposed `PlanApprovalBlocked` | Y/P; 422 safe paths; no state change | Resolve/dispose listed confirmations; approval negative |
| E27 `approve_plan` race | Older-than-current approval/exact revision changed; proposed `PlanApprovalConflict` | Y/P; 409, old approved plan intact | Review exact current state; simultaneous approval |
| E28 browser/proxy read/write | Fetch `TypeError`, abort/timeout `DOMException`; safe API non-2xx | Y/P; unknown-generation versus known-rejection distinction; GET reconciliation only | Draft/key retained in memory, no re-POST; real offline/UI check |
| E29 reconciler/lifespan | DB error/cancellation while sweeping or closing SDK | Y/P; finite work, static event, stop task on shutdown; expired records remain eligible | Reads reconcile later; no healthy/resumed-work fiction |
| E30 prompt/package resource | Missing/unreadable versioned prompt; `FileNotFoundError`, `OSError` | Y/P; disable PM capability with setup error; no provider call | Planning service unavailable; Stage 02 remains usable |

```text
named failure -> classify safely -> rollback current DB transaction
        |                       -> persist terminal run in a fresh short transaction
        |                                  | success: return run + safe category
        |                                  + DB failure: outcome UNCONFIRMED
        + cancellation: re-raise; lease fencing/reconciliation is the fallback

No rescue -> generated fallback document; no rescue -> automatic provider retry.
```

The skill's generic suggestion to log arguments/full context is overridden by the owner's explicit secret/project-description restrictions. Correlate with actor/workspace/project/run/diagnostic UUIDs, static event codes, sanitized exception class/status/request ID, and timings. Do not use a blanket `except Exception` to fabricate completion or swallow cancellation. A final framework 500 boundary may return an opaque reference, but it does not replace named mapping or count as a handled business outcome.

## 3. Security and threat model

**Four high-priority findings: CEO-04, CEO-06, CEO-10, CEO-11.** The new attack surface is seven PM route families, full nested editable content, prior-plan selection, long-lived provider requests, a server secret, and lease reconciliation. It does not include command execution, file retrieval, browsing, or arbitrary model endpoints. Every read authorizes the current project/member before touching run/plan/context data; every write also uses CSRF/Origin and current role under workspace lock. Viewer read access must not expose raw diagnostics, input snapshots beyond the authorized plan/source display, secret configuration, or another project's metadata.

| Threat | Likelihood / impact | Mitigation and remaining limit |
|---|---|---|
| Cross-workspace/project UUID substitution in run, plan, context, body child IDs | Medium / High | Project-first lookup plus child FK scoping; identical 404; never trust supplied workspace/creator. Add mismatch tests using known real UUIDs, not only random absent IDs. |
| Provider or client claims text is “human edited,” approved, or supplied evidence | High / High | Separate provider schema from edit commands; server diffs the stored draft by stable field/key, preserves unchanged provenance and assigns actual editor/time to changed/new fields. Server alone resolves source snapshot IDs/quotes and approval metadata. Whole-document PUT cannot manufacture those fields. |
| Exact quote is attached to a stronger unsupported claim | High / Medium | Exact binding catches invented quotes but cannot prove entailment. Label it “source: supplied brief,” preserve suggestion/assumption distinctions, and require human review. No semantic-certification badge. |
| Role removal, logout, session expiry, or disabled user during provider wait | Medium / High | Fresh final session/user/membership check; no plan when authority is lost; usage may be retained without publishing. Captured identity objects must not satisfy the recheck. |
| Cost/availability abuse across many projects | Medium / High locally | Global and actor admission limits, finite tokens/context/time, no retries, explicit click. No currency ceiling or internet-scale abuse resistance is claimed. |
| Prompt injection in brief/instructions/prior plan | High / Medium | Data object separate from fixed system prompt; no tools or code execution; structural/source checks after output. The model may still produce bad advice; no guarantee of prompt-injection immunity. |
| HTML/script/Markdown URL injection in generated or edited text | Medium / High | Render text through React escaping; no `dangerouslySetInnerHTML`, auto-linking or executable Markdown. Any future link renderer needs its own scheme validation and scope decision. |
| Input-size/graph denial of service, pathological Unicode | Medium / Medium | Byte + character + total-node/reference bounds, strict integers/UUIDs/enums, linear graph validation; treat text as Unicode, reject whitespace-only, do not strip meaningful password/project content. |
| Key/cookie/brief leakage through SDK, Pydantic errors, logging or browser evidence | Medium / High | SecretStr server settings, no public raw diagnostic endpoint, `hide_parameters`, SDK HTTP debug off, error location/type allowlist, no auth traces or raw screenshots of sensitive briefs. No new log can echo request/response bodies. |
| Inconsistent run.workspace_id/project.workspace_id | Low / High | Enforce one source of ownership through derivation/composite constraints; authorize via Project, not a denormalized client/run field. |

The new key is local server configuration only; users never submit it through the UI, logs, evidence, model context, or chat. Operator rotation is documented but not performed. `store=False` is an API request option, not a guarantee that the provider has no retention/processing obligations. Explicit Generate should say that the project brief and selected context are sent to the configured model provider, with no credential or unrelated workspace data included. Do not promise research, confidentiality certification, or production security.

OpenAI's official SDK is the only new integration dependency. Pin its resolved stable version in uv.lock and inspect the actual response/error types and transitive dependencies during implementation; this review did not install it or assert a latest version. SDK schema support is model/capability specific, so exported schema validation and actual account access are feasibility gates. The provider can produce refusal or incomplete output despite schema configuration. [OpenAI structured output guide](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), [Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create).

## 4. Data flow and interaction edge cases

**CEO-09/12/13/16: pin the canonical input, revision, graph, and browser ownership.** All four paths below are required for every new flow. Optional nil/empty instructions are valid “none”; required nil/empty brief/document never reaches the provider or persistence. An absent authorized history is an empty collection, while a missing selected resource is a private 404. A provider failure cannot produce a half-plan.

```text
GENERATION
  brief + optional context ID/rev -> authorize + bounds -> immutable canonical snapshot/hash
       | nil/empty required:422         | wrong tenant:404 / stale context:409
       | optional nil/empty:none        | too large:413/422
  -> admission + idempotency -> pending/running commit -> ONE SDK call
       | same key/same hash:replay  | missing config:failed, no call
       | same key/different:409     | refusal/empty/incomplete/error:failed
       | active/budget:409/429      v
  -> validate full graph + provenance -> fresh authorization + lease -> atomic draft+children+success
       | bad quote/ref/cycle:failed       | lost permission:failed / expired:interrupted
       | nil/empty result:failed          | DB failure:rollback/unknown, no claimed plan

READ / CONTEXT / CAPABILITY
  project + optional plan/run ID -> current membership -> bounded query -> safe DTO
       | nil/malformed ID:422        | foreign/missing:404
       | no history:[]               | DB failure:503, no stale protected fallback
  selected plan context -> verify project + expected revision -> immutable source snapshot
       | absent selection:none       | empty/oversized context:reject selection explicitly
  capability -> configured fields/limits only; absent key/model -> unavailable, never “connected”

EDIT
  complete local draft + expected rev -> authorize -> validate bounds/graph -> server provenance diff
       | nil/empty/invalid:422             | missing child/foreign key:422/404
  -> workspace + plan lock/CAS -> update root+children + increment rev atomically -> safe DTO
       | stale/state conflict:409; preserve local text | DB failure:rollback/keep local draft

APPROVE
  exact plan ID/version/rev -> Owner/Admin under workspace lock -> complete graph + confirmations
       | missing/wrong type:422  | Viewer/Member:403 | foreign/missing:404
  -> compare current approved version -> supersede old + approve exact draft in ONE commit
       | stale/incomplete/open:409/422; no state change | DB error:rollback both changes

RECONCILE
  internal tick or authorized read -> bounded expired active candidates -> workspace lock + refresh
       | none:0 updates                 | not expired/terminal:no-op
  -> fence pending/running -> interrupted -> status DTO / static event
       | invalid run/membership:404     | DB failure:503/defer; never “resumed”
```

Canonical hashing must cover normalized validated inputs, the selected context's immutable content/revision, title/description snapshot, prompt/schema version, and requested model. The same key cannot silently rebind to today's changed project description or edited context on replay. First authorize project, then look up the scoped initiating-account key; a replay returns the original immutable run. A changed body is 409 even if the earlier run failed. Explicit regeneration uses a new key and preserves approved data. **CEO-09.**

Saving a full document needs one transaction and expected-revision CAS or locked reread. Validate before mutation; update child collections only inside that transaction; rollback must restore all rows if the last criterion fails. Client-supplied row IDs are scoped references, never authority to move rows between plans. Add/remove of a referenced requirement/story must report dangling dependencies, never silently drop or retarget them. Maintain stable local keys across draft edits and new server-owned UUIDs for new nodes. **CEO-12/13.**

For approval, compare the candidate version against the **current approved** version. A newer unapproved draft must not forbid approving an otherwise valid older draft unless the owner explicitly changes that policy. Two simultaneous approvals serialize through the workspace lock; the final current approved record is unique and prior content/approver/timestamps remain readable. Do not compare only max(version), silently approve the latest revision, or autosave edits during approval. An approval retry after an uncertain response first GETs the exact plan; it must not be treated as a request to approve a newer version.

| # | Interaction edge case | Required handling / verification |
|---|---|---|
| I01 | Double Generate click in one frame | Immediate submission ref/lock, disable action, one stable key; server constraint independently protects. |
| I02 | Two tabs/users start one project | One active run; loser sees 409 and authorized reference; test with independent clients. |
| I03 | Two projects bypass per-project protection | Global/actor admission applies; bounded concurrency and no hidden provider calls. |
| I04 | Stale CSRF/session on submit | Real guard rejects; retain nonsecret local brief; no automatic authentication/write retry. |
| I05 | Slow provider while browser navigates/reloads | Clear UI state on route change; history recovers real run; no new POST; completion/interruption policy is explicit. |
| I06 | Proxy timeout after API committed success | Say outcome unknown, Check Status GET with original key/run; show the committed result once found. |
| I07 | Timeout before any reservation | GET may show no matching run; only an explicit new action may POST; explain absence rather than declare failure saved. |
| I08 | Check Status GET fails | Keep unknown state/key; show error; never replace with a fake failed/succeeded record. |
| I09 | Role removed/session revoked during execution | Final authority check prevents publication; unauthorized follow-up reads clear protected UI. |
| I10 | Read response for version A arrives after selecting B | Request generation/key guard ignores A; do not overwrite selected document/dirty editor. |
| I11 | Workspace/account changes during save/generate | AuthGate remount clears protected drafts; old callback cannot restore them into new context. |
| I12 | Brief edited while generation is active | Snapshot remains immutable; pending result labels the submitted snapshot. Editable next brief cannot alter that run. |
| I13 | Project description changes concurrently | Preserve project fields; resulting plan labels captured source, not “latest project description.” |
| I14 | Plan selected as context was edited | Expected context revision mismatch rejects before call; replay uses original snapshot. |
| I15 | Two edits race | Exactly one expected-revision save succeeds; loser retains text and can inspect fresh server version separately. |
| I16 | Save fails / validation fails / DB unavailable | Preserve local entire draft, dirty flag and selected revision; truthful field/global error. |
| I17 | Version switch, context switch, cancel edit, or back action with unsaved changes | Explicit discard confirmation for application-owned actions; beforeunload for document leave where supported. No protected localStorage backup. Browser-back limitations remain documented. |
| I18 | Approval while edits are dirty | Disable approval until saved or explicitly discarded; confirmation names saved version/revision. |
| I19 | Confirmation list is empty/open/resolved/deferred | Empty is valid only when model found none; open blocking item prevents approval; dispositions use actual human metadata. |
| I20 | New generation while a plan is approved | Retain approved default view; new draft labeled separately; no silent replacement. |
| I21 | Older draft versus newer approved/newer draft | Reject only superseded/older-than-current-approved candidates; preserve explicit version navigation. |
| I22 | Empty run/plan history | Honest no-plan state and permitted Generate action/config guidance; no sample output. |
| I23 | Many history rows/change during pagination | Bounded stable ordering; no repeated full trees; reset pagination on project change; no loss of selected document. |
| I24 | Maximum nodes, long Unicode/HTML-like strings | Escape text, wrap, native disclosure, no horizontal overflow; total bounds protect rendering. |

The interaction map has 24 mapped edges. These are planned handling rules, not executed results. No edge remains unspecified after these decisions; the main plan still needs to adopt them and implementation must prove them.

## 5. Code quality review

**Two organization findings: CEO-21 and CEO-24.** The proposed router/service/provider separation is sufficient, and Pydantic plus SQLAlchemy/Alembic already cover the right responsibilities. Put output/edit/run DTOs and integrity checks in `pm_schemas.py`, provider response normalization in `pm_provider.py`, lifecycle/persistence in `pm_service.py`, and thin HTTP mapping in `pm.py`. Keep models with the existing schema authority or one explicitly imported PM model module; do not leave migrations unaware of a second Base. The fixed prompt is a packaged local resource with a version/hash, not a user-selected path.

Avoid DRY regressions at the concrete reuse seams: `main.py:137` project lookup; `security.py:84,102,118` CSRF/membership/roles; `lib/api.ts:10` cookie transport; SessionProvider's generation guards; existing ProjectForm creation. PM must not fork those into new implementations. Preserve a single canonical serializer/deserializer and a single integrity validator shared by generated results, full-draft saves, reads, and approval; apply role-specific provenance rules outside the common structural validator.

No one method should hide all lifecycle branches. If start/finalization/approval branches exceed five independent conditions, split named guard functions (`validate_source_bindings`, `check_admission`, `assert_run_lease`, `validate_approval`) that return ordinary typed data or raise the specific domain errors in Section 2. Do not create an abstract generic service hierarchy just to move branches around. An explicit schema version and stable local identifiers are cheap now; promising stable cross-version semantic identity is not. **CEO-24.**

The current JSX compression becomes painful in a nested editor; new feature code should use readable components grouped by actual user tasks (overview, requirements, epic/story editing, confirmations). Add helpers only when a repeated input/error pattern is real. Use native controls and existing Button/tokens, with no form/graph/state-management dependency. Unknown/empty/refusal/429/timeout paths remain first-class typed outcomes, never optional “TODO” branches.

## 6. Test review

**Two verification findings: CEO-14 and CEO-15.** Preserve the original 44 backend and 42 browser cases and their assertions, but report resulting counts from executed output rather than assuming parameterized totals. Core deterministic tests and controlled service failures must run without hidden paid calls. The full mandatory Stage 03 command cannot report VERIFIED if separate real API or browser generation is blocked. No skip, xfail, fake production provider, canned browser response, or successful fixture artifact can substitute.

```text
NEW UX FLOWS
  input/config -> Generate -> real pending/result -> inspect sources -> edit/save
  -> exact approval -> reload/history -> read-only/revoked access -> unknown recovery
     coverage: real API+PostgreSQL browser journey; role/offline/error cases; max-size mobile UI

NEW DATA / CODE PATHS
  bounds + strict DTO + DAG/source validation        -> isolated unit contracts
  admission/idempotency/lease/state transitions      -> real PostgreSQL constraints + API/service tests
  snapshot + relational children + rollback         -> fresh-session DB assertions
  draft CAS + provenance diff + atomic approval     -> real persistence/independent-client races
  project-first resource lookup + CSRF/current role -> real handlers/users/tenants

NEW ASYNC / EXTERNAL WORK
  one official SDK call + cancellation/deadline      -> separate real provider test
  bounded internal expiration reconciler            -> seeded expired/unexpired rows + actual GET/lifespan
  live browser Generate                             -> separately invoked desktop flow, actual provider

NEW ERROR / RESCUE PATHS
  E01–E30 -> unit contract cases where isolated; real API/DB negative paths where applicable
  Case A actual config/connectivity failure -> API + useful UI + unchanged existing approved/project data
  Case B malformed-provider DOUBLE -> explicitly owner-authorized narrow negative, never live evidence
  intentionally wrong success assertion -> explicit-only file; actual exit 1, outside passing discovery
```

### Exact owner-required backend coverage

The parent's supplied original requirement list is preserved below so “all 20 cases” cannot become an unverifiable summary. Headers are proposed test specifications; none of these new tests is claimed to exist or pass.

| # | Required scenario / proposed test header | Evidence boundary and key assertion |
|---|---|---|
| 1 | `test_authorized_member_can_initiate_pm_generation` | Real signup/workspace/API; authorized reservation reaches the real application path. Live success is proved separately. |
| 2 | `test_viewer_cannot_initiate_pm_generation` | 403, no admitted run/provider call; real Viewer membership. |
| 3 | `test_unrelated_user_cannot_read_exact_run_uuid` | Same private 404 as missing; exact existing ID. |
| 4 | `test_unrelated_user_cannot_read_exact_plan_uuid` | Same private 404; no document/model/diagnostic leak. |
| 5 | `test_invalid_input_is_rejected_before_provider_boundary` | 422/413, count unchanged; isolated invocation counter only in a justified unit test, real API negative independently. |
| 6 | `test_product_plan_contract_accepts_valid_structured_output` | Isolated Pydantic fixture contract; separately live output passes same validator. No claim fixture was generated. |
| 7 | `test_generated_plan_persists_across_database_sessions` | Live API-generated draft, fresh SQLAlchemy session and GET agree. Authored persistence fixtures may exercise storage code but do not prove generation. |
| 8 | `test_epic_story_criteria_relationships_match_document` | Actual DB FKs/order/local keys/counts, no duplicate JSON tree; live output plus application persistence tests. |
| 9 | `test_malformed_provider_output_is_rejected_case_b` | Explicitly named owner-authorized malformed double, real validator rejects; no valid plan. |
| 10 | `test_failed_generation_never_persists_a_successful_plan` | Real Case A + explicit Case B; terminal status and fresh DB relationship count. |
| 11 | `test_provider_timeout_records_failed_run` | Isolated timeout mapping/state test plus actual bounded SDK/timeout failure where reachable; no fake timeout integration classified as real provider evidence. |
| 12 | `test_missing_runtime_configuration_is_an_honest_failure` | Actual absent key/model settings; safe response, failed run when DB writable, no call or plan. |
| 13 | `test_duplicate_generation_keys_and_active_runs_are_safe` | Real DB constraints/independent-client races; one successful plan at most, same-key replay never calls again, payload mismatch 409. |
| 14 | `test_draft_full_save_persists_and_increments_revision` | Real API PUT and fresh DB/reload; provenance server-derived. |
| 15 | `test_approval_persists_real_actor_and_utc_timestamp` | Owner/Admin real session; exact version/rev; new DB session confirms actor/time. |
| 16 | `test_incomplete_invalid_or_open_confirmation_plan_cannot_approve` | Integrity validation and actual approval guard; no approved-state mutation. |
| 17 | `test_generation_and_stale_save_do_not_overwrite_approved_plan` | Existing approved document/hash/actor/time compared before/after failure and new generation. |
| 18 | `test_older_approved_and_superseded_versions_remain_readable` | Authorized history/detail, immutable content and approval evidence. |
| 19 | `test_pm_preserves_project_and_tenant_isolation` | Cross-project IDs inside same workspace + exact unrelated tenant IDs + restricted legacy; project fields unchanged. |
| 20 | `test_existing_auth_workspace_project_regressions_remain_intact` | Original backend/browser suites, CSRF/Origin/owner preservation and legacy migration tests retained. |

Only isolated unit tests may use ordinary justified mocks under AGENTS. The owner explicitly authorizes a malformed-provider double for Case B; that is a narrow exception, not blanket permission to replace the provider in every integration test. Name it in the command/output/evidence, wire it only through test dependency construction, and provide no environment-selectable production fake. Unit fixtures may be hand-authored contract inputs; actual persistence setup may insert declared test data using real application storage code. Neither may be presented as a successful model run. Lifecycle/permission/concurrency tests should exercise real PostgreSQL and application guard/finalization functions with explicitly seeded states; successful live execution still requires the separate real calls. Engineering must make this boundary explicit in the test plan instead of ambiguously calling every double-backed case an integration success.

Add targeted specifications for session/role loss mid-run, active/unexpired cross-process lease protection, expired-read reconciliation, canonical key mismatch, concurrent global admission, late finalization, child transaction rollback, stale save/approval, provenance forgery, unsupported schema/model, Unicode/error-payload secret redaction, missing PM schema readiness, and populated Stage 02→03 upgrade/repeated upgrade. Use barriers/real transactions for races and explicit DB timestamps for expired rows; avoid sleep-based timing tests. Any unavoidable live timing uncertainty is reported, not papered over with retries.

The separate real API command and desktop live browser command each make at least one actual generation; neither reuses a fixture as its claimed generation. The live browser must Generate → inspect output → edit a criterion → save → reload → approve exact version → reload → verify actor/time/persistence and deny an unrelated account's exact UUID access. Additional mobile/tablet PM checks cover readable empty/error/read-only/max-size/editor states; they do not establish native-device or all-browser compatibility. Because the owner requires two distinct live flows, plan at least two real model calls and disclose actual usage if returned; no unbounded rerun loop or estimated price is implied. **CEO-15.**

The Friday-at-2am confidence test is the whole live journey followed by a new failed generation that leaves the approved plan and original project byte-for-byte equivalent. The hostile QA case submits a valid foreign plan/context UUID plus forged human provenance while another user changes membership. The chaos case terminates a generation process after reservation and restarts the API: the run expires/interruption is visible, no partial child tree exists, no duplicate/replayed model call occurs, and Stage 02 still works.

There is no existing CLAUDE prompt-eval convention in this checkout. Add a compact declared brief set (clear habit tracker, underspecified brief, conflicting instructions, prompt-injection text, Unicode/long boundaries) and a human-readable quality rubric: supplied needs represented, suggestions labeled, no invented factual targets, usable story/criteria, references valid, unresolved choices explicit. Core unit evaluation uses declared authored inputs; model quality conclusions use actual live results and prompt hash/model/response metadata. A small live sample establishes bounded functionality, not a statistical model-quality score or a benchmark win.

## 7. Performance review

**CEO-22: define resource budgets and verify bounded growth before choosing optimization.** The three slowest new paths will be provider generation, maximum-size plan validation/save/serialization, and maximum-history/document reads. There is no measured PM p99 yet; inventing one would be misleading. The proposed provider hard cap is 180s, default 60s, with the separate lease/transport allowance in Section 1. Record actual provider and total run durations in live evidence. Read/save latency should be measured on both compact and maximum allowed documents in the real local PostgreSQL environment before setting a product performance target.

Load the plan root and children in bounded batches/eager relationships; do not issue one query per epic, story, criterion, source, or dependency. A useful regression checks that doubling story count within the cap does not grow SELECT count per story, rather than mirroring a fragile implementation-specific query total. Index every actual query: project/run created-time+UUID history, plan project/version, child parent/order, run generating-plan uniqueness, initiator/project/client-key lookup, active status/deadline reconciliation, and actor/global admission-time lookups. Verify plans against real `EXPLAIN` where the query shape or index is uncertain; do not add indexes without a query.

The memory budget is bounded by request/snapshot/document caps, but their parsed Python/ORM/React representation is larger than raw JSON. Two active provider runs bound external work; concurrent reads and edits still need finite pool wait and bounded result sets. Synchronous SQLAlchemy phases belong outside the event loop, and a shared Session cannot be used concurrently. Reconciler scans should be finite (proposed batch 20, interval 5s) and release connections between batches; no endless request-time full-history sweep. Test an unexpired run owned by another process to prove it is not interrupted.

Do not cache protected plan responses or provider output across users/projects: responses already use no-store, and explicit idempotency is the appropriate reuse mechanism. Reuse a single owned SDK client per application lifespan for connection efficiency, close it on shutdown, and leave SDK retries disabled. CPU profiling, Redis, distributed caches, and load certification at 100x are deferred. A bounded concurrent two-run plus ordinary project-read smoke check is enough for the local design; it must show that generation does not consume the entire DB pool or freeze Stage 02 navigation.

## 8. Observability and debuggability

**CEO-18: the run table is the local operational dashboard, but it needs an explicit runbook.** Day-one inspection must answer: was the request admitted; did it reach the provider; why did it fail; did the database confirm the outcome; which exact prompt/schema/model/snapshot/revision was involved; and who approved the resulting document? A durable run record and sanitized events cover that without introducing an observability platform. This is not a claim that logs alone reconstruct unsaved browser edits or every historical draft revision.

Emit static, structured events for admission/replay/rejection, provider start/end, validation rejection, authorization loss, finalization, draft save, approval, lease expiry, and diagnostic persistence failure. Include run/project/workspace/actor/diagnostic UUIDs, safe error category/class, prompt/schema version/hash, phase durations, returned model/request ID, and nullable actual usage. No brief/output/error body, key, cookies, source quote, email, password, raw validation input, or raw stack trace. Run ID correlates API, provider metadata, browser Check Status, and DB evidence; an unrelated new tracing service is unnecessary.

| Operational signal | Where to obtain it locally | Response |
|---|---|---|
| Active runs and oldest deadline | Authorized run history; operator read-only SQL by status/deadline | If expired, reconcile; if unexpired, wait. Never restart/re-POST automatically. |
| Success/failure/interrupted counts and safe categories | Stored run summary grouped by time/status | Investigate the dominant category; counts measure execution reliability, not plan quality. |
| Provider latency versus timeout | Stored timestamps/static phase durations | Inspect configured model/time/output cap; deliberate new generation only. |
| Output/usage completeness | Actual returned metadata or null | Show unavailable where absent; do not infer tokens, costs, or IDs. |
| Approval blocked/conflict counts | Static event code and current revision/confirmation state | Resolve data/permissions, then review the exact version. |
| Reconciler errors / failure outcome unconfirmed | Static diagnostic event + expired active record | Restore PostgreSQL; GET/reconcile, inspect terminal state before any new paid action. |

Alerts in local scope are visible unavailable/error status plus an operator-documented query/log check, not an invented Slack/email notification or unattended monitoring guarantee. No message is sent. Proposed runbook entries cover missing config; inaccessible model/schema; provider 429/timeout/outage; DB outage during finalization; stuck active lease; permission loss; stale save/approval; and restart with in-flight work. Each says what evidence to inspect, what remains unknown, how to stop new generation with a nonsecret enable flag, and when a new explicit request is safe. No raw diagnostic endpoint or generic admin UI is needed.

The small operational delight is that a user can give the operator a run/diagnostic reference and receive a precise explanation without sharing the brief or secret. Persisted metadata should be sufficient three weeks later to distinguish configuration, provider, validation, permission, persistence, and interruption failures. Retain plan/run history in this stage; do not add an automatic deletion policy that conflicts with preservation. Document growth as an operational debt for a later owner-authorized retention decision.

## 9. Local rollout, migration, and rollback

**CEO-19/20: make the additive rollout and forward rollback explicit.** Add a nonsecret `ORBA_PM_ENABLED` capability/kill switch, defaulting unavailable until explicitly enabled locally with working model/key configuration. Missing provider credentials or a disabled flag must not break app startup, login, existing projects, core readiness, lint/typecheck/build, or deterministic negative tests. Readiness should still fail if the expected Stage 03 schema is missing; provider reachability belongs to separate capability/live checks, not a paid readiness probe.

The Stage 03 migration creates only new PM tables/constraints/indexes; it does not rewrite Stage 01/02 project, user, session, workspace, membership, invitation, or timestamp data. New FKs can acquire locks on referenced tables, so this local rollout should stop API writes before migration rather than claim zero downtime. Test a populated Stage 02 schema with varied roles, sessions, invitation state, ordinary and restricted legacy projects, preserving all old fields; upgrade twice; verify model/migration drift. Never downgrade/reset the development database. The existing populated Stage 01→02 test remains intact.

```text
LOCAL ROLLOUT
  checkpoint + operator backup verified by parent
       -> stop local API writes / PM disabled
       -> additive Alembic upgrade + check
       -> start API (--host 127.0.0.1 --no-proxy-headers), PM unavailable
       -> Stage 02 core regression + readiness + schema/preservation tests
       -> explicit local provider configuration + bounded real API smoke
       -> real live browser journey + negative paths
       -> complete verification ledger and truthful stage verdict

FORWARD ROLLBACK
  PM malfunction?
       -> disable new PM admissions (nonsecret flag); preserve all records
       -> stop/drain or interrupt in-flight handlers; verify no late publication
       -> restart compatible API/web with PM disabled or revert compatible code
       -> retain additive PM tables and historical data; NO downgrade/reset
       -> verify login/workspace/project create/read/edit + readiness
       -> record exact remaining active/terminal run outcomes and blocker
```

A PM flag changed through configuration takes effect only according to the documented settings lifecycle; if Settings is loaded at startup, restart is required. Do not promise instant hot disabling. Old Stage 02 code can ignore the additive tables, but new PM writes must stop before running an older frontend/API pair. A stale browser must receive a safe unavailable/conflict response rather than invoke an undocumented endpoint. Do not run mixed-version migrations, workers, or overlapping backend/browser cleanup on the shared test DB.

First five-minute checks: liveness; migrated readiness; real login/session/CSRF; existing project list/detail/edit; disabled/unconfigured PM capability; no startup provider call. First-hour checks after enabling: one bounded API execution, one separately bounded browser execution, exact saved/approved retrieval, negative case behavior, no leaked secret fields, no expired active runs, and no unauthorized exact-ID access. These are a planned local checklist, not a public deployment or staging/prod-parity claim. The parent backup alone is not a tested disaster restore; no destructive restore test is authorized here.

## 10. Long-term trajectory

**CEO-24: preserve a versioned agreement, not a premature universal agent protocol.** A schema version, immutable source snapshot/prompt hash, stable local document keys, and exact approved plan ID are sound foundations. They keep later consumers from having to reinterpret current browser state or treat a newly generated draft as authority. They do not establish that story S1 in independently regenerated v2 is semantically identical to S1 in v1; cross-version mapping/diff needs later explicit design.

Reversibility is **4/5** for the adapter/prompt/UI/module choices, **3/5 overall** once approvals and version history are real records: additive tables are easy to ignore but legitimate historical evidence must be retained. A provider change is a future explicit compatibility/evaluation decision, not a reason to build Model Hub now. SQLAlchemy 2/Pydantic 2/FastAPI and the current Next App Router/strict TypeScript stack fit the repository's chosen ecosystem. Existing compatibility pins remain; this stage does not justify an unrelated framework upgrade.

Six-month regrets would be: a broad schema consistently fills invented commitments; the app cannot distinguish draft from approved; an outage encourages duplicate paid requests; all tests use model doubles; or a queue/plugin framework costs more to operate than the one agent. The accepted choices directly address those failures. The strongest next product-learning question is whether humans can actually turn one draft into an agreement with few corrections, rather than whether more agent roles can be added. No customer identity, market size, conversion target, or usage KPI is inferred from this unconfigured local product.

Debt explicitly introduced is limited to the synchronous non-resumable lifecycle, retained run/snapshot growth, a small live-quality sample, and draft edits that preserve current per-field origin/last-editor metadata without claiming a full immutable event log for every draft revision. Document these four limitations. A new engineer in twelve months should be able to read the schema/prompt version, lifecycle diagram, role table, error registry, and exact commands to understand why a stored approval exists. Rejected diff/push/platform expansions are not load-bearing for the accepted scope; they remain deferred. Nothing in this trajectory authorizes Stage 04.

## 11. Design and UX review

**CEO-16/23: make authority and recovery visually explicit before adding density.** Preserve the original project overview/editor, then show a Product Plan section with: current approved agreement if present; a clear separate draft/version choice; the explicit Generate action and bounded brief/context; open confirmation summary; the selected plan content; sources and actual execution metadata in disclosure; and recent run history/recovery. If no approval exists, show the latest draft clearly labeled. A newer unapproved result must never quietly replace the approved default.

```text
authorized project detail
   -> no plan [brief + provider disclosure + explicit Generate]
   -> submitted [real pending/running status + run reference]
         | -> unknown [Check Status GET] -> active / succeeded / failed / interrupted / no record
         | -> failed [safe category, preserved brief, existing approval intact]
         + -> draft [sources + uncertainty + native expandable epics]
                    -> edit [dirty local state] -> Save -> saved exact revision
                            | conflict/error: keep draft + inspect server revision
                            + version/leave: explicit discard choice where app can intercept
                    -> confirmations [human resolve/defer with reason]
                    -> Owner/Admin approve exact version/revision
                    -> approved [actor/time, immutable] -> reload same approved agreement
   Viewer: read-only plan/source/history; no generate/save/approve authority
```

| Feature | Loading | Empty | Error | Success | Partial/unknown |
|---|---|---|---|---|---|
| Capability/input | Check configuration without model call | Missing model/key/disabled: specific setup explanation | Capability fetch unavailable | Nonsecret model/limits; explicit data disclosure | No “connected” badge based on config alone |
| Generate/run | One actual pending/running status | No previous runs | Safe named failure, unchanged approved/project data | Real draft/version/run metadata | Unknown outcome with Check Status; no fake percentage/steps |
| Plan/history | Selected version loading, keep labels coherent | No plan, permitted next action | Not found/permission/DB error | Draft/approved/superseded state plus actual version/rev | Obsolete response ignored; selected plan not silently switched |
| Editor | Save pending, prevent duplicate submit | Optional list is explicitly empty; required fields cannot disappear | Field validation/stale revision/DB error | Saved revision and last editor | Unsaved marker; all text retained on failed save |
| Confirmation/approval | Explicit approval pending | No blocking confirmations | Open blocker/stale/forbidden | Real approver/time; immutable approved content | Dirty edits cannot be silently autosaved/approved |

The journey should move from clear intent, through a truthful wait, to scrutiny and ownership. The meaningful reassurance is “saved revision 3, approved by this person,” not animated agent avatars, fictional thoughts, glowing status cards, confidence numbers, or sample content. First generation should keep the submitted brief visible and show how suggestions differ from supplied needs. Metadata and sources should be available without making them dominate the agreement.

No DESIGN.md exists; semantic tokens in `globals.css`, the existing Button, native form controls, and the existing responsive shell are the actual design authority. Use a single mobile column, wrapped long strings, no horizontal story table, bounded nested disclosures, and at least the existing 44px mobile target convention. Controls need visible labels, unique stable IDs, fieldset/legend groups, descriptions/error association, keyboard-operable add/remove/select controls, focus placement after removal and on first error, and polite status announcements without announcing every long text change. Color alone cannot identify provenance/state. Check both themes, keyboard focus, reduced motion, and actual browser overflow; Chromium emulation establishes only that tested scope.

X1–X5 still fit the architecture after deep review: they require no live push, new store, generated execution, or cross-version diff engine. The UI gets clearer by keeping one primary action per state and progressive disclosure for the rest. A dedicated Design phase is appropriate next, but this reviewer does not start it or imply its approval.

## Failure modes registry

All rescue, user, log, and test entries below are **planned obligations**. `P` is not a passed test or implemented handler. No current Stage 03 failure path has been executed by this reviewer. There are 30 mapped paths and zero unassigned rescue actions in the proposed design; live verification is blocked by absent runtime configuration. The absence of a designed silent path is not a VERIFIED product verdict.

| Codepath | Failure mode | Rescue | Test | User sees | Logged/persisted safely |
|---|---|---|---|---|---|
| E01 input validator | Missing/type/blank/count invalid | P:422, no call | P:unit + real API | Correct field | Static validation category |
| E02 body reader | Too many actual bytes | P:413 | P:direct + proxy | Size limit | Code only |
| E03 security guard | Session/Origin/CSRF invalid | P:401/403 | P:real auth/CSRF | Sign-in/refresh/denied | Existing static event |
| E04 resource lookup | Missing/foreign exact UUID | P:private404 | P:two tenants/projects | Not found | No foreign data |
| E05 admission | Actor/global rate/slot exhausted | P:429 | P:real DB race | Wait, safe Retry-After | Admission category |
| E06 reservation | Active same-project run | P:409 | P:independent clients | Check existing run | Existing authorized run ID |
| E07 idempotency | Same key/different snapshot | P:409, no call | P:canonical replay | Conflict, deliberate new action | Key conflict category, no payload |
| E08 config | Missing/invalid runtime config | P:failed/unavailable | P:actual settings | Setup guidance | Failed run if persistable |
| E09 SDK auth | Key rejected | P:failed, no retry | P:error mapping / actual if encountered | Config/auth issue | Class/status/reference |
| E10 SDK model/schema | Access/model/schema rejected | P:failed | P:contract + real configured model | Model unavailable/invalid response contract | Safe code/status |
| E11 SDK429 | Quota/rate limited | P:failed, no retry | P:isolated error mapping | Later explicit attempt | Safe status/timing |
| E12 transport | SDK connection fails | P:failed | P:real Case A | Connection failure | Class/reference |
| E13 deadline | Provider/outer timeout | P:failed | P:timeout path | Timed out, status if unknown | Duration/category |
| E14 SDK response/status | Upstream5xx/invalid envelope | P:failed | P:named SDK contract | Provider failed | Class/status, no body |
| E15 refusal | Model refuses | P:failed | P:isolated response branch | Declined request | Refusal category only |
| E16 incomplete | Token/response incomplete | P:failed, no partial plan | P:isolated branch | Incomplete output | Category/actual usage if present |
| E17 parser | Empty/invalid JSON | P:separate safe errors | P:unit / explicit Case B | No usable output | Parse category only |
| E18 Pydantic | Invalid structure/type/extra field | P:failed | P:explicit Case B | Invalid generated plan | Paths/types only |
| E19 integrity | Bad source/reference/cycle | P:reject full document | P:unit + API guard | Specific safe correction | No source text |
| E20 cancellation | Handler/process interrupted | P:interrupt/re-raise/lease | P:cancellation + restart | Interrupted/unknown | Run/state/time |
| E21 final auth | Current authority lost | P:no publication | P:real roles/seeded finalization | Permissions changed | Nonsecret IDs/category |
| E22 final lease | Late/terminal run attempts commit | P:CAS rejects | P:DB finalization race | Interrupted, no new plan | Lease-loss event |
| E23 DB | Pool/connect/statement/commit failure | P:rollback, unknown if unsaved | P:real unavailable DB | Persistence unavailable/unknown | Class/static reference |
| E24 constraints | Unique/FK race | P:rollback + named conflict | P:real PostgreSQL | Conflict/safe failure | Constraint allowlist only |
| E25 draft save | Stale/immutable document | P:409, preserve local | P:real PUT race | Local edits retained | Plan/revision IDs |
| E26 approval validation | Incomplete/open blocker | P:422, unchanged | P:actual approval route | Resolve listed blockers | Static reason/paths |
| E27 approval race | Old approved/stale revision | P:409, atomic | P:independent clients | Review exact version | Actor/version/rev |
| E28 browser/proxy | Offline/timeout/bad error body | P:unknown + GET only | P:actual offline/error UI | Check Status, retained draft | No credential-bearing trace |
| E29 reconciler | DB unavailable or shutdown | P:bounded retry on later tick/read | P:real state/lifespan | Honest active/unavailable | Static error, no resumed claim |
| E30 prompt resource | Missing packaged prompt | P:PM unavailable | P:resource failure unit | Setup error | Resource category, no user path |

## NOT in scope and deferred ledger

No TODOS.md is created under this one-file assignment. The entries below carry enough context for the parent to merge into the roadmap/TODO authority after the final gate. Deferred work is not authorized implementation.

| # | What / why / context | Pros / cons | Priority / effort / dependency |
|---|---|---|---|
| N1 | Architect, developer, QA or other agents; downstream execution/orchestration | Future end-to-end automation; new authority and failure surface now | P3; XL human/L assisted; separate owner stage authorization |
| N2 | GitHub OAuth/repository analysis/contributions or Skills installation | Real project integrations; credentials/external effects require separate scope | P3; XL/L; explicit later-stage security/product decisions |
| N3 | Model Hub/multiple providers/custom endpoints | Choice/fallback; unnecessary compatibility and secret/SSRF risk for one adapter | P3; L/M; demonstrated need and provider evaluations |
| N4 | Queue/Redis/Celery/LangGraph, resumable jobs, SSE/WebSockets | Durable/disconnected workflows; new distributed operations and billing semantics | P3; L/M; measured need beyond bounded local requests |
| N5 | Multiplayer presence/visual canvas/cloud sandbox | Collaboration/visualization; unrelated to approving one agreement | P3; XL/L; separate owner stage |
| N6 | Side-by-side semantic diff and cross-version story identity | Better comparison/change impact; requires semantics beyond stable local keys | P3; M/S; usable real version history first |
| N7 | External research/fact verification or automatic repository context | Better evidence breadth; untrusted retrieval/privacy/tool scope | P3; L/M; separate evidence/source authorization |
| N8 | Token pricing/cost estimates/confidence/progress percentages | Possible future budget UX; no authoritative current signal to support it | Skip now; future P3 S/S only with actual pricing/progress contract |
| N9 | Full append-only per-edit audit/event store and generalized retention/deletion | Stronger historical reconstruction; migration/privacy/operational scope | P3; L/M; owner retention/audit policy; retain existing stage records now |
| N10 | Public deployment, production security certification, SSO/MFA/recovery, mail delivery | Future operational readiness; cannot be inferred from local account/model proof | P3; XL/L; separate owner authorization and environments |
| N11 | Market analytics/automated quality score/large benchmark claims | Product learning at scale; premature without real local use and defined rubric | P3; M/S; actual user evidence; no fabricated success metric now |

Accepted completion work is X1–X5; rejected/deferred expansions are X6–X8/N1–N11. No deferred item is needed to complete the authorized single-agent workflow. The dream-state delta remains one trusted artifact before execution, rather than a universal agent platform.

## Stale diagram and documentation audit

The current architecture diagram is accurate for Stage 02 and becomes incomplete after PM routes/tables/provider lifecycle are implemented; extend it rather than delete the Stage 02 trust boundary. The Stage 03 generation diagram needs the explicit admission/session/lease/disconnect rules from this review. README/ROADMAP/AGENTS/VERIFICATION currently say Stage 03 is not authorized/started and describe uncommitted source; update those statements from the owner's current authority/checkpoint only when recording the actual implementation state. Preserve Stage 02 historical evidence separately. No other source ASCII diagram was identified as needing replacement in the files examined; do not claim a repository-wide visual audit.

## Implementation tasks

These are build-actionable proposed tasks, not executed work. Efforts are human-equivalent / assisted coding ranges and exclude owner credential setup, real model waits, and unresolved final-gate choices. P1 blocks Stage 03 acceptance; P2 should land with it. Exact new filenames/commands below are proposals for the engineering phase, not claims that those files already exist. All tasks run sequentially with respect to backend/browser ownership of `orba_test`.

- [ ] **T1 (P1, human 4–6h / assisted 1–2h)** — Freeze the versioned PM document, edit, provenance, confirmation and integrity contracts.
  - Surfaced by: CEO-01/03/04/05/13/24; Sections 0A, 1, 3–6.
  - Files/responsibilities: `apps/api/orba/pm_schemas.py` strict DTOs, numeric/total bounds, graph/source rules; proposed `tests/test_pm_contracts.py` isolated unit/error fixtures.
  - Verify: `uv run --directory apps/api pytest -q tests/test_pm_contracts.py`; generated schema inspected for the actual provider subset; no provider/actor authority in input.
- [ ] **T2 (P1, human 4–6h / assisted 1–2h)** — Add authoritative relational PM storage and a forward-only additive migration.
  - Surfaced by: CEO-11/12/20/22; Sections 1, 4, 7, 9.
  - Files/responsibilities: `orba/models.py` (or an explicitly imported PM module), new Alembic revision, `migrations/env.py` metadata import if necessary; named FK/check/unique/partial indexes and root-only JSONB.
  - Verify: real migration/preservation tests, `alembic upgrade head`, `alembic check`; inspect actual DB keys/order/no duplicate child tree.
- [ ] **T3 (P1, human 3–5h / assisted 1–2h)** — Implement the sole official SDK adapter and safe capability configuration.
  - Surfaced by: CEO-02/03/17/19; Sections 1–3, 9.
  - Files/responsibilities: `orba/config.py`, `pm_provider.py`, `orba/prompts/product_manager_v1.txt`, `.env.example`, `pyproject.toml`, `uv.lock`; SecretStr, explicit model, enable/limits, no retries/tools, actual metadata/nulls, named error translation.
  - Verify: isolated provider-contract/error tests, locked dependency checks, missing-config and real connection-failure commands; actual configured-schema compatibility in T13.
- [ ] **T4 (P1, human 2–3h / assisted 30–60m)** — Extract the private project authorizer and add thin authenticated PM read/write routes.
  - Surfaced by: CEO-06/11/21; Sections 1, 3, 5.
  - Files/responsibilities: `orba/main.py`, `security.py` or focused project helper, `pm.py`; reuse CSRF/Origin/role dependencies, project-first lookup, safe public DTOs and private 404.
  - Verify: real current-member/Viewer/foreign-project/exact-UUID/CSRF integration checks; original project route regressions remain intact.
- [ ] **T5 (P1, human 6–9h / assisted 2–3h)** — Implement bounded run reservation, admission, idempotency, provider phases and fenced finalization.
  - Surfaced by: CEO-07/08/09/10/11; Sections 1–4.
  - Files/responsibilities: `pm_service.py`, `pm.py`, `db.py` finite wait settings as needed; short sessions, canonical snapshot/hash, one call, deadline/cancellation, current-session/user/member recheck, atomic children+success, unknown persistence handling.
  - Verify: real PostgreSQL independent-client races, same-key replay/mismatch, account/global limits, permission loss, transaction rollback, terminal/late lease guards; no DB connection held during SDK await.
- [ ] **T6 (P1, human 4–6h / assisted 1–2h)** — Implement full-draft CAS, server-derived human provenance, immutable approval and version history.
  - Surfaced by: CEO-04/05/12/13; Sections 3–6.
  - Files/responsibilities: `pm_service.py`, `pm.py`, DTOs/models; root+children atomic save, stable local keys, actual editor metadata, exact approval actor/time, no open blocking confirmations, atomic supersession.
  - Verify: actual PUT/approval routes and fresh DB sessions; stale/concurrent save/approve; older draft versus newer draft/approved policy; approved content unchanged.
- [ ] **T7 (P1, human 2–4h / assisted 45–90m)** — Extend same-origin transport with PUT, typed safe PM errors and bounded PM-only time/body options.
  - Surfaced by: CEO-03/07/17; Sections 1, 2, 4.
  - Files/responsibilities: proxy `src/app/api/v1/[...path]/route.ts`, `src/lib/api.ts` and optional focused `pm-api.ts`; exact path/method matching, body enforcement, safe error metadata, no secret forwarding or POST retry.
  - Verify: strict typecheck/lint; real proxy 401/403/413/503 and long-request behavior; ordinary project requests retain existing limits/behavior.
- [ ] **T8 (P1, human 4–6h / assisted 1–2h)** — Build the Product Plan reader/generation/history/recovery feature inside project detail.
  - Surfaced by: CEO-01/08/16/23; Sections 0D, 4, 11.
  - Files/responsibilities: project detail `page.tsx`, new `product-plan.tsx`, typed client; source snapshot disclosure, actual metadata/nulls, approved/draft selection, real status, stable client key, GET recovery, obsolete-response guards.
  - Verify: real browser empty/config/failed/unknown/read-only/status/history/reload states; no call on mount/create and no fabricated plan/progress.
- [ ] **T9 (P1, human 5–8h / assisted 1.5–3h)** — Build the bounded native plan editor and exact approval interaction.
  - Surfaced by: CEO-04/05/12/13/16/23; Sections 3, 4, 11.
  - Files/responsibilities: `product-plan-editor.tsx` and small task-oriented child components, `globals.css`; overview/scope/requirements/epic/story/criteria controls, dependencies, confirmations, dirty/error state, role-aware exact-version approval and focus handling.
  - Verify: browser save failure/conflict preserves draft, add/remove reference validation, approved immutability, keyboard/theme/mobile maximum document, no overflow.
- [ ] **T10 (P1, human 2–4h / assisted 45–90m)** — Harden guarded test cleanup and prove populated Stage 02 preservation.
  - Surfaced by: CEO-20; system audit and Section 9.
  - Files/responsibilities: `scripts/prepare_tests.py`, `tests/conftest.py`, `tests/test_legacy.py` or `test_pm_migrations.py`; exact DB/role/loopback/test-port guard, PM FK cleanup, isolated-schema populated upgrade/repeated upgrade.
  - Verify: invalid cleanup target rejects before mutation; original populated field values/ownership/sessions retained; real test PostgreSQL only.
- [ ] **T11 (P1, human 5–8h / assisted 1.5–3h)** — Implement the exact 20-case backend map plus meaningful concurrency, security and negative-path coverage.
  - Surfaced by: CEO-14; Section 6 and E01–E30.
  - Files/responsibilities: proposed `test_pm_runs.py`, `test_pm_plans.py`, `test_pm_permissions.py`, `test_pm_errors.py`; declare any unit/error doubles and the explicit Case B exception, keep production free of fake switches.
  - Verify: `uv run --directory apps/api pytest -q`; actual counts/no skips/xfail; separate session DB assertions; retain 44 baseline cases and causes of any genuine failure.
- [ ] **T12 (P1, human 3–5h / assisted 1–2h)** — Add deterministic real browser PM states and retain existing responsive/project/team journeys.
  - Surfaced by: CEO-15/16/23; Sections 4, 6, 11.
  - Files/responsibilities: `apps/web/tests/product-plans.spec.ts`, helpers, existing specs/config only as needed; no canned API interception or hidden paid generation in ordinary fixtures.
  - Verify: `pnpm test:e2e` after backend suite ends; actual Chromium desktop/mobile/tablet counts and accessibility/negative outcomes.
- [ ] **T13 (P1, human 2–4h / assisted 45–90m plus live waits)** — Provide and execute a separate real model API verification command.
  - Surfaced by: CEO-02/14/15; Section 6.
  - Files/responsibilities: proposed `apps/api/scripts/verify_pm_live.py`, explicit live test support/evidence schema; real configured provider, compact habit-tracker brief, full validation and fresh DB/API retrieval, sanitized returned model/response/usage/count evidence, nonzero BLOCKED when unavailable.
  - Verify: proposed `uv run --directory apps/api python -m scripts.verify_pm_live`; inspect actual output/exit and human rubric; no retry loop or fabricated metadata.
- [ ] **T14 (P1, human 3–5h / assisted 1–2h plus live waits)** — Provide and execute a separately identified live-model browser journey.
  - Surfaced by: CEO-15; Sections 6, 11.
  - Files/responsibilities: proposed `apps/web/playwright.live.config.ts`, `tests-live/product-plan-live.spec.ts`, package script; actual click/generate/edit/save/reload/approve/reload plus unrelated exact-ID denial, independent of core regression discovery.
  - Verify: explicit live browser command; at least one actual new model generation in that browser flow; sanitized evidence, no auth trace, actual provider/account scope stated.
- [ ] **T15 (P1/P2, human 3–5h / assisted 1–2h)** — Complete lifecycle operations, integrated verification, truthful docs and the explicit wrong-success experiment.
  - Surfaced by: CEO-17/18/19/20/24; Sections 2, 6–10.
  - Files/responsibilities: app lifespan/reconciler/readiness, `scripts/verify.ps1`, `tests/experiments/pm_wrong_success_experiment.py`, README/AGENTS/ARCHITECTURE/ROADMAP/STAGE03_TEST_PLAN/VERIFICATION and sanitized evidence; bounded tasks/SDK shutdown, enable/disable runbook, no auto-paid readiness, nonzero live blocker.
  - Verify: `pwsh -File scripts/verify.ps1`; separately invoke the incorrect-success experiment and preserve its actual exit 1, never as a passing suite; lint, format, strict typecheck, production build, real API/browser/DB evidence, then stop at Stage 03.

No additional task is generated merely to introduce a framework, test low-impact decoration, or simulate a success. T15's operations and verification substeps are explicitly named and may be split for execution tracking without changing scope. Markdown is the task authority for this delegated artifact; the parent can serialize it for autoplan aggregation without this reviewer violating the one-file write boundary.

## Incremental decision audit: deep review resolutions

| Decision | Classification | Principle | Resolution / rejected path |
|---|---|---|---|
| C-D11 | Mechanical | P1/P5 | Strict complete numeric/total bounds and schema_version before provider/UI; reject arbitrary-text salvage or truncation. |
| C-D12 | Mechanical | P1/P4 | Derive/enforce project/workspace ownership; root JSONB excludes relational tree; reject competing representations. |
| C-D13 | Mechanical | P1 | Close initial identity DB transaction before SDK await; independent finalization session; reject lock/connection across provider latency. |
| C-D14 / C03 | Taste | P3/P5 | Disconnect is best-effort continuation, actual cancellation interrupts; reject guaranteed cancel/resume claims. |
| C-D15 / C04 | Taste | P2 | Add two global active slots and finite actor/global rolling admission; default numbers go to final gate. |
| C-D16 | Mechanical | P1 | Provider timeout is failed; expired/cancelled lease is interrupted; terminal-state/deadline CAS rejects late success. |
| C-D17 | Mechanical | P1 | Recheck original current session/user/member before publish; reject cached identity as final authority. |
| C-D18 | Mechanical | P1/P5 | Canonical immutable snapshot/hash binds replay; same key never calls again, even after failure; reject rehashing changed context on replay. |
| C-D19 | Mechanical | P1 | Save/approve exact revision atomically; reject max-draft auto-approval, silent autosave, or dropped dangling references. |
| C-D20 | Mechanical | P4/P5 | One structural/integrity validator plus separate source/role authority; reject duplicated route/provider/editor business validation. |
| C-D21 | Mechanical | P1 | Preserve typed run/error references through proxy/client; unknown outcome gets GET recovery, never automatic POST retry. |
| C-D22 | Mechanical | P1 | Map all 20 owner cases; identify unit/error doubles and explicit malformed Case B; reject double-backed evidence as live success. |
| C-D23 | Mechanical | P1/P6 | Two separately invoked real generation flows (API and browser), live missing config nonzero BLOCKED; retain core independent checks. |
| C-D24 | Mechanical | P2/P5 | Use run history/static events/read-only operator queries as local dashboard; reject telemetry service/admin UI expansion. |
| C-D25 | Mechanical | P2 | Add nonsecret PM enable/disable capability; keep core startup/readiness useful without credentials; no readiness model call. |
| C-D26 | Mechanical | P1 | Forward-compatible additive rollout with preserved PM tables on rollback; reject dev reset/downgrade. |
| C-D27 | Mechanical | P1 | Strengthen exact test target before extended cleanup; keep API/browser test DB ownership sequential. |
| C-D28 | Mechanical | P1/P5 | Show approved agreement separately from drafts, visible confirmation/source/dirty/recovery states; reject generic agent dashboard/progress theater. |
| C-D29 | Mechanical | P3 | Keep four explicit debts: synchronous interruption, history growth, bounded quality sample, no full per-edit event log; no hidden Stage 04 work. |
| C-D30 | Mechanical | Explicit | Write only this artifact, no global/JSONL/TODOS/product/main-plan edits; parent owns voices and phase transition. |

There are 30 decision rows total across the two audit tables, with four distinct taste choices C01–C04 (C-D09 reinforces C02 rather than creating a fifth choice). No two-model User Challenge is asserted. These recommendations are auto-decided for review continuity and await the parent's final gate where required; they are not an owner approval record.

## Document quality assessment and adversarial self-check

This is a self-assessment of the proposed review/specification after the fixes above, not an independent model consensus or test score. A separate child/CLI adversarial loop was not run because the parent explicitly owns the next voice. The parent should reconcile its findings before claiming that independent review occurred. No claim of “survived N rounds” is made.

| Dimension | Score / disposition | Concrete assessment |
|---|---|---|
| Completeness | 9/10, PASS for review coverage | All Step 0 items, eleven sections, 20 owner scenarios, error/interaction/failure registries, rollback and tasks are present. Product remains unimplemented/unverified. |
| Consistency | 9/10, PASS with pending gate choices | Canonical plan tree, exact revision authority, provider failure versus interruption, and real versus double-backed evidence are consistent. Parent must adopt/dispose C01–C04 centrally. |
| Clarity | 9/10, PASS for handoff | Explicit limits, state transitions, roles, error categories, file responsibilities and test headers replace “handle/bounded” placeholders. Engineering still validates SDK-specific types and timing feasibility. |
| Scope | 9/10, PASS | One PM agent/local workflow only; accepted touches fit existing feature files; eleven exclusions/deferred items are explicit. No Stage 04, public deployment, new agent framework or external message. |
| Feasibility | 8/10, CONCERN | Current architecture supports the plan, but actual key/model access, strict schema compatibility, full timeout inequality, max-size UI, and two live calls remain unproven. Code cannot remove this runtime dependency. |

Overall document score: **8.8/10** (simple mean). This is not a stage verdict or a quantified product-quality claim. The self-check caught and resolved the ambiguity around context replay, latest-draft versus current-approved ordering, human source authority, request DB session lifetime, controlled-double evidence, and unsaved edits; these are now explicit recommendations. Actual independent concerns from the parent's next CLI pass remain pending. No global durable learning was written under the one-file assignment.

## Completion summary

| Required output | Result |
|---|---|
| Mode selected | SELECTIVE EXPANSION, approach B proposed |
| System audit | Actual source and Git inspection; one checkpoint/no remote/no hotspot history; current timeout/auth/session/test seams mapped |
| Step 0 | A–F complete; eight premise assessments, three alternatives, eight cherry-picks, temporal interrogation |
| Section 1 — Architecture | Five material findings; dependency/full system/state diagrams; caps, admission and rollback posture |
| Section 2 — Errors | 30 named error paths, all assigned proposed rescue/user/test actions; none executed as PM evidence |
| Section 3 — Security | Four high-priority authority/admission/ownership findings; ten threat rows; no production certification |
| Section 4 — Data/UX | All generation/read/edit/approve/reconcile flows and shadow paths; 24 interaction edges, handling specified |
| Section 5 — Quality | Two organization/trajectory findings; concrete DRY seams and complexity cuts |
| Section 6 — Tests | New-work diagram; exact 20-case map; separate API/browser live proof and two named negatives; live scope currently blocked |
| Section 7 — Performance | One resource-budget finding; no invented p99; bounded tree/query/pool/concurrency checks |
| Section 8 — Observability | One operational/runbook gap; six local signals; no new dashboard service |
| Section 9 — Deployment | Two rollout/test-isolation findings; local forward rollback and startup/readiness/disable plan |
| Section 10 — Future | Overall reversibility 3/5; four explicit debt items; schema/version trajectory without Stage 04 |
| Section 11 — Design | Two interaction/design findings; six-stage flow and five feature state rows; accessibility/mobile/theme obligations |
| NOT in scope | Written, eleven entries with why/pros/cons/effort/dependency |
| What already exists | Nine sub-problems mapped to concrete reuse; no parallel auth/provider platform |
| Dream state delta | Current → one trusted artifact → later governed workflow, later work unauthorized |
| Error/rescue registry | 30 paths across API/provider/DB/UI/maintenance; zero unassigned actions; all PM execution unverified |
| Failure modes registry | 30 planned entries, no designed silent fallback; no actual passing PM result claimed |
| TODOS updates | Eleven proposals recorded here; no third-file/global mutation |
| Scope proposals | Eight evaluated; five accepted as feature completion, two deferred, one rejected |
| CEO plan | This artifact written; main plan not edited by this reviewer |
| Outside voice | This Codex-family fresh-context voice completed; parent CLI voice pending; no Claude/cross-model consensus |
| Lake score | Complete option selected for all26 mechanical decisions; four taste rows represent four distinct final-gate choices. C-D09 is implementation of C02, not another taste choice; no claim of owner approval |
| Diagrams produced | Dream state; dependency/system; run/plan/confirmation states; error rescue; generation/read/edit/approve/reconcile flows; test graph; rollout/rollback; UX storyboard |
| Stale diagrams/docs | Stage 02 architecture becomes incomplete after PM; proposed generation diagram needs refinements; stale authorization/checkpoint prose identified |
| Tasks | Fifteen build-actionable tasks with files, responsibilities, effort and verification |
| Decisions | Thirty audit rows; four distinct taste choices; zero asserted two-model User Challenges |
| Document quality | Five dimensions, mean 8.8/10; self-assessed, runtime feasibility concerns explicit |

### Pending final-gate choices and blockers

- **C01:** retain proposed relational children/root JSONB rather than a whole-document JSONB plan.
- **C02:** require human resolution or explicit reasoned deferral of blocking confirmations before exact approval.
- **C03:** browser disconnect permits best-effort server completion; actual task/process cancellation interrupts, with no provider-charge cancellation guarantee.
- **C04:** approve finite generation admission defaults (proposed two active globally, one/project, 5/account/hour and 20/global/hour), with configurable stricter limits.
- **Live blocker:** actual `ORBA_PM_API_KEY`/model capability is unavailable at intake. The parent must record actual configuration/provider results later; neither this review nor any unit/double result can produce VERIFIED.
- **Review boundary:** the parent's second CLI voice and Design/DX/Engineering phases are pending. This file completes only the requested CEO voice.

**CEO voice complete.** Four final-gate taste choices and the runtime/live-evidence blocker are handed to the parent. No subsequent phase, product implementation, provider call, or Stage 04 work was started here.
