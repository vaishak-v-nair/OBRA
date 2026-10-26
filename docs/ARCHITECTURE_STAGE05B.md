# Stage05B scheduler and worker receipt protocol

This is a local control plane. No Implementation Agent, QA Agent, execution
sandbox, task-completion API or model request exists in this stage. All engineering
task snapshots retain `awaiting_executor` (or human cancellation). A handoff
acknowledgment confirms receipt, not work, useful progress or verified delivery.

## Persistence and source authority

The Stage05A immutable run/task/edge snapshots remain authoritative. New additive
migration `5a28ca29f8df` introduces worker identities, hashed credentials, one
scheduler coordination row, durable dispatch decisions, lease history, immutable
handoffs, claim request receipts and heartbeat receipts. No old source field or
project data is rewritten. Forward-only migration refuses a destructive downgrade.

New queue/claim/ack admission revalidates the exact approved architecture, its
current PRD agreement, canonical snapshot checksum, requirement coverage and DAG
using the existing services. Edges remain prerequisite -> dependent. Only roots
can be offered: no prerequisite has execution-completion evidence. Approval does
not satisfy dependencies. New approved source versions never rebase an old run.

## Transaction and selection policy

Every control-plane mutation locks PostgreSQL `scheduler_state(id=1)` first, then
workspace/project/run, then worker and lease state. Human cancellation takes the
same first lock. Database state, not an in-memory mutex, arbitrates separate API,
scheduler and operator processes. A partial unique index independently prohibits
more than one active (`claimed`/`acknowledged`) lease per task. Composite foreign
keys enforce same run/project/workspace ownership. DB triggers preserve snapshots,
append-only events/manifests/receipts, terminal leases and monotonic fencing.

This intentionally serializes short local transactions; it is not high-throughput
distributed scheduling or starvation-free fairness. Stable selection is priority
P0..P3, run creation time, task display order, task UUID. Polling is bounded, default
one tick and five-second interval for an explicitly longer runner. Queued+leased
reservations count toward global and per-run limits; worker capacity is checked
atomically at claim. Queued reservations are withdrawn if source or matching live
workers disappear, so stale reservations cannot pin capacity indefinitely.

`phase` preserves existing lock/statement/transaction deadlines (1/2/10seconds).
Database `clock_timestamp()` is sampled after lock acquisition. No network request
or worker operation runs inside a scheduler DB transaction. A policy is saved at
first use; incompatible process settings fail closed until aligned, rather than
silently changing existing lease semantics. Production policy administration is
not implemented.

## Worker security

Local operator provisioning is the only registry writer. A worker has one
workspace and optional narrower project scope, an authorized category capability
list, capacity1..4 and type `protocol_only`. Category matching only permits receipt
of a planning task; it does not certify implementation ability. Actual authenticated
activity, not provisioning or a fake background clock, establishes liveness.

Worker authentication uses `Authorization: Bearer` and a random256bit opaque
credential, independently of browser sessions. PostgreSQL stores SHA256 hashes only.
High-entropy random tokens do not use the user-password hashing policy. Credentials
expire and have versioned rotation/revocation. Rotation, disable and revocation fence
affected leases transactionally. Browser cookies never grant worker authority.
User inspection remains current membership-authorized; browser mutations retain
Origin/CSRF validation. Dedicated nonambient Bearer requests do not use cookie CSRF.

Provisioning writes once to an exclusive file outside the repository. POSIX mode
0600 or a Windows current-user-only file ACL is applied before writing secret bytes.
Do not place that file on an untrusted/shared filesystem. Secrets never appear in
normal CLI output, manifests, event metadata, user APIs or verification receipts.
A failed DB commit may leave a private file containing an unusable credential;
the command reports failure and the operator must use a fresh reviewed path.

## Lease, handoff and fencing contract

Dispatch: queued -> leased -> withdrawn (safe preack recovery), exhausted,
needs_reconciliation or cancelled. A withdrawn opportunity can be queued again
only by a bounded scheduler tick. Each claim increments its fencing epoch;
invalidation also advances it, so ownership epochs may contain gaps.

Lease: claimed -> acknowledged -> terminal expired/released/revoked/cancelled.
Claimed leases can also become terminal without acknowledgment. Terminal leases
never revive. Every protected mutation presents owning credential, lease UUID,
current positive epoch, manifest version and checksum. Foreign ownership returns
404; authenticated stale ownership returns409 and records an actual safe rejection
when its run is still active. Rejections are committed before returning the error.

