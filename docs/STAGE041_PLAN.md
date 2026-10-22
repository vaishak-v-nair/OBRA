# Stage04.1 — Browser navigation reliability and unpaid preflight

Authority: repair the failed browser setup, preserve all previous evidence and owner
work, run deterministic verification and five independent clean no-generation
preflights. No paid generation, model/configuration changes, commit or Stage05.

## Baseline and restore point

Stage03 checkpoint: `1aeb882cf9e788948df5ca5eac52e2a682a1f487`.
Stage04 prior source: `07bf0deb6c2a0cdaed19a4441619404fbda0f57674a0db9171cb3ea47628eab7`.
Prior A: 386 backend / 60 core / 33 PM / 33 Architect browser tests;15 commands.
Prior B failed waiting for Approve plan on Chat;0 model requests and0 Architect runs.
Historical reports/receipts remain unchanged. Intake hashes989 evidence files and
the owner's ignored environment files in an external, private audit directory:
`C:/Users/vaish/.gstack/projects/OBRA/stage041/20261021T185326Z`.

## What already exists / scope boundary

Reuse real registration/session/CSRF/workspace/project/PRD routes, the guarded
human-authored draft fixture and UI approval, existing API proxy and verifier.
There is no evidence that Gemini caused this local browser failure. No provider,
model, prompt, schema, budgets, DAG algorithms or paid retry policy changes belong
in this repair. Do not bypass UI approval with SQL.

## Investigation and implementation sequence

1. Preserve the failed step/snapshot and record a safe navigation timeline.
2. Reproduce the missing route synchronization using a controlled barrier around
   an actual persisted project response/navigation; no canned API response.
3. Await the exact created project URL, matching loaded project identity and
   selected workspace before reload. Inspect application guards before deciding
   whether an application fix is necessary.
4. Extract a shared Phase1 setup used by unpaid preflight and future live B. Load
   the exact authored PRD, approve its saved version/revision via UI, verify the
   actual API and independent SQL state, reload and reach Architecture.
5. Introduce a fail-closed generation boundary: Phase1 blocks all model-generation
   POSTs; only a future explicitly authorized Phase2 may forward one Architect
   POST. Phase3 reuses that architecture. No paid authorization in this task.
6. Add real-service navigation/restoration/stale-project/slow-response/approval/
   session-expiry/error tests. Controlled barriers/errors must be labeled and
   never stand in for live provider evidence. Keep all existing tests mandatory.
7. Run focused checks, complete Gate A, isolated regressions, five separate clean
   preflight runs and the isolated genuinely failing false-success experiment.
8. Save actual commands/exits, route/PRD/project identities, SQL observations,
   generation counters and new source fingerprint. Update current docs, preserve
   old reports and receipts. Stage04 remains PARTIAL; request fresh live authority.

## Architecture and observable milestones

```text
actual UI registration -> workspace -> project POST -> exact /projects/{id}
                                      |              + loaded ID/workspace fence
guarded human-authored draft ----------+-> Product Plan data -> UI approval
                                                            |-> API/SQL exact v/r
                                                            +-> reload same route
                                                            +-> Architect entry
Phase1 boundary: every PM/Architect generation POST blocked; provider dispatch0
Phase2 future authority: ONE Architect request -> existing live verification
Phase3: same architecture -> SQL/render/edit/approve/isolation (no generation)
```

## Failure registry and acceptance

| Failure | Required observation / response | Test |
|---|---|---|
| POST persisted but route not committed | Fail with expected/actual path; no reload shortcut | barrier reproduction and synchronized regression |
| Slow project response | Remain on requested route/loading; no wrong project/Chat | real response barrier |
| Workspace restoration pending | Protected project hidden until current session/workspace resolved | real session response barrier |
| Different project navigation | Never substitute prior project's protected content | two persisted projects |
| Draft missing/unavailable | Stop Phase1 with plan identity/state error | controlled transport failure with real DB |
| Expired/revoked session | No approval success or generation boundary crossing | real session revocation |
| Unauthorized approval | Backend denial and unchanged SQL approval state | real non-approver membership |
| Approval request failure | Draft remains, no source accepted, zero generation | controlled response error |
| Unexpected generation POST | Abort browser request; server test boundary rejects; fail receipt | explicit boundary probe |
| Preflight failure | Nonzero native command/receipt; no paid Phase2 | verifier-unit failure propagation |
| Stale/missing evidence | Never VERIFIED; new source invalidates prior A applicability | existing gate contract plus additions |

## Review and decision audit

Autoplan reviews run sequentially CEO -> Design -> DX -> Engineering. Installed
native gstack helper is unavailable; no global repair or external paid model probe.
Review voices are in-host, not an invented Claude/Codex cross-model consensus.
Implementation is already explicitly authorized by the owner's prompt; no redundant
plan approval is required. Paid generation is the explicit final stop boundary.

| ID | Phase | Decision | Reason |
|---|---|---|---|
| D1 | Intake | Preserve bytes and capture current source before edits | Historical failure must remain visible |
| D2 | Intake | Prove ordering with real-response barriers | A screenshot alone cannot establish the race |
| D3 | Intake | Separate Phase1 evidence from Gate B | Navigation/metadata are not live generation |
| D4 | CEO | HOLD SCOPE; require authoritative project/workspace identities and server-side generation denial | Existing AuthGate already fences account/workspace/path; do not invent an application bug |
| D5 | Investigation | Fix test synchronization, preserve application routing | Real Next response barrier reproduced POST201 on Chat followed by unsafe reload on Chat; exact-route navigation showed the persisted draft |
| D6 | Design | Add only invisible loaded project/workspace identity attributes; reuse accessible controls | Existing session/path remount handles stale state; no visual or session redesign |
| D7 | DX | Separate unpaid command and immutable receipts; fail on unexpected denied requests | A denied accidental generation must not be hidden by a green browser result |
| D8 | Engineering | Bind exact persisted source approval before opening future Phase2; retain partial milestone failures | Browser status and a screenshot alone do not establish PostgreSQL approval |

