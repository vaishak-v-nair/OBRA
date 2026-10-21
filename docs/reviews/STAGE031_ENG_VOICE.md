# Stage03.1 independent engineering review

Review source: an independent in-host Codex-family engineering voice. This is not outside-model consensus. Reviewed the amended `docs/STAGE031_PLAN.md`, repository contracts, application code, installed SDK source and relevant tests/scripts; did not read other review artifacts or secrets. No tests, service requests, database queries, model calls, source edits or Git writes were performed. This document is static review evidence, not a VERIFIED implementation verdict.

Recommendation: proceed with the amended architecture, incorporating E1–E5 below as implementation acceptance details. Keep Gate B blocked until Gate A passes and the owner gives the later explicit authorization. The timeout split is justified by the installed SDK; it does not establish that upstream latency has improved.

## Six engineering dimensions

| Dimension | Assessment | Confidence and evidence |
|---|---|---|
| Architecture | Sound, bounded extension of the existing lifecycle. Keep one provider dependency and one shared verifier; do not fork generation, authorization or persistence for browser tests. | High: `pm.py:52–55,82–100`; `pm_service.py:327–349,431–499`; plan `:64–74`. |
| Code quality and complexity | The standard-library runner plus thin PowerShell wrappers is proportionate. One versioned receipt schema and command registry are enough; a general workflow engine, second evidence database or signed-attestation system is unnecessary. | High: current `scripts/verify.ps1:8–13,20–36` repeats imperative execution without a reusable evidence validator; plan `:68–74` addresses this directly. |
| Tests and evidence | Existing tests cover important real PostgreSQL and authority boundaries. Deterministic browser recovery and gate self-rejection need meaningful new coverage. Exit zero alone cannot prove complete mandatory coverage. | High: `test_pm_lifecycle_unit.py:153–198,222–238,281–298,323–371`; `tests/pm.spec.ts:20–102`; E3 below. Counts in the plan were not re-executed during this review. |
| Performance and deadlines | Preserve short SQL phases and no checked-out authentication transaction during model execution. The proposed T/T+5/T+10 envelopes fit the existing fences. Bound diagnostic size and runner execution; avoid another SQL transaction solely to write postcommit timing. | High for source behavior; no latency benchmark was performed: `pm_service.py:47–53,255–276,374–380,431–466`; `pm_repository.py:22–77,80–128`. |
| Security and isolation | Production must continue selecting only the official adapter; the test factory must guard the exact isolated DSN before creating its app. Effective credential scrubbing must also defeat dotenv fallback. | High: `config.py:17–20,34–40`; `scripts/test_database.py:6–18`; `security.py:68–99`; E1 below. |
| Failure handling and rollout | GET-only uncertain recovery, immutable receipts and separate historical outcomes are correct. Specify known pre-admission rejection, child-process cleanup and configuration provenance before calling the gates complete. | High for identified source branches; medium for proposed runner details because the runner has not been implemented: E2, E4, E5. |

## Required implementation refinements

### E1 — Gate A must override dotenv, not merely delete environment keys

Priority: P1. Confidence: high.

`Settings` reads both root and API dotenv files (`apps/api/orba/config.py:34–38`). Ordinary backend fixtures construct `Settings(database_url=TEST_DATABASE_URL)` (`apps/api/tests/conftest.py:24–29`), so removing inherited key/model variables would allow those files to configure the provider again. The core Playwright configuration already demonstrates the intended effective overrides: empty `ORBA_PM_API_KEY`, `GEMINI_API_KEY` and `ORBA_PM_MODEL` (`apps/web/playwright.config.ts:14`).

Make the shared runner pass those explicit empty values to every deterministic child, including migrations and nested `uv`/Playwright processes. Use `_env_file=None` in the guarded controlled-provider factory and explicit synthetic unit settings. Add a small unit regression with temporary synthetic dotenv values proving that the Gate A child profile is unconfigured, without reading or changing the owner's files. Test that no configuration check or missing-opt-in path reaches the provider dependency. Scrubbing is a configuration boundary, not proof of provider access or a general network sandbox.

### E2 — Removing Clear creates a dead end for requests rejected before a run exists

Priority: P1. Confidence: high.

The UI writes the UUID before invoking `pm.generate` (`apps/web/src/components/product-plan.tsx:83–85`), and the shared client fetches CSRF before sending the POST (`apps/web/src/lib/api.ts:19–25`). Origin/CSRF rejection occurs before generation (`apps/api/orba/security.py:78–99`); request validation can also reject before `create_run`. Admission 429 and context validation errors occur before `db.add(run)` (`apps/api/orba/pm_service.py:217–249`). These cases can leave no durable run to become terminal.

