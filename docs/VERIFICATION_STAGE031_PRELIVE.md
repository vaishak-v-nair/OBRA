# ORBA Stage03.1 verification record

Date: 2026-10-19. Scope: reliability and verification hardening of the existing single Product Manager agent. No Stage04, public deployment, commits or additional paid model requests. Uncommitted Stage03 work above `e3fccd63e88162065189b00be1696617f616eea3` is preserved. The prior report is preserved verbatim in [VERIFICATION_STAGE03.md](VERIFICATION_STAGE03.md), with an intake copy of historical artifacts in [stage031-intake.json](evidence/stage031-intake.json).

**Stage03 verdict: PARTIAL.** Final Gate A passed on the current source:139 backend tests,51 regression browser tests and18 controlled-provider browser tests, with all14 required commands exiting0 and no skips/retries. Gate B's actual opt-in refusal exited2 with zero commands dispatched; a fresh live request requires explicit owner authorization. Gate C exited2 and retained PARTIAL. Historical real model successes cannot certify changed source.

Current relevant-source fingerprint: `c5c705e057e346e2d1f9059110b2927f86d6493dc94a3332065e4aa5dc32a9e1` across116 source files. Gate A ran2026-10-19T16:46:15Z through16:52:50Z. Its [receipt](evidence/stage031/20261019T164615Z-A-d01ac6df/receipt.json) includes complete native argv, exits, durations, artifact hashes and structured results. The [stage summary](evidence/stage031-final-summary.txt) independently revalidated A after the separate experiments. No paid call was made in Stage03.1.

## A. Root-cause investigation

The failed historical Full command was15, `uv run --directory apps/api python -m scripts.verify_pm_live`, after14 prior commands exited0. It called FastAPI directly through TestClient, bypassing Next/browser. Its saved diagnostic records official SDK ServerError, HTTP504, DEADLINE_EXCEEDED and provider_response. That supports an upstream HTTP deadline response, rather than a local browser/proxy timeout. It does not establish an independent provider outage, quota cause or exact duration. The recorded90s setting is configuration, not measured latency.

Installed SDK2.31.0 also derives X-Server-Timeout from HttpOptions unless explicitly supplied and applies its value to HTTPX. Previously the server, transport and outer asyncio deadlines were equal. They are now T, T+5 and T+10 respectively, keeping the server budget unchanged. This separates deadline races; it does not prove upstream availability improved. Full source/evidence reasoning, run/diagnostic IDs and bounds are in [STAGE031_TIMEOUT.md](STAGE031_TIMEOUT.md).

## B. Code and verification changes

| Files | Responsibility |
|---|---|
| `apps/api/orba/pm_provider.py` | Explicit server/transport/envelope bounds, one attempt, upstream/local/transport error origins, provider-unavailable classification |
| `pm_timing.py`, `pm_service.py` | Safe monotonic phase timings, precommit measurement boundary, acknowledged commit logs, preserved terminal fencing and lease diagnostics |
| `pm.py`, test-only `tests/controlled_app.py` | Native model dependency; production only Gemini; isolated guarded controlled provider override without auth bypass |
| Web `product-plan.tsx`, `lib/pm.ts`, `lib/api.ts`, API proxy | Exact terminal retry confirmation, new UUID, unknown GET-only recovery, explicit snapshot restore, retained result references, honest loaded/error/neutral states and labels |
| `scripts/verify.ps1`, `scripts/verify-live.ps1` | Thin Gate A / explicitly opted-in Gate B entrypoints with actual native exit propagation |
| `apps/api/scripts/verification.py`, `owned_process.py`, `verification_baseline.json` | Fixed checks, guarded deterministic environment, complete result validation, source/profile/artifact identity, create-once receipts, advisory lock, bounded owned process trees, conservative Gate C |
| `inspect_pm_run.py`, live Playwright test | Fresh graph reconstruction/Pydantic/hash/FK/count checks before edit and after exact approval; failure proof written from finally |
| Backend tests and `tests-controlled/pm-recovery.spec.ts` | Real PostgreSQL lifecycle/security regressions, SDK synthetic-HTTP contracts, explicit controlled browser recovery and gate rejection tests |
| Evidence helpers and `verify_false_success.py` | Unique per-attempt artifacts; real-PG incorrect-success experiment stays outside normal discovery |

There is no new migration: timing diagnostics use the existing JSONB field. No automatic retry, fallback PRD, new agent, authentication system or orchestrator was added. Earlier approved artifacts remain immutable.

## C. Commands and actual exits

Every pnpm command uses `npm exec --yes --package=pnpm@12.14.0 -- pnpm` because no global pnpm is installed.

