# ORBA Stage03 verification record

Date: 2026-10-19. Scope: one Product Manager planning agent. Stage04 is excluded. Historical evidence remains in VERIFICATION_STAGE01.md and VERIFICATION_STAGE02.md. Source is uncommitted Stage03 work above `e3fccd6 chore: checkpoint Stage 02 baseline`; no deployment or push.

**Stage verdict: PARTIAL.** Genuine gemini-3.8-flash API generation and a complete live browser generation/edit/reload/approval/isolation flow have passed. The latest mandatory Full workflow nevertheless exited1: its live API request received an actual upstream504 DEADLINE_EXCEEDED, persisted a failed run and no plan, and stopped before its browser command. The subsequent standalone live browser command passed; this does not turn the failed Full run green. All14 preceding component commands passed, including102 backend tests,51 regression browser tests and1 real provider-failure browser test. Six owner-credential generation attempts were made in this continuation; no more calls were made after that cap. Credentials were preserved, never printed or copied into source.

## A. Implementation summary

Implemented one official Google GenAI adapter, versioned PM prompt, strict Pydantic document, additive relational migration, persisted execution lifecycle and private PM APIs. Project detail includes brief generation, overview/epics/stories/criteria, provenance, uncertainty, revision-controlled draft editing, explicit Owner/Admin approval, immutable approved history, human draft copies and read-only recovery. Existing authentication, permissions, themes and Chat project creation remain.

There is no canned fallback or simulated agent progress. A real response must pass schema/graph/source validation and commit the complete plan and succeeded status atomically. Failure/timeout/invalid output/interrupted leases cannot produce fake success. Architect/coding/QA agents, orchestration, tools, GitHub, Skills and Model Hub are excluded.

## B. Important files

| Files | Responsibility |
|---|---|
| API pm_schemas.py; prompts/product_manager_v1.txt | Authoritative document/edit contract, graph/source/blocker rules, pm-v1 prompt |
| API pm_models.py; migrations/versions/ab3987da8961_product_manager_plans.py | Five PM tables, ownership/version/idempotency constraints; actual parent0febbe526f54 |
| API pm_provider.py | Official SDK, bounded request/response, single attempt, no continuation/functions, actual metadata and safe errors |
| API pm_service.py; pm_repository.py | Short transactions, released auth connection, admission, original-session/deadline fencing, atomic graph and terminal reconciliation |
| API pm.py; pm_errors.py; pm_middleware.py; main.py | Private routes, revisions/approval/copy, streamed body guard, errors, lease sweep/readiness |
| Web components/product-plan.tsx; plan-editor.tsx; lib/pm.ts | Native reader/editor, genuine request/status/history/evidence, exact approval, preserved conflicting drafts |
| Web lib/api.ts; app/api/v1/[...path]/route.ts; components/session.tsx | PUT, scoped long timeout, caller abort signals, safe errors, stale-auth-response guard |
| API tests/test_pm_*.py; web/tests*, playwright.*.config.ts | Explicit unit/human-fixture/live boundaries, actual PostgreSQL/browser verification |
| API scripts/test_database.py, prepare_tests.py, seed_pm_fixture.py, inspect_pm_run.py, verify_pm_live.py | Strict test guard, cleanup, explicitly human fixtures, independent SQL and real-model evidence |
| scripts/verify.ps1; env examples; README/AGENTS/architecture/roadmap | Full/Core reproduction and preserved security rules |

API basenames resolve under `apps/api/orba`, Web under `apps/web/src`, unless a full path is shown.

## C. Commands and actual exits

Every pnpm command below ran through `npm exec --yes --package=pnpm@12.14.0 -- pnpm` because no global pnpm is installed. Transcripts retain native output/exit codes.

