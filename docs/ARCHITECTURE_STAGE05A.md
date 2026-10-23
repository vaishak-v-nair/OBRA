# Stage05A: persistent orchestration foundation

This is a deterministic local control plane. It does not execute engineering tasks,
call a model, register an executor, schedule work, perform a handoff or certify
software delivery. Approved architecture remains a proposal. Root-task eligibility
does not establish that code was written or tested.

```text
Approved PRD -> approved Architecture + task DAG
  -> authorized explicit Create orchestration run
  -> current-source/schema/approval/coverage/DAG validation
  -> atomic canonical snapshot + relational tasks + edges + events
  -> awaiting executor (no implementation or completion evidence)

Browser -> existing Next same-origin proxy -> FastAPI
  -> existing Origin/CSRF/session/workspace/role checks -> PostgreSQL
```

## Source agreement and checksum

Creation requires architecture ID, exact version/revision and request UUID. The
server fetches the authoritative approved same-project architecture, verifies its
content hash, exact approved PRD ID/version/revision/hash, current approved PRD
state, strict Pydantic document, requirement coverage, graph and saved-revision
human approval dispositions. Owner/Admin approval metadata must be intact. A
draft, superseded, stale, corrupt or foreign source cannot initialize a run.

The existing workspace/project locks serialize source agreement changes against
creation. The original session is checked after locking and before commit. No
transaction spans a model request because this flow makes none.

The immutable source_snapshot includes the complete architecture and PRD documents,
source approval actor/time/dispositions, source task UUIDs with ordered definitions,
source dependency UUIDs/edges and requirement-trace UUID/story/target references.
It preserves assumptions, criteria and uncertainty instead of copying only titles.

Hash contract `orba-orchestration-canonical-json-v1`: SHA-256 over UTF-8 JSON with
sorted object keys, `separators=(",", ":")`, `ensure_ascii=False`, retaining array
order. No run UUID, creating-user identity or run timestamp is included, so the
same exact source produces the same snapshot hash across deliberate new runs.
Source approval identity and time are part of the snapshot.

Relational tasks/edges are materialized query projections of that snapshot. On
detail/graph reads, reassemble and compare definitions, source task IDs, ordered
edges, checksum, bindings, eligibility/execution states and lifecycle ledger.
Integrity failure is409; no graph or execution success is fabricated. Future
source approval changes only source_current=false on historical run reads.
It never rebases, updates or deletes the snapshot.

## Tables and additive migration

Migration `f9e997d59bb4`, after Stage04 `7dd7671f9417`, adds:

| Table | Responsibility and important constraints |
|---|---|
| orchestration_runs | Exact workspace/project/architecture/PRD binding; source hashes, canonical snapshot/checksum, creator/request UUID/hash, lifecycle/revision/event counter, aware timestamps/cancellation. Unique(project,creator,request). Composite same-project source FKs. |
| orchestration_tasks | Run-owned source engineering-task UUID/key, ordered definition snapshot (title, description, scope, deliverables, criteria, category, priority and trace refs), eligibility separate from execution status. Unique run/key and run/source. Composite same-run/project/architecture FKs. |
| orchestration_dependencies | Source edge UUID; prerequisite -> dependent task UUIDs. Composite same-run/project FKs, unique edge, no self edge. |
| orchestration_events | UUID, run/task, unique run-local sequence, revision, server-owned type/actor/time, previous/new state and minimal metadata. No event mutation API. |

UTC timezone-aware database timestamps are used. Service-owned updated timestamps
avoid transaction-start now() moving time backwards during counter-only updates.
Indexes bound project history, task display order and event sequence queries.
DB triggers reject snapshot definition/edge updates/deletes, graph insertion after
publication, ledger updates/deletes and unsupported execution transitions. The
local table owner remains trusted and can use DDL; these are not a substitute for
separate least-privilege production operations. Downgrade refuses data destruction.
The migration neither resets nor changes existing Stage01–04 records.

## Lifecycle and events

```text
created --initialize in the same transaction--> awaiting_executor --cancel--> cancelled
   event1, revision1                              event2, revision2          revision3
```

Created is an uncommitted initialization state, recorded in the ledger. Clients
only receive a fully initialized committed run. Blocked is reserved for future
design: Stage04 currently prohibits approving tasks needing clarification, so
Stage05A rejects such sources rather than inventing a blocked valid run. Running,
paused, failed execution, succeeded and verified-complete are not exposed states.

Each task has eligibility `eligible` or `waiting_prerequisites`, and execution
status `awaiting_executor` or terminal `cancelled`. Its planning definition remains
proposed. Cancellation retains immutable dependency classification while removing
dispatch eligibility and displaying a cancelled explanation. No completion field
or completion-evidence input exists.

The centralized transition service rejects unsupported transitions and stale
expected revisions. Cancellation locks the project/run, checks role/session,
changes run and task states, increments revision and appends ordered task/run
events in one transaction. Cancellation is terminal; an explicit new run is the
future-dispatch alternative. Repeating cancellation with an old revision returns409.

