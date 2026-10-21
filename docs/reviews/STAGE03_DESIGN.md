# Stage 03 full design review

2026-10-19. Status: primary seven-pass review completed; second CLI voice pending. This is a proposed-design review, not an implemented PM interface or a live-model result. Stage 04 and a shell redesign remain excluded.

## Step 0: scope, evidence and rating

This is APP UI: a document and editing workflow inside the current authorized project page. Read the actual project detail/editor/form, Shell/AuthGate, API client/proxy, Button, globals.css and retained browser tests. The current protected shell and source-level UX are the authority; a new agent dashboard is unnecessary. Initial plan design completeness is 7/10: the workflow is described, but dirty-state transitions, large nested validation, version orientation and focus recovery need exact rules. A 10/10 plan specifies those branches and has rendered/live evidence for its maximum-size, keyboard and responsive behavior.

There is no DESIGN.md. There is a working design system in globals.css and the owner's explicit theme preservation requirement. Reuse that source rather than inventing another theme file or changing fonts globally. Source/read-only coverage includes the existing 244px sidebar, 720/1050px breakpoints, native workspace/account controls, Button focus styles, AuthGate state keys and three Chromium viewports. The previous home screenshots were inspected as baseline style evidence; they are not PM screenshots.

The documented `design/dist/design` helper is absent at repository, user Codex and installed agents paths. `DESIGN_NOT_AVAILABLE` therefore activates the skill's labeled HTML wireframe fallback. Created external user-owned artifacts at `C:/Users/vaish/.gstack/projects/OBRA/designs/pm-stage03-20261019/`: product-plan-wireframe.html, capture.cjs and desktop/mobile light/dark PNGs. The page states DESIGN SKETCH/no live AI/API/data; all business actions are disabled placeholders. Two CLI captures and a four-viewport/theme capture script exited 0. Its actual assertions establish the sketch label and no horizontal overflow at1280×1000 and390×844 only. They do not establish application behavior or accessibility conformance. The first mobile render put the version selector below the document; it was moved into the plan header and recaptured. This is an actual visual design correction, not a product fix.

## Pass 1: information architecture — 7/10 -> specified target 9/10

The current detail page contains overview, metadata, a small real editor and a future panel. A PRD must become a readable agreement, not dozens of identical decorative cards. Keep one main Product Plan section below the existing overview; its header always identifies the viewed version, saved revision and state when those exist. Approved is the default reader agreement, while an author may explicitly open a returned new draft. Run history and model metadata are secondary context, not the main visual anchor.

```text
Existing Shell / project title / project metadata / current description + editor
  Product Plan h2                          [state] [version select]
    source freshness / newer draft notice / current role
    no plan -> brief + optional instructions/context -> Generate
    saved plan -> short section outline -> Overview -> Requirements
                 -> Epics/stories/criteria -> Review items
                 -> exact saved-version approval area
    secondary disclosures -> inputs used | run history | generation evidence
    later-stage architecture/tasks/agents/evidence placeholder remains honest
```

On desktop with enough content width, a narrow secondary context column may sit beside the document. At tablet/mobile widths, move essential version/state controls ahead of the document and place secondary evidence/history after it. A small anchor outline opens/focuses the chosen section; it does not add global sidebar entries. A large brief/instruction form is open in the initial empty state, then collapsed under Generate another version when a plan exists. In a first project there is one clear Generate Product Plan action; merely opening a project never sends a model request.

## Pass 2: interaction states — 6/10 -> specified target 9/10

Use separate state for selected plan ID/version, loaded saved revision, local editable document, dirty flag, outstanding operation and its actual persisted run reference. Approval is disabled while dirty, saving, loading or blocked; the explanation says Save changes before approving or identifies open confirmations. A failed save leaves every field in memory, while account/workspace changes and sign-out still clear protected state immediately. No browser storage gains authentication or secret authority.

