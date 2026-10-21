# Stage03.1 CEO review

Source: primary Codex-family review plus independent in-host voice in STAGE031_CEO_VOICE.md. Nested CLI reviews are skipped under the detected Codex host; CLI0.163.0/login status were checked without a model call. No outside model or cross-model consensus is claimed. Mode: SELECTIVE EXPANSION within the owner's fixed Stage03.1 boundary.

## Premises and outcome

The premise that a504 implies an application timeout is not assumed. The failed command was python -m scripts.verify_pm_live, which uses FastAPI TestClient directly and bypasses browser/Next. Its saved SDK ServerError/provider_http_status504/DEADLINE_EXCEEDED supports an upstream HTTP error; actual per-phase latency and the provider's internal cause are unknown. A90-second setting is not a measurement of a90-second request.

The premise that existing success can certify changed code is rejected. HEAD is e3fccd6 while Stage03 is uncommitted, so commit identity alone is insufficient. Preserve old proof as historical and make new gates depend on relevant file hashes.

The owner's outcome is reliable failure recovery and honest acceptance, not a higher apparent pass rate. Doing nothing preserves correct failed-state handling but makes local regression results depend on an external model and permits accidental use of stale evidence. No competitive deadline justifies additional paid probes, fallback content or weakened authorization.

## Existing code leverage

| Problem | Reuse | Change |
|---|---|---|
| Actual provider/error handling | pm_provider.py, SDK one-attempt transport | Add safe origin/timing classification; retain full schema |
| Execution/ownership/idempotency | pm_service.py, existing PostgreSQL locks and leases | Instrument boundaries, preserve terminal fences |
| Recovery | ProductPlan pending UUID, run GET, input snapshot | Terminal-confirmed manual retry and explicit brief restore |
| Verification | verify.ps1, existing102 backend/51 browser cases | Separate no-network Gate A from explicit live Gate B |
| Real-model evidence | live browser plus inspect_pm_run | Independent draft/approval SQL audit in one paid flow |
| Historical proof | Stage03 transcripts and JSON | Immutable attempts, source manifest and conservative verdict |

## Dream state and alternatives

```text
CURRENT                         THIS PLAN                         12-MONTH IDEAL (not scope)
correct failures, mixed gate -> local checks + opt-in live proof -> broader evaluated planning quality
unbound old receipts          -> code-bound attempt receipts      -> defined retention/attestation policy
manual recovery friction     -> explicit safe retry               -> demand-led durable execution
```

| Approach | Coverage | Effort (human / agent) | Risk | Pros | Cons |
|---|---:|---|---|---|---|
| Minimal script split only | 6/10 | 0.5d / 30m | Medium | Few files; preserves commands | No timings, stale-proof defense or unknown-outcome retry fix |
| Shared gate receipts + existing lifecycle instrumentation | 10/10 | 2-3d / 2-4h plus checks | Medium | Reuses app, closes stated gates, one live generation | More contract tests and manifest maintenance |
| Durable worker/observability platform | Outside scope | weeks / days | High | Could support disconnect recovery | New infrastructure, retry authority and Stage04 drift |

Choose the second approach for completeness and explicit boundaries. A single live browser generation can cover provider/API validation, independent draft SQL, edit/reload, approval SQL and isolation without a second paid probe. This is a documented test-composition choice, not removal of an API or persistence assertion.

Hour1 human / first20m agent: snapshot uncommitted code/evidence and establish baseline. Hours2-3 / next45-90m: instrument and implement shared receipt validation, opt-in and failure propagation. Hours4-5 / next45-90m: UI recovery, controlled browser API, SQL audits and regressions. Hour6+ / checks and review: run Gate A and false-success experiment; stop before paid Gate B. These are estimates, not measured completion claims.

## 1. Architecture

Keep FastAPI as authority and the synchronous provider lifecycle. Add one small trace collector and one shared verification module, with thin PowerShell entrypoints. No queue, new service, database reset or second authentication system is warranted.

```text
Browser -> Next proxy -> FastAPI auth/CSRF -> PM lifecycle -> ONE Gemini SDK call
                                               |                  |
                                               +-> PostgreSQL <---+ validated result only
                                               +-> safe timing diagnostics/logs

verify.ps1 -> shared runner -> local required commands -> Gate A receipt
verify-live.ps1 + explicit opt-in + current A -> real browser/API/SQL -> Gate B receipt
Gate A/B + source/runtime fingerprints + artifact hashes -> conservative stage summary
```

