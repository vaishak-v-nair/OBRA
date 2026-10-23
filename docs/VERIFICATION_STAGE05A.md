# Stage05A verification work record

Current verdict: **VERIFIED**, based on the applicable real A/B/C receipts below.
Overall Stage05: IN PROGRESS. No model request or executor is required or authorized.

Baseline checkpoint: bb880486bf7d8441cc6415f4dc6d6085a731151b. Before implementation,
historical Stage04 A/B receipts validated against
f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb.
This is historical baseline proof, not a fingerprint for changed Stage05A source.
Nine excluded untracked files and1294 preexisting evidence files were hashed before
work; credential hashes only were recorded privately and no credential was printed.

## Actual preliminary execution

- Docker probe failed1 because Docker Desktop's Linux engine was stopped. Started
  the existing desktop helper hidden; test-postgres startup then exited0/healthy.
- Existing baseline pytest command exited0:420 passed, no skips (111.54s test time).
- Additive Alembic revision/upgrade/check commands exited0; no schema drift.
- First orchestration integration command exited1:33 passed/5 failed. Fixed actual
  detached event serialization and missing history limit/offset. Two corruption
  fixtures had hit an existing DB approval-metadata constraint before the tested
  API path; dedicated tests now assert that genuine earlier rejection.
- Repair command exited0:38 passed. Expanded real-PG suite exited0:45 passed,
  including migration preservation, ownership FKs and concurrent cancellation.
- Initial ESLint exited1 on a render-time ref read/cleanup warning; fixed the
  render use and cleanup. No lint rule was suppressed.
- Initial Chromium orchestration command exited1:7 failed at the final test-only
  safety-counter URL. It used Next's non-proxied /__test path and received404.
  Corrected to the actual loopback FastAPI counter endpoint, preserving assertions.
  Underlying prior creation/reload/recovery/cancellation/isolation checks had run,
  but these cases are recorded as FAILED, not passed.
- The corrected orchestration suite exited0:21 passed across desktop/mobile/tablet,
  zero skips/retries,378.975s command duration. Expanded backend regression exited0:
  476 passed (169.55s test duration). This includes integration and isolated units.
- First full Gate A was deliberately stopped after its first12 commands passed
  while core browser checks were running. Final inspection found that cancelled
  task list labels still said eligible for future dispatch despite cancelled
  execution state. Fixed the wording and added a per-task browser assertion.
  The stopped core command and outer PowerShell command recorded native Windows
  exit4294967295 (0xFFFFFFFF, signed -1); that Gate A receipt remains FAIL and is
  not replaced by a claimed pass. A new full gate is required for corrected source.
- The next full attempt, `20261022T131642Z-A-b4b8fa90`, passed the first13
  commands (including476 backend and60 core browser tests). The controlled-provider
  browser command exited1073807364 after225.496s. Final fingerprint discovery then
  failed with Git exit3221226091, preventing final receipt publication. Its logs
  and incomplete attempt remain unchanged; the outer PowerShell command exited1
  after553.049s. It is not a passing gate. The native
  exit codes do not establish a provider, application or host-interruption cause.
  On resumption Docker's Linux engine was stopped and Git executed normally.
- Hardened only the Stage05A verifier to journal each actual command result as it
  completes and fail closed if final source discovery is unavailable. Two added
  isolated tests execute real child processes with exits0/7, simulate only Git
  discovery failure and prove both final receipts remain FAIL while preserving
  native results. Targeted verifier checks exited0:13 passed, no skips. The
  mandatory backend identity inventory is now478, preserving every prior case.
- Resumed full Gate A `20261023T033052Z-A-38eb0084` exited124 after801.859s.
  Its478 backend cases passed; dependency/migration/drift/Ruff/format/TypeScript
  commands also exited0. ESLint hit its unchanged180s command deadline after
  181.142s (termination native exit1); its log was empty, and later commands
  were not run. The preserved receipt correctly remains FAIL. npm's own log
  records a successful public package-metadata GET in413ms, so a registry/network
  cause is not established. Independent normal/offline pinned-pnpm version probes
  both exited0 (5.729/6.451s). The exact ESLint command then exited0 with zero
  warnings in114.347s. No assertion, rule, source or per-command deadline was
  changed to obtain that result; a fresh complete Gate A is required.
