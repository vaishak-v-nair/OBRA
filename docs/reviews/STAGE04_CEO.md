# Stage04 scope and failure review

2026-10-21; SELECTIVE EXPANSION within the owner's explicit Stage04 boundary.
Review of `STAGE04_PLAN.md` against the committed PM, auth, provider and verification
implementation. These are design findings, not test results. Primary reviewer is
Codex; the independent in-host voice is reported separately, never as another model.

## Premises and alternatives

The user problem is the gap between an approved product plan and a reviewable technical
delivery plan. Existing PM stories are requirements, not engineering tasks, and their
dependency graph cannot stand in for an implementation task DAG. An architecture
proposal with no persisted traceability would repeat this gap; a diagram alone would
hide invalid dependencies. Doing nothing leaves the approved PRD without a trustworthy
handoff, but executing tasks now would exceed the explicitly authorized planning stage.

The verified Stage03 checkpoint and source/profile receipts were revalidated before
changes. This proves that historical baseline, not that Stage04 or future provider
availability is already verified. The assumption that approved source data is immutable
holds for content/revisions, while approval currency can change; therefore source
currency must be rechecked at publication and approval, not silently restamped.

| Approach | Completeness | Effort (human / assisted) | Risk | Reuse and tradeoff |
|---|---|---|---|---|
| JSON-only architecture with rendered dependency lines | 5/10 | M / S | High | Smallest patch, but lacks relational traces, FK protection and authoritative graph operations; fails owner requirements |
| Bounded relational architecture/task engine, shared SDK/auth primitives | 10/10 | XL / L | Medium | Meets the current handoff, isolation, audit and editing requirements with no new infrastructure; selected |
| Generic event-driven agent/orchestration platform | Outside scope | XL / XL | High | Could serve later agents but introduces execution/scheduling ownership and unneeded services; deferred |

All alternatives were evaluated against the actual API ownership and short-transaction
patterns. The middle approach is the smallest complete implementation, despite more
than eight files: schema, graph, migration, service, routes, UI and verification are
different security/consistency responsibilities, not interchangeable wrappers.

```text
CURRENT                    THIS STAGE                    FUTURE, NOT BUILT
approved PRD -> no tasks -> technical proposal + DAG -> evidence-driven execution
                           source/approval preserved     under separate authority
```

## 1. Architecture and ownership

Reviewed PM route/service/repository boundaries, the shared SQLAlchemy Base, the official
SDK adapter, and same-origin frontend proxy. Reuse the existing authorization/short
transaction primitives; extract only the bounded SDK request core. Architect publication
must remain distinct because it additionally binds an approved source, coverage and a
task graph. No orchestrator or parallel authentication authority is warranted.

```text
source selection -> authorization -> persisted pending/running -> SDK (no DB tx)
 -> schema + references + DAG -> original authority fence -> atomic draft + success
missing/empty/invalid source --------> 404/422/409 before dispatch
provider/validation failure --------> terminal failure only, prior approval preserved
uncertain publication -------------> GET reconciliation, no retry or status overwrite
```

## 2. Error and rescue registry

| Codepath | Failure / exception | Handling | User impact and verification |
|---|---|---|---|
| Source resolution | missing/foreign UUID; HTTPException | Same404; no context sent | No resource existence leak; real tenant tests |
| Source/revision validation | draft/superseded/stale source; domain error |409 before dispatch; recheck before publish/approve | Choose the current approval; source-race tests |
| Input/output parsing | Unicode/Pydantic/ValueError |422 before admission or failed run after response | Input retained; malformed/schema tests |
| DAG validation | GraphValidationError |422; transaction rollback | Saved graph unchanged; cycle/self/missing/duplicate tests |
| Reference/coverage validation | domain validation error | Reject invalid refs; block incomplete approval | Inspect coverage/exceptions; real source tests |
| Provider | ProviderFailure; TimeoutError; SDK APIError | Safe category/status, real metadata, terminal failure | Explicit retry only after confirmed terminal state |
| Reservation/start/publication | SQLAlchemyError | Outcome unknown; GET only; no automatic dispatch | Durable request reference; commit-boundary tests |
| Original authority | HTTPException after logout/role change | Fence publication, failed/interrupted record | No replacement-session authority; revocation tests |
| Optimistic save/approval | expected revision/state conflict |409 without replacing server/local drafts | Compare latest version; stale-editor tests |

Every failure maps to a named response and real test target. Raw exception bodies,
credential headers and product content must not enter diagnostics. An unknown commit
is distinct from a known failed model response; the service cannot rewrite possible
success into failure merely because the browser lost a response.

## 3. Security and threat model

