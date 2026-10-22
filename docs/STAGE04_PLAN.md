<!-- /autoplan restore point: C:/Users/vaish/.gstack/projects/OBRA/stage04/20261021-implementation/autoplan-restore.md -->
# Stage04 implementation plan: Architect Agent and task dependencies

Owner-authorized 2026-10-21. Baseline commit: `1aeb882cf9e788948df5ca5eac52e2a682a1f487`.
Baseline Stage03 source: `661f2828f7adbdc368a31616280ebec5d27048b2dc6f9feb1ecada06505b282d`.
This is an implementation/review plan, not evidence that Stage04 exists or works.
No paid generation, commit, push, repository execution agent, or Stage05 is authorized.

## Objective and scope

Turn one authoritative, approved, same-project Product Plan into a reviewable technical
proposal, relational engineering tasks, a validated dependency DAG and explicit human
approval. Preserve all Stage01-03 auth, project, workspace, password and PM guarantees.
The task graph is a planning model: no task is executed or marked code/test/deployment
complete. Gate A must actually run; Stage04 remains PARTIAL until its own authorized
real Architect Gate B succeeds on the same relevant source/configuration fingerprint.

## Existing implementation to reuse

| Need | Existing authority |
|---|---|
| Identity, CSRF, Origin and tenant checks | `security.py`, `auth.py`, `workspaces.py` |
| Short locking phases and original-session checks | `pm_service.phase/lock_project/check_session/db_now` |
| Approved source and immutable version history | `ProductPlan`, `read_document`, `content_hash`, PM approval |
| Official bounded SDK transport and safe errors | `pm_provider.py`, `pm_models_policy.py`, `pm_errors.py` |
| Runtime validation and safe Settings errors | `config.py`, readiness helpers |
| UI tokens, session boundary, request errors | `globals.css`, `session.tsx`, `api.ts`, Product Plan patterns |
| Real integration verification | guarded PostgreSQL fixtures and `scripts.verification` |

Do not copy the entire PM service or adapter. Extract only the small SDK request core
needed by both planning agents; retain PM behavior and regression tests. Architect
transactions remain explicit and separate because their source, DAG and coverage
publication rules differ. No generic orchestrator or job framework is introduced.

## Architecture and persistence

```text
Authenticated project -> Product Plan (exact approved version/revision/hash)
                             |
                  explicit Generate Architecture
                             v
Next same-origin proxy -> FastAPI authorization + CSRF
  -> lock workspace/project + original session + idempotency + bounded admission
  -> persist pending -> persist running -> release every DB transaction
  -> ONE official Gemini request, tools off, retries 0, bounded bytes/time/output
  -> strict Pydantic -> source references -> component references -> task DAG
  -> recheck original authority/deadline/executor -> atomic relational publication
  -> persisted draft architecture + tasks + dependencies + traces + succeeded run
                             |
            review/edit -> exact revision save -> explicit Owner/Admin approval
                             |
       immutable approved architecture -> future Stage05 (NOT implemented here)
```

Additive Alembic migration creates ArchitectRun, ArchitectureVersion,
ArchitectureComponent, EngineeringTask, TaskDependency and RequirementTrace tables.
Use timezone-aware UTC timestamps, FKs, unique version/request/node keys, explicit
run-state checks and partial unique active-run/current-approved indexes. Composite
FKs bind every dependency to the same architecture/project and every story trace to
the exact source plan. Database self-edge and duplicate-edge constraints complement
the complete server-side DAG validator. No original row or migration is reset.

One root architecture JSONB stores overview, technology, proposed database/API,
security/deployment, uncertainty and coverage exceptions. Components/tasks/edges/
story traces are authoritative relational rows, excluded from the root JSON copy.
Task acceptance criteria and source requirement/criterion keys are bounded task
fields; relational traces bind actual persisted source story UUIDs. Assembly is
bounded bulk queries, with stable node UUIDs retained when stable keys survive edits.

ArchitectureVersion records source plan FK, version, revision and content hash;
ArchitectRun retains the exact authoritative source snapshot, input/request hashes,
prompt version/hash, requested/returned model, genuine response IDs/usage, timing,
deadline/executor/session and safe failure diagnostics. A newer PRD cannot rewrite
an older source. API/UI explicitly report whether a source is still current.

## Authoritative output and source validation

