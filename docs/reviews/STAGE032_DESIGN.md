# Stage03.2 design review

Scope: the existing ProductPlan generation/recovery interface, not a redesign. New readiness is an operator CLI and adds no frontend badge, endpoint, polling or model call. Read product-plan.tsx, lib/pm.ts, controlled recovery tests and globals.css. This is a static review; execution evidence will come from Gate A.

## Scope and existing patterns

Initial design completeness8/10 for this bounded change. No standalone DESIGN.md was found; AGENTS, owner palette and globals.css remain design authority. Preserve existing Button, textarea/label, role=status/alert, PM history, explicit approval and theme tokens. The designer binary is absent; an authored fallback sketch was rendered/viewed at C:/Users/vaish/.gstack/projects/OBRA/designs/stage032/states.html and states.png. It illustrates existing failure/unknown hierarchy, not a screenshot/test result or generated PRD. One initial sketch command failed from an incorrect relative uv directory; native corrected command exited0.

## 1. Information architecture:8/10

The primary object is the saved Product Plan, with the current brief and explicit Generate above it and run history below. An approved plan must remain visible while failure copy sits beside its generation form; do not replace the document with a provider status panel. Existing setup text states configured credentials do not guarantee access. CLI readiness details belong in setup documentation, preserving the main user's planning task.

```text
Project overview
  Product Plan heading + explicit usage disclosure
  Brief / optional instructions / explicit Generate or Retry
  Actual error + reference / GET Check status
  Saved version / draft or approved / document / edit and approval
  Run history (actual states only)
```

## 2. State coverage:8/10

| Feature | Loading | Empty | Error | Success | Partial/unknown |
|---|---|---|---|---|---|
| Generation |Waiting for ORBA; no percentage|Brief and explicit CTA; no generated content|Safe provider message + actual run reference|Validated saved draft, never auto-approved|GET Check status; Generate disabled, UUID retained|
| Saved plan |Loading saved plans|Requirements start here|Read/save errors keep current local draft|Actual persisted version/revision|Inspect latest without replacing editor revision|
| Retry |Only during user-submitted operation|No retry before known terminal run|503/429/504/validation remain distinct first-response errors|A new run only after deliberate click|Unknown outcome cannot unlock a new POST|
| Readiness CLI |Bounded metadata request only|not_configured|Safe diagnosis/fix|ready_for_attempt, generation_verified=false|unknown when non-generative evidence is incomplete|

Initial server503 copy is useful, but after GET recovery `runFailure` falls back to the category rather than the full initial sentence. It remains truthful and clearly states no draft was created; broad copy refactoring is unnecessary. Add a focused controlled503 browser case to verify brief/approval survival and repeated-click behavior across all three viewports.

## 3. User journey:8/10

| Step | Action | Likely feeling | Support |
|---|---|---|---|
|1|Open project|Need orientation|Current brief and saved version|
|2|Choose Generate|Concern about usage|Explicit action and cost disclosure|
|3|Wait|Uncertainty|Truthful waiting label; no fake steps|
|4|Receive provider failure|Concern about lost work|No new plan saved; original brief and approval retained|
|5|Check status|Need confirmation|Exact own run, GET-only recovery|
|6|Choose Retry|Control over extra usage|New recorded request and warning|
|7|Review/edit/approve|Need ownership|Exact persisted version and explicit approval|

The first5seconds should orient the user to their project rather than diagnose Google. The next5minutes should let them safely recover without retyping. Long-term trust comes from preserved failures and immutable approvals, not decorative badges.

## 4. Specificity and AI slop:9/10

This is task-focused app UI, not a marketing landing page. No hero/card grid, decorative icon system, fake progress, optimistic success or extra dashboard is introduced. Existing finite-state controls convey actual operation status and use the current layout. The fallback sketch is expressly labeled authored and cannot enter gate evidence.

## 5. Theme and component alignment:9/10

Soft Minimal uses existing background/surface/foreground/primary tokens; Graphite Mint uses the same semantic roles under .dark. No colors, typography, borders or components need modification to support an operator command. The repository's existing Arial/14px baseline differs from generic skill preferences; the owner's explicit instruction to preserve the design governs this focused stage. Do not change global typography or theme tokens here.

## 6. Responsive/accessibility:8/10

Existing PM fields have persistent labels and native textarea/button semantics; alert/status regions expose errors and operation updates. Mobile PM buttons use44px minimum targets, the overview collapses and the current navigation focus behavior stays intact. Re-run desktop/mobile/tablet Chromium cases and theme/overflow assertions; these establish emulated coverage, not native-device/all-browser certification. No new browser interaction means no additional tab order or modal is needed.

## 7. Unresolved decisions:9/10

The plan now specifies exactly where readiness lives, what its limited success means and when a retry is permissible. Empty, failed and unknown generation states use the existing controls, so no aesthetic choice or generic status badge remains to invent. Only owner authorization of a later single paid attempt remains; that is a usage gate, not design indecision. Existing auth-copy TODO remains outside scope.

## Litmus scorecard

| Check | Primary assessment |
|---|---|
|Product recognizable|YES: ORBA workspace and Product Plan|
|Visual anchor|YES: project and plan headings|
|Scannable|YES: brief, error, saved state, actions|
|Each section has a job|YES; no readiness dashboard added|
|Cards necessary|No new cards; existing saved-object grouping retained|
|Motion useful|Only actual waiting indicator, no decorative progress|
|Works without shadows|YES: tokens, type and spacing carry hierarchy|

NOT in scope: typography refresh, Model Hub dashboard, automatic provider polling, UI model switching, auth-network copy and unrelated pages. What already exists: semantic tokens, project panel, native controls, keyboard states and meaningful controlled tests. No additional deferred item is needed because the existing Model Hub/auth TODOs already cover broader concerns.

## Implementation tasks and completion

- T1(P1,human1h/agent15min): add a labeled controlled503 browser case with real auth/API/PostgreSQL, repeated click count1, brief/approval preservation, no new plan and GET recovery. No real provider call.
- T2(P1,human30min/agent10min): document metadata readiness as an operator diagnosis without a generated-success state, keeping exact live opt-in separate.

All7 passes were evaluated. Static review supports preserving product UI; no new UI component is proposed. Independent review and consensus are recorded in the main plan before DX begins.
