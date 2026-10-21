# Stage 03 developer-experience plan review

Mode: DX POLISH. Product type: local developer workspace with a private authenticated HTTP API and operator verification commands. Review date2026-10-19. This evaluates a proposed contract and existing Stage02 source; no PM implementation or live provider execution is claimed. Parent /autoplan overrides intermediate questions with explicit recommendations; taste choices remain at its final gate.

## Investigation and persona

Primary developer: the local ORBA owner/contributor extending an existing Next.js/FastAPI/PostgreSQL checkout. Context: Windows PowerShell, two application processes, Docker, uv and pinned pnpm; occasionally another contributor follows the README. Tolerance: a proposed5-minute warm setup, with slower cold prerequisites explicitly disclosed. Expects: preserved project/account data, copied commands, current docs, no paid request until explicitly requested, and errors that identify a safe next step. A hosted no-install customer is not the present stage's persona.

Evidence: README starts `ORBA · Stage 02`, lists six tool/runtime prerequisites, seven install/migration commands and two terminals. It supports an npm-exec fallback for missing pnpm. `scripts/verify.ps1` runs thirteen actual checks sequentially but has no Stage03/live distinction yet. Config reads `.env` relative to the API working directory. The API client discards structured error fields and uses20s for all requests; proxy has15s and no PUT. The isolated cleanup guard currently checks DB and role, despite README also promising port54330. No installed gstack history/log/brain helper is available, so no historical DX trend or helper execution is invented.

### Developer perspective (first-person evidence-grounded roleplay)

I open the README and see `ORBA · Stage 02`. Its first paragraph tells me accounts and projects work, while AI is later work. I know where I am, but a Stage03 checkout needs that sentence updated before I can discover the PM feature. The prerequisites name Node, pnpm, Python, uv and Docker; I can use the documented npm-exec fallback because pnpm is not globally installed here. I copy the install block, which protects existing env files and explicitly warns against clearing development data. I appreciate that warning because I want my projects to survive.

Next I start the API and web in separate terminals and open localhost:3000. Registering, creating a workspace and entering an idea gives me real project persistence. That is useful Stage02 value, but it is not yet a generated plan. I need a clearly linked setup section telling me where to configure a runtime key and which model my account can use. My Codex login should not be presented as that key. If I choose Generate and it fails, I want a saved run reference, a safe explanation, and a way to inspect its outcome before paying for a second request. Finally I want verification to tell me whether it exercised the actual provider, rather than bury that distinction inside a green test total.

This is a roleplay grounded in actual docs/source, not a timed new-user study or observed failed PM UI.

### Competitive/reference benchmark

Three current official sources were searched/opened during this review. Their flows are useful reference patterns, not equivalent ORBA competitors or measured timing evidence.

