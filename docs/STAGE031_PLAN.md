<!-- /autoplan restore point: C:\Users\vaish\.gstack\projects\OBRA\main-autoplan-restore-stage031-20261019T112206Z-0ec2245d.md -->
# ORBA Stage03.1 reliability and verification plan

Authority: implement the owner's reliability hardening request, preserve all uncommitted Stage03 work and data, no commits or Stage04. New paid requests require a later explicit user authorization after Gate A passes and diagnostics are reviewed.

Outcome: truthful, independently runnable deterministic Gate A; explicit opt-in real-model Gate B; revision-bound Gate C verdict. Preserve historical failures, the working provider/PRD contract, authentication, themes and approved plans.

Initial implementation approach:
1. Inspect actual timeout evidence and all request/deadline/idempotency boundaries. Capture uncommitted source/evidence before edits.
2. Run sequential CEO, Design, DX, Eng autoplan reviews. Reuse current lifecycle, routes, provider abstraction and verification commands.
3. Add safe monotonic phase timings to existing run diagnostics; distinguish upstream HTTP504, local SDK timeout and browser/proxy loss. No automatic retry or increased timeout claim.
4. Make manual retry use a fresh durable run identity only after a confirmed terminal run, preserving brief/instructions and approved plans. Unknown outcomes get GET recovery only.
5. Refactor verify.ps1 into Gate A with no external AI dependency. Add labeled, test-only controlled-provider browser failure checks with real API/PostgreSQL and no production bypass.
6. Add verify-live.ps1 with explicit paid opt-in and current passing Gate A prerequisite. Prefer one real browser generation with actual API validation and independent draft/approval SQL audits, avoiding duplicate paid API probes.
7. Add shared versioned source manifest, immutable per-attempt reports, strict evidence validation and a stage summary that cannot use mocks or stale source as live proof.
8. Run deterministic tests, failure experiments, full Gate A and docs; prepare Gate B but stop before invoking the model and request explicit authorization.

Verification boundaries: integration uses guarded orba_test PostgreSQL; only controlled provider behavior is doubled in explicitly labeled Stage03.1 deterministic tests. No generation-on-load, fallback PRDs, token logging, fake successes, deployment, database reset or automatic commits.

Task checklist:
- [x] Inspect saved evidence, Git and current security/lifecycle implementation; intake snapshot captured.
- [x] Complete sequential autoplan reviews and record decisions.
- [x] Implement diagnostics, retry and verification gates; final current-source A passed139/51/18 after retaining both reproduced recovery regressions.
- [x] Extend meaningful regression and gate failure tests; existing102/51 identities preserved and new cases registered.
- [x] Execute Gate A and isolated false-success experiment: A exit0; real-PG intentionally wrong assertion actually exit1, detection=true.
- [x] Document exact findings/evidence and prepare Gate B authorization request. No-opt-in B actually exit2/zero dispatch; Gate C actually exit2/PARTIAL.
- [x] Execute exactly one Gate B after explicit owner approval: upstream503 UNAVAILABLE, real browser exit1, persisted failed/no plan; no retry. Gate C revalidated A PASS/B FAIL/PARTIAL on unchanged source.

## Sequential reviews and decision audit

CEO completed: docs/reviews/STAGE031_CEO.md and STAGE031_CEO_VOICE.md. Primary plus independent in-host review; no outside-model consensus. Design follows only after these artifacts are written; DX follows Design, and Eng reviews the final amended plan last.

| ID | Phase | Decision | Class | Principle | Reason / rejected option |
|---|---|---|---|---|---|
| C1 | CEO | Shared no-external-AI Gate A and explicit live Gate B | Mechanical | Complete/explicit | Script split alone leaves stale proof and recovery gaps |
| C2 | CEO | One paid browser generation with API and fresh draft/approval SQL | Test composition | Pragmatic/DRY | Avoid duplicate paid API probe while preserving assertions |
| C3 | CEO | Immutable attempts, source/artifact hashes, conservative verdict | Mechanical | Complete | HEAD e3fccd6 alone cannot identify uncommitted source |
| C4 | CEO | Fresh terminal confirmation before manual new-UUID retry | Mechanical | Complete | Unknown-outcome Clear reference can unlock duplicates |
| C5 | CEO | Bounded timing/origin diagnostics, no inferred historical duration | Mechanical | Explicit | A90s setting is not an actual latency measurement |
| C6 | CEO | Preserve original scope, no queue/automatic retry/deployment/commit | Mechanical | DRY | Existing lifecycle and deferred TODOs already define authority |
| D1 | Design | Keep unknown request UUID; remove clear-reference unlock | Mechanical | Complete | No matching run is not proof dispatch cannot arrive |
| D2 | Design | Recheck exact terminal run before explicit fresh-UUID Retry | Mechanical | Explicit | Local active-history state alone is insufficient |
| D3 | Design | Restore submitted brief explicitly from authorized snapshot | Mechanical | Complete | No browser storage of briefs and no silent edit overwrite |
| D4 | Design | Keep success recovery UUID until saved result read succeeds | Mechanical | Complete | A metadata refresh failure must not lose the saved result reference |
| D5 | Design | Separate loaded-empty/configuration from failed reads; neutral uncertainty notices | Mechanical | Explicit | Do not turn unavailable data or pending status into success/setup |