CEO review complete: [STAGE041_CEO.md](reviews/STAGE041_CEO.md). Independent
in-host review found no scope challenge. Two mandatory gaps incorporated above:
the rendered identity fence and a server-side boundary covering direct API calls.
External probe startup initially exited1 because Playwright resolves webServer cwd
relative to its external configuration. Explicit repository cwd is the justified
probe-only correction; the first command/log remain preserved.

The corrected probe exited0 (one actual browser test). Its sanitized timestamped
events show POST201 at18:57:55.900Z on `/`, persisted draft at18:57:59.631Z,
actual Next route response held200 at18:57:59.647Z, reload initiated on `/` at
18:57:59.649Z, then Chat remained. Opening the exact project route displayed the
same persisted draft at18:58:02.977Z. This proves the unsafe response/reload ordering
can cause the historical failure signature. The original run had no navigation
trace; its exact scheduling/latency cannot be reconstructed retrospectively.
The confirmed defect is a missing route-commit/identity wait in the test.

## No-generation preflight design

Use the real application factory, routes, security and PostgreSQL. A test-only
factory, guarded to the exact isolated database, denies PM/Architect generation
POSTs before dependencies and also installs dependency tripwires. It uses a clearly
labeled non-runtime configuration sentinel solely to inspect the enabled entry
control; it is not a real credential, provider response or readiness proof. The
owner's configuration and production factory remain unchanged. Browser context
guards cover pages/popups; direct API probes prove server denial. Independent
read-only SQL counts must show zero PM/Architect runs and zero architectures/tasks.
This is Phase1 proof only; future live B uses the production factory, genuine
configuration and the same setup helper, with a generation boundary closed until
all exact source/approval/reload checks complete.

Standalone unpaid commands get unique source-bound receipts and actual exit codes.
Five runs reset only guarded orba_test, with fresh accounts/projects/source IDs and
no test retries. Browser recordings contain only paths/status/identifiers/timestamps;
full network traces stay off because they capture authentication secrets.

## Status

- Inspection/intake: complete; missing test route synchronization is confirmed;
  exact historical scheduling remains unrecorded.
- Reviews: CEO, Design, DX and Engineering complete in that order; no unresolved
  scope/taste decision or owner challenge. Review artifacts are in docs/reviews.
- Reproduction: complete; confirmed missing test synchronization, historical exact
  scheduling unknown. No application routing/session refactor needed.
- Repair: shared exact-identity Phase1, phase boundary, isolated server denial,
  readonly SQL audit, unpaid command and additive tests implemented.
- Focused verification initially found a TypeScript inferred environment-union
  mismatch and a wrong NEW test assumption that PRD approval increments revision.
  Existing pm.py correctly binds the saved revision unchanged; corrected tests
  assert that exact revision, actor and timestamp. Initial logs remain preserved.
  Corrected focused backend40 passed; TypeScript and ESLint exited0.
- First full navigation development run exited1:9 passed/30 failed. Its first
  slow-response fixture held only one of two actual GETs; repaired to hold all
  matching responses. Later PostgreSQL exited255 and the Docker Linux engine
  became unavailable; initial snapshots/logs/receipts remain. No underlying Docker
  stop cause is claimed. Restored the existing Docker Desktop/test service without
  resets; recovered focused backend51 passed. Focused browser4 and boundary3 passed.
- Static review found missing-on-both-sides identity acceptance in the new proof
  parser. It now requires nonempty identities, positive integer versions/revisions
  and a64-character hash. Added11 meaningful parser regressions. Partial milestones
  are written even when boundary assertions fail. Direct API-context model POSTs
  are guarded too; service workers are blocked in these verification contexts.
- Full Gate A, isolated final navigation, five final-source preflights and final
  report: complete. Initial unpaid preflight passed on its earlier development
  source and is not acceptance for the final source. Frozen source:
  `f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb`.
  Gate A passed all16 commands:420 backend and60/33/33/39 browser tests, no skips or
  retries. Standalone navigation39 passed;5/5 clean unpaid preflights passed on
  matching source. Wrong-success experiment actually failed with pytest exit1;
  wrapper0 verifies that expected failure separately. Final independent SQL confirms
  approved v1/r1 and0 generation records. Gate C exited2/PARTIAL because new live B
  has not run; the old failed B remains unchanged.988 historical immutable files and
  credentials are intact; only latest-A control pointer advanced. No paid generation,
  commit/push/reset/discard or Stage05 occurred. See VERIFICATION_STAGE041.md.

## GSTACK REVIEW REPORT

| Review | Runs | Status | Findings absorbed |
|---|---:|---|---|
| CEO |1|HOLD SCOPE clear| Causal reproduction; exact identity fence; server boundary |
| Design |1|Scoped UI clear| Invisible identifiers, accessible existing controls, honest states |
| DX |1|Scoped workflow clear| Separate unpaid command, real exits, five independent receipts |
| Engineering |1|Architecture/test plan clear| Exact source SQL, partial failure milestones, no routing refactor |
| External model voice |0|NOT RUN| Native gstack helper unavailable; no paid probe or invented consensus |

VERDICT: scoped implementation authorized by the owner's Stage04.1 request.
This review is not execution evidence or live Architect proof. Gate A and five
no-generation runs remain required; fresh owner authority is required for paid B.

NO UNRESOLVED DECISIONS