`HandoffManifest` v1 is typed and server-derived: worker/scope/run/task identities,
exact approved architecture and PRD IDs/versions/revisions/hashes, snapshot hash,
task definition, acceptance criteria, traces, dependency context, capability,
lease/epoch and bounded deadlines. Its policy is `protocol_only_no_execution`.
Its SHA256 checksum covers sorted, compact UTF8 JSON of the typed wire object
excluding `checksum`. A checksum is content integrity, not an authentication
signature. The immutable initial deadline stays in the manifest; a renewed
current expiration is returned in the lease envelope. Publishing an HTTP response
only makes a handoff available; explicit acknowledgment establishes receipt.

Identical worker+requestUUID claims return the same active lease; changed inputs409.
A terminal receipt never silently creates a new lease. GET recovery dispatches
nothing. The protocol client saves only nonsecret request/lease references before
POST. Unknown outcomes require GET inspection and explicit `--retry-claim` for a
same-key repeat, never an automatic new UUID. A new lease attempt requires a
deliberate fresh state file after reviewing prior terminal ownership.

## Heartbeat and recovery policy

Defaults (bounded environment overrides through existing Settings):

|Variable|Default|Meaning|
|---|---:|---|
|ORBA_SCHEDULER_ACK_SECONDS|10|Unacknowledged receipt deadline|
|ORBA_SCHEDULER_LEASE_SECONDS|30|Current ownership duration|
|ORBA_SCHEDULER_MAX_LEASE_SECONDS|120|Hard lifetime from original claim|
|ORBA_SCHEDULER_HEARTBEAT_SECONDS|10|Minimum accepted renewal interval|
|ORBA_SCHEDULER_LIVENESS_SECONDS|60|Recent authenticated worker activity|
|ORBA_SCHEDULER_GLOBAL_CAPACITY|8|Queued+leased reservations|
|ORBA_SCHEDULER_RUN_CAPACITY|2|Reservations per run|
|ORBA_SCHEDULER_MAX_ATTEMPTS|3|Maximum unacknowledged claim attempts|
|ORBA_SCHEDULER_BATCH_SIZE|8|New opportunities per tick|

Acknowledgment precedes heartbeats. Each accepted renewal has a durable request
UUID receipt and one event; exact duplicates add neither renewal nor event.
Early renewals reject429. No renewal extends beyond the original hard maximum.
Expired, superseded, cancelled or revoked ownership cannot be revived by a late
heartbeat. Observed expiry is reconciled by scheduler ticks or protected worker
operations, not an uncontrolled scheduler loop in FastAPI. Read-only UI timestamps
are observations, not proof that a process remains alive.

Before acknowledgment, the protocol prohibits side effects, so bounded requeue is
allowed after expiry/release. After acknowledgment, expiry, release or revocation
requires reconciliation; no automatic redispatch and no inference of execution
failure or completion is safe. Stage05C human recovery controls are deferred.
Cancelling a run fences ownership atomically and preserves audit history.

## APIs and event semantics

Worker-only: GET `/api/v1/workers/me`, POST `/api/v1/workers/claim`, GET
`/api/v1/workers/claims/{request_id}` and POST
`/api/v1/workers/leases/{lease_id}/{acknowledge|heartbeat|release}`.
Typed bodies reject extra status/completion fields. There is no public provision,
event-writer, task-execution or task-completion endpoint.

User read-only: GET `/api/v1/projects/{project_id}/orchestration-runs/{run_id}/scheduler`.
Existing task/graph/events/history reads remain authoritative. The Execution Plan
shows actual queue, worker, lease, acknowledgment, expiry and reconciliation data.
Manual Refresh is available; no fabricated progress, terminal or agent activity.

Per-run ordered ledger events include dispatch_queued/withdrawn, lease_claimed,
handoff_available/acknowledged, lease_renewed/expired/released/revoked,
worker_lease_rejected/disabled, task_requires_reconciliation, dispatch_exhausted
and scheduler_recovered. The latter means a new actual scheduler process was
observed while queuing, not a claim of crash diagnosis. System events use system
actor plus a typed worker UUID, never a forged user identity. Every mutation and
event commits together; legacy events retain their exact original contract.

## Reproduction

From repository root (use a reviewed actual workspace/project UUID):

