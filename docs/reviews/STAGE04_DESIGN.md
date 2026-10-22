# Stage04 design review and interaction contract

2026-10-21. APP UI; preserve the current ORBA shell, Arial typography and semantic
Soft Minimal/Graphite Mint tokens rather than imposing a different design system.
Initial specificity7/10; amended plan specificity8.8/10, not a rendered-product score.
No paid mockup generator is available or authorized. A human-authored standalone HTML
sketch was rendered locally in Playwright and inspected at1280px light and390px dark:
`C:/Users/vaish/.gstack/projects/OBRA/designs/stage04-architecture-sketch.html`.
Its labeled example content is design material, not application/model evidence.

## 1. Information architecture (7 -> 9)

Keep project overview and current sidebar/workspace/account controls. Add local project
navigation for Product Plan, Architecture and Task Graph; default to the existing PM
view. Architecture and Task Graph share one mounted parent and draft/revision state;
changing the view cannot discard a dependency or text edit. The existing PM view also
stays mounted after its initial visit. Replace only the obsolete architecture/task
future-placeholder text; execution/coding/QA remains future scope.

```text
project title / description
Product Plan | Architecture | Task Graph   (native named navigation controls)
  source strip: PRD v/r, current or earlier source, exact-source review
  architecture title + state + version/revision + one contextual action
  review summary: unsaved input, DAG status, linked coverage, open obligations
  section navigation -> overview / technology / components / data / API / security
  task graph -> diagram + synchronized native list + selected-task detail
```

The first three priorities are source agreement, proposal state and the next safe
action. Do not append several expanded documents below one another. On long proposals,
use native disclosures and section links so the reviewer can scan without losing
approval/source context. Exact source review opens read-only persisted source content
inside the planning context, preserving unsaved architecture and PM editors.

## 2. Interaction state coverage (7 -> 9)

| Feature | Loading | Empty | Error | Saved result | Partial/unknown |
|---|---|---|---|---|---|
| Approved source | Text status, no protected proposal yet | Approve a Product Plan first; link to PM; Member gets Owner/Admin guidance | Safe read failure + GET retry | Exact approved v/r/hash and source review | Earlier-source notice; no silent rebase |
| Provider setup | Capability read only | Configure Architect model/server credential; no fake draft | Safe configuration guidance | Configured for explicit generation, not live-proof claim | Readiness unknown stays unknown |
| Generation | One bounded request; disable repeat submit | No saved architecture; explicit Generate | Timeout/unavailable/validation/rate-limit category; old approval/input remain | Real saved draft, model metadata if supplied | Keep UUID; GET status; no automatic POST |
| Proposal editing | Busy Save, fields retained | Nonempty contract enforced | Focus safe error summary + field/task links | Saved revision and actual response | Local draft + separate latest revision comparison |
| Dependency editing | Saving preview | No prerequisites explained, not a blank panel | Directed cycle/missing-reference error; no saved change | Server-validated graph/recomputed readiness | Unsaved preview explicitly not validated |
| Coverage | Read with artifact snapshot | Missing items listed by source key | Broken lineage/source integrity message | Linked-to-tasks counts and exact exceptions | Structural linkage, not semantic/execution completion |
| Approval | Named exact version/revision confirmation | Missing requirements/decisions listed | Stale/invalid/incomplete/role409/403 guidance | Persisted actor/time/version | No speculative approved label |

Full CRLF/legacy verification histories remain historical and are not UI success
signals. A generated API contract is labeled Proposed; a task is always unexecuted.
Save/approval failures must not reset text, selection, source constraints or acknowledgments
into a misleading saved state. Acknowledgments reset when their bound revision changes.

## 3. Journey and confidence (7 -> 8)

| Step | User action | Expected feeling | Concrete support |
|---|---|---|---|
|1| Open project | Oriented | Existing title/workspace, unchanged PM entry |
|2| Open Architecture | Understand prerequisite | Current approved source or actionable empty state |
|3| Review source/constraints | In control | Exact source context and explicit usage-triggering action |
|4| Generate | Waiting honestly | Bounded loading and real run reference; no fictional steps |
|5| Review proposal | Skeptical but informed | Proposed labels, model/source metadata, inherited uncertainty |
|6| Inspect graph/coverage | Able to audit | Named prerequisite arrows, task details and exact missing links |
|7| Edit/save | Safe to correct | Shared draft, targeted errors, optimistic revision and preserved text |
|8| Approve/reload | Agreement recorded | Exact saved source/version/revision, explicit human dispositions |

For the first five seconds, show where the proposal comes from and whether it is saved.
For the first five minutes, make the complete source-to-task correction journey possible
without dragging nodes or learning graph jargon. Long-term trust comes from immutable
history, honest failure and explicit source currency, not celebratory progress graphics.

## 4. Specificity and false-authority risk (8 -> 9)

Use a quiet document layout with section dividers and one contextual primary action.
No feature-card mosaic, agent avatars, decorative gradients, motion for atmosphere,
progress percent or simulated task execution is added. Reuse existing Button, form
styles, native disclosures and Lucide only where the icon explains an action.

Use "Linked to tasks" rather than an unqualified "Complete" coverage badge. Put the
structural-linkage limitation next to the counts. A root task says "No prerequisites
in this planning graph; not executed"; a dependent lists the unmet prerequisite task
names. Approved means human agreement to that proposal, never implementation evidence.

