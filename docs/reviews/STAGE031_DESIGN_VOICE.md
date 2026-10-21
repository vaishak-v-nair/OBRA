# Stage03.1 independent design review

Source: independent in-host Codex-family review. This is a separate review perspective within the same host/model family, not outside-model consensus.

Scope: `AGENTS.md`, `docs/STAGE031_PLAN.md`, `apps/web/src/components/product-plan.tsx`, `apps/web/src/lib/pm.ts`, `apps/web/src/lib/api.ts`, and `apps/web/src/app/globals.css`. No earlier review artifacts, skills, credentials, or `.env` files were read. No tests, services, browser sessions, model calls, database actions, or Git writes were performed. The findings below describe source behavior and proposed acceptance cases; they do not establish rendered or live verification.

Design assessment: **changes requested**. The plan's GET-only recovery and explicit fresh-identity retry direction is appropriate. It needs a concrete state/action contract before implementation. Keep the existing ORBA Product Plan panel, shell, typography, semantic theme tokens, native controls, and Button component. This work does not justify a redesign, another agent, or Stage04.

## Concrete findings

### D1 — High: an unknown outcome can currently be released into another paid request

Evidence: `product-plan.tsx:79`, `:93-108`, `:120`, `:132`, and `:138`. “Clear request reference” removes the local UUID without confirming that its exact run reached a terminal state. Its `active` guard depends on the currently loaded run page. A missing record, stale list, failed refresh, or unconfirmed transport outcome is not terminal evidence.

Fix: retain the account/project-scoped request UUID while its outcome is unknown. Recovery actions perform GETs only. Remove the clear-reference action from this state. A failed status read or no matching run must keep generation and paid retry unavailable. A confirmed `succeeded` run leads to its saved plan; a confirmed `failed` or `interrupted` run may offer an explicit retry. Before that retry, obtain fresh authoritative status for the exact tracked request, then allocate a new UUID for the single user-triggered POST. An HTTP error or elapsed client clock alone must never unlock it.

Put the distinction in visible copy: “We could not confirm this request's outcome. Check status before starting another request.” A terminal failure can say “This run ended without creating a draft. Retry starts a new model request and may incur usage.” Previous usage must not be described as refunded or absent.

### D2 — High: a saved result can be presented as an unconfirmed generation failure

Evidence: `product-plan.tsx:85-90`. A successful generation response clears the pending reference before `load()` refreshes the plan and run lists. If those GETs fail, `action()` displays an error; the saved result's recovery linkage is no longer held as pending, and the success notice was never set. `api.ts:28` also labels every failed PM request, including GETs, as an unconfirmed operation.

Fix: retain the confirmed run ID, result plan ID, and success outcome independently of follow-up display loading. Report “Draft saved. ORBA could not refresh the view.” Offer GET-only reopening/refreshing of that saved result. Do not display generation failure or offer retry as the remedy for a failed refresh. Keep the previously displayed plan visible until the new plan loads. An existing approved version remains immutable and available throughout.

### D3 — High: “preserve brief/instructions” needs an explicit restoration contract

Evidence: `product-plan.tsx:42-44`, `:54-55`, `:68-69`, `:72`, `:84-85`, and `:127-130`; `pm.ts:14-16`. Current form text survives same-page errors, but a reload initializes the brief from the original project description and clears additional instructions. Only UUID references are stored. The client `Run` type exposes no submitted input snapshot; the available `Plan.inputs` snapshot exists only with a saved plan. The unsaved-change warning tracks plan editing, not generation form text.

Fix: treat current form text and the last submitted snapshot as distinct. Keep current edits during all status checks. Offer **Restore submitted brief** as a separate, explicit action after a terminal failure; it restores the submitted brief and instructions only after making any overwrite of current edits clear. It must not automatically replace current edits when a GET completes or when Retry is clicked. Make Retry's input source explicit: the visible current form, unless the person first restores the submitted input.

If restoration must work after reload, expose the saved snapshot through an authenticated, membership-checked run read contract. Do not put briefs/instructions in sessionStorage, localStorage, URLs, diagnostics, or logs. Store only the permitted scoped UUID reference. Preserve and show the submitted context plan/revision when relevant; do not silently replace it with a newly selected or newer revision. If restoration is deliberately limited to the current page, the plan must state that limitation and guard unsaved form navigation; it cannot claim reload preservation.