| Command / attempt | Actual outcome |
|---|---|
| Docker test/development startup during intake | 0; services healthy, development data not reset |
| Baseline `uv run --directory apps/api pytest -q` | 0;102 passed,1 third-party warning,89.78s |
| First baseline `pnpm test:e2e` | 1 before tests: existing development Next lock. Only verified repository-owned old API/web processes were stopped |
| Repeated baseline `pnpm test:e2e` | 0;51 passed in5.4m |
| Targeted backend verifier/SDK/lifecycle/reliability run | 0;59 passed,1 warning in22.07s; [output](evidence/stage031-targeted-backend.txt) |
| First controlled browser command | 1 before tests: test factory used the wrong import root; actual ModuleNotFoundError preserved in [output](evidence/stage031-controlled-first.txt) |
| Second controlled browser command | 1;7 passed/5 failed. It caught introduced Windows encoding and implicit prefilled-label defects; fixes landed during this diagnostic run, so it is not clean acceptance evidence. [Output](evidence/stage031-controlled-second.txt) |
| Third controlled browser command | 0;12 passed in2.2m after UTF-8 and explicit-label fixes; [output](evidence/stage031-controlled-third.txt) |
| Ruff during edits | Initial combined check/format shell returned0 from its final format command while the check printed B008; that invocation is not passing lint evidence. Subsequent separate check returned1 for SIM102; fixed without disabling rules. Final separate lint and format commands0 |
| Standalone TypeScript and ESLint | Each0; full Gate A repeats current-source checks |
| Owned native process smoke | 0; actual child process exit0 under Windows Job Object ownership |
| `git diff --check` | Initially nonzero for introduced CRLF/encoding changes; normalization preserved content, final0. Historical evidence bytes excluded from normalization |
| Final review shell | One wrapper exited1 because an unintended `afterDiffCheck=$null` token was executed after Git; PowerShell reported the term was not recognized. Corrected standalone `git diff --check` exited0. This wrapper failure was not a Gate A command or an application/test failure |
| First `pwsh -NoProfile -File scripts/verify.ps1` | 0;139 backend,51 core browser,12 controlled browser; all14 native commands0; receipt `20261019T121457Z-A-f9bdb939`. Correctly STALE after later source changes |
| Targeted competing-editor regression | Actual failure reproduced: native1,1 failed in8.3s; saved competing summary was overwritten. Fresh SQL observed revision3 and the old summary; [log](evidence/stage031-editor-reproduced-before-fix.log), [exit](evidence/stage031-editor-reproduced-before-fix-exit.json), [SQL](evidence/stage031-editor-reproduced-db.json) |
| Resumed-session prerequisites | Two earlier targeted attempts1 before tests: Docker Linux pipe absent, then fresh test DB lacked migrations. Docker Compose startup1 with actual missing pipe; `docker desktop start --timeout 45`0; test-only Compose startup0; guarded prepare/migration0. Dependency failures were not counted as executed regression cases |
| Targeted competing-editor regression after fix | 0;3 passed in28.3s, desktop/mobile/tablet. Save409, competing summary/revision preserved, local criterion retained |
| Gate C before/after source changes | Each2: first A PASS/B NOT RUN -> PARTIAL; after relevant source change A STALE/B NOT RUN -> PARTIAL; [stale refusal](evidence/stage031-source-drift-summary.txt) |
| Second `pwsh -NoProfile -File scripts/verify.ps1` | 0;139 backend/51 core/15 controlled; all14 native commands0; receipt `20261019T163456Z-A-a018d085`. Correctly historical after the later admission-recovery fix |
| Targeted active-admission recovery regression | Actual1 before fix: a rejected request UUID remained unconfirmed despite having no run. After fix0;3 passed in32.0s on desktop/mobile/tablet. The existing active run failed truthfully, the rejected new request created no row, input remained and no automatic POST occurred; [before](evidence/stage031-admission-reference-before-fix.log), [after](evidence/stage031-admission-reference-after-fix.log) with separate native-exit JSON files |
| Final `pwsh -NoProfile -File scripts/verify.ps1` | 0;139 backend in43.69s,51 core browser in2.9m,18 controlled browser in2.3m; all14 commands0, no skipped/retried tests; [receipt](evidence/stage031/20261019T164615Z-A-d01ac6df/receipt.json), [console](evidence/stage031-gate-a-acceptance-console.txt) |
| Historical evidence preservation audit | 0;64 archived files byte-for-byte unchanged; [audit](evidence/stage031-historical-preservation.json) |
| Bounded literal-credential scan | 0; current runtime key absent from402 Git-visible files and24 current client static assets; no key value/hash recorded. This is a scoped literal scan, not a universal secret audit; [result](evidence/stage031-literal-credential-scan.json) |
| `uv run --directory apps/api python -m scripts.verify_false_success` | Actual1 as required:1 deliberately failing assertion, persisted failed != succeeded; detection=true, no provider call; [experiment](evidence/stage031/20261019T165256Z-wrong-success-4a34c450/experiment.json), [actual failure](evidence/stage031/20261019T165256Z-wrong-success-4a34c450/wrong-success.log) |
| `pwsh -NoProfile -File scripts/verify-live.ps1` without opt-in | 2/BLOCKED, zero child commands and zero provider dispatch; [receipt](evidence/stage031/20261019T165305Z-B-88f5674d/receipt.json) |
| `uv run --directory apps/api python -m scripts.verification summary` | 2; A PASS, B BLOCKED, Stage03 PARTIAL for the current fingerprint; [output](evidence/stage031-final-summary.txt) |
| Post-documentation stage summary | 2; independently revalidated the same current source and A PASS/B BLOCKED/PARTIAL; [output](evidence/stage031-post-doc-summary.txt) |
| New paid Gemini calls | NOT RUN; zero in Stage03.1 |

