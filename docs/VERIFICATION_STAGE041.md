# Stage04.1 — navigation repair and unpaid preflight

**Gate A PASS; standalone navigation PASS; five clean unpaid preflights PASS.
Stage04 remains PARTIAL.** All Stage04.1 deterministic requirements executed. No
paid Architect generation was authorized or executed. Historical live/provider
evidence and failed attempts remain unchanged.

## A. Confirmed failure cause and evidence limits

The failed live test waited for project POST response, authored a draft and called
reload before awaiting the Next project route. Its snapshot shows Chat while SQL
shows the saved project/draft. The old run had network tracing disabled, so its exact
scheduling cannot be reconstructed retrospectively.

An isolated probe against the unchanged07bf0deb baseline held the **actual Next
project-route response**. POST201 and draft persistence occurred while URL remained
`/`; reloading there reproduced Chat with no Approve plan control. Navigating to the
exact project then displayed that same real draft. No API response was replaced.
[Probe events, actual exits and receipt](evidence/stage04/stage041-baseline-reproduction/receipt.json).
This confirms the missing route synchronization defect can cause the observed
failure. It does not establish a Gemini failure or an application authorization
redirect. No model-generation request or ArchitectRun existed in the historical B.

The first development navigation run also exposed a test-fixture error: it held
only the first matching GET; another real GET completed. The corrected barrier
holds all matching responses until the assertion and records each response. The
focused slow-response proof records two actual held200 responses. No sleep, repeated
click, POST retry or blanket timeout increase is used.

## B. Code and test changes

| File | Responsibility |
|---|---|
| apps/web/tests/architect-preflight.ts | Shared real registration/workspace/project/draft/UI approval/API/SQL/reload/source setup |
| apps/web/tests/architect-boundary.ts | Closed Phase1; one authorized UI generation; closed Phase3; direct API-context model POST denial |
| apps/web/tests-architect-live/architect-live.spec.ts | Uses that setup; preserves partial milestones and reuses one future generated architecture |
| apps/web/tests-navigation/navigation.spec.ts |39 cases across desktop/mobile/tablet: actual response barriers, identity, session/permission/errors and denial probes |
| apps/web/tests-architect-preflight/preflight.spec.ts | One clean standalone Phase1, no generation or runtime credential |
| apps/api/tests/no_generation_app.py | Isolated test-only early generation denial, dependency tripwires, safe counters and sentinel configuration |
| apps/api/scripts/inspect_architect_preflight.py | Independent repeatable-read, read-only relational source/hash/approval/zero-run inspection |
| apps/api/scripts/architect_preflight.py | Immutable unpaid receipts; strict reports/source matching; real child exits |
| scripts/verify-architect-preflight.ps1 | Explicit unpaid command; navigation mode; native exit propagation |
| apps/api/scripts/architect_verification.py | Adds navigation to Gate A; requires exact zero-dispatch Phase1 proof for future B |
| apps/api/tests/test_architect_preflight.py | Real PostgreSQL guard/audit and explicitly labeled parser/process unit tests |

Both production frontend source files differ from intake only by invisible loaded
project/workspace and saved PRD identity attributes. Existing AuthGate already remounts
protected state on account/workspace/path changes; no routing/session refactor was
needed. All apps/api/orba runtime modules, provider/model/prompt/schema/budgets and
owner dotenv files are unchanged. No dependency or database migration was added.

## C. Synchronization and generation boundaries

```text
project POST201 -> exact /projects/{id} -> loaded ID + workspace + selected workspace
 -> authored draft -> reload confirmed project -> exact saved PRD ID/v/r/draft
 -> authorized UI approval -> exact API actor/time/v/r/hash -> independent SQL
 -> reload same route -> same approved source -> Architect entry -> STOP
```

Approval binds the saved content revision; it does not increment it. The fixture's
approved source is v1/r1. A UI label alone cannot satisfy the helper. Assertions check
the actual approval payload/response, selected plan, loaded state, current source and
independent reconstructed SQL hash. A failed prerequisite never opens generation.
Route/loaded-identity observations retain the prior live15s action budget. Ordinary
project/approval response observations are bounded25s around the existing20s client
request budget, replacing a wait for the entire browser-test deadline.