Versioned strict Pydantic architecture contract contains title, summary, style,
goals, constraints, assumptions, non-goals; proposed technologies with reasoning,
alternatives/tradeoffs; keyed components and relationships; logical database
entities/fields/relationships/constraints/indexes/ownership/privacy; proposed API
methods/routes/contracts/auth/errors; trust boundaries/auth/authorization/data/
secrets/threats; deployment assumptions/operations; risks/open decisions; tasks and
coverage exceptions. Unknown fields, wrong types, duplicate keys, dangling references,
invalid Unicode, oversized input/output, malformed JSON and partial SDK output fail.

Tasks contain stable key, title, description, scope, deliverables, observable criteria,
priority/category, optional labeled complexity estimate, component/story/requirement/
criterion references and prerequisite keys. Tasks expose only planning states. Generated
decisions remain proposals, not installed or verified technologies. Bounded collection
sizes prevent hundreds of tasks and unbounded graph traversal; small live samples are
instructed to use a proportional compact design without removing required sections.

Criterion references must belong to the exact source stories referenced by that task.
Preserve source-story prerequisite meaning: a task for a dependent story must also
cover its prerequisite story and include every other contributing prerequisite task
as an ancestor, or have paths from all such prerequisite tasks; otherwise record a
coverage gap requiring an exact, reasoned human exception before approval. Coverage
is structural linkage, not semantic adequacy or proof that any requirement was built.
Server-owned source context retains original suggested/assumed provenance and deferred
confirmations/risks/questions independently of generated or edited architecture text.
An empty model uncertainty list can never erase those inherited obligations.

Current source means the current **approved** PRD identity/version/revision/hash;
creating a newer unapproved PRD draft does not make that agreement stale. A newly
approved PRD does. Publication and architecture approval recheck the same source.
An older architecture draft cannot supersede a newer approval. Exact already-approved
confirmation may be idempotent; no historical content or actor/time is restamped.

Only persisted ProductPlan state `approved` can initiate a run. The client sends source
ID/version/revision, never an authoritative source body. Read/validate the saved PRD
and its hash under the project/workspace lock. Source stories and criteria are resolved
from the exact saved plan, not arbitrary project UUIDs or model-created identities.

## Dependency and coverage engine

Convention: **A -> B means B depends on A**. Input `B.dependencies=[A]` maps to this
same convention in SQL, API, SVG arrows, detail panels and tests. Validate missing,
duplicate and self dependencies before deterministic Kahn topological ordering using
display order then stable key as the tie-break. Reject any unconsumed cycle. Impact
analysis traverses transitive dependents in deterministic order. All tasks are
unexecuted: a root has no unmet planning prerequisites, and every nonroot remains
blocked by its prerequisites. Needs-clarification takes precedence. This does not
infer code completion merely because an upstream node is dependency-ready.

Every task/component reference must exist in the source or architecture. Coverage
reports covered/uncovered source requirements, stories and criteria, tasks lacking
clear source links and open decisions. A draft may expose missing coverage for human
repair; approval requires coverage or an exact documented exception explicitly
acknowledged by the human approver. Model text cannot record human acceptance.
Approval also rejects a stale source, invalid/damaged DAG/document or stale revision.

## Versioning, authorization and failure integrity

Member/Admin/Owner may generate and edit drafts; Viewer may only inspect authorized
records. Owner/Admin may approve the exact version/revision after review. Every read
checks current workspace membership. Every write locks the workspace/project before
checking the role and current session. Unrelated resource UUIDs uniformly return404.
All writes use existing Origin+CSRF protections. No frontend button grants authority.

Approved/superseded versions are immutable. A human draft-copy action creates a new
version with its source and copy relationship preserved; generation never overwrites
an existing approval. Draft PUT saves the entire validated graph under an expected
revision and updates only that draft atomically. Invalid edits leave the saved graph
and the browser's local input intact. Approval records exact actor/time/revision and
only supersedes the previous approval within the same project.

Persist pending and running before dispatch. No DB transaction remains open during
the model request. Global admission lock plus per-project active uniqueness and
actor/project request UUID prevent duplicate calls. Exact replay returns the existing
record; changed input with the same UUID conflicts. Preserve the originating session
and fence publication by executor/status/deadline. Logout or role/source changes cannot
authorize publication using a replacement login. Reconcile stale runs honestly as
interrupted. Commit uncertainty returns an unknown outcome requiring GET, never an
automatic POST retry or overwrite of possible success. Safe diagnostics retain error
class, stage, actual HTTP status and elapsed timings without secrets/private bodies.

