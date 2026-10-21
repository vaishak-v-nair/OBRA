# ORBA Stage 03.2: authorized live Gate B result

Recorded 2026-10-20. **Stage 03 verdict: PARTIAL.** The owner authorized one bounded live attempt on the frozen source below. It was executed once; Gemini returned upstream HTTP **504 DEADLINE_EXCEEDED**. The attempt stopped, no retry/model switch occurred, and no further paid call is authorized.

## Gate A, B and C

| Gate | Actual result | Native exit | Evidence |
|---|---|---:|---|
| A: deterministic | PASS; 224 backend, 60 core browser, 30 controlled-provider browser tests; all 14 commands 0, no mandatory skips/retries | 0 | [Receipt](evidence/stage031/20261020T083556Z-A-15fa5007/receipt.json) |
| B: real Gemini browser | FAIL; 0 passed, 1 failed, 0 skipped, 0 flaky; one worker, retries 0 | 1 | [Receipt](evidence/stage031/20261020T090120Z-B-0f70b66f/receipt.json), [actual browser log](evidence/stage031/20261020T090120Z-B-0f70b66f/live-browser.log) |
| C: source-bound summary | PARTIAL; A passes, B has no passing complete receipt | 2 | [Actual summary output](evidence/stage032-authorized-live-20261020T090047Z/gate-c-console.txt), [native exit](evidence/stage032-authorized-live-20261020T090047Z/gate-c-native-exit.json) |

Gate A was revalidated against the unchanged current source and immutable report artifacts; it did not need a new execution. Its deterministic provider doubles remain separate from live model evidence. Gate C was calculated by the existing network-free script, without another model request. Historical successful live flows and failed HTTP 503/504 attempts remain history, not substitutes for this failed current-source B.

## Actual provider response and validation evidence

| Field | Recorded value |
|---|---|
| Requested provider/model | google-gemini / gemini-3.8-flash |
| Official SDK | google-genai 2.31.0 |
| Generation run | c0078a43-d0ad-4036-93d6-5881ba886e66 |
| Test project | f0adb599-03e9-44e7-aa24-6cebeea87097 |
| Provider outcome | ServerError, upstream HTTP 504, DEADLINE_EXCEEDED |
| Error category/origin | provider_timeout / upstream_http |
| Public API status | 504 |
| Provider call duration | 88,825.025 ms (88.825025s) |
| Recorded elapsed before terminal commit | 88,900.712 ms |
| Acknowledged failure commit duration | 11.984 ms, separately logged |
| Final run status | failed |
| Internal diagnostic reference | 8271fdfd-5bfc-45f7-aae0-392418ae55ae |
| Returned model / provider response ID / provider request ID | null / null / null |
| Token usage | null; not returned, never assumed zero |
| Structured PRD/schema validation | NOT RUN: no product-plan response was received |

The record identifies an **upstream HTTP deadline response**, not a local 100s envelope or Next proxy timeout. The 90s provider / 95s transport / 100s outer limits were preserved. No timeout, model, credential, provider adapter, lifecycle or test assertion was changed to obtain another outcome.

The read-only readiness child separately exited 0 before generation and reported ready_for_attempt; it never proved generation availability. [Readiness artifact](evidence/stage031/20261020T090120Z-B-0f70b66f/model-readiness.json). The actual failed provider response has no returned model identifier, response/request ID or usage. Missing values were not inferred from configuration or populated with dummy metadata. The internal diagnostic reference above is not a provider response ID.

## Persistence, browser and isolation results

| Mandatory live requirement | Actual result |
|---|---|
| Single real generation dispatch | One attempted POST, one forwarded POST, zero blocked duplicates; SDK attempts 1, HTTP transport retries 0 |
| Configured scope | 1 worker, 0 browser retries, LOW thinking, 6,000 combined output/thinking-token limit; no continuation or paid API probe |
| Browser setup | Real registration/sign-in, workspace and project creation reached the generation action |
| Generation success | FAIL: browser/API received 504; normal 201 assertion actually failed |
| Truthful failure UI | PASS for failure handling: the browser observed an alert; no fabricated PRD appeared |
| Persisted run | One actual failed run, with completion timestamp and safe provider diagnostics |
| Persisted plan graph | Zero plans, zero epics, zero stories, zero criteria |
| Generated PRD rendering | NOT RUN: no valid plan existed |
| Human criterion editing/reload | NOT RUN: stopped at provider failure |
| Approval and approval persistence | NOT RUN: no draft/approved plan existed |
| Unrelated-user isolation in this live flow | NOT RUN: stopped before that step; existing Gate A isolation coverage remains passed |
| Successful live schema/API/independent SQL graph audit | NOT RUN: no generated plan |

