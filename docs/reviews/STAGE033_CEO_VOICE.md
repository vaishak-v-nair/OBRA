# Stage03.3 independent CEO review

Date: 2026-10-20. Reviewer: independent in-host Codex-family voice. This is a source-and-artifact review, not a second provider, live-generation experiment, executed test result or cross-model consensus. I did not execute tests, call external APIs, read credential values or change implementation/configuration/history.

## Material inspected

- `docs/STAGE033_PLAN.md` and `docs/reviews/STAGE033_CEO.md`.
- `docs/evidence/stage033-research-20261020/model-metadata.json` and `offline-before.json`.
- Current `orba/config.py`, `pm_provider.py`, `pm_schemas.py`, application construction in `main.py`, and readiness/verification references.
- The latest Gate B receipt at `docs/evidence/stage031/20261020T090120Z-B-0f70b66f/receipt.json`.

The model-metadata artifact records three exact-model HTTP200 metadata GETs, one attempt each, no generation, and account-visible `generateContent` plus advertised input/output bounds. Its alternative-model status is still `unknown` under the existing one-model readiness policy. That is consistent with preparing a reviewed policy; it is not successful execution evidence. The recorded grammar measurements are useful offline size measurements, not measured Gemini token counts or provider-side processing time.

## Recommendation

Proceed with the small explicit model policy and bounded request preparation, after the concrete amendments below. Do not reframe the product, add retries/routing, or spend on generation during this task. No P0 or P1 strategic defect was found. The proposed work can improve configuration correctness and observability; whether it improves live completion or planning quality remains unknown until a separately authorized Gate B.

## Findings

### CEO-V1 - P2: Add an explicit configuration-change history regression

**Evidence:** The owner's model-selection requirement includes preserving run history across configuration changes. The primary review says history remains untouched, but its test map lists per-model settings/SDK cases and failed-regeneration preservation without explicitly testing retrieval of an older run and approved plan under a different current model configuration. Current runs store model provenance separately from runtime `Settings`; a new allowlist must not accidentally become a validator for historical records or UI retrieval.

**Consequence:** Correct new-generation dispatch can pass while old evidence becomes inaccessible or is mislabeled by the current configured model. That would undermine the audit trail which differentiates ORBA's real execution from a chat simulation.

**Concrete fix:** Add a deterministic real-PostgreSQL regression that persists a run/plan with one requested/returned model, changes only the runtime configuration to a different approved model, and retrieves the prior run and approved plan through the authorized API. Assert the old model metadata, plan version/revision/content and approval actor/time are unchanged. The fixture/provider double must remain explicitly labeled deterministic evidence. Do not generate again to perform this test. The static selection policy should apply to new requests, not rewrite or reinterpret historical model strings.

### CEO-V2 - P2: State the operational scope of stricter Settings validation

**Evidence:** `create_app()` constructs `Settings()` before building the API and database engine. Adding an approved-ID/compatible-thinking validator to `Settings` can therefore fail application startup for a syntactically valid but newly unapproved PM configuration. The primary error registry promises no provider dispatch and a safe CLI error, but does not explicitly tell the operator that the entire API may remain unavailable until this configuration is corrected. Empty PM configuration is a distinct supported setup state and must remain so.

**Consequence:** An operator could understand an unsupported PM model as a disabled planning feature while unexpectedly losing local sign-in/project access after restart. Data is not lost, but the operational impact exceeds the apparent PM-only change.

**Concrete fix:** Make this an explicit fail-closed configuration decision in the plan and README, with an offline pre-restart `scripts.check_pm_config` procedure and safe corrective configuration guidance. Preserve the missing/empty-provider application's ability to start and the existing 15-character credential/session behavior. Test missing configuration separately from invalid configuration. Do not add a fallback model or silently ignore an unsupported choice to keep startup green. Isolating PM configuration further would be a separate architectural choice; it is not required merely to resolve this documentation gap.

### CEO-V3 - P2: Publish the recommendation as a bounded hypothesis, with a complete comparison artifact

**Evidence:** The primary review recommends `gemini-3.6-flash` with `minimal` thinking for a later attempt. The inspected fresh account metadata proves exact metadata visibility but does not establish alternative-model structured-output acceptance, latency, quality, quota or usable output at that thinking setting. The primary review acknowledges these limits; the final comparison and authorization request must preserve that precision. Current offline sizes do not demonstrate why an upstream504 occurred.

**Consequence:** A concise final recommendation could unintentionally overstate an older or lower-thinking model as more reliable, making the next paid call look like a verified fix rather than a controlled trial.

