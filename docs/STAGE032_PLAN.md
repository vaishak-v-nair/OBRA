<!-- /autoplan restore point: C:\Users\vaish\.gstack\projects\OBRA\main-autoplan-restore-stage032-20261019T180758Z.md -->
# Stage03.2 provider readiness and live-verification preparation

Owner scope: inspect the current working tree and Gate A/B evidence; verify the exact configured Gemini model using official documentation and bounded read-only metadata; add honest non-generative readiness if missing; review timeouts, idempotency, concurrency, approved-plan preservation and UI errors; rerun full deterministic Gate A and the isolated false-success experiment; prepare one-generation Gate B and STOP for explicit paid authorization. Preserve credentials, all historical receipts, password policy, Stage01/02 data and security. No model switch, paid generation, automatic retry, commit, discard or Stage04.

## Implementation tasks

- [x] S1 Capture intake; inspect evidence, source, configuration, SDK and deadlines. Validated current A and historical B; official documentation plus account metadata list confirms the exact model; generation calls0.
- [x] S2 Complete sequential CEO, design, DX and engineering reviews and test plan. Each independent voice and primary artifact was read/written before proceeding to the next phase; no cross-model claim.
- [x] S3 Implement a small read-only readiness contract and explicit operator CLI check using existing provider patterns; no browser readiness dashboard or automatic network check. Actual SDK-boundary and CLI deterministic tests passed in the96-case focused run; real configured metadata command subsequently passed after final A (one GET, ready_for_attempt; zero generation).
- [x] S4 Add deterministic readiness and concurrency/negative-path coverage without removing baseline tests.96 focused backend and12 new controlled browser cases actually passed;Initial221 backend/30 controlled identities were collected and every prior identity retained; three subsequent verifier regressions bring current backend collection to224.
- [x] S5 Prepare and audit the one-generation live command and evidence linkage. Strict metadata artifact/CLI content tests passed; the actual shared browser guard was exercised with two attempted requests/one forwarded/one blocked against the controlled real API/PG. No paid/live generation was invoked.
- [x] S6 Run targeted checks, isolated wrong-success experiment and full Gate A. Two failed A receipts preserved; locator and literal-identity causes fixed without assertion weakening. Final A actually passed224/60/30 and all14 commands0; current wrong-success actually exited1.
- [x] S7 Record source fingerprint2a2128d0f21c914b4640db6eb7c31ddf446ad00076a9a28e52d03bfcbe44b098, actual native exits, final preservation audit and A–J report. Readiness preparation GET actually passed and strict A linkage validated; Stage03 stays PARTIAL.
- [x] S8 Prepare the final concrete one-generation authorization question with exact command, model, caps, tariff scope and limitations. Paid B has NOT RUN and must wait for the owner reply.

## Boundaries

Readiness is point-in-time metadata/configuration evidence, never proof of generation, JSON grammar acceptance, quota, latency or persistence. Provider metadata is not a ProductManagerRun and must not mutate projects/plans or consume a generation admission slot. Stage03 remains PARTIAL until authorized current-source Gate B really passes. No model identity or usage is invented. All deterministic model doubles are labeled and real auth/PostgreSQL remain exercised.

## Initial approach

Reuse Settings, the official Google GenAI SDK, bounded HTTP transport, safe metadata classifiers, the existing operator config command and A/B/C receipts. The UI continues through its existing authorized Next proxy; readiness adds no endpoint or browser polling. Add an explicit --check-model operation only; never generate on load. Keep the existing generation lifecycle intact unless a concrete failing test proves a defect. SDK retries and transport retries stay disabled. Preserve historical503/504 and earlier successful evidence separately.

## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|---|---|---|---|---|---|
|1|Intake|Honor the owner's explicit implementation scope and stop only at the paid gate|Mechanical|P6|The user explicitly requests preparation, necessary changes and Gate A before approval|Extra generic plan reconfirmation|
|2|Intake|Use native Windows tools and degraded local skill artifacts|Mechanical|P3/P5|Startup helper is absent; do not repair global tooling for repository work|Global setup/telemetry changes|
|3|Intake|No nested Codex model probe or CLI paid review|Mechanical|P5|Current host is Codex and the task prohibits unapproved model-generation requests|An external model probe hidden inside review|
|4|CEO|Extend the existing config CLI with --check-model; no new API/UI|Mechanical|P3/P4/P5|Read-only diagnosis solves the operator problem without a new credential-backed browser surface|Dashboard/polling or duplicate CLI|
|5|CEO|Keep exact configured gemini-3.8-flash and record metadata limits separately from local budgets|Mechanical|P5|Real metadata supports generateContent; owner model remains explicit and unchanged|Automatic fallback/model switch|
|6|CEO|Readiness returns ready_for_attempt only for complete positive metadata and never certifies generation|Mechanical|P1/P5|Unknown metadata and failed external checks cannot establish live success|A generic ready/success indicator|
|7|CEO|Preserve90/95/100s budgets and diagnose503 as upstream unavailability|Mechanical|P5|Stored1537.654ms/HTTP503 is concrete evidence; increasing timeouts does not fix it|Unjustified timeout increases|
|8|Design|Preserve existing UI, add controlled upstream503/repeated-click regression only|Mechanical|P1/P5|Existing states are truthful; executable coverage is more useful than a new status badge|Unrelated style or recovery redesign|
|9|Design|Keep upstream503 separate from public502 and identify doubles clearly|Mechanical|P5|Current adapter intentionally maps provider unavailability to safe public502|Changing HTTP expectations merely to call a test503|
|10|DX|Keep default CLI configured0/missing1; explicit metadata ready0/non-ready2; safe invalid settings2|Mechanical|P4/P5|Existing scripts keep offline semantics; the new flag makes external metadata deliberate|A silent external call or misleading generic success|
|11|DX|Dispatch metadata once in execute_gate(B), never in recursive live-preflight/profile checks|Mechanical|P4/P5|Playwright invokes preflight again; moving I/O there would repeat checks|Hidden duplicate metadata or model calls|
|12|DX|Validate readiness content and block a second browser generation before forwarding|Mechanical|P1/P5|A final post-count assertion alone detects excess usage too late|Only detecting duplicate paid calls afterward|
|13|Eng|Bind readiness to exact A receipt hash, attempt, source/profile and in-attempt timestamps|Mechanical|P1/P5|A copied positive metadata artifact must not validate another attempt|Hash-only content validation|
|14|Eng|Use separate real HTTP clients and held-provider scheduling for exact-key replay|Mechanical|P1|Proves one admitted call and full graph under a genuine simultaneous API schedule|Sequential replays or shared-client inference|
|15|Eng|Observe after actual SQL child flush, then inject rollback and preserve unknown/interrupted semantics|Mechanical|P1/P5|Incomplete graphs must be invisible across sessions; don't rewrite uncertain commits as failures|Inspecting only root count or changing lifecycle for a green test|

## Phase1 CEO completion

[Primary11-section review](reviews/STAGE032_CEO.md) and [independent in-host voice](reviews/STAGE032_CEO_VOICE.md) completed sequentially before design. The independent voice's four medium refinements are absorbed: CLI-only scope, explicit typed semantics, current-source authorization package and effective budgets. Premises, alternatives, error/failure registries, architecture/UX diagrams, NOT in scope and temporal plan are written. No user challenge or taste disagreement remains.

| Dimension | Primary Codex | Independent Codex voice | Consensus |
|---|---|---|---|
|Premises|Metadata does not prove generation|Same|Confirmed|
|Right problem|Operator diagnosis + evidence|Same|Confirmed|
|Scope|CLI-only, no dashboard|Same|Confirmed|
|Alternatives|Probe/CLI/dashboard compared|Same|Confirmed|
|Risk|Quota and availability remain unknown|Same|Confirmed|
|Trajectory|One provider, no routing|Same|Confirmed|

