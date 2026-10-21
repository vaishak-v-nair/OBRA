# ORBA Stage 03.2: provider readiness and live verification

Recorded 2026-10-20 (local timezone Asia/Calcutta; immutable receipts use UTC). **Stage 03 remains PARTIAL. Gate A passed. Current-source Gate B has NOT RUN.** The next paid generation requires fresh owner authorization. This preparation made zero new paid model-generation requests.

The previous password-policy report is preserved in [VERIFICATION_PASSWORD_POLICY.md](VERIFICATION_PASSWORD_POLICY.md). Earlier Stage 03/03.1 reports, real successes, HTTP 504 and HTTP 503 failures remain separate historical evidence. A later passing local check does not rewrite a failed attempt.

## A. Provider/model availability findings

The exact configured model remains **gemini-3.8-flash** through the official Google GenAI SDK **2.31.0**. No model or credential was changed. The account catalog actually listed this identifier with generateContent and input/output limits of 1,048,576/65,536. Other observed text-model identifiers include gemini-3.7-flash, gemini-3.6-flash and gemini-3.5-flash; they were not substituted or used for generation. [Recorded account catalog](evidence/stage032-model-metadata.json).

After the current Gate A passed, the new native CLI made **one read-only models.get request**, exited **0**, and reported **ready_for_attempt**, HTTP **200**, in **619.754 ms** (native process: 2.108s). Its exact metadata model is models/gemini-3.8-flash. The actual CLI report and its strict source/profile/A-receipt linkage were validated using the same recorder/validator that Gate B will use. [Preparation record](evidence/stage032-readiness-preparation-20261020T084607Z/preparation.json), [metadata artifact](evidence/stage032-readiness-preparation-20261020T084607Z/model-readiness.json), [actual CLI output](evidence/stage032-readiness-preparation-20261020T084607Z/provider-readiness.log).