- Full Gate A `20261023T034932Z-A-d6cf5f08` exited1 after1286.344s: first12
  commands passed, including478 backend cases, lint and production build. Core
  browser checks reported59 passed/1 failed, zero skips/retries. The desktop
  two-user PRD edit/approval/history/isolation journey reached its30000ms whole-test
  limit during second-user signup, after successful edit/approval/history checks.
  Mobile/tablet versions passed; the failure snapshot shows the approved source.
  Preserved the FAIL receipt and exact context under
  `development-core-timeout-20261023`. Gave only that multi-account journey a90s
  aggregate budget, matching other long integration journeys. Every assertion,
  per-expect deadline, all other test budgets and retries0 remain unchanged.
  This is not a performance-SLA claim. New source requires a complete new Gate A.
- Targeted real-service PRD journey verification then exited0:3 passed across
  desktop/mobile/tablet (25.4/23.7/21.0s), zero skips/retries. Its128.025s command
  and exact report are under `targeted-core-20261023`; this is not a full gate.
- The isolated incorrect-completion experiment executed against real PostgreSQL
  and exited1 as required. Actual task state was awaiting_executor; the assertion
  of verified_complete failed. The recorder exited0 only because it confirmed the
  expected nonzero child failure; production_test_pass=false. Receipt:
  `20261023T041426Z-expected-failure-4673fc79/receipt.json`. Its source fingerprint
  is daff99b31e5db1156011058eed168e0c04136bb840dcb75f7de2d928fe7d3f62.
- Full attempt `20261023T041504Z-A-152961ff` was interrupted before a final
  receipt:11 command journals record exit0, including478 backend tests (403.30s
  pytest time), Ruff/format/TypeScript/ESLint. Build output exists but its native
  exit was not captured and cannot count as passed. A tool wait observed Windows
  exit1073807364 and a separate shell launch returned -1073741502. On resumption
  the host's LastBootUpTime was11:35:06.5+05:30 and Docker was stopped. The restart
  is observed; its trigger is not established. No gate exit is invented and no
  partial results are combined into a pass. Diagnostic:
  `development-host-interruption-20261023/receipt.json`. Current source is unchanged.
- Attempt `20261023T061322Z-A-9e543300` also ended without a receipt after5
  actual zero-exit commands. A subsequent bounded helper attempt
  `20261023T062633Z-A-628968c6` honestly failed database startup (exit1): Docker's
  Linux engine pipe was absent. These are not passing gates. Read-only Windows
  evidence confirms another boot at11:46:58.5+05:30 and Kernel-Power41/EventLog6008
  events. They establish an unexpected shutdown, not its underlying cause.
  The earlier `development-daemon-interruption-20261023` diagnostic mistakenly
  reused11:35 boot metadata from a check before that restart. Its bytes remain
  unchanged; `development-environment-audit-20261023/receipt.json` explicitly
  corrects that sentence using actual native output. Verification is moving to a
  bounded hidden local helper; application source and per-command limits remain
  unchanged. No partial invocation is combined into a passing full Gate A.

Portable copies of these command results, selected original logs and targeted
verifier evidence are bound by
`docs/evidence/stage05a/development-20261023/receipt.json`. This development receipt
is explicitly not a passing verification gate. Incomplete and failed attempts
remain visible alongside any subsequent success.

Detailed preliminary logs/XML/JSON and sequential CEO/design/DX/engineering review
artifacts are in the private local audit directory
`C:/Users/vaish/.gstack/projects/OBRA/stage05a/20261022T122138Z`.
They are development diagnostics, not final Gate A/B receipts.

## Reproduce gates (repository root, sequentially)

```powershell
pwsh -NoProfile -File scripts/verify.ps1
pwsh -NoProfile -File scripts/verify-orchestration-local.ps1
uv run --directory apps/api python -m scripts.orchestration_verification C
uv run --directory apps/api python -m scripts.orchestration_false_success
```

Gate A: frozen dependency checks, migrated guarded PostgreSQL, schema drift, all
backend tests, Ruff, TypeScript, ESLint, production build and every previous browser
regression plus orchestration browser checks. Gate B independently runs actual
local services/browser/PostgreSQL without Gemini or an executor. The same saved run
is used for SQL/hash/graph/events/reload/replay/authorization checks. Gate C fails
closed on missing/stale/failing evidence. Receipts are create-new under
docs/evidence/stage05a and preserve command exits and source fingerprints.

The false-success command runs a separate pytest file which intentionally asserts
that awaiting_executor means verified_complete. Its actual child exit must be1;
the wrapper records the expected failure and is not a passing production test.
Do not run backend/browser checks concurrently: both own orba_test.

## Final A/B/C verification — 2026-10-23

