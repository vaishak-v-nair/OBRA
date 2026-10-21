# Stage03.3 DX review

Date2026-10-20; DX POLISH. Developer-facing surface is the existing PowerShell/Python verification workflow and server configuration, not a public SDK product. Scores below grade specification completeness from inspected source/docs, not a measured usability experiment. Initial8/10, amended9/10. Independent in-host voice follows before engineering.

## Investigation0A-0G

Persona: local owner/contributor on Windows with uv, pnpm, Docker and the existing checkout. They want a trustworthy explicit model choice and reproducible test receipts; they tolerate local infrastructure but not hidden paid calls. README labels the app local development and separates deterministic from live gates. No enterprise onboarding or hosted trial is appropriate.

Developer perspective (source-derived narrative, not observed user telemetry): I open README and see a local ORBA workspace with Stage03 still PARTIAL. I need to know whether my setup is wrong or the provider simply failed. The ordinary verify command should run the real database, authentication and browser checks without spending my key. I find the offline configuration command, which should tell me whether an exact model and reasoning level are valid without displaying my key. If it rejects an unsupported choice, I want the three supported identifiers and a concrete correction, not a provider stack trace. I then explicitly request a metadata GET. A ready result must not persuade me a plan has already been generated or that quota is available. I want to retain my current3.8 configuration while evaluating a separately documented3.6/minimal trial. Before approving any paid command I expect the new A receipt, matching source fingerprint, thinking/output/deadline limits and cost uncertainty. If the eventual call fails, the receipt should retain its real exit and I should still have my brief, historical approval and a run reference. A successful local fixture must never stand in for my actual model response.

