# Stage04 developer experience review

2026-10-21; DX POLISH. Product: local developer workspace + authenticated API/CLI.
Persona: a maintainer continuing the existing Stage03 checkout with Docker/Node/uv
installed, expecting a safe additive upgrade, trustworthy errors and a reproducible
planning workflow. Secondary persona: a contributor verifying it without a model key.
This review changes the plan, not the runtime; scores below measure plan specificity.

## Developer perspective

I open README and see the verified Stage03 report, then prerequisites and the frozen
pnpm/uv installation commands. I already have a working checkout, so I need to know
which migration and environment values Stage04 adds. I do not want another app, a new
authentication system, or a test that suddenly spends money. The existing safe command
is scripts/verify.ps1, and I expect it to keep checking my old password/workspace/project
flows. If Docker is stopped, I need the actual service error and a clear startup action,
not a claim that PostgreSQL is broken. After migrating and starting the two services,
I should find Architecture on my existing project. An empty view should explain that
I need an approved Product Plan or explicit Architect configuration. It must not create
an example technical plan and imply Gemini generated it. When I do configure a model,
I want one deliberate action and a durable request reference if the network drops.
On a graph error, I need the task and prerequisite names, the saved revision, and a way
to correct the local draft. When I read the final verification report, I want source-
bound test counts and a clear distinction between controlled application checks and
the still-unauthorized live Architect call. The first meaningful result is a real
saved planning artifact I can audit, not a spinner, a mock agent or a passing stub.

This is a grounded roleplay, not a measured user-study transcript. Current README
headings/commands, the observed Docker pipe failure and existing PM recovery code
provide its evidence. No user onboarding duration is invented.

## Reference workflows and time target