**Concrete fix:** Before asking for paid authorization, publish a dated three-model comparison with direct official references for structured output, supported thinking settings, lifecycle and prices, plus a separate column for this account's read-only HTTP200 metadata. Label lower thinking and leaner grammar as plausible ways to reduce avoidable work, not proven causes or latency improvements. State that `gemini-3.6-flash` is recommended for a single bounded trial, retain `.env` on the owner's current3.8 choice, and show the exact explicit override needed for any new model authorization. Output-token-only exposure may be calculated from documented pricing; full billing remains uncertain without actual input/usage and applicable account terms.

### CEO-V4 - P3: Keep task state and budget semantics concrete

**Evidence:** S1 and S2 remain unchecked even though intake and research artifacts now exist. The proposed complete request-byte envelope includes prompt, grammar and snapshot, whereas the current implementation's character bound applies to snapshot content. A48000-byte combined envelope is consequently a new admission contract, not just an implementation-equivalent rename.

**Consequence:** Stale checkboxes obscure progress, and operators could interpret new rejection of a previously admissible long or multibyte brief as a provider failure. A byte bound also must not be presented as an exact Gemini token count or dollar ceiling.

**Concrete fix:** Update task status only with links to actual receipts. Document exactly which canonical bytes count toward the new envelope, why the initial bound was chosen, what error occurs before provider dispatch, and how the retained brief can be shortened. Add exact-boundary and multibyte tests without private content in logs. Retain every required PRD field and the full independent schema/graph checks. Keep any observed request-size reduction separate from claims of provider reliability.

## Premises and reframing

The review chooses the right problem: make one planning request explicit, bounded and auditable while preserving truthful failure handling. The product concept does not need expansion. A healthy metadata response and a smaller schema are intermediate evidence, not the desired product outcome. The current failed0-plan behavior is a security and integrity success even though Stage03 remains incomplete.

The proven root cause should remain phrased as an upstream HTTP504 error on this request path. The server timeout header makes a deadline-related provider response unsurprising, but does not identify which provider component consumed the budget or establish that a different thinking level would finish. The fast prior503 also prevents a single local90-second-timeout explanation for all historical failures. No additional paid experiment is needed to reach these conclusions.

## Alternatives and scope

| Choice | Independent assessment |
|---|---|
|Documentation-only, arbitrary syntactically valid model IDs|Too narrow: does not meet the explicit validated-selection requirement and leaves thinking compatibility ambiguous.|
|Three reviewed explicit choices, model-compatible thinking and one request envelope|Appropriate if implemented as a small policy, strict tests and clear setup errors. This is not a runtime routing engine.|
|Retries, fallback routing, split multi-call generation, long-lived pool or Model Hub|Reject for this task: violates or exceeds the one-call/manual-selection boundary and lacks measured justification.|

The time spent changing schema hints is justified only while the change remains small, keeps the authoritative PRD contract, and has precise omission/security tests. Avoid a speculative redesign of the document or prompt solely to optimize unmeasured latency.

## Cost and authorization boundary

- Current authority permits deterministic work and bounded read-only metadata, not generation.
- Existing3.8 authorizations are exhausted; they cannot be reused for a new source fingerprint or3.6 model choice.
- One future B must reuse its single generated plan for schema, API, independent SQL, browser display, editing, approval and outsider isolation. No extra generation for setup or a standalone API probe.
- A passing A and a fresh readiness GET are insufficient for VERIFIED. A new relevant-source live B is required; preserve all previous failed receipts.
- A failure of the next future B must remain failed, with no automatic retry, model switch, dummy document or shifted test expectation.

## Six-month regret assessment

The largest regret would be an allowlist presented as permanently accurate, or a configuration tweak reported as an upstream availability fix. Dated documentation, explicit review/update procedure, unchanged historical model fields and source/profile-bound evidence limit this risk. A second regret would be growing this into a Model Hub before one real planning flow has passed. The scoped static table is reversible and does not create that obligation.

## Completeness, consistency, clarity and feasibility

| Dimension | Assessment |
|---|---|
|Completeness|Covers requested diagnostics, model options, bounded generation, strict persistence, real-PG negatives, A/B/C and paid stop. Add the explicit cross-configuration history test.|
|Consistency|No conflict with Stage03 authority or no-paid boundary. Clarify invalid Settings startup scope and ensure only new-dispatch model selection is constrained.|
|Clarity|Evidence versus hypotheses is strong. Final comparison and byte-budget docs must retain the same care; update completed task state.|
|Feasibility|Local additive work fits existing adapter/readiness/verifier architecture. No migration, account reset, secret mutation or new service is needed. Live reliability remains externally dependent.|
|Strategic fit|Preserves the genuine planning-agent concept and the human review/approval boundary. No product reframing or new agent is warranted.|

## Review disposition

No user taste decision or additional preparation permission is needed. Resolve the P2/P3 amendments mechanically in the plan, implementation tests and documentation, then proceed to design/DX/engineering review. This review does not authorize any paid request, validate a model response or change Stage03 from PARTIAL.
