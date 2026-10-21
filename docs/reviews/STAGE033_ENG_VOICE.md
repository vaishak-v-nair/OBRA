# Stage03.3 independent final engineering voice

Date: 2026-10-20. Independent in-host Codex-family source review after CEO, design and DX. This is not cross-model consensus or executed application/provider evidence. No tests, network requests, generation, configuration changes or historical-evidence changes were performed. This file is the only authored artifact.

## Verdict

Proceed with the scoped implementation and deterministic verification. No architecture or scope blocker was found. The primary engineering review's E1-E6 requirements are appropriate; the two precise boundary refinements below belong in their acceptance tests. This review does not establish a passing Gate A or successful live generation. Stage03 remains PARTIAL until qualifying current-source real-model browser evidence exists.

Read STAGE033_PLAN.md, STAGE033_ENG.md and STAGE033_TEST_PLAN.md against the current Settings, provider, readiness, service, schema, API startup/routes, verification runner/wrappers and existing provider, contract, persistence, reliability, verifier and controlled-browser tests. Current source still represents the pre-Stage03.3 implementation.

## Findings and required fixes

### ENG-V1 / P1 / confidence 9 of 10: Apply the new admission bound after exact replay resolution

Source: apps/api/orba/pm_service.py:175-257. Existing admission validates project membership, workspace role and original session, then resolves the existing request UUID and payload hash before building the current snapshot or applying input limits. Exact replay returns the old run without a new provider call. The proposed shared byte helper must not be moved ahead of that decision merely to reject early.

A previously admitted request can exceed a subsequently lowered byte limit or have a different current prompt/hint overhead. Re-evaluating it against the new runtime budget would replace durable idempotency behavior with a new 422, and recomputing diagnostics could misrepresent its original request configuration. A stale context revision must likewise not invalidate retrieval of the already admitted exact request.

Keep current authorization/session checks and hash comparison authoritative. For a new UUID, build the authorized snapshot, validate shared UTF8 metrics and reject before inserting a run. For exact replay, return the historical outcome without restamping model, thinking, byte counts, hint hash, deadlines or diagnostics. A mismatching payload using an existing UUID must retain its idempotency conflict.

Add a labeled real-PostgreSQL test: admit a valid deterministic SDK-backed request with a sufficiently large payload, lower the configured byte cap within its permitted range and change the supported runtime model, then replay the identical UUID/input. Assert the same run/plan, original stored configuration, unchanged approved version/actor/time/hash/graph and no second HTTP request. Also retain the different-input same-UUID conflict assertion. This extends E2/E3 without a new mechanism or migration.

### ENG-V2 / P2 / confidence 9 of 10: Safe UTF8 rejection must include the earlier request-hash path

Source: apps/api/orba/pm_service.py:176 hashes canonical(payload.model_dump(mode="json")).encode() before _snapshot at line 235; snapshot hashing at line 245 also encodes. canonical in pm_schemas.py uses ensure_ascii=False. Guarding only snapshot metrics or the adapter cannot protect the first encoding operation.

Handle invalid Unicode consistently before any durable admission, without replacement encoding, silent truncation or raw input in errors/logs. Preserve request hashing for valid existing input. Use a static safe 422 input error and no invented terminal run; keep authorization and real middleware in the integration path. The exact lower-level parser rejection may already prevent a malformed string, which must be established by executing the API test rather than assumed from a helper test.

Add an authenticated raw-JSON request with an escaped unpaired surrogate, plus a direct helper/adapter encoding case. Assert safe rejection, no sentinel/brief exposure, no SDK/client dispatch and independently counted zero new runs/plans. Keep the existing ordinary multibyte and exact-limit/+1 cases. This is a focused addition to the plan's existing invalid-Unicode requirement, not a broader input-policy change.

## Engineering assessment

