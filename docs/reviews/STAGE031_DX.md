# Stage03.1 developer experience review

Product type: local developer workspace/API plus verification CLI/documentation, not a skill product or hosted service. Persona: the Windows-based repository owner or contributor who wants one honest local check and a separate conscious paid acceptance action. Mode: DX POLISH. Initial completeness6/10; the scores below rate the amended specification, not executed timings.

## Developer perspective

I open README's Verification section expecting to check my local change. It offers verify.ps1, which currently defaults to Full. I have a configured Gemini key and do not realize that this ordinary command can issue two generation requests. I choose Core instead, but it still invokes a real invalid-key provider test, so an external outage can still affect my local result. I now have a transcript with102 backend passes and a paid provider timeout, and cannot easily tell which acceptance gate is incomplete.

I inspect the JSON files, but their fixed names are reused and HEAD still names the Stage02 checkpoint. I cannot tell whether a past successful browser receipt applies to my current uncommitted provider code. I want a command that reports the exact failing step and its real exit code, and a separate command that refuses to call a model until I opt in.

When I open the app after a timeout, I want my brief and existing approved plan to remain readable. If delivery is uncertain, I need Check status before any new submission. If the server confirms failure, I want an explicit retry with a new run reference and an accurate usage warning. This narrative traces the current docs/code; it is not a recorded first-user session.

## Journey and friction

| Stage | Current authority | Friction | Planned outcome |
|---|---|---|---|
| 1 Discover | README introduction | Partial versus passing components needs context | Explain A/B/C and current verdict up front |
| 2 Prerequisites | README prerequisites | pnpm absent globally; dev Next lock | Exact npm-exec wrapper and stop-dev instruction |
| 3 Install | pnpm/uv lockfiles | Dependency/version mismatch | Preserve frozen/locked checks |
| 4 Hello world | health/config commands | A key can look like live proof | Presence-only configuration clearly labeled |
| 5 Local verification | verify.ps1 | External AI included; dev migration target | Gate A, guarded test DSN for upgrade/check/tests |
| 6 Real usage | ProductPlan | Unknown-state clear/retry risk | GET-only recovery or explicit terminal retry |
| 7 Debug | saved diagnostics | No phase durations/origin | Safe named timings/status/run ID |
| 8 Upgrade | uncommitted tree/evidence | Old success can mask new source | Source fingerprint, immutable attempt artifacts |
| 9 Acceptance | previous Full | Paid retry pressure, missing receipts | Opt-in one-call B, conservative C, exact exits |

Warm time to first health/configuration response has a target under2 minutes after dependencies/services are ready; cold Docker/dependency/key setup is not measured. A full regression run is not "hello world" and its actual duration must be recorded separately. No invented under-five-minute claim is made for the test suite.

## Reference benchmarking and first-use roleplay

