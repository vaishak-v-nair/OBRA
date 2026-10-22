# ORBA Stage04.1 — deterministic verification complete; Stage04 PARTIAL

The browser setup defect is repaired and verified. The old test reloaded after
project POST persistence without awaiting the Next project route. A real-response
barrier reproduced the failure signature on unchanged07bf0deb source. The repair
awaits exact route/project/workspace/PRD identity, real UI approval, independent SQL
and reload before reaching the Architect generation boundary. Runtime API/provider
modules, model configuration and owner credentials are unchanged.

| Gate/check | Actual result | Exit | Evidence |
|---|---|---:|---|
| A deterministic | PASS:420 backend;60 core,33 PM controlled,33 Architect controlled,39 navigation browser tests;16 commands;0 skips/retries |0| [A receipt](evidence/stage04/20261022T052137Z-A-38c00535/receipt.json) |
| Standalone navigation | PASS:39 desktop/mobile/tablet cases;0 skips/retries |0| [Receipt](evidence/stage04/20261022T054323Z-unpaid-navigation-edc595cd/receipt.json) |
| Five clean unpaid Phase1 runs | PASS5/5, distinct users/workspaces/projects/PRDs, actual UI approval/API/SQL/reload;0 generation attempts |0 each| [Aggregate](evidence/stage04/20261022T054322Z-stage041-repeatability-f4a1378e/receipt.json) |
| Isolated deliberately wrong success assertion | Expected genuine pytest failure:1 failed,0 architectures; wrapper validates it separately |1 child /0 wrapper| [Receipt](evidence/stage04/20261022T054749Z-expected-failure-30bdac65/receipt.json) |
| B live Architect | NOT RUN on current source; historical failed pre-dispatch B preserved; no paid request authorized here |NOT RUN| [Historical B](evidence/stage04/20261021T184000Z-B-c6b2865b/receipt.json) |
| C combined verdict | PARTIAL; A PASS, existing B remains FAIL; unpaid evidence cannot certify live generation |2| [Actual C/final SQL audit](evidence/stage04/20261022T055127Z-stage041-final-audit-aa625b40/receipt.json) |

Current177-file source fingerprint:
`f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb`.
A receipt SHA256:
`1d10c4073333578c31ecdc7fe15e9f729312befc54927519107e45424854007c`.
All five receipts and final independent SQL match this source. Real Gemini generation
requests: **0**; intentional denied boundary probes are recorded separately.

[Full A–K report, exact commands, failure history and reproduction](VERIFICATION_STAGE041.md).
The initial9 passed/30 failed navigation attempt remains visible; its barrier-fixture
error and later Docker/test-database outage were diagnosed and recorded, not converted
to passes. Subsequent recovered focused checks and complete Gate A ran for real.
[Development command history](evidence/stage04/stage041-development-history/receipt.json).

Final read-only PostgreSQL inspection reconfirmed the last PRD approved at v1/r1,
actual approver/time/hash and1 epic/1 story/1 criterion;0 PM runs,0 Architect runs,
0 architectures/tasks/dependencies. All989 preexisting evidence files were checked:
988 immutable files unchanged, only the exact latest-A pointer advanced. Credentials,
HEAD1aeb882 and index remain unchanged; all user work stays uncommitted.
[Preservation audit](evidence/stage04/stage041-preservation/receipt.json).

```powershell
pwsh -NoProfile -File scripts/verify.ps1
pwsh -NoProfile -File scripts/verify-architect-preflight.ps1 -Mode navigation
pwsh -NoProfile -File scripts/verify-architect-preflight.ps1
uv run --directory apps/api python -m scripts.architect_false_success
uv run --directory apps/api python -m scripts.architect_verification summary
```

Run backend/browser commands sequentially against guarded orba_test. Default
preflight is unpaid and denies model dispatch; its sentinel is not provider readiness
or live evidence. Native device/all-browser compatibility and production security
certification are not claimed. One existing Google SDK/Python deprecation warning
remains. Historical Stage03 VERIFIED and503/504 failures remain unchanged in
[Stage03 report](VERIFICATION_STAGE033_LIVE.md); they cannot certify Architect.
[Historical failed Stage04 live report](VERIFICATION_STAGE04_LIVE.md) and
[prior current index](evidence/stage04/stage041-intake/previous-VERIFICATION.md) are preserved.

**Stop: fresh explicit owner authorization is required for the next single bounded
Architect Gate B.** No live command, model switch, commit, push, reset, discarded work,
generated task/code execution, public deployment or Stage05 occurred here.
