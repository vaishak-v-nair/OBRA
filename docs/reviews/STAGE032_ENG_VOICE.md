# Stage03.2 independent engineering review

Recommendation: proceed with the bounded readiness/CLI and deterministic verification work, with E1-E5 below as acceptance details. No generation lifecycle, prompt, authentication, migration or credential change is justified by this review. Complete Gate A and the isolated false-success experiment, prepare the concrete one-generation Gate B command, then STOP for the owner's fresh paid authorization.

This is an independent in-host Codex-family source review, not cross-model consensus or executed verification. Reviewed the Stage03.2 plan and repository provider, configuration, service, persistence, gate and test code. No skill files or credentials were read. No external requests, database queries, tests or model calls were executed. Only this review document was written. Source references describe the preimplementation checkout and may move during implementation.

## Six engineering dimensions

| Dimension | Assessment | Confidence and motivating source |
|---|---|---|
| Architecture | A small typed metadata module shared by the existing CLI and Gate B is proportionate. Keep application generation and authorization independent of metadata readiness. | High: `apps/api/scripts/check_pm_config.py:8-41`; `apps/api/orba/pm.py:53-62,89-108`; `apps/api/orba/pm_service.py:345-415`. |
| Code quality and complexity | Reuse the official SDK, bounded transport and safe metadata classifiers. A narrow report schema and validator are enough; avoid a client framework or another preflight executable. | High: `apps/api/orba/pm_provider.py:65-109,135-177,193-239`; `apps/api/scripts/verification.py:117-152`. |
| Tests and evidence | The proposed additions close real gaps: current concurrent generation uses different request UUIDs; SDK rejection tests and approval preservation tests are separate. Metadata evidence must be validated semantically. | High: `apps/api/tests/test_pm_lifecycle_unit.py:301-319,349-371`; `apps/api/tests/test_pm_provider_unit.py:88-134`; `apps/api/scripts/verification.py:424-459`. |
| Performance and deadlines | One metadata GET with 10s transport/server and a 12s outer budget is bounded. Preserve the existing generation T/T+5/T+10 split and short SQL phases; metadata must not open a database transaction. | High for source structure; no latency measurement: `apps/api/orba/pm_provider.py:193-211`; `apps/api/orba/pm_service.py:49-55,262-283,406-409,470-506`. |
| Security and isolation | CLI-only readiness avoids another credential-backed browser surface. Safe Settings errors and adversarial marker tests are necessary because the current CLI constructs Settings outside any safe handler. | High: `apps/api/scripts/check_pm_config.py:8-10`; `apps/api/orba/config.py:17-40,43-60`; `apps/api/tests/controlled_app.py:40-54`; `apps/api/tests/test_pm_boundaries.py:60-87`. |
| Failure handling and rollout | Preserve unknown-outcome recovery, fenced terminal states, immutable receipts and historical failures. Guard the second browser POST before dispatch and retain the distinct SQL-rollback and lost-acknowledgement outcomes. | High: `apps/web/tests-live/pm-live.spec.ts:10-11,57`; `apps/api/orba/pm_service.py:296-342,470-543`; `apps/api/tests/test_pm_lifecycle_unit.py:323-346`. |

## Required implementation refinements

### E1 - Readiness artifact content is part of the gate contract

Priority P1; confidence high.

Current receipts hash artifact bytes and recompute structured results, but Gate B requires only browser/proof files (`apps/api/scripts/verification.py:445-459`), and records the selected A receipt as a path (`:524-526`). A newly hashed JSON file is not enough to establish freshness or linkage.

Make the readiness artifact required in both `results_for(B)` and receipt validation. Validate its schema, `ready_for_attempt` status, `live_generation_verified=false`, actual metadata request count1 and generation count0. Bind it to the exact attempt ID, source fingerprint, complete nonsecret execution profile and exact successful Gate A receipt path/hash. Require its checked/start/end times to lie within this attempt, before browser dispatch, and its duration to be finite and nonnegative. Validate A itself against the same source; do not merely trust a mutable latest-A pointer or a path string. No credential value or fingerprint belongs in this linkage.

Invoke metadata once in `execute_gate(B)` after opt-in, current A, profile/configuration and port checks. `live-preflight` is invoked by both the package command and Playwright configuration (`apps/web/package.json:13`; `apps/web/playwright.live.config.ts:2-3`), so it must validate existing evidence without making another GET. Save a non-ready result as a blocked attempt with zero browser-generation dispatches. Add validator rejection cases for absent, altered, incomplete, controlled, wrong-model, wrong-profile, wrong-A, wrong-attempt and out-of-attempt evidence. Keep readiness separate from the actual browser and SQL generation proof.

### E2 - Prove the small metadata adapter at its real SDK boundary

Priority P1; confidence high.

The generation adapter already sets a fixed endpoint, explicit timeout, SDK attempts1 and transport retries0 (`apps/api/orba/pm_provider.py:155-177,193-213`). Extend that pattern narrowly; the existing SDK tests demonstrate an appropriate synthetic HTTP boundary (`apps/api/tests/test_pm_provider_unit.py:27-44,47-85,103-134`).

