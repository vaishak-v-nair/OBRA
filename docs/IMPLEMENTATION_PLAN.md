# ORBA Stage 01 implementation plan

Review date: 2026-10-18. Scope authority: the user's Stage 01 specification and explicit instruction to start implementing. This document plans behavior; it is not evidence that behavior exists or passes. Sequential review order: CEO, Design, DX, Engineering. Base branch fallback: main. Repository inspection at review intake found only `.git`; there is no existing application, dependency manifest, migration, test suite, AGENTS.md, design document, or reusable project code.

## Review execution and degradation

The applicable autoplan phase sections and four review skills were read from `C:/Users/vaish/.agents/skills`. Shared preambles, prerequisite offers and duplicate outside-voice sections are excluded by autoplan's skip list. This is one delegated Codex review voice, not a cross-model consensus. The requested Claude voice is unavailable in the exposed agent tools; no Claude review is claimed. The gstack startup helper was reported absent by the primary agent. Its private session/config, review-log, telemetry, designer binary and jq aggregation pipeline are not claimed executed. Review requirements remain documented here; missing machinery does not block the explicitly authorized implementation. No public deployment, destructive operation, or Stage 02 work is authorized.

## CEO review: premise challenge and scope

### Premises, alternatives, and existing leverage

1. A persisted project is the correct first vertical slice. It exercises navigation, forms, API boundaries, migrations, real PostgreSQL and browser reload durability without pretending an AI system exists. The risk is a workspace that visually implies agents are already operating; explicit future-stage labels mitigate this.
2. Local single-user operation is a deliberate boundary. It permits a small trustworthy foundation but provides no identity or tenant boundary. Bind development services to loopback and describe this plainly rather than adding fake accounts.
3. A split Next.js/FastAPI stack adds setup cost compared with one runtime. The user explicitly chose this stack; retaining it tests the intended integration now. No justified compatibility evidence currently supports changing it.
4. Stable dependencies must be verified from official registries/documentation during implementation. A version recalled by a reviewer is not confirmed current. Commit pnpm and uv lockfiles and record actual resolved versions.
5. Docker availability is an environmental prerequisite for the requested local PostgreSQL flow. Probe the daemon, not merely the executable. If unavailable, preserve the actual error and label database-dependent verification blocked until a real PostgreSQL service is available.

| Subproblem | Existing code | Reuse decision |
|---|---|---|
| Routing and layouts | None | Next.js App Router built-ins |
| Validation and OpenAPI | None | FastAPI and Pydantic v2 |
| Persistence and migration | None | SQLAlchemy 2 and Alembic |
| Accessible UI primitives | None | shadcn/ui where useful; native form controls |
| Theme and responsive layout | None | CSS semantic tokens and media queries |
| Browser verification | None | Real Playwright browser against real services |

```text
CURRENT                 THIS STAGE                       12-MONTH IDEAL
empty repository  -->   local durable project workspace --> unified human/AI delivery
                        creation -> detail -> reload       secure agents, evidence,
                        truthfully absent AI features      collaboration and sandboxes
```

Dream-state delta: this stage establishes trustworthy identity for projects and reliable UI/API/database seams. It does not establish users, tenancy, agents, tasks, provider calls, repository access, execution or evidence generation.

| Approach | Completeness | Effort (human / agent estimate) | Pros | Cons / risk |
|---|---:|---|---|---|
| Requested split app + PostgreSQL | 10/10 | 3–5 days / one sustained session, environment dependent | Exercises final seams; matches specification | Three services and migration setup |
| SQLite or browser storage | 4/10 | 1 day / hours | Faster local start | Violates source of truth and DB test requirements; rejected |
| Build later-stage agent platform now | 2/10 for this stage | weeks / unbounded | Broad apparent feature coverage | Unverifiable external services and scope drift; rejected |

Mode: SELECTIVE EXPANSION within Stage 01. Accepted refinements are bounded errors, explicit timeouts, isolated test DB guards, stable list ordering, accessible states and double-submit protection. No future-stage expansion is accepted. Hour 1 must establish tooling and PostgreSQL feasibility; hours 2–3 establish migrated APIs; hours 3–5 complete the actual UI journey; hour 6+ is reserved for startup, tests, fixes and evidence. These are planning estimates, not measured delivery times.

