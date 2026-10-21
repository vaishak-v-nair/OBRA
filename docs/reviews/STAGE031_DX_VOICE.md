# Stage03.1 independent DX review

Date: 2026-10-19. Review type: static repository and plan assessment. Recommendation: proceed with the Gate A/B/C direction after making the command, failure and receipt contracts below explicit. This is a planning review, not a Stage03 verification verdict.

The reviewed surface was `docs/STAGE031_PLAN.md`, README, repository instructions, verification/package scripts, API configuration/provider/error/migration code, test-database helpers, Playwright configurations and live/negative scenarios, plus the current test and verification documentation. Other review documents and skill definitions were not consulted. No services, tests, database queries, configuration checks or model requests were executed; no credentials or ignored environment files were read. Historical execution statements in documentation were treated as recorded history, not independently reverified evidence.

## Eight DX dimensions

| Dimension | Assessment of the current source | Stage03.1 acceptance condition |
|---|---|---|
| 1. Getting started and first useful result | Needs change. README gives locked installs, exact loopback ports and a real account/workspace/project journey, but the first verification command defaults to paid-capable Full. | A newcomer can install, migrate the isolated test DB, run Gate A and use core project features without provider configuration or an external AI request. First-use instructions identify what success proves. |
| 2. API and CLI consistency | Needs change. Root/web package aliases are understandable, but `verify.ps1`, direct Python live verification and `test:e2e:live` expose different prerequisites and independent paid entrypoints. | One authoritative Gate A command and one explicitly authorized Gate B command; low-level live entrypoints enforce or participate in the same prerequisite contract. A browser generation supplies the actual listening-API assertions without a second paid API probe. |
| 3. Error feedback and recovery | Useful base; needs a command-level contract. Public PM errors already carry a code, safe message, run and diagnostic references, and distinguish uncertain outcomes. Native check failures currently end in a generic exception. | Every failure says what failed, the known cause or uncertainty, the next safe action and whether dispatch occurred. Recovery remains GET-only until a terminal outcome is confirmed. |
| 4. Documentation findability | Needs change. README links architecture/current evidence and explains auth well; Stage03.1 is not linked from its verification instructions, while the Stage03 test plan still prescribes Full and two paid probes. | A short command table in README links the Stage03.1 gate contract, historical record, troubleshooting and exact evidence locations. Historical commands remain labeled historical rather than appearing as current acceptance instructions. |
| 5. Local environment and tooling | Needs change. Loopback bindings, real PostgreSQL guards, frozen locks and rejected occupied E2E ports are good. The `.next/dev` lock and absent-global-pnpm fallback add hidden iteration cost. | Early, nonsecret preflight identifies missing tools, test-port conflicts, the development frontend lock and browser installation before tests run. The documented npm-exec fallback also works for Playwright's nested `pnpm exec next` command. |
| 6. Testing and iteration loop | Needs change. Sequential workers and zero retries support honest results. Core still invokes an actual external-provider negative scenario, and the test DB is shared across independent commands. | Gate A never depends on external AI access; controlled-provider failure browser tests are explicitly labeled and use real API/auth/PostgreSQL. A shared run lock prevents concurrent cleanup across backend/browser/live/fixture entrypoints. No automatic retry conceals a failure. |
| 7. Safe upgrades and compatibility | Useful base; needs test-only targeting. The stopped-old-API rule, forward ownership migration, preserved named volume and lockfile compatibility notes are clear. Verification's standalone Alembic commands currently resolve normal runtime DB configuration. | Gate A explicitly validates and uses only guarded `orba_test` for migration/drift checks. Upgrade guidance preserves development data and ignored configuration, records compatibility exceptions and never recommends reset/downgrade/global-tool repair. |
| 8. Evidence, reproducibility and handoff | Needs change. Existing documents preserve Full failure separately from standalone success. Fixed transcript/JSON paths overwrite attempts; the browser report is written only at final success and has no source binding or independent SQL audit phases. | Immutable, schema-validated attempts bind source/configuration/test identity, actual child exits and artifact hashes. Gate C rejects missing/stale/incomplete/tampered proof and distinguishes deterministic, controlled-provider and genuine live evidence. |

## Concrete findings and fixes

Severity: P0 requires resolution before any new paid verification; P1 blocks acceptance of the proposed gates; P2 creates avoidable developer friction. These are source findings, not claims of newly observed runtime failures.

### DX1 — P0: normal verification still crosses the live boundary

