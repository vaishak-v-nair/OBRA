# Stage03.2 test plan

Pre-implementation contract,2026-10-20 local date. Tests below are requirements, not passing evidence. Actual results/native exits and source fingerprints belong in VERIFICATION.md and immutable receipts. No paid model call is authorized in this task.

## Affected surfaces

- Operator `scripts.check_pm_config`: offline configuration and explicit bounded metadata check. Run from repository root; no Docker, API, browser or PostgreSQL connection required for this command.
- Gate B orchestration/readiness artifact validation and live browser dispatch guard. Do not execute with paid opt-in until owner authorizes the concrete final handoff.
- Existing `/projects/{id}` Product Plan error/recovery flow through actual auth/CSRF/API/PostgreSQL. Controlled cases replace only model behavior in the guarded test factory, never identity or persistence.

## Codepath and flow coverage map

```text
check_pm_config argv
  help / unknown flag -> parser0/2, no Settings/network
  invalid Settings -> safe invalid_configuration2, no input values
  default -> offline configured0 / missing1, no network
  --check-model -> configuration_readiness
      missing/blank/invalid -> no GET, safe non-ready
      valid -> official SDK models.get (ONE GET,10s HTTP /12s envelope)
          200 exact positive metadata + reviewed JSON capability -> ready_for_attempt
          missing/mismatch/unknown capability -> unknown
          explicit incompatible method /404 -> model_not_supported for operation/account
          max-output exceeds metadata -> invalid_configuration
          400 invalid key /401/403 -> credential_error
          429 -> rate_limited
          500/502/503 -> provider_unavailable (actual upstream code retained)
          504/HTTPX/local deadline -> timeout (origin distinguished)
          other HTTP/decoding/SDK mismatch -> safe unknown/non-ready
          every branch -> generation_requests0, live_generation_verified=false

execute_gate B (never run paid now)
  no opt-in / stale A / config / occupied ports -> no metadata or model dispatch
  current A + explicit opt-in -> one fresh metadata artifact
      non-ready -> BLOCKED/nonzero; no browser command
      ready -> ONE guarded actual browser generation
          extra POST -> abort before forwarding; gate FAIL, never automatic retry
          provider failure -> failed run, SQL no new plan, visible safe error, nonzero
          genuine response -> Pydantic -> atomic graph -> SQL draft audit
              -> edit criterion -> reload -> exact approval -> reload
              -> independent approval SQL -> unrelated404/no content
  artifact/source/profile/attempt/time mismatches -> cannot certify B or VERIFIED
```

## Deterministic readiness tests

Create `tests/test_pm_readiness.py`. Use the actual official SDK with explicitly synthetic HTTPX transport in isolated contract tests; no real network or live-model claim. Assert GET-only exact Google path, empty request body, timeout/header values, at most one SDK dispatch on errors and no generate/countTokens operation. Exercise the entire safe status matrix, missing/mismatched/empty metadata and unchanged configuration. Check `--help`, bad args, offline0/1, explicit0/2 and safe invalid Settings without secret/input leakage.

Positive metadata reports must still say generation_requests0 and live_generation_verified=false. A syntactically valid different model with metadata alone has unknown structured-output compatibility until reviewed; never auto-select or change the owner's model. Metadata HTTP error bodies/headers and input exceptions must not enter report output. A real PG integration probe around a controlled metadata check asserts run/plan counts unchanged.

## Durable lifecycle schedules with real PostgreSQL

Extend `tests/test_pm_reliability.py`, retaining all existing identities and assertions. Provider doubles are explicit and do not certify Gemini.

1. Hold the first generation inside a counted double. Submit the exact same user/project/key/input concurrently: observe the same running record, no second provider call, then one validated committed graph and same successful replay. Read the plan in a new SQLAlchemy session and verify epics/stories/criteria.
2. Feed a synthetic actual SDK HTTP503 through the real application endpoint. Verify public502/provider_unavailable, stored503/upstream_http, failed run/no result, exactly one SDK request and approved plan hash/actor/time unchanged. A later successful unrelated run cannot mutate the failed record; an exact replay must not redispatch.
3. Inject a persistence failure after full graph flush, inspect from an independent session while the transaction is uncommitted and assert no root/children are visible. After rollback assert no roots/children persisted and the run is never succeeded; an unknown execution can be honestly reconciled to interrupted using its durable deadline. Retain existing final-commit acknowledgement, expired-session graph rollback, fencing and invalid-output tests.

## Browser recovery

Extend the guarded controlled provider and `tests-controlled/pm-recovery.spec.ts` with explicit upstream503/public502, provider429 and malformed-output scenarios. Each seeds a labeled human-authored plan, explicitly approves it, submits a distinct brief, rapidly activates Generate twice and observes exactly one POST/failed run. Verify no new plan, preserved brief/instructions and approved hash/actor/time; reload, GET Check status and explicitly restore input without any new POST. Run desktop/mobile/tablet Chromium with both-theme/overflow checks where applicable. No intercepted fake API responses or auth state; only test-only provider behavior is controlled. Keep existing18 controlled and60 core identities.

## Verifier and negative-path integrity

Extend existing verifier tests with typed readiness artifact content/linkage/time/source/profile validation and non-ready short-circuiting. Use temporary authored test receipts solely to test validators, never as real A/B evidence. Prove a required native child assertion still exits1 and stops a gate, and B cannot ignore a failed browser command. Preserve every existing anti-skip/retry/controlled/stale-evidence check.

Run the isolated `scripts.verify_false_success` experiment separately with actual real PostgreSQL. Its intentionally incorrect assertion must actually yield native1 and failed-vs-succeeded text; that receipt is not a mandatory-suite failure or a passing live test.

## Required execution and boundaries

Run focused Ruff/format/backend/type/lint/browser checks as justified, then the entire `pwsh -NoProfile -File scripts/verify.ps1` after source stabilizes. Backend and browser execution must be sequential against guarded orba_test. All old tests remain mandatory; no skips/xfail/retry. Record actual native failures/fixes instead of rewriting them. Final audit compares all pre-existing receipt/artifact and dotenv file hashes, allowing only latest-A pointer advancement, and confirms no Git commit/stage/discard.

Gate B remains NOT RUN on changed source until fresh owner authorization. Existing actual Gemini metadata and documentation prove model identity/advertised methods only. No controlled test or old live success can supply the missing paid current-source acceptance evidence.

## Verification defects discovered during full execution

The first full A exposed an ambiguous text locator matching both the saved project paragraph and editable PM brief. Verify the saved overview paragraph and labeled Product brief independently, including after reload; retain creation201/detail/list checks. The second A executed all14 commands with exit0 (221/60/30 tests) but correctly did not become PASS because JUnit baseline normalization corrupted a slash in a parameter ID. Normalize module paths only. Three authored UNIT XML regressions exercise slash, dot and embedded .py:: parameter text; matching literal identities must pass and changed names must still be rejected. Their actual pre-fix run exited1 (2 failed/1 passed); corrected focused verification exited0 (55 passed), and collection retained every prior identity plus the three new cases. These fixtures are verifier tests, never provider evidence. The final full A subsequently passed224/60/30 on fingerprint2a2128d0f21c914b4640db6eb7c31ddf446ad00076a9a28e52d03bfcbe44b098; all14 native commands and structured report validation passed. Real paid Gate B remains NOT RUN pending fresh authorization.