The existing planning concurrency/account/global limits count PM and Architect runs
together under the same PostgreSQL admission lock. Retain existing PM environment
names for compatibility; do not create a second independent budget that permits two
simultaneous paid requests while the configured total is one. Test both directions
of PM/Architect competition and the combined hourly counters.

## Provider configuration

Use the existing official Google SDK, reviewed Gemini model policy and transport.
Architect-specific environment settings explicitly select model/thinking/time/output/
input bounds; reuse the existing server credential when no separate Architect key is
provided. Missing model is a supported setup state, never an automatic fallback.
Recommended future bounded live profile: gemini-3.6-flash/minimal, one worker, zero
retries and one generation, with explicit documented deadlines/output budget. Do not
edit the owner's ignored3.8 PM configuration or infer runtime access from Codex.
Provider readiness is non-generative and never proves live Architect success.

The exact settings are `ORBA_ARCHITECT_API_KEY`, `ORBA_ARCHITECT_MODEL`,
`ORBA_ARCHITECT_THINKING_LEVEL`, `ORBA_ARCHITECT_TIMEOUT_SECONDS`,
`ORBA_ARCHITECT_MAX_OUTPUT_TOKENS` and `ORBA_ARCHITECT_MAX_INPUT_BYTES`.
An absent/empty Architect credential reuses the existing resolved server credential;
model selection remains explicit. Gate A blanks every key alias and both model choices.
Extend the PM-only proxy, streamed body limit and unknown-outcome request policies to
Architect paths without lengthening ordinary API deadlines.

## User experience and interaction states

All multi-query artifact, task, graph and coverage reads hold a shared root lock and
return the same revision/hash, preventing a torn graph during an overlapping edit.
Exact own request replay precedes current-source/configuration/input-cap checks.
An edgeless DAG is valid; verification must not require positive dependency counts
unless the particular authored source intentionally requires a fork/join dependency.

Keep the current project page and Product Plan section. Add Architecture and Task
Graph views inside the same workspace, using semantic tokens and existing controls.
Architecture shows exact source, source currency, real runs, proposal sections,
version/revision/history, draft editing and explicit approval. The task graph uses
accessible native controls, a deterministic SVG dependency diagram and synchronized
list/detail panel; no new graph package is needed for this bounded planning graph.
Keyboard users and narrow screens can perform all dependency edits in the list.
Nodes show category/priority, coverage and prerequisite explanations, never progress.

```text
No approved PRD -> actionable empty state -> Product Plan review/approval
Approved PRD -> choose exact source + optional constraints -> explicit Generate
  -> generating (truthful, no invented steps) -> saved draft -> review/edit/save
  -> graph/coverage validation -> human approval -> immutable approved version
  -> provider/schema/network failure -> retain source/constraints/old approval
       -> GET status -> confirmed own terminal run -> explicit fresh-UUID retry
```

Unknown outcomes retain only nonsecret account/project/request UUIDs in sessionStorage,
never briefs or credentials. Disable in-flight mutations synchronously to avoid
double-click dispatch. Clear protected state on account/workspace/project changes.
Draft text stays on validation/network/conflict errors. Show latest saved revision
without silently overwriting local input. Newer PRD sources get a clear stale-source
notice. Generated SQL/routes are labeled proposed and never executed.

## Incremental implementation and actual verification tasks

- [x] Confirm committed Stage03, source/profile evidence and clean intake; preserve hashes.
- [x] Execute existing deterministic baseline: native0, all14commands0;285backend/60core/33controlled browser cases; receipt `stage031/20261021T101616Z-A-ea3efcdb`.
- [ ] Complete sequential CEO -> Design -> DX -> Eng review artifacts and decisions.
- [ ] Implement schemas, DAG and coverage; run focused meaningful unit tests.
- [ ] Add models/migration; verify upgrade, preservation and schema drift on real test PG.
- [ ] Add shared provider request, prompt and explicit configuration; run isolated adapter tests.
- [ ] Implement fenced lifecycle, persistence/versioning and authorized APIs; run real PG tests.
- [ ] Implement project Architecture/Task Graph UI and draft/approval editing.
- [ ] Add real-service controlled-provider browser coverage across desktop/mobile/tablet.
- [ ] Execute isolated false-success assertion; require an actual nonzero exit separately.
- [ ] Run complete Gate A, fix real defects, preserve every earlier failed receipt.
- [ ] Prepare one-request Architect Gate B and fail-closed Stage04 Gate C; no paid dispatch.
- [ ] Record source fingerprint, exact counts/commands/exits, limits and A/B/C verdict.