The amended GET-only rule is correct for an unknown outcome. Its implementation must separately represent an authoritative rejection before admission. A generic 503, failed fetch, missing GET row or elapsed browser timer must never be treated as such proof. Define an explicit API error classification for known pre-admission rejection, preserve the typed brief/instructions and require a new explicit user action for a new request. If that distinction is intentionally deferred, display the truthful blocked state and document its recovery limitation; do not claim complete retry recovery. Do not invent a failed provider run to satisfy the terminal-run UI condition.

For admitted runs, bind Retry to the exact account/project/request/run and a fresh GET of that run; a history page or another actor's active-run ID is insufficient. Fetch the existing authorized run-detail snapshot (`apps/api/orba/pm.py:161–174`) only when the user chooses restore. Keep the UUID until the saved result is actually read after both a synchronous 201 and a later GET recovery; the current code clears it before `load` in both paths (`product-plan.tsx:87–88,99–107`).

### E3 — Validate complete test results in addition to fixed commands and exits

Priority: P1. Confidence: high.

The current runner checks only native exit codes (`scripts/verify.ps1:8–13`). The plan adds exact command arrays and receipt integrity (`docs/STAGE031_PLAN.md:68–74`), which are necessary but do not by themselves reject skipped tests or environmental filtering. For example, inherited `PYTEST_ADDOPTS` can select a small subset while the fixed `pytest -q` command still exits zero. Pytest can also exit zero when selected cases are skipped. The repository contract explicitly disallows mandatory skips and xfail.

Have mandatory commands emit structured result artifacts, such as pytest JUnit and Playwright JSON. Validate executed test identities/projects, counts, zero failures/errors/skips/xfail, and zero retries for the applicable execution class. Clear inherited test-selection/report-routing variables in the runner. Keep the retained 102 backend/51 core browser baseline identities and append the new cases; avoid hardcoding only the old counts, which would reject legitimate additions. A missing, empty or truncated report is incomplete evidence even if stdout says PASS. Hash the result artifacts in the receipt and validate them from the shared registry rather than building a second list in Gate C.

### E4 — Source identity is not effective nonsecret configuration identity

Priority: P2. Confidence: high.

Excluding credentials and dotenv files from source hashing is correct. Those files also select the model, timeout, output limit and admission limits (`apps/api/orba/config.py:17–33,43–53`). Consequently, the same source hash can describe materially different provider execution. Record and validate a small safe execution profile: provider, requested model, prompt/schema/hash versions, server/transport/outer budgets, output cap, admission bounds, actual SDK version and test execution class. Do not record credential values or credential fingerprints. Compare the Gate B preflight profile with the actual persisted run and the Gate C selection; label any later configuration change as outside that evidence.

Define the source manifest file-set rule precisely: tracked files plus relevant nonignored untracked files, including newly added verifier/test code, root scripts/configuration and lockfiles. Hash relative paths and bytes so additions, deletion and renaming change identity. Include the manifest/receipt schema version. Start/end manifests detect ordinary in-run changes; they are not a hostile-machine attestation claim.

For the one real browser flow, require draft and approval audits to refer to the same attempt/project/run/plan and exact revisions. The current live browser checks API persistence but has no fresh SQL graph audit (`apps/web/tests-live/pm-live.spec.ts:22–42`), while the existing inspector reports stored root hashes without independently rebuilding the graph (`apps/api/scripts/inspect_pm_run.py:22–50`). Extend the real audit to reconstruct and recompute the graph hash, check linkage/counts and assert approval actor/time/version/revision. Use fresh sessions for each observation, before and after edit/approval. Do not label an API-returned hash or a merely nonempty stored hash independent SQL validation.

### E5 — Define bounded runner interruption and ownership cleanup

Priority: P2. Confidence: medium; the planned shared runner does not yet exist.

The planned local lock is explicitly advisory (`docs/STAGE031_PLAN.md:70`), which is an honest boundary. It should remain held until owned command descendants have exited, including Playwright's API/web processes. Otherwise a Ctrl-C or startup failure could release the lock while a child still occupies the test ports or isolated database. Specify command deadlines, terminal interrupted/failed receipts, and cleanup of only processes launched by that attempt. Never kill unrelated services or clear the development database. A launch failure must have an explicit nonzero result rather than a missing exit field mistaken for zero.

