# Stage04.1 Engineering review

Scope: browser navigation synchronization, reusable unpaid Architect Phase1,
generation boundary and evidence. Reviewed after CEO, Design and DX. This is an
independent in-host review, not cross-model or live-provider verification. No
provider call was made. Native gstack helpers are unavailable; no global repair,
telemetry or external model probe was attempted.

## Architecture review

The proposed boundary is appropriate: reuse production authentication, project,
PRD and approval services; isolate the generation-denial factory to tests and the
exact guarded `orba_test` DSN. No new production authentication or provider service
is justified. No migration, dependency, distribution artifact or deployment is
needed. Existing production routing stays authoritative.

Confirmed P1, confidence10/10: `apps/web/tests-architect-live/architect-live.spec.ts:23-27`
awaits `const project=await(await creating).json()` and then executes
`await page.reload();await page.getByRole("button",{name:"Approve plan",exact:true}).click()`.
There is no exact URL or loaded project identity assertion between creation and
reload. `project-form.tsx` awaits the browser's response processing before its
`router.push`; the independent test response observer does not establish that
navigation committed. The parent's real-response barrier probe demonstrates the
same Chat/reload failure signature. Fix the ordering in the test helper, not with
sleeps or blanket timeout increases. The original historical scheduling is unknown
because that run did not record a route trace.

Do not infer a stale-content application bug merely from detail-page local state.
`apps/web/src/components/session.tsx:72-73` explicitly fences it:
`return <div key={`${user?.id ?? "guest"}:${workspace?.id ?? "none"}:${path}`}>{content}</div>;`.
The route, account and workspace remount protected children. Verify slow state
restoration and same-workspace project changes before changing this mechanism.

Mandatory safety invariant: Phase1 must reject PM and Architect generation at both
BrowserContext and test-server boundaries. A page-only route misses popups and
direct `APIRequestContext` requests. The current live test's `await page.route(...)`
also allows one Architect POST before prerequisite checks have completed. The new
shared boundary must begin CLOSED, become generation-authorized only after all
Phase1 checks and explicit live opt-in, forward at most one Architect POST, then
remain CLOSED for post-generation checks. Test-server denial precedes route
dependencies; dependency tripwires make a bypass fail loudly. A sentinel enables
control inspection only, and must never count as credential/model readiness.

```text
real registration/session -> workspace -> real project POST -> URL/id/workspace fence
  -> authored draft fixture -> loaded exact draft -> UI confirmation -> actual API
  -> independent READ ONLY SQL v/r/actor/time -> exact route reload -> same approved PRD
  -> source binding -> Architecture entry point -> STOP (unpaid)

browser context: CLOSED --[all prerequisites + fresh paid opt-in]--> ONE Architect POST
test-only server: generation POST -> explicit denial before model/session dependencies
any error: receipt FAIL + reached milestone + counters; never advance phase
```

## Code quality review

One helper must own Phase1 for both unpaid and live flows. Do not create a second
copy of source-authoring/approval/navigation logic. Extract the command runner,
exact route assertion, generation budget/phase gate and safe timeline into focused
test helpers. Keep the production component change limited to invisible loaded
project/workspace identity attributes. Do not use a test marker as authorization.

Assertions must check API HTTP status before reading content. Bind plan ID,
version, revision, content hash, actor and state to the seeded draft and API/SQL
result, rather than merely asserting a visible `approved` string. Do not silently
reload around failed approval. Preserve exceptions while flushing partial proof in
`finally`; failure of receipt writing must also fail the command. Use strict
test-only database guards before cleanup or SQL; no development database access.

Logging must be allowlisted paths/status/IDs/times and safe errors. Full browser
network traces and headers can contain cookies, CSRF tokens and test passwords;
leave them off. Historical evidence remains immutable. New receipts must bind the
new helper/config/test files in the source fingerprint and must not set live B PASS.

## Test review

Detected frameworks: pytest with real PostgreSQL, Playwright with actual Next.js
and FastAPI. Existing verifier unit tests already test native child failures and
false certification. New preflight branches require additive tests; prior mandatory
test identities remain required.

```text
CODE PATH / USER FLOW                                    TEST REQUIREMENT
create -> POST201 -> route not yet committed              [E2E] barrier reproduction
exact URL + loaded project + workspace -> reload          [E2E] persisted identity
slow real project GET / session workspace restoration     [E2E] no Chat or wrong data
second project navigation -> old response completion      [E2E] correct identity only
human draft -> exact UI approval -> SQL -> reload         [E2E] same plan/v/r/approver
draft GET fails / approval POST fails                     [E2E] stop, draft unchanged
expired session / unauthorized member approval            [E2E] denied, no false success
context PM/Architect POST / popup                         [E2E] deny, zero forwarded
direct API generation POST                               [integration] server rejects
provider dependency bypass                               [unit/integration] tripwire
closed -> authorized one request -> second denied         [unit] exact phase budget
CLI child failure / missing proof / bad counters          [unit] nonzero + FAIL receipt
five fresh independent resets/accounts/projects           [E2E] five distinct receipts
controlled failed Architect run expected succeeded        [experiment] genuine pytest1
```

All additions are requirements until executed, not passing evidence. No new LLM
eval is appropriate because model, prompt and output contract are unchanged and
paid generation is prohibited. The actual live Architect gate remains unverified.
The detailed branch map and execution plan are in the external test-plan artifact.

## Performance review

No production performance regression is expected from data attributes or test
helpers. Keep one browser worker and zero retries. Five standalone runs are five
clean observations, not retrying a failed test into a pass. Controlled slow responses
must use explicit deferred barriers around real responses, not sleeps. A bounded
Playwright assertion may time out with an actionable expected/current route and
last safe milestone; do not expand all deadlines. Avoid per-poll shell/SQL process
launches: one independent SQL audit at persisted milestones is sufficient.

## Error and rescue registry

| Integration | Realistic failure | Required behavior |
|---|---|---|
| Browser to project API | POST persists before navigation | Wait exact route/id; fail before reload if absent |
| Session/workspace restoration | Response arrives late or401 | Protected content fenced; stop before approval |
| Draft load |404/503/network error | No approval or phase transition; useful failing milestone |
| Approval |403/401/503/stale revision | Keep draft; SQL confirms unchanged approval |
| Independent SQL | Connection fails or identity differs | Fail preflight; do not substitute screenshot evidence |
| Generation boundary | Unexpected POST from page/popup/API | Reject before provider; count attempted/blocked; fail |
| CLI/report parsing | Child nonzero, missing report or skipped test | Preserve native code and FAIL/BLOCKED; no PASS |
| Gate evidence | Old fingerprint or controlled proof reused | Reject VERIFIED; retain PARTIAL |

## Completion

Architecture, code quality, tests and performance reviewed. Three mandatory gaps
in the old path are addressed by the proposed plan: route-commit fencing,
phase-aware context/server denial, and exact independent approval evidence.
No new owner decision or scope change is required. Proceed with the approved
small repair and additive verification. Implementation/testing remain pending.

NO UNRESOLVED DECISIONS
