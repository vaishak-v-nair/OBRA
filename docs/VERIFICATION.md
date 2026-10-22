# ORBA Stage04 — VERIFIED

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
