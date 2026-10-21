# Stage03.2 engineering review

Final amended plan incorporates CEO, design and DX before this review. Full review mode; tests use pytest/real guarded PostgreSQL and Playwright, as documented in pyproject/package/config sources. This is source/spec review, not test execution.

## Scope challenge and existing leverage

`check_pm_config.py` currently constructs Settings and prints presence, without parsing args. `pm_provider.py` already has capped official SDK transport, one-attempt retry settings and safe error metadata. `pm_service.py` already releases auth transactions, locks admission/workspace/project, commits running before dispatch, validates Pydantic and commits the graph/success atomically. Existing lifecycle tests force distinct-key concurrency, uncertain commits, session changes, approval preservation and invalid responses; the new coverage gap is exact-key concurrent replay plus independent visibility of a flushed-but-uncommitted graph.

Add one read-only module and extend the existing CLI and verifier; do not refactor the provider/lifecycle, prompt, persistence schema or security dependencies. More than eight touched source/test files is justified by the connected CLI, B receipt contract, browser guard and mandatory negative tests, not a new subsystem. No infrastructure/dependency/migration is needed. The wrong abstraction would be a provider registry, cached availability authority or automatic retry coordinator.

## 1. Architecture and threat analysis

```text
existing Settings -> configuration_readiness (offline typed report)
                -> explicit check_model -> official SDK models.get -> safe typed report
                    [fixed URL, capped transport,1 GET,10s/12s,no DB/generation]

top-level B runner
  opt-in -> current A -> nonsecret profile -> local ports -> readiness artifact
      | non-ready -> BLOCKED/nonzero, no browser POST
      v ready-for-attempt only
  real browser guard -> ONE permitted PM POST -> unchanged FastAPI lifecycle -> PG
      | second attempt blocked before dispatch             |
      +-- counts fail B                    genuine response -> validate -> atomic graph
  API+fresh SQL draft -> edit/reload -> approve/reload -> fresh SQL+unrelated404
  source/profile/artifact/result validation -> Gate C (A and genuine B required)
```

The CLI has local operator authority and no arbitrary endpoint/model argument, so it adds no public tenant-resource surface. Fixed SDK credentials stay server-side, names/status/limits are allowlisted, and ValidationError never serializes private input. Readiness GET failures preserve actual HTTP origin/code and never create a run or spend an admission attempt.10x explicit operator use increases metadata traffic, but no polling, listener, long DB transaction or automatic load multiplier is added.

## 2. Code quality and exact contracts

P1(confidence9/10): `def main(): config = Settings()` in the existing config command lacks argv parsing and a safe settings-validation boundary. Add argparse before Settings and typed safe results; preserve configured0/missing1 offline compatibility, explicit ready0/non-ready2 and parser help0/error2. Do not use an exception string as diagnostic output.

P1(confidence9/10): the live config executes `scripts.verification live-preflight` again, while the root B runner already calls `require_live_opt_in`. Keep metadata I/O only in execute_gate(B); execution_profile, require_live_opt_in and Gate C must stay network-free. Use one typed report and validator rather than duplicating status parsing in every callsite. An added required artifact must be validated for content, exact source/profile/A/attempt/time identity and false generation-proof flags, not merely hashed.

P1(confidence9/10): the live test currently counts requests via `page.on('request',...)` and asserts count only at the end. Add a test-only routing guard that forwards the first generation POST, aborts a second before the backend receives it and makes any attempted duplicate fail the flow. It must not synthesize API responses or intercept the actual first response, editing, approval, auth or isolation. Record attempted/forwarded/blocked counters explicitly.

No prompt, output-contract, model selection or generation timeout change is justified by the observed503. SDK2.31.0 accepts the current structured request types; actual grammar compatibility/availability remains a real live gate. A reviewed selected-model documentation reference can explain JSON capability; unreviewed metadata alone must remain unknown, without routing/fallback.

## 3. Test review and data-flow edges

The complete branch/flow map and concrete assertions are in [STAGE032_TEST_PLAN.md](../STAGE032_TEST_PLAN.md), copied to the external gstack test-plan path. New UX is limited to CLI output; the existing browser's failure paths receive additional executed coverage, not a redesign. Readiness default/missing/invalid/success/error/unknown branches need isolated SDK HTTP tests; a real-PostgreSQL count test proves the diagnostic path does not mutate runs/plans. No mock can count as current live model evidence.