Stage05A: **VERIFIED**. **Overall Stage05: IN PROGRESS.**
No AI generation, executor, task execution or delivery completion is claimed.

| Gate | Actual result | Exit | Immutable receipt |
|---|---|---:|---|
| A deterministic |478 backend;60 core,33 PM controlled,33 Architect controlled,39 navigation and21 orchestration browser cases;all17 commands passed |0| [Gate A](evidence/stage05a/20261023T063056Z-A-26607b2b/receipt.json) |
| B independent real local control plane |1 browser flow, real auth/API/PostgreSQL, independent SQL/hash/graph/ledger/reload/replay/isolation checks;no provider double or executor |0| [Gate B](evidence/stage05a/20261023T071133Z-B-2d2ea8b4/receipt.json) |
| C applicability/verdict |Applicable passing A+B, matching202-file source and local contract |0| [Gate C](evidence/stage05a/summary-dc55869d356642b4b00fad6acd364dac.json) |

All mandatory cases executed without skips, xfail, flaky results or automatic
browser retries. Backend totals include real PostgreSQL integrations and isolated
unit tests;58 orchestration/verifier cases were added to the420-case baseline.
The66 PM/Architect controlled browser cases use explicitly labeled test-only
providers with real auth/API/database/browser behavior. They are not live-model
proof. Orchestration fixtures are human-authored sources approved through the
actual UI; no AI response or executor result is fabricated.

Matching source fingerprint:
`daff99b31e5db1156011058eed168e0c04136bb840dcb75f7de2d928fe7d3f62`

Gate A receipt SHA-256: `b7d811360c4346337116e2a9064fae51b7286246b468a18f62951017b55a8685`.
Gate B receipt SHA-256: `e90914e51c3651f88951ad465b9953cb5bd534c7eea3c0fac26779bcbbc070c6`.
The source policy binds application, tests, migrations, scripts, infrastructure,
lockfiles and nonsecret templates; documentation/evidence updates are outside
that existing policy. The local contract binds schemas, hash version, state
transitions, edge direction, guarded test DB, one worker, zero retries and no
executor/model dispatch. Historical Stage04 fingerprint and receipts remain
historical; they are not substituted for these new gates.

### Actual Gate A commands

All commands ran from the repository root. npm exec supplies pinned pnpm12.14.0.
Durations are actual outer-command seconds, not invented timing estimates.