Gate receipts are the authoritative automatically captured command argv/log/exit/duration records. Historical Stage03 failed commands and six paid generation attempts remain visible in the preserved report/archive.

## D. Gate A

The fixed registry runs test-postgres startup, locked uv/frozen pnpm installs, peers, test Alembic upgrade/check, all backend tests, Ruff/format, strict types, ESLint, production build, all51 existing browser regressions and18 controlled-provider browser cases. It binds migrations/tests to loopback54330/orba_test and empties both key aliases/model to defeat dotenv fallback. It rejects missing identities, failed/skipped/xfail/flaky/retried/incomplete reports, native failures and source/artifact changes. Frozen package/image acquisition can use ordinary network access; no paid or external model request is part of A.

The first complete Gate A passed139 backend/51 core/12 controlled browser tests and the second passed139/51/15, each with all14 native commands0 and complete no-skip reports. Subsequent real competing-editor and active-admission regressions each found a recovery defect; their fixes each passed all3 viewports. Final current-source Gate A passed139/51/18. Backend results contain one installed-SDK Python deprecation warning; browser results contain harmless Node color-environment warnings. Neither represents a skipped or failed test.

| Final Gate A command | Native exit | Captured duration |
|---|---|---|
| `docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres` | 0 | 0.757s |
| `uv sync --locked --directory apps/api` | 0 | 0.037s |
| `pnpm install --frozen-lockfile` | 0 | 1.216s |
| `pnpm peers check` | 0 | 1.079s |
| `uv run --directory apps/api alembic upgrade head` | 0 | 1.419s |
| `uv run --directory apps/api alembic check` | 0 | 1.458s |
| `uv run --directory apps/api pytest -q --junitxml=<attempt>/backend.xml` | 0 | 46.744s |
| `uv run --directory apps/api ruff check .` | 0 | 0.078s |
| `uv run --directory apps/api ruff format --check .` | 0 | 0.069s |
| `pnpm typecheck` | 0 | 3.857s |
| `pnpm lint` | 0 | 7.212s |
| `pnpm build` | 0 | 7.678s |
| `pnpm test:e2e` | 0 | 177.590s |
| `pnpm test:e2e:controlled` | 0 | 140.753s |

The pnpm wrapper and absolute JUnit destination are recorded without abbreviation in the receipt. Tests use real isolated PostgreSQL; synthetic HTTP/model behavior is explicitly labeled in deterministic SDK/lifecycle/browser cases. None is live Gemini evidence.

## E. Gate B

Prepared command: `pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid`. Do not execute until the owner explicitly authorizes the next attempt after passing A. It requires current A, actual runtime Gemini configuration and one explicit opt-in. It performs one real model-backed browser generation, authenticated API checks, independent draft SQL audit, edit/reload, exact approval/reload, independent approval SQL audit and unrelated-user404. Retries are zero. Provider/browser failure is nonzero; failure artifacts retain safe stage/run/category/SQL metadata. Missing opt-in/config/prerequisite is BLOCKED, never PASS.

No actual Gate B provider request has been executed on the changed code. The actual no-opt-in invocation produced BLOCKED/exit2, with an empty command list. Safe configuration inspection confirmed the selected model, official SDK2.31.0,90/95/100-second deadlines,6000 output tokens, concurrency1, account3/hour/global6/hour and a present credential; it made no request and does not prove the key is valid. New live availability, genuine output under the new deadlines and the full live browser path remain unverified. Controlled provider tests do not close this gate. The low-level API diagnostic and direct live config also require explicit opt-in; the old external invalid-key test is retained as a separate deliberately opted-in diagnostic outside A.