Comparable onboarding research used primary references: [Google SDK quickstart](https://github.com/google-gemini/gemini-api-quickstart), [FastAPI local first steps](https://fastapi.tiangolo.com/tutorial/first-steps/), [Next.js installation](https://nextjs.org/docs/app/getting-started/installation). They emphasize one concrete start path and clear command output. Only Google's repository advertises under5minutes; no measured comparable time is asserted here. ORBA has a larger database/auth/browser setup and must not claim a new cold install under5minutes. Target on an already installed checkout: offline configuration feedback within one terminal command; exact TTHW is unmeasured. The first genuine planning value remains a separately authorized real draft, not the offline diagnostic.

## Nine-stage journey

| Stage | Existing touchpoint | Friction and decision |
|---|---|---|
|Discover|README verdict|PARTIAL visible; link investigation|
|Evaluate|Dated three-model table|Separate docs/GET/live evidence; no guaranteed latency|
|Install|uv/pnpm locks/Docker|Reuse frozen workflow; no new dependency|
|Configure|root/API dotenv, process env|Never overwrite key; compatible model/level allowlist|
|First feedback|check_pm_config offline|Safe invalid settings exit2; missing config exit1|
|Inspect metadata|--check-model|Exactly one GET; unknown/failure exit2; no paid probe|
|Integrate|Existing project UI/API|Same auth/workspace/CSRF and explicit Generate|
|Verify|verify.ps1 then later authorized verify-live|A14commands; B one actual generation; C source/profile bound|
|Recover/maintain|Run history, README runbook|No automatic retry, immutable approval/history/receipts|

First-time confusion: model metadata GET200 can coexist with failed generation; invalid Settings may block API startup whereas missing provider remains a supported app setup state; alternative configuration must be explicit and carried into B. Resolve these in docs/help and deterministic tests, not extra setup screens.

## Pass1: Getting started (9/10)

Golden path is inspect nonsecret settings offline, run deterministic A, then request one concrete paid authorization. Metadata GET is optional and explicit outside B; B reuses its own single recorded GET. Never suggest running verify_pm_live as an extra probe before the browser, since that would consume a second request. Target diagnostic under5minutes is a goal, not measured performance or a promised external response time.

## Pass2: API/CLI design (9/10)

Use ORBA_PM_MODEL, ORBA_PM_THINKING_LEVEL, ORBA_PM_MAX_INPUT_BYTES and the existing timeout/output variables. Keep -AllowPaid as the sole deliberate live switch. Model IDs are exact reviewed names, optional models/ prefix only; no arbitrary alias or auto-selected default. DefaultLOW preserves current3.8 behavior; minimal on3.8 rejects. Settings, readiness and adapter must share one small dependency-free policy table. A directly mutated/copied Settings instance must not bypass the adapter guard.

## Pass3: Errors/debugging (9/10)

Trace1: invalid model/level -> safe offline invalid_configuration and exit2, zero network; docs list corrected choices before restart. Trace2: oversized prompt+schema+snapshot -> input_too_large422 before a run is admitted, explain shorten brief/instructions or exclude selected context, no generation started. Trace3: upstream503/504 -> failed run with upstream status and actual durations, safe UI, preserved plan and no auto retry. Never print raw Settings inputs, provider bodies or request content even if an operator misplaces a key in a model field. Preserve original unknown-outcome UUID behavior.

## Pass4: Documentation (9/10)

README quick configuration links the dated investigation for prices/lifecycle and ARCHITECTURE for strict generation. VERIFICATION links current A and the immutable latest failed B; historical sections remain intact. .env.example documents compatible choices and bounds with an empty explicit model, no credential. Distinguish setup instructions from commands actually executed. Both default3.8/LOW and recommended3.6/minimal must be covered without silently changing root .env.

## Pass5: Upgrade/migration (9/10)

No schema migration, password/session reset or project rewrite. Approved records store their original requested/returned model and prompt version, independent of current policy. Unsupported syntactically valid model IDs now fail early; explain API startup impact and offline preflight. Changing model selection is reversible configuration, not a history migration. Test retrieval of old run/approved graph after selecting a different supported model and preserve promptv1 beside any v2.

## Pass6: Environment/tooling (9/10)

Use native pwsh and current locked official SDK; no Bash/WSL/global repair or new package. Existing verify.ps1 owns guarded test PG lifecycle and sequential backend/browser execution. PYTHONIOENCODING=utf-8 belongs in outer wrappers too. SDK synthetic HTTP tests assert exact body, one call, zero retry/continuation and safe timeout origin; these are labeled unit evidence. Do not claim CI/native-device coverage from local emulator results.

## Pass7: Ecosystem (8/10)

The dependency and provider docs are primary evidence, not a new community feature. No public publishing, contributor messaging or full Model Hub is authorized. Dated capabilities/prices and billing uncertainty avoid surprise cost claims. A small reviewed registry needs an operator review when lifecycle changes; no provider alias is treated as an independent alternative. Existing TODOs suffice; marketing/community infrastructure is out of scope.

## Pass8: Measurement/feedback (9/10)

Record offline prompt/schema bytes, definitions/union/property counts, unchanged authoritative-schema hash, safe request bounds and source/profile receipts. They make changes reproducible but cannot substitute for live quality/latency. GateA rejects missing/skipped/flaky identities, B rejects a second POST before dispatch, C rejects stale/controlled evidence. The deliberately incorrect success assertion must actually exit1 separately. No extra analytics/telemetry or paid benchmarking is introduced.

## Implementation checklist/tasks

- X1(P1): Add one reviewed policy and environment validation, safe errors/help/examples; tests for every supported model/level and invalid settings.
- X2(P1): Bind thinking/input/provider-schema identity into execution profile and readiness validation; test mismatch/tampering fails without network.
- X3(P1): Document invalid-startup versus missing-provider behavior, same-plan one-generation B, current prices and explicit selection command.
- X4(P1): Preserve complete historical data/receipts and run source-bound A plus expected-failure experiment; report real statuses.

No unresolved product taste decision. The next phase must review actual touched paths and this final scope. No model call has been made by this review.