| Feature | Loading | Empty | Error | Success | Partial/uncertain |
|---|---|---|---|---|---|
| Authorized section | Checking session/project/plan with status text | No product plan yet; authorized next action | Safe401/403/404/503; no old protected content | Actual authorized version loaded | Independent failed history fetch does not imply plan loss |
| Provider setup | Loading nonsecret capability | Setup required, static operator guidance | Invalid configuration/auth/rate/connection category | Configured model label, without claiming connection verification | Configuration alone is not a successful provider call |
| Generation inputs | Brief retained while submitting | Description-derived brief; optional fields visibly optional | Field/path/size guidance | Actual request accepted/completed | Unknown submission retains request UUID and offers Check Status |
| Model run | Actual pending/running from request/DB | No runs; no simulated timeline | Persisted failed/interrupted category and reference | Validated saved draft reference | Still running versus unknown transport versus persistence unconfirmed are distinct |
| Version reading | Loading explicit selected version | No versions | Private not-found or retry GET | Version/revision/state/source shown | Approved agreement remains visible if another generation fails |
| Draft editing | Saving, controls bounded/disabled | Empty optional list has Add action | Linked errors; local data retained | Returned revision and actual save announcement | Dirty badge distinguishes unsaved text from saved artifact |
| Nested removal | No asynchronous removal until Save | Last required item cannot be removed silently | Affected references listed | Local removal after explicit confirmation where text would be lost | Other stories/criteria never silently cascaded away |
| Source/freshness | Loading actual snapshot | No quote for suggested/assumed/human content | Unavailable snapshot is labeled, never reconstructed falsely | Exact supplied-input excerpt and origin | Current project differs; approval concerns captured inputs only |
| Blocking confirmations | Local resolution being edited | None is a legitimate empty list | Unresolved/empty reason blocks approval | Actual saved human resolution/deferral | Nonblocking questions/risks remain disclosed |
| Approval | Actual POST in progress | No saved eligible draft | Stale/invalid/permission/blocker error, no frontend-only state change | Actor/version/revision/time returned from server | Network ambiguity offers GET of that exact plan |
| Human copy | Explicit create-copy in progress | No source version | Conflict/private/error; retain source | Real human-origin draft with source version | Existing matching copy may be returned; no model-call claim |
| Large history | Fetching next summary page | No older versions | Retry GET without clearing document | Bounded page/select options | Unloaded history is not represented as complete |

Generation, Save and approval have independent errors and operation-aware actions. Typed ApiError must preserve safe code/run/reference/field paths; the current generic POST message about checking Projects cannot drive this interface. Normal network failures never cause automatic POST retries. No progress percentage, fabricated thinking phase or made-up usage value is displayed.

## Pass 3: journey and emotional arc — 7/10 -> specified target 9/10

The desired first five seconds are orientation: same workspace/project, one Product Plan area and a clear explicit action. The first five minutes should feel like an editable proposal with visible unknowns, not an AI decree. Later returns should make the approved agreement and its real source evidence easy to identify. Emotions here are design hypotheses, not observed user research or adoption metrics.

| Step | User does | Intended experience | Concrete support |
|---|---|---|---|
| Arrive after project creation | Reads overview, opens Product Plan | Understands the next step | Existing context, labeled section/action, no automatic charge |
| Refine brief | Adds scope/instructions | Retains control | Editable bounded text; explicit prior context; no silent project rewrite |
| Generate | Clicks once | Knows a real request is pending | Busy action, persisted run/status when available; no invented intermediate steps |
| Review | Reads supplied/suggested/assumed content | Can challenge the proposal | Source excerpts, requirements/story keys, explicit uncertainty |
| Correct | Edits criterion/story/scope | Work feels recoverable | Labeled fields, dirty marker, local preservation, stable-path errors |
| Approve | Reviews saved exact version | Makes an intentional decision | Actor permission, blocking confirmations, exact version/revision confirmation |
| Return/share | Reloads approved version | Knows what is authoritative | Actual approved actor/time, newer drafts separate, source freshness notice |
| Correct history | Creates editable copy | Avoids paying merely to correct wording | Human-copy origin/source label; old approved content stays immutable |

Navigation away does not promise provider cancellation. If unsaved edits would be lost within the same project, provide Save, Discard or Keep editing; no implicit discard or automatic approval. Browser/tab close may use a best-effort native beforeunload warning for dirty data, but that is not persistence or crash recovery. Existing AuthGate security clearing takes precedence over preserving text after loss of authentication.