No test removes baseline identities or substitutes SQLite/mock auth. Real PostgreSQL
integration tests cover approved-source requirements, version/revision binding,
schema/graph failures, relational persistence/atomic rollback, immutable approval,
viewer and tenant denials, cycle/self/missing/duplicate/cross-project edges,
deterministic order/readiness/impact/coverage, stale edits, concurrent idempotency,
503/504 failures, prior approval preservation and original-session revocation.
Browser tests retain the existing60 core +33 controlled cases and add the complete
new controlled flow, accessible list/diagram, invalid-edge rollback, edit/reload,
approval, stale input, failure/retry and outsider denial. Doubles replace only the
provider dependency in the guarded test factory and never count as live evidence.

Gate A remains `pwsh -NoProfile -File scripts/verify.ps1`; extend the existing
pipeline rather than bypassing it. Keep old Stage03 receipts immutable and stage-
bind new evidence so old B cannot certify Stage04. Architect live Gate B must refuse
without fresh explicit opt-in/current A. It uses one preexisting approved real source
and one generation, then reuses that architecture for browser/SQL/edit/approval/DAG/
coverage/isolation checks. Capture actual metadata only. Gate C is PARTIAL if B is
absent/stale/failed/controlled. No skipped/xfail/retried case can become a passing gate.

## Not in scope

No task scheduling/execution, coding or QA agent, repository changes by an agent,
LangGraph/Redis/Celery orchestrator, remote sandbox, external tool execution, Skills,
GitHub automation, full Model Hub, realtime collaboration or advanced canvas.
Existing TODOS describe those future directions; Stage04 adds only the explicitly
authorized planning engine. Public deployment, global tooling repair, further paid
calls and Stage05 remain unauthorized.

## CEO review completion

Full primary review: [scope, eleven sections, error/failure registries, state diagrams
and alternatives](reviews/STAGE04_CEO.md). Independent same-family voice:
`C:/Users/vaish/.gstack/projects/OBRA/stage04/20261021-implementation/ceo-independent.md`.
Three high findings were incorporated into the required design: shared admission,
server-preserved uncertainty/provenance and exact lineage/source ordering. Medium
clarifications define current-approved source/monotonic approval and non-paid source
setup for B after guarded test resets. These are design fixes, not executed test claims.

| Dimension | Primary assessment | Independent assessment | External CLI |
|---|---|---|---|
| Premises | Baseline evidenced; Architect quality unverified | Same distinction | Unavailable |
| User problem | Reviewable technical handoff | Correct problem | Unavailable |
| Scope | Full bounded Stage04 | Appropriate with integrity additions | Unavailable |
| Alternatives | Relational engine; no scheduler | Selected approach strongest | Unavailable |
| Product risk | Proposal/linked coverage only | Same false-authority risk | Unavailable |
| Trajectory | Stable source/task authority for future use | Sound if versioned | Unavailable |

Six dimensions assessed by both in-host perspectives. External cross-model consensus
is N/A, not six falsely confirmed external comparisons. No owner-scope challenge or
unapproved expansion arose. Pass the amended plan to Design, then DX, then Eng last.

## Decision audit trail

