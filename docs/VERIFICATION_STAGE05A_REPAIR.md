# Stage05A evidence-validator repair

The checkpoint audit found a real evidence-validation defect. The old
`live_local_proof` compared absent graph/hash/source values with `dict.get`,
allowing `None == None`. Its missing-task loop used `any([])`, so a claimed
count could substitute for absent SQL records. An isolated in-memory reproduction
called the full receipt validator and confirmed acceptance. Only exact proof and
receipt reads plus their matching synthetic digest were doubled. Actual saved
historical B is complete; no historical proof or receipt was changed.

Historical fingerprint:
`daff99b31e5db1156011058eed168e0c04136bb840dcb75f7de2d928fe7d3f62`.
Its historical PASS/PASS/VERIFIED results remain recorded in
[Stage05A verification](VERIFICATION_STAGE05A.md). They do not certify repaired
source, and the old validator did not perform the new checks described here.

## Repair contract

`scripts/orchestration_proof.py` is an evidence-only Pydantic contract. Required
UUIDs, positive revisions, strict integer counters, lower-case 64-hex checksums,
aware timestamps and complete record structures reject missing/null/empty/wrong
types. Boolean values cannot stand in for integer counts or revisions. Literal
coercion and text normalization in reused document schemas cannot make raw
contradictory task/source data agree. Diagnostics show safe field paths without
printing supplied values, unknown key text, credentials or provider bodies.

The guarded native SQL inspector opens an independent PostgreSQL connection and
a read-only repeatable-read transaction. It reads the run, actual task definitions
and IDs, dependency IDs/endpoints, complete lifecycle events and saved canonical
source snapshot. It recalculates SHA-256 and reconstructs relational projections.
Mandatory failures use explicit exceptions and remain active under Python `-O`.

The production verifier requires at least one SQL task, reconciles actual API/SQL
task and source identities, checks counts/uniqueness/ownership/order, recomputes the
DAG, validates endpoint references and compares graph membership exactly. A valid
graph may have zero edges. Raw canonical source is rehashed independently
of claimed flags; approved architecture/PRD IDs, versions, revisions, document
hashes and approvals must agree. Events must be the persisted creation and
awaiting-executor transitions with exact run/project/actor/revision/state bindings.
No task may claim execution or verified completion. Reload SQL must match exactly.

Gate receipts bind proof-version2 and the typed proof-schema hash as well as the
existing source/command/artifact/time/auth/zero-generation controls. Contract,
source and result comparisons are type-sensitive JSON comparisons. Native exits
cannot be booleans. This adds no endpoint, migration, executor, scheduler, model
request, dependency or automatic retry.

## Tests and reproduction

Run sequentially from the repository root:

```powershell
uv run --directory apps/api pytest -q tests/test_orchestration_proof.py tests/test_orchestration_verification.py
pwsh -NoProfile -File scripts/verify.ps1
pwsh -NoProfile -File scripts/verify-orchestration-local.ps1
uv run --directory apps/api python -m scripts.orchestration_verification C
uv run --directory apps/api python -m scripts.orchestration_false_success
```

Unit mutation fixtures are explicitly synthetic inputs, never actual browser/SQL
execution evidence. They exercise the actual helper and full receipt validator
with matching invalid proof/hash/results envelopes. Positive PostgreSQL tests
use real authenticated application initialization and separate native SQL reads.
A narrow empty-task-query double proves the SQL inspector rejects absent rows;
that double is not used for positive integration or local Gate B. All previous
478 backend identities remain; 205 adversarial/integration cases are added, for
683 mandatory backend cases. All previous browser identities remain mandatory.

The isolated completion experiment must retain actual pytest exit1. A separate
empty-proof command must exit nonzero. Neither is a passing engineering execution
test, and neither is included as a mandatory green suite failure.

## Verification status

The repaired implementation is **VERIFIED** on2026-10-23. Fresh Gate A, independent
real local Gate B and Gate C all passed against the same205-file source:

`6c21f5d8534403c93be7feaa9b232aa57e62a6686d49084bc09dbd808e56e705`

| Gate | Actual result | Native exit | Immutable evidence |
|---|---|---:|---|
| A |683 backend;60 core,33 PM controlled,33 Architect controlled,39 navigation,21 orchestration browser cases;all17 commands |0| [A receipt](evidence/stage05a/20261023T092004Z-A-91210a2f/receipt.json) |
| B |1 real local browser/auth/API/PostgreSQL flow;complete proof-v2 accepted |0| [B receipt](evidence/stage05a/20261023T094846Z-B-6bdddf00/receipt.json) |
| C |Applicable matching A/B source and contract;VERIFIED |0| [C summary](evidence/stage05a/summary-163ce3ae0b4d438699a611a8e459660a.json) |

