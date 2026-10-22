# ORBA Stage04: Architect Agent and Task Dependency Engine

Recorded 2026-10-21. **Stage04 verdict: PARTIAL.** Deterministic implementation is
complete; the Architect has not made a paid/live generation request. Stage03's own
VERIFIED checkpoint remains historical evidence, not Architect verification.

## A. Implementation summary

The existing application now supports approved Product Plan -> explicit Architect
request -> validated technical proposal -> relational engineering tasks/dependencies/
traces -> human draft editing -> explicit Owner/Admin approval. Everything stays in
the same authenticated workspace and existing themes. Tasks are planning proposals;
no code, migration, tools, tests, deployment or agent handoff executes from a design.

The official Google GenAI request core is shared with PM. Production has no controlled
provider mode. Controlled deterministic tests replace only the model dependency;
authentication, CSRF, API, PostgreSQL, browser and persistence remain real.

## B. Architecture and data model changes

Alembic `7dd7671f9417` adds six tables: `architect_runs`, `architecture_versions`,
`architecture_components`, `engineering_tasks`, `task_dependencies`, `requirement_traces`.
No original table/record is dropped. Migration preservation evidence covers all 13
existing rows across 12 existing tables; an automated fresh-schema upgrade test also
preserves a real user hash/project/approved PRD graph and reapplies head safely.

Runs bind the authoritative source PRD ID/version/revision/hash, original session,
request UUID, prompt hash, provider metadata, deadline, diagnostics and actual outcome.
A new unapproved PRD does not stale an agreement; a new approval does. Recheck current
approved source before dispatch/publication/architecture approval. Free draft copies
retain source and lineage. Approved/superseded content stays immutable. Draft PUT
requires the saved expected revision; approval binds exact version/revision/actor/time.

Root JSON holds design sections once; components/tasks/edges/story traces are relational.
Composite foreign keys scope edges and source traces to the correct architecture,
project and source. Components and tasks retain stable node UUIDs during draft edits.
Full multi-query reads hold the architecture root share lock to avoid mixed revisions.
No DB transaction spans a provider request. Shared PM/Architect admission, short
transactions and fenced terminal transitions preserve existing session/quota guarantees.

Important files:

| Files | Responsibility |
|---|---|
| `orba/architect_schemas.py`, `prompts/architect_v1.txt` | Versioned full strict proposal contract and untrusted-input prompt |
| `orba/task_graph.py`, `architect_traceability.py` | DAG algorithms, exact source references, structural coverage and obligations |
| `orba/architect_models.py`, migration `7dd7671f9417` | Additive relational persistence and ownership constraints |
| `orba/architect_repository.py`, `architect_service.py`, `architect.py` | Atomic lifecycle, source fencing, revisions, approval and protected APIs |
| `orba/pm_provider.py`, `architect_provider.py`, `planning_admission.py` | Shared official SDK transport and bounded admission, separate agent prompt/source rules |
| `apps/web/src/components/architecture.tsx`, `architecture-editor.tsx`, `task-graph.tsx`, `project-planning.tsx` | Existing-project architecture/editor/graph experience |
| `scripts/architect_verification.py`, `architect_false_success.py`, `inspect_architect_run.py` | Stage/agent-bound gates, genuine incorrect-assertion experiment and independent SQL audit |

Backend filenames above are relative to `apps/api`.

## C. Task dependency algorithm and validation evidence

Edge convention: prerequisite -> dependent; B.dependencies=[A] means A precedes B.
A real bounded Kahn algorithm produces deterministic topological ordering using
explicit display order/stable keys for ties. Traversal computes ancestors, dependents
and transitive impact. DFS supplies an actual cycle path. Reject missing/self/duplicate
edges, duplicate keys, two/multi-node cycles and cross-owner SQL references. A valid
edgeless graph is allowed. Display reordering never overrides an edge.

Every task remains proposed/needs clarification. Derived readiness means no unmet
prerequisites in the unexecuted planning model, never implemented/tested/deployed.
All non-root prerequisites remain unmet because Stage04 does not execute tasks.

