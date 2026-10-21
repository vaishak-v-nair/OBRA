# Stage 03 engineering plan review

Full review,2026-10-19, main/e3fccd6. Eng runs after completed CEO->Design->DX amendments. Scope is docs/STAGE03_PLAN.md plus actual Stage02 source; this is not a review of implemented PM code. Parent /autoplan auto-decides mechanical issues and retains genuine taste choices for the final gate. All execution claims are limited to the unchanged Stage02 baseline and external design sketch. No PM/provider tests have executed.

## Step0: scope, actual source and complexity challenge

The plan touches more than eight files and introduces more than two data types. That triggers the skill's complexity smell. Keep the owner's complete one-PM-agent scope under /autoplan's explicit no-reduction override, while rejecting accidental infrastructure: no second auth system, queue, Redis, worker fleet, generalized agent bus, multi-provider routing, duplicate current-document JSON tree or new global frontend state. The small alternative is a focused PM router/service/schema/provider/prompt, five related tables, an inline project-local reader/editor and existing transport/verification extensions. This remains substantial because the user explicitly requires real persistence, security, failure handling and live browser evidence; omitting them is not a valid reduction.

### What already exists

| Subproblem | Inspected authority / motivating line | Reuse and minimum extension |
|---|---|---|
| DB lifecycle | db.py:22–23 `with Session(request.app.state.engine) as session: yield session` | Capture scalar identity IDs and close before provider; new short sequential transactions |
| Session authority | security.py:61–63 revoked null/expiry/active User conditions | Recheck these in finalization; row-lock session/user to serialize logout |
| Workspace writes | security.py:105 `query = query.with_for_update()` | Preserve workspace-before-role rule for PM mutations |
| Logout | auth.py:150–151 `identity.revoked_at = now(); db.commit()` | Existing session-row update provides finalization serialization boundary |
| Private project lookup | main.py:137–149 joins Workspace/WorkspaceMember, missing404 | Extract helper without weakening existing project access |
| DB waits | db.py:17 connect_timeout3, statement_timeout5000 | Finite pool wait and PM-local transaction/lock deadlines; no migration-wide PM settings |
| Safe errors | main.py:49 validation field/message, SQLAlchemy handler logs exception type | PM-specific safe code/paths/run/diagnostic envelope, no raw secrets |
| Transport | api.ts:9 retains only message/status; line20 fixed20s | Preserve simple old callers; typed PM errors/PUT and PM-only long timeout |
| Proxy | route.ts:15 fixed15s, export lacks PUT | Exact generation route/method matching, streamed body bounds and separate deadline |
| UI | project detail/ProjectEditor, SessionProvider/AuthGate, semantic globals.css | Add project-local PM section; preserve real auth/shell/theme/create flow |
| Tests | prepare_tests.py:19 DB/role only; conftest.py DB-only guard | Shared strict host/port/role/DB guard before any mutation |
| Migrations | test_legacy.py creates isolated test schema, applies0001->head | Add populated actual Stage02 `0febbe526f54`->Stage03 preservation/repeated-upgrade test using same guarded pattern |

No product implementation is inferred from the existence of a planning file. Git history is one explicit checkpoint, with no remote/review-driven refactor history to analyze. There is no existing TODOS.md at intake. Required new package is only official OpenAI SDK with locked compatible stable dependencies at implementation time; no new distribution artifact type is proposed. Local source/locks are the distribution; public publishing/CI deployment is explicitly deferred.

### Search and built-in check