Zero skips, xfails, flaky results or automatic retries occurred. The targeted
verifier suite passed218 cases with exit0 before Gate A. Initial development Ruff
checks exited1 on style/import issues; explicit corrections passed final lint and
format checks. No assertion, permission boundary or test identity was weakened.
Exact observed development results and native logs/commands are bound by
[the repair integrity receipt](evidence/stage05a/validator-repair-20261023/receipt.json).

### Actual Gate A commands

All commands ran from the repository root. npm exec supplies pinned pnpm12.14.0.

| Check | Actual command | Exit | Seconds |
|---|---|---:|---:|
| database | `docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres` | 0 | 0.882 |
| python-lock | `uv sync --locked --directory apps/api` | 0 | 0.056 |
| frontend-lock | `npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile` | 0 | 1.968 |
| peers | `npm exec --yes --package=pnpm@12.14.0 -- pnpm peers check` | 0 | 1.808 |
| migration | `uv run --directory apps/api alembic upgrade head` | 0 | 2.142 |
| schema-drift | `uv run --directory apps/api alembic check` | 0 | 1.933 |
| backend | `uv run --directory apps/api pytest -q --junitxml=E:\BrosKi\OBRA\docs\evidence\stage05a\20261023T092004Z-A-91210a2f\backend.xml` | 0 | 157.346 |
| ruff | `uv run --directory apps/api ruff check .` | 0 | 0.099 |
| format | `uv run --directory apps/api ruff format --check .` | 0 | 0.097 |
| typecheck | `npm exec --yes --package=pnpm@12.14.0 -- pnpm typecheck` | 0 | 5.235 |
| eslint | `npm exec --yes --package=pnpm@12.14.0 -- pnpm lint` | 0 | 10.366 |
| build | `npm exec --yes --package=pnpm@12.14.0 -- pnpm build` | 0 | 9.861 |
| core-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e` | 0 | 218.293 |
| controlled-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:controlled` | 0 | 298.783 |
| architect-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:architect` | 0 | 405.458 |
| navigation-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:navigation` | 0 | 265.571 |
| orchestration-browser | `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:orchestration` | 0 | 300.901 |

The full native `pwsh -NoProfile -File scripts/verify.ps1` invocation exited0
after1688.075s. Independent `scripts/verify-orchestration-local.ps1` exited0
after41.352s; its child browser command took34.36s. Gate C exited0 after2.106s.

### Independent SQL and negative evidence

Saved run `d7bb258d-b48b-48d7-9cc3-850208553b39` contains2 actual task snapshots,
1 dependency,3 traces and2 events. An additional native SQL inspection exited0
and exactly matched the browser's initial/reloaded independent audits, including
the canonical source, full task/edge/event records and graph. Root eligibility and
downstream blocking remain separate from execution_status=awaiting_executor.
The browser verified same-key replay200, reload consistency, unsupported
completion404/405 and unrelated-workspace404 with protected UI hidden.

The empty-proof process exited1. The full-validator experiment first accepted
the complete saved B, then replaced only exact B proof/receipt reads and their
corresponding proof digest in memory with an incomplete matching envelope. It
exited1 at required run_id; actual A/B/proof bytes remained unchanged. These
isolated malformed inputs are not live-control-plane evidence or successful
engineering work. Exact native commands/logs are in the repair receipt.

The preserved completion assertion genuinely failed with pytest exit1:
`awaiting_executor == verified_complete` is false. Its recorder exited0 because
it confirmed that expected failure; production_test_pass=false. See the new
[expected-failure receipt](evidence/stage05a/20261023T095125Z-expected-failure-bcc658f6/receipt.json).

Before checkpoint resumption,1699 immutable preexisting evidence files remained
byte-identical. Only2 documented mutable latest-A/B controller pointers moved
to new receipts. Historical receipts/results,9 original exclusions and credentials
remained intact. No paid request, commit, executor or later-stage feature was
introduced. Staged secret/whitespace checks are a separate checkpoint audit.


Local receipts are integrity-bound operational records, not attestation against
an operator who controls source, artifacts and the database. This repair does not
certify production security or the semantic truth of an arbitrary authored plan.
Overall Stage05 remains IN PROGRESS. Commit authorization remains separate.
