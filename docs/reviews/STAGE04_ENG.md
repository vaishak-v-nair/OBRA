# Stage04 engineering review

2026-10-21. Full sequential review; this is a design/test contract, not runtime proof.
Scope accepted: one planning agent, a persisted technical proposal and task DAG.
No scheduler, task execution, coding agent, framework migration or paid request.

## Architecture and existing authorities

Reuse the current session/CSRF/workspace locks, short transaction helpers, official
bounded SDK transport, PM source document assembler and native UI tokens. Extract
only a configurable structured-request core and combined admission counters. Keep
Architect-specific source, publication and approval checks explicit. Root proposal
JSON excludes relational components/tasks/edges/story traces. Composite ownership
FKs complement application reference validation; no diagram substitutes for a DAG.

1. Shared admission must count both run tables, not merely take the same mutex.
2. Exact source state/version/revision/hash must be checked again at publication and
   approval. New unapproved PRD drafts do not supersede the current agreement.
3. Criterion parentage, source prerequisites and inherited uncertainty must survive
   generated or edited text. Linked coverage is not semantic completeness.
4. Publication uses original-session authority, a fenced lease and one transaction;
   uncertain COMMIT gets a fresh read, never a forced failure over possible success.

Selected complete option for all four. Rejected: per-agent counters, last-write-wins,
flat key existence and best-effort partial graph saves. These are integrity fixes
within the owner's scope, not new product choices.

## Code quality and performance

Use bounded strict schemas and pure deterministic graph functions. Stable keys retain
node UUIDs during saves. Assemble children with bounded bulk queries, not per-task
round trips. Kahn ordering is O(V+E) plus deterministic priority-queue ordering; impact
and prerequisite closure are bounded traversals. At most40 proposed tasks and12
components keep native SVG/list interaction readable. No caching of fresh AI results,
generic orchestrator, background queue or new graph dependency is warranted.

No DB session is checked out across the network call. Short transaction statement,
lock and transaction limits retain current safeguards. Provider/transport/envelope
budgets are explicit; proxy and browser envelopes must contain them. Logs allow only
safe IDs, durations, error categories and real provider status/usage metadata.

## Test coverage diagram

```text
New code paths                                      User journeys
schema -> refs -> DAG -> coverage                    approved PRD -> Architecture [E2E]
  valid / malformed / dangling / cycle [unit]           no source / no model / viewer [E2E]
reserve -> replay / limits / source lock [Postgres]    one click -> one durable run [E2E]
provider -> valid / 503 / 504 / timeout [controlled]   failed -> GET -> explicit retry [E2E]
publish -> lease/session/source -> atomic [Postgres]  draft -> edit -> reload [E2E]
edit -> revision / refs / graph rollback [Postgres]   graph add/remove -> cycle error [E2E]
approve -> current source / coverage [Postgres]       approve -> reload -> outsider404 [E2E]
actual prompt -> actual Gemini -> valid artifact [LIVE EVAL: NOT AUTHORIZED]
```

All new paths are initially coverage gaps, not claimed tested by this review. Add
`test_task_graph.py`, `test_architect_schemas.py`, `test_architect.py`, provider and
verifier tests alongside implementation. Real PostgreSQL integration must check
actual rows after errors and through fresh sessions. Preserve all285 existing backend,
60 core and33 controlled-browser baseline identities. Controlled model doubles are
labeled; auth/API/DB/browser remain real. A skipped/retried case cannot pass a gate.

Critical regression targets: both directions of combined admission, PM SDK request
shape, all deterministic credential blanks, proxy/body boundaries, session expiry,
tenant404 and old approval/hash preservation. Source fixture preparation uses an
authored PRD approved through the real API; it never claims PM model evidence.

## Failure registry

| Failure | Required handling and test | User visibility |
|---|---|---|
| Source changed during generation | Fence publication, no artifact, terminal run | Explicit source conflict |
| Concurrent same UUID | One admitted execution; replay/202 | Existing run, no new request |
| 503/504 or malformed output | Failed run, zero new artifacts, old approval intact | Safe actual error category |
| Invalid/cross-project edge | Schema/FK rejection and atomic rollback | Task-specific validation |
| Stale edit | Revision409, saved graph unchanged | Local draft retained |
| Unknown commit | Independent read; otherwise unknown outcome | GET-only recovery |
| Diagram renders a cycle | Backend rejects save/approval regardless | Unsaved invalid preview |
| Missing live evidence | C remains PARTIAL | No false certification |

Each failure has a planned meaningful test and explicit handling; no silent gap is
accepted. The isolated incorrect-success assertion must actually exit1 and stay
outside normal discovery. It is evidence of rejection, not a passing production test.

## Delivery, workstreams and follow-ups

Sequential implementation: contracts/algorithms -> migration -> persistence/provider
-> lifecycle/API -> shared UI/editor/graph -> tests/gates/docs. These steps share
source contracts and modules; no parallel implementation worktree is necessary.
Fresh-context review voices are in-host, same-family; external CLI consensus is N/A.
No new TODO beyond the existing later-stage roadmap is needed. No deferred mandatory
integrity fix is silently relabeled optional.

## Implementation tasks

- [ ] E1: enforce composite ownership, exact source lineage and all graph invariants.
- [ ] E2: fence publication/approval and share admission without changing PM behavior.
- [ ] E3: cover every negative branch with real DB assertions and preserve regressions.
- [ ] E4: stage-bind A/B/C and prove failed required children cannot yield VERIFIED.

Completion: scope accepted;4 architecture issues addressed in the plan;2 code quality
constraints; coverage diagram and concrete test targets written; performance bounds
specified; exclusions/reuse/failures documented. Runtime implementation remains to do.