### 1. Architecture

The primary seam is browser to Next.js to FastAPI to PostgreSQL. Keep a small API client and one session dependency rather than a generic service framework. PostgreSQL and the API are single points of failure; the UI must preserve input and show a truthful recoverable error.

```text
Browser -> Next.js App Router -> API HTTP client -> FastAPI routes
                                                 | validation
                                                 v
                                             SQLAlchemy sessions -> PostgreSQL
                                                 ^                    ^
                                                 |                Alembic upgrade
                                             Pytest               isolated test DB
Playwright -> real browser -> real web -> real API -------------------+
```

Nil project body -> 422; empty/whitespace values -> 422; valid body -> transaction commit -> 201 and detail navigation; DB failure -> rollback, structured 503, preserved form. Listing empty DB -> 200 empty collection -> useful empty state. Missing detail -> 404 with recovery navigation. Project lifecycle is `absent -> created`; no endpoint changes status in this stage. Invalid transitions are prevented by the absence of mutation routes and a server-owned status default.

### 2. Error and rescue registry

| Codepath | Failure / exception | Rescue | User sees / action |
|---|---|---|---|
| Request validation | RequestValidationError | Structured 422 field details | Correct the named field; no insert |
| UUID path validation | RequestValidationError | Structured 422 | Invalid project identifier |
| Project lookup | No matching row | Structured 404 | Project not found; return to Projects |
| DB connection/query | SQLAlchemy OperationalError / timeout | Roll back session; log safe context; 503 | Database unavailable; retry after service recovery |
| Unexpected server defect | Unhandled defect | Server logs traceback; sanitized 500 boundary | Request failed; no database/secret details |
| Browser fetch | Network error / abort / non-2xx | Typed error display; retain draft | API unavailable or validation explanation |
| Commit succeeded, response lost | Network ambiguity | Never automatic POST retry | Creation uncertain; check Projects before retry |
| Readiness | Unreachable DB or missing migration | Real probe; 503 | Not ready; operator checks DB and migrations |

### 3. Security and threats

Every endpoint is callable by anyone who can reach the local API; this is documented rather than described as authenticated. SQLAlchemy bound parameters prevent interpolated SQL; React text rendering prevents descriptions becoming executable HTML. Do not log descriptions or credentials. Oversized input is rejected by Pydantic constraints, secrets live in ignored environment files, CORS is restricted to configured local web origins, and no upload/repository URL is consumed in Stage 01. Internet exposure has high impact and is excluded; untrusted input remains relevant even locally.

### 4. Data and interaction edge cases

```text
form -> trim/validate -> POST -> Pydantic -> INSERT/COMMIT -> response -> navigate
  |          |           |         |             |             |
empty     max length   network    422          DB failure     lost response
inline    inline       preserve   no row       rollback/503   no auto retry
```

Disable submission while pending and use a submission guard to suppress same-form rapid clicks. Preserve textarea content on failures; allow explicit retry. New tabs can intentionally create identical descriptions; do not impose a fabricated uniqueness rule. Sort project lists deterministically by creation timestamp and UUID, and avoid static arrays or client caches that hide reload failures.

### 5. Code quality

There is no prior code to compare or duplicate. Use explicit modules for configuration, database, model/schema, routes and error handling; avoid speculative repositories, dependency containers and event systems. Share one ProjectForm and one API/error client across Chat and Projects so validation and failure UX cannot drift.

### 6. Tests

All persistence tests use real PostgreSQL, with migration-run setup and a dedicated test database. The hostile test submits whitespace, missing fields and over-limit values and checks the row count stays unchanged. The shipping-confidence test creates through the browser, reloads the detail page, and finds the same UUID in Projects; the chaos test points a real app at an unavailable database and requires readiness 503 while liveness remains 200. Full branch mapping is in TEST_PLAN.md; no mock AI, SQLite replacement or dummy PASS driver is permitted.

### 7. Performance

The initial list query is the first growth risk because descriptions can be large. Bound input and consider a bounded paginated list only if the implementation supplies truthful UI controls; never silently truncate records. Add deterministic indexed ordering if the chosen API paginates. No cache is justified for a local single-user project list, no background jobs exist, and no N+1 relationship traversal exists. Measure service startup and request behavior before claiming latency targets.