| Command | Actual result |
|---|---|
| git commit -m "chore: checkpoint Stage 02 baseline" | 0; e3fccd6,94 files; explicitly authorized |
| Original pwsh -File scripts/verify.ps1 on unchanged Stage02 | 0;44 backend/42 browser; stage03-baseline.txt |
| docker compose -f infra/compose.yaml --profile test up -d --wait | Initially1 (Docker engine pipe unavailable);0 after starting actual per-user Docker Desktop; both DBs healthy |
| uv add --directory apps/api google-genai; uv add --directory apps/api 'httpx>=0.28,<1' | Each0; official SDK2.31.0 and bounded HTTPX adapter locked |
| uv sync --locked --directory apps/api | 0 |
| pnpm install --frozen-lockfile; pnpm peers check | Each0; no peer issues |
| uv run --directory apps/api alembic upgrade head; alembic check | Each0; no schema drift |
| uv run --directory apps/api pytest -q | Expanded44/82/86/93/94/96/97/101 runs0; latest102 passed in84.45s,0 |
| uv run --directory apps/api ruff check .; ruff format --check . | Each0; earlier import/style findings fixed, no rules disabled |
| pnpm typecheck; pnpm lint; pnpm build | Each0 in Full; strict types, zero lint warnings, actual production build |
| Initial pnpm test:e2e | 1;49 passed/2 failed at implicit textarea labels; fixed with explicit label/control associations |
| pwsh -File scripts/verify.ps1 | 1;94 backend/51 browser/1 real provider-failure browser passed; live API then BLOCKED for missing ORBA_PM_MODEL |
| First pwsh -File scripts/verify.ps1 -Scope Core | 1;96 backend passed,50 browser passed/1 failed: test reloaded before confirmed save; failure preserved and wait strengthened |
| Latest pwsh -File scripts/verify.ps1 -Scope Core | 0;97 backend in43.59s,51 browser in2.8m,1 real provider-failure browser in17.6s; all14 component commands0 |
| pnpm test:e2e:live | 1; configuration preflight BLOCKED on ORBA_PM_MODEL; browser/model test not run |
| uv run --directory apps/api python -m scripts.verify_pm_live | 1; explicit BLOCKED JSON identifies ORBA_PM_MODEL; no mock substitute |
| Model configuration preflight and authenticated metadata GET | 0; owner-selected gemini-3.8-flash, metadata HTTP200; key preserved; configuration/catalog are not generation evidence |
| First Full with selected model | 1;97 backend/51 browser/1 negative browser passed; actual provider400 INVALID_ARGUMENT became502, failed run eaa1eccc-a4c2-4419-8622-bd384b54397b, zero plans |
| New real-SDK isolated unit tests | Initial collection2 (incorrect fixture import); then1 (assumed camelCase thinking field); corrected actual SDK wire handling:4 passed in0.20s,0. No assertion/validation removed. |
| Full after provider compatibility fix | 1;101 backend/51 browser/1 negative browser and genuine live API passed; live browser timed out at exact getByLabel for its generated blocking confirmation |
| pnpm --filter @orba/web exec playwright test tests/pm.spec.ts --grep=human-authored | 0;3 passed in1.3m; strengthened real-service fixture flow now resolves a blocking confirmation and verifies actual actor/time |
| Subsequent Full with corrected confirmation selector | 1;101 backend in105.45s,51 browser in6.7m and1 negative browser in26.6s passed; live API then received actual provider504 DEADLINE_EXCEEDED, stored failed/no plan. The old mapper exposed generic502; corrected to provider_timeout/504. |
| uv run --directory apps/api pytest -q tests/test_pm_provider_unit.py after timeout fix | 0;5 passed in0.62s; actual installed SDK with explicitly synthetic HTTP proves one attempt and correct safe504 mapping, not live service availability |
| Latest pwsh -File scripts/verify.ps1 | 1; first14 commands0:102 backend in84.45s,51 browser in5.1m,1 provider-failure browser in24.6s plus installs/migration/static checks. Command15 live API failed on actual provider504; command16 live browser NOT RUN by Full. |
| Subsequent pnpm test:e2e:live | 0;1 actual model-backed browser flow passed in1.4m; no response stubs/intercepts, real API/PostgreSQL; stage03-final-live-browser-console.txt |
| Independent live-browser SQL audit before test cleanup | 0; succeeded run, approved version1/revision2,1 epic/1 story/2 criteria, relationships/hash/human edit/approval verified in a fresh PostgreSQL session |
| Final pnpm typecheck; pnpm lint; pnpm build | Each0 after final live-test brief/instruction changes; stage03-final-static-checks.txt |
| uv run --directory apps/api pytest -q tests/experiments/pm_failed_run_success_experiment.py | Latest1 expected;1 failed in0.63s, actual assert 'failed' == 'succeeded'; outside normal discovery; no provider call |
| git diff --check during work | 1 for new CRLF package whitespace and test-overwritten historical evidence; package normalized, history archived/restored after tests |
| Final git diff --check | 0; historical Stage02 evidence restored after archiving Stage03 results |
| Development service restart and final HTTP/browser smoke | Direct Uvicorn/pnpm development sessions started; HTTP/DB and browser smoke each0: live200/ready200/web200/unauthenticated me401, sign-in gate/no overflow, original dev counts unchanged. Detached launcher was rejected before execution with "blocked by policy", no native exit; tool-managed foreground sessions worked. Initial historical HOME-variable smoke error remains archived and is not passing evidence. |
| Final credential literal scans and history restoration | Each0;81 compiled JavaScript files and199 tracked/non-ignored repository files scanned, runtime credential not found; root .env ignored/untracked, historical authorization bytes restored and Stage02 archive blob matched. Bounded literal scans, not certification. |