| Reference | Observed documented approach | Measured onboarding time here |
|---|---|---|
| [FastAPI First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) | Small runnable API and discoverable interactive documentation | Not measured |
| [LangGraph Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) | Explicit model credential and progressive graph/function example | Not measured; no framework adopted |
| [Google agents CLI tutorial](https://google.github.io/agents-cli/guide/hands-on-tutorial/) | Explicit prerequisites and sequential create/install/playground steps | Not measured; no CLI/framework installed |
| ORBA Stage03 continuation | Existing frozen installs, additive Alembic, API/web startup and same project | Stage04 onboarding not yet timed |

These primary documents inform discoverability, not unsupported competitor speed or
adoption claims. Target: reach the existing authenticated project and honest Architect
setup/source state within5minutes with dependencies/services ready. Cold installation,
model credential acquisition and full verification are separate unmeasured durations.
The actual baseline Gate A took11m23s; it is not a time-to-first-use benchmark.

## Journey map and confusion fixes

| Stage | Developer does | Existing evidence/friction | Plan action |
|---|---|---|---|
| Discover | Read README stage status | Old text says Stage04 unauthorized | Update current status; retain historical reports |
| Evaluate | Inspect architecture and A/B/C evidence | A valid PM B does not prove Architect | Separate stage/agent/profile receipts |
| Install | Use locked pnpm/uv dependencies | Docker may be stopped; no new graph package needed | Preserve locks; real Docker health/startup error |
| First use | Start API/web and open existing project | Missing source/model must be meaningful | Actionable non-paid empty/setup states |
| Integrate | Generate from exact approved PRD | PM-only proxy/body policy would break new path | Extend bounded planning route policy |
| Debug | Read error and exact run | Unknown commit differs from failed provider | Structured categories, field keys, GET recovery |
| Upgrade | Apply additive migration | Metadata registration/fixture truncation must include new tables | Migration preservation/drift tests |
| Extend | Inspect graph/coverage API | Linked coverage is not semantic or execution proof | Versioned typed contracts and edge convention |
| Migrate/operate | Reproduce receipts and plan history | Local source/profile binding; no portable attestation | Exact commands, limitations and independent SQL inspector |

Illustrative confusion sequence: T+0 README still names only PM configuration; fix by
linking the Architect quick start. T+0:30 a stopped Docker daemon emits its real pipe
error; document/check service readiness. T+1:00 an empty Architecture view must distinguish
no approved source from unavailable API. T+2:00 a valid long generation must not inherit
the generic15s proxy deadline. These timestamps describe a roleplay, not executed timing.
The selected delivery vehicle is the existing UI plus copy-paste offline/verification
commands; a hosted playground/video/new framework is outside the owner's stage.

## 1. Getting started (7 -> 8)

Document the incremental path first: locked dependencies, additive migration, API/web
startup, existing project, current approved PRD, explicit Architect model selection.
The deterministic suite requires no model key; opening a setup state makes no model
call. Do not advertise an unbounded cold setup or guarantee model availability.

Architect settings use `ORBA_ARCHITECT_API_KEY`, `ORBA_ARCHITECT_MODEL`,
`ORBA_ARCHITECT_THINKING_LEVEL`, `ORBA_ARCHITECT_TIMEOUT_SECONDS`,
`ORBA_ARCHITECT_MAX_OUTPUT_TOKENS` and `ORBA_ARCHITECT_MAX_INPUT_BYTES`.
The optional nonempty Architect key overrides the existing resolved PM/Gemini key;
empty/absent override reuses that key. The model never falls back implicitly to PM.
Templates explain precedence and keep real keys blank. No existing dotenv is edited.

## 2. API/CLI ergonomics (7 -> 9)

Use project-scoped architect-runs and architectures routes, exact revision PUT, explicit
approve and a free human draft-copy route. Graph/tasks/coverage are bounded read views
of the same saved artifact. Return source identity, version/revision, proposal state,
run references and actual metadata; forbid client actor/workspace/model authority.

Offline `python -m scripts.check_architect_config` and its help run before Settings
validation can expose supplied values; document configured0/missing1/invalid2. Only an
explicit --check-model may perform one read-only official metadata GET. No readiness
command dispatches generation, counts tokens, retries or changes a model. A separate
verify-architect-live.ps1 requires explicit opt-in; verify.ps1 remains unpaid Gate A.

## 3. Error and recovery quality (7 -> 9)

| Path | Avoid | Required safe outcome |
|---|---|---|
| Source not approved | Generic500 or silently using a draft |409; approve/select the current saved PRD before generation |
| Cyclic dependency | Rendered graph falsely called valid |422 with directed task path/field links; saved graph unchanged |
| Provider503/504 | Fake PRD, retry/fallback or generic save error | Failed run with actual safe upstream status; no architecture; explicit GET/Retry |
| Unknown dispatch/commit | Treating network loss as a known failure | Keep UUID; GET exact own result; never automatically POST again |
| Stale edit/source | Last response silently wins |409 with comparison/source review; local input preserved |

The existing Next proxy and frontend request helper recognize only PM paths. Extend
their explicit planning-path policy and the streamed-body middleware to Architect
routes before integration. Preserve ordinary route deadlines; do not lengthen every
POST. Use the same existing generation envelope (provider budget+5s transport/+10s
outer; proxy290s; client330s) with explicit Architect bounds and no retries. Errors
link to actual Architect setup documentation rather than the PM-only anchor.

## 4. Documentation and learning (7 -> 9)

README links directly to Architect setup/use, architecture, DAG convention, API examples,
test evidence and limits. Include the real Origin/CSRF/session flow, source IDs, expected
revision and an explicit usage-triggering action; no example bypass identity is added.
Distinguish generated proposal, human-authored source fixture, human draft copy and
executed verification in every relevant example.

The application setup state links to concise configuration guidance, while deeper
reference covers source binding, inherited uncertainty, FK constraints and optimistic
revision semantics. Safe errors retain field/task keys without provider bodies or
secret-bearing values. Search/find is native repository/README structure, not a new
hosted docs/search service.

## 5. Upgrade and migration (8 -> 9)

Register Architect models in Alembic and use one additive forward chain. Verify that
existing project IDs/fields, users/hashes, sessions, workspace isolation and approved
PRD rows/children/source hashes survive. New readiness checks must reject an unmigrated
Architect schema; test reset remains strictly guarded orba_test and never development.

No current API route contract is removed. Shared admission now counts both planning
run tables using the existing PM-named limit environment variables, documented as
combined controls. Keep PM command/receipt history valid as historical evidence while
new Stage04 gates use their own agent/source/profile discriminator.

## 6. Environment and contributor tooling (8 -> 9)

Gate A must blank every runtime key alias and both model selections before any child
loads dotenv. Test factories override only their named provider dependency and refuse
development DSNs. No production fake-provider flag, browser credential authority or
uncontrolled external call is added. Run backend/browser phases sequentially against
the existing guarded database, ports and owned-process cleanup contract.

No new npm graph library is required; use native SVG/list controls and strict TypeScript.
New Python logic uses existing dependencies and lockfiles. Stage04 source fingerprint
includes relevant code/config/tests/prompt; immutable reports record actual native exits,
not just a wrapper's success. A failed required deterministic child fails A.

## 7. Ecosystem and costs (6 -> 7)

This is a local authorized workspace, not a public hosted platform with a community,
license promise, support SLA or free paid-model quota. Existing later-stage GitHub/
Model Hub/Skills backlog remains deferred; no external messages or publication is
needed. Runnable real-service examples and explicit test-double labels are the useful
contributor surface in this stage.

Keep request byte/output/time/admission bounds and actual provider usage metadata.
Do not invent dollar costs or unlimited credentials. The recommended future3.6/minimal
profile is based on the recorded Stage03 pass, not a fresh accessibility/performance
claim or guarantee. Fresh owner authorization remains mandatory for Architect generation.

## 8. Measurement and feedback (7 -> 8)

Record actual command durations, failed attempts/fixes, test identities/counts, source/
profile fingerprints and the isolated incorrect-success assertion's nonzero exit.
Keep UI and API/database evidence independent. Retain all historical503/504 outcomes.
No telemetry or adoption study is invented or introduced to score this plan.

Gate A and B have distinct commands and artifacts; Stage04 C is fail-closed for missing,
stale, failed or controlled B. B creates a clearly labeled human-authored compact PRD
in guarded test storage and approves it through real auth/API before its sole Architect
request. It never runs the PM live suite. The same generated architecture supplies every
subsequent browser/SQL/edit/approval/DAG/coverage/isolation check. Preparation validates
this source setup without paid dispatch; the source fixture is not PM model evidence.

## Independent findings, scorecard and checklist

The independent same-family voice found three high integration gaps: extend credential/
model blanking, stage-bind all evidence and source setup, and extend PM-only proxy/body/
unknown-outcome policies. All are added to the implementation contract. External CLI
model review is unavailable; this is not six confirmed cross-model comparisons.

| Dimension | Initial -> amended plan | Remaining evidence |
|---|---|---|
| Getting started |7 ->8| Warm incremental target not timed |
| API/CLI |7 ->9| New commands/routes must execute |
| Errors |7 ->9| Negative and unknown-outcome tests required |
| Documentation |7 ->9| Reproduction commands must match final code |
| Upgrade |8 ->9| Real preservation/drift required |
| Environment |8 ->9| Full deterministic pipeline required |
| Ecosystem |6 ->7| Local scope; no public support/community claim |
| Measurement |7 ->8| Runtime timing/count receipts still required |

- [ ] Add explicit Architect config/offline help and all deterministic environment blanks.
- [ ] Extend proxy/request/body/error policy without changing unrelated route deadlines.
- [ ] Preserve full regression identities and add current-stage source/profile receipts.
- [ ] Implement unpaid real source approval setup and one-request opt-in Architect B.
- [ ] Execute migration/drift/API/browser/negative checks and document actual exits.

No broader public ecosystem/hosting/telemetry work is proposed. Pass this amended plan
to Eng last; full implementation remains authorized, while no paid generation is.