Use labeled synthetic HTTP with the actual SDK to assert exactly one GET to the exact canonical configured model, no generate/count/list request, fixed HTTPS host, no redirects/environment proxy, expected 10s server/transport timeout and bounded bytes before buffering. Exercise malformed/oversized/compressed responses, HTTP401/403/404/429/503/504, transport timeout, outer cancellation and client cleanup. Use zero-budget cancellation or an equivalent bounded hook instead of long sleeps. Reused generation transport failures must map into readiness statuses without presenting generation-specific failure claims.

Only complete positive exact-model metadata and explicit `generateContent` support can yield `ready_for_attempt`; absent/empty/malformed actions or limits and a mismatched model remain unknown. A nonempty supported-actions list explicitly excluding generation can be unsupported. Expose only allowlisted bounded values. Assert marker secrets from provider bodies, headers and invalid settings do not reach JSON, stderr or logs. Parse CLI arguments before Settings so help/unknown-option behavior stays deliberate; safely handle Settings validation without serializing input or exception repr. Default configured0/missing1 must make zero network calls, and invalid settings2 must be safe in both modes.

### E3 - Enforce the live browser request allowance before forwarding

Priority P1; confidence high.

The existing live test only counts request events and writes the count afterward (`apps/web/tests-live/pm-live.spec.ts:10-11,57`); `results_for(B)` subsequently rejects counts other than one (`apps/api/scripts/verification.py:274-280`). That detects excess requests after usage could have happened.

Register a test-only route guard before generation. Match the real same-origin generation URL and POST method; increment attempted/allowed/blocked counters synchronously before any awaited operation. Continue the first original request without replacing its response; abort every subsequent matching request before forwarding. Record counters in `finally` and require attempted1/allowed1/blocked0 for a successful B. An aborted second attempt still fails B even though it protected the allowance. Add a deterministic controlled-browser regression proving simultaneous/repeated attempts cannot both be forwarded; it must never issue a paid call. Do not label this browser routing guard a production provider-wide quota mechanism.

### E4 - Force exact-key HTTP replay with independent clients

Priority P1; confidence high.

Reservation checks exact `(project, actor, client_request_id)` before active-project admission (`apps/api/orba/pm_service.py:175-210`), protected by PostgreSQL locks and the unique key (`apps/api/orba/pm_models.py:28-30`). Current concurrency coverage holds one provider call but invokes a fresh request UUID for the competing request, proving active-project rejection rather than exact-key replay (`apps/api/tests/test_pm_lifecycle_unit.py:349-371`).

Use the real API/auth/CSRF/PostgreSQL application with a labeled held provider, two independent TestClients carrying the same authenticated session and CSRF state, and the same exact payload/UUID. Begin the second request while the first provider is held; assert it returns the same active run before releasing the provider. After release assert one provider call, one run, one complete graph and the same final plan on replay. Use Events/barriers with bounded timeouts and release in `finally`; no timing-only sleep or sharing one mutable TestClient across threads. Preserve existing different-UUID admission and changed-input conflict coverage. Never print copied session/CSRF values.

### E5 - Strengthen preservation tests without changing uncertain-commit semantics

Priority P1; confidence high.

Real SDK HTTP503 classification currently has isolated transport coverage (`apps/api/tests/test_pm_provider_unit.py:88-134`); approval preservation currently uses a provider double (`apps/api/tests/test_pm_lifecycle_unit.py:301-319`). Join these through a real API/PG test with only synthetic SDK HTTP: assert one upstream503 request, public502 `provider_unavailable`, actual safe503/UNAVAILABLE diagnostics, no new plan/children and an unchanged prior approved graph/hash/revision/actor/time. Keep controlled-browser503/429/invalid-output cases explicitly labeled; they prove UI/API preservation, not live Gemini availability.

For partial graph rollback, inject the fault after real parent and at least one child flush, before publication commit; repository flush ordering makes that boundary concrete (`apps/api/orba/pm_repository.py:126-128,160-162`). Observe rollback using a new Session/connection: no root or orphan epic/story/criterion rows for the attempted plan/run, and the prior approved document and approval metadata unchanged. A root-plan count alone is weaker than this graph check; current expiry rollback only asserts run/plan counts (`apps/api/tests/test_pm_lifecycle_unit.py:184-197`).

Keep SQL failure behavior aligned with `pm_service.py:527-543`: an unconfirmed persistence result can remain `run_outcome_unknown` and recover through GET/lease reconciliation. Do not force a failed terminal state or permit another automatic execution to make a rollback test simpler. Preserve the separate lost-final-acknowledgement test, which proves a committed success stays successful (`apps/api/tests/test_pm_lifecycle_unit.py:323-346`).

## Acceptance boundary

Retain every baseline identity and append meaningful new cases. Run backend, controlled browser, false-success experiment and full Gate A sequentially against guarded `orba_test`; preserve the experiment's expected native exit1 as a separate negative result. Record actual commands/exits/counts/limitations in `docs/VERIFICATION.md`. The review itself supplies no passing counts or performance measurements. Current-source deterministic success remains PARTIAL until a separately authorized real-model browser Gate B passes; no old receipt, metadata GET or controlled-provider result can close that gap.