Evidence: [parsed actual command exits](evidence/stage03-execution-summary.json), [Full transcript](evidence/stage03-full-verification.txt), [final static checks](evidence/stage03-final-static-checks.txt), [Core transcript](evidence/stage03-core-verification.txt), [first Core failure](evidence/stage03-core-first-failure.txt), [reload failure](evidence/stage03-mobile-reload-failure.md), [wrong assertion](evidence/stage03-expected-failure.txt), [repository credential scan](evidence/stage03-repository-secret-scan.json). Original label failures are preserved in stage03-first-browser-*.md. No failure was relabeled as a passing production check.

## D. Verification matrix

| Requirement | Status | Boundary |
|---|---|---|
| Frontend/API start, PostgreSQL, migration/drift | PASS | Actual Next/Uvicorn/PostgreSQL, Alembic0 |
| Stage01/02 project/auth/workspace/role/tenant behavior | PASS | All44 old backend and42 old browser scenarios retained |
| Existing IDs/data survive migration | PASS | Seeded Stage01 and populated Stage02 schema upgrades; exact original fields/timestamps and repeated head |
| Strict schema/source/graph validation | PASS | Actual Pydantic rejects wrong types, keys, references/cycles, source/human-authority spoof |
| Graph persistence/edit/approval/history | PASS | Real DB/fresh sessions; genuine API draft and complete live browser edit/approval/reload, exact hash/actor/time verified |
| Viewer write denial, Member approval denial | PASS | Actual server role checks |
| Cross-workspace plan/run/diagnostic privacy | PASS | Real authenticated404 and unchanged DB records |
| Idempotency/admission/session/deadline/commit handling | PASS in controlled tests | Labeled lifecycle doubles + real DB; not live provider proof |
| Concurrent edits/approvals/coherent graph reads | PASS | Forced real PostgreSQL schedules; no response stubs |
| Stale lease GET/startup sweep | PASS | Actual admission, SQL, GET and fresh lifespan sweep; no resume |
| Provider failure never creates fake success | PASS | Real SDK/provider rejection, failed DB run/no plan, unchanged approval, useful UI |
| Malformed output rejection | PASS | Explicit isolated double -> actual Pydantic rejection -> failed run/zero plans |
| Wrong success assertion fails | PASS | Detection: experiment exit1; not a passing production test |
| Responsive/theme/editor browser flow | PASS | Desktop/mobile/tablet Chromium, human fixtures |
| Frozen installs, peers, Ruff, types, ESLint, build | PASS | Actual component exits0 |
| Genuine successful runtime generation/draft | PASS | Actual gemini-3.8-flash201, strict validation, API retrieval and fresh PostgreSQL session |
| Positive live model-backed browser flow | PASS | Standalone actual model/UI/API/DB flow0; edit/reload/approval/reload/private404; earlier selector failure remains recorded |
| Full integrated workflow green | FAIL | Latest Full exit1 at real provider504 during live API; browser command not reached in that invocation |
| Provider availability for a repeatable all-green Full | BLOCKED | Intermittent upstream DEADLINE_EXCEEDED at60s and90s; no invented quota explanation or unbounded retries |

## E. Test evidence and boundaries