**Problem:** `scripts/verify.ps1:1` defaults to Full; lines 28–33 run the provider-negative browser test and both positive live commands. Core excludes only the two positive calls. `apps/web/playwright.negative.config.ts:7` supplies an intentionally invalid credential to the actual SDK, and `tests-negative/provider-failure.spec.ts:1–2` explicitly identifies its external request. Therefore renaming Core to Gate A alone would retain external AI dependence. The existing direct live commands have no Gate A/owner-approval prerequisite (`apps/web/package.json:13`, `apps/api/scripts/verify_pm_live.py:34–60`).

**Fix:** make bare `verify.ps1` deterministic Gate A. Replace the external negative dependency with the specifically authorized, test-only controlled-provider failure path; keep its boundary visible in names and receipts. Give `verify-live.ps1` the sole documented paid workflow, with explicit paid opt-in, a current passing Gate A receipt and later explicit owner approval. Guard low-level live entrypoints too, so a package alias or direct Python command cannot accidentally bypass the workflow. Do not silently map the old `-Scope Full` spelling to a paid call; reject it with the replacement command and nonzero status, or retain only an explicitly nonpaid compatibility behavior documented as such.

An opt-in flag expresses operator intent; it cannot invent the owner's later approval or reuse approval for an unbounded future attempt. Do not automatically rerun Gate A, repair configuration, continue a failed generation or invoke another model to satisfy Gate B.

### DX2 — P1: evidence currently has no durable identity or freshness contract

**Problem:** the transcript uses `-Force` on a fixed path (`scripts/verify.ps1:6`); Python writes `stage03-live-api.json` with `write_text` (`verify_pm_live.py:142–145`); the browser writes `stage03-live-browser.json` only after the last assertion (`pm-live.spec.ts:42`). A crash or an earlier assertion failure can leave an older success file available. Neither file binds the source that produced it. File existence and a manually supplied `mocks:false` are not proof.

**Fix:** use one versioned manifest implementation across A/B/C. Include uncommitted application/provider/prompt/schema/migration sources, lockfiles, relevant tests/configuration, runner and validator code. Explicitly exclude secrets, caches and generated evidence; document the inclusion rule and detect source drift before/after a gate. Create a unique attempt directory exclusively, begin with an incomplete status, record child results and atomically finalize without overwriting prior attempts. Hash artifacts and validate their schema, gate type, source fingerprint, command completion, exit status and parent Gate A reference before any passing summary. Bind relevant nonsecret runtime settings separately; never hash or emit credentials or briefs. Keep historical Full failure and later standalone outcomes individually addressable.

### DX3 — P1: consolidating paid calls must preserve draft and approval proof

**Problem:** the live browser observes actual API responses and approval, but its initial GET only parses JSON and checks some graph fields (`pm-live.spec.ts:24–25`); its final report contains API metadata, not an independent relational audit. `inspect_pm_run.py:26–50` lists plan summaries but does not validate the complete graph, exact revision/actor or recomputed content hash. The separate API script does use a fresh SQLAlchemy session, but removing its paid request must not remove that proof.

**Fix:** use the single real browser generation, then assert actual POST/GET status, run/plan linkage and the full application contract through the real listening API. Before editing or approval, run a guarded, fresh-session SQL audit of the persisted draft and complete graph: same run/project/workspace/version/revision, expected provenance, valid relations, recomputed hash, draft state and absent approval. After the real user edit/save/reload/approval, run a second independent audit binding the exact saved revision, content hash, approver and timestamp, with no mutation to the approved version. Store separate draft/approval receipts under the same attempt and only then allow cleanup. These checks must query actual rows and fail on missing/mismatched data; authored fixtures and API JSON alone cannot satisfy the live SQL requirement.

### DX4 — P1: define nonzero outcomes and preserve native command failures

**Problem:** current `Run-Check` captures `$LASTEXITCODE` immediately after the pipeline and throws on nonzero (`verify.ps1:8–13`), which is a useful base. It records neither an attempt-wide structured result nor a completed command record when process launch fails. The new prerequisites add refusal cases that must not look like skipped success. No such failure cases were executed for this review.

**Fix:** record gate state and child state separately, including start/end time, safe command identity, launch failure versus native exit, original exit code and evidence path. Exit nonzero for any refusal/failure/incomplete attempt. A catch/finally that writes evidence or stops a transcript must preserve the failing gate exit. Do not interpret PowerShell's successful final statement, stale `$LASTEXITCODE`, missing test output or an existing old report as success. Keep the deliberately incorrect exit1 experiments separate; verify that they failed for the intended assertion, not just for any import/service error.