The browser's first independent SQL process found the failed run and no plans. A second existing read-only inspector exited 0 and confirmed the same. A further fresh SQLAlchemy session used an explicit READ ONLY transaction on guarded PostgreSQL orba_test and counted **1 project, 1 run, 0 plans, 0 epics, 0 stories and 0 criteria**. That confirms the failure was persisted and no successful-looking graph was created; it is not successful-generation evidence. [Live proof](evidence/stage031/20261020T090120Z-B-0f70b66f/live-proof.json), [independent inspector](evidence/stage032-authorized-live-20261020T090047Z/failure-sql.json), [read-only SQL graph audit](evidence/stage032-authorized-live-20261020T090047Z/project-graph-sql-audit.json).

## Commands and actual exit codes

| Command/check | Exit | Duration/meaning |
|---|---:|---|
| pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid | 1 | Exactly one authorized native invocation; no retry |
| uv run --directory apps/api python -m scripts.check_pm_config --check-model | 0 | Native B readiness child: 1.924s, read-only metadata only |
| npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:live | 1 | Native B browser child: 111.328s; actual browser report duration 106.758812s |
| uv run --directory apps/api python -m scripts.verification summary | 2 | Actual Gate C: PARTIAL |
| uv run --directory apps/api python -m scripts.inspect_pm_run --run c0078a43-d0ad-4036-93d6-5881ba886e66 | 0 | Fresh SQL failure inspection: 1.560s, no model call |
| Initial inline read-only preservation audit | 1 | Windows backslash-vs-forward-slash comparison in audit helper; SQL audit already written; no application edit or model request |
| Corrected inline preservation audit | 0 | Normalized only path separators; still required exactly latest-B pointer to be the sole changed prior evidence file |

The preservation-helper failure remains in [audit-first-error.json](evidence/stage032-authorized-live-20261020T090047Z/audit-first-error.json). It was not suppressed and did not trigger any paid request. Existing isolated false-success experiments and every original negative-path result remain untouched; no assertion was weakened or skipped to turn this live failure green.

## Source fingerprint and evidence integrity

```text
2a2128d0f21c914b4640db6eb7c31ddf446ad00076a9a28e52d03bfcbe44b098
```

All **123 relevant source files** are byte-identical to the owner-authorized intake. The same fingerprint appears in Gate A and Gate B start/end manifests and Gate C. Gate B's exact nonsecret runtime profile and Gate A receipt hash match intake; its readiness and immutable artifact hashes were independently validated. No implementation code was edited.

Of **564 pre-existing evidence files**, **563 remain byte-identical**. Only the documented mutable latest-B.json pointer advanced to this new failed attempt; no historical receipt was modified. Latest-A stayed unchanged. HEAD/index, root .env and API dotenv presence/content remain unchanged. No commit, discard, reset, credential change, public deployment or Stage 04 work occurred. [Authorization/intake](evidence/stage032-authorized-live-20261020T090047Z/authorization-intake.json), [preservation audit](evidence/stage032-authorized-live-20261020T090047Z/preservation-audit.json).

The previous current verification report was archived byte-for-byte before this current status update and checked against its pre-authorization hash. It preserves the complete Gate A command table, historical failed attempts, controlled-provider test evidence, timeout findings and reproduction instructions. [Pre-live report](evidence/stage032-authorized-live-20261020T090047Z/prelive-verification.md), [archive hash check](evidence/stage032-authorized-live-20261020T090047Z/prelive-report-preservation.json). Earlier Stage 03/03.1/password reports remain unchanged. A literal runtime-key scan found no occurrence in Git-visible files/frontend assets at audit time; this is not a comprehensive security certification.

## Remaining blocker and verdict

The current-source real Gemini generation and the downstream live validation/edit/approval/isolation journey did not complete. Correct failure handling cannot substitute for those mandatory successful live checks. Upstream DEADLINE_EXCEEDED is the observed blocker. Token consumption and any actual charge are unknown because the provider returned no usage metadata.

**Stage 03: PARTIAL.** The single authorized paid attempt is consumed. Do not execute another live command, switch models, increase limits, retry or start Stage 04 without fresh owner authorization. This report records the failure; it does not authorize remediation or another attempt.
