# Stage04.1 live Architect verification: A/B/C report

Executed 2026-10-22 UTC under the owner's one-request authorization. **Stage04: VERIFIED.**
No implementation code, provider configuration files or relevant source bytes changed.
This report concerns the isolated local test environment, not production certification.

## A. Verification gates

| Gate | Result | Actual native exit | Applicable evidence |
|---|---|---:|---|
| A deterministic | PASS:420 backend;60 core,33 PM controlled,33 Architect controlled,39 navigation browser tests;16 commands |0| [A receipt](evidence/stage04/20261022T052137Z-A-38c00535/receipt.json) |
| B real Architect | PASS:1 actual Gemini generation and1 complete live browser test |0| [B receipt](evidence/stage04/20261022T063526Z-B-ee98c2e7/receipt.json) |
| C combined verdict | VERIFIED:passing applicable A+B, matching source and recorded configuration |0| [C receipt](evidence/stage04/summary-836d79a10e0944dfa78e075ae60d2556.json) |

The existing A was revalidated against current source, reports and artifact hashes;
it was not rerun during this frozen live attempt. All165 deterministic browser tests
and420 backend tests passed with no skips/retries; the live browser report adds1
passing test,0 skipped/unexpected/flaky and no retries. Controlled-provider results
remain deterministic evidence only; the B flow used the production API/provider.

Source fingerprint, before and after both gates:
`f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb` (177 files).

A receipt SHA256:`1d10c4073333578c31ecdc7fe15e9f729312befc54927519107e45424854007c`.
B receipt SHA256:`36e58edf6f05bf6729dac56cbaabf6502cfb12365d6007f8458a8b4137bca486`.
C receipt SHA256:`c186b491515ed687ea7bfc74e2ab1bd4c04efab5e3561097b999087bdbdf245c`.
B records the exact A receipt/hash, source manifests, prompt/schema hashes and runtime
profile. A previous successful PM flow is not being used to certify Architect.

## B. Actual commands and exits

| Command | Exit | Duration |
|---|---:|---:|
| Previously executed `pwsh -NoProfile -File scripts/verify.ps1` |0|1250.530s outer |
| `docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres` |0|0.767s |
| Authorized `pwsh -NoProfile -File scripts/verify-architect-live.ps1 -AllowPaid` |0|55.317s outer |
| B: `uv run --directory apps/api python -m scripts.check_architect_config --check-model` |0|1.674s |
| B: `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:architect:live` |0|46.165s |
| Fresh independent read-only SQL audit through `uv run --directory apps/api python -c ...` |0|1.850s |
| Post-audit `uv run --directory apps/api python -m scripts.architect_verification summary` |0|1.315s |

The live script also calculated C automatically after B succeeded. Its original
[summary](evidence/stage04/summary-ee8a4d7720f243ff8c21c40042c3afc9.json) remains unchanged.
[Exact executed argv/native exits](evidence/stage04/authorized-live-20261022T063435-7b971272/execution-receipt.json)
and [post-verification argv/exits](evidence/stage04/authorized-live-20261022T063435-7b971272/post-verification-receipt.json).
The SQL controller source is preserved beside those receipts; it dispatched no generation.
The B browser prepared/migrated only guarded loopback54330/orba_test. Development
project data was not cleared. No backend suite ran concurrently with the browser.

## C. Phase1 and request boundary

The real browser registered a test account, created its workspace/project, awaited
its exact loaded route and workspace identity, loaded an authored draft PRD, approved
the exact saved version/revision through the real UI, independently checked SQL,
reloaded the same project and confirmed the approved source before generation.
No PM generation occurred. The human-authored draft is identified as such; it is
not PM-model evidence. Phase1 SQL confirmed zero Architect runs/artifacts/tasks/edges.