### 8. Observability

Liveness means the process can serve requests; readiness means a real DB query and expected schema are available. Preserve real command logs and test outputs in verification records. HTTP access logs and named server exception logs are enough for this local stage; hosted metrics, alerts, trace collectors and administrative dashboards add unrelated infrastructure and are deferred.

### 9. Rollout and rollback

Start PostgreSQL, wait for its real health check, apply Alembic, then start API and web. Test readiness and project creation after startup. There is no public rollout. A migration downgrade dropping projects destroys data and must never be run on a valued database without explicit approval; prefer a database backup and forward repair. Test database resets require a strict test-name guard and must not touch the development volume.

### 10. Trajectory

UUIDs, timestamps, strict schemas and versioned HTTP endpoints provide a useful future seam without pre-creating agent tables. Authentication and tenant ownership must be designed before exposure or multiplayer use. Application source choices are reversible (4/5), while persisted schema changes require care (3/5); keeping migration history and clear docs reduces concentrated knowledge. Stage 02 remains planned only.

### 11. Product design

Chat's heading, supporting sentence and single creation form establish the first action. Navigation remains consistent on every route. Empty, pending, failed, not-found and future-stage states must be specified, not filled by imagined output. The dedicated design review below resolves mobile layout, themes and keyboard behavior before engineering review.

### CEO completion

| Item | Result |
|---|---|
| Scope | Stage 01 retained; 0 user challenges |
| Premises | 5 named premises assessed |
| Accepted refinements | Errors, isolation, states, deterministic reads, submit guard |
| Critical implementation gates | DB availability, migrations, real browser persistence |
| Outside voices | Delegated Codex review only; no dual-model consensus |
| Plan status | Ready to implement; no execution success claimed |

Phase 1 complete: no scope reversal recommended. Missing independent CLI/Claude voices are N/A, not confirmed. Passing the retained scope to Design.

## Design review

Initial specification completeness: 7/10. No DESIGN.md or components existed at intake; the user's supplied palettes are the design authority. Classifier: app workspace UI, not marketing. Planned scores below assess specification completeness after decisions, not tested visual quality.

### 1. Information architecture: 9/10

The first three priorities are the build prompt, create action, and persistent project navigation. Desktop has a restrained sidebar and one primary content column; detail views use readable sections rather than a mosaic of empty cards. Chat submission creates a project and navigates, with no conversational assistant bubble.

```text
App shell
  Sidebar: ORBA / Chat / Projects / Skills / Contribute / Workspaces / Activity / Settings
  Main
    Chat: heading -> supporting sentence -> description form -> Create project
    Projects: title + New project -> real list / empty state
    Detail: project title/status -> original description -> future-stage reservation
  Theme control: persistent accessible light/dark action
```

### 2. Interaction states: 9/10

| Feature | Loading | Empty | Error | Success | Partial |
|---|---|---|---|---|---|
| Create | Button says Creating; fields retain values | Visible labels and invitation | Inline field error or API alert | Navigate to real UUID | Lost response warns; inspect Projects |
| Projects | Readable loading text | No projects yet + create action | Error and Retry | Rows from API | No fabricated cached results |
| Detail | Loading text | Missing identifier routes to not-found | Not found or service error with return link | Title, original text, times, real status | Future work clearly absent |
| Later sections | Immediate page | Coming in a later stage | No service request | Honest scope message | No fake connection badge |

### 3. Journey and emotional arc: 9/10

| Step | User action | Expected feeling | Design support |
|---|---|---|---|
| 1 | Opens Chat | Oriented in 5 seconds | Exact heading and one action |
| 2 | Describes project | Focused | Multiline label and roomy input |
| 3 | Submits | Confident something real happens | Pending button, no fake agent progress |
| 4 | Opens detail | Trust | Original words, real status/timestamp |
| 5 | Reloads / opens Projects | Durable ownership | Same persisted project |
| 6 | Opens Skills | Clear expectations | Explicit later-stage explanation |

