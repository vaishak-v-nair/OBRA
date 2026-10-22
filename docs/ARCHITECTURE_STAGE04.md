# Architect proposals and task dependency engine

Stage04 extends the same application. It proposes architecture and engineering work;
it never implements, tests or deploys that work. Its own live model gate is mandatory
for VERIFIED; Stage03 live evidence and controlled fixtures cannot substitute.

```text
current approved ProductPlan ID/version/revision/hash (server-owned source)
 -> authenticated explicit request UUID + optional untrusted constraints
 -> shared admission / pending commit / original-session running commit
 -> released DB connection -> one bounded official Gemini SDK call
 -> strict ArchitectureDocument -> source refs -> DAG -> coverage
 -> current source/session/role/lease recheck
 -> ONE commit: architecture + components + tasks + edges + traces + succeeded run
 -> human exact-revision draft edit -> explicit Owner/Admin review/approval
```

## Persistence and source history

Alembic `7dd7671f9417` adds six tables, no deletion/reset of existing data:
architect_runs, architecture_versions, architecture_components, engineering_tasks,
task_dependencies and requirement_traces. A fresh-schema migration test preserves
user hash/project fields/approved PRD and relational children byte-for-byte through
the actual Alembic upgrade. The development database is never test-cleaned.

Architecture root JSON stores overview, technologies, logical database/API proposals,
security/deployment, uncertainty and coverage exceptions. Relational components/tasks,
dependency edges and source-story traces are excluded from that JSON copy. Task bodies
store their scoped deliverables/criteria/reference keys once; category/priority/state
and display order are queryable columns. Stable keys preserve node UUIDs during edits.
Composite FKs bind both edge ends to one architecture/project and bind every story
trace to the architecture's exact source plan. SQL checks reject self/duplicate edges
and execution statuses. Full cycles/reference/coverage checks run in application code.

Versions/revisions are positive and project-scoped. Generated versions start draft/r1;
whole-document PUT increments only the intended draft revision. Expected revision is
mandatory. Approval records exact version/revision/actor/time and human dispositions,
superseding only the prior current architecture. Older drafts cannot supersede a newer
approval. Approved/superseded content stays immutable. Explicit idempotent draft copies
create a new version with original source/copy lineage; no source is silently rebased.

Only the current approved PRD authorizes a new run. Read its complete saved graph and
verify its canonical hash under locks. Record source identity and an immutable request
snapshot in the run. Recheck before dispatch, publication and approval. A new unapproved
PRD draft does not stale a source; another approved PRD does. Historical architecture
remains readable with earlier-source status. Protected reads hold a shared root lock
across bulk assembly, preventing mixed revisions during a concurrent PUT.

## Authoritative contract, graph and coverage

`architect-v1` is a separate versioned prompt. `ArchitectureDocument` is strict,
extra-forbid and bounded: all required design sections, at most12 components/40 tasks,
observable task acceptance criteria, proposed API status, optional explicitly estimated
complexity, risks/open decisions and exact source references. Provider schema projection
is a generation hint; full Pydantic validation remains authoritative. Generated text is
untrusted data. SQL/routes/commands and embedded source instructions are never executed.

**A -> B means B depends on A**, represented as B.dependencies=[A]. The pure graph
engine rejects duplicate keys, self/missing/duplicate edges and cycles, then uses Kahn
ordering with display order/stable key tie-breaks. Traversal computes ancestors,
dependents and transitive impact. A valid edgeless DAG is permitted. Reordering only
affects unconstrained topological ties; it cannot satisfy an edge or schedule work.
Every task is unexecuted: roots are dependency-ready in the planning graph, nonroots
are blocked by their prerequisites, and needs-clarification takes precedence.

Source stories/requirements/criteria must exist. Criteria must belong to the task's
referenced stories. Components also bind valid source stories. Coverage reports missing
links, orphan tasks, clarification tasks and open decisions. Source story B depending
on A requires all contributing A tasks to be ancestors of each B task, except the same
combined task; a precise gap is reported otherwise. Linked coverage is structural,
not semantic adequacy or proof of implementation. Missing coverage can be accounted
for only by exact reasoned exceptions. Approval requires explicit human acknowledgment
of those exceptions/blocking decisions and inherited unresolved/deferred blocking
source confirmations. Source assumptions/risks/questions/provenance are retained
server-side and displayed independently of model-owned editable text.

## Provider and execution integrity

Architect reuses `GeminiStructuredProvider` and the existing official SDK/limited
transport. PM defaults and request schema remain unchanged. Architect environment:
ORBA_ARCHITECT_MODEL/THINKING_LEVEL/TIMEOUT_SECONDS/MAX_OUTPUT_TOKENS/MAX_INPUT_BYTES,
optional ORBA_ARCHITECT_API_KEY. An absent/empty Architect key reuses resolved PM/Gemini
credential; model never inherits. Reviewed model policy and explicit thinking are
shared. Defaults90s provider/95s transport/100s asyncio envelope,6000 combined output/
thinking tokens,96000 total prompt/schema/source UTF8 content bytes. Requests exceeding
the input cap fail before admission, without truncating source. Next generation POST
envelope290s and browser300s enclose server bounds (provider maximum180s), while normal
API requests retain short deadlines. Streamed body bounds apply to both planning APIs.