## Pass 4: specificity and slop risk — 8/10 -> specified target 9/10

The visual anchor is the current agreement/draft heading and readable text, not a new hero, dashboard mosaic or agent avatar. Use restrained section separators and native disclosure for hierarchy; a story is a group of editable fields, not a promotional card. Keep source labels in text, with an optional excerpt disclosure, so meaning never depends on mint versus amber colors. Explain unknown model usage with unavailable wording rather than zero or invented dollar costs.

The generic rule against default fonts conflicts with the owner's requirement to preserve ORBA's actual visual design. The owner wins: inherit the existing font stack, and do not import a new font or redesign the shell as a side effect. New PM reading text and error guidance target16px with comfortable line height; metadata is secondary but readable. Placeholder-only design artifacts remain explicitly labeled; the actual application never substitutes these outlines for generated plans.

App UI hard rules were evaluated against the proposed composition: no card mosaic, no ornamental gradient/image, no generic feature grid, no mood headline replacing an action, no gratuitous motion. Current page structures are preserved where they remain accurate; Stage02/no-AI and future-requirements copy must be updated when the corresponding Stage03 functionality actually exists. Motion is restricted to real loading affordances and respects reduced-motion settings. No decorative shadows are needed for hierarchy.

## Pass 5: design-system alignment — 8/10 -> specified target 9/10

Reuse globals.css semantic background/surface/foreground/secondary/primary/border/ring tokens and existing Button variants. Add scoped PM textarea/fieldset/error/outline styles rather than scattering hardcoded theme colors. The actual current standard-form styles inputs/selects but not equivalent textarea surfaces, so the nested editor needs deliberate control treatment. New controls inherit the existing overall language; no dependency is justified solely for disclosure, selects or confirmation.

Calculated sRGB contrast for opaque token pairs: light body/background13.37:1, light secondary/white6.42:1, white/accent4.95:1; dark body/surface12.48:1, dark secondary/surface7.16:1, dark primary-foreground/accent8.75:1. These calculations support the named token pairs only; opacity, focus, disabled states and actual rendered controls still require application checks. They are not a WCAG certification. Keep approved/draft/suggested labels and icon-independent text alongside color.

Use visible labels and fieldset legends, with stable story/criterion keys for repeated fields. API metadata is secondary evidence, wrapped safely and never styled like an authenticated secret. Links need visible focus and meaningful visited styling in the PM section without a broad unrelated navigation rewrite. Long source excerpts use pre-wrap/overflow-wrap and a bounded disclosure rather than shrinking text.

## Pass 6: responsive and accessibility — 6/10 -> specified target 9/10

| Surface | Desktop content width >=880px | Tablet/narrow desktop | Mobile <=720px |
|---|---|---|---|
| Navigation | Existing sidebar/skip link | Existing215px variant | Existing dialog/focus trap/Escape; no second PM modal system |
| Document | Main readable column + optional220–240px context | Single document column, compact outline | State/version before content; full-width stacked primary actions |
| Version/history | Labeled select with state/date; bounded older-page control | Same select, no growing tab strip | Full-width select near header; secondary evidence below document |
| Editor | Fieldsets with consistent labels; generous text width | One-column nested groups | No horizontal form grids;44px targets; keyboard not obscured by sticky action bars |
| Sources/metadata | Expandable exact excerpts and nonsecret IDs | Wrap identifiers | Wrap all strings; no forced horizontal scrolling or text reduction |
| Approval/errors | Summary above fields; exact revision near action | Same semantic order | Blockers adjacent to approval; error links open/focus the correct nested control |

Keyboard and assistive behavior is explicit: unique labels include story/criterion identifiers; native summary is keyboard operable; validation summary links expand closed ancestors and focus the invalid input. Actual run completion and Save success use a concise polite status region; errors use an alert. Polling must not steal focus or repeatedly announce unchanged status. Explicit Open draft may focus its heading. Approval confirmation identifies version/revision, is keyboard operable and restores focus on cancel.