Traceability validates real saved story/requirement keys and exact criterion parentage.
Each task's component links must cover its referenced stories. All contributing tasks
for prerequisite stories must precede each dependent-story task. Coverage reports gaps,
orphan tasks, component gaps, clarification and open decisions. Exact gap exceptions
and blocking decisions require saved-revision human dispositions before approval.
Inherited PRD uncertainty remains server-owned outside generated/editable text.
Coverage is structural linkage, not proof of semantic completeness or implementation.

## D. API and frontend functionality

All routes under `/api/v1/projects/{project_id}` require current workspace membership.
Mutations require Origin/CSRF, workspace/project locks and current original-session
checks. Viewer reads; Member/Admin/Owner generate/edit/copy; Owner/Admin approve.
Unrelated IDs return 404 without private content.

Implemented routes: GET architect-source; POST/GET architect-runs and GET exact run;
GET architectures/exact version; PUT exact draft; POST draft copy/approve; GET tasks,
graph and coverage. Typed synchronized view responses carry saved revision/hash.

Product Plan remains the default view. Architecture and Task Graph share one local
editor, exact source summary, version/state history, actual run metadata and all
proposal sections. Native SVG nodes/edges synchronize with an accessible native task
list/detail. Add/remove dependencies, reorder ties, inspect impact/coverage and save
validated edits to PostgreSQL. Dirty previews never claim validated saved state.

Save/Discard/Cancel protects deliberate navigation and workspace changes. A body-level
native dialog remains visible when Architecture is hidden by the Product Plan tab;
rejected saves announce their error there and preserve local input/saved records.
Session expiry/logout clears immediately. SessionStorage holds scoped nonsecret
request/copy UUID references only. Unknown outcomes use GET-only recovery. Explicit
retry confirms the exact own terminal run, then creates a new audited UUID/attempt.
No generation, continuation, model switch or POST retry occurs automatically.

## E. Actual commands and exit codes

| Command | Native exit | Duration (s) |
|---|---:|---:|
| `docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres` | 0 | 1.027 |
| `uv sync --locked --directory apps/api` | 0 | 0.084 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile` | 0 | 1.648 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm peers check` | 0 | 1.502 |
| `uv run --directory apps/api alembic upgrade head` | 0 | 2.212 |
| `uv run --directory apps/api alembic check` | 0 | 2.584 |
| `uv run --directory apps/api pytest -q --junitxml=E:\BrosKi\OBRA\docs\evidence\stage04\20261021T174944Z-A-1ce59ebc\backend.xml` | 0 | 225.153 |
| `uv run --directory apps/api ruff check .` | 0 | 0.196 |
| `uv run --directory apps/api ruff format --check .` | 0 | 0.35 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm typecheck` | 0 | 4.947 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm lint` | 0 | 24.827 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm build` | 0 | 18.893 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e` | 0 | 392.117 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:controlled` | 0 | 425.261 |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:architect` | 0 | 652.983 |

Gate A wrapper: `pwsh -NoProfile -File scripts/verify.ps1` exited 0 (1762.259s). Gate C: `uv run --directory apps/api python -m scripts.architect_verification summary` exited 2/PARTIAL. Offline configuration check exited 1 (Architect model missing); live script without `-AllowPaid` exited 2 before dispatch. [Native supporting command evidence](evidence/stage04/closure-20261021/development-command-artifacts.json).

The complete commands, timestamps, PIDs, durations, native exits, source manifests,
JUnit/browser reports and artifact SHA256s are in the immutable Gate A receipt below.
No skipped/flaky/retried result can pass this verifier.

## F. Deterministic Gate A results

| Gate | Result | Actual exit | Evidence |
|---|---|---:|---|
| A deterministic | PASS; all 15 required commands | 0 | [Immutable receipt](evidence/stage04/20261021T174944Z-A-1ce59ebc/receipt.json) |
| B real Architect | NOT RUN; fresh paid authorization/model selection required | NOT RUN | No live Architect request dispatched |
| C source-bound verdict | PARTIAL | 2 | [Actual output](evidence/stage04/closure-20261021/stage04-gate-c-console.log), [native exit](evidence/stage04/closure-20261021/stage04-gate-c-command.json) |