Unpaid mode runs the actual app factory/routes/authentication/CSRF/PostgreSQL with
explicit isolated test settings and empty runtime credential aliases. A clearly
labeled non-credential sentinel enables entry-control inspection. It is not readiness
or a provider response. Server denial precedes dependencies; dependency tripwires
prevent provider construction. Context guards cover pages/popups and direct API
requests; service workers are blocked. Separate intentional probes verify server and
client denial. Unexpected attempts fail even when denied. No production bypass flag
or fake generated architecture was introduced.

## D. Gate A and command results

Current source: `f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb` (177 files).
`pwsh -NoProfile -File scripts/verify.ps1` exited0 (1250.530s). All16 required
commands exited0. **420 backend +60 core browser +33 PM controlled browser +33
Architect controlled browser +39 navigation browser tests passed; zero skips,
xfail, flaky results or retries.** These include real PostgreSQL integration and
explicitly labeled deterministic provider/parser doubles; they are not live-model
proof. All prior baseline identities remain mandatory.

[A receipt](evidence/stage04/20261022T052137Z-A-38c00535/receipt.json),
SHA256 `1d10c4073333578c31ecdc7fe15e9f729312befc54927519107e45424854007c`.
Receipt start/end/current source all match. Actual commands are stored as exact
argv arrays in that receipt; the command names below correspond to that workflow.

| Gate A command | Exit | Duration(s) |
|---|---:|---:|
| database |0|0.789 |
| python-lock |0|0.05 |
| frontend-lock |0|1.732 |
| peers |0|1.723 |
| migration |0|1.799 |
| schema-drift |0|1.71 |
| backend |0|101.03 |
| ruff |0|0.089 |
| format |0|0.072 |
| typecheck |0|4.038 |
| eslint |0|8.44 |
| build |0|14.139 |
| core-browser |0|198.103 |
| controlled-browser |0|279.898 |
| architect-browser |0|374.232 |
| navigation-browser |0|255.703 |

These include actual guarded PostgreSQL startup, locked uv/pnpm installs, peer
checks, Alembic upgrade/drift, Pytest, Ruff/format, TypeScript, ESLint, Next production
build and every browser group. One existing Google SDK/Python3.14 deprecation warning
remains; no test was skipped or weakened. Prior failed development commands remain
in [their actual history](evidence/stage04/stage041-development-history/receipt.json).

## E. Independent navigation and five clean preflights

Standalone navigation exited0: **39 passed**, all three viewports, no skips/retries.
[Standalone receipt](evidence/stage04/20261022T054323Z-unpaid-navigation-edc595cd/receipt.json).
Then the isolated false-success experiment ran, followed by **exactly five** clean
standalone preflights, one worker and zero test retries. All5 passed; each has a
fresh user/workspace/project/PRD, real API/UI approval, SQL evidence and zero
attempted/forwarded/blocked generation POSTs. All receipt start/end sources equal
Gate A's177-file fingerprint. Server processes, browser contexts and guarded data
were fresh for each command; normal compiler/dependency caches were retained.

[Fixed-size execution/aggregate receipt](evidence/stage04/20261022T054322Z-stage041-repeatability-f4a1378e/receipt.json)
records every actual command/exit and the executed controller; it exited0 (425.580s,
including standalone navigation, expected-failure wrapper and five runs).

| Run | Project ID | PRD ID | Version/revision/state | Exit | Duration(s) | Evidence |
|---|---|---|---|---:|---:|---|
|1|`bec34e22-71fa-489e-a22e-3da3546388bf`|`7b80eda4-73b3-4946-8d08-40cc12bddbb3`|1/1 approved|0|30.92|[receipt](evidence/stage04/20261022T054755Z-unpaid-preflight-9f232393/receipt.json)|
|2|`cdd16706-ef05-45ff-a47e-8ba8c9d16a7a`|`f3b42f5c-cdb7-43d1-b110-669247f3429d`|1/1 approved|0|30.416|[receipt](evidence/stage04/20261022T054826Z-unpaid-preflight-d54a31ad/receipt.json)|
|3|`dc136e53-3a41-45c7-aaea-fa39c8458643`|`ad149eaa-8051-4627-9964-5edf74c53440`|1/1 approved|0|30.661|[receipt](evidence/stage04/20261022T054856Z-unpaid-preflight-bc59ca77/receipt.json)|
|4|`74907aff-0bc9-4fd0-901c-a3e541494817`|`61bac669-1f8c-46cc-9a46-39f73e421ed1`|1/1 approved|0|28.881|[receipt](evidence/stage04/20261022T054927Z-unpaid-preflight-041c0e79/receipt.json)|
|5|`78f915c1-01bb-4a75-86ce-5b24f1f63f49`|`f8724289-f902-4f34-b0a3-108c99756d6a`|1/1 approved|0|29.991|[receipt](evidence/stage04/20261022T054956Z-unpaid-preflight-690e9010/receipt.json)|