Required operator-facing outcomes:

| Condition | Gate result and process exit | Problem / cause / next safe action |
|---|---|---|
| Live opt-in absent | BLOCKED, nonzero; zero dispatch | Paid verification was not requested. Obtain the later owner approval, then invoke the documented live command with explicit opt-in. |
| Key/model absent or invalid | BLOCKED, nonzero; zero dispatch | Name only missing/invalid setting fields. Preserve existing environment files, resolve the specific configuration issue and restart the API where relevant. Configuration preflight is not access proof. |
| Gate A receipt missing, failed or source-stale | BLOCKED, nonzero; zero dispatch | Identify the failed prerequisite or fingerprint mismatch. Run current Gate A explicitly and review its result before seeking/using live authorization. |
| Evidence missing, truncated, wrong gate or hash-mismatched | Nonverified verdict, nonzero | State which artifact/check failed. Repair the evidence-producing implementation and rerun the affected permitted gate; do not fill in a success JSON manually. |
| Native check returns nonzero | FAILED, nonzero | Show command identity, original native exit and transcript path; correct the actual cause. Do not overwrite the attempt or rerun automatically. |
| Executable unavailable, Docker/DB unavailable, browser unavailable or test port occupied | BLOCKED, nonzero | Identify the dependency/port and documented recovery. Do not kill unrelated services, reset development data or install/upgrade global tooling automatically. |
| Provider rejection/timeout after authorized dispatch | Actual failure recorded, nonzero | Preserve safe provider category/origin, run/diagnostic references and dispatch uncertainty. Usage may have occurred. Check the same run with GET; any new paid attempt needs explicit bounded authorization. |
| Child interrupted or receipt not finalized | INCOMPLETE or BLOCKED, nonzero | State that no complete result exists. Preserve its files and references; recover state before deciding whether another attempt is safe. |

Exact numeric refusal codes may be kept simple, but must be documented and consistent. A distinct reason code in structured evidence is needed even if all blocked cases use process exit1.

### DX5 — P1: Gate A must not inherit the development database target

**Problem:** `verify.ps1:20–21` runs standalone Alembic upgrade/check without a test DB override. `apps/api/migrations/env.py:11,22` resolves `Settings().database_url`; its default points at development port54329 (`orba/config.py:9`). Meanwhile test fixtures independently validate/use test port54330 (`tests/conftest.py:11–27`). This produces two different targets inside one verification command.

**Fix:** validate the exact guarded test scheme/loopback/port/database/role before migrations or cleanup, apply that target explicitly to both migration and drift commands, and restore any temporary process environment in finally. Report only safe target host/port/database/role, never a credential-bearing URL. Development migration remains an explicit install/upgrade action, with the existing stopped-old-API safeguard. A Gate A run should not require modifying the owner's `.env` or upgrading their development database.

### DX6 — P2: the supported pnpm fallback must reach child processes

**Problem:** README supports absent global pnpm by wrapping commands in `npm exec --package=pnpm@12.14.0`. All Playwright web servers still invoke the bare command `pnpm exec next ...` (`playwright*.config.ts`). That relies on the ancestor invocation supplying pnpm on PATH; direct Playwright use is a different context. The development frontend's `.next/dev` lock also conflicts with tests despite separate ports, as README already acknowledges.

**Fix:** document one verified invocation route and ensure its child-process tool resolution uses the pinned package manager consistently. Fail early with the exact supported wrapper if the required context is missing. Move the existing stop-development-frontend instruction directly beside the Gate A command and list3000/3001/8001 plus the shared build lock in troubleshooting. Do not silently change a user's global pnpm or terminate their dev process. Check browser installation before the long suite; do not spend an authorized live attempt discovering a missing Chromium binary.

### DX7 — P2: current and historical verification commands need one index

**Problem:** README's main verification block advertises bare Full and individual paid commands (`README.md:124–145`), and the Stage03 test plan still says Full is mandatory (`docs/STAGE03_TEST_PLAN.md:173–202`). The Stage03.1 plan describes replacements but is not linked from the main README verification entry. A developer following the most visible instructions can take the older paid path after Stage03.1 is implemented.

**Fix:** put a compact current command table in README: setup, Gate A, no-generation configuration preflight, Gate B after authorization, and evidence/verdict inspection. Label Gate B as not run by Gate A and label its browser/provider billing boundary before the command. Update current architecture/test-plan/verification reproduction sections together. Preserve older Full commands/results in a historical section; do not rewrite their exits. State that package-level component tests are diagnostics and do not create a complete current gate receipt.