The exact-key schedule must hold provider execution with an Event, submit the identical UUID/payload and observe one durable running ID before release. This proves actual concurrent behavior, unlike two sequential successful calls. A separately injected synthetic SDK503 through the real API verifies public502, stored upstream503 and approved data unchanged, followed by a later unrelated success that leaves the failure terminal. A flush observer and injected persistence exception must prove every relational table remains empty to another transaction and after rollback; leave uncertain run status honest and reconcile via the existing deadline path.

```text
NEW PATH / FLOW                         COVERAGE REQUIRED
offline CLI / help / bad argv        -> actual CLI function tests, network tripwire
invalid Settings / absent key        -> safe JSON/no HTTP/no private marker
SDK metadata200                     -> real SDK + synthetic GET transport contract
missing/mismatch/limits/methods      -> parameterized strict readiness classification
401/403/404/429/503/504/network       -> synthetic SDK status/origin + one-request assertions
local envelope / malformed body     -> bounded timeout + safe unknown
B preflight / artifact              -> validator tests; non-ready zero browser command
B native browser failure            -> real child assertion propagation in temporary unit attempt
exact concurrent replay             -> real PG/Event +1 provider double call +full graph
partial graph / rollback            -> fresh-session MVCC visibility and children counts
503/429/invalid-output UX            -> actual browser/API/auth/PG, controlled provider only
full regression                    -> every baseline backend/core/controlled identity in A
wrong-success claim                 -> isolated actual assertion must exit1
genuine model/edit/approval/isolate  -> authorized B only; remains NOT RUN in this task
```

The Friday-night confidence check is that a rapid double click and unknown network outcome cannot cause a second paid dispatch. Hostile checks place secret markers in provider bodies/config errors and mutate readiness evidence/source/model/time so no false VERIFIED result is possible. Chaos includes the existing interrupted lease/uncertain commit tests plus partial graph rollback. No source-only table is called passing coverage. Controlled browser cases for429 and invalid output are added because design review identified those missing concrete states; existing timeout tests remain unchanged.

## 4. Performance and operability

Metadata work is bounded by one GET,10-second HTTP/server and12-second outer timeout with no retry or pagination and the existing1MiB envelope cap. It runs without a database session or application request lock. Keep generation90/95/100, lease135 and publication/proxy/client285/290/300 budgets unchanged, with cheap1s lock/2s statement/10s transaction bounds. Browser generation wait260 and whole-test300 exceed the actual configured provider envelope; the runner's900s deadline includes owned service startup and the full one-plan browser flow. These are independent bounds, not measured generation latency or a promise of provider success.

The response begins at browser -> same-origin Next -> synchronous FastAPI worker -> async official SDK -> validation -> short publication transaction. Browser cancellation can leave that bounded worker running; the existing retained request UUID/GET-only recovery remains authoritative. A metadata check cannot cancel, recover or automatically resume generation. Add no index, cache, persistent readiness table, extra connection pool or distributed claim.

## Failure registry, rollout and completion

| Failure | Critical gap | Planned disposition |
|---|---|---|
|Readiness succeeds without generation|False-certification risk|Always false live evidence; B/C still require genuine plan/SQL/browser|
|Metadata call repeated by nested preflight|Avoidable external work|Single top-level dispatch; network-free subordinate helpers|
|Missing/stale/mutated metadata artifact|Evidence integrity|Strict content/linkage + hash validation|
|Second generation slips through page|Paid usage ceiling|Pre-dispatch abort, fail attempt, no retry|
|Same-key racing execution|Coverage gap|One held real-PG reservation/provider call/graph|
|503 or malformed response overwrites approval|Already protected, extend proof|Controlled failure plus fresh approved snapshot checks|
|Flushed graph visible/partial commit|Atomicity risk|Independent MVCC read + rollback child counts|
|Provider still unavailable|External limitation|Keep PARTIAL, preserve exact error and stop|

NOT in scope: lifecycle rewrite, new model/credential, Model Hub, provider fallback, public deployment, reset/commit, background jobs, production certification, Stage04. What already exists is reused as listed above. No new deferred item is needed; broader observability/routing/production and auth-copy concerns already live in TODOS.md.

Completion summary: four sections, concrete source findings, ASCII architecture/coverage maps, full test plan, threat/failure analysis and rollout checks written. Final independent engineering refinements must be absorbed before implementation. Then execute targeted checks and full A, preserve all failures/history and STOP at the owner's paid gate. Source review alone is not a Stage03 verdict.