Unchanged Stage02:44 backend in25.79s and42 browser in1.8m,0. Earlier Core:97 backend in43.59s,51 browser in2.8m and1 real provider-failure browser in17.6s; exit0, all14 commands0. Latest Full's regression portion:102 backend in84.45s,51 browser in5.1m (17 flows per viewport) and1 real provider-failure browser in24.6s; each exit0. Its live API then failed with provider504/exit1. Separately the complete genuine model-backed browser flow passed:1 in1.4m, exit0. These are separate executions, not a fabricated green Full result.

Integration uses real PostgreSQL/handlers/sessions, no SQLite or fake authentication. Core PM browser plans are explicitly **human-authored**, seeded only in the guarded test DB with generating_run_id=null. They prove editor/approval/history behavior, not generation. Narrow schema/lifecycle/error units use named counted provider doubles and actual DB writes. Five installed-SDK units use synthetic HTTP MockTransport and are explicitly not live-provider evidence. Unit-only model/response labels never count as real-model evidence; no runtime switch enables them. Executed mandatory suites contain no skips/xfail/dummy drivers. The positive live API has both a preserved passing execution and subsequent genuine failures; the final standalone live browser passed.

Auth traces are off to keep passwords/cookies out of artifacts. Safe actual human-fixture screenshots are `docs/evidence/stage03-*-human-plan.png`, distinct from explicitly labeled review design sketches. Actual mobile dark UI was inspected; covered flows assert no horizontal overflow. This does not certify native devices, other browsers or full WCAG conformance.

Final collection/execution confirms102 tests:25 auth/workspace,15 retained project/health,5 legacy/migration,17 PM contract,19 isolated PM lifecycle/error,9 PM persistence/authorization,3 PM concurrency,4 body/transport boundary and5 real-SDK/synthetic-HTTP unit cases. The original44 remain; one populated Stage02 migration case and57 PM cases were added. The latest Full transcript records all102 passing execution. Expected-failure experiments are outside this count and normal discovery.

Development services are running at http://localhost:3000 and http://127.0.0.1:8000. [Actual HTTP/DB smoke](evidence/stage03-dev-smoke.json), [actual browser smoke](evidence/stage03-dev-browser-smoke.json), [local process references](evidence/stage03-local-processes.json), [literal secret scan](evidence/stage03-client-secret-scan.json). Development data still has0 users/0 projects/1 restricted legacy workspace/0 PM runs/0 plans, matching intake; tests never seeded/reset development data. The archived Stage02 verification file's Git blob matches checkpoint e3fccd6 exactly (dde460d8cc315bac70b16a099045454255e1d84d).

## F. Real model evidence