### D4 — Medium: status semantics currently imply more certainty than the client has

Evidence: `product-plan.tsx:90`, `:99-103`, `:135`, and `:137`; `api.ts:26-39`. All notices use a green Check icon, including “No matching run was found yet,” “Planning is running,” and “Status refreshed.” “The provider request is running” appears as soon as the POST starts, before the client has authoritative provider-phase evidence. An HTTP 504 with a non-JSON body falls back to “Something went wrong. Please try again,” which does not explain the outstanding request.

Fix: use neutral information styling for submitted, pending, running, no-match, and unconfirmed states. Reserve the Check icon for a confirmed saved/approved result. Say “Request sent. Waiting for ORBA to confirm the result” until server state supports more specificity. Classify browser/proxy transport loss separately from a server-recorded terminal provider error; a browser-facing 504 alone does not prove that generation failed. Invalid response JSON must also preserve the recovery UUID and show safe unknown-outcome guidance. Do not render raw parser/provider messages as the recovery explanation.

Show safe run ID, diagnostic ID, actual server outcome, and last successful check time near the recovery message. Keep phase timings in a secondary disclosure. Label a deadline as the server's recorded deadline, not a guarantee that upstream usage has stopped. Never show inferred percent complete, invented intermediate steps, or elapsed duration derived from a configured timeout.

### D5 — Medium: failed loading is presented as both setup and empty content

Evidence: `product-plan.tsx:58-69`, `:125`, and `:151`. When initial loading fails, `capability` stays undefined and `plan` stays absent. The UI then shows “Configure the Product Manager” and “Your requirements start here,” although neither provider misconfiguration nor an empty saved-plan list was established.

Fix: distinguish unqueried/loading, failed read, confirmed empty, and confirmed unconfigured. On a failed initial read, show “Could not load product plans” with a GET-only recovery action. Show the setup panel only after the API positively reports `configured: false`; show the empty-plan state only after a successful empty read. A refresh failure must preserve already loaded plans and form edits. A single status summary should explain the next safe action without requiring the person to interpret a contradictory setup, error, and empty state.

### D6 — Medium: recovery needs its own accessible, readable location

Evidence: `product-plan.tsx:124-138` and `:152`; `globals.css:6`, `:10`, `:16-18`. Native labels, details/summary, visible focus tokens, mobile Button sizing, wrapping layout, and reduced-motion support are useful foundations. However, the current recovery information is split across the form, an alert, a general notice, an action row, and collapsed history. Checking status has no distinct in-progress label. The standalone request-reference span does not receive the paragraph wrapping rule used elsewhere.

Fix: add one compact recovery section inside the existing Product Plan panel, immediately before its saved-plan content. Give it a heading, one clear outcome sentence, and only the actions valid for that state. Use a polite atomic live region for status updates, a single alert for a newly failed user action, and an in-progress label such as “Checking status…”. Keep keyboard focus stable during GET refreshes; if a submit reveals a recovery decision, move focus to its summary without scrolling the person through the full document. Associate relevant error/help text with the form controls. Mark decorative icons as hidden from assistive technology.

Reuse the existing semantic colors, border, radius, spacing, and Button variants. Make long IDs wrap with `min-width: 0` and `overflow-wrap: anywhere`; keep diagnostics secondary and selectable. Proposed browser coverage should include both existing themes, 320 CSS-pixel width, zoom/reflow, keyboard-only use, long safe error text/IDs, and reduced motion. Source rules are not proof those cases pass. Retain readable approved content below the recovery section rather than replacing the panel with a full-page error.

## Required journey and state contract

