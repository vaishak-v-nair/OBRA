# Stage04.1 design review

Reviewed 2026-10-22 against `docs/STAGE041_PLAN.md`, the CEO review and the actual
project, session, Product Plan and Architecture components. This is an independent
in-host review, not a cross-model consensus or a browser test result. The installed
gstack native helper is unavailable; its dashboards and outside-provider probes
were not run. Only this review was written. Existing owner authorization resolves
the scope choices below; no new visual direction or paid action is proposed.

## What already exists

`ProjectForm` creates a real project, awaits its JSON and requests the project
route. `AuthGate` hides protected content during session restoration and keys it
by account, workspace and pathname. Project detail has loading/error/retry states;
Product Plan has real saved version selection, draft state, explicit approval and
an exact-version confirmation. Architecture has a configured-provider notice,
source checks and explicit generation. Reuse these components, semantic CSS
tokens and both themes. No separate design system or mockup is necessary here.

## Pass 1 — Information architecture

Plan rating: 9/10; with the identity specification below: 10/10. This rates the
plan's specificity, not verified implementation quality.

```text
Chat creation -> exact /projects/{created UUID} -> matching project overview
 -> Product Plan: exact draft/version/revision -> approval confirmation
 -> saved approved state -> reload same project -> Architecture source/action
```

1. **Resolve identity before actions.** The three decisive observations are the
project identity, the exact source plan identity/state and the permitted next
action. Add a stable rendered marker carrying project/workspace IDs after the
authorized project GET completes. A marker is verification metadata, not new
visible UUID clutter. Scope approval locators to the Product Plan region, and
source checks to the exact saved version/revision. Do not seek an approval button
on Chat or use a matching project title as proof of identity.

## Pass 2 — Interaction state coverage

Plan rating: 8/10; with this explicit observation contract: 10/10.

| Area | Loading | Empty | Error | Success | Partial or interrupted |
|---|---|---|---|---|---|
| Session/workspace | Existing Checking your session status; no project text | Existing workspace creation guidance | Workspace unavailable or sign-in state | Expected account and workspace resolved | Keep protected content hidden; no guessed workspace |
| Project detail | Existing Loading project status at intended route | Missing project is an error, not an empty record | Existing project error and real retry action | Expected ID/workspace and overview | Never show the preceding project's content |
| Product Plan | Existing Loading saved plans status | Existing requirements guidance; approval absent | Actual load error; preflight stops | Exact draft and saved version/revision | Loaded project alone does not authorize approval |
| Approval | Existing disabled controls while busy | No control for non-approver or absent draft | Actual denial/conflict/error; draft preserved | Actual approved state, actor/time confirmed independently | Unknown response remains unconfirmed; no next phase |
| Architecture entry | Saved source loading | Existing no-architecture guidance | Source/configuration message | Exact approved source and generation action | Unpaid mode stops here, with zero model requests |

2. **Record the failed prerequisite.** A preflight failure must identify whether
route, project data, source data or approval failed. Never report a generic
missing button as the only explanation. No new toast or error overlay is needed;
use existing UI states and sanitized test milestones. A disabled generation
button due to absent credentials is configuration evidence, not live readiness.

## Pass 3 — User journey and emotional arc

Plan rating: 9/10; specified outcome: 10/10.

| Step | User does | Useful experience |
|---|---|---|
| 1 | Creates the project | One visible pending action; no repeated click needed |
| 2 | Opens the resulting project | Correct title/description and workspace establish orientation |
| 3 | Reviews the draft | Visible saved version and draft state establish what is being reviewed |
| 4 | Confirms approval | Exact version/revision confirmation prevents accidental agreement |
| 5 | Reloads | Same project and persisted approval establish continuity |
| 6 | Opens Architecture | Exact source and honest explicit generation action establish the boundary |

The five-second goal is clear location; the five-minute goal is a trustworthy
approval; the long-term goal is immutable evidence rather than a remembered toast.
No new emotional copy, animation or progress indicator is warranted.

## Pass 4 — AI slop risk

Plan rating: 10/10; no new issue. Classification: **app UI**. This repair adds no
hero, card mosaic, decorative icon, percentage or fictional activity. Existing
utility language and restrained layout remain authoritative. Litmus checks:
product identity yes; primary workspace anchor yes; scannable headings yes;
one job per section yes; no new cards required; no new motion required; no new
shadow dependency. These are code/plan observations, not a visual browser audit.

## Pass 5 — Design system alignment

Plan rating: 10/10; no new issue. Retain existing semantic tokens in `globals.css`,
Button, native form controls, status/alert patterns and planning navigation.
The rendered identity marker must introduce no color, spacing, font or layout
change. A separate DESIGN.md or theme rewrite would enlarge this repair without
helping the failed route synchronization.

## Pass 6 — Responsive and accessibility

Plan rating: 8/10; with explicit checks: 10/10.

3. **Use accessible, scoped observations across devices.** Preserve the existing
main landmark, labelled Product Plan region, Project planning views navigation,
exact button names, status and alert semantics. The marker must describe the
rendered record without replacing its visible heading. It must be absent during
session/project loading and after authorization failure. Test desktop, tablet
and mobile using existing device profiles. On narrow screens, approval and the
Architecture action must remain reachable by normal scrolling/keyboard focus;
do not require a desktop sidebar locator. Confirm keyboard activation and visible
focus using the existing controls. No contrast, target-size or native-device
claim is made without measurement; no relevant CSS change is proposed.

`AuthGate` already remounts protected children on pathname/workspace/account
change. Therefore the project component's retained local state does not alone
prove a stale-content defect. Exercise two-project and delayed workspace cases
before changing application state logic.

## Pass 7 — Unresolved design decisions

Plan rating: 10/10. Three choices resolved within the authorized repair: retain
the current navigation/layout; add an authoritative nonvisual record marker;
reuse current approval/error controls with named preflight milestones. No new
user preference or irreversible design choice is needed. The factual cause of
the historical failure remains an investigation item, not a design assumption.

## Implementation tasks

- [ ] **D1 (P1; human estimate 1h / agent estimate 15min)** — Project navigation:
  expose the loaded authorized project/workspace identity and await the exact
  route plus that identity before reload. Source: Pass 1. Files: project detail,
  shared browser navigation/setup helper and navigation tests. Verify with a held
  real response and immediate reload after the identity milestone.
- [ ] **D2 (P1; human estimate 2h / agent estimate 30min)** — Approval preflight:
  scope controls, assert saved source identity/state and stop on loading,
  authorization, approval or configuration failures. Source: Passes 2 and 6.
  Files: shared preflight/browser tests and evidence serializer. Verify real API
  and independent PostgreSQL actor/time/version/revision, mobile navigation,
  revoked-session/denied-approval cases and zero generation dispatch.

These are estimates, not measured execution durations. No unrelated TODO is
proposed. The parent autoplan will aggregate these tasks with DX and Engineering.

## Not in scope

- UI redesign, typography or new theme tokens: preserve verified product design.
- New routing/session state service: first test existing ownership fences.
- Automatic approval or SQL approval setup: bypasses the reviewed user workflow.
- Model/prompt/configuration changes or generation: expressly unauthorized here.
- Production readiness or all-browser certification: not established by this review.

## Completion

All seven passes evaluated. Initial plan specificity: 9/10; specified target:
10/10. Three design decisions resolved, zero deferred design decisions, no new
mockups and no product code changes. This is a scoped design clearance for
implementation; actual navigation, accessibility and persistence checks remain
unrun by this reviewer. Continue with DX then required Engineering review.

NO UNRESOLVED DECISIONS