Five-minute utility comes from returning to a persisted project. Long-term trust comes from never presenting anticipated agent output as observed work. Errors must allow recovery without retyping.

### 4. Intentionality / slop risk: 9/10

The composition uses a calm prompt workspace, structured project rows and restrained section dividers. Avoid decorative gradients, metric widgets, agent avatars, colored icon circles and fake activity timelines. Attachment and GitHub entry points remain visible but explain their later-stage availability; they cannot accept files or imply repository connectivity. Use one locally available deliberate font choice without making startup depend on a remote font download.

### 5. Design system: 9/10

Define semantic background, surface, elevated, text, muted, accent, border, focus and destructive tokens. The exact supplied light/dark palettes map to these names; choose readable foreground tokens for accent buttons rather than assuming white on mint passes. Keep radii restrained and spacing consistent, with visible form labels and text hierarchy. Use shadcn/ui primitives for actual interaction needs instead of adding a dependency solely as a logo requirement.

### 6. Responsive and accessibility: 9/10

Desktop >=1024px retains a sidebar; tablet and mobile use a labeled navigation toggle and accessible sheet or wrapping compact navigation. At 375px the creation form and project text must fit without horizontal scrolling; long titles wrap. Support skip-to-content, semantic landmarks, active link indication, focus rings, keyboard activation, 44px touch targets, screen-reader error announcements and reduced motion. Verify both themes with a real viewport, including readable body contrast and a usable theme button; persist preference without hydration errors or a misleading theme icon.

### 7. Unresolved decisions: 9/10

Use created as the server-owned initial status, derive Chat project title deterministically from the description or offer an explicit title on the shared form, and display the original description unchanged except surrounding whitespace normalization. The root implementer should keep title generation documented and test its bounds. No aesthetic choice requires a scope challenge; all are reversible within the specified palettes. Mockups are not generated because the gstack designer workflow was unavailable; actual browser validation is still required.

### Design litmus scorecard and completion

| Litmus | Planned result | Other model | Consensus |
|---|---|---|---|
| Brand obvious | ORBA in navigation | Unavailable | N/A |
| One anchor | Project creation input | Unavailable | N/A |
| Scannable | Clear page heading and actions | Unavailable | N/A |
| One job per section | Creation, list, overview | Unavailable | N/A |
| Necessary cards only | Rows and sections preferred | Unavailable | N/A |
| Purposeful motion | Only pending/focus/transition affordances | Unavailable | N/A |
| Premium without shadows | Tokens, spacing, typography | Unavailable | N/A |

All seven dimensions assessed; 0 confirmed dual-model judgments, 0 unresolved product changes. Phase 2 complete; state and responsive specifications now feed DX.

## Developer experience review

Product type: local developer workspace with REST API and contributor monorepo. Persona: a developer comfortable with git and terminals, installing Node/pnpm, Python/uv and Docker on Windows or another supported host. Mode: DX POLISH. Initial documentation completeness is 3/10 because no README or scripts existed at intake. Time to hello world is unmeasured; target under five minutes after prerequisites and initial dependency downloads, with cold install time reported separately.

First-person empathy: I want one documented route from checkout to a project that survives reload. If Docker is down I need the actual failing command and remedy before I spend time on the web UI. I should not wonder whether a green card means a mocked service, or whether running tests will erase my projects. The moment of value is seeing my exact description survive a browser reload, not seeing an agent animation.

### Developer journey map

| Stage | Action | Friction / resolution |
|---|---|---|
| Discover | Read README | Say local single-user and Stage 01 up front |
| Evaluate | Inspect architecture and scope | Separate working, planned, blocked and verified |
| Prerequisites | Check runtimes / Docker | Versions and daemon probe, no hidden service |
| Install | pnpm install; uv sync | Committed lockfiles, frozen reproduction |
| Configure | Copy env examples | Loopback defaults, no real secrets committed |
| Database | Compose up then Alembic | Readiness, port collisions, named test DB |
| First success | Start API/web, create project | Exact ports and URL, real saved UUID |
| Debug | Trigger 422 / DB outage | Structured problem, cause, fix and docs |
| Return / maintain | Run tests / upgrade | Isolated DB guards, migration and lockfile steps |

### Eight passes