This is same-family independent review, not cross-model agreement. Nested CLI passes are skipped inside Codex; no paid review/model probe is performed. The existing architecture and explicit owner brief serve as design input; no unrelated office-hours exercise is needed.

## Planned readiness contract

`scripts.check_pm_config` remains offline by default. `--check-model` performs at most one official SDK models.get request with10s HTTP/server and12s outer budget, SDK attempts1, HTTP transport retries0, fixed Google endpoint, no redirects/proxy/pagination and bounded response bytes. It never calls generate_content, count_tokens, tools, a project route or PostgreSQL. A typed result reports not_configured, invalid_configuration, model_not_supported, credential_error, provider_unavailable, rate_limited, timeout, ready_for_attempt or unknown; only complete positive metadata for the exact configured model can be ready_for_attempt. Returned metadata alone never proves structured generation, quota or live availability. `live_generation_verified` is always false; missing fields remain unknown. The CLI reports safe problem/cause/fix and the effective local budgets, with no exception body or credential output. Explicit metadata check exit0 means ready for a separately authorized attempt; other states exit2. Default configuration-only compatibility is retained.

Gate B must capture one fresh readiness artifact after opt-in/current A/profile validation and before the single generation; a non-ready check stops without a paid dispatch. The artifact is hash-manifested and source/profile-bound, but never substitutes for real live-proof/SQL/browser assertions. Add a test-only browser transport guard that aborts any second generation POST before dispatch and records the count. Reuse the same actual generated plan for every draft/edit/approval/isolation assertion. No new paid request is authorized by this plan.

The metadata operation is a separately recorded native `provider-readiness` command in B, followed by `live-browser`. Its actual argv, stdout, start/completion and native exit are captured, rather than inventing an exit for an in-process operation. Nested preflight and Gate C only validate the stored result and never refetch metadata.

## Phase2 design completion

[Primary7-pass review](reviews/STAGE032_DESIGN.md) and [independent in-host review](reviews/STAGE032_DESIGN_VOICE.md) completed before DX. Retain current project panel, theme tokens, native fields, actual waiting/error state and GET-only unknown recovery. No UI source change is required; add one controlled upstream503 browser scenario on desktop/mobile/tablet with public502, one POST despite repeated clicks, preserved brief/approval and no fabricated plan. The fallback HTML sketch was actually rendered and viewed but remains explicitly authored design input, not application evidence. Both reviewers found no design blocker or taste disagreement.

| Litmus | Primary | Independent | Consensus |
|---|---|---|---|
|Recognizable ORBA workspace|Yes|Yes|Confirmed|
|Plan visual anchor|Yes|Yes|Confirmed|
|Scannable hierarchy|Yes|Yes|Confirmed|
|One job per section|Yes|Yes|Confirmed|
|No unnecessary new cards|Yes|Yes|Confirmed|
|Only truthful waiting motion|Yes|Yes|Confirmed|
|No shadow-dependent hierarchy|Yes|Yes|Confirmed|

Scores are source/design judgments, not measured usability or passing browser counts. A safe public502 for upstream503 is the established contract and must remain explicit in test/report wording.

## Phase2.5 DX completion

[Primary8-pass review](reviews/STAGE032_DX.md) and [independent review](reviews/STAGE032_DX_VOICE.md) completed before engineering. Nine-stage journey, first-person narrative, exact exits, safe-error contracts, command location, target12-second metadata envelope and documentation checklist are written. Both reviewers agree on six areas: actionable root command, consistent CLI names, safe problem/cause/fix, findable docs, non-breaking upgrade and isolated deterministic environment. All six are agreement between same-family source reviewers, not live service or measured onboarding evidence. Cold install and other platforms remain unmeasured. Existing README/architecture and observed local metadata are the references; no fabricated competitor timings are used.