| Area | Acceptance condition |
|---|---|
|Architecture and authorization|One dependency-free reviewed-model policy shared by Settings, readiness and adapter; no new route/provider/agent, automatic fallback or migration. Preserve FastAPI authentication, Origin/CSRF, workspace locks, current membership and original-session checks. Invalid copied/mutated Settings must fail before HTTP; old run model strings remain readable.|
|Safe configuration errors|Keep the accepted Settings hide_input_in_errors change and actual module-startup subprocess check. Test sentinels in invalid model/thinking fields with a nonzero native exit and no disclosure. Missing provider configuration remains distinct and permits the rest of the app.|
|Strict output|Derive only the generation hint from ProductDocument. Remove optional server-owned authority/disposition hints and the forbidden human generation enum; retain every required PRD/GWT field, Pydantic/graph/source checks, relational atomic publication and existing document/envelope bounds. Keep pm-v1 immutable and version the new prompt.|
|Request bounds and performance|Use the exact shared UTF8(PROMPT) + UTF8(canonical(hint)) + UTF8(canonical(snapshot)) formula, equality accepted, default 48000 and supported range 8192-96000. Retain separate character/context guards. Report local content bytes, not wire bytes or tokens. Avoid new queries, pooling, deadlines or dependencies without evidence; per-request async-client cleanup remains appropriate.|
|Configuration history|Persist a server-owned nonsecret generation_configuration at reservation. Merge terminal timing/error data without losing it; exact replay and uncertain-commit recovery preserve original facts. Requested and returned model remain separate, including null returned metadata on genuine failures.|
|Tests and preservation|Keep every baseline identity and historical baseline array; add Stage03.3 identities and require their union in Gate A. The existing unreviewed-model readiness test currently expects one metadata GET; retain its identity while strengthening it for the new fail-closed zero-request policy. In tests/controlled_app.py:71, replace the fake configured model ID with reviewed gemini-3.8-flash so Settings validates, while preserving the guarded test DSN, native dependency override and controlled-double-not-live returned metadata/labels. Do not admit the fake ID into production policy; historical persisted model strings stay readable.|
|Meaningful negative paths|The accepted real-SDK synthetic HTTP malformed-JSON and structurally invalid-PRD cases must traverse real API/auth/CSRF/PostgreSQL and independently prove failed run, zero partial graph and prior approved-plan preservation. Existing 503/504, revocation, concurrent UUID, cancellation and uncertain-COMMIT tests remain mandatory.|
|Browser recovery|Use an actual API combined-byte rejection with the labeled controlled provider; retain exact brief/instructions/context and selected approval, clear only a known unadmitted UUID and make the corrected submission explicit. No route.fulfill success or implicit POST retry.|
|Evidence gates|Extend execution profile and strict readiness artifacts together with model/thinking/input limit/hint identity and per-model official references. Tampered/stale/model-doc/profile/controlled evidence must fail without external requests. Changed source requires fresh A; current B binds its native metadata command, profile, source and A-receipt hash; C remains network-free.|

All SDK synthetic HTTP and controlled providers must remain explicitly labeled deterministic evidence. They establish request/error/persistence behavior, not provider availability, semantic planning quality or model success. Offline reduced hint bytes/unions establish a measured request change, not an explanation or fix for upstream 503/504.

## Completion boundary

Run targeted checks and the full serial Gate A against guarded orba_test, then the isolated false-success experiment with its actual expected native exit 1. Record command exits/counts/limitations, fresh source fingerprint, nonsecret effective profile, hint/full-schema measurements and preservation evidence. Do not alter either ignored dotenv file, prior receipt bytes or the owner's unrelated work; do not commit automatically.

Preparation ends with a concrete proposed gemini-3.6-flash/minimal configuration, 6000 output/thinking tokens, existing 90/95/100-second budgets, concurrency 1 and zero retries. The owner must freshly authorize the single future Gate B browser generation. Its one bounded native metadata GET is readiness only; do not add a generation probe. Use that one resulting plan for API/SQL/browser/edit/reload/approval/isolation evidence. Non-ready metadata, failed generation or a blocked duplicate POST ends that attempt with the actual outcome. Preserve historical Full/standalone and later 503/504 outcomes independently; no next paid call or Stage04 is authorized here.