## 2. Error and rescue map

The current adapter distinguishes local timeout from APIError in separate handlers, but does not persist enough elapsed/origin detail. The proxy currently turns every upstream exception into api_unavailable; it must distinguish its own deadline from a forwarded provider504 while keeping the outcome unconfirmed. Neither layer may create a new POST automatically.

| Path / exception | Rescue | User/operator sees | Test |
|---|---|---|---|
| SDK APIError504 / ServerError | failed run, no plan, provider response origin | Provider timeout, run reference | SDK synthetic HTTP + historical actual504 |
| asyncio TimeoutError / HTTPX timeout | failed run, local deadline origin | Timed out; usage may have occurred | Isolated unit, real PG |
| APIError429 | failed run, safe Retry-After | Provider rate limit | SDK unit |
| APIError500/503 / network HTTPError | provider_unavailable | Provider unavailable, not credential advice | SDK/transport unit |
| Pydantic ValidationError | failed run, no plan | Invalid model response | Existing unit + PG |
| SQLAlchemyError during final commit | fresh read or outcome unknown | GET recovery, no retry POST | Existing uncertain-commit unit |
| Browser/proxy timeout or cancellation | retain request UUID and brief | Outcome unconfirmed, Check status | Controlled E2E |
| Missing/corrupt/stale gate receipt | nonzero/reject eligibility | Missing gate or source mismatch | Runner/verdict contract tests |
| Child native check nonzero | preserve exact code, stop subsequent steps | Gate FAIL with real log | Actual failure experiment |

## 3. Security

The existing project/workspace/session and CSRF fences remain authoritative for every real request. Controlled provider behavior belongs only in a test-owned app factory with the exact guarded orba_test DSN/origin and no runtime production flag; the owner explicitly permits this deterministic test boundary. Logs and receipts contain UUIDs, phases, bounded numeric durations, categories and allowlisted status metadata, never credentials or private briefs.

Threats: accidental test provider activation has low likelihood/high impact and needs a hard test-DB guard. Stale artifact certification has high likelihood/high impact without fingerprints and required-command validation. Operator-forged local evidence is outside this local verification trust boundary; a JSON receipt is not signed production attestation.

## 4. Data and interaction shadow paths

```text
explicit submit -> auth/input -> reserve/running commits -> provider -> validate -> atomic plan/success
nil/empty brief ->422 before dispatch
provider error -> failed/no plan -> read terminal state -> explicit new request UUID
network loss -> unknown UUID retained -> GET recovery only -> terminal or still unknown
missing evidence -> NOT RUN/BLOCKED -> never VERIFIED
stale/edited artifacts -> reject receipt -> never VERIFIED
```

Double clicks must remain one request; unknown outcomes must not be unlocked by Clear request reference. Retry requires a freshly confirmed failed/interrupted run and a new UUID, and retains editable brief/instructions. Navigation, revoked membership, stale context, admission429 and empty history need named states, with no automatic paid retry.

## 5. Code quality

The existing lifecycle already solves the hard transaction/terminal problem; rewriting it would increase risk. Add trace boundaries and keep error classification in the provider, recovery wording in one UI helper and evidence rules in one verification module. A generic job framework or separate provider router would duplicate working authority.

## 6. Tests

Preserve102 backend cases and all51 browser cases. Add tests at actual failure boundaries rather than asserting a PASS string. A hostile QA test should mutate source/artifact hashes, omit a required check, label doubles as live, replay an idempotency key and attempt retry while the original outcome is unknown.

```text
Timing/origin         -> SDK units + lifecycle real-PG tests
Manual retry/recovery -> browser -> actual Next/API -> controlled provider -> real PG
Gate A child failure  -> shared runner -> actual failing pytest experiment -> native nonzero
Gate B opt-in         -> absent opt-in/current A -> BLOCKED before dispatch
Gate C eligibility    -> missing/failed/stale/double/mutated evidence -> not VERIFIED
Real success          -> ONLY explicitly authorized live browser + draft/approval fresh SQL
```

Time/randomness risks are controlled with fresh UUIDs, explicit awaits and no retries. Do not use a paid call as a local regression prerequisite. The deliberately wrong-success experiment remains separate from green discovery.

## 7. Performance