SDK/HTTP transport retries are disabled; no continuation/tools/functions/fallback.
One shared PostgreSQL advisory admission lock and combined run counts enforce the
existing PM-named active/account/global limits. Separate per-agent project-active
indexes complement that shared budget. At concurrency1, PM and Architect cannot call
simultaneously. Larger configured concurrency permits distinct planning requests;
this is local admission, not a distributed provider quota or task scheduler.

Persist pending then running before dispatch. Current original session, current role,
executor and deadline fence atomic publication. Record actual requested/returned model,
response/request IDs and usage only when supplied. Safe phase timings stop before
terminal commit; acknowledged commit is logged separately. Actual upstream503/504 is
classified separately from local/transport timeout. No raw provider bodies, user
content, credentials, tokens or stack traces are public diagnostics.

Exact actor/project/request UUID replay precedes new source/config/input-cap policy;
changed payload under the same UUID conflicts. Replays never resume paid execution.
Explicit retry creates a new auditable attempt only after terminal confirmation.
Expired pending/running leases become interrupted on GET/monitor, without takeover.
After SQL uncertainty a new locked read can confirm success or an incomplete rollback;
only a confirmed incomplete run becomes persistence_failed. Otherwise outcome remains
unknown for GET recovery, never forced failure over possible committed success.

## APIs and permissions

All paths are under `/api/v1/projects/{project_id}`. Every read validates membership;
every mutation validates Origin/CSRF, locks workspace/project, rechecks role and the
original session. Viewer reads only; Member/Admin/Owner generate/edit/copy; Admin/Owner
approve. Unrelated IDs return404 without artifact content. FastAPI remains the sole
authentication authority; no production controlled-provider flag exists.

| Endpoint | Contract |
|---|---|
| GET /architect-source | Current actual approved PRD or null, validated saved graph |
| POST /architect-runs | Request UUID + source ID/version/revision + constraints; synchronous bounded generation |
| GET /architect-runs[/{id}] | Bounded real history/exact record; optional own request-UUID filter |
| GET /architectures[/{id}] | Versions/complete validated proposal, source, graph, coverage and genuine generation metadata |
| PUT /architectures/{id} | Whole strict document + expected_revision; atomic draft edit |
| POST /architectures/{id}/draft | Exact source architecture version/revision + copy UUID; no model call |
| POST /architectures/{id}/approve | Exact version/revision + exact obligation-ID/reason map |
| GET /architectures/{id}/tasks, /graph, /coverage | Typed revision/hash-bound synchronized read views |

## UI and verification boundaries

Product Plan remains mounted while the local Architecture/Task Graph views share one
draft. Native SVG overview plus synchronized native task list/detail provide directed
edges, dependency add/remove, reorder, coverage and planning explanations. All actions
work without drag/hover/SVG keyboard dependence. Unsaved previews never claim saved
validity. Rejected edits retain local input and saved revision; error links target
fields. Deliberate navigation/workspace changes use Save/Discard/Cancel; reload warns.
The native navigation dialog is portaled to the document body so switching to the
Product Plan tab cannot hide an active modal. Rejected saves keep the dialog open,
announce the error there, and preserve both the local draft and saved graph.
Session expiry/logout clears immediately. SessionStorage holds only nonsecret scoped
request/copy UUIDs, never briefs, constraints, credentials or authorization.

Gate A extends the existing runner and all historical regression identities. Separate
guarded factories double only their named model dependency. Stage04 evidence namespace
and stage/agent/prompt/schema/source discriminator prevent PM live proof from certifying
Architect. A failing required native command stops A. Stage04 B requires explicit
opt-in/current A/configuration, one read-only metadata check and one real browser
generation. One authored source is persisted and approved through the real UI without
PM generation. Reuse one architecture for SQL/hash/DAG/coverage/browser/edit/approval/
isolation checks. Additional generation POSTs are blocked before forwarding and fail B.
Gate C revalidates source, command exits, reports, profile, timestamps and artifact
hashes. Missing/failed/stale/controlled B stays PARTIAL. No paid B has been run for this
implementation. The wrong-success experiment genuinely exits1 separately from normal
discovery. No Stage05 task execution, scheduler, sandboxes or agent handoffs exist.

Live identity checks also reject missing/non-Gemini/controlled returned-model labels
and any controlled-provider diagnostic flag. A plausible model label alone is never
live proof: matching real browser, API, independent SQL, actual command exits and
source/profile-bound receipt artifacts are all required.