Adapter: **google-gemini**, official locked **google-genai2.31.0**, owner-selected **gemini-3.8-flash**, LOW thinking,6000 output tokens,one concurrent request,three attempts/user/hour,six globally/hour. Actual project/tier RPM/TPM/RPD remain unknown. No automatic retries/continuation. [Runtime bounds](evidence/stage03-runtime-limits.json), [official model](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [provider quotas](https://ai.google.dev/gemini-api/docs/rate-limits).

First genuine API PASS: run8432a0c6-c251-4e31-83e2-1cc4d603ba04, plan48c9104c-e53b-4a6b-8f6e-b35851c0f13a, response rrnVatSjNcnMjuMP86CS2AI, HTTP201. Actual returned model gemini-3.8-flash;736 input/2648 candidate/3384 total tokens. One epic,three stories,five criteria; draft,unapproved; strict validation plus API and independent SQL retrieval. [Preserved evidence](evidence/stage03-first-live-api-success.json).

Final complete browser PASS: run f2ecf88d-6d7c-4d22-bd0e-902e2778e9ae, plan a8772c8e-563a-4754-b587-61c4e0b2f461, response Tu_VavCWHpmLjuMP-6CPoQk, returned model gemini-3.8-flash;753 input/2326 candidate/3079 total tokens. Initial generated state was a draft, never auto-approved. The user then edited a criterion, deferred one blocking confirmation with an explicit reason, saved/reloaded and explicitly approved/reloaded version1/revision2. Approval actor6493df36-f4fa-4105-bc4b-68021af483e7 at2026-10-19T10:23:02.593628Z matches the fresh DB read. One epic/one story/two criteria, correct FKs and content hash89423948d7aa24f711a632f328a83effa68eea19d5be55dfc40a8a50580675c7; edited criterion has server-owned human provenance. An unrelated authenticated user received404 and no content in API/UI. [Browser evidence](evidence/stage03-live-browser.json), [independent SQL audit](evidence/stage03-live-browser-db.json), [actual output](evidence/stage03-final-live-browser-console.txt).

Limited review of this public test sample found a concrete epic goal, consistent "As a ... I want ... so that ..." story, observable reload criterion, a retained literal brief quote and an explicit unresolved decision requiring human disposition. The audited sample clearly distinguishes the human-edited criterion from the untouched model-authored criterion. This is not a benchmark, factual/business certification or evidence that every future plan is semantically sound.

Six owner-credential generation attempts were made, sequentially, without SDK retries or continuation:

| Attempt | Actual outcome | Evidence |
|---|---|---|
| 1 | Provider400 INVALID_ARGUMENT, ORBA502, failed run eaa1eccc-a4c2-4419-8622-bd384b54397b, zero plans | stage03-first-configured-live-api.json / stage03-first-configured-live-db.json |
| 2 | Genuine API201, validated persisted draft,3384 returned total tokens | stage03-first-live-api-success.json |
| 3 | Genuine succeeded browser generation,3934 returned total tokens; full UI test failed at exact implicit-label selector before save/approval | stage03-first-live-browser-draft.json / stage03-live-confirmation-label-failure.md |
| 4 | Provider504 DEADLINE_EXCEEDED at the60s setting; old generic ORBA502 mapper, failed run ad50a952-4c4c-4378-b66b-ee8f63311f0d, zero plans | stage03-provider-timeout-live-db.json |
| 5 | Provider504 DEADLINE_EXCEEDED at90s, correct ORBA504/provider_timeout, failed run979a3a0c-b657-49af-b219-2dab98b79f34, zero plans; Full exit1 | stage03-final-live-api-failure-db.json / stage03-full-verification.txt |
| 6 | Complete live browser PASS,3079 returned total tokens; human edit and approval persisted | stage03-live-browser.json / stage03-live-browser-db.json |

For the final browser call the public brief was deliberately narrowed to one user's daily habit completion and reload persistence, requesting exactly one epic/one story/at most two criteria. The separate API example retains daily check-ins, streak and weekly summary with at most three stories/six criteria. Generation, persistence, edit, reload, approval and isolation assertions were retained; no generated wording is hardcoded. This controls verification size, not provider availability. Test DB resets also reset its admission counters; the six-attempt continuation cap is tracked across those resets in this ledger. Invalid-key negative tests do not use the owner's credential. No live429 was observed, and provider project/tier quotas remain unknown.

The first browser generation's selector failure is preserved, not relabeled as a pass. Provider request IDs were not returned; null is accurate. Usage was not returned for failed calls and their cost/usage is unknown. Dollar costs are not estimated.

## G. Negative paths

**A: Actual provider failure.** Separate negative browser configuration uses an intentionally invalid test key, never changes the owner's key, and calls the real official SDK. Provider HTTP400 / INVALID_ARGUMENT / API_KEY_INVALID becomes safe ORBA HTTP502 / provider_access_denied. The run is failed with diagnostic UUID and no plan. The previous human-authored approved plan keeps its exact hash/approval timestamp. UI displays the error, GET recovery confirms no draft, and a fresh SQLAlchemy session verifies DB state. [Latest evidence](evidence/stage03-provider-failure.json), [Full-run evidence](evidence/stage03-full-provider-failure.json).

**B: Invalid output.** A clearly labeled isolated unit double returns `{"not_a_plan":true}`. Actual Pydantic reports missing fields/forbidden extra; run failed, invalid_model_response, diagnostic UUID, zero persisted plans. [Actual isolated-unit evidence](evidence/stage03-invalid-output.json). Not live model evidence.

**Additional actual provider timeouts.** At60s, run ad50a952-4c4c-4378-b66b-ee8f63311f0d failed with actual provider504 / DEADLINE_EXCEEDED / SDK ServerError and no plans; its old generic ORBA502 mapping was fixed and tested. At90s, the latest Full's run979a3a0c-b657-49af-b219-2dab98b79f34 likewise failed, now correctly returning ORBA504/provider_timeout. Diagnostic de784cb8-5225-4beb-8032-c14124905520 and an independent SQL read confirm failed/no plan. No returned model/response/usage is fabricated. [Latest HTTP failure](evidence/stage03-final-live-api-failure.json), [latest DB state](evidence/stage03-final-live-api-failure-db.json), [Full transcript](evidence/stage03-full-verification.txt), [earlier timeout](evidence/stage03-provider-timeout-live-db.json). A later small browser call passed; that does not erase either failure or establish reliable provider availability. No more calls were made after attempt6.

**Wrong expectation.** Separate explicit-only experiment causes a real missing-configuration failure, observes HTTP503, reads the failed PostgreSQL run, and incorrectly asserts succeeded. Pytest really exits1 with `assert 'failed' == 'succeeded'`. The app was not modified to satisfy it. [Actual output](evidence/stage03-expected-failure.txt).

## H. Limitations

The mandatory integrated Full did not pass: real provider deadline failures occurred at60s and90s. Positive API and complete browser successes exist, but a repeatable all-green Full remains unverified. No missing credential is claimed and no unbounded provider probing was used. Earlier missing-model/provider400/selector errors remain historical evidence. The provider400 explanation was not retained beyond safe INVALID_ARGUMENT/status diagnostics, so its precise cause is not asserted. Five isolated installed-SDK/synthetic-HTTP units cover parsing/metadata/errors without claiming live availability; full Pydantic/graph validation remains mandatory.

Local development, not certified production security. No email verification/recovery/MFA/SSO, real-time permission push, full draft edit audit/diff, retention/deletion, semantic truth guarantee, distributed orchestration, failover, resume or billing/cancellation guarantee. Usage may occur before authority/lease failure prevents publication. Quotes prove textual traceability, not business facts. Exhaustive fault/throughput/native-browser certification is not claimed. Isolated test data is cleaned between suites and by the final wrong-expectation experiment; the actual successful live rows were audited before cleanup, with safe evidence preserved. Development data was never reset.

SDK emits a Python `_UnionGenericAlias` deprecation warning; Node/Playwright emit NO_COLOR/FORCE_COLOR warnings. They were preserved, not suppressed. Existing ESLint9/TypeScript6 compatibility pins remain; SDK compatibility selects websockets16.1.1.

## I. Reproduction

PowerShell at repository root. Never run backend/browser/fixture/live/experiment commands concurrently: they share guarded orba_test at127.0.0.1:54330. Preserve development volume and existing ignored .env. Stop an old API before ownership migration. Stop the development Next.js server on3000 before Playwright/Full/Core: the test frontend on3001 shares this checkout's .next/dev lock. Run verification before starting the development frontend again.

```powershell
docker compose -f infra/compose.yaml --profile test up -d --wait
uv sync --locked --directory apps/api
npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile
uv run --directory apps/api alembic upgrade head
uv run --directory apps/api alembic check
```

Two terminals:

```powershell
uv run --directory apps/api uvicorn orba.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
```

```powershell
npm exec --yes --package=pnpm@12.14.0 -- pnpm dev
```

Open http://localhost:3000, sign in/register, create/select workspace, create/open project. Configure GEMINI_API_KEY (or ORBA_PM_API_KEY) and explicit ORBA_PM_MODEL in ignored root .env; restart API. Bounds/defaults: root .env.example and README.

```powershell
# Configuration only, no generation:
uv run --directory apps/api python -m scripts.check_pm_config
pwsh -File scripts/verify.ps1 -Scope Core
# Real key + explicit supported model; two bounded paid-capable positive calls:
pwsh -File scripts/verify.ps1
# Separate intentionally wrong experiment, must exit1:
uv run --directory apps/api pytest -q tests/experiments/pm_failed_run_success_experiment.py
```

Individual positive gates, sequentially: `uv run --directory apps/api python -m scripts.verify_pm_live`, then `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:live`. They validate real structure, persistence and edits, never hardcoded expected generated wording. Missing configuration exits nonzero.

## J. Stage verdict

**PARTIAL**

Actual model API generation and the complete real-model browser journey passed, as did102 backend/51 core browser/1 real failure browser tests and required static checks. The latest mandatory Full workflow still exited1 on actual provider504 before reaching its browser command. No further calls were made after the six-attempt cap. Stage04 was not started.
