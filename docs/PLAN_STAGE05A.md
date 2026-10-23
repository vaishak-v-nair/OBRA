# Stage05A implementation and verification plan

Owner authority: persistent orchestration foundation only. Preserve checkpoint
`bb880486bf7d8441cc6415f4dc6d6085a731151b` and historical Stage01–04 evidence.
No model calls, executor, task execution, scheduler, handoffs, commit or push.

## Design

An authorized Member/Admin/Owner selects an exact approved architecture ID,
version and revision. In one short transaction, acquire the existing workspace
and project locks, revalidate the original session, resolve idempotent replay,
validate the approved architecture and current approved PRD through the existing
repository/coverage/DAG engine, and snapshot the server-owned source.
Check approval actor/time and exact saved-revision dispositions, not just the
state label. Reject structural or approval corruption without creating records.

The canonical snapshot includes the architecture document, its approval binding,
PRD ID/version/revision/hash, source task UUIDs, dependencies and requirement
traces. SHA-256 of UTF-8 canonical sorted JSON is the immutable checksum. Store
the snapshot once on the run; relational task snapshots and edges support queries
and future execution contracts. Validate relational reconstruction against it.

Run states: created -> awaiting_executor -> cancelled. Creation and
initialization occur atomically; created is only an event-visible transient.
Blocked is reserved and inaccessible in Stage05A: Stage04 approval already
rejects tasks needing clarification. Such source corruption is rejected, not
converted into a valid-looking orchestration run.
No running/completed/succeeded state or arbitrary status-update endpoint exists.
Cancellation is an explicit CSRF-protected mutation with expected revision.

Task fields separate dependency eligibility (eligible, waiting_prerequisites)
from execution (awaiting_executor or cancelled). Clarification blockers are
reserved for future design; current approved-source validation rejects them. Root tasks
may be eligible; downstream tasks wait for verified prerequisite evidence which
Stage05A cannot produce. No completion input is accepted by the evaluator.

Edges are prerequisite -> dependent, with composite same-run/project FKs,
unique edges and no self-edge. Reuse Stage04's deterministic DAG analysis.
Task definitions/dependencies/source snapshots are immutable; cancellation only
changes execution state. An append-only event ledger uses a run-local sequence,
allocated under the run lock and committed with state/revision changes. Database
constraints/triggers protect immutable records; table-owner SQL remains an
operator trust boundary, not an end-user API.

Creation uniqueness is (project, creating user, client request UUID). Identical
authorized replay returns the original run even after source approval changes;
different inputs with that UUID produce 409. Project locking serializes creation
against source approval and concurrent duplicate requests. Invalid initialization
rolls back every child and event. Read endpoints verify current membership and
exact run/project identity; unrelated resources return 404.

## User experience

Add one Execution Plan project view. Show approved-source selection, saved run
ID, exact source version/revision, eligibility and blocker reasons, accessible
graph/list, persisted event timeline, and explicit awaiting-executor copy:
"No code has been run." Preserve input/request UUID on uncertain writes, offer
GET-only reconciliation, never automatically repeat POST. Reuse existing theme
tokens, session/workspace fencing and accessible native controls.

## Incremental work

- [x] Inspect baseline, preserve nine excluded files and evidence hashes.
- [x] Complete CEO, design, DX, engineering plan reviews sequentially.
- [x] Add typed state contracts, snapshot models and additive migration.
- [x] Implement evaluator, snapshot publication, ledger and state transitions.
- [x] Add secured typed APIs and real PostgreSQL integration tests.
- [x] Add minimal UI, desktop/mobile/browser persistence and isolation tests.
- [x] Extend Gate A with every Stage01–04 regression plus new checks.
- [x] Independently run local control-plane Gate B with zero generation.
- [x] Execute isolated deliberately wrong success assertion (actual pytest exit1).
- [x] Record applicable A/B/C evidence, fingerprint and preservation audit.

## Test strategy and failure matrix

Use the fixed guarded orba_test role/database. Never run backend and browser
tests together. Authored approved fixtures are test source data, never model or
execution evidence. Test approved/draft/stale/foreign sources, schema/graph and
trace corruption, same-run FK constraints, deterministic ordering, checksum,
snapshot immutability, root eligibility versus execution, replay/conflict/races,
atomic rollback, restart persistence, ledger sequence/append-only protection,
revision conflict, cancellation, expired sessions, CSRF, Viewer and unrelated
workspace restrictions. Unsupported task success routes must reject unchanged.

Browsers use real Next/FastAPI/auth/PostgreSQL without model dependency. Verify
creation, exact IDs, graph, downstream blocking, no completed tasks, reload,
events, duplicate prevention and role/isolation on desktop and mobile. Gate B
independently checks database rows/hash/events against browser/API records.

New receipts live under docs/evidence/stage05a. The Stage04 gate lock and receipts
are not modified. Gate A and local B bind the current source fingerprint and
nonsecret deterministic control-plane contract. Gate C requires both to pass;
old Stage04 live evidence cannot certify Stage05A. Overall Stage05 remains
IN PROGRESS even if Stage05A is VERIFIED.

## GSTACK REVIEW REPORT

CEO review completed in local single-model development-review mode. Accepted:
reserve blocked initialization; validate exact approval dispositions; actor-scoped
request-ID recovery; historical reads after source changes; scoped evidence.
Detailed artifact: C:/Users/vaish/.gstack/projects/OBRA/stage05a/20261022T122138Z/ceo-review.md.
No scope challenge or expansion. Design, DX and engineering reviews follow in
that order. The native gstack launcher is absent; local review skills and
development review agents are used without paid model probes.

Design review completed (seven dimensions; specification review only). Accepted:
one Execution Plan view; exact source/run identity; separate eligibility/execution;
read-only dependency diagram with accessible list; account/workspace fencing;
typed uncertain-write errors and exact GET recovery; ordered persisted events;
confirmed cancellation with revision conflict and focus recovery. Reuse theme
tokens and graph geometry, not Stage04's editing/ready vocabulary unchanged.
Detailed private artifact: design-review.md alongside the CEO report. No owner
decision remains; DX then engineering review follow.

DX review completed (eight dimensions, single-model development review). Accepted:
credential-free local control-plane reproduction; exact request-ID reconciliation;
source-conflict remedies; event cursor examples; migration preservation tests;
new Stage05A-scoped gates rather than writing the Stage04 lock. API routes keep
the existing project/version convention. Detailed private artifact: dx-review.md.
Engineering now reviews the amended plan and implementation boundaries last.

Engineering review complete (architecture, code quality, branch-by-branch test
diagram and performance). Accepted: truthful cancelled-node explanations,
explicit same-run/project FK tests, concurrent cancellation and exact cursor
boundaries. Private eng-review.md and test-plan.md contain diagrams and failure
registries. No confirmed P0/P1 or unresolved owner choice. No external second
model or runtime verification was claimed by any review.

Aggregated implementation tasks: immutable source/approval binding (P1), guarded
transactional snapshots and event ledger (P1), idempotency/concurrency/recovery
(P1), secured typed APIs and negative tests (P1), truthful accessible project UI
(P1), scoped A/B/C gates and independent SQL/browser audit (P1), reproduction and
upgrade documentation (P2). All are inside the owner's explicit Stage05A scope.
The owner already authorized implementation, so no additional plan permission
is required. Review execution is complete: matching Gate A/B/C passed; intentional scope and
operational limits remain documented in VERIFICATION_STAGE05A.md.