Keep the current bounded provider/output/phase budgets rather than inventing a larger timeout as a fix. Timing is constant-sized per run and does not hold a connection while the model runs. Manifest hashing occurs only during verification, excludes dependency/build/credential trees and must detect files changed while a gate runs.

## 8. Observability

Record admission, confirmed running, provider, validation and persistence boundaries using a monotonic clock. Distinguish measurements before a terminal commit from complete transaction timings logged after an acknowledged commit; do not claim exact crash durations. Historical runs without timings keep unknown values, not fabricated backfills.

## 9. Rollout and rollback

No schema migration is expected: existing diagnostic JSON can hold bounded measurements. Preserve the owner's uncommitted work, archive the Stage03 report/evidence, and do not auto-commit or reset. Run local gates before restarting development; no public deployment is authorized.

## 10. Trajectory

This change improves evidence quality without altering the PM product or creating an orchestrator. Reversibility is4/5: code can be reviewed independently, while immutable receipts remain historical records. Existing TODOs already cover durable jobs, retention, broader evaluation and production identity; do not duplicate them or treat this request as authorization.

## 11. Design

Reuse ProductPlan, native controls and semantic tokens. Lead with the failed outcome and what remained safe, then offer Check status for uncertainty or an explicit paid-capable Retry for a confirmed terminal failure. Desktop/mobile/tablet and keyboard labels must cover these states without percentages, fake steps or an endless spinner.

## Failure modes

| Failure | Prevention / rescue | Critical gap before work |
|---|---|---|
| Local gate calls external invalid-key provider | Replace its inclusion with labeled controlled browser checks | Yes |
| Historical success certifies changed lifecycle | Full relevant source manifest + artifacts/config validation | Yes |
| Failed live run leaves no receipt | Attempt report finalized on nonzero/exception/interruption | Yes |
| Unknown request cleared into duplicate POST | GET-only recovery; freshly terminal-confirmed retry | Yes |
| Trace claims committed success before commit | Separate precommit diagnostics from postcommit logging | Yes |
| Test provider leaks into normal runtime | Test-owned guarded factory, no runtime selection flag | Yes |

All six gaps have implementation/test tasks below; none is claimed closed by this review.

## Decisions and scope

1. Reuse the existing lifecycle, no worker/queue/migration (mechanical, explicit/DRY).
2. Separate independent gates and preserve nonzero exits (mechanical, owner requirement).
3. Prefer one live browser generation plus independent API/SQL checks (composition choice, pragmatic/quota conscious).
4. Reject stale evidence and fail closed on missing proof (mechanical, completeness).
5. Permit only terminal-confirmed explicit retry (mechanical, safety/completeness).
6. Keep external operational dashboards, durable jobs, retention and production certification out of scope (duplicates of existing deferred TODOs).

## Independent voice and consensus

The independent in-host voice found four P1 issues (external Core call, stale evidence, incomplete SQL audit, unsafe unknown-outcome unlock) and two P2 issues (timings and scope). They agree with the six decisions above. CLI outside-model voice is unavailable/skipped under the detected Codex host; external consensus is N/A for all six dimensions, not6/6 cross-model confirmation.

## Implementation tasks

- [ ] C1 (P1, human2h / agent30m): replace mixed verification with shared required-command receipts and no-network Gate A; scripts/verify.ps1, API scripts/verification.py.
- [ ] C2 (P1, human3h / agent45m): implement opt-in, one-call Gate B with draft/approval SQL and failure artifacts; verify-live.ps1, live browser and inspector.
- [ ] C3 (P1, human2h / agent30m): bind verdict to current source/artifacts and reject controlled/stale proof; shared verification module/tests.
- [ ] C4 (P1, human2h / agent30m): require confirmed terminal retry, retain/recover brief, cover actual UI/API/DB; ProductPlan and controlled tests.
- [ ] C5 (P1, human2h / agent30m): instrument safe timings/origin and test failures/approved preservation; provider/service/trace module.
- [ ] C6 (P1, human1h / agent20m plus checks): run required gates/false-success experiment and document exact boundaries without paid calls.

## Completion summary

System audit, premise challenge, alternatives, existing leverage, dream delta, five diagrams, nine error/rescue paths and six failure modes are written. All11 sections were evaluated. Six decisions stay within the owner's scope; no user challenge or additional future TODO is required. Independent voice completed, external voice N/A; no cross-model vote is invented. Review complete with implementation concerns, not implementation success.