No hidden invalid field should strand a full document. Validate local structure before submission for immediate feedback, then respect server validation as authority. While a save is in flight, prevent conflicting structural edits so field paths correspond to the submitted snapshot. A stale409 preserves local edits and offers a separate latest-server view; only explicit discard replaces the local document. Planned browser evidence includes both themes, nested invalid disclosure, large multi-epic content, keyboard-only Save/approval, Viewer controls, real offline ambiguity and exact UUID denial across desktop/mobile/tablet. Core fixtures must be explicitly labeled and never called live generation.

## Pass 7: decisions and unresolved choices — 6/10 -> specified target 9/10

| Decision | Recommendation and alternative | Classification |
|---|---|---|
| Version selection | Native labeled select; tabs grow poorly with version history | Mechanical, P5; default reader view already C01/C02 context |
| Editing location | Inline project-local editor mode using the same section/outline; dedicated page is viable if large-form usability requires it | Taste D01; no shell redesign |
| Source presentation | Short text origin + inspectable actual excerpt; a separate source rail is viable but consumes mobile space | Taste D02 |
| Dirty version/navigation transition | Save, Discard, Keep editing; security identity clearing remains immediate | Mechanical, P1 |
| Structural deletion | Show affected references, require repair, never silently discard dependent content | Mechanical, P1 |
| Approval | Saved exact revision only, Owner/Admin, blockers resolved/deferred, no implicit Save | Mechanical under C02; no UI-only label change |
| Copy correction | Support C05 human-copy draft without a model charge; preserve inherited source/version | Existing CEO taste, not an additional decision |
| Motion/notifications | Native/real-request status only; no fictional progress or decorative agent animation | Mechanical, P5 |

No design decision remains intentionally vague for implementation; actual visual/keyboard verification remains unexecuted. The inline editor and source presentation are real taste choices for the final gate. A font replacement, realtime comments/presence, graphical backlog canvas, full diff viewer, configurable component library, new global navigation and native-device certification are excluded. Their absence does not remove required responsive/keyboard/error checks.

## Decision audit

| ID | Finding | Classification / principle | Auto-decision and rejected alternative |
|---|---|---|---|
| DS-D01 | IA/state ambiguity | Mechanical P1/P5 | Explicit viewed version/revision/state before content; reject a generic mixed timeline |
| DS-D02 | Long form navigation | Mechanical P5 | Native outline/disclosure and bounded select; reject growing tabs/card mosaic |
| DS-D03 | Unsaved approval | Mechanical P1 | Disable until real Save returns revision; reject autosave-and-approve |
| DS-D04 | Local recovery | Mechanical P1 | Preserve all local fields and stable error mapping; reject replacing draft on409 |
| DS-D05 | Large nested deletion | Mechanical P1 | Reference-aware explicit removal; reject silent cascading text loss |
| DS-D06 | Unknown run outcome | Mechanical P1/P4 | Typed run-aware errors and GET recovery; reject automatic charged POST retry |
| DS-D07 | Source trust | Mechanical P5 | Accurate text origin/excerpt and source freshness; reject Verified fact labels |
| DS-D08 | Editor placement | Taste D01 P5 | Inline local mode recommended over a new page |
| DS-D09 | Provenance placement | Taste D02 P5 | Text/disclosure recommended over a persistent rail |
| DS-D10 | Scope/visual authority | Mechanical Explicit | Preserve actual font/themes/shell, scoped16px PM reading; reject broad design rewrite |
| DS-D11 | Native accessibility | Mechanical P1 | Unique labels/focus/error expansion/status announcements/44px targets; reject custom control dependency |
| DS-D12 | Artifact truth | Mechanical Explicit | Label/render external sketch; never present it as working PM/provider evidence |
| DS-D13 | Unknown writes beyond Generate | Mechanical P1 | Reconcile Save/Approve/Copy by exact authorized GET; reject automatic write retry |
| DS-D14 | Authority loss | Mechanical P1 | Refresh permissions after denial and clear protected data on membership/auth loss |

## Implementation tasks