The new attack surface is project-scoped run/artifact/graph/coverage endpoints and a
second model-context builder. High-impact threats are guessed cross-workspace IDs,
forged source snapshots, role/session changes during generation, and dependency/trace
edges crossing artifact or project boundaries. Existing membership joins, locked writes,
original-session checks, composite FKs and authoritative source resolution mitigate
them and must be exercised independently of hidden UI controls.

Model output is untrusted planning data. JSON/Pydantic/reference validation does not
prove semantic correctness or technical installation. Keep text safely rendered, never
execute generated SQL/shell/routes, never allow model text to record human acceptance,
and explicitly document that neither tests nor proposals certify production security.

## 4. Data and interaction edge cases

Nil/empty source selection is invalid before admission; no approved plan is an actionable
empty state. Empty task/component/criterion collections must fail the authoritative
contract, while drafts with uncovered source items may remain reviewable but cannot
be approved without explicit accepted exceptions. A provider503/504 creates no valid-
looking artifact; transaction faults cannot expose a partial graph.

Repeated clicks are blocked synchronously and server-side by durable UUID/active-run
constraints. Navigating away does not authorize a second POST; unknown outcomes retain
only a scoped request UUID. Saves preserve local content on server/network conflicts,
and changing accounts/workspaces aborts/clears protected UI. Version selection and
approval are tied to exact IDs/revisions, not whichever response arrives last.

## 5. Code quality and reuse

The review identified two duplication risks: cloning the400-line PM SDK adapter and
reimplementing session/role locking. Both are rejected in favor of existing primitives
and a small typed configurable SDK core. The DAG algorithm belongs in a pure module,
independent of SQL/API/SVG, so all callers use one edge convention and validation.

Relational assembly must preserve stable node IDs and use ordered bulk queries. A
generic multi-agent service registry would obscure admission/publication rules and is
unnecessary for two explicit planning flows. Existing tests stay additive, with no
baseline assertions removed to accommodate new behavior.

## 6. Test ambition and evidence boundaries

The decisive test is a simultaneous repeated request reaching exactly one controlled
provider call, persisting one complete graph, with another independent SQL session
reconstructing the same artifact. Hostile tests cover a cyclic PUT, cross-project edge
insert, foreign source UUID, revoked original session, damaged stored graph and stale
approval. A publication fault must roll back every child row as well as the root/run.

```text
pure schema/DAG/coverage -> unit boundaries and deterministic algorithm invariants
real auth/API/PG         -> source, roles, transactions, FKs, idempotency, revisions
real browser + DOUBLE   -> review/graph/edit/approval/reload/failure/isolation
real browser + Gemini   -> separate authorized B, one call, NOT RUN in this stage work
wrong-success assertion -> isolated actual nonzero, excluded from normal discovery
```

Controlled model output only proves application behavior. Preserve prior test identities,
zero skips/retries, historical provider failures, and source-bound immutable receipts.
No paid probe is permitted during implementation or readiness checks.

## 7. Performance and bounded behavior

The provider is the expected slow path, followed by bounded relational reconstruction
and graph/coverage computation; no latency percentile is claimed without measurements.
Limit input UTF8 bytes, provider envelope/output/time, task/component counts and relation
counts; Kahn ordering is bounded by nodes/edges with a small deterministic priority heap.
Do not keep DB sessions checked out while waiting for the SDK.

At10x local use, configured admission and per-project uniqueness reject work before
paid dispatch. At100x, the local synchronous server and shared-IP/session system need
a separately authorized operational design; no distributed production scalability is
claimed. Cached authority or stale graph validation must never replace current checks.

## 8. Observability and operational recovery

Record run/request IDs, actual stage durations, safe HTTP/error categories, executor and
terminal state. Capture only genuine returned model/response/usage fields, allowing null
values where the provider supplies none. Existing plan approvals and run inputs are audit
anchors, not a fabricated activity feed.

Recovery is explicit: GET the exact request, reconcile stale lease as interrupted, then
allow a deliberate fresh UUID only after an own terminal result. No auto-resume, model
fallback, retry loop or paid readiness generation is added. Docs and an independent
SQL inspector must explain provider failure versus publication/database uncertainty.

## 9. Migration, rollout and rollback

Use a forward additive migration and schema drift check, then start the updated API/UI.
Preserve every Stage01-03 project, user, hash, session, approved PRD and migration revision;
test this with real pre-upgrade records. New readiness checks must include Architect
tables so missing migration cannot masquerade as healthy operation.

No deployment is authorized. If local rollout fails, stop the changed API and inspect
the actual error; do not downgrade/drop data or serve an unauthenticated old version.
The checkpoint supplies a reviewed code restore point, while persistent new tables
remain intact for an operator-controlled recovery rather than a destructive shortcut.

## 10. Long-term trajectory and scope decisions

