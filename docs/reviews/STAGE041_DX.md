# Stage04.1 developer experience review

Independent in-host DX review of `docs/STAGE041_PLAN.md`, the existing Architect
verifier, live Playwright configuration, live test and shared browser helpers.
Mode: DX POLISH. Persona: the local Windows maintainer reproducing a failed paid
verification safely. No external calls, model probes or cross-model consensus.
Installed gstack helper is unavailable; review is local and does not certify tests.

## Journey and acceptance target

The useful moment is an actual approved, persisted PRD on its exact project route,
followed by the Architect entry point, with independently verified zero generation.
Target: one clearly named unpaid PowerShell command produces a source-bound receipt;
five runs produce five separate clean attempts. Execution duration is not estimated
as a verified result. This is repair of a verification workflow, not a new SDK or
community product. No competitor investigation is needed for this bounded repair.

## Eight review passes

| Pass | Before / planned target | Findings and required implementation |
|---|---|---|
| 1. Getting started | 5 / 9 | Add a standalone unpaid command, such as `pwsh -NoProfile -File scripts/verify-architect-preflight.ps1`, with a documented default of one run and an explicit bounded five-run invocation. No credential or paid opt-in is necessary. List PostgreSQL, uv, Node and pnpm prerequisites and the guarded database before execution. |
| 2. API / CLI design | 5 / 9 | Keep unpaid preflight distinct from `verify-architect-live.ps1 -AllowPaid`. Share Phase1 browser setup rather than maintaining divergent setup copies. A successful preflight reports `PREFLIGHT PASS`, never Gate B PASS. Reject unsupported counts and preserve native child exits. |
| 3. Errors / debugging | 4 / 9 | Replace ambiguous late approval timeouts with stage-specific expected and actual route, project ID, workspace ID, plan ID/version/revision, HTTP status and elapsed time. Save partial milestones even when setup fails. Do not include URL secrets, headers, tokens, credentials or arbitrary API response bodies. |
| 4. Documentation / learning | 6 / 9 | Put the unpaid command, exact five-run command, receipt paths and zero-generation meaning beside the future paid command. State that a credential-free sentinel test configuration proves navigation and persistence only; it does not establish provider readiness. Preserve the historical failed B report unchanged. |
| 5. Upgrade / migration | 9 / 9 | No database migration, authentication contract or model profile change is needed. Add mandatory test identities; retain every old identity and receipt. Any source/test/script change invalidates earlier source applicability and requires a new Gate A receipt. No issues found beyond these existing plan obligations. |
| 6. Environment / tooling | 6 / 9 | Use native PowerShell exit propagation and the repository's existing command runner/pinned pnpm approach. Serialize clean runs against guarded `orba_test`, never backend and browser suites together. Scope child environment changes and restore them. A test-only server boundary must deny both browser and direct API generation before admission/SDK dispatch; no production fake-provider switch. |
| 7. Ecosystem / cost transparency | 9 / 9 | No community, plugin or release surface is introduced. Document zero paid calls and separate next-call authorization. Do not imply a metadata response or sentinel configuration verifies Gemini. No additional scope is needed. |
| 8. Measurement / feedback | 4 / 9 | Capture each of five attempts independently, including failed attempts: source fingerprint, start/end, exact command/exit, phase milestones, safe route timeline, project/PRD IDs, independent SQL approval state and generation counters. Do not aggregate later success over an earlier failure or silently rerun failures. |

Scores are plan assessments and targets, not measured post-implementation ratings.

## Three diagnostic paths traced

1. Project creation currently waits for the POST response, then the test reloads
   without asserting the route. Expected diagnostic: `project-navigation` with
   expected `/projects/{created-id}`, actual path, rendered identity and selected
   workspace. The helper must stop before approval if any identity differs.
2. PRD loading or approval failure currently becomes a missing-control timeout.
   Expected diagnostic: `draft-load` or `approval-persistence`, exact saved
   version/revision and safe HTTP outcome. A rejected approval must leave the
   SQL record draft and must not proceed to generation readiness.
3. A mistaken generation call during preflight must be blocked by both browser
   interception and the guarded test-only server boundary. Record the attempted
   request and fail the command even though dispatch was prevented; zero paid
   dispatch alone cannot excuse an unexpected generation attempt.

## Required evidence contract

Each clean attempt owns a new evidence directory and receipt. Bind it to the
source manifest captured before execution and confirm the source afterward. Store
commands, true exits, test report identity, phase status and the independent SQL
audit as hashed artifacts. Database cleanup is restricted to `orba_test`. Its
generation/run counts must be zero before and after setup, while the final PRD
has the exact authorized approver/version/revision. The five-run aggregate points
to all five receipts and passes only if every required attempt passes.

The unpaid test may use a nonsecret sentinel solely in an explicitly labeled,
guarded test factory, with unconditional generation denial. It must not read the
owner credential, dispatch readiness metadata, supply model output or enter the
paid verification class. Future live B uses the production app and real configured
provider, with its own fresh authority and receipt; it cannot reuse this test
factory as live evidence.

## Review disposition

Proceed within the already authorized repair. The plan covers the eight passes;
the concrete CLI, diagnostics and receipt requirements above should be carried
into Engineering review and implementation tests. No new owner decision or paid
operation is required. Engineering review is next; post-implementation review must
compare these targets with actual command receipts and five-run observations.

NO UNRESOLVED DECISIONS