Primary sources checked: [Playwright webServer](https://playwright.dev/docs/test-webserver), [FastAPI dependency overrides](https://github.com/fastapi/fastapi/blob/master/docs/en/docs/advanced/testing-dependencies.md), [Python subprocess](https://docs.python.org/3/library/subprocess.html). These describe managed real test servers, explicit controlled dependencies and real process return codes. They publish no comparable ORBA onboarding timing here, so TTHW is unknown rather than fabricated; they are workflow references, not measured competitive rankings.

Illustrative roleplay, not execution: T+0 reads Verification and expects local safety; T+30s notices the npm-exec fallback; T+1m starts prerequisites; T+2m sees the previous Full/Core ambiguity; T+3m inspects a fixed JSON receipt but cannot associate it with the current dirty tree. Address all of these with explicit gates, prerequisite errors and source identity, not a hosted playground or another package manager.

## Pass1: getting started (8/10 specified)

Use verify.ps1 as the one local regression entrypoint; it must never require a model key or call the external invalid-key test. Configuration checking is a separate no-generation operation. Keep Docker/Node/Python prerequisites explicit; no auto-install/global repair promise or fabricated expected output is appropriate.

## Pass2: API/CLI (9/10 specified)

Use verify-live.ps1 with explicit AllowPaid, no automatic retry and a current passing Gate A prerequisite. Shared runner logic records native argument arrays and exits instead of duplicating status parsing across scripts. Legacy Full/Core compatibility must be explicit: Core can mean A; Full must not silently retain paid behavior.

## Pass3: errors/debugging (9/10 specified)

Trace1: upstream SDK504 currently returns provider_timeout; add origin and phase elapsed data, retain failed/no plan, give the user Check status or deliberate retry. Trace2: browser/proxy interruption currently becomes generic unavailable; distinguish the transport boundary, preserve UUID and block a new POST until recovery. Trace3: missing/stale gate proof must identify the absent/changed prerequisite and the exact command to rerun, with nonzero exit and no provider invocation.

Every error supplies problem/cause-known-or-unknown/fix, never raw provider bodies, credentials or private briefs. Timing must identify its measurement boundary; after-commit uncertainty is not a confirmed failed run. No verbose mode may dump environment secrets.

## Pass4: documentation (9/10 specified)

README should lead with install/start, Gate A, Gate B opt-in and stage summary in a short path; architecture carries lifecycle details and VERIFICATION carries actual results/history. All examples use the actual installed npm-exec fallback and root working directory. Update stage authority, controlled-provider boundaries and no-paid-call policy in AGENTS rather than leaving contradictory old instructions.

## Pass5: safe upgrades (9/10 specified)

Keep all Stage03 data and the owner's dirty tree, archive the previous report/evidence and never auto-commit. Gate A migration and schema drift must run against the validated test database, not Settings' development default. No new migration is planned for bounded diagnostic JSON, and no downgrade/reset shortcut is authorized.

## Pass6: environment/tooling (9/10 specified)

Real PostgreSQL remains mandatory and shared test DB ownership stays sequential. Playwright must refuse occupied test servers, and docs explain the checkout's shared Next dev lock. Python native subprocess handling needs fixed argument arrays and preserved return codes; Windows npm.cmd handling must not interpolate untrusted text or credentials.

## Pass7: ecosystem (7/10, intentionally local scope)

There is no established public community, hosted playground, support SLA or license claim to fabricate. Existing source/AGENTS/reproduction commands are the contributor interface for this owner-controlled local stage. Public distribution, plugins and production support remain the existing deferred TODOs, not hidden acceptance requirements.

## Pass8: measurement/feedback (9/10 specified)

Gate attempts record timestamps, command elapsed time, exact exits, code fingerprint and immutable artifact hashes. PM traces record only real phase measurements and available provider metadata; old runs are not backfilled. A one-call real browser flow is the measured acceptance vehicle; broader prompt-quality benchmarks, billing dashboards and telemetry remain outside this stage.

## Scorecard, consensus and implementation checklist

Scores: getting started8, CLI9, errors9, docs9, upgrade9, tooling9, ecosystem7, measurement9. They are review judgments, not passing test evidence. Independent in-host DX findings are in STAGE031_DX_VOICE.md; external-model consensus is N/A across the six CLI/getting-started/error/docs/upgrade/environment dimensions.

- [ ] X1 (P1, human2h / agent30m): normal local A, explicit live opt-in, clear nonzero prerequisite and child failures.
- [ ] X2 (P1, human2h / agent30m): guarded test-only migration/drift environment, secret scrubbing and per-attempt artifacts.
- [ ] X3 (P1, human2h / agent30m): current source/config/artifact validation and a summary that rejects stale/double-only proof.
- [ ] X4 (P1, human1h / agent20m): exact docs, historical evidence preservation and honest timing/recovery instructions.

No new public/distribution/retention TODO is needed: those scopes already exist in TODOS.md. All eight passes, nine journey stages, empathy narrative, timing target and checklist are written. Implementation and actual Gate A/B results remain outstanding.