| Authoritative situation | Main message and action | Generation/retry rule |
|---|---|---|
| Initial plan/status GET failed | Could not load plans; Check status | No invented empty/setup result; no automatic POST |
| Exact request is pending/running | Recorded state, last checked time, recorded deadline when available; Check status | Keep UUID; no second generation |
| POST transport loss, proxy error, invalid response, or status GET failure | Outcome unconfirmed; Check status | Keep UUID; GET-only recovery |
| Exact request lookup returns no match | ORBA has not confirmed receipt/outcome; Check status | No match does not unlock Retry or Clear |
| Exact request is `failed`/`interrupted` | Safe actual reason; Retry generation; separate Restore submitted brief | Fresh exact-run check, then fresh UUID and one explicit POST; no automatic restore/retry |
| Exact request is `succeeded`, result view loads | Draft saved; Open resulting plan | Recovery is complete; ordinary later generation remains a separate deliberate action |
| Exact request is `succeeded`, result/list refresh fails | Draft saved; could not refresh; Open/refresh saved plan | GET-only recovery; never regenerate to recover the display |
| An approved plan already exists during any failure | Keep that plan and approval provenance visible | Failure/retry must not modify the approved version |
| Unsaved plan edits or generation form edits exist | Preserve edits during checks; explicit overwrite/discard decisions | No automatic restoration, selection change, or context revision substitution |
| Session/membership access is lost | Existing session/access flow; do not expose protected content | Do not present authentication failure as model failure or allow retry |

Retry is an explicit new usage event, not a continuation, resume, or guaranteed fix. Keep “Check status” visually distinct from “Retry generation.” A generic “Try again” button is too ambiguous for these two actions.

## Seven-dimension litmus assessment

| Dimension | Assessment | Requirement for this change |
|---|---|---|
| Information architecture and hierarchy | Partial | One visible recovery summary owns outcome and next action; raw diagnostics/history stay secondary. Keep the existing project shell and saved-plan hierarchy. |
| State coverage | Changes required | Explicitly cover unknown/no-match, confirmed terminal failure, success with failed refresh, initial read failure, retained edits, and access loss. |
| Journey | Changes required | Submit once → confirm by exact UUID → open saved result or deliberately retry after terminal failure. Restore input separately; preserve approved plans. |
| AI-slop risk | Low stylistically; material semantic risk | Existing provenance and immutable approval copy are specific. Remove green checks on uncertainty and unsupported provider-progress claims; add no simulated agent steps, decorative dashboard, or generic reassurance. |
| Theme/design-system reuse | Good foundation | Reuse semantic tokens in both themes, native details/summary, existing Button, and the PM panel. No new UI dependency, theme, shell, status design system, or broad refactor is needed. |
| Responsive/accessibility | Promising source foundation; unverified | Preserve native labeling/focus/reduced motion; verify recovery announcements, focus behavior, target sizing, long-ID wrapping, and narrow/zoomed layouts later. |
| Unresolved choices and specificity | Partial | The plan names the correct safety boundary but must resolve the input snapshot, retry payload/context, recovery state ownership, and busy/status-check decisions below. |

## Unresolved design decisions to record before implementation

1. **Restoration across reload:** recommended: an authenticated saved-run snapshot supports Restore submitted brief after recovery. If only same-page restoration is in scope, explicitly record that bounded promise and protect unsaved text. Browser text persistence is not an allowed shortcut.
2. **Retry payload:** recommended: Retry submits the currently visible brief/instructions and explicit context selection. Restoring the original snapshot is a separate action with overwrite disclosure. Label the retry as a new model request that may incur usage. Clarify how an unavailable/stale context revision is presented before any POST.
3. **State ownership:** recommended: keep a small explicit recovery state tied to the exact account/project/request identity, including confirmed result linkage. Do not infer it from the current paginated history, a generic `busy` string, or presence/absence of an error message.
4. **Status checks during the initial long POST:** current `busy` disables Check status until the POST settles. Either retain that bounded wait with honest request-level copy, or allow a separately gated GET that cannot race terminal UI transitions. Do not add polling or a second POST. Record the chosen interaction and cover it deterministically.
5. **Timing disclosure:** recommended: show concise server state and last checked time first; put safe measured phase timings and IDs in an existing-style details element. Do not expose backend implementation details or configured timeout numbers as a product progress promise.

## Proposed acceptance evidence, not executed in this review

Use explicitly labeled controlled-provider browser scenarios with the real API and isolated PostgreSQL to establish the deterministic UI behavior. Assert that unknown, no-match, failed GET, and success-with-refresh-failure recovery perform no additional generation POST; that terminal Retry performs exactly one fresh-UUID POST after an exact status check; and that Restore is explicit and does not overwrite edits on status refresh. Cover form/context retention, approved-plan immutability, accessible status messaging, initial failed reads, and both themes at narrow width.

These cases belong to deterministic Gate A evidence and do not prove model success. Real-model/browser Gate B remains separate and blocked from execution until the owner's later explicit authorization. This review made no new live model call.