Actual executed results: **386 backend tests; 60 core browser; 33 PM controlled-provider browser; 33 Architect controlled-provider browser**. Browser total: 126 across desktop/mobile/tablet. **Zero skips, flaky cases, xfail or retries.** No controlled result is counted as live-model evidence.

The original 285 backend, 60 core browser and 33 PM-controlled browser identities remain
mandatory. New coverage is additive; controlled provider tests are labeled explicitly.
Real-PG cases cover approved-source fencing, original-session revocation, exact replay,
concurrency/shared admission, publication visibility, rollback, graph constraints,
coverage, revision conflicts, roles, CSRF and tenant isolation. A real SQL division-by-
zero forces rollback; another transaction cannot observe an incomplete graph.

The SDK transport tests use the actual maintained SDK against isolated synthetic HTTP;
they prove request/timeout/retry/error handling, not Google service success. Gate A
clears every runtime key alias/model/live opt-in. No paid request is required or sent.
The SDK emits one existing Python3.14 deprecation warning; all checks still execute.

## G. Negative-path and false-success evidence

Controlled actual SDK HTTP503/504, provider timeouts, malformed JSON/schema and cyclic
responses leave truthful failed runs and no architecture. Previously approved PRDs
and architectures remain unchanged. Invalid dependency saves return 422 and keep the
saved revision/hash valid. Invalid/stale source, role/CSRF/session and cross-workspace
requests are rejected. Invalid DAGs/coverage cannot be approved.

[Isolated experiment](evidence/stage04/20261021T174932Z-expected-failure-a0c50ff4/receipt.json) used real authentication/API/PostgreSQL plus a labeled controlled 503 provider. Its deliberately incorrect failed==succeeded assertion genuinely exited **1**, with an actual failed run and zero architectures. The evidence wrapper exited 0 only because that expected nonzero failure was observed; production_test_pass=false. It is excluded from normal discovery and is not one of the 386 passing tests.

Development failures remain visible: initial browser checks failed on recovery wording,
alert scope, a UTF8 helper encoding error and invitation-navigation synchronization.
Those causes were repaired without removing assertions. A later focused browser check
exited 1 before tests because Docker Desktop was unavailable; its actual PostgreSQL
connection-timeout log is preserved. Starting the existing Docker Desktop and restoring
only guarded test PostgreSQL exited 0; the focused repair passed3/3 viewports. The
first complete Stage04 A passed379 backend/60 core/33 PM/30 Architect browser cases on
source55d54ed5..., then the hidden-tab modal defect was repaired and the entire gate
rerun. That older PASS is retained, never reused to certify the changed source.
An ad hoc collection launcher also exited 1 on bare npm resolution; rerunning through
the existing native executable resolver exited 0. Collection lists define required
identities; they are not test execution evidence.

A separate external report-helper draft exited 1 with `SyntaxError: invalid decimal literal` before any writes because of nested quote delimiters. Report assembly was corrected using a direct script; implementation source, tests and Gate A were unaffected. This tooling failure is separate from the passing application suite.

## H. Source fingerprint and evidence integrity

Current relevant source fingerprint: `07bf0deb6c2a0cdaed19a4441619404fbda0f57674a0db9171cb3ea47628eab7` (165 files). A start/end/current match. Policy `git-relevant-source-v2-including-root-template` covers implementation/tests/scripts/infra/lockfiles/nonsecret templates, excluding generated outputs, credentials, docs and evidence. Stage04 prompt/schema/policy hashes are embedded in the receipt. A receipt SHA256: `64541615f31e619235fd60a2cecaedf702d6464a04855fab048466ed2bbc22ad`. [Preservation audit](evidence/stage04/closure-20261021/preservation-audit.json).

Checkpoint `1aeb882cf9e788948df5ca5eac52e2a682a1f487` remains HEAD. No Stage04 commit,
staging, push, discard or paid generation occurred. Credential bytes and20 historical
receipts/325 referenced artifacts passed the fresh preservation audit. The original
Stage03 verification document is archived byte-identically in
[VERIFICATION_STAGE033_CHECKPOINT.md](VERIFICATION_STAGE033_CHECKPOINT.md).
Its actual acceptance report is [VERIFICATION_STAGE033_LIVE.md](VERIFICATION_STAGE033_LIVE.md).
Historical 503/504 failures are preserved and not relabeled. [Final preservation/source/ports audit](evidence/stage04/closure-20261021/final-audit.json).