| Check | Exact command | Exit | Seconds |
|---|---|---:|---:|
| database | `docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres` | 0 | 1.355 |
| python-lock | `uv sync --locked --directory apps/api` | 0 | 0.099 |
| frontend-lock | `npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile` | 0 | 21.499 |
| peers | `npm exec --yes --package=pnpm@12.14.0 -- pnpm peers check` | 0 | 2.084 |
| migration | `uv run --directory apps/api alembic upgrade head` | 0 | 3.744 |
| schema-drift | `uv run --directory apps/api alembic check` | 0 | 2.299 |
| backend | `uv run --directory apps/api pytest -q --junitxml=E:\BrosKi\OBRA\docs\evidence\stage05a\20261023T063056Z-A-26607b2b\backend.xml` | 0 | 163.753 |
| ruff | `uv run --directory apps/api ruff check .` | 0 | 3.338 |
| format | `uv run --directory apps/api ruff format --check .` | 0 | 0.095 |
| typecheck | `npm exec --yes --package=pnpm@12.14.0 -- pnpm typecheck` | 0 | 31.149 |
| eslint | `npm exec --yes --package=pnpm@12.14.0 -- pnpm lint` | 0 | 97.947 |
| build | `npm exec --yes --package=pnpm@12.14.0 -- pnpm build` | 0 | 19.895 |
| core-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e` | 0 | 317.639 |
| controlled-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:controlled` | 0 | 450.39 |
| architect-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:architect` | 0 | 607.563 |
| navigation-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:navigation` | 0 | 313.898 |
| orchestration-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:orchestration` | 0 | 309.688 |

Independent Gate B: `pwsh -NoProfile -File scripts/verify-orchestration-local.ps1`,
exit0; actual child browser command took33.671s.
Gate C: `uv run --directory apps/api python -m scripts.orchestration_verification C`,
exit0. The earlier failed/interrupted invocations above remain preserved.

### Independent real local control-plane evidence

- Saved run `3cf384c2-ed64-43ba-bc39-0bd072786539` in project `5709efab-1110-4bb9-afb8-f0d1d9ec6ebf`.
- Approved architecture `53d577ff-45f4-427f-b9cd-8c9408f8a545`, version1/revision1; approved PRD `48297922-253a-429d-9789-16c320c11f3f`, version1/revision1.
- Canonical snapshot SHA-256 `c0c1431491ede7643657fc2e7f04cb844009d003b577e4f6029ce5b82666c8bc`; hash and relational reconstruction both valid.
- PostgreSQL contains2 task snapshots,1 prerequisite -> dependent edge,3 source traces and2 ordered events (sequences1/2).
- Run state awaiting_executor, revision2. Root storage is dependency-eligible;
  screen waits for storage. Both execution states remain awaiting_executor;
  execution_performed=false. No task completed or produced an artifact.
- Double activation sent1 browser creation POST. Explicit same-key replay
  returned200 and the same run; reload returned identical saved API/SQL data.
- Unsupported forged completion returned404; unrelated workspace access returned404; protected UI stayed hidden. Independent SQL remained unchanged.
- Browser generation attempted/forwarded/blocked counters were all0; server
  generation/dependency-entry counters were0. PostgreSQL PM/Architect run counts
  were0. Read-only audit commands do not dispatch any model request.
- A further native SQL inspection after the browser exited also returned0 and
  exactly matched both earlier independent-session audits. Actual command/output:
  [final audit](evidence/stage05a/final-audit-20261023/independent-sql-command.json).

### Negative-path and false-success evidence

Real API/database tests reject unapproved/corrupt/cyclic/missing/foreign source
references with no run/task/edge/success-event publication. Viewer writes and
unrelated reads are denied. Injected initialization failure rolls back all rows;
concurrent identical requests publish one run, and concurrent cancellation accepts
one revision with a contiguous ledger. Unsupported execution transitions and
public completion/event-write paths are rejected without changing saved state.

The separately executed incorrect-completion experiment has actual pytest exit1:
`awaiting_executor == verified_complete` is false. Its recorder returned0 only
because this expected failure was observed. It is not counted as a passing
production test. [Exact experiment receipt](evidence/stage05a/20261023T041426Z-expected-failure-4673fc79/receipt.json).

### Scope and operational limits

No scheduler, task claiming, executor, handoff, QA agent, sandbox or completion
API exists. Run-level blocked is reserved: invalid/clarification sources are
rejected before publication; downstream dependency blocking is implemented.
Table-owner DDL remains trusted, history uses bounded offset pagination and
browser emulation is not native-device/all-browser certification. Local test
verification is not production security or availability certification.

The host had repeated unexpected interruptions and one empty-log tool-startup
stall. Passing current evidence does not erase these failures or establish their
underlying causes. A bounded hidden local helper completed the final Gate A;
no application code, per-command timeout or model configuration changed during
that run. Only the separately documented multi-account test's aggregate journey
budget changed earlier; all assertions/per-expect limits remained intact.

No commit, push, reset/discard, development-database reset or paid model request
was performed. Stage05B and06 were not started. Preservation/secret/working-tree
checks are recorded separately in the final audit receipt.

### Final preservation and secret review

[Final audit](evidence/stage05a/final-audit-20261023/receipt.json) records unchanged
checkpoint HEAD, an empty Git index, all9 excluded files, all1294 preexisting
evidence files (including47 receipts) and the credential file unchanged. No
credential values or credential hashes are published.

Gitleaks source scanning exited0. The unfiltered Stage05A evidence scan exited1
on144 generic-api-key matches in source-manifest checksum entries. Each match was
validated as an exact64-character SHA-256 of the named current source file, with
the expected manifest policy; none was credential material. The original report
and nonzero exit remain preserved. The rerun exited0 with no remaining findings,
using only144 exact finding fingerprints and hash-bound reviewed artifacts. No
rule or directory was disabled. The full classification and exact exceptions are
in [checksum review](evidence/stage05a/final-audit-20261023/checksum-findings-review.json).
The applicable CRLF-aware tracked whitespace check exited0; immutable historical
transcripts were not edited or broadly exempted.

## Focused evidence repair superseding current applicability

The historical results above remain unchanged. A subsequent checkpoint audit
found incomplete-proof acceptance in the verifier. Owner-authorized proof-v2
repair now has fresh A/B/C at source6c21f5d8. See
[the full repair record](VERIFICATION_STAGE05A_REPAIR.md) for683 backend/186 browser
cases plus independent local B, native negative exits and immutable receipts.
The old validator did not perform those newly added checks. Overall Stage05
remains IN PROGRESS; no task execution or commit is implied.
