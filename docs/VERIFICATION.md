# ORBA current verification

**Stage05B VERIFIED after the credential-publication repair,2026-10-26.**
Fresh Gate A:792 backend and201 browser tests,18 commands exited0. Independent
local Gate B:1 real scheduler/worker-protocol browser flow,exit0. Gate C:VERIFIED,
exit0. Source `d47cf1fe3478c7877dd7cda342e56c94fdc16a517be7964f5cfefd4244f20b6f`
(243 files). No skips,retries,paid requests or engineering execution.
The pre-repair PostgreSQL reproduction returned201 after credential expiry;
new regressions return401 without SQL publication. See [current evidence and
commands](VERIFICATION_STAGE05B_CREDENTIAL_REPAIR.md). The earlier acceptance
below remains historical and cannot certify the repair.

## Historical Stage05B acceptance before credential repair

**Stage05B VERIFIED, 2026-10-26.** Gate A passed 776 backend and 201 browser tests;
all 18 native commands exited 0. Independent local Gate B passed1 real scheduler/
worker-protocol browser flow and strict SQL/API/source proof validation. Gate C
exited 0 with applicable matching source and policy. No skips, xfails or retries.
Source: `4bfcc3ec0d903cfedcd7addaca7e06c4287467a4ed1d1e79d33524a446d2538d` (241 files).
[Complete Stage05B report,commands and preserved failures](VERIFICATION_STAGE05B.md).
No model generation or task execution occurred. **Overall Stage05: IN PROGRESS.**
No Stage05C/D/06, Git commit or push occurred.

## Historical Stage05A verified checkpoint

The focused proof-v2 repair is **VERIFIED** against fresh passing A/B/C:
683 backend tests;60 core,33 PM controlled,33 Architect controlled,39 navigation
and21 orchestration browser tests;1 independent local control-plane browser flow.
All17 A commands and local B/C exited0 with zero skips, xfails or retries.
Source: `6c21f5d8534403c93be7feaa9b232aa57e62a6686d49084bc09dbd808e56e705`.
See [the repair record](VERIFICATION_STAGE05A_REPAIR.md). No paid model, executor,
commit or later-stage work occurred. Overall Stage05 is IN PROGRESS.

The historical pre-repair results below remain unchanged:

Stage05A orchestration foundation is **VERIFIED** on2026-10-23, source
`daff99b31e5db1156011058eed168e0c04136bb840dcb75f7de2d928fe7d3f62`. Gate A passed478 backend and186 browser tests (all17 commands); independent
local Gate B passed1 real browser/API/PostgreSQL control-plane flow. Gate C exited0.
No mandatory skips/retries, model generation or executor simulation. Actual
commands, failures/repairs, source bindings and receipts are in
[VERIFICATION_STAGE05A.md](VERIFICATION_STAGE05A.md).
**Overall Stage05: IN PROGRESS.** No execution or software-delivery completion
is claimed. Historical Stage04 evidence follows and is not reused for this verdict.

## ORBA Stage04 — VERIFIED historical baseline

2026-10-22: the owner's single authorized Gemini Architect request passed the complete
live browser and independent PostgreSQL verification. No implementation code changed.

| Gate | Result | Native exit | Evidence |
|---|---|---:|---|
| A deterministic | PASS:420 backend;60 core,33 PM controlled,33 Architect controlled,39 navigation browser tests;all16 commands;no skips/retries |0| [A receipt](evidence/stage04/20261022T052137Z-A-38c00535/receipt.json) |
| B real Architect | PASS:1 model request,1 live browser test;validation,persistence,DAG,traceability,editing,approval,isolation |0| [B receipt](evidence/stage04/20261022T063526Z-B-ee98c2e7/receipt.json) |
| C combined verdict | VERIFIED:applicable passing A+B and matching source/profile |0| [C receipt](evidence/stage04/summary-836d79a10e0944dfa78e075ae60d2556.json) |

Matching177-file source fingerprint:
`f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb`.
A was revalidated against current source/artifacts,not rerun during this live attempt.

Real provider:Google Gemini3.6 Flash,minimal thinking;6000 combined output/thinking
cap,90/95/100s deadlines,1 worker,0 retries. Requested/returned model both
`gemini-3.6-flash`;response ID`0K7ZaoKYDfTMqfkPxr3nkQ4`;provider duration8441.055ms.
Actual usage:1890 prompt +1322 candidates =3212 total tokens. Separate thinking usage
and cost were not returned and are not invented.

Run`c971636c-2cb9-4146-a4bd-4e954977c3e0` generated architecture
`2c4ba3b3-11de-4f47-8efa-62e98bc6088d` from approved source
`f22f924d-06cc-4071-8b18-5b6ff180346f`,v1/r1. It persisted1 component,3 proposed tasks,
2 DAG edges and4 requirement traces. Coverage has no gaps. Real browser editing
persisted;explicit test-owner approval persisted at architecturev1/r2. Unrelated
workspace access returned404 and displayed no protected content. Independent
READ ONLY/REPEATABLE READ SQL confirmed the same approved artifact/hash/graph and
exactly1 Architect run,0 PM runs. No generated task was executed.

[Complete final A/B/C report,commands,metadata and limitations](VERIFICATION_STAGE041_LIVE.md).
[Independent final SQL](evidence/stage04/authorized-live-20261022T063435-7b971272/independent-sql.json).
[Preservation audit](evidence/stage04/authorized-live-20261022T063435-7b971272/final-preservation.json).

Earlier results remain intact:

- [Stage03 VERIFIED and historical503/504 failures](VERIFICATION_STAGE033_LIVE.md).
- [Original failed Architect live B:0 model generations](VERIFICATION_STAGE04_LIVE.md).
- [Stage04.1 repair,420 backend/165 browser,standalone39 and5/5 unpaid preflights](VERIFICATION_STAGE041.md).
- [Isolated deliberately incorrect success assertion:actual pytest exit1,wrapper0](evidence/stage04/20261022T054749Z-expected-failure-30bdac65/receipt.json).
- [Previous verification index before this live result](evidence/stage04/authorized-live-20261022T063435-7b971272/verification-index-before.md).

All1264 preexisting immutable evidence files,source files,credential files and HEAD
checkpoint1aeb882 remain unchanged. Only latest-B's mutable control pointer advanced.
Current report/README/roadmap updates are documentation outside the source manifest;
previous bytes are saved. No implementation edits,commits,pushes,discarded work or
Stage05 occurred. The authorization is consumed;no further paid request is authorized.

To calculate C without a provider call,use the same recorded nonsecret profile:

```powershell
$env:ORBA_ARCHITECT_MODEL = 'gemini-3.6-flash'
$env:ORBA_ARCHITECT_THINKING_LEVEL = 'minimal'
uv run --directory apps/api python -m scripts.architect_verification summary
```

One real passing journey is bounded evidence,not a provider reliability guarantee,
production-security certification or proof that proposed designs were implemented.
# Stage05B current verification

New scheduler and worker-protocol results are recorded separately in
[VERIFICATION_STAGE05B.md](VERIFICATION_STAGE05B.md) and new immutable
`docs/evidence/stage05b` receipts. Stage05B has not yet passed its full A/B/C gates.
No paid AI or engineering task execution is part of this verification. All older
reports and historical receipts below remain unchanged.