- Project:`f5795d6e-f958-4698-a09e-da08b33cfd25`.
- Workspace:`da508bbb-36c5-40e4-85b7-7872291b8b47`.
- Source PRD:`f22f924d-06cc-4071-8b18-5b6ff180346f`,version1/revision1.
- Source hash:`c71ef966a097bfec74f9917be365b42b96dfec126bf95818a6427b27f3fb5755`.
- Source approved by:`88cfc7e1-3941-4313-ac8e-3662c0d4f6a5` at `2026-10-22 06:35:53.699971+00:00`.
- Preflight generation budget:attempted0/forwarded0/blocked0.
- Entire live flow:attempted1/forwarded1/blocked0;PM generation POSTs0.
- Unrelated-user context:attempted0/forwarded0/blocked0.

Safe route/approval milestones, both SQL source audits, phase transitions and request
counters are in the [unaltered live proof](evidence/stage04/20261022T063526Z-B-ee98c2e7/live-proof.json).
Full browser traces/screenshots stayed disabled to avoid secret-bearing captures.

## D. Real provider response

- Provider:Google Gemini;official Google GenAI SDK2.31.0.
- Requested model:`gemini-3.6-flash`;returned model:`gemini-3.6-flash`.
- Thinking:minimal;combined output/thinking cap6000;UTF8 input cap96000 bytes.
- Deadlines:90s provider,95s transport,100s outer;1 worker/concurrent generation;
  SDK one initial attempt,0 automatic retries/continuations/model switches.
- Actual input accounting:13868 bytes (2686 prompt,7535 projected schema,3647 snapshot).
- Run:`c971636c-2cb9-4146-a4bd-4e954977c3e0`;actual HTTP201;final persisted run state:`succeeded`.
- Provider response ID:`0K7ZaoKYDfTMqfkPxr3nkQ4`. No provider request ID was returned.
- Provider-call duration:8441.055ms;validation:1.922ms;persistence flush:31.461ms.
  Acknowledged publication log:8588.774ms elapsed from admission start. Stored
  timing8585.093ms stops before terminal commit; these boundaries are distinct.
- Actual usage:prompt1890 tokens,candidates1322,total3212. Separate thinking usage
  was not supplied; no value or dollar cost is invented.

A genuine response passed the strict Pydantic contract, source checks, graph and
traceability checks before atomic publication. No controlled provider, cached PRD,
architecture fallback, second generation or generated task execution was used.
[Safe actual timing log](evidence/stage04/20261022T063526Z-B-ee98c2e7/live-browser.log).

## E. PostgreSQL, design and dependency evidence

Architecture:`2c4ba3b3-11de-4f47-8efa-62e98bc6088d`.
Independent browser-run SQL audits observed draftv1/r1 with null approval, followed
by edited/approvedv1/r2 with the actual test-owner actor/time. A fresh post-process
SQL audit used a new **REPEATABLE READ, READ ONLY** transaction and reconstructed
both relational documents with the application Pydantic/hash validators.

| Persisted proposal | Count |
|---|---:|
| Architecture versions for this run |1|
| Technology decisions |2|
| Components |1|
| Proposed database entities |1|
| Proposed API endpoints |2|
| Security threats with mitigations |1|
| Risks |1|
| Open decisions |0|
| Engineering tasks |3|
| Dependency edges |2|
| Relational requirement traces |4|

DAG analysis was run twice on the persisted tasks and produced the same ordering:
`task_db_setup -> task_api_implementation -> task_frontend_ui`.
Edges are prerequisite -> dependent. Every edge is forward in the deterministic
order; there are no missing/self/cyclic references. Coverage accounts for
`story_checkin`, `fr_checkin` and `criterion_checkin`;no gaps,orphan tasks,component
gaps or review obligations remain for this bounded source. Structural coverage is
not a semantic quality certificate.

All3 task records remain **proposed**. The first is dependency-ready and the latter2
are dependency-blocked because prerequisites are unexecuted. No task is completed,
tested or deployed. API contracts and database designs remain proposals.
[Independent SQL/graph/coverage evidence](evidence/stage04/authorized-live-20261022T063435-7b971272/independent-sql.json).

## F. Browser review, approval and isolation

The actual Next/FastAPI/PostgreSQL browser flow passed these checks on the same
single generated architecture:detail display,saved Task Graph rendering,draft
acceptance-criterion editing,save,reload/edit persistence,explicit test-owner
approval,reload/approval persistence,unrelated account/workspace rejection.