1. **Getting started, planned 9/10.** The README needs copy-paste-complete commands in working-directory order. Distinguish prerequisite installation from warm startup. Record actual startup timing only if measured; no benchmark claim is justified yet.
2. **API ergonomics, 9/10.** Keep `/api/v1/projects` and UUID resource URLs consistent, return 201 on insert and 404 on missing row, and document schema in FastAPI's OpenAPI. Reject invalid bodies consistently rather than silently coercing arbitrary types. Health endpoints remain outside the resource prefix for operational clarity.
3. **Errors and debugging, 9/10.** Surface stable error code/message/details while keeping SQL and secrets server-side. Distinguish an unavailable API, unavailable DB, bad input and missing project. Give configuration and migration remedies in README; preserve actual command stderr in verification notes.
4. **Documentation, 9/10.** README starts with run/test instructions and links architecture, roadmap, verification and AGENTS.md. Examples include environment variables, ports and the required current directory. Avoid a second contradictory startup workflow.
5. **Migration and upgrade, 8/10.** Use explicit Alembic revision history and locked dependencies. Document that downgrade can destroy project data; it is not a routine repair command. Future migrations require review against persisted projects and an update to evidence.
6. **Environment and tooling, 9/10.** pnpm/uv scripts should expose typecheck, lint, build, backend tests and E2E. Test database creation and web/API startup must be reproducible and fail clearly. Do not require Bash-only commands on the user's Windows host when a native command exists.
7. **Community and ecosystem, 7/10.** No public distribution or community is promised in Stage 01. AGENTS.md and contributor docs preserve verification rules and help a future contributor operate the local application. Public package publishing, hosted onboarding and support channels are deferred explicitly.
8. **Measurement and feedback, 9/10.** Preserve command exit status, test counts and real-service scope in VERIFICATION.md. Track defects found and fixes without claiming a skipped test passed. No telemetry collector or feedback backend is required for this local stage.

Reference benchmark: a local full-stack quickstart should reach a visible durable record in a few explicit commands after tools are installed. Competitor timings were not measured, so no quantitative comparison is claimed. First-time confusion risks are root folder OBRA versus product ORBA spelling, test-versus-development DB selection, and which terminal owns which service; resolve these in docs.

### DX implementation checklist

- [ ] Document prerequisites, real daemon check, configuration and ports.
- [ ] Provide locked installation and migration commands.
- [ ] Provide separate backend and E2E test database settings and guards.
- [ ] Provide actionable structured error examples.
- [ ] Document exact lint/typecheck/build/Pytest/Playwright commands.
- [ ] Record measured results, blockers and no-auth limitation.

DX consensus dimensions (getting started, naming, errors, docs, safe upgrades, environment): this voice assessed all six; missing CLI/Claude voice means N/A for every consensus cell, 0/6 confirmed. Overall planned specification average 8.6/10, implementation unmeasured. Phase 2.5 complete; passing amended setup and isolation requirements to Engineering last.

## Engineering review

### Scope challenge and architecture

Intake inspection found no application source to reuse or line-level bugs to quote. More than eight files are necessarily involved in the mandated two-app monorepo; autoplan's no-scope-reduction override retains the complete required slice. Use framework-native routing, schema validation, migrations and sessions [Layer 1]; do not create a custom ORM, job runner, authentication layer or capability registry. No code defect is asserted before code exists.

Use synchronous SQLAlchemy sessions in FastAPI synchronous handlers unless implementation evidence supports async; this avoids blocking the event loop with synchronous database work. Construct configuration and engine in an app factory or equivalent injectable boundary so readiness can be tested against a genuinely unreachable URL. Bound connection/probe timeouts so an outage test finishes reliably. Application migrations remain explicit startup operations, never model `create_all` calls.

Architecture graph and error flow above remain authoritative after the design/DX amendments. FastAPI schema and frontend Project types are a small explicit contract; do not add a generated shared-package pipeline yet. Restrict web/API origin configuration to the actual chosen dev ports and check same-origin/proxy behavior in the browser.

### Code quality