These are independent verification runs, not automatic retries of a failed test or
model request. No initial failure was hidden: the earlier9/30 development navigation
failure and earlier-source initial preflight remain separate receipts. Neither this
aggregate nor any controlled-provider case is live Architect Gate B evidence.

## F. PostgreSQL and authorization observations

The shared flow uses actual authenticated Owner membership, server-created project
identity, relational human-authored PRD and real UI/API approval. Each SQL inspection
uses a fresh engine/session and read-only repeatable-read transaction on guarded
orba_test. It reconstructs epics/stories/criteria, validates the canonical hash,
source parentage, version/revision/current agreement, approver and timestamp.
Normal preflight requires0 PM runs,0 Architect runs,0 architectures/tasks/edges.
Development project data is never reset. Test rows may be cleared by subsequent
guarded tests; per-attempt SQL evidence records the committed state before cleanup.

After all five runs, a further independent SQL command exited0 and reconfirmed the
last approved source: project `78f915c1-01bb-4a75-86ce-5b24f1f63f49`, PRD `f8724289-f902-4f34-b0a3-108c99756d6a`,
version1/revision1, approver `2a05e417-1cd7-4a78-a4ea-aeafc3b15ebd`,
approved at `2026-10-22T05:50:19.378146+00:00`. Reconstructed counts:1 epic,1 story,1 criterion;
canonical hash matches. PM runs, Architect runs, architectures, engineering tasks and
dependencies are all0. [Final independent audit](evidence/stage04/20261022T055127Z-stage041-final-audit-aa625b40/receipt.json).

## G. Negative paths and preserved actual failures

Real session revocation clears protected content on the next authority check; real
Member approval returns403 with source still draft; unrelated workspace returns404
without private project content. Narrowly labeled transport503/409 tests preserve
the actual draft and stop before generation. Wrong-route assertions report the
expected project UUID and actual URL. Missing proof identities and invalid versions
cannot pass evidence validation. Existing DAG/provider503/504/invalid-output/isolation
regressions and the isolated false-success experiment remain mandatory/separate.

Actual development failures are preserved:

- External baseline probe initially exited1 because its config resolved webServer
  cwd outside the repository. Corrected explicit cwd run exited0; first log retained.
- Initial focused backend:32 passed/1 failed due to the NEW test's wrong approval
  revision assumption. Corrected against existing pm.py, then40 passed. Initial
  TypeScript shared environment-union type error exited1; explicit config type fixed it.
- Initial navigation command exited1:9 passed/30 failed/0 skipped/retried. One early
  fixture defect, then a missing project response and PostgreSQL preparation errors.
  [Actual failure/outage/snapshot record](evidence/stage04/stage041-navigation-investigation/receipt.json).
- Docker test container exited255 at2026-10-21T19:16:36.701Z, OOMKilled=false; underlying
  stop cause unknown. Its recovery command exited0, but Docker later became
  unavailable again (Linux-engine named pipe missing). Focused backend then had
  44 passed/7 setup errors; these are not passes. Restarted the existing installed
  Docker Desktop hidden and restored only test-postgres without resets. Recovered
  focused backend51 passed; focused navigation4 and boundary3 passed.
- Static review identified missing-on-both-sides identity comparison and failure
  diagnostics loss. Both fixed, with additional parser regressions and finally writes.

The intentionally incorrect Architect success assertion actually ran separately:
**1 pytest test failed, native exit1**. It asserted succeeded for a real PostgreSQL
failed run with0 architectures using a labeled provider503 double. The wrapper
exited0 only after checking the nonzero result, actual evidence line and failure
report; this is never counted as a passing production test.
[Expected-failure receipt](evidence/stage04/20261022T054749Z-expected-failure-30bdac65/receipt.json),
[unaltered actual pytest output](evidence/stage04/20261022T054749Z-expected-failure-30bdac65/experiment.log).