[Google's model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) documents stable 3.8 Flash, structured output and LOW thinking. [Models API documentation](https://ai.google.dev/api/models) defines the read-only metadata operation. The installed SDK accepts the request types; controlled HTTP tests verify serialization and disabled retries. **Recommend retaining the selected 3.8 model.** No alternative is necessary on the present metadata evidence.

Metadata is not proof of actual structured generation, grammar acceptance, paid access, remaining quota, latency or PostgreSQL persistence. The readiness command sends no brief, project context, token-count request or generation request. Its live_generation_verified field is always false. [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) depend on the provider project and tier; those active quotas remain unknown. [Official-reference findings](evidence/stage032-provider-docs.json).

## B. Changes made

| Important files | Responsibility |
|---|---|
| apps/api/orba/pm_readiness.py | Typed, safe offline/metadata states; one explicit official SDK GET; fixed Google HTTPS endpoint, bounded response, no redirects/environment proxy/pagination/retry; no database or generation |
| apps/api/scripts/check_pm_config.py | Offline default; deliberate --check-model; real argparse/help; safe invalid-settings handling without secret-bearing validation text |
| apps/api/scripts/verification.py | Separate actual native readiness/browser commands in B; immutable readiness content linked to exact A hash, source, profile, attempt and ordered timestamps; nested preflight and Gate C remain network-free |
| apps/api/scripts/verification_baseline.json | Additive mandatory identities; retains every old test and requires 224 backend, 60 core and 30 controlled browser cases |
| apps/api/tests/test_pm_readiness.py and test_readiness_evidence.py | 38 metadata/CLI cases and 23 evidence cases; explicitly authored SDK HTTP/report doubles, not live model evidence |
| apps/api/tests/test_pm_reliability.py | Separate-client exact-key race, actual SDK synthetic 503 with approved-plan preservation, and independent-session observation after real SQL child flush/rollback |
| apps/api/tests/controlled_app.py; apps/web/tests-controlled/pm-recovery.spec.ts | Strictly test-only model override; real auth/API/PG/browser 503/429/malformed/retry/duplicate-request checks across three viewports |
| apps/web/tests/generation-budget.ts; tests-live/pm-live.spec.ts | Forward the original first generation POST; abort every subsequent POST before dispatch; record attempted/forwarded/blocked counts; require 1/1/0 for a successful live gate |
| apps/web/tests/projects.spec.ts | Fix ambiguous description locator; independently assert saved overview and editable brief, including after reload |
| apps/api/tests/test_verification.py | Three new literal-identity regressions; only module path separators normalize, never parameter text; changed/missing identities still fail |

The actual generation adapter, versioned prompt, Pydantic product schema, generation lifecycle, migrations, authentication, workspace permissions, password policy and UI themes are unchanged. New-password validation remains 15–128 Unicode code points; legacy login remains 1–128, without forced resets or session invalidation. [Reviewed plan](STAGE032_PLAN.md), [test plan](STAGE032_TEST_PLAN.md).

Readiness distinguishes not configured, invalid configuration, unsupported model metadata, credential problems, upstream unavailability, rate limiting, timeout, ready for an authorized attempt, and unknown. Only the selected model's complete positive metadata and reviewed structured-output documentation qualify as ready_for_attempt; unreviewed model compatibility stays unknown. No general Model Hub or public credential-backed readiness endpoint was added.

## C. Timeout and request-path assessment

```text
Browser -> same-origin Next proxy -> FastAPI (auth transaction released)
        -> official SDK -> strict Pydantic validation -> short PostgreSQL publication
Unknown browser outcome -> retained UUID -> authorized GET recovery, never automatic POST
Operator readiness -> official SDK metadata GET only; no project or database context
```

| Deadline/limit | Effective value |
|---|---|
| Metadata server/HTTP; outer envelope; native command | 10s; 12s; 30s including startup |
| Generation server; transport; outer envelope | 90s; 95s; 100s, unchanged |
| Pending-start budget; active lease | 20s; 135s |
| API startup/publication backstops; Next upstream timeout | 60s/285s; 290s |
| UI generation timeout; live response observation; whole live test | 300s; 260s; 300s |
| Live browser native command | 900s including service startup, generation, SQL audits, editing and isolation |
| SQL lock; statement; transaction | 1s; 2s; 10s; no transaction held during model work |
| Generation output; active concurrency | 6,000 combined output/thinking tokens; 1 |
| Local account/global admission | 3/account/hour; 6/global/hour; not provider quota |

The provider's normal 100s envelope fits within the proxy/browser bounds. Broader publication and browser observation backstops are separate failure boundaries, not latency guarantees. A browser failure can leave bounded server work running; it must retain the UUID and use GET-only recovery. No POST is automatically replayed. Actual upstream HTTP 504, transport timeout, local envelope timeout and proxy failure remain distinct diagnostics; stored pre-commit timing and acknowledged terminal commit are separate.

Historical run **5421d0db-f2da-4886-b583-d5c8acf99dee** received **upstream 503 UNAVAILABLE in 1,537.654 ms**. The client received 502/provider_unavailable, the run stayed failed, and independent SQL found zero plans. This was not a local 90s timeout. Earlier run **979a3a0c-b657-49af-b219-2dab98b79f34** received actual upstream **504 DEADLINE_EXCEEDED** in the direct API Full command, bypassing Next/browser. [Investigation](STAGE031_TIMEOUT.md), [503 receipt](evidence/stage031/20261019T170920Z-B-26bec4ac/receipt.json). No timeout increase or upstream-availability fix is claimed.

## D. Deterministic Gate A results and actual commands

**PASS, native exit 0.** [Immutable receipt](evidence/stage031/20261020T083556Z-A-15fa5007/receipt.json), [native wrapper exit](evidence/stage032-gate-a-final-native-exit.json), [console](evidence/stage032-gate-a-final-console.txt).

- **224 backend tests passed** in 54.82s; one third-party SDK/Python deprecation warning, no skipped/xfail cases.
- **60 core browser tests passed**, covering existing Stage 01/02/03 behavior on desktop, mobile and tablet Chromium emulation.
- **30 controlled-provider browser tests passed** on the same three viewports; no retries/skips/flaky results.
- All prior identities remain mandatory. All 14 native commands exited 0; structured report validation passed too.

Backend integration tests and browser flows use the guarded **real PostgreSQL orba_test** database, real API, authentication and browser. Narrow SDK/model/report doubles are explicitly labeled and do not prove live Gemini generation. Backend and E2E were executed sequentially. No development project data was reset.

| Actual native argv | Exit | Duration |
|---|---:|---:|
| `docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres` | 0 | 0.863s |
| `uv sync --locked --directory apps/api` | 0 | 0.064s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile` | 0 | 1.297s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm peers check` | 0 | 1.302s |
| `uv run --directory apps/api alembic upgrade head` | 0 | 1.602s |
| `uv run --directory apps/api alembic check` | 0 | 1.667s |
| `uv run --directory apps/api pytest -q --junitxml=E:\BrosKi\OBRA\docs\evidence\stage031\20261020T083556Z-A-15fa5007\backend.xml` | 0 | 58.677s |
| `uv run --directory apps/api ruff check .` | 0 | 0.07s |
| `uv run --directory apps/api ruff format --check .` | 0 | 0.085s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm typecheck` | 0 | 3.801s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm lint` | 0 | 8.029s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm build` | 0 | 9.169s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e` | 0 | 219.012s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:controlled` | 0 | 273.285s |

### Earlier attempts preserved without rewriting

| Attempt/check | Actual outcome |
|---|---|
| First focused readiness suite | Exit 1: 37 passed/1 setup error; guarded PostgreSQL connection timeout while Docker engine was unavailable |
| Initial Compose startup | Exit 1: Docker Desktop Linux-engine named pipe absent. docker desktop start --timeout 60 then exited 0; corrected test-postgres startup exited 0 |
| Initial metadata collector | Exit 1: AsyncPager has no next_page_token; two metadata GET attempts, zero generation. Corrected bounded catalog collector separately exited 0/HTTP 200; no auto pagination |
| Initial Ruff passes | Exit 1: implicit string-concatenation/import-order defects; fixed formatting/imports without changing assertions |
| Corrected focused backend | Exit 0: 96 passed, one SDK warning, 8.19s |
| Standalone TypeScript/output wrapper | Actual TypeScript exit 0; parent wrapper exit 1 printing a check-mark under cp1252 before lint. UTF-8 parent environment corrected; failure preserved |
| Focused new browser scenarios | Exit 0: 12 passed across desktop/mobile/tablet; explicitly controlled model, real browser/auth/API/PG |
| First full A: 20261020T081357Z-A-39eae2fe | Exit 1: 221 backend passed, core 59 passed/1 failed; controlled NOT RUN. Description locator matched both saved paragraph and editable brief. Precise overview/brief/reload assertions fixed the cause |
| Second full A: 20261020T082305Z-A-1ab7fc65 | Exit 1 despite all 14 native commands 0 and 221/60/30 tests passed: evidence validator incorrectly normalized a slash inside a parameter ID and rejected one mandatory case |
| New JUnit regressions before fix | Exit 1: 2 failed/1 passed, 29 deselected in the targeted run; literal slash and embedded .py:: parameters exposed the bug |
| Corrected JUnit/verifier checks | Format 0, Ruff 0, pytest 0: 55 passed, one SDK warning, 2.84s. Collection 0: 224 cases; every prior 221 identity retained |
| Whitespace/documentation wrappers | git diff --check initially exited 1 for current report CRLF lines; current report alone was rewritten LF. A docs wrapper also exited 1 using uv child cwd as repo root; corrected ROOT-based wrapper exited 0. Historical docs/evidence were not normalized |
| Offline configuration CLI | Exit 0: configured true, status unknown, zero external requests; not readiness/generation proof |
| Actual current-source metadata CLI | Exit 0: one GET, ready_for_attempt, HTTP 200, 619.754ms; strict current-A linkage passed; zero generation |
| Current-source false-success experiment | Actual exit 1; wrong assertion detected. Kept separate from mandatory suite |
| Receipt-only stage summary | Actual exit 2: A PASS; historical B FAIL/no current passing receipt; Stage 03 PARTIAL |
| Final preservation/documentation check | Exit 0: current A and readiness artifacts validated after docs, unchanged source/HEAD/index/history, git diff --check 0. [Post-documentation check](evidence/stage032-post-doc-check.json) |
| New paid generation/Gate B | NOT RUN; zero generation requests; fresh owner authorization required |

[First focused failure](evidence/stage032-targeted-first/), [environment recovery](evidence/stage032-environment-recovery.json), [Ruff failures](evidence/stage032-targeted-second/), [96-case focused run](evidence/stage032-targeted-third/), [encoding wrapper](evidence/stage032-frontend-checks/), [focused browsers](evidence/stage032-focused-browser/), [first failed A](evidence/stage031/20261020T081357Z-A-39eae2fe/receipt.json), [second failed A](evidence/stage031/20261020T082305Z-A-1ab7fc65/receipt.json), [JUnit red](evidence/stage032-junit-red/), [JUnit green](evidence/stage032-junit-green/), [offline CLI](evidence/stage032-offline-config/), [stage summary](evidence/stage032-summary-console.txt).

## E. Source fingerprint, receipts and preservation

Current Gate A, readiness preparation and stage summary all use:

```text
2a2128d0f21c914b4640db6eb7c31ddf446ad00076a9a28e52d03bfcbe44b098
```

123 relevant source files: **110 unchanged, 9 intentionally modified, 4 added, 0 removed** relative to intake. HEAD remains e3fccd63e88162065189b00be1696617f616eea3; no staging, commit, reset or discard was performed. Root .env and API dotenv presence/content remain unchanged. [Final audit](evidence/stage032-final-audit.json), [intake manifest](evidence/stage032-intake.json).

The intake fingerprint **19097cc5cb84c430e53bf68dee65299e8a6dbb0a4b5b6a5cb4996ac9849efed9** and its earlier passing A remain history. Of 369 pre-existing evidence files, **368 remain byte-identical**; only the explicitly mutable latest-A.json pointer advanced. Every historical receipt and latest-B.json remain unchanged. Current documentation is excluded by the documented relevant-source fingerprint policy; runtime credentials are excluded and never individually fingerprinted in receipts. The nonsecret execution profile is recorded in the readiness artifact and will be recorded in B.

The literal credential scan found zero occurrences in 655 Git-visible files (including evidence) and 24 built frontend assets at audit time. It recorded no credential value/hash. This is a bounded literal scan, not a comprehensive secret/security certification.

### Verification matrix

| Requirement | Result | Evidence/boundary |
|---|---|---|
| Exact model metadata/account access and installed SDK | PASS | Actual one-GET CLI plus recorded catalog; not generation proof |
| Structured-output compatibility review | PASS | Official documentation and deterministic SDK serialization; actual server grammar remains live scope |
| Honest timeout diagnosis, classification and bounded execution | PASS | Historical upstream 503/504; current deterministic tests; no deadline inflation |
| Successful response validation and atomic persistence | PASS | Deterministic provider double with real API/PG; live current-source proof NOT RUN |
| Timeout/503/429/malformed output; approval preservation | PASS | Real SDK synthetic HTTP, real PG and controlled browser cases |
| Exact-key concurrency/idempotency/rollback visibility | PASS | Actual concurrent HTTP clients, one double dispatch, independent SQL sessions |
| Input recovery, explicit retry, duplicate-click protection | PASS | Real browser/API/PG on all three viewports; test-only pre-dispatch guard |
| Authentication, roles, tenant/legacy isolation, password policy | PASS | Existing identities retained and full regression suite executed |
| Migrations/drift, frozen locks, Ruff, TS, ESLint, build | PASS | Actual native exit 0 for every applicable command |
| Gate A rejects a required failing check | PASS | First actual browser failure and second evidence failure both returned native 1; separate unit failure schedules retained |
| Gate B rejects failures/controlled/stale/incomplete evidence | PASS | Deterministic verifier tests; this does not count as live B |
| Deliberately wrong-success assertion | PASS (detection) | Experiment itself actually exited 1; never counted as a passing production test |
| Fresh real generation/edit/approval/isolation flow | NOT RUN | Paid authorization is pending; older successes do not certify changed source |
| Matching current-source Gate A + real Gate B | BLOCKED | A passed; no current-source B execution authorized |
| Historical receipts, credentials and uncommitted work | PASS | Hash audit, unchanged HEAD/index, no discard/commit |

## F. Gate B readiness and execution plan

**Readiness preparation is complete; Gate B itself has not executed.** The preparation artifact is deliberately not a B receipt and does not advance latest-B. Gate C still reports PARTIAL/native 2. [Readiness-only preparation](evidence/stage032-readiness-preparation-20261020T084607Z/preparation.json), [summary native exit](evidence/stage032-summary-native-exit.json).

The exact paid command for the owner's next explicit authorization is:

```powershell
pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid
```

It requires current passing A/configuration/free local test ports, then records one fresh read-only models.get command and at most **ONE actual generation request** in a single browser test (one worker, retries 0). SDK attempts are 1 and HTTP transport retries 0. The synchronous browser allowance blocks a second POST before forwarding; any attempted excess fails verification. No separate paid API probe, continuation or fallback exists.

The small daily-habit brief requests **1 epic, 1 story, at most 2 criteria**, LOW thinking, and at most **6,000 output/thinking tokens**. The same actual plan is reused for provider metadata/usage, strict schema validation, API graph retrieval, independent draft SQL graph/hash audit, browser rendering, human criterion edit/reload, explicit exact-version approval/reload, independent approval SQL audit, and unrelated-user 404/no-content checks. Actual missing provider metadata stays null; no dollar cost or response ID is invented.

[Google's current standard pricing](https://ai.google.dev/gemini-api/docs/pricing) through December 31, 2026 is **US$0.75/1M input** and **US$3.75/1M output including thinking**. At that tariff, a fully used 6,000-token combined output cap corresponds to **US$0.0225 output charge, plus actual input**. This is a conditional tariff calculation, not an invoice or total-charge guarantee. Input includes the prompt/schema; actual token usage, account tier, taxes and remaining quota are unknown. No countTokens request was made. [Thinking-token cap documentation](https://ai.google.dev/gemini-api/docs/generate-content/thinking).

## G. Negative-path and false-success evidence

- **Provider unavailable:** deterministic real-SDK synthetic HTTP 503 produces public 502/provider_unavailable, a failed run, zero new plans and unchanged prior approved graph/hash/revision/actor/time. Exact replay does not redispatch; a later unrelated success leaves the failed run failed. The historical real upstream 503 remains separate evidence, not relabeled as a controlled test or retried.
- **Malformed model output:** labeled test-only output fails Pydantic validation, creates no valid plan, cannot become approved and preserves the original brief/approved plan. No canned replacement is used as live content.
- **Concurrency/atomicity:** two real authorized HTTP clients with the same key observe one run and one double dispatch. A fresh SQL session cannot see the actually flushed uncommitted plan/children; injected transaction failure rolls everything back. Unknown outcome remains honest until deadline reconciliation marks interrupted.
- **Browser recovery:** all three viewports verify truthful failure, brief/instructions and approval preservation, no repeated-click dispatch, GET-only unknown recovery and explicit new-attempt retry. The shared allowance test forwards one request and blocks the simultaneous second before dispatch. These are controlled-provider tests, never paid model evidence.
- **False-success experiment:** uv run --directory apps/api python -m scripts.verify_false_success actually returned **1** on this current fingerprint. The deliberately wrong assertion failed with **assert 'failed' == 'succeeded'**. Detection was true. [Experiment receipt](evidence/stage031/20261020T084627Z-wrong-success-d8c51f67/experiment.json), [actual failing assertion](evidence/stage031/20261020T084627Z-wrong-success-d8c51f67/wrong-success.log), [native exit](evidence/stage032-false-success-final-native-exit.json). It is outside normal discovery and is not a green stub, xfail, skipped test or mandatory-suite failure.

## H. Known blockers and limits

A fresh paid model-backed browser Gate B remains unexecuted. Metadata and controlled tests cannot establish generation availability or close Stage 03. Historical real successes prove earlier source actually generated/persisted/editable/approved plans; they cannot certify changed readiness/verifier/test implementation or replace a matching current-source B. The last actual live attempt still failed upstream 503; the earlier Full 504 remains a failed historical command.

Readiness reviews structured compatibility only for the selected 3.8 model; other catalog models remain unknown until explicitly reviewed. The test-only allowance is not a distributed production/provider quota. A disconnected browser may leave bounded server work running; there is no automatic resume/takeover/retry. The observed environment is Windows/Chromium with mobile/tablet emulation, not native-device or all-browser certification. Existing local-development security limitations remain; no production security certification, Stage 04, extra agent, provider routing, recovery/MFA or email-delivery feature was introduced.

## I. Exact reproduction commands

From E:\BrosKi\OBRA, with the checkout's development Next server stopped and no concurrent backend/E2E test:

```powershell
# If Docker Desktop is stopped:
docker desktop start --timeout 60
# Starts only guarded test PostgreSQL and runs all 14 deterministic checks:
pwsh -NoProfile -File scripts/verify.ps1
# Offline configuration (zero external requests):
uv run --directory apps/api python -m scripts.check_pm_config
# Explicit read-only metadata (one GET, never generation):
uv run --directory apps/api python -m scripts.check_pm_config --check-model
# Isolated deliberately incorrect assertion: MUST actually exit 1:
uv run --directory apps/api python -m scripts.verify_false_success
# Network-free evidence summary: currently exits 2/PARTIAL:
uv run --directory apps/api python -m scripts.verification summary
```

The live command in section F must not be executed without the next explicit owner authorization. Preserve the ignored .env. Set a real GEMINI_API_KEY or ORBA_PM_API_KEY and explicit ORBA_PM_MODEL server-side; API dotenv overrides root dotenv and process environment has precedence. No credential is printed, committed or placed in browser code. Default offline CLI exits configured 0/missing 1/invalid settings 2; explicit metadata exits ready_for_attempt 0/every non-ready state 2. In custom Windows Python output wrappers set PYTHONIOENCODING=utf-8 in the parent process. uv --directory apps/api changes child cwd; use scripts.verification.ROOT for repo artifacts. Full native argv and timings are in section D and the immutable receipt.

## J. Stage 03 verdict

**PARTIAL.** Current-source Gate A passed; the exact selected model's read-only readiness passed; the real current-source Gate B has NOT RUN and awaits fresh paid authorization. Gate C actually exited 2/PARTIAL. No old failed result was rewritten and no new paid model-generation request was made. Stop after Stage 03; do not begin Stage 04.