Proposed responsibility boundaries are `config`, `database`, `models`, `schemas`, `routes`, and `errors` in the API; layout/navigation, API client, shared project form and page views in web. There are no actual functions or diagrams to audit for regressions at intake. Re-review real implementation before claiming quality checks complete. Avoid broad exception swallowing, module-import database connectivity and duplicate create forms; each obscures a failure this stage exists to reveal.

### Test review and execution graph

```text
SCHEMA -> valid / missing / whitespace / wrong type / over-limit -> Pytest validation
POST   -> validate -> insert -> commit -> return UUID ------------> PostgreSQL integration
                    -> DB unavailable -> rollback/503 ----------> real unreachable URL
LIST   -> empty / saved records / stable order ------------------> PostgreSQL integration
GET    -> existing / absent / malformed UUID --------------------> PostgreSQL integration
LIVE   -> process responds even without DB ----------------------> real app HTTP test
READY  -> query + expected schema / DB unavailable ---------------> real DB + outage test
FORM   -> create / pending duplicate click / server error -------> browser real services
DETAIL -> UUID route / reload / missing record ------------------> browser + API
NAV    -> Projects includes UUID / empty / later-stage ----------> browser
THEME  -> light/dark / persistence / mobile focus ----------------> browser
```

At planning time tests existing: zero. Every arrow is a planned test gap, not passed coverage. TEST_PLAN.md provides concrete assertions. No LLM prompt, external provider or agent code exists, so model evals would be unrelated; Pytest and Playwright are the relevant suites. Backend integration tests should directly query committed rows with a fresh session rather than only inspect HTTP responses, and invalid-body tests must compare counts before/after.

The browser test must use isolated DB-backed running services, create a unique meaningful description, assert the real UUID detail route, reload, then navigate and locate that same record. Browser route interception must not replace API/database responses for that mandatory flow. Unit mocks, if added for isolated helpers, must be identified and cannot replace persistence/readiness evidence.

### Performance and resilience

No current query source exists to measure. The proposed project list is one query and detail is a primary-key lookup, so no relationship N+1 is designed. Set bounded description/title sizes and pool connection timeout; do not invent p99 results. With no agent stream, task runner or model calls, caching and queues add accidental complexity. Reassess pagination against actual response shape, and document any bounded list limit truthfully.

### Failure modes and critical gaps

| Failure | Detection | Handling | Critical gate |
|---|---|---|---|
| Docker daemon unavailable | Actual docker compose failure | Preserve stderr, mark DB verification BLOCKED | Yes until real DB available |
| Wrong / unmigrated DB | Readiness and Alembic/current schema checks | 503 and migration instructions | Yes |
| Test targets dev DB | Explicit test DB name/config guard | Abort before destructive cleanup | Yes |
| Invalid request creates row | Count comparison | Reject 422 without commit | Yes |
| UI claims save before commit | Reload and fresh DB lookup | Navigate only after success | Yes |
| DB down but readiness green | Real unavailable-port test | Ready 503, live 200 | Yes |
| Browser API cannot connect | Real UI E2E | Actionable API error; fix origin/proxy | Yes |
| Fake future-stage success | UI/route inspection | Honest later-stage screen | Yes |
| Theme hydration mismatch | Browser console and reload | Stable initialization / hydration handling | Yes if present |
| Duplicate POST after lost response | UX review | No automatic mutation retries | Document ambiguity |

### Implementation tasks (aggregated)

- [ ] T1 P1: probe tooling and Docker; preserve inventory/errors (human ~1h / agent ~10m).
- [ ] T2 P1: scaffold config, sessions, Project model and Alembic migration (human ~4h / agent ~30m).
- [ ] T3 P1: implement five endpoints, strict schemas and structured errors (human ~4h / agent ~30m).
- [ ] T4 P1: shell, shared creation form, real projects list/detail and later-stage routes (human ~1d / agent ~1h).
- [ ] T5 P1: tokens, themes, responsive navigation and accessible error/loading states (human ~4h / agent ~30m).
- [ ] T6 P1: real PostgreSQL tests, isolated E2E flow and genuine outage/validation negative tests (human ~1d / agent ~1h).
- [ ] T7 P1: start real services, run lint/typecheck/build/tests, fix defects and preserve actual logs (effort depends on environment).
- [ ] T8 P1: document reproducible commands, limitations and requirement matrix with exact verdict (human ~2h / agent ~20m).