## H. Source and evidence integrity

Old source07bf0deb and all historical Stage03/04 receipts remain authoritative only
for their own source/attempt. [Current frozen source and preservation checks](evidence/stage04/stage041-source-freeze/receipt.json).
The current verifier includes all new helpers/tests in its177-file source manifest.
Before edits,989 existing evidence files were hashed (runtime gate.lock excluded).
Final preservation audit checked all989 preexisting files:988 immutable files are
byte-identical; only the exact latest-A control pointer advanced to the genuine new
receipt. Runtime gate.lock was excluded at intake because it is mutable. No prior
receipt/transcript/artifact was rewritten. Credentials and HEAD remain unchanged,
index is empty, and99 working-tree status entries remain uncommitted.
[Preservation receipt](evidence/stage04/stage041-preservation/receipt.json).
Checkpoint1aeb882 remains HEAD; no commit/push/reset/discard occurred.

## I. Paid request accounting

Real provider-generation requests: **0**. No live model response, usage or response
ID exists for Stage04.1; none is invented. Denied intentional application/client
boundary probes are recorded separately from actual provider dispatch. Normal
standalone Phase1 requires zero attempted/forwarded/blocked generation POSTs.

## J. Reproduction and prepared future live command

```powershell
pwsh -NoProfile -File scripts/verify.ps1
pwsh -NoProfile -File scripts/verify-architect-preflight.ps1 -Mode navigation
pwsh -NoProfile -File scripts/verify-architect-preflight.ps1
uv run --directory apps/api python -m scripts.architect_false_success
uv run --directory apps/api python -m scripts.architect_verification summary
```

For five runs, invoke the default unpaid command five times sequentially and retain
every exit/receipt; a failing attempt must remain visible. The linked fixed-size
aggregate records the exact executed controller and all seven commands. No generation
command is present in that controller. The script automatically allocates new receipt
directories; never rerun raw historical argv that writes to old artifact paths.

```powershell
$anyPreflightFailed = $false
for ($preflightAttempt = 1; $preflightAttempt -le 5; $preflightAttempt++) {
    pwsh -NoProfile -File scripts/verify-architect-preflight.ps1
    $preflightExit = $LASTEXITCODE
    Write-Output "Preflight ${preflightAttempt}: native exit ${preflightExit}"
    if ($preflightExit -ne 0) { $anyPreflightFailed = $true }
}
if ($anyPreflightFailed) { exit 1 }
```

Only after fresh explicit owner authorization, the prepared **unexecuted** paid command:

```powershell
$env:ORBA_ARCHITECT_MODEL = 'gemini-3.6-flash'
$env:ORBA_ARCHITECT_THINKING_LEVEL = 'minimal'
pwsh -NoProfile -File scripts/verify-architect-live.ps1 -AllowPaid
```

Same reviewed configuration:6000 combined output/thinking tokens,90/95/100s provider/
transport/outer deadlines,96000 input bytes,1 worker,0 retries, at most1 real generation.
It requires a matching passing A and genuine runtime credential, shares Phase1, then
reuses that one architecture for validation/SQL/DAG/traceability/browser/edit/approval/
isolation. It never generates a second architecture for browser testing. No paid
command ran here; source/model availability or upstream reliability is not guaranteed.

## K. Verdict and limits

**Stage04: PARTIAL.** Gate A PASS and Stage04.1 repeatability/preflight checks PASS.
Gate B has not run on the new source; its old failed pre-dispatch receipt remains.
Gate C was actually calculated and exited2/PARTIAL, retaining B FAIL rather than
accepting unpaid/controlled evidence as real-model proof.
[Actual C output and exit](evidence/stage04/20261022T055127Z-stage041-final-audit-aa625b40/receipt.json).
All current source fingerprints match the new A; no old live proof was reused.
The next one-request live Architect command needs fresh explicit owner authority.
No Stage05, task/code execution,
deployment, credentials change or Git commit occurred. Chromium device emulation
does not certify native devices/all browsers, and these local receipts are not
hostile-machine attestation or production security certification.
