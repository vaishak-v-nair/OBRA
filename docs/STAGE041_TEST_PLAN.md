# ORBA Stage04.1 test plan

Reviewed against docs/STAGE041_PLAN.md and existing production routing/session,
live Architect setup, test factories and stage verification code. All new tests
are pending until actually executed. No paid generation is permitted.

## Source and observed baseline

Before repair:07bf0deb6c2a0cdaed19a4441619404fbda0f57674a0db9171cb3ea47628eab7.
Historical live B timed out waiting for Approve plan while Chat remained visible;
database had one draft PRD and zero Architect runs. A real Next response barrier
reproduced the missing route-wait signature. Do not rewrite old evidence.

## Proposed branch map

1. Shared project helper waits successful real POST, extracts actual UUID, awaits
   exact `/projects/{id}`, loaded DOM project/workspace IDs and displayed content.
   Test success; slow real response held by deferred barrier; wrong route/identity
   rejection; confirmed navigation followed immediately by reload.
2. Shared Phase1 helper authors a clearly labeled human draft via guarded fixture.
   Fetch exact plan; assert draft ID/version/revision; real UI review/confirmation;
   await real approval HTTP response and assert saved exact version/revision. Read
   independent SQL via a fresh READ ONLY session. Assert approver/time/state.
3. Reload only after route/data approval fences; wait current session/workspace;
   refetch exact PRD and source binding; verify same IDs/hash/approved state;
   expose Architecture action. Never click generation in unpaid mode.
4. Error branches: missing draft, controlled real transport503, expired real
   session, unauthorized member, failed approval, wrong version. Assert no source
   accepted, no new run, no approval fabrication, bounded actionable failure.
5. BrowserContext boundary starts Phase1 CLOSED. PM and Architect POSTs from
   ordinary page/popup rejected before dispatch. Direct API is guarded at test
   server before dependencies. Model dependency tripwires must never be invoked.
   Unit-test explicit authorized phase admits only one Architect POST, never PM;
   second request denied; Phase3 closed. These are not live-model evidence.
6. Standalone unpaid CLI: exact isolated DB guard; source fingerprint; actual child
   argv/exit; missing proof, invalid counters, malformed report, skipped/retried
   report and nonzero child must reject PASS. No latest-B success update. Receipt
   writing/cleanup errors stay failures, and already recorded outcomes persist.

## Browser cases, actual services

Suggested suite apps/web/tests-architect-preflight/navigation.spec.ts, three
existing viewports. Shared helper under apps/web/tests-architect-live or common
tests helper module; unpaid preflight config separate from paid live config.

| Case | Required assertions |
|---|---|
| Exact navigation and immediate reload | URL/DOM/API/SQL same project and workspace |
| Slow successful project GET | Correct route/loading then correct details; no Chat |
| Delayed workspace restoration | Protected details withheld, then exact selected workspace |
| Two same-workspace projects | No stale first project rendered as second |
| Draft approval and reload | Exact seeded ID/v/r; actual approver/time; SQL approved |
| Member without approval privilege | UI/API denial; SQL remains draft |
| Expired/revoked real session | Session guard, no success or generation |
| Draft load failure | Helpful error; cannot approve/generate from absent data |
| Approval failure | Draft and brief preserved; no approved source accepted |
| Browser generation boundary | Attempt recorded/blocked, forwarded0 |
| Direct API generation boundary | Explicit denial before dependency/SDK; SQL runs0 |

Controlled barriers fetch and delay real responses. Any deliberately replaced
failure response is labeled controlled transport failure, not a provider response.
Use no arbitrary sleep or automatic test retry. Use path/status/UUID/timestamp
events only; no full trace/header/token/password capture.

## Backend/verifier additions

Suggested tests/test_architect_preflight.py: exact guarded DSN rejects other DBs;
test factory does not load dotenv keys; direct generation POST denied before model
dependency; dependency tripwire fails if called; no run/plan/task persisted;
read-only audit identifies exact approved source and zero generated records.
Extend verifier unit coverage with synthetic child/report inputs clearly labeled
unit evidence. Verify failure propagation, non-live classification, source changes
and invalid/missing reports. Preserve existing graph/security/provider tests.

## Execution order and receipts

1. Focused lint/typecheck/backend and navigation suite; fix genuine defects while
   recording initial failures. No backend/browser overlap against orba_test.
2. Run unchanged-command full Gate A after final implementation; all previous
   identities plus new cases mandatory. Record actual counts and all exits.
3. Run isolated navigation regressions independently after Gate A.
4. Run exactly five clean standalone desktop Phase1 invocations sequentially;
   each owns a new receipt and reset of guarded orba_test only. Fresh user,
   workspace, project and PRD IDs every time. No failed run hidden by a later pass.
5. Run isolated intentionally incorrect Architect success assertion; preserve
   genuine pytest exit1 separately. It is never a mandatory-suite passing test.
6. Audit all five proofs: project/plan/source binding; actual API/SQL approval;
   route/reload; generation attempt counters zero in happy path; provider dispatch0;
   Architect runs/architectures/tasks/dependencies0; new fingerprint consistent.
7. Preserve historical immutable hashes, keys and working tree. Gate C stays
   PARTIAL because real-model Architect Gate B has not passed for changed source.

## Acceptance

Implementation refinement: guard BrowserContext.request.fetch as well as page/
popup traffic; the installed Playwright post method delegates to fetch. A direct
API-request probe must be denied client-side with zero forwarded requests. An
independent request fixture separately proves the test SERVER denies model POSTs.
Service workers are blocked in these verification contexts. Neither test is live
provider evidence. Hold every matching response during barrier tests, including
development-effect duplicate GETs; record each actual held response. Preserve
partial milestone proofs in finally even when setup or boundary assertions fail.

All mandatory local checks pass without skips/retries. Five of five independent
preflights pass or report each actual failure. No paid model request. No dummy
architecture, no DB approval shortcut, no historical receipt overwrite. Request
fresh owner authorization for the next explicit one-request live B only after
Gate A passes on the new source fingerprint.