Start only `test-postgres` for the gate; the current Compose command selects the test profile without a service target (`scripts/verify.ps1:16`), and the default development `postgres` service also exists (`infra/compose.yaml:3–18`). Ordinary Gate A needs no development database startup. Distinguish no external AI dependency from fully offline operation: frozen installs and Docker image acquisition may still require ordinary package/image network access (`scripts/verify.ps1:16–18`). Avoid calling the whole gate network-free unless that stronger property is actually enforced and checked.

## Timeout and diagnostic acceptance details

The installed SDK preserves an explicitly supplied `X-Server-Timeout` and otherwise derives it from `HttpOptions.timeout` (`apps/api/.venv/Lib/site-packages/google/genai/_api_client.py:207–212,1541–1553`). It also passes that timeout as the per-request HTTPX timeout (`:1791–1796`). Therefore setting only the `AsyncClient` default to T+5 is insufficient. Set the explicit server header to T, SDK `HttpOptions.timeout` to `(T+5)*1000`, the HTTPX default to T+5 and the outer envelope to T+10. This is consistent with the amended plan, not a request to lengthen the server budget.

Extend the existing real-SDK synthetic HTTP tests (`apps/api/tests/test_pm_provider_unit.py:26–108`) to assert the outgoing header and actual request timeout extensions at both configured bounds, one request only, no redirects/retries, and safe distinctions among an HTTP 504, HTTPX timeout and outer-envelope cancellation. These are provider contract unit tests, never live evidence. Avoid long wall-clock sleeps to test the envelope.

Keep timings on an allowlist of finite, nonnegative monotonic durations and bounded stage/origin enums. Store timings known before the terminal transaction's commit in the existing diagnostic JSON; name them accordingly. Emit true postcommit confirmation in safe structured logs only after the context has completed. Do not pretend a precommit timestamp measures commit acknowledgement, and do not let failed diagnostic enrichment overwrite committed success. Existing acknowledgement-loss coverage (`test_pm_lifecycle_unit.py:323–346`) must continue to prove that status and the complete graph remain succeeded.

## Branch and regression coverage to add

| Boundary | Meaningful assertion |
|---|---|
| Unknown POST outcome | Disconnect after admission and before response; zero automatic POSTs on check/reload/navigation; retain exact UUID; late success opens the existing plan only. Include GET returns no row and failed GET. |
| Confirmed rejection without a run | CSRF/request validation/admission/context rejection exercises the chosen E2 policy; typed inputs survive; no fake terminal run and no implicit resubmission. |
| Terminal Retry | Fresh exact terminal confirmation permits exactly one explicit new UUID/call; double click, failed confirmation, wrong account/project and another active run do not unlock generation. |
| Successful run, failed result read | Both immediate 201 and recovered success retain the reference if plan/history GET fails; a later read restores the same saved result without a new generation. |
| Snapshot restoration | Explicit restore uses authorized run input; changing account/project or revoking membership denies the read and clears protected rendered state. Declining restore preserves local text. |
| Honest loaded/error states | Initial plan/run/configuration read failure shows unavailable state, not setup/empty success. Pending/unknown notices use neutral styling in both themes; successful GET clears stale errors. |
| Controlled-provider browser factory | Exact DSN guard fails closed; only the provider dependency is overridden; real route/auth/CSRF/workspace locks/SQL validation still run; production app selects only Gemini. Labeled controlled success/failure cannot satisfy B/C. |
| Timing and terminal fencing | Invalid output, HTTP429/504, local timeout, expired lease, changed original session and lost commit acknowledgement retain their true category and graph/status guarantees; safe diagnostics omit marker secrets/briefs. |
| Receipt and manifest rejection | Missing/duplicate command, unexpected execution class, nonzero/absent exit, skip/xfail, truncated report, source addition/deletion/change, changed artifact, stale A, absent B and partial interrupted attempt all fail closed. These tests execute validator code; native wrong-success experiments still assert against real guarded PostgreSQL and actually exit1. |
| Paid opt-in and process ownership | Missing opt-in/config/current A returns BLOCKED and zero provider dispatch; direct legacy entrypoints cannot bypass that policy. Interruption cleans owned children and preserves an incomplete/nonpassing receipt. |

Retain the complete baseline suites and meaningful negative assertions. Run backend, browser, experiments and future live checks sequentially because they share the guarded database. No additional paid probe is needed for any review recommendation above. Gate B remains later authorized work; until then record deterministic scope separately and retain the actual historical Full failure.
