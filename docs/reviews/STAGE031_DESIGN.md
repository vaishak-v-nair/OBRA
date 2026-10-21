# Stage03.1 design review

Scope: ProductPlan failure/recovery only, APP UI. Existing globals.css tokens, Button, native forms, workspace/auth shell and both themes remain authoritative. No DESIGN.md or designer binary was found; the existing theme is sufficient for this bounded change. Fallback design sketch was written and rendered at C:/Users/vaish/.gstack/projects/OBRA/designs/stage031-recovery-20261019/recovery.html and recovery.png, explicitly labeled DESIGN SKETCH, not executed application/model evidence.

Initial design completeness:6/10. A complete design must distinguish known failure from unknown delivery, preserve submitted text, keep saved plans visible and describe the exact control enabled in each state. Scores below evaluate the amended specification, not an unexecuted UI.

## Pass1: information architecture (9/10 specified)

Keep the existing Product Plan heading and generator. Order the local state as outcome, retained brief/instructions, relevant recovery action, then existing saved plan/history; do not replace saved agreement content with an error. Run/diagnostic UUIDs are secondary context and must wrap without horizontal overflow.

```text
Product Plan -> current brief + instructions -> explicit Generate or Retry
             -> truthful alert / neutral status + run reference + Check status
             -> existing saved version / reader / approval evidence
             -> version and run history
```

## Pass2: state coverage (9/10 specified)

The current component incorrectly treats a failed initial history read as both unconfigured and empty. Only a successful server read can establish configured=false or no plan. A generation failure can coexist with a real approved plan and must leave it visible.

| Feature | Loading | Empty | Error | Success | Partial/unknown |
|---|---|---|---|---|---|
| History/config | Checking saved plans | Only after successful empty response | Unavailable, read-only refresh | Actual saved versions | No invented setup/empty conclusion |
| Generation | Waiting during actual request | No generated plan yet | Safe specific category and retained text | Validated saved draft | UUID retained, no further POST |
| Retry | Fresh terminal status check | No prior failure: ordinary Generate | New failed run remains separate | New genuine draft if provider succeeds | Unavailable until exact prior outcome confirmed |
| Brief restore | Authenticated GET | No snapshot: unavailable | Keep current edits on failure | Explicitly replace from snapshot | Never overwrite edits automatically |
| Approval | Existing save/confirmation flow | No draft: no approval | Preserve actual prior state | Exact actor/version/revision/time | GET reconciliation only |

Neutral status must not use the green success Check icon for pending/no-matching-run messages. A success icon is reserved for a confirmed saved/approved outcome.

## Pass3: journey (9/10 specified)

In the first five seconds a timeout should explain what happened and what remains safe. During the next five minutes the user can inspect the exact request and consciously retry, retaining brief/instructions. Longer-term trust depends on failure history remaining visible rather than being rewritten as a recovered success.

| Step | Action | Likely feeling | Designed response |
|---|---|---|---|
| 1 | Enter brief | Intent | Existing labeled form, clear paid-capable action |
| 2 | Generate | Waiting | Real bounded request, no invented steps |
| 3 | Receive504 | Concern | Provider timeout, no new plan, existing agreement visible |
| 4 | Inspect/recover | Uncertainty | GET-only Check status; UUID retained |
| 5 | Retry | Deliberate choice | Fresh terminal check and new recorded UUID |
| 6 | Reload | Need confidence | Snapshot restore action and persisted history |
| 7 | Approve | Accountability | Existing explicit exact-version confirmation |

## Pass4: AI-slop risk (10/10 specified)

This is a task workspace, not a landing page. Add no hero, card grid, progress percentage, celebratory agent activity or decorative gradients. Copy names the outcome and the next safe action; there is no fake generated content in an error state.

## Pass5: design system (9/10 specified)

Reuse semantic tokens and the existing Button variants. The sketch demonstrates the two intended states in the existing light and dark palettes, but production styling comes from globals.css rather than copying sketch colors. No unrelated typography, navigation or layout changes are authorized.

## Pass6: responsive/accessibility (9/10 specified)

At desktop, retain the current workspace column and inline recovery controls; at tablet/mobile, controls wrap and UUIDs break without clipping. Keep visible native labels, keyboard access, focus outlines and44px action targets; alerts announce actual errors and status text announces read-only updates. Check preservation, restore and retry in all existing Chromium desktop/mobile/tablet profiles; no native-device or full-WCAG certification is implied.

## Pass7: decisions resolved (9/10 specified)

Unknown delivery retains the pending UUID and exposes GET recovery only; remove Clear request reference as an unknown-outcome escape. Retry is available only for a server-confirmed failed/interrupted own request and is rechecked before POST; no automatic retry occurs. Restore submitted brief is explicit, obtains authorized input_snapshot and does not silently replace current edits.

Do not clear a succeeded request reference before its saved result can be read: a failed history refresh must retain recovery linkage. Known pre-admission rejections should remain distinguishable from an unconfirmed dispatch so ordinary validation/admission failures do not trap the form indefinitely.

## Litmus and independence

| Question | Primary assessment | Independent in-host voice | Outside model |
|---|---|---|---|
| ORBA identity retained? | Yes, existing shell | See STAGE031_DESIGN_VOICE.md | N/A |
| One clear visual anchor? | Outcome and action | See voice | N/A |
| Scannable headings/actions? | Explicit timeout vs check status | See voice | N/A |
| Each section one job? | Reader/generator/history retained | See voice | N/A |
| Cards necessary? | No new card mosaic | See voice | N/A |
| Motion useful? | Actual waiting only | See voice | N/A |
| Premium without shadows? | Existing spacing/tokens | See voice | N/A |

No cross-model agreement is claimed. The independent voice surfaced the unsafe clear-reference path, success-reference loss on refresh failure, missing snapshot restore contract, success-colored uncertainty and invented initial empty/config states; all are in the amended plan.

## Tasks, scope and completion

- [ ] D1 (P1, human2h / agent30m): terminal-confirmed Retry, unknown GET-only recovery and retained UUID until result read; product-plan.tsx.
- [ ] D2 (P1, human1h / agent20m): explicit authorized snapshot restore, no silent overwrite; lib/pm.ts and ProductPlan.
- [ ] D3 (P1, human1h / agent20m): distinguish loaded-empty/setup from failed read and neutral from confirmed-success notices.
- [ ] D4 (P1, human1h / agent20m plus browser): exercise all recovery states/brief preservation/approval preservation across existing viewports.

No unrelated screen redesign, offline brief storage, real-time presence or full draft audit is in scope. Existing TODOs cover broader devices and retention, so no duplicate TODO is added. All seven passes have specific findings/specifications and a rendered fallback sketch; implementation/browser verification remains outstanding.