## F. Negative and false-success evidence

Controlled provider timeouts use the actual API/auth/CSRF, real PostgreSQL and real browser. They persist failed runs with no generated plan, retain an existing approved human fixture unchanged, preserve typed input, restore the authorized snapshot after reload and allow exactly one new explicit UUID/run on retry. Lost-response/GET faults are explicitly injected transport failures, not fabricated API success responses. Controlled valid output proves validation/persistence/recovery behavior only.

Malformed structured output remains rejected by Pydantic with a failed run/zero plans in the existing isolated provider-double test. The separate real-PG wrong-success experiment actually exited1, with1 failed in0.49s and `assert 'failed' == 'succeeded'`. It used the real missing-configuration API path (503), then read the persisted run in a fresh database session before making the deliberately incorrect assertion. Detection=true is an experiment observation, not a passing production test; it never belongs to the mandatory green suite or positive gate evidence.

The competing-editor regression was a real application defect, separate from the deliberately incorrect success experiment: pre-fix SQL showed a valid draft hash at revision3 containing the overwritten summary. The fix keeps an open editor's original revision even before local changes. A fresh conflicting save returns409 and retains both the competing saved state and unsaved local criterion.

The active-admission regression was also a real application defect: project_generation_active returned409 with the existing run's ID, which was incorrectly treated as evidence the new request might have been admitted. The fix distinguishes that explicit rejection from genuinely unknown dispatch, clears only the rejected new reference and refreshes history without changing an open editor's revision. Waiting text now describes ORBA confirmation, without inventing provider dispatch before admission.

Verifier contract tests execute native failure/timeout/launch-error behavior and reject missing, stale, mutated, skipped, retried, incomplete or controlled-as-live evidence. Unit report fixtures are explicitly authored test data, not actual gate executions. The updated Gate B wrapper's real provider-failure path has not been newly executed because another paid call requires authorization.

## G. Existing live evidence applicability

Historical browser run `f2ecf88d-6d7c-4d22-bd0e-902e2778e9ae` genuinely generated, edited and approved plan `a8772c8e-563a-4754-b587-61c4e0b2f461` on the earlier implementation. Actual model: gemini-3.8-flash, response `Tu_VavCWHpmLjuMP-6CPoQk`, usage753 input/2326 candidate/3079 total tokens; approved v1/revision2,1 epic/1 story/2 criteria. Browser exit0 and fresh SQL/hash/isolation evidence are preserved in `stage03-live-browser.json` / `stage03-live-browser-db.json` and the intake archive.

Those files have no contemporaneous relevant-source fingerprint. The intake fingerprint was measured later and is not backfilled onto them. Changed deadlines, diagnostics, lifecycle and UI require new applicable B evidence; the historical success is not current certification and the historical Full504 remains a failure.

## H. Limitations

Local development scope, without production-security certification. No distributed orchestrator, recovery/takeover, automatic paid retry, availability guarantee, email verification/recovery or later agent. Provider project/tier quota and remaining budget are unknown. A browser disconnect may not stop already dispatched bounded server work or incurred usage. Briefs/unsaved edits are not persisted in browser storage; restore requires an existing authorized run snapshot. Chromium emulation is not native-device/all-browser proof. Local owner-controlled receipt files are not adversarial attestation. A forcibly terminated verifier may leave an incomplete attempt, which cannot pass; only its owned descendants are cleanup targets.

## I. Reproduction

From repository root, with Docker running and this checkout's development Next server stopped:

```powershell
npm exec --yes --package=pnpm@12.14.0 -- pnpm --filter @orba/web exec playwright install chromium
pwsh -NoProfile -File scripts/verify.ps1
uv run --directory apps/api python -m scripts.verify_false_success
# Expected experiment exit1; inspect false_success_assertion_detected, never count it as a green test.
pwsh -NoProfile -File scripts/verify-live.ps1
# Expected BLOCKED exit2 without opt-in; zero dispatch.
uv run --directory apps/api python -m scripts.verification summary
# Exit2 until both applicable gates pass.
```

Only after explicit owner authorization:

```powershell
pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid
uv run --directory apps/api python -m scripts.verification summary
```

Runtime configuration remains in ignored root/API dotenv: GEMINI_API_KEY or ORBA_PM_API_KEY, explicit ORBA_PM_MODEL=gemini-3.8-flash, timeout90, output6000, concurrency1, account attempts3/hour, global6/hour. These application controls do not claim provider quota. Never print/commit/replace credentials. README contains exact local application startup and environment instructions. Do not run backend/browser/live/fixture/experiment commands simultaneously.

## J. Stage03 verdict

PARTIAL