[SQLAlchemy Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) confirms transaction scope and per-thread ownership; [FastAPI concurrency](https://fastapi.tiangolo.com/async/) supports ordinary def endpoints in its worker pool. [PostgreSQL18 locking](https://www.postgresql.org/docs/18/explicit-locking.html) supplies row/advisory transaction locks and stresses consistent ordering. [Python asyncio timeout](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) supplies the async-call deadline. These primary sources were actually searched/opened; they do not prove the application implementation works.

[Layer1] use PostgreSQL constraints/transactions, SQLAlchemy sessions, FastAPI worker dispatch, official AsyncOpenAI with one scoped event loop and native UI controls. [Layer2] compose only the PM state machine, provenance/graph validator and typed transport. No custom queue, retry engine, session manager or async ORM engine is needed. A normal sync route owns sequential DB phases; a scoped asyncio.run executes the bounded AsyncOpenAI call with no DB checkout. This avoids sharing sessions across tasks or abandoning DB worker threads. Two durable active slots bound model work; thread occupancy/health responsiveness still require measurement. No hard real-time/network-partition claim is made.

## 1. Architecture review

```text
Browser existing SessionProvider/AuthGate + workspace preference
  -> ProjectDetail
     -> ProductPlan reader / local editor / generation controls
        -> typed PM client (no credentials / no automatic POST retry)
           -> existing same-origin Next proxy (+PUT, exact PM deadline/body bound)
              -> FastAPI session + Origin/CSRF + private project helper
                 -> PM router (sync request worker)
                    -> PM schema + shared integrity/source validator
                    -> PM service / fresh short SQLAlchemy Sessions
                       -> PostgreSQL workspace/session locks + run lease/CAS
                       -> plan root ->epics ->stories ->criteria
                    -> one scoped asyncio.run
                       -> official AsyncOpenAI ->configured real model
                       <- actual response envelope/nullable usage
                    -> final current-session/member check
                    -> atomic full plan + succeeded commit

Existing project/auth/team endpoints remain separate/reused.
Lifespan/read reconciliation ->expired active runs only ->interrupted; no resume.
```

Eight architecture findings, each confidence8–9/10 from the quoted source or explicit plan omission; these are future integration risks, not demonstrated Stage03 exploits:

| ID / severity | Finding, evidence and recommendation | Tradeoff / rejected option |
|---|---|---|
|E-A01 P1,9| Request-lifetime DB/ORM identity cannot survive provider wait safely; db.py22–23. Snapshot scalar IDs, end transaction, keep short phases in one worker | More explicit transaction code; reject held connection/lock during SDK |
|E-A02 P1,9| Workspace lock alone cannot serialize logout; auth.py150 update is independent. Finalization locks workspace->project/run/plan->original session/user, rechecks using DB clock | Logout may wait for bounded commit; reject cached authorization |
|E-A03 P1,8| Replay hash initially mixed current snapshot with client intent. Separate canonical explicit-input hash from immutable execution snapshot/hash; replay before fresh capture | Two named hashes; reject spurious409 after project/model changes |
|E-A04 P1,8| Keys/FKs must cover every editable node and cross-project link. Stable criteria/confirmation/requirement keys; composite generating-run/copy/child ownership FKs and plan-wide uniqueness | Small ownership columns; reject positional origin or unrelated single FKs |
|E-A05 P1,8| Pending/running and commit-error windows need deadlines from first durable reservation, terminal CAS and fresh-session reconciliation | Extra states; reject failed overwrite after ambiguous successful commit |
|E-A06 P1,8| Save/approval/copy share version allocation and exact revision. Durable copy key/source hash, workspace/project serialization, immutable approvals and monotonic current approval | Copy replay may return now-approved original; reject accidental new copy |
|E-A07 P1,8| One SDK timeout doesn't bound body/auth/DB/finalization. Adopt explicit full budget, per-transaction limits, deadline checks and PM-only long transport | Long worker occupancy/local timing limits; reject second ORM engine/uncancelled DB threads |
|E-A08 P1,9| prepare_tests19 guard omits host/port; future tables add destructive blast radius. One guard before all migration/reset connections | Reject nonstandard unsafe targets instead of relaxing isolation |

All PM lookups authorize the project before nested IDs, pagination or configuration. Viewer read only; Member generate/edit/copy; Owner/Admin approval. Every write reuses exact Origin/CSRF and current membership under workspace lock. Provider output cannot choose workspace/actor/model evidence/permissions, execute instructions or request tools. Root JSONB deliberately excludes relational children; immutable snapshots are execution evidence, not competing current state. Retained secrets and raw headers/bodies are excluded from public/internal diagnostic payloads. Internal reason preserves actual safe exception/code/status/locations/IDs; absent evidence remains null.

Publication linearization is explicit: logout committed before session lock prevents publication; logout after finalization's lock waits and revokes subsequent access. Session expiry is tested at the final authorization point using database time. Membership changes serialize with the workspace lock. Lock order for all PM mutation paths is global admission(if start)->workspace->project->run/plan->session/user; no code acquires global admission after a workspace lock. Expiry reconciler changes only active expired run status through conditional updates, never plans, and takes no reverse workspace lock. No transaction waits for the model.

## 2. Code quality review

Four issues, confidence8–9/10. E-Q01: extract the existing private project query once, preserving its join and404 behavior; duplicate route-specific authorization invites drift. E-Q02: one Pydantic schema/integrity engine supports provider validation, persistence assembly, full PUT and approval; provider-origin and human-change authority are separate server operations, not competing validators. E-Q03: use one typed safe transport envelope without rewriting existing simple project callers; preserve caller abort signals and avoid a PM-specific clone of auth/CSRF. E-Q04: split the frontend by reader/editor/state responsibility, avoiding a thousand-line component or generic recursive form framework. Scope small native controls and semantic styles; do not duplicate current child tree in root JSON.

Version/hash the prompt separately from business logic. Use typed actual provider metadata; no default zero usage, invented cost or fake timestamps. Code comments should retain concise ASCII state/transaction boundaries in models/service and test setup. Existing architecture/test diagrams require Stage03 updates during implementation, while Stage01/02 historical verification remains archived unchanged. Security logs accept static event codes/UUIDs only; no SDK debug logging. A PM integrity error on read is a safe error requiring operator attention, never an automatic repair that fabricates a valid artifact.

Stable identities apply to every source-bearing node, independent of order. Server compares content to saved keyed nodes; unchanged origin remains, changed/new content receives actual human actor. Client origin claims never create authority. Copy stores immutable source revision/hash/evidence, and human confirmation dispositions carry actor/time/reason. All collection and aggregate limits are shared by API/provider/editor where appropriate, with the server as authority. Generated source quotes establish textual traceability only; they do not prove semantic truth.

## 3. Test review — complete branch audit

Read actual pytest discovery/conftest/legacy fixtures, project/auth/team tests, browser helpers/specs/config, API transport and affected page/editor. Frameworks are real Pytest/TestClient/SQLAlchemy PostgreSQL and Playwright Chromium workers1/retries0; no CLAUDE.md testing authority supersedes AGENTS. Stage03 tests do not yet exist. Preserve44 backend/42 browser scenarios, not merely counts. Critical regression risks are shared project authorizer extraction, request cancellation/error handling, proxy methods/deadlines/body parsing, session clearing and schema readiness.

The full [Stage03 test plan](../STAGE03_TEST_PLAN.md) enumerates every new branch/user flow, all20 owner backend guarantees, security/race/bounds matrix, live quality rubric, responsive/error journeys, migration preservation and command order. Actual external copy: C:/Users/vaish/.gstack/projects/OBRA/vaish-main-eng-review-test-plan-20261019.md. Neither copy is test execution evidence.

```text
Coverage group / new path                             Planned evidence (all PM GAP now)
G01 session/CSRF/Origin/role guards                    API real DB + old regression + browser
G02 private project/context/run/plan lookup            API exact UUID + unrelated browser
G03 streamed body/brief/type/aggregate bounds          real proxy/API + pure schema units
G04 provenance/explicit context/snapshot freshness     schema units + actual DB save + LIVE EVAL
G05 reservation/hash/key replay/mismatch               independent DB races + LIVE same-key replay
G06 project/global/account admission                  real DB reservation races/window boundaries
G07 pending->running/connection release               DB pool/lease assertion + isolated phase unit
G08 missing provider capability/configuration         actual Settings/API/browser no-plan failure
G09 timeout/auth/rate/connection/status mapping         isolated SDK error units + genuine failure
G10 response/model/usage/refusal/incomplete/empty       schema/provider units + LIVE envelope
G11 keys/refs/cycles/full valid document               pure validators + assembled actual DB
G12 original-session/user/member publication authority real DB lock schedules + isolated lifecycle
G13 relational draft+success/rollback/unknown commit   DB constraints/storage + LIVE persisted success
G14 cancel/crash/lease/late terminal CAS               real DB/process probe + isolated cancellation
G15 run history/own-key empty/active/terminal           actual API pagination + browser + LIVE
G16 plan history/detail/order/integrity                actual DB/API, authored fixtures + LIVE
G17 full PUT/revision/state guards                    real API/DB + browser reload/conflict
G18 reorder/add/remove/server human origin             unit diff + real DB/API + nested browser
G19 exact approve/blockers/supersede/actor/time         real API/DB races + LIVE browser
G20 copy origin/source/key/version concurrency         actual API/DB, no model call
G21 empty/current-approved/new-draft reading           actual browser fixture/DB, no fake generation
G22 explicit Generate/pending/failed/unknown/status    browser + actual config negative + LIVE EVAL
G23 long nested editor/error focus/limits              authored fixture real API/browser all sizes
G24 dirty version/nav/conflict/security clearing       real browser tabs/offline/auth lifecycle
G25 exact clean revision approval/reload               browser Member/Owner/Viewer + LIVE
G26 unavailable/offline/rejected versus unknown        actual network/config/error UI, no POST retry
G27 same-origin PUT/body/deadline/signal/headers        actual proxy/browser and original regressions
G28 liveness/readiness/PM-disabled core availability    real migrated DB/offline/schema tests
G29 test guard/populated migration/repeated upgrade    real isolated PostgreSQL schema, no dev reset
G30 real API + real browser structured/quality eval    TWO actual model generation flows required
G31 Full/Core/negative/incorrect assertion exits       actual commands; exit1 experiment separate
G32 docs/env aliases/reproduction/evidence safety      config tests + actual reproduction audit
```

Five test-gap decisions: E-T01 add every assigned branch, including no-success cases, with no placeholder green drivers; E-T02 real DB assertions use new sessions and verify unchanged protected records after denial; E-T03 strictly separate human authored fixtures/isolated provider doubles from live generation; E-T04 explicit live API+browser gates with nonzero credential blocker and a human quality rubric; E-T05 retain all prior behavioral tests plus actual unsafe-target rejection/populated migration/expected-failure experiment. These five coverage requirements are mechanical P1, confidence9/10 from the owner's explicit contract and absent PM implementation. They are not five executed failures.

Deterministic backend positives for storage/edit/approval use explicitly human-authored plan fixtures with no fabricated successful model run. Provider doubles stay inside isolated unit/error tests; they cannot replace DB/API/browser integration or either real model flow. Reservation/concurrency tests exercise actual PostgreSQL service functions without claiming model execution. NegativeCaseA uses actual missing runtime configuration or a genuine SDK failure; CaseB is the explicit malformed-output double. Expected wrong assertion is outside normal discovery and must exit1 separately. No skips/xfail. Mandatory live/browser output-quality, role/isolation/persistence failures prevent VERIFIED even if schema validation succeeds.

No raw generated text equality or fabricated business verification score is used. The live habit-tracker case checks supplied daily check-ins/streaks/weekly summary, one-user/no-social boundary, story/criterion observability, valid graph, no unsupported confirmed facts and proportionality; retain qualitative shortcomings. Two real successful model calls are planned minimum, one through API and one clicked in browser, with bounded tokens/time and no automatic retry. Extra paid regeneration must be explicit, not hidden in ordinary test setup. Credential absence remains unresolved external dependency.

## 4. Performance review

Four issues, confidence8/10: E-P01 bound full documents and graph validation, with linear keyed maps/DFS rather than repeated scans and cycle recursion without visited sets. E-P02 eager/bulk child queries/inserts, history summary-only, no per-story API requests; assert a bounded query envelope at the40-story/160-criterion authored maximum. E-P03 separate provider time from worker/DB time and bound admission, pool/lock/transaction waits; prove a checked-out DB connection is not retained during actual SDK wait and health/auth remain responsive. E-P04 use deterministic paginated indexes, bounded5s expiry batches and GET backoff; no infinite polling, hidden model checks or unbounded auto-retries.

Operational limits adopted in the main plan supersede CEO's provisional lease: providerT5..180 default60, output512..16000 default6000; pending20s, runningT+45s; API operation300s, PM proxy330s/client350s plus CSRF10s. Preflight40+reserve/start30+provider180+cleanup5+validate5+finalize15+one error-reconcile15+serialize5=295s. Pool2/connect3 plus PM-local PostgreSQL transaction10/statement2/lock1 sit inside each15s phase. Deadline checks fence provider start and publication. Local OS/network stalls are not hard-real-time certified; unknown acknowledgements remain unknown rather than false failures. Ordinary15/20s requests remain unchanged. Settings must validate bounds; actual timing/load evidence is pending.

Limits: brief10000/instructions4000/context20000/serialized48000 chars; actual streamed POST256KiB/PUT512KiB; document80000chars/512KiB;8epics/40stories/160criteria/40FR/20NFR. Every other collection defaults max20, target users/goals max10, dependency/reference lists max10/story, stable keys max64; aggregate document/node bounds dominate individual maxima. Labels200/prose2000/GWT500 each. No truncation. Model output can be much smaller than maxima.6000 default output tokens does not guarantee every allowed maximum document can be generated; incomplete responses fail honestly. No dollar price or throughput claim is invented.

No broad protected-data cache or speculative prefetch. Pending/failed runs retain actual immutable input/evidence under current workspace authorization; storage retention/deletion is a stated future policy limitation. Admission limits bound locally active records and attempts, not provider billing/exactly-once execution after process loss. Global transaction advisory lock is short and precedes workspace locks. Query indexes cover project/version, run project/created/status/deadline and initiator/time budgets; benchmark them on actual test data before reporting performance.

## Failure modes registry and critical-gap assessment

Every G group above has at least one realistic failure, proposed handling and assigned test. All handling/tests are planned; no runtime coverage is claimed.

| Group | Realistic failure | Handling / visible result | Assigned coverage |
|---|---|---|---|
|G01| Session expires/invalid CSRF |401/403; sign-in/refresh, no protected content | auth/API/browser |
|G02| Foreign exact UUID/context | private404, no document/diagnostics | isolation API/browser |
|G03| Chunked oversize/empty input | bounded413/422 before model | body/schema/API |
|G04| Fabricated source quote | validation failure; no valid draft | provenance unit/LIVE rubric |
|G05| Double click/project text changed replay | original key/outcome or payload409; no new call | DB races/LIVE replay |
|G06| Concurrent cross-project saturation | finite safe429/Retry-After | real DB admission |
|G07| Crash after pending commit | deadline->interrupted, no stuck active | DB/process probe |
|G08| Key/model absent | safe setup+failed run if writable; no plan | actual config API/browser |
|G09| SDK timeout/rate/auth/network | actual safe category/metadata; failed/no plan | isolated mapping + genuine negative |
|G10| Refusal/truncation/missing usage | reject invalid output, preserve actual envelope/nulls | unit + LIVE |
|G11| Cyclic dependency/empty criterion | strict validation, linked repair, no save | schema/API/editor |
|G12| Logout/removal during call | serialized final denial; no publication | DB authority schedules |
|G13| Child constraint/commit ack loss | atomic rollback or unknown->GET; terminal immutable | real DB fault/LIVE |
|G14| Late response after lease/sweep | conditional terminal fence; no stale plan | lease/CAS/process |
|G15| Poll/network lookup missing | observed empty/unknown, stop/backoff; no retry POST | actual API/browser |
|G16| Corrupt relational assembly | safe integrity error; no silent repair | DB invalid fixture/API |
|G17| Stale full PUT/approved edit |409/local buffer retained | API/two-tab browser |
|G18| Positional move spoofs origin | stable-key server diff, actual human attribution | pure diff + DB |
|G19| Concurrent/old-version approval | exact CAS + one approved, no regression | real DB/API/browser |
|G20| Repeated copy after approval | original immutable copy returned, no model | real DB/API |
|G21| Empty/newer draft hides agreement | distinct states/approved default | real browser fixture |
|G22| Lost Generate response | actual pending/terminal GET, no imaginary progress | network/browser/LIVE |
|G23| Last hidden criterion invalid | summary opens/focuses control, retain fields | maximum fixture/browser |
|G24| Dirty nav/account switch | explicit nav choice; mandatory auth clear | real browser |
|G25| Visible unsaved changes approved | disable; exact saved confirmation/revision | browser/API |
|G26| Offline save/approval | operation unknown/reconcile, not false success | real network/browser |
|G27|15s proxy cuts real call/PUT absent | exact-route bounded timeout, PUT, typed errors | real proxy/LIVE |
|G28| Old schema or DB offline | readiness503, no model call; liveness independent | real DB/schema |
|G29| Test points at development | reject before connection/mutation | guard test + migration |
|G30| Missing credential/poor live output | nonzero BLOCKED/FAIL, no VERIFIED | actual API/browser eval |
|G31| Green verifier hides live omission | Full nonzero; Core explicit NOT RUN; experiment exit1 | actual command evidence |
|G32| Stale docs/leaked diagnostics | required stage/docs audit and safe artifacts | reproduction/schema/log audit |

Critical plan gaps before amendments: final logout serialization, replay/snapshot identity, stable keys/composite ownership, copy request identity and total deadline. All now have specified handling/tests; zero *unassigned* critical plan gaps remain. Every PM implementation/test is still unexecuted. Missing runtime credentials/live evidence remain a delivery blocker, not resolved by the registry.

## NOT in scope and deferred work

Architect/coding/QA agents, execution, GitHub/Skills/Model Hub, queues/resumability/presence/cloud/canvas, public deployment and production certification are excluded by owner scope. Full per-edit audit/diff, pricing/billing budget, retention policies, hosted setup/CLI/SDK, public community/support and broad OS/native-device certification are deferred with context/effort/dependencies in TODOS.md. None blocks implementing the requested local PM flow; absence must remain visible in final limitations. Model runtime access and all required tests are not deferrable acceptance items.

## Dependency and worktree strategy

| Workstream | Modules | Depends on |
|---|---|---|
| Contract/model/migration/provider | apps/api/orba, migrations, tests | Frozen schema/source rules |
| Lifecycle/routes/authorization | same apps/api modules/tests | DB contract/provider boundary |
| Reader/editor/transport | apps/web components/lib/app/tests | Frozen API/error/revision contract |
| Verification/docs | scripts, docs, API/web test setup | All actual implementations |

Theoretical lanes are API and web after contract freeze, but shared DTO/transport/recovery decisions couple them. Recommend sequential implementation in this shared checkout; no worktree/agent implementation is authorized by this planning review. Root owns integration. Current review voices write distinct docs only. Backend/core-browser/live suites always serialize on orba_test, regardless of coding lanes. No concurrency claim from multiple agents replaces actual integration evidence.

## Decision audit

| ID | Classification/principle | Auto-decision / rejected alternative |
|---|---|---|
|E-A01|Mechanical P1/P5| Explicit scalar snapshot/short sessions; reject retained identity/connection |
|E-A02|Mechanical P1| Serialize final session/user with logout under fixed locks |
|E-A03|Mechanical P1| Separate request/snapshot hashes and original replay |
|E-A04|Mechanical P1| Stable all-node identities, plan-wide child keys/composite ownership |
|E-A05|Mechanical P1| Durable first deadline, fenced terminal CAS, fresh commit reconciliation |
|E-A06|Mechanical P1| Durable copy keys, exact revision/version, immutable approval |
|E-A07|Mechanical P5| Existing sync DB worker + scoped bounded AsyncOpenAI; no second engine/queue |
|E-A08|Mechanical Explicit/P1| Shared strict test target before any mutation |
|E-Q01|Mechanical P4| Extract existing private authorizer once |
|E-Q02|Mechanical P4| One integrity engine; separate human/provider authority |
|E-Q03|Mechanical P4| One typed transport/error extension preserving old callers |
|E-Q04|Mechanical P5| Small native reader/editor modules; no generic form platform |
|E-T01|Mechanical P1| Assign every new branch/error/user flow; no placeholder tests |
|E-T02|Mechanical P1| Fresh DB assertions and unchanged records after negatives |
|E-T03|Mechanical Explicit| Isolated doubles/authored fixtures distinct from live generation |
|E-T04|Mechanical Explicit| Two actual provider flows + quality rubric, missing config nonzero |
|E-T05|Mechanical P1| Preserve old guarantees/unsafe-target/migration/exit1 experiment |
|E-P01|Mechanical P5| Shared aggregate limits/linear graph validation |
|E-P02|Mechanical P1| Eager/bulk relational access and bounded history |
|E-P03|Mechanical P1| Complete numeric budgets/deadline fences, no hard-real-time claim |
|E-P04|Mechanical P5| Indexed finite sweep/GET backoff; no hidden model checks |

## Implementation tasks

| ID | Component/files | Title / source | Priority | Human / agent-assisted estimate | Verify |
|---|---|---|---|---|---|
|EN-T1| PM service/security/DB | Implement scalar-session release, logout-linearized publication and terminal fences; E-A01/02/05 |P1|1–2d /1–2h| Real authority/lease/rollback races |
|EN-T2| PM schemas/models/migration | Stable all-node identity, same-project constraints, dual input/snapshot hash and durable copy identity; E-A03/04/06 |P1|1–2d /1–2h| Real FK/replay/reorder/copy tests |
|EN-T3| PM provider/router/proxy/client | Enforce scoped SDK and complete phase/body/transport budgets; E-A07/E-P03 |P1|1d /45–90m| Real local timing, API health, live response |
|EN-T4| PM schemas/service/web modules | Share validators/authorizer/error shape and small reader/editor modules; E-Q01..04 |P1|1d /45–90m| Old regressions + schema/API/editor consistency |
|EN-T5| API/browser/live tests | Execute all32 coverage groups/all20 owner guarantees with honest fixtures/live boundaries; E-T01..05 |P1|2–3d /2–4h plus live| Actual counts/exit evidence, no skips |
|EN-T6| Test guard/migrations/verify/docs | Strict test target, populated preservation and Full/Core/expected-failure evidence; E-A08/E-T05 |P1|1d /45–90m| Full verifier + wrong assertion actual exit1 |
|EN-T7| PM DB/index/reader | Bound queries, graph cost, history and expired-run sweep; E-P01/02/04 |P1|0.5–1d /30–60m| Actual max authored document/query/timing checks |

Estimates exclude owner credential provisioning and real provider latency. They are planning ranges, not elapsed evidence. Tasks overlap earlier phase findings intentionally; aggregator exact-match dedupe must not silently merge different obligations. External JSONL and TODO ledger are primary-owned. Independent source voice is complete; final CLI voice/consensus and completion counts follow before the gate.

## Final voice disposition and execution boundary

The actual final CLI review is [STAGE03_ENG_CLI.md](STAGE03_ENG_CLI.md), exited0, with eight ranked concerns. Both independent voices are Codex-family; this is not Claude/cross-model consensus. The later owner continuation authorizes execution of recommended routine defaults; it is not fabricated approval of individual taste votes. The Gemini-specific source amendment is [STAGE03_GEMINI_AMENDMENT.md](STAGE03_GEMINI_AMENDMENT.md). Its source findings are not test evidence.

| ID | Classification | Disposition / current code |
|---|---|---|
|E-CLI01|Mechanical P1|Preserve original blocking confirmation keys/text and recorded disposition; server-owned context inheritance |
|E-CLI02|Mechanical P1|ASGI/proxy streamed body deadlines/byte caps, capped provider envelope, bounded generation-only timeouts |
|E-CLI03|Mechanical P1|Fresh clock_timestamp after locks, original-session fence again after graph flush |
|E-CLI04|Mechanical P1|Reservation/running commits must be acknowledged before dispatch; unknown is reconciled, never taken over |
|E-CLI05|Mechanical P1|Context snapshots retain transitive origin and human dispositions; approval does not manufacture facts |
|E-CLI06|Mechanical P1|Copies share workspace/version locking and durable identity; exact source revision/hash stored |
|E-CLI07|Mechanical P1|Transport auth epoch and caller abort signals prevent obsolete completion side effects |
|E-CLI08|Mechanical P1|Actual migration parent0febbe526f54; canonical hash version persisted; populated upgrade probe |

These eight rows resolve planning decisions, not execution outcomes. Current implementation/test evidence and any unverified stress/live cases are recorded in `../VERIFICATION.md`. No mechanical decision is presented as a new user taste choice. No Stage04 work is authorized. The 32 aggregated review source tasks overlap; their original checkboxes are not an independent implementation/verification ledger.