## 5. Design system alignment (8 -> 9)

No DESIGN.md exists, but globals.css and the owner's explicit palettes are the current
design authority. New styles use `--background/surface/elevated/foreground/secondary/
primary/border/ring/danger` without scattering new hex values. Preserve global typography
and current components; use readable16px proposal body text and restrained7-12px corners
inside the new surface without redesigning Stage01-03.

Graph edges use secondary foreground contrast rather than faint decorative borders.
Visible focus uses the existing accent ring. Light/dark rendered screenshots and computed
layout/contrast checks are later QA requirements; neither the static source review nor
the design sketch establishes application accessibility or native-device compatibility.

## 6. Responsive access and draft lifetime (6 -> 9)

At desktop widths, place the bounded scrollable dependency overview beside task detail.
On narrow screens, default to the complete task list then detail, with the diagram in
an optional disclosure; do not force page-level horizontal scrolling. Keep controls at
least44px high. Graph inspection has a plain arrow legend: A -> B means B depends on A.
The diagram never validates the graph merely by rendering it.

The native task list is authoritative for keyboard interaction. Use named task selection
buttons and a selected-state indicator; the detail region has its task title. Provide
"Depends on" and "Blocks" lists, a single prerequisite selector and Add, and individually
named Remove buttons. No Ctrl/Command multi-select, drag, hover or SVG-only action is
required. Selection remains on the same task after edits; removal moves focus to the
prerequisite selector, and a concise live status announces the change.

Keep one draft and expected revision in the project-scoped planning parent. Switching
Architecture/Task Graph or inspecting source preserves it. Guard deliberate link/workspace
navigation away with Save, Discard and Cancel; failed Save cancels navigation and keeps
input. Native beforeunload warns on reload/close. Auth expiry/logout/account replacement
must clear protected state immediately and cannot be blocked by an editor dialog. Do
not store draft content in localStorage/sessionStorage. Test keyboard,320px/zoom and
desktop/mobile/tablet emulation; do not claim screen-reader/native-device certification.

## 7. Approval, stale source and error recovery decisions (6 -> 9)

Show a review summary before the proposal: exact source and currency, saved/unsaved
revision, validated graph, missing linked requirements/stories/criteria, source-dependency
gaps, tasks with no clear source, inherited uncertainty and blocking architecture decisions.
Every missing item has a stable reference and a link to the corresponding task/field.
Exceptions require a reason and an explicit human acknowledgment for the saved revision;
model text cannot preselect it. The confirmation repeats architecture v/r and source v/r.

An earlier-source artifact stays readable and keeps its original source. Offer read-only
review of the current approved PRD and a separate explicit Generate-from-current-source
action; a free draft copy does not silently rebase it. A newer unapproved PRD draft does
not stale the current agreement. Owners/Admins get approval actions; Members get a clear
approval-required explanation and Viewers remain read-only.

Preserve ApiError field details in an error summary with focus after rejected Save. Mark
matching fields invalid and associate help/errors; open the relevant native disclosure
before jumping to a field. A graph cycle names its directed path and task dependency
controls. Revision conflicts expose the fetched revision separately; Inspect latest
must never overwrite the local draft. Dirty previews show no authoritative readiness
claim until saved and validated by the server.

## Independent voice and litmus

The independent same-family design voice found2high/4medium specificity gaps, all mapped
to the concrete decisions above: shared draft lifetime, explicit review obligations,
earlier-source recovery, native graph access, local hierarchy and targeted errors. These
are in-scope UX decisions; no owner-scope challenge or visual redesign was proposed.
External CLI/visual-model review is unavailable and no paid substitute was invoked.

| Litmus | Primary design assessment | Independent evidence boundary |
|---|---|---|
| ORBA recognizable | Existing shell/tokens retained | Existing source inspected |
| Main anchor | Source + proposal header | Initial hierarchy gap fixed in plan |
| Scannable headings | Local navigation and section links | Requires rendered QA |
| One job per section | Source, review, document, graph/detail | No new global dashboard |
| Cards necessary | Bounded graph/task detail only | Avoid card mosaics |
| Motion purposeful | Real loading only; reduced-motion retained | No invented progress |
| Premium without shadows | Quiet typography, spacing and dividers | Actual app styling still unverified |

Cross-model confirmation remains N/A. No score above is a passing accessibility or
browser result. The authored wireframe is illustrative and not an approved product
artifact generated by a model.

## Implementation tasks and completion

- [ ] D1: Share draft/source/revision/selection across project planning views and protect
  deliberate navigation; verify cancel and failed-save behavior without blocking auth clearing.
- [ ] D2: Build exact-source review summary, linked-coverage exceptions and revision-bound
  approval acknowledgment; test missing criterion and inherited obligation visibility.
- [ ] D3: Implement readable graph/list/detail with native prerequisite controls, focused
  validation recovery and earlier-source actions; verify at desktop/mobile/tablet/320px.

All seven dimensions evaluated; six concrete independent findings resolved in the plan,
zero visual scope expansions, no new graph dependency, zero AI mockups/paid calls.
The sketch was rendered and inspected, but the actual Stage04 application is not yet
implemented. No additional TODOS are needed beyond the existing advanced canvas,
realtime collaboration and execution backlog. Pass this amended contract to DX review.