Design completed: docs/reviews/STAGE031_DESIGN.md plus independent voice. Fallback light/dark recovery sketch is external under .gstack/projects/OBRA/designs, labeled design only. No redesign, offline credential/brief storage or paid calls were introduced.

DX completed: docs/reviews/STAGE031_DX.md and independent voice. The inherited script's upgrade/check used the development default; Gate A will force the guarded orba_test DSN for migrations, drift and tests, while scrubbing AI keys/model from deterministic child processes.

| ID | Phase | Decision | Class | Principle | Reason / rejected option |
|---|---|---|---|---|---|
| X1 | DX | Normal verify is local A; explicit live opt-in and current A prerequisite | Mechanical | Explicit | Do not preserve implicit paid Full behavior |
| X2 | DX | Guard and bind migration/drift/test DSN to orba_test | Mechanical | Complete | Existing script could migrate/check dev instead |
| X3 | DX | Shared runner with fixed native arguments, exact exits, immutable attempt logs | Mechanical | DRY | No duplicate ad hoc parsing or swallowed failure |
| X4 | DX | Keep historical live proof historical; new lifecycle requires fresh opt-in B | Mechanical | Complete | No backfilled fingerprint on old results |

## Timeout finding and concrete implementation refinement

Installed SDK2.31.0 populates X-Server-Timeout from HttpOptions.timeout (milliseconds converted to seconds). The prior adapter used the same90s value for that header, HTTPX and the outer asyncio timeout. Saved ServerError504 proves an upstream HTTP response, but does not establish an independent provider outage or exact latency; the caller also supplied the server deadline.

Keep ORBA_PM_TIMEOUT_SECONDS as the server/model budget (currently90). Explicitly send that server deadline, give HTTPX/SDK transport five seconds of grace and the outer async envelope ten seconds of grace. Existing running lease is budget+45, publication285, proxy290 and client300; the adjusted transport stays inside these fences, including the configured maximum180s. This avoids equal-deadline classification races without claiming to cure a real upstream timeout or making another call. Record actual origin/stage durations and test the real SDK's outgoing header/read timeout with synthetic HTTP. Both changes invalidate old live certification until a fresh authorized B.

Controlled browser failures will use FastAPI's native dependency override in a test-owned guarded app factory, not a runtime fake-provider environment switch. The production provider dependency still selects only the official Gemini adapter.

## Gate implementation contract for final engineering review

Use one standard-library Python verifier under apps/api/scripts with thin PowerShell entrypoints. Fixed required command arrays are the sole execution/validation registry; no CLI override can omit tests and still produce a passing gate. Gate A scrubs model credentials/selection in child environments and binds DATABASE_URL to the exact guarded test target, including Alembic upgrade/check. Keep all102 existing backend/51 core browser cases and add controlled-provider recovery browser checks; preserve the old external invalid-key test as an explicit external diagnostic, outside A.

Each invocation owns a unique immutable attempt directory and captures native stdout/exit/duration, start/end source manifests and artifact hashes; a latest pointer only references a receipt. Relevant Git-tracked/nonignored source, prompts, migrations, tests, scripts/configs and lockfiles are hashed, excluding credentials, docs/evidence/build/dependency/generated files. An advisory local gate lock prevents ordinary concurrent A/B runs; this is not coordination with arbitrary manually launched tests. Interrupted attempts and missing/incomplete/mutated receipts cannot pass.

Gate B requires explicit AllowPaid plus current passing A, checks configuration without dispatch, and performs one real browser generation only. That same flow validates actual authenticated API output, then fresh PostgreSQL draft graph/hash/state and later edited/approved graph/hash/actor/time, and unrelated-user denial. Missing opt-in/config/prerequisites returns nonzero with BLOCKED evidence and zero provider calls; an actual provider/browser failure stays nonzero and leaves a receipt. Direct legacy live entrypoints also need deliberate opt-in rather than bypassing the gate.