Tasks are a build plan, not completion marks. No JSONL aggregation is claimed because no healthy gstack helper session or commit window existed at intake. Work lanes: API, web, and planning may be independent after agreeing contract; final migration/service/E2E verification is sequential against the integrated application.

### Engineering completion summary

| Measure | Result |
|---|---|
| Architecture | Small explicit two-app slice; no speculative services |
| Test review | Full planned branch/flow map; all execution initially NOT RUN |
| Performance | Bounded inputs/timeouts required; no fabricated measurements |
| Security | Local single-user only; no tenant/auth claims |
| Failure modes | 9 critical implementation gates plus response ambiguity |
| Outside voice | One delegated Codex voice; 0 dual-model confirmations |
| Completeness | All mandatory Stage 01 requirements retained |
| Review verdict | Ready for authorized implementation; verification still required |

Phase 3 complete. Cross-phase themes are truthful state, explicit environment errors, test database isolation, and durable save/reload evidence. No user challenge changes the requested scope. Implementation was explicitly authorized by the user; no redundant approval is requested.

## NOT in scope

Authentication, tenancy, human multiplayer, LangGraph, Redis, agents, provider APIs, GitHub credentials/repository analysis, Skills installation, uploads, sandboxes, visual canvas, evidence generation, public deployment and artifact publishing are later-stage work. No stubs should suggest these run today. Hosted observability and community channels are unnecessary for the local foundation. No production-readiness claim is permitted merely because local checks pass.

## Decision audit trail

| # | Phase | Decision | Classification | Principle | Rationale / rejected |
|---|---|---|---|---|---|
| 1 | CEO | Retain exact Stage 01 slice | Mechanical | Completeness | No future expansion; reject fake breadth |
| 2 | CEO | Retain requested split stack | Mechanical | Explicit | No demonstrated compatibility blocker |
| 3 | CEO | Real PostgreSQL all persistence tests | Mechanical | Completeness | Reject SQLite substitution |
| 4 | CEO | No automatic POST retries | Mechanical | Explicit | Commit/response ambiguity can duplicate projects |
| 5 | Design | Shared ProjectForm | Mechanical | DRY | Keep Chat and Projects behavior consistent |
| 6 | Design | Semantic tokens / restrained workspace | Mechanical | Explicit | Supplied palettes remain authority |
| 7 | Design | Honest disabled future entry points | Mechanical | Completeness | No fake uploads or GitHub connectivity |
| 8 | Design | Responsive nav and visible labels | Mechanical | Completeness | Mobile and keyboard routes stay usable |
| 9 | DX | DB name safety guard | Mechanical | Completeness | Test cleanup must not erase dev data |
| 10 | DX | Warm-start timing is target only | Mechanical | Explicit | No measured TTHW yet |
| 11 | Eng | App config boundary for real outage test | Mechanical | Explicit | Avoid readiness mocks |
| 12 | Eng | No extra service/repository abstractions | Mechanical | Pragmatic | Framework-native behavior suffices |
| 13 | Eng | Report missing review machinery | Mechanical | Explicit | Missing voices never count as consensus |
| 14 | Eng | Continue authorized implementation | Mechanical | Bias toward action | User explicitly said start implementing now |

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|---|---|---|---:|---|---|
| CEO | autoplan | Scope and premises | 1 | Plan reviewed | Five premises; retain Stage 01 |
| Design | autoplan | UI states and hierarchy | 1 | Plan reviewed | Seven dimensions; runtime unverified |
| DX | autoplan | Contributor journey | 1 | Plan reviewed | Eight dimensions; timing unmeasured |
| Engineering | autoplan | Architecture and tests | 1 | Plan reviewed | Real DB isolation and outage tests required |
| Dual-model voices | autoplan | Independent consensus | 0 | Unavailable | One delegated Codex reviewer only |
| Helper review logs | autoplan | Readiness dashboard | 0 | Unavailable | No healthy helper session; no log execution claimed |

VERDICT: Plan reviewed with tooling concerns; implementation authorized; Stage 01 verification NOT RUN at plan creation. No executed feature or passing test is claimed by this report.

NO UNRESOLVED DECISIONS

