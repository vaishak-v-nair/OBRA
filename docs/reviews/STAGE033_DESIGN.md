# Stage03.3 design review

Date2026-10-20. APP UI, seven passes. Source review of product-plan.tsx, plan-editor.tsx, semantic CSS, PM API error contract and existing core/controlled browser tests; no new live visual or AI execution claimed. Initial completeness8/10; amended plan9/10. Ten would require fresh rendered/device evidence; deterministic emulation is not native hardware. No new screen or model selector is in scope. External mockup designer is unavailable, so the diagrams below are authored specifications, not screenshots. Preserve existing ORBA design even where generic skill aesthetics would prefer another font/layout.

## Existing vocabulary and scope

Use ProductPlan, PlanEditor, existing Button/error alerts, session/workspace shell and globals.css. DESIGN.md is not the authority for a redesign here: the owner's Soft Minimal/Graphite Mint tokens and existing responsive implementation are. Config readiness remains operator-facing; normal page loads must not call metadata or generation. No decorative cards, fake progress, new onboarding wizard or public model picker.

## Pass1: Information architecture (9/10)

```text
project overview
  Product Plan
    brief + optional instructions/context
    explicit Generate / terminal-confirmed Retry
    real status/error + run reference
    selected persisted version -> overview -> requirements -> epics/stories/criteria
    edit draft / explicit version+revision approval
    history -> previous immutable plan / original generation metadata
```

The three anchors are brief, actual outcome, and saved plan. Metadata availability belongs in operator docs, not a success banner above an empty plan. Current source exposes requested/returned model in run history; changing runtime model must not relabel historical plans. Test the latter with real-PG/API retrieval rather than a decorative UI label.

## Pass2: Interaction states (9/10)

| Feature | Loading | Empty | Error | Success | Partial/unknown |
|---|---|---|---|---|---|
|Generate|Busy text, disabled submit; no percentage|Brief prompt with explicit paid action|Safe unavailable/rate/timeout/validation message and run reference|Validated saved draft announcement only after API success|Retain UUID; Check status GET only|
|Input bound|Synchronous field/API handling|No brief -> visible validation|422 before admission, retained brief, shorten input|Only admissible request reaches model|No invented failed run for rejected input|
|Recovery|Check status labelled busy|No matching run -> outcome unconfirmed|Terminal own run confirms explicit retry; no POST loop|Saved plan confirmed by server|Unknown stays GET-only; no second generation|
|Plan edit/approve|Save/approval disabled while busy|No plan -> useful generation explanation|Draft edits retained on conflict/failure|Saved revision/actor/time reflected after reload|Inspect latest saved revision without replacing local draft|
|Operator configuration|No automatic network probe|No provider -> setup instructions|Invalid ID/level needs correction before restart|Metadata only ready for an authorized attempt|Unknown remains unknown; no generated plan|

No new states require frontend implementation. Existing product-plan.tsx already recognizes input_too_large as authoritative pre-admission rejection and keeps in-memory input. New API tests must preserve that error code. Regenerate failure must leave the previous approved version visible.

## Pass3: Journey and emotional arc (9/10)

| Step | User action | Likely feeling | Concrete support |
|---|---|---|---|
|1|Open project|Orientation|Existing brief and current version first|
|2|Choose Generate|Agency/cost awareness|No generation until explicit submit|
|3|Wait|Uncertainty|Truthful busy state; bounded server request|
|4|Receive503/504|Frustration|No-new-plan safety statement, retained brief/approval, actual failed run|
|5|Check or retry|Cautious control|Own terminal confirmation; explicit new UUID only|
|6|Review/edit/save|Ownership|Provenance and observable acceptance criteria|
|7|Approve/reload|Trust|Exact revision, actor and timestamp from PostgreSQL|

At5seconds the user understands the next action; at5minutes a failure has not destroyed input; years later retained versions explain decisions. No copy claims faster generation before live evidence.

## Pass4: Intentional UI / slop (9/10)

Brand first screen:yes via shell. Visual anchor:project brief/plan content. Scannable headings:yes. Each section one job:yes. Cards only for grouped document content:existing restrained treatment. Motion useful:busy indicator only. Understandable without decorative shadows:yes. These are source judgments, not fresh visual measurements. Do not add generic feature grids, agent avatars, animated execution steps, or success badges from metadata.

## Pass5: System alignment (9/10)

Keep existing semantic surfaces/text/accent and theme switch. No new colors/components are necessary for server-only model policy. Errors continue through existing role=alert/form-note patterns. Alternative thinking appears in operator configuration and run diagnostics, not raw provider bodies. Preserve existing text and spacing unless a real browser defect is demonstrated in A; no taste-driven redesign.

## Pass6: Responsive and accessibility (9/10)

Retain desktop rail and mobile navigation, wrapping action groups, readable plan editor and long error references. Labels remain visible, focus styles and keyboard controls stay native; approval confirmation explicitly names version/revision. Existing browser projects cover desktop/mobile/tablet emulation and themes. Full A must rerun them sequentially with backend PG tests. These checks do not certify all browser engines, native devices or measured contrast; no new accessibility score is fabricated.

## Pass7: Decisions (9/10)

No product taste change is needed. Mechanical decisions: keep current UI, keep input_too_large, expose no secret configuration, and preserve the exact failed/unknown distinction. Recommend3.6/minimal only as a future operator trial in docs, not an automatic user-visible fallback. Remaining live visual quality/latency is an explicit verification limitation, not an unresolved implementation choice.

## Implementation tasks and verification

- D1 (P1): Preserve pre-admission error code and retained input; verify API exact-byte boundary and existing controlled browser recovery/rejected-admission tests.
- D2 (P1): Preserve approved plan and run metadata under configuration changes; real-PG regression plus existing browser reload/history coverage.
- D3 (P2): Document operator-only selection and honest metadata/failed/unknown semantics; no UI redesign.

No new design-debt TODO is warranted beyond the existing live/device limitations. Full GateA and a future paid GateB remain separate. Await independent design voice before DX.
