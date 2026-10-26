# Stage05B credential-publication repair

Status: **VERIFIED against fresh Gate A/B/C,2026-10-26.** Overall Stage05 remains IN PROGRESS.
No executor, paid model request, Git commit or later-stage work is authorized.

## Confirmed pre-repair race

The [actual pre-repair PostgreSQL reproduction](evidence/stage05b/20261026T144623Z-credential-prefixed-reproduction-597e6a69/reproduction.json)
ran before changing production scheduler code. The credential was valid when the
claim started at14:46:29.021906UTC. PostgreSQL observed claim PID5800 blocked by
holder PID5799 at14:46:29.089282. The credential expired at14:46:29.715446;
the independent workspace lock was released at14:46:29.719247.

The real API returned **201** after expiry. Independent SQL showed one lease,
one handoff, one claim receipt, attempts/fencing epoch advanced0->1, and two new
publication events. Both engineering tasks remained awaiting_executor; no code
was executed. The repaired-behavior assertion genuinely failed with pytest exit1.
Its recording wrapper exited0 only after confirming that actual failure plus201
and contention evidence; this is never a passing security test.

Cause:the claim authenticated after coordination, then could wait on workspace/
project/run locks. It sampled fresh database time after that wait but did not
apply it to credential expiration before lease publication. The old A/B/C results
against4bfcc3ec remain immutable historical records; they did not cover this case.

## Repair and authorization boundary

The implementation reuses trusted credential validation and short PostgreSQL
transactions. Initial authentication does not dirty/implicitly lock a worker
before workspace locking. After run/source locks, worker and credential rows are
locked/reloaded in that order, and expiry, revocation, enablement, credential
version, scope and capability are checked again before new admission.

Tentative lease/handoff/receipt/event/activity writes are flushed before a final
fresh-clock authorization guard. The guard uses clock_timestamp(), never the
transaction-start timestamp. Invalid credentials raise the existing safe401 and
roll back all tentative records, dispatch counters and fencing changes. No ORM
mutation follows the guard before commit. Equivalent final guards protect claim
replay, saved-claim recovery and lease acknowledgment/heartbeat/release paths.
Ownership deadlines are also checked before accepting a claim/acknowledgment/
heartbeat; expired ownership cannot be revived by processing delay.

The final database guard is the publication linearization point. Later HTTP
arrival is not that instant. Every subsequent protected request authenticates
again. Global coordination serializes legitimate operator revoke/disable/rotate;
regressions exercise those actual operations while the claimant waits there.
Workspace/project worker scope is immutable in PostgreSQL. Tests preserve that
constraint and verify foreign-scope rejection rather than inventing a mutable
scope-administration endpoint or disabling an audit trigger.

## Focused verification

The [focused source-bound command](evidence/stage05b/20261026T145933Z-credential-focused-ed413510/diagnostic.json)
exited0: **69 passed**, zero skips or retries. This includes16 new credential
cases plus existing protocol/recovery/security cases. One installed Google SDK
Python deprecation warning remains; it is not a skipped test or model invocation.

New cases cover real workspace, worker-row, credential-row and task-FK publication
waits crossing actual DB expiry; revocation, disablement and rotation while waiting
on coordination; expired-before-entry rejection; a valid worker unaffected by
an unrelated expired credential; immutable workspace/project scope and foreign
worker rejection; and expiry during replay, GET recovery, acknowledgment, release
and heartbeat. The tests use real PostgreSQL, real hashed credentials and actual
API/service code. No controlled clock or successful-authentication double is used.
Historical issuance fixtures use a normal60second credential lifetime with a
past creation timestamp, providing short actual remaining lifetimes without
weakening runtime provisioning limits.

The repaired [workspace race](evidence/stage05b/20261026T145933Z-credential-focused-ed413510/workspace-race.json)
returned401. Its independent before/after SQL snapshots match exactly: queued
dispatch, zero counters/epoch, zero lease/handoff/claim and no publication event.
The [publication FK wait](evidence/stage05b/20261026T145933Z-credential-focused-ed413510/task_fk-race.json)
also returned401 with identical SQL state, proving the final guard rolls back
writes even when a later insertion waits after the post-lock authentication.

All776 previous backend identities remain mandatory;16 additional identities
are pinned for792 expected backend cases. Gate A retains all201 browser cases
and18 native commands. It must also retain all12 actual credential-race diagnostic
artifacts. Old passing evidence cannot certify changed implementation code.

## Fresh acceptance evidence

Source: `d47cf1fe3478c7877dd7cda342e56c94fdc16a517be7964f5cfefd4244f20b6f`
(243 source files); unchanged between each gate's start and end. The prior
`4bfcc3ec0d903cfedcd7addaca7e06c4287467a4ed1d1e79d33524a446d2538d`
receipts stay historical and unchanged.

- [Gate A](evidence/stage05b/20261026T150514Z-A-491fc5da/receipt.json): PASS,
  792 backend and201 browser tests;18 native commands exited0. Browser split:
  core60,PM controlled33,Architect controlled33,navigation39,orchestration21,
  scheduler15. No skips,xfails,retries or flaky acceptance.
- [Local Gate B](evidence/stage05b/20261026T154518Z-B-06240af9/receipt.json): PASS,
  1 actual scheduler/worker-protocol browser flow,94.168seconds native duration.
  [Strict proof](evidence/stage05b/20261026T154518Z-B-06240af9/scheduler-proof.json)
  contains actual authenticated API,process,SQL,heartbeat,restart,reconciliation,
  reload and isolation evidence. This is control-plane behavior,never code execution.
- [Gate C](evidence/stage05b/summary-a2a54ead40ed40f0b42b6d3964d1bc37.json):
  VERIFIED,matching source and policy,A/B receipt hashes validated. Overall05
  remains IN PROGRESS;model_generation_requests=0,execution_performed=false.

Actual commands from the repository root:

```powershell
pwsh -NoProfile -File scripts/verify.ps1
pwsh -NoProfile -File scripts/verify-scheduler-local.ps1
uv run --directory apps/api python -m scripts.scheduler_verification C
```

Each outer command exited0,without automatic retry. Gate A's database startup,
Python frozen lock,frontend frozen lock,peer checks,migration,schema drift,
backend,Ruff,formatting,TypeScript,ESLint,production build and all6 browser groups
exited0. The installed Google SDK produced one Python deprecation warning;no
model request was made. No migration or dependency change was needed for this repair.

## Isolated negative experiments

The [fresh experiment record](evidence/stage05b/20261026T150454Z-credential-experiments-d8477729/experiment.json)
binds the current source and actual command logs/XML. The unchanged handoff
completion assertion genuinely failed with pytest exit1. The new deliberately
incorrect expired-credential assertion expected201 but observed401 and genuinely
failed with pytest exit1. An empty proof was rejected by the real validator CLI,
exit1. These are isolated experiments outside normal passing test discovery;
the wrapper's exit0 only confirms their expected native failures.

## Checkpoint boundary and limitations

Checkpoint preparation resumes only after these fresh gates. No Git commit is
authorized;an exact staged-file review,secret scan,CRLF-aware whitespace check
and historical-artifact audit must precede a separate commit request. Historical
receipts,credentials and90excluded files must stay unchanged. Database admission
and fencing do not guarantee exactly-once external execution. No coding/QA
executor or reconciliation UI has been introduced;no task became completed.