| ID | Phase | Decision | Classification | Principle | Reason | Rejected alternative |
|---|---|---|---|---|---|---|
| 1 | Intake | Preserve checkpoint/source/receipts and credential bytes before changes | Mechanical | Explicit | Establish actual baseline and audit | Blind scaffolding or reset |
| 2 | Intake | Shared SDK core and existing auth/short transaction primitives | Mechanical | DRY | Preserve proven failure handling without generic orchestration | Copying whole PM implementation |
| 3 | Intake | Native SVG plus synchronized accessible task list | Mechanical | Pragmatic | Bounded graph needs no new package; every edit has a native control | Large graph/canvas framework |
| 4 | Intake | Approval checks DAG, exact source/revision and human exception acknowledgment | Mechanical | Completeness | Prevent false completeness and stale approval | Visual-only validation |
| 5 | CEO | Share admission counters across both planning run tables | Mechanical | Completeness | A shared mutex without shared counts does not bound concurrent paid work | Independent per-agent counters |
| 6 | CEO | Preserve source uncertainty server-side and validate criterion parentage/source dependency coverage | Mechanical | Explicit | Generated references cannot erase deferred source obligations or reverse prerequisites | Flat key existence alone |
| 7 | CEO | Bind currency to current approved PRD and preserve monotonic architecture approval | Mechanical | Explicit | New drafts do not erase agreements; old drafts cannot overwrite newer approvals | Latest-version or last-response wins |
| 8 | CEO | Live B setup uses a labeled human-authored, persisted and explicitly approved source, with zero PM generation | Mechanical | Completeness | Reproduce from empty guarded test DB without a second paid request; never claim authored input is PM model evidence | Depending on test-reset live rows |
| 9 | Design | One mounted project-scoped architecture draft shared by both views; Save/Discard/Cancel for deliberate navigation | Mechanical | Completeness | View changes cannot lose graph edits; auth changes still clear immediately | Unmounting tab-local editors |
| 10 | Design | Source/state/review summary before proposal; exact exceptions and blocking decisions need saved-revision human acknowledgment | Mechanical | Explicit | Review obligations must be visible before approval | Generic success badges and hidden blockers |
| 11 | Design | Native task list/detail and single prerequisite selector; optional overview diagram on narrow screens | Mechanical | Pragmatic | Every action works without dragging or modifier keys | SVG-only actions/multi-select |
| 12 | Design | Field-linked focused errors; local/remote conflict comparison; explicit old-source recovery | Mechanical | Completeness | Preserve inputs without suggesting validation or rebase occurred | Silent overwrite or context-free alert |

## Design review completion

[Seven-dimension design contract](reviews/STAGE04_DESIGN.md) specifies local navigation,
shared draft lifetime, source/review hierarchy, complete state matrix, story/criteria
obligation review, native graph controls, narrow/keyboard access and targeted errors.
It incorporates the independent same-family voice's2high/4medium findings without
changing product scope. A labeled authored HTML sketch was locally rendered and
inspected at desktop light/mobile dark; it is not real Architect output or app proof.
External visual/model helpers are unavailable; no paid substitute was called. Overall
plan specificity7 ->8.8/10; runtime visual/accessibility verification is still required.

## DX review completion

[Eight-dimension DX review](reviews/STAGE04_DX.md) defines incremental setup, safe
configuration, actionable source/graph/provider errors, additive migration and exact
stage-bound gates. Independent review identified credential blanking, PM-only path
policies and live source preparation gaps; all are included above. Full old test
identities remain mandatory. Live source setup is human-authored and approved through
the real application, with no PM model request. No broader ecosystem work is added.
Pass the amended plan to Engineering last.

## Engineering review completion

[Engineering review and coverage diagram](reviews/STAGE04_ENG.md) closes the sequence.
The independent in-host review added shared-root read consistency, all-contributor
source prerequisite coverage, replay-before-new-policy ordering and correct treatment
of edgeless DAGs. These four integrity fixes are incorporated in this contract. The
external test-plan artifact and14 aggregated review tasks are saved under
`C:/Users/vaish/.gstack/projects/OBRA/`. No cross-model consensus is claimed.

The owner has explicitly authorized full Stage04 implementation and deterministic
verification. There is no new scope challenge or permission-dependent product choice;
proceed incrementally. Paid Architect generation, commits/pushes and Stage05 remain
outside that authorization. No skill-generated final gate supersedes these limits.


## Deterministic implementation closure

Implemented and verified incrementally, followed by final Gate A: 386 backend, 60 core browser, 33 PM controlled browser and 33 Architect controlled browser; all 15 commands exited 0, no skips/retries. Source `07bf0deb6c2a0cdaed19a4441619404fbda0f57674a0db9171cb3ea47628eab7`. The prior complete A remains preserved after subsequent modal/verifier repairs. Own live Architect B is prepared, not executed; Stage04 is PARTIAL. [Actual A-K report](VERIFICATION_STAGE04.md). No paid generation, commit/push or Stage05.