- Saved architecture:v1/r2,approved by `88cfc7e1-3941-4313-ac8e-3662c0d4f6a5`.
- Approval timestamp:`2026-10-22 06:36:10.606427+00:00`.
- Draft content hash:`75d9d81800f71e4dcba933fce80f0d2e1517efa60871391b22a5853e30fef2eb`.
- Edited approved content hash:`2bb657cc26be91e7bcdd94268093a512a0cc98490ebaa285c09afcafb57b2912`;API and independent SQL agree.
- Unrelated authenticated user's exact architecture request:HTTP404,no private
  criterion returned. Its actual project UI showed `Project not found.` and no
  protected criterion. The authorized record remained present in independent SQL.

[Browser report](evidence/stage04/20261022T063526Z-B-ee98c2e7/live-browser.json):1 passed,
0 skipped/unexpected/flaky,retries0;30.6s test,41.4s Playwright run.

## G. Negative paths, historical outcomes and integrity

Existing deterministic503/504,invalid schema,DAG,authorization,concurrency and
approval checks remain passing in the applicable A. They were not rerun against
and did not clear the saved live artifact. The isolated wrong-success experiment
really produced **1 failed assertion,pytest exit1**;its wrapper exited0 only after
checking that expected failure. It is not a production test pass.
[Expected-failure receipt](evidence/stage04/20261022T054749Z-expected-failure-30bdac65/receipt.json).

The old Architect B failed before generation;its exact receipt and report remain
unchanged. Earlier Stage03 upstream503/504 attempts are also retained. This later
success does not change any historical failed exit.
[Historical failed B](evidence/stage04/20261021T184000Z-B-c6b2865b/receipt.json),
[historical report](VERIFICATION_STAGE04_LIVE.md),
[unpaid Stage04.1 report](VERIFICATION_STAGE041.md).

The authorized intake hashed1265 existing evidence files:1264 immutable files are
unchanged;only the exact mutable latest-B pointer advanced. Mutable gate.lock was
excluded at intake. Credential files,all177 source files,checkpoint
`1aeb882cf9e788948df5ca5eac52e2a682a1f487` and the empty Git index are unchanged.
Current documentation/index updates preserve their previous bytes in the new audit
folder. No commit,push,reset,discard,production migration,public deployment or Stage05
occurred. Ports3001/8001 were released after browser cleanup.
[Final preservation receipt](evidence/stage04/authorized-live-20261022T063435-7b971272/final-preservation.json).

## H. Reproduction and authorization boundary

No further model request is authorized. The one attempt is consumed. Only the
following commands were authorized for this paid execution;do not rerun without
fresh explicit owner approval:

```powershell
$env:ORBA_ARCHITECT_MODEL = 'gemini-3.6-flash'
$env:ORBA_ARCHITECT_THINKING_LEVEL = 'minimal'
pwsh -NoProfile -File scripts/verify-architect-live.ps1 -AllowPaid
```

Read-only C recalculation requires the same nonsecret model/thinking overrides so
its strict runtime-profile comparison matches the preserved B. No model is called:

```powershell
$env:ORBA_ARCHITECT_MODEL = 'gemini-3.6-flash'
$env:ORBA_ARCHITECT_THINKING_LEVEL = 'minimal'
uv run --directory apps/api python -m scripts.architect_verification summary
```

The owner's dotenv was not edited;these overrides were confined to verification
processes. Full Gate A and unpaid preflight reproduction remain documented in
[Stage04.1](VERIFICATION_STAGE041.md). They reset only orba_test,so rerunning them
can remove this test artifact;the immutable audit receipts remain evidence.

## I. Limits and verdict

**Stage04: VERIFIED** for the matching local implementation and bounded real-model
journey. One passing request does not establish upstream uptime,latency guarantees,
formal architecture correctness,production security or all-browser/native-device
coverage. Automation exercises explicit human-review UI/API actions under a real
test Owner;it does not certify a person's independent technical judgment. No API
cost is fabricated. Coding/QA agents,task execution,orchestration and Stage05 remain
unimplemented. Any next paid generation requires fresh authorization.