| ID | Component/files | Work / source finding | Priority | Human / agent-assisted estimate | Verify |
|---|---|---|---|---|---|
| DS-T1 | project detail, new ProductPlan component | Implement canonical reading order/version/source context; passes1/3 | P1 | 0.5d /30–60m | Actual first-project and return flows |
| DS-T2 | PM editor components + globals.css | Labeled nested editor, dirty tracking, safe structural edits; passes2/6 | P1 | 1–2d /1–2h | Real save/reload/conflict and keyboard cases |
| DS-T3 | api.ts/proxy/PM status UI | Typed errors, unknown outcome, GET recovery, preserved approved content; pass2 | P1 | 0.5–1d /30–60m | Actual failure/offline/late status cases |
| DS-T4 | approval/source UI + API contract | Exact saved revision/blockers/human-copy/freshness; passes3/7 | P1 | 0.5–1d /30–60m | Live Save/Approve/reload + wrong revision negative |
| DS-T5 | scoped CSS + Playwright | Both themes, max-size/mobile/tablet/keyboard/error focus; passes4–6 | P1 | 1d /45–90m | Required core and live browser suites |

Estimates are planning ranges, not elapsed measurements. Deferred scope is captured for the final Eng/TODOS aggregation; no extra prototype feature is authorized. Full skill JSONL/log helpers are absent; primary will write supported task JSONL with installed jq for aggregation rather than claim an unavailable helper ran.

## Completion and remaining evidence

All seven passes, state matrix, storyboard, layout/flow, scoped design reuse, responsive/focus contract, decisions and tasks are written. Actual sketch capture and token contrast calculations are bounded design evidence. Proposed document-completeness target9/10 retains a concern for application/max-size/live validation; it is not a UI test pass. No product code, provider call or Stage04 work was performed.

## Independent voices and disposition

[Fresh-context design voice](STAGE03_DESIGN_VOICE.md) identified six ranked concerns. [CLI design voice](STAGE03_DESIGN_CLI.md) actually completed with exit0 and six ranked concerns. Both are Codex-family reviews; Claude/cross-model consensus is unavailable and is not claimed. CLI reviewed the pre-amendment contract and real source, without seeing the first voice. Its conditional/negative litmus findings identify missing specifications, not failing runtime tests.

| Litmus | Independent voice | CLI | Resolution in amended plan |
|---|---|---|---|
| Unmistakable product | Scope/trust explanation needs current copy | Conditional: Chat/build copy overstates Stage03 | Preserve Chat; accurately label planning stage and no-provider state |
| Useful visual anchor | Version/revision/dirty state needs hierarchy | No artifact/action focal point | Artifact header before content and jump link near project heading |
| Scannable headings | Long plan needs summary/navigation | Conditional: collapsed summaries undefined | Section outline, epic/story counts, stable keys and priorities |
| One job per section | Generation/editor/history need separation | No: proposed mixed section | Distinct reader/editor/generator/evidence disclosures |
| Justified containers | Restrained fieldsets, avoid card nesting | Conditional: justify nested cards | Native fieldsets/disclosures; borders and spacing for actual hierarchy |
| Purposeful motion | Truthful status, no fake steps | Yes: pending reflects actual waiting | Changed-status announcements only; reduced motion preserved |
| Premium without shadows | Error recovery/density must remain usable | Conditional: maximum editor unspecified | Scoped16px reading,44px targets, responsive max-size tests |

Both voices independently emphasized dirty-state approval, recoverable nested errors, operation-specific ambiguous writes, input freshness, long-plan hierarchy and focus recovery. No design disagreement requires changing the owner's stated stage structure. D01 inline editing and D02 text/excerpt provenance remain taste choices; the existing C05 human-copy recommendation is supported rather than counted twice. Main plan now includes typed errors/Retry-After, exact saved-revision approval, separate latest revision on409, reference-aware deletion, explicit navigation choices, semantic error focus, actual snapshot labels and maximum-size browser coverage.

DS-D13 (mechanical P1): extend unknown-outcome handling to Save/Approve/Copy as well as generation; reconcile via authorized GET, reject automatic write retry. DS-D14 (mechanical P1): refresh current permissions after denial and clear protected data on identity/membership loss, rather than preserving sensitive unsaved content across authority changes. These augment the twelve audit rows above.

Final plan-specification assessment:9/10 after amendments; remaining point is actual implemented/live/max-size evidence, which cannot be earned by this review. Design phase complete; pass the amended contract to DX, then Eng last.