Stable source/node IDs, explicit prerequisites and immutable approval can support later
execution without pretending it exists now. Task readiness must remain dependency
readiness, never synthetic execution evidence. Per-edit audit diffs, durable distributed
execution and advanced canvas remain in existing TODOS rather than slipping into Stage04.

The six-month regret scenario is mistaking a polished graph for validated coverage or
completed work; server-side DAG/coverage gates and explicit proposal labels address it.
Architecture/model configuration changes are reversible; approved historical records
are deliberately immutable. No paid/provider change or product-scope challenge is needed.

## 11. Design intent and state coverage

Source identity and proposal state appear before detailed technology/task content.
Use current semantic tokens, typography and workspace shell; preserve the existing PM
view instead of replacing it with a second application. Every graph operation must also
be reachable through native labeled list controls, including on narrow viewports.

Loading, no-source, no-provider, failed-generation, draft, conflict, stale-source and
approved states have separate truthful messages/actions. A failed run preserves prior
approval and constraints; no progress percentages or fictional agent steps are added.
The design phase will specify state matrices, focus and actual browser review targets.

## Completion summary

| Item | Design result |
|---|---|
| Scope | Selected bounded complete relational planning engine; no expansion beyond Stage04 |
| Premises | Verified baseline; future live availability explicitly unknown |
| Error/authority/commit risks | Named handling and required test targets above |
| Critical gaps | None deliberately accepted; implementation and tests still required |
| Reuse | Existing security/transactions, shared bounded SDK, native UI |
| Deferred | Existing later-agent, distributed-execution, advanced-canvas and broader quality-evaluation TODOS |
| Reversibility | Local code checkpoint preserved; additive data/history must not be destroyed |
| Evidence | Baseline verification in progress; no new Architect execution claimed |

Independent-voice findings and the six-dimension consensus are appended after that
voice completes. Nested external CLI/model review probes are unavailable in degraded
native mode; agreement within the in-host family is not cross-model verification.

## Temporal decisions, state machines and rollout

Hour1 foundations require source IDs, shared admission and the edge convention to be
settled before migration. Hours2-3 core logic require exact criterion lineage and
source prerequisite semantics before API approval exists. Hours4-5 integration require
unknown-outcome GET recovery and atomic graph edits; hours6+ QA requires preserved
baseline identities and a separate non-generative preparation gate. These are human
sequencing labels, not a promised completion time; assisted implementation is still
bounded by actual test/service execution and no verification is inferred from elapsed time.

```text
pending --confirmed start--> running --validated atomic commit--> succeeded
   |                           |
   +---- real failure --------+--> failed
   +---- expired lease -------+--> interrupted
terminal -X-> running/succeeded (no takeover, replay or invented recovery)

draft v1/r1 -> saved v1/r2 -> approved v1/r2 -> superseded v1/r2
                                  |
                                  +--> explicit human copy -> draft v2/r1
approved/superseded content -X-> PUT (immutable history)

upgrade additive schema -> drift/preservation tests -> start local API -> UI
     failure -> stop changed process -> inspect actual error -> operator recovery
     -X-> destructive downgrade/drop/reset of development data
```

The existing current auth/project and PM diagrams remain applicable. ARCHITECTURE.md
must add the new run/source/task relationships and combined admission rather than
leaving its Stage03-only diagram as a description of the new system. Stage03 historical
verification diagrams/reports must remain immutable, clearly labeled as history.

## Failure modes registry

| Path | Failure | Rescued design | Required test | Visible outcome | Safe diagnostics |
|---|---|---|---|---|---|
| Source | Unapproved/foreign/superseded source | Yes | API integration |404/409 before dispatch | Code and IDs |
| Admission | Cross-agent concurrent request | Yes, shared counts | PG interleaving |429 without duplicate dispatch | Admission stage |
| Provider |503/504, empty/refused/malformed body | Yes | Adapter/unit + PG double | Failed run, no architecture | Actual status/category |
| Validation | Cycle, dangling/cross-project edge | Yes | Pure graph + SQL/API |422, saved graph unchanged | Validation category |
| Trace | Foreign criterion, omitted deferred obligation | Yes | Source/coverage tests | Invalid refs or inherited uncertainty remains | Source identity |
| Publication | Revocation/deadline/unknown commit | Yes | Controlled interleaving/fault | Failure/interruption/unknown, never fake success | Commit stage/reference |
| Editing | Stale revision/network failure | Yes | PG + browser | Conflict and preserved local text | Exact revision |
| Approval | Corrupt graph/missing coverage/stale source | Yes | PG + browser | Rejected with repair guidance | Validation category |

No silent critical gap is accepted. Each "Yes" describes the required implementation
and test, not a claim that the not-yet-written code passed. Operator restoration and
future durable execution remain explicitly distinct from automatic retry.