Run creation emits run_created (human actor) and run_awaiting_executor (system
actor). Cancellation emits task_cancelled for each ordered task, then run_cancelled.
The run lock allocates unique contiguous sequence numbers. There is no public
event writer or client-supplied actor/type/metadata. Metadata only states
execution_performed=false. Short safe commit logs contain IDs/status, never source
documents, cookies, credentials or tokens.

## DAG eligibility

Reuse Stage04 `task_graph.analyze`: bounded40-node graph, missing/self/duplicate
rejection, deterministic Kahn topological order with display-order tie breaks,
cycle path detection, prerequisite closure and transitive impact. Source Pydantic,
coverage and composite FKs reject cross-project or invalid references. The new
pure evaluator accepts no completed-task set and cannot unlock downstream work.

For A -> B -> C, A has no unmet prerequisites but awaits an executor; B waits for
A with verified evidence; C waits for B. Approval, generation and graph rendering
do not satisfy any prerequisite. There is no scheduler, background task dispatcher
or hidden task-completion operation.

## Idempotency, concurrency and recovery

Creation201 publishes one run. Identical project/actor/request UUID plus identical
exact source inputs returns200 with the original run. Different inputs with that
UUID return409. Resolve authorized replay before checking current source, so old
requests remain recoverable even after a newer approval. Workspace/project locks
serialize simultaneous creation; database uniqueness provides a second guard.
Any initialization failure rolls back run, tasks, edges and events together.

The UI disables duplicate activation synchronously. It stores only account,
workspace and project scoped request UUID/source ID/version/revision references
in SessionStorage. These are untrusted preferences, never authentication or source
authority. A lost response retains that key. Check creation status performs an
actor-scoped GET; if no run is found, explicit Retry original creation reuses the
same key and binding. No automatic POST, new-UUID fallback or model retry occurs.
Account/project/workspace changes remount the fenced view and abort stale reads.

## API reference

All routes are under `/api/v1/projects/{project_id}/orchestration-runs`.

| Method / suffix | Behavior |
|---|---|
| POST (root) | `{client_request_id,architecture_id,architecture_version,architecture_revision}`;201 new,200 exact replay; Member/Admin/Owner plus CSRF/Origin. |
| GET (root) | Saved history, limit1–50/offset; optional client_request_id filters the current actor for exact recovery. |
| GET /source | Validated current approved architecture summary or null. Stale source409 does not hide historical run reads. |
| GET /{run_id} | Bound metadata, audited tasks, graph and source_current. |
| GET /{run_id}/tasks | Audited immutable task definitions with eligibility/execution states. |
| GET /{run_id}/graph | Validated deterministic graph, roots, eligibility/blockers/impact; execution_performed=false. |
| GET /{run_id}/events | Ordered ledger, after>=0 and limit1–100; next_sequence is the exclusive next-page cursor. |
| POST /{run_id}/cancel | `{expected_revision}`; guarded terminal cancellation, Member/Admin/Owner plus CSRF/Origin. |

All reads require current authenticated membership, including Viewer access. Exact
run/project predicates prevent cross-project guesses. Foreign resources return404;
Viewer writes403, unauthenticated reads401, invalid input422, source/revision/replay
conflict409, database unavailable503. Structured errors include a safe remedy and
the `#orchestration-foundation` documentation anchor. There is no unrestricted
status PATCH, executor claim, event append or task-success endpoint.

Example after authenticating and obtaining the existing session-bound CSRF token:

```json
{"client_request_id":"<new UUID>","architecture_id":"<approved UUID>","architecture_version":1,"architecture_revision":2}
```

Retain that exact request on an uncertain save. GET the root with
`?client_request_id=<UUID>` before explicitly repeating the original POST.

## Verification and future boundary

Gate A retains all Stage01–04 checks and adds real-PG orchestration tests and
desktop/mobile/tablet browser flows. Independent local Gate B approves authored
test source through actual UI, creates a real run and compares browser/API data
with a fresh native-process SQL audit, then checks replay/reload/isolation.
Provider construction/generation are denied by the guarded test factory and
browser boundary; any attempted generation fails verification. Auth, CSRF, roles,
API, PostgreSQL and browser code remain real. Authored fixtures are not AI evidence,
and no synthetic executor exists.

Stage05A Gate C requires applicable passing A+B at the same source/contract. Older
Stage03/04 real-model receipts remain historical and cannot certify new code.
See VERIFICATION_STAGE05A.md for actual results, not this design document.

Future05B needs explicit executor identity/registration, atomic claim leases and
fencing tokens, acknowledged dispatch and independent evidence acceptance before
dependency completion. Those interfaces will require a new migration and guarded
transition contract. No placeholder claim/completion route or scheduler is added
in05A. Human execution approvals and Mission Control remain05C/05D.