### DX8 — P2: diagnostics should resolve uncertainty without prescribing another POST

**Problem:** provider code uses safe categories and messages, but `provider_timeout` covers both local timeout exceptions and upstream HTTP504 (`pm_provider.py:231–266`). The public error only has a generic `#pm-setup` documentation hint (`pm_errors.py:29`), which is useful in the project UI but weak for CLI/API troubleshooting. Runtime settings can also override root configuration (`config.py:34–40`), while the setup message names only the root file.

**Fix:** preserve the public error shape and add bounded phase/origin timings to safe diagnostics and gate receipts. Name local SDK timeout, upstream504 and browser/proxy loss separately when actually observed; use unknown when not established. Link CLI documentation to a stable repository troubleshooting section explaining configuration precedence, exact run lookup and GET recovery. Display active nonsecret limits/model after configuration preflight without implying provider access. Never instruct users to raise timeouts, clear a request reference or submit a new POST as the default repair for an uncertain result.

## Nine-stage developer journey

| Stage | Developer intent and entrypoint | Required experience / completion signal |
|---|---|---|
| 1. Discover | Open README and identify the current stage. | Stage03 scope and A/B/C responsibilities are visible; previous PARTIAL history is linked. No instructions imply Stage04, deployment or paid generation by default. |
| 2. Install | Use pinned pnpm/uv and Docker prerequisites from repository root. | Frozen locks succeed or identify the exact missing tool/version; the no-global-pnpm route covers child commands. No global repair is assumed. |
| 3. Configure | Set up local API/web values; optionally inspect PM configuration. | Existing ignored files are preserved. Root/API/process precedence and exact origin/loopback ports are clear. `check_pm_config` performs no generation and says that explicitly. Core features do not require a model key. |
| 4. Upgrade safely | Follow the explicit development migration path. | Old unauthenticated API is stopped; existing projects/legacy restrictions and named development volume remain. No reset/downgrade is offered as a shortcut. |
| 5. Reach first core success | Start API/web, register, create a workspace, create/open/reload/list a project. | Actual authorized persisted data is visible, with loading/empty/error states. Product Plan setup/empty state neither fabricates a run nor generates automatically. |
| 6. Iterate deterministically | Stop the conflicting dev frontend and run bare `verify.ps1`. | Gate A uses real isolated PostgreSQL/API/browser sequentially, explicitly labeled failure doubles only at the authorized provider boundary, no external AI dependency, and an immutable passing or failing receipt. |
| 7. Diagnose and recover | Read a failing command/run and use documented recovery. | Problem/cause/fix, actual exits, dependency details and safe IDs are available. Unknown writes retain their references; GET recovery precedes any fresh POST. Drafts and approved versions survive failures. |
| 8. Verify live with approval | Review current Gate A/diagnostics, obtain later owner approval, then explicitly opt in to `verify-live.ps1`. | Exactly one bounded genuine browser generation, actual API checks, independent draft and approval SQL audits, sequential execution, no retry/duplicate API generation, and a receipt for every attempted outcome. |
| 9. Interpret and maintain | Inspect Gate C and later change/upgrade source. | Current fingerprint-bound proof determines the verdict. Stale/missing/incomplete/failed evidence exits nonzero. Historical Full failures and standalone outcomes remain separate; a source change requires new applicable evidence rather than inheriting a prior green file. |

## Minimal plan amendments

1. Specify the public command names/options and migration behavior for old Full/Core callers before changing scripts. Keep only one documented live workflow.
2. Define one gate-result schema and source-manifest policy shared by all entrypoints; define incomplete, blocked, failed, passed and nonverified-summary behavior explicitly.
3. Put the no-external-AI Gate A boundary under a meaningful regression check, including the former invalid-key negative browser path.
4. Add independent draft and approval SQL audits to the existing browser flow before deleting the duplicate paid API request. Audit failure must fail the live attempt.
5. Test missing opt-in, missing/invalid configuration, missing/failed/stale Gate A, edited artifacts, native exit/launch failure, incomplete child execution and source drift without making a model call. Use actual failing subprocesses and real guarded integration dependencies where required; do not replace the production gate with a dummy success driver.
6. Preserve safe command failures and historical records, run deterministic Gate A, then stop for the owner's later live authorization. This review supplies no live evidence or authorization.