The explicit implementation and Gate A are already authorized by the owner, so the generic review reconfirmation does not add an earlier stop. The sole upcoming approval is the paid one-generation gate required by the owner, after actual verification and a concrete report. No new model or broader scope challenge is proposed.

## Phase3 final engineering completion

[Primary engineering review](reviews/STAGE032_ENG.md), [independent engineering voice](reviews/STAGE032_ENG_VOICE.md) and [full test plan](STAGE032_TEST_PLAN.md) are written and read. The external test artifact is C:/Users/vaish/.gstack/projects/OBRA/vaish-main-eng-review-test-plan-stage032-20261020.md. Five independent acceptance refinements are absorbed: strict readiness linkage, real-SDK synthetic GET boundary tests, synchronous pre-await browser dispatch counts, separate-client exact-key scheduling and actual child-flush rollback observation. No unresolved implementation decision requires owner clarification; paid execution remains explicitly unapproved.

| Dimension | Primary | Independent | Consensus |
|---|---|---|---|
|Architecture|Small operator-only diagnostic|Sound with exact artifact linkage|Confirmed with refinement|
|Tests|Full branch/flow plan|Add exact schedules/GET cleanup tests|Confirmed with refinement|
|Performance|One bounded metadata GET; no DB hold|Same|Confirmed|
|Security|No new public surface; safe allowlist|Same|Confirmed|
|Errors|Unknown remains unknown; preserve503|Same|Confirmed|
|Rollout|No migration/credential change; fresh A|Same|Confirmed|

## Cross-phase themes and approved preparation

Every phase identified the boundary between metadata readiness and real generation; none recommends bypassing the live gate. CEO/DX/Eng independently require one explicit action, source/profile-linked evidence and safe failure preservation. Design/DX/Eng require pre-dispatch protection and existing UI/approved data preservation. These are same-family source-review agreements, not independent provider verification. Broader provider routing, monitoring, auth-copy and production work remain in existing TODOS; nothing new is silently deferred.

The owner's Stage03.2 request authorizes S3-S7 implementation and deterministic checks. Phase4's generic approval is satisfied for that already-requested preparation; S8 remains the sole actual stop before any paid generation. No taste overrides, user challenges, model switch, commits or new stage are proposed.

## Authorized live execution:2026-10-20

The owner subsequently authorized one bounded attempt on source2a2128d0f21c914b4640db6eb7c31ddf446ad00076a9a28e52d03bfcbe44b098. The command ran once: metadata0, real browser1, upstream504 DEADLINE_EXCEEDED in88.825025s, failed run/zero plans. Editing, approval and live isolation were not reached. Gate C actually returned2/PARTIAL. Source, credentials and historical receipts remain unchanged. That authorization is consumed; no additional paid request, implementation change or Stage04 work is authorized. Current evidence is in VERIFICATION.md. Earlier review/preparation statements above are the historical pre-authorization plan state.

## GSTACK REVIEW REPORT

| Runs | Status | Findings |
|---|---|---|
|CEO|DONE|11 sections, six same-family dimension agreements; CLI-only scope|
|Design|DONE|7 dimensions/litmus; preserve interface and execute distinct controlled failures|
|DX|DONE|8 dimensions/9-stage journey; explicit offline/metadata/paid boundaries|
|Engineering|DONE|Four sections, five concrete acceptance refinements, coverage diagram and test artifact|
|Preparation verification|DONE|Final A PASS224/60/30,14 commands0; exact-model metadata GET0/current-A linkage valid; wrong-success native1; prior failures preserved; authorized B FAIL1/upstream504; Gate C PARTIAL2|

VERDICT: Review and requested deterministic preparation complete. Current A and metadata readiness passed; preservation audit passed. Stage03 remains PARTIAL; the subsequently authorized single B failed upstream504 and exited1, C returned2. No further paid call is authorized.

NO UNRESOLVED DECISIONS