## I. Prepared live Gate B configuration and reproduction

From `E:\BrosKi\OBRA` with Docker Desktop running:

```powershell
npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile
uv sync --locked --directory apps/api
docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres
pwsh -NoProfile -File scripts/verify.ps1
uv run --directory apps/api python -m scripts.architect_false_success
uv run --directory apps/api python -m scripts.architect_verification summary
```

The summary exits 2 for PARTIAL while live B is missing. The experiment wrapper exits 0
only when its separate deliberately incorrect pytest child genuinely exits 1. Do not
run backend/browser suites concurrently against the shared guarded test database.

For development, preserve existing dotenv, start Compose postgres, apply Alembic head,
then run FastAPI/Next in separate terminals as documented in README. Never clear the
named development volume. Offline Architect setup check sends no external request:

```powershell
uv run --directory apps/api python -m scripts.check_architect_config
```

Current Architect model is unset, so this correctly exits 1/BLOCKED. It does not inherit
PM's model. `ORBA_ARCHITECT_API_KEY` optionally overrides the resolved existing server
credential when nonempty. No credential or model was changed. The existing PM dotenv
remains3.8/low. Recommended FUTURE separately authorized profile is Gemini3.6/minimal,
based on Stage03's actual earlier success, not proof of Architect/account availability.
Defaults: one active request, zero SDK/transport retries,90s provider/95s transport/
100s envelope,6000 combined output/thinking tokens,96000 UTF8 input content bytes.
Next generation proxy290s, browser request260s/test300s and gate child600s are outer
bounded observation envelopes; SQL lock1s/statement2s transactions stay short. There is
no token truncation/paid continuation or guarantee this output budget will suffice.

Only AFTER fresh explicit owner authorization, the prepared command would be:

```powershell
$env:ORBA_ARCHITECT_MODEL = 'gemini-3.6-flash'
$env:ORBA_ARCHITECT_THINKING_LEVEL = 'minimal'
pwsh -NoProfile -File scripts/verify-architect-live.ps1 -AllowPaid
```

It first validates applicable A/source/profile and performs one bounded read-only
metadata GET (no generation), then one browser worker forwards at most ONE real
Architect generation POST. Additional PM/Architect generation POSTs are blocked and
fail the test; SDK retries 0. The source is a clearly human-authored real persisted PRD,
approved through the real UI without PM generation. Reuse the single real architecture
for strict schema/source/DAG/coverage, independent SQL, browser graph/display, criterion
editing/reload, explicit approval/reload and unrelated-user 404/UI denial. Record real
model/response/request IDs and usage only when supplied, actual command exits and
source/profile/A-receipt/artifact linkage. Missing/controlled/stale proof cannot pass C.
No part of this prepared live workflow has dispatched a paid generation.

## J. Remaining limitations

Own live Architect B is NOT RUN and requires fresh owner authorization plus explicit
model selection. Provider availability/schema acceptance/latency/real output quality
are unverified for Architect; historical PM success does not substitute. Readiness
metadata is not generation proof. No dollar cost is invented and token/input caps are
not a precise billing ceiling.

Coverage validates structural traceability; human review must assess design quality,
tradeoffs, requirement adequacy and uncertainty. No automated technology-installation,
security certification, implementation, test or deployment claims are made. Current
scope remains local development with the existing authentication limitations in README.
History is paginated in the API; the UI shows its bounded latest 20 architecture entries.
Approved history is immutable; intermediate old draft bodies are not a full edit audit.
Native Chromium desktop/mobile/tablet emulation does not certify every real device or
browser. No Stage05 orchestration, coding/QA agents, execution, sandboxes or handoffs.

## K. Stage04 verdict

**PARTIAL**. Deterministic implementation/verification and prepared paid opt-in gates
are complete. Own freshly authorized real Architect Gate B has not run; VERIFIED is
forbidden until applicable A+B evidence both pass on the same relevant source/profile.