| Reference | Published/on-page path | TTHW evidence | ORBA lesson |
|---|---|---|---|
| [OpenAI quickstart](https://developers.openai.com/api/docs/quickstart) | Configure real API key, install official SDK, make one request | No controlled elapsed measurement supplied | Credential acquisition is a prerequisite; never borrow Codex authentication |
| [Supabase local CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) | Pinned project runner, init, start; Docker/runtime required | First image downloads take time; no universal<5min guarantee | One golden local path, disclose cold downloads and preserve local data |
| [Next.js installation](https://nextjs.org/docs/app/getting-started/installation) | Scaffold, start dev server, visit localhost | Three-step flow, no elapsed measurement | Group related steps and show the actual URL/meaningful result |
| ORBA baseline | Seven install/migrate lines + two service terminals + account/workspace/project | Fresh suite timings are test timings, not onboarding TTHW | Warm goal<=5min with prerequisites/deps/key already available; cold target must be measured |

Competitive tier target: warm competitive2–5min; cold unmeasured, not champion-rated. No dependency rewrite, hosted sandbox or fabricated timer is justified to claim a faster tier. The meaningful moment is the owner's own small brief becoming a real persisted draft, then surviving reload. Lowest-effort vehicle: existing UI plus one copy-paste local setup path and an explicitly invoked live verification command. Do not provide a fake plan/demo in the empty state.

### Nine-stage journey and friction decisions

| Stage | Actual path / proposed extension | Friction | Decision/status |
|---|---|---|---|
|1 Discover | README Stage02 heading, project future-area copy | PM entry is currently absent | Update stage/capability copy during implementation; planned |
|2 Prerequisites | README runtime/ports | Missing Docker/pnpm/provider model possible | List supported versions, runner fallback, occupied-port fix; planned |
|3 Install | Frozen pnpm + uv, env copies, Compose | Multiple working directories and cold downloads | Root commands, conditional copies, no secrets printed; existing plus planned |
|4 Upgrade/start | Stop old services, additive Alembic, two terminals | Accidental old binary against new schema | Backup/stop/migrate/drift/restart guide; no reset; planned |
|5 Authenticate | Real register/workspace/create | A model key does not authenticate an ORBA user | Reuse real sessions/CSRF; existing |
|6 First PM result | Explicit UI Generate + real provider | Absent/invalid model config, cost, variable latency | Setup guidance, exact bounded call, draft, nullable actual evidence; planned |
|7 Real usage | Edit/save/reload/approve/history | Dirty/stale revisions and permission differences | Keep buffer, exact saved revision, owner/admin approval; planned |
|8 Debug/verify | verify.ps1, run lookup, safe error code | Core success may hide no live integration | Full default includes live; explicit Core reports live NOT RUN; planned |
|9 Maintain/contribute | AGENTS, architecture, test plans, evidence | Stale stage docs, no contributor entry | Root README links required docs and exact targeted commands; planned |

First-time confusion log (illustrative ordering only, not measured elapsed time): T+0 open README Stage02 label; T+0:30 find pinned package runner; T+1:00 inspect preserved env copy commands; T+2:00 discover separate service terminals; T+3:00 ask where runtime model credentials belong. Fix all five in the Stage03 golden path; do not claim the timed roleplay actually executed PM.

## Pass 1: getting started — initial6/10 -> specified9/10

The current README provides a viable local path and a working pnpm fallback, but no PM credential/setup/result path. The warm target only starts after tool installation, dependency/image downloads and a valid provider credential/model; credential acquisition and cold network time remain separately recorded. Show three labeled blocks: install/migrate, configure/start, create/generate/verify. Each block can contain the necessary commands rather than misrepresenting nine operations as one command.

The existing project UI is the tutorial: sign in, select/create a workspace, create a project, review its brief, explicitly Generate. Expected output is described structurally as an actual draft with nonempty epics/stories/criteria and returned metadata, not a canned sentence. Configure keys only in the API process/local ignored env file, restart it after changes, and never paste keys into chat or URL arguments. A setup check must be non-billable configuration validation; only a separate explicit live command spends API usage. Actual onboarding measurement remains unrun, keeping the rating below10.

## Pass 2: API/CLI design — initial7/10 -> specified9/10

Preserve `/api/v1/projects/{id}/pm-runs` and `/pm-plans` resource names, existing cookies/CSRF and private404 semantics. Exact examples must include how a browser/session obtains CSRF; an unauthenticated curl POST example that always fails is not a usable quickstart. Expose idempotency UUID/revision semantics in schemas/OpenAPI and safe nonsecret runtime capabilities in authorized project context. Distinguish configured model from actually returned model, and timestamp run creation versus model completion.

Specify pagination defaults20/max50, deterministic descending timestamp+UUID ordering and no brief/full-document payload in history listings. Terminal replay returns the original run outcome and plan reference; active202 supplies a polling hint, with finite2s-to10s GET backoff, stop on terminal/auth loss/unmount and no automatic POST. Editing needs full-document PUT + expected revision; approval exact version/revision. A deliberate user retry uses a new key only after known terminal failure, with an explicit possible charge. No general CLI/SDK or multi-provider configuration layer is needed.

## Pass 3: errors/debugging — initial6/10 -> specified9/10

Current API validation exposes field/message, but the frontend flattens it; a network POST error always says Check Projects. PM needs structured `code`, safe `message`, optional stable `field` paths/run ID/diagnostic reference/docs anchor and safe Retry-After. Do not echo submitted values, raw provider bodies, headers or stack traces. The local operator can correlate UUIDs and safe exception type/status in internal records; adding verbose secret-bearing HTTP logging is not an acceptable escape hatch.

| Error path | Actual current experience | Required proposed experience / safe action |
|---|---|---|
| No runtime model/key | No PM handler exists; not a tested PM error | `pm_not_configured`: set named variables in apps/api/.env and restart API; saved failed run if admission occurred; no fabricated plan |
| Request outcome unknown | Generic Check Projects loses run/revision context | Keep local input and key, offer authorized Check Status; failed GET stays unknown; no charged retry |
| Invalid nested criterion / stale revision | Client joins detail messages; existing editor has only generic field scope | Linked stable field paths/opened disclosures, repair guidance;409 keeps buffer and offers latest saved revision separately |

Unrelated resources retain generic private404, without detailed existence/provenance/diagnostics hints. Safe configuration failure is actionable without exposing exact provider credential.401 refreshes sign-in state,403 refreshes current role,429 honors safe delay,504 indicates bounded timeout rather than declaring no billing. All three error paths need real code tests/UI behavior before the score can become a verified rating.

## Pass 4: documentation/learning — initial6/10 -> specified9/10

README is the entry, not a second sprawling specification. Its top section must say what Stage03 actually does, link quickstart/config/troubleshooting/live verification, and describe the local-only security boundary. Architecture owns schema/lifecycle; a dedicated Stage03 test plan owns coverage/mocks/live boundaries; verification owns actual commands, exit statuses and artifact links. Roadmap clearly separates implemented versus verified and future agents. AGENTS preserves all owner non-fabrication/security rules and the Stage03 stopping point.

Copy-paste examples use PowerShell root cwd and the documented pnpm fallback, quote paths safely, conditional-copy env files, name all required variables and never provide a supposedly valid default model. Include request/response *shapes* marked illustrative, actual response artifacts only when generated. Link a troubleshooting table with the same stable API codes and docs anchors. Proposed findability target: configuration/failure/live instructions reachable from README in<=2 links; actual two-minute discoverability study is not performed. No hosted playground or external docs system is necessary.

## Pass 5: upgrade/migration — initial7/10 -> specified9/10

Keep the authorized e3fccd6 checkpoint, external pg_dump, dev named volume and Stage02 historical evidence. New migration is additive, with empty new tables and no legacy reassignment. Old IDs/fields/timestamps/account/session/membership records must survive a populated before/after migration test. Run upgrade twice and schema drift. Current dev has zero users/projects; its successful upgrade alone cannot establish populated preservation.

Document stop API/web, backup, locked deps, upgrade/check and restart compatible app. Explain that a rollback is an explicit offline operator restore decision, not a provided drop/downgrade command. Existing ownership migration's API-port guard and the new revision's behavior must be covered; do not disable the old guard merely because it is inconvenient. No Stage01/02 endpoint contract should change except safe shared transport extensions; required regression suite validates that assumption. A codemod/versioned public SDK is not relevant to this local additive stage.

## Pass 6: environment/tooling — initial7/10 -> specified9/10

Reuse uv/pnpm locks, Ruff, strict TS, ESLint, actual Next production build and Playwright workers1/retries0. Strengthen destructive-test guards to require explicit loopback host, port54330, `orba_test` role and DB before migration/reset; cleanup only new test tables and existing guarded test data. Never run backend and browser cleanup concurrently. Refuse occupied test API/web ports and never reuse development services. API credentials belong to the child API environment, not NEXT_PUBLIC values or browser config.

Extend the existing `verify.ps1` with explicit `-Mode Core|Full`, default Full. Core executes deterministic application/security regressions with clearly labeled unit/error doubles and real database/browser fixtures, and reports live API/browser NOT RUN; Full additionally invokes the bounded live API and live browser flows, and cannot exit0 when runtime credentials/live evidence are missing. Both modes retain real exit codes. No new fake-provider environment switch exists in application runtime. Public model selection remains explicit configured model; timeout/output/admission limits are validated settings. No cross-platform/macOS/native-device claim follows from this Windows run.

## Pass 7: community/ecosystem — initial6/10 -> specified8/10

This is an owner-local checkout with no Git remote. There is no evidence of public licensing, community support SLA, marketplace, plugin ecosystem or customer pricing; do not invent any. Contributor guidance can be a concise README section linking AGENTS/test plan and the evidence contract. Bugs should include safe command/run references and reproduction, never cookies, key-bearing traces, raw credentials or unrelated project briefs.

Show provider usage as actual nullable counts, not invented dollar costs/free-tier assurances. Explicit Generate and a clearly described Full verification command are the cost boundaries; a core check must not unexpectedly call the model. Defer public community channels, support integrations, pricing UI and skill/plugin distribution: they add external surface unrelated to the requested PM stage.8/10 reflects deliberate local-scope fit, not a populated community.

## Pass 8: measurement/feedback — initial5/10 -> specified8/10

Use local reproducible evidence: process startup durations, provider-call elapsed time from real timestamps, returned usage/counts, database persistence and test totals/exit codes. Add one warm-path timing exercise once implemented, record machine/cache/config preconditions, and keep credential acquisition/cold downloads separate. Do not equate44/42 regression results with PM usability. Record the live artifact quality rubric against the real brief, with uncertainty and shortcomings retained.

No new external analytics, event forwarding or surveys are authorized. Safe local verification artifacts and owner feedback suffice. Future comparison should report which dimensions were actually timed/browser-tested versus inferred from the plan.8/10 leaves actual onboarding/long-document measurements unearned. The absence of gstack logging helpers is documented; file-backed evidence does not pretend those helpers ran.

## Scorecard and principle coverage

Scores rate specification completeness after fixes, not implemented DX or test success.

| Dimension | Initial | Proposed specification | Evidence still required |
|---|---|---|---|
| Getting started |6|9| Actual cold/warm onboarding |
| API/CLI |7|9| Real contracts/replay/revision tests |
| Errors |6|9| Failure UI/API and sanitized diagnostics |
| Documentation |6|9| Reproduce written commands |
| Upgrade |7|9| Populated migration/old regression |
| Environment |7|9| Full/core real exit behavior |
| Community/local contributor |6|8| Safe contributor issue procedure |
| Measurement |5|8| Actual PM timing/quality records |
| Mean |6.25|8.75| Not a runtime rating |

TTHW current: unmeasured. Warm target<=5min; cold unmeasured/needs-work until measured. Magical moment: designed via own-project UI/live verification, not executed. Zero friction: bounded prerequisite disclosure; Learn by doing: real brief; Fight uncertainty: typed errors + GET recovery; opinionated defaults + escape hatches: validated limits, explicit model, no security bypass; Code in context: root PowerShell commands; magical moment: real persisted draft. No Claude Code Skill appendix applies to the product itself.

## Decision audit and implementation checklist

| ID | Finding | Decision / principle | Alternative rejected |
|---|---|---|---|
|DX-D01| Missing PM quickstart | Three honest blocks, preserve commands, P5 | Hidden new global bootstrap service |
|DX-D02| Credential ambiguity | Explicit API .env key/model + restart, P1/Explicit | Codex auth or guessed model default |
|DX-D03| Unmeasured timing | Separate warm target and cold measurement, P1 | Claiming<5min from command count |
|DX-D04| Live/core ambiguity | Full default, explicitly labeled Core, P1 | Core green reported as Stage03 verified |
|DX-D05| Cleanup guard drift | Check exact loopback test host/port/role/DB, P1 | Destructive reset based on DB name alone |
|DX-D06| Errors lose context | Preserve typed safe codes/paths/refs, P1 | Raw provider bodies or generic Check Projects |
|DX-D07| History/chatty polling |20/max50 deterministic summaries, bounded GET backoff, P5 | Full documents in unbounded history |
|DX-D08| Unclear current source | Required docs share stage authority/evidence links, P1 | Duplicate standalone instructions |
|DX-D09| No community evidence | Local contributor guide only, P3 | Invent support/pricing/marketplace |
|DX-D10| Timing/truth evidence | Local measurement, no external analytics, P5 | Fabricated or externally transmitted metrics |
|DX-D11| Config/transport/readiness | Preserve caller cancellation, explicit config aliases and PM schema readiness, P1 | Ignored settings or configured-means-connected claim |
|DX-D12| Required exact recovery | Own-client-key GET and precise empty/active/terminal behavior, P1 | Guessing recent history or optional recovery |

All checklist items are proposed implementation tasks, not completion claims: [ ] golden path/config/troubleshooting; [ ] safe typed API errors; [ ] documented replay/revision/pagination; [ ] strengthen test guard; [ ] extend verify Full/Core with bounded live tests; [ ] additive upgrade/preservation guide; [ ] reproduce every required command; [ ] record actual PM runtime and blockers.

## Implementation tasks

| ID | Component/files | Title / source | Priority | Human / agent-assisted estimate | Verification |
|---|---|---|---|---|---|
|DX-T1| README, API/web env examples | Real-model golden path and troubleshooting; passes1/4 |P1|0.5d /30–60m| Copy commands from clean shell; no key echoed |
|DX-T2| API errors/schemas, web client/proxy | Stable PM codes, fields, references and GET recovery; passes2/3 |P1|0.5–1d /45–90m| Actual invalid/offline/config responses |
|DX-T3| prepare_tests, verify.ps1, test configs | Strict test targets and Full/Core/live workflow; pass6 |P1|0.5–1d /45–90m| Nonzero missing-live check, sequential real suites |
|DX-T4| docs/AGENTS/verification | Migration guide, evidence boundaries and local contributor path; passes4/5/7 |P1|0.5d /30–60m| Populated preservation + reproduction audit |
|DX-T5| live verification/evidence | Actual timing/usage/quality and honest blockers; pass8 |P1|0.5d /30–60m| Actual API/browser model calls |

Deferred: hosted playground, global CLI/SDK, multi-provider hub, public support/pricing, automatic telemetry and broad platform certification. Preserve in TODOS with rationale/effort/dependencies; do not implement them. No new taste beyond the existing admission/disconnect/presentation choices is required by this primary DX review. Independent voice and CLI disposition must be added before phase completion.

## Independent voices, consensus and completion

[Fresh independent voice](STAGE03_DX_INDEPENDENT.md) read a physically scoped contract excerpt and current source only, and supplied six ranked findings. [CLI voice](STAGE03_DX_CLI.md) completed with exit0 and six findings after the first voice; it did not read other DX artifacts. Both voices are Codex-family, not cross-model evidence. A supplemental [source review](STAGE03_DX_VOICE.md) disclosed accidental exposure to CEO/Design summaries and is therefore not counted as the required blind voice. The replacement independent review avoids that limitation.

The CLI opening sentence assumed runtime configuration was present. That assumption is rejected: intake's actual presence check found key/model absent, and no subsequent credential confirmation or successful call establishes otherwise. Configuration remains a mandatory live blocker until checked and executed. The review's remaining source findings distinguish current code from planned contracts; none is live-generation evidence.

| Dimension | Fresh independent voice | CLI | Disposition |
|---|---|---|---|
| Getting started<5min | No timed evidence | Conditional warm target | Confirmed evidence gap: unmeasured target only, cold/model provisioning separate |
| Guessable API | Conditional contract/examples | Conditional recovery naming | Confirmed: exact own-key lookup/envelope/revision semantics now mandatory |
| Actionable errors | Conditional proposed, current loses data | No current typed transport | Confirmed: carry codes/paths/refs/delay, distinguish before-send/rejected/unknown |
| Findable/complete docs | No current Stage03 quickstart | No current Stage03 quickstart | Confirmed: update actual root entry point on implementation |
| Safe upgrade | Conditional populated/guard checks | Conditional same risks | Confirmed: stronger test target, disclose dev migration, preserve all old data |
| Reproducible tooling | Conditional Full/Core/model prerequisites | Conditional Full/Core live gates | Confirmed: no green full verdict absent actual API/browser generation |

Six shared concerns, zero substantive disagreements and zero User Challenges. Verdict words differ between current-code readiness and future-plan sufficiency; they do not establish product PASS. Existing taste C04/C05 remain at the final gate, not duplicated. DX-D11 (mechanical P1): preserve caller cancellation, explicit model setting aliases and PM readiness checks; do not silently ignore config or imply configured means connected. DX-D12 (mechanical P1): make own-client-key GET lookup and exact reconciliation mandatory, reject recent-history guessing or optional recovery. Main plan now explicitly defines the response envelope, empty/active/terminal behavior and limits of Save reconciliation after subsequent edits.

All eight passes, nine-stage journey,180+-word narrative, actual-source friction trace, nonmeasured competitive references, scorecard/checklist and five task rows are written. JSONL was serialized with installed jq; an initial whitespace parser found zero table tasks and was corrected to require/serialize the actual five, with no application test result affected. Completion score8.75/10 is specification-only; TTHW remains unmeasured with<=5min warm target. Pass the amended plan to Eng last; no PM product code or live call was performed.
