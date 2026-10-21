<!-- /autoplan restore point: C:/Users/vaish/.gstack/projects/OBRA/main-autoplan-restore-stage033-20261020T092221Z.md -->
# Stage03.3 provider reliability and explicit model selection

Inspect repeated upstream503/504 failures, provider/prompt/schema/configuration and existing A/B/C evidence. Separate observed facts from hypotheses. Compare exact configured Gemini3.8 with up to two documented/account-listed alternatives using only bounded read-only metadata. Preserve all PRD requirements and strict Pydantic/server authorization, transactions, idempotency and approval history. Implement minimal explicit approved-model configuration and useful justified request/schema/budget improvements. Preserve credentials and prior evidence. Add real-PostgreSQL deterministic negative/model/budget coverage, retain every existing test identity, run full Gate A and the isolated false-success experiment, record a new source fingerprint and evidence, prepare at most one future authorized model-backed browser flow and STOP for paid authorization. No paid generation in this task, no automatic fallback/retry, no Model Hub, no commit/discard or Stage04.

## Tasks

- [x] S1 Inspect baseline and create preservation snapshot: stage033-intake-20261020T092221Z/intake.json.
- [x] S2 Research official model capabilities/lifecycle/pricing and account metadata; measure current prompt/schema offline: stage033-research-20261020/*.json, three metadata GET200, zero generation.
- [x] S3 Complete CEO, design, DX and final engineering reviews sequentially, with independent in-host voices and concrete tests (docs/reviews/STAGE033_*.md; STAGE033_TEST_PLAN.md).
- [x] S4 Implement explicit reviewed model/thinking policies, pm-v2, a shared UTF8 admission bound and original run diagnostics; authoritative ProductDocument remains unchanged.
- [x] S5 Execute 117 unit/contract tests, 170 targeted real-PostgreSQL/backend tests and three new responsive recovery browser cases; preserved earlier fixture/engine failures and their fixes.
- [x] S6 Execute full Gate A: native0, all14commands0, 285 backend/60 core browser/33 controlled browser passed with zero skips/retries; isolated wrong-success assertion actually exits1.
- [x] S7 Record current fingerprint661f2828... and immutable A receipt, real Gate C native2/PARTIAL,588-file historical preservation audit, unchanged credentials/HEAD and full A-J report in VERIFICATION_STAGE033.md.
- [x] S8 Prepare explicit gemini-3.6-flash/minimal,6000combinedtokens,90/95/100s one-generation trial and fresh paid-authorization question; current runtime file stays3.8/LOW and no paid request is made.

## Decision audit trail

| # | Phase | Decision | Class | Principle | Reason | Rejected |
|---|---|---|---|---|---|---|
|1|Intake|Proceed with explicitly authorized preparation and stop only before paid generation|Mechanical|P6|Owner specifies implementation/GateA and final paid stop|Redundant plan permission|
|2|Intake|Keep ignored .env untouched; recommend model overrides separately|Mechanical|P5|Model choice must remain explicit; no credential changes authorized|Silent model/config switch|
|3|Intake|Use native Windows tooling and local degraded skill artifacts; no nested paid CLI probe|Mechanical|P3/P5|gstack startup helper absent; no generation authorized|Global tooling repair/roundtrip model probe|
|4|CEO|Use three exact reviewed models with compatible thinking levels and LOW default|Mechanical|P1/P5|Explicit configuration without fallback; unchanged3.8 semantics|Arbitrary paid IDs or automatic routing|
|5|CEO|Prune optional server-only generation hints while preserving ProductDocument and every PRD field|Mechanical|P2/P5|Less irrelevant grammar, stricter model authority, measured offline only|Weakened validation or shorter incomplete PRDs|
|6|CEO|Bound prompt+provider-schema+snapshot UTF8 bytes before admission, default48000|Mechanical|P1|Existing48000character snapshot bound excludes prompt/schema and multibyte cost|Unbounded input or claimed exact token accounting|
|7|CEO voice|Add real-PG history retrieval under a changed runtime model; document fail-closed Settings startup impact|Mechanical|P1/P5|Historical strings and approvals must remain independent of current policy|Revalidating or rewriting old evidence|
|8|Design|Keep existing UI; make byte rejection actionable and test exact retained brief/instructions/context and approved plan|Mechanical|P1/P5|New bound must reject before admission without stranding form state|New model picker or cosmetic redesign|
|9|DX|Hide Settings validation inputs even at startup; verify real import failure redaction|Mechanical|P1|CLI-only sanitization misses module startup errors|Logging raw ValidationError inputs|
|10|DX|Share exact UTF8 content formula; bind thinking/input/hint hash to readiness/profile; set UTF8 at outer gate wrappers|Mechanical|P1/P5|Reproducible one-shell profile and safe Windows output|Different admission/adapter definitions or stale3.8-only proof|
|11|Eng|Resolve exact authorized replay before new byte admission; retain old config after cap/model change|Mechanical|P1/P5|Idempotency/history must not change with current prompt or limits|Restamping/rejecting an already admitted exact request|
|12|Eng|Guard raw request hashing against invalid Unicode; test raw JSON and direct paths|Mechanical|P1|Snapshot/adapter-only guard misses earlier encoding|Uncaught500/replacement encoding|
|13|Eng|Use a reviewed ID in the guarded controlled factory, retain explicit provider-double metadata|Mechanical|P1/P5|Test fixtures must obey configuration without allowing fake production IDs|Production fake allowlist exception|

## CEO phase outcome

Full review: [STAGE033_CEO.md](reviews/STAGE033_CEO.md). Independent in-host Codex-family voice: [STAGE033_CEO_VOICE.md](reviews/STAGE033_CEO_VOICE.md). Four P2/P3 refinements accepted above and in implementation scope; no P0/P1 strategic blocker or owner-direction challenge. Consensus dimensions (premises, problem, scope, alternatives, cost/competitive boundary, six-month trajectory) agree between primary and independent source reviewers. Claude/CLI voice unavailable/N/A; no cross-model agreement claimed. Running under Codex: nested Codex passes are omitted. Next: design, DX, then final engineering review. S3 remains open until all finish.

## Design phase outcome

Full seven-pass [design review](reviews/STAGE033_DESIGN.md) and [independent source voice](reviews/STAGE033_DESIGN_VOICE.md) completed. One mechanical P2 recovery-copy/test refinement accepted as decision8. No owner taste/structure change or P0/P1 blocker. Both source reviews preserve current hierarchy, states, themes and responsive coverage; fresh rendered verification remains GateA work, not a review claim. Claude/CLI unavailable/N/A, no cross-model consensus. Next: DX, then final engineering.

## DX phase outcome

Full eight-pass [DX review](reviews/STAGE033_DX.md) and [independent source voice](reviews/STAGE033_DX_VOICE.md) completed. Four confidentiality/budget/profile/measurement refinements accepted in decisions9-10 and existing X1-X4. Fail-closed startup redaction is a P1 acceptance requirement to implement and test, not a user-direction challenge. No claim of measured TTHW or external model consensus. Next: final engineering reviews the complete scope before implementation.

## Engineering outcome and execution

Full final [engineering review](reviews/STAGE033_ENG.md), [independent voice](reviews/STAGE033_ENG_VOICE.md) and [test plan](STAGE033_TEST_PLAN.md) completed after all earlier phases. Two replay/Unicode acceptance refinements and fixture compatibility accepted in decisions11-13. No owner-direction or taste challenge remains. Implementation, deterministic verification and documentation are already explicitly authorized by the owner's Stage03.3 request. The remaining approval boundary is paid generation only; no extra plan permission is inferred or requested.

Concrete implementation tasks: E1 reviewed configuration/safe startup; E2 lean hints/versioned prompt/shared byte guard; E3 immutable original run configuration/history; E4 current profile/readiness and additive required identities; E5 real API/browser negatives plus A/false-success; E6 dated comparison/fingerprint/preservation and paid-stop report. No new duplicate TODO for Model Hub/fallback/other agents; those remain later-stage scope.

## Cross-phase findings and task aggregation

The primary and independent source reviews repeatedly identified three shared concerns: metadata must remain distinct from live success (CEO/design/DX/engineering); input rejection and failed generation must preserve the user's work and approved history (design/DX/engineering); and explicit configuration must remain reproducible without secret-bearing startup errors or stale evidence (CEO/DX/engineering). The accepted mechanical decisions and tests above address them. These are source-review agreements within the Codex host, not measured product scores, a second model's agreement or executed verification.

Native Windows extraction produced sixteen current-branch/current-commit tasks across the four phases, scoped to their latest review run and deduplicated only by exact component/files/title. The local aggregate is `C:/Users/vaish/.gstack/projects/OBRA/aggregated-tasks-stage033-20261020T092221Z.json`; task/review logs and a checked test-plan copy sit beside it. Helper/CLI unavailability is recorded; no nested model probe, telemetry upload or global repair was performed. Task extraction was retrospective from the completed review artifacts. The first test-plan copy command used uv's changed child working directory and exited1; its empty local file was preserved, and the corrected checked copy uses the repository ROOT.

| Phase | Extracted tasks | Implementation mapping |
|---|---|---|
|CEO|C1 explicit policy; C2 full-schema-preserving request hints; C3 paid/evidence boundary|E1, E2, E6|
|Design|D1 retained byte-error input; D2 approved history; D3 operator-only model selection|E2, E3, E5, E6|
|DX|X1 safe startup; X2 profile identity; X3 reproducible docs; X4 honest complete gates|E1, E4, E5, E6|
|Engineering|E1 configuration; E2 byte contract; E3 exact replay/history; E4 evidence; E5 tests; E6 report|S4-S8 above|

No new scope-cut TODO was added. The owner's implementation and deterministic-verification authorization already covers these tasks. The pending decision is whether to authorize a specific future paid trial after Gate A passes; no general plan approval or commit permission is inferred.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|---|---|---|---|---|---|
|CEO|autoplan|Scope/evidence|1 primary +1 independent in-host|CLEAR for implementation|Four refinements accepted; live evidence still required|
|Design|autoplan|Truthful recovery/state preservation|1 primary +1 independent in-host|CLEAR for implementation|One actionable byte-error refinement|
|DX|autoplan|Safe explicit configuration/workflow|1 primary +1 independent in-host|CLEAR for implementation|Four refinements accepted; startup confidentiality P1|
|Engineering|autoplan|Final architecture/branches/tests|1 primary +1 independent in-host|CLEAR for implementation|Exact replay/Unicode/fixture acceptance added|
|External CLI/Claude|unavailable|Degraded host workflow|0|N/A|No cross-model agreement or paid probe claimed|

VERDICT: Sequential reviews and authorized implementation/preparation complete. Gate A actually passed on fingerprint661f2828..., the isolated false-success assertion exited1, and Gate C correctly remains PARTIAL. No paid generation was made. Stop for fresh explicit authorization of the proposed one-request model trial; source reviews and deterministic doubles are not live-model verification.

NO UNRESOLVED DECISIONS