Stage summary validates exact required commands/exits, current source hash, expected execution class, complete browser/API/SQL proof and artifact integrity. Controlled or absent B can never yield VERIFIED. A/B native failure experiments remain separate, with actual failing PostgreSQL/Pytest assertions; no green stub or weakened application assertion is used.

## Final engineering decisions

E1: explicitly empty both API-key aliases and model in Gate A; defeat dotenv fallback. E2: distinguish authoritative non-dispatch/pre-admission rejection from unknown outcomes. E3: fixed commands also require complete zero-skip structured reports and scrubbed test-selection environment. E4: record nonsecret effective provider configuration, not secret hashes. E5: bound commands, clean only owned descendants and start only test-postgres. Adopted after primary and independent engineering review.

## Aggregated implementation tasks

- [x] C1 (P1) Verification: Separate local and live verification with conservative verdict
- [x] C3 (P1) Evidence: Bind immutable attempts to source and actual artifacts
- [x] D1 (P1) ProductPlan: Keep unknown outcome GET-only and confirm terminal retry
- [x] D4 (P1) ProductPlan: Retain saved result reference and explicitly restore submitted input
- [x] X1 (P1) Verification: Explicit paid opt-in and current Gate A prerequisite
- [x] X2 (P1) Verification: Guard test migrations and override dotenv credentials
- [x] E3 (P1) Verification: Validate complete no-skip results and propagate native failures
- [x] E4 (P1) Provider: Bound deadlines and add safe measured phase diagnostics
- [x] E5 (P1) Tests: Preserve regressions and test controlled browser recovery

## Cross-phase themes

All four phases identified truthful evidence and explicit scope as core boundaries. CEO/Eng require revision-bound proof; Design/Eng require GET-only uncertainty and exact retry confirmation; DX/Eng require guarded test configuration and complete command results. No scope expansion, taste choice or owner-direction challenge remains.

## GSTACK REVIEW REPORT

| Phase | Result | Independent voice |
|---|---|---|
| CEO | Scope and six decisions documented | In-host Codex, complete |
| Design | Seven dimensions, recovery sketch and state contract | In-host Codex, complete |
| DX | Eight dimensions, journey and command contract | In-host Codex, complete |
| Engineering | Six dimensions, test/failure diagrams and E1-E5 adopted | In-host Codex, complete |

[running under Codex — nested codex passes skipped; set GSTACK_FORCE_CODEX_REVIEW=1 to force]

Outside-model consensus: N/A. Helper binaries unavailable; native JSON task aggregation used. The owner explicitly requested implementation; proceed with reversible authorized hardening. The final approval gate is the concrete new paid Gate B attempt after Gate A, as the owner required. Review completion is not implementation verification.

Implementation QA refinement: an unchanged open editor could receive a newer plan revision from Check status while keeping its older draft content. The real browser/API/PostgreSQL regression reproduced a lost competing summary (native exit1; fresh SQL revision3). Recovery now keeps every open editor bound to its original revision. The same regression passed across desktop/mobile/tablet with409 conflicts and retained local edits. This is within the reviewed exact-revision/recovery contract, not a new stage. Gate C actually refused the earlier passing A as STALE after relevant source changed.

A second real browser/API/PostgreSQL regression reproduced an active-project rejection that stranded a never-admitted request UUID (native exit1). The fix clears only the confirmed rejection, preserves GET-only unknown outcomes and refreshes history without changing an open editor. It passed on all3 viewports. Final complete Gate A passed139 backend/51 regression browser/18 controlled browser, all14 commands0. The separate wrong-success experiment actually failed as required; B refused absent opt-in with zero commands, and current-source Gate C retained PARTIAL. Fingerprint and immutable receipts are recorded in VERIFICATION.md. No additional paid request or commit occurred. That statement records the pre-authorization checkpoint. The owner later authorized exactly one bounded attempt; its actual outcome is appended below.

Authorized execution on2026-10-19T17:09:20Z used the existing reviewed command and unchanged fingerprint c5c705e057e346e2d1f9059110b2927f86d6493dc94a3332065e4aa5dc32a9e1. One browser generation POST received application502 after upstream503 UNAVAILABLE; run5421d0db-f2da-4886-b583-d5c8acf99dee remained failed with no plan. Browser command exit1, subsequent independent SQL inspection exit0 and Gate C exit2/PARTIAL. There was no retry and no additional paid authorization remains. New password-length instructions are a separate pending security/scope clarification; application source was not changed during this attempt.

NO UNRESOLVED DECISIONS FOR THE REVIEWED LIVE ATTEMPT
