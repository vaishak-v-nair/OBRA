# Stage03.3 independent design voice

Date: 2026-10-20. Independent in-host Codex-family source review. Reviewed STAGE033_PLAN.md, STAGE033_DESIGN.md and ProductPlan; checked the existing semantic CSS, API error presentation, current size rejection and controlled recovery test source where relevant. No skill files, application edits, test execution, browser session, external requests or model calls were used. This is a design review, not rendered or live-model verification.

Verdict: no P0/P1 design blocker. The server-only model policy, request-byte guard and lean generation grammar fit the existing product without a new screen or model selector. One P2 clarification should join D1 before implementation. The seven dimensions below agree with the primary review's scope, with no cross-model consensus claimed.

## Finding DV1 - P2: Make combined-byte rejection actionable

The proposed 48000-byte envelope includes the prompt, provider schema and snapshot. ProductPlan's 10000/4000-character controls cannot predict this combined limit, especially with Unicode or saved-plan context. The current API text is only "The combined planning input exceeds its size limit." ProductPlan displays that safe server message directly; it already recognizes input_too_large as rejection before admission and preserves the form.

Add an explicit recovery-copy requirement to D1: the API's input_too_large message should explain that no generation was started and suggest shortening the brief or instructions, or excluding the saved version as context. Keep the existing error code and do not expose private input, provider bodies or internal grammar. A character/byte counter or frontend redesign is unnecessary.

Verification acceptance: extend a labeled controlled-provider browser negative path to receive the actual new API rejection, retain exact brief/instructions/context selection and the selected approved plan, clear the rejected request reference, show an actionable alert and permit a later deliberate submission. Real-PG boundary/Unicode tests must separately establish zero admitted run/plan/provider call for this rejection. These are recommended checks; none were executed by this review.

## Seven-dimension assessment

| Dimension | Assessment and acceptance condition |
|---|---|
|1. Information hierarchy|Examined, no issue. Brief, actual request outcome and saved document remain the main anchors. Model/thinking choices stay in operator configuration; readiness metadata must not displace the saved plan or become a generation-success badge. Preserve historical requested/returned model values rather than relabeling old versions with current Settings.|
|2. Loading, empty, error, success and unknown states|Examined, DV1 above. Existing loading/status regions, explicit paid action, error alert, empty explanation and saved-draft notice are distinct. Unknown UUIDs remain GET-only; exact own terminal-run confirmation precedes Retry. New size rejection must remain a known pre-admission event, without an invented failed run. Configuration validity or metadata GET success cannot produce a draft-success notice.|
|3. End-to-end journey|Examined, no issue. Open project, explicitly generate, wait, recover, review/edit/save and approve retain clear actions. Failure preserves the current in-memory brief and previous plan; explicit authorized Restore submitted brief remains the only restoration after navigation. No browser-storage brief, automatic POST retry, model fallback or page-load generation is introduced. Approved versions and exact-revision approval remain authoritative.|
|4. Specificity and unnecessary decoration|Examined, no issue. The proposal addresses exact configuration and request limits without agent avatars, simulated progress, generic health cards or a Model Hub. Grammar reduction must remove only generation-inappropriate authority hints; every required PRD field and server validation remain. Smaller grammar or lower thinking are hypotheses for a future trial, not claims of faster or more reliable results.|
|5. Existing theme and component alignment|Examined, no issue. ProductPlan already uses Button, native form/details controls and semantic surfaces, text, primary, border and danger tokens. The scoped changes need no new color, font, spacing system or shared abstraction. Preserve current Soft Minimal/Graphite Mint behavior.|
|6. Responsive behavior and accessibility|Examined, no new scoped issue. Source contains labeled inputs, native selects/details, focus rings, alert/status semantics, wrapping actions, long-reference wrapping, one-column mobile document layout and reduced-motion rules. The new server error should continue through the existing alert. Source inspection does not establish measured contrast, screen-reader behavior, native-device support or all-browser compatibility; rerun mandatory browser coverage in Gate A.|
|7. Unresolved decisions|No owner taste decision blocks this plan. Adopt DV1 as a mechanical recovery clarification. Keep exact supported model/thinking settings and byte-envelope composition documented for operators, including fail-closed invalid Settings/startup impact. A future recommended model is an explicit owner-authorized trial; account metadata cannot resolve generation quality, schema acceptance, latency, quota or persistence.|

## Preservation and verification boundary

The plan preserves honest upstream 503/504 outcomes, safe diagnostics, failed/unknown separation, retained input, atomic validated draft success, immutable approvals and historical evidence. Require the proposed real-PG configuration-change history regression and existing recovery/reload/isolation coverage to demonstrate those promises. Keep historical failed Full/standalone receipts and source/profile binding; new Gate A cannot certify live generation, and old live evidence cannot certify changed source.

Do not add UI work merely to act on this review. Record DV1 in the implementation/test plan, run Gate A after implementation, then present the concrete single-generation configuration for fresh explicit paid authorization. This review performs no generation and does not change PARTIAL into VERIFIED.