```powershell
docker compose -f infra/compose.yaml --profile test up -d --wait postgres test-postgres
uv sync --locked --directory apps/api
npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile
uv run --directory apps/api alembic upgrade head
uv run --directory apps/api uvicorn orba.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
# Separate terminal:
npm exec --yes --package=pnpm@12.14.0 -- pnpm dev
# Create and approve a PRD/architecture, then create an Execution Plan in the UI.
# Existing real AI actions still require the owner's explicit authorization.
# Separate terminal; an existing private directory outside this repository:
uv run --directory apps/api python -m scripts.worker_admin provision --workspace <UUID> --project <UUID> --name 'Protocol worker' --capability backend --credential-file C:\private\orba-worker.credential
uv run --directory apps/api python -m scripts.worker_client --credential-file C:\private\orba-worker.credential --state-file C:\private\orba-claim.json --run <RUN_UUID>
# That first bounded probe may find no work and establishes real activity.
uv run --directory apps/api python -m scripts.scheduler --ticks 1
uv run --directory apps/api python -m scripts.worker_client --credential-file C:\private\orba-worker.credential --state-file C:\private\orba-claim.json --run <RUN_UUID> --cycles 3 --interval 10
# Optional finite runner, independent of the browser:
uv run --directory apps/api python -m scripts.scheduler --ticks 60 --interval 5
```

Rotation/revocation use `scripts.worker_admin rotate --worker <UUID>
--credential-file <NEW_PRIVATE_PATH>`, `revoke --worker <UUID>` or `disable --worker
<UUID>`. Never put a credential value on a command line. A credential file must not
be reused/overwritten. The client only speaks loopback HTTP for this local scope;
remote production workers need TLS/mTLS or equivalent reviewed transport, dedicated
secret distribution, operational policy management and finer DB-role boundaries.

## Verification and future executors

Normal `scripts/verify.ps1` is new Stage05B Gate A and retains all earlier commands.
Install the pinned Playwright engines first with `pnpm --filter @orba/web exec
playwright install chromium webkit`. Earlier device regressions use Chromium
emulation; the added scheduler mobile/tablet projects use their declared WebKit
engine. Neither device emulation nor WebKit on Windows proves native iOS behavior.
`scripts/verify-scheduler-local.ps1` is independent local Gate B: actual services,
scheduler/client processes, restart, expiration, scoped auth, SQL, browser and
strict proof reconciliation. It uses authored test sources approved through real
UI, never model or executor simulation. Historical Stage05A proof-v2 stays strict.
New proof reconciles real SQL task/dispatch/lease/credential/event records, canonical
checksums and all identities; missing values or bool/int coercion cannot pass.

Database leases do **not** guarantee exactly-once external effects. A future Stage06
executor must enforce ownership/epoch at each relevant resource boundary and submit
artifacts for independent evidence acceptance. No such interface is exposed now.
Overall Stage05 remains IN PROGRESS; Stage05C/D/06 do not start automatically.

PostgreSQL references: [row locking](https://www.postgresql.org/docs/18/explicit-locking.html),
[partial indexes](https://www.postgresql.org/docs/18/indexes-partial.html).


## Credential publication authorization

A real PostgreSQL regression exposed an initially valid credential expiring while
a claim waited for the workspace row. Admission now reauthenticates after the
run/source locks. Worker and credential rows are locked and reloaded in that
order;early authentication does not dirty a worker before workspace locking.
Post-lock scope and capability checks use the current registered identity.

All tentative lease,manifest,claim-receipt,event and activity writes are flushed
before a final publication guard. That guard reloads the exact credential under
row locks and validates clock_timestamp(),revocation,current credential version
and worker enablement. A failed check raises the existing safe401 and rolls back
the whole transaction,including counters and fencing epochs. Replay,recovery,
acknowledgment and heartbeat paths retain equivalent final guards;ownership
deadlines are checked without allowing a late heartbeat to revive ownership.
No ORM mutation follows the guard before commit.

The final database authorization check is the publication linearization point.
It does not promise validity at the later instant HTTP delivery finishes. Every
subsequent protected operation authenticates and fences ownership again. Normal
operator revoke/disable/rotate operations serialize on coordination. Tests race
those actual operations at that lock;scope fields remain database-immutable,so
no artificial mutable-scope administration endpoint is introduced.

See VERIFICATION_STAGE05B_CREDENTIAL_REPAIR.md for genuine pre-fix evidence,new
PostgreSQL regression results and the required fresh A/B/C receipts. Historical
acceptance against4bfcc3ec cannot certify this changed implementation.
