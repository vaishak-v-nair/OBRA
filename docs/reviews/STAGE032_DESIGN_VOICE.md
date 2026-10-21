# Stage03.2 independent design voice

Review date: 2026-10-20. Scope: the current Product Plan generation and recovery journey. Stage03.2 readiness remains an explicit operator CLI operation; it adds no browser component, endpoint, polling or automatic model call.

This is a static source review, not executed browser, visual, accessibility or model evidence. Read `docs/STAGE032_PLAN.md`, `docs/reviews/STAGE032_DESIGN.md`, `apps/web/src/components/product-plan.tsx`, `apps/web/src/lib/{pm,api}.ts`, `apps/web/src/app/globals.css`, the ordinary and controlled PM browser tests and their controlled Playwright configuration. Consulted provider error mapping and lifecycle test source to distinguish upstream failures from public API envelopes. No tests, application, network calls or credentials were used; only this review file was written.

Verdict: preserve the existing interface. No concrete UI implementation blocker was found for CLI-only readiness. The required refinement is an accurately labeled controlled upstream503 recovery case; the existing source does not yet provide that browser coverage. Scores describe source design completeness, not verification results.

## Seven dimensions

| Dimension | Score | Assessment |
|---|---:|---|
| Information hierarchy | 8/10 | Project brief, explicit usage disclosure, Generate/Retry, actual error and Check status precede the saved version and history. A generation failure does not replace the approved document with a provider panel. Keep CLI metadata in operator documentation. |
| Loading, empty, error, success and unknown states | 8/10 | Loading is a truthful waiting state; empty content requires a completed read; success follows the generation response and saved-plan reload. Unknown outcomes retain the UUID and disable another Generate. Non-timeout terminal GET recovery has less helpful copy than its initial failure response, described below. |
| User journey | 8/10 | Deliberate generation, GET-only recovery, explicit input restoration, confirmed terminal retry and exact-version approval form a coherent journey. Briefs survive failures in the mounted form. After reload, restoring submitted input is deliberately explicit and server-authorized. |
| Specificity and honest product language | 9/10 | No invented progress, optimistic model success or readiness badge is needed. “Configured” is already qualified as insufficient proof of access. Do not let `ready_for_attempt` enter the product as a generated-success state. |
| Semantic tokens and component alignment | 9/10 | Existing surface, foreground, primary, danger, border and focus tokens cover the states in both themes. Native fields and the shared Button already fit the task. No new palette, type scale or component is justified. |
| Responsive, keyboard and accessibility | 8/10 | Persistent labels, native details/select/buttons, alert/status roles, focus outlines, wrapping actions, a single-column mobile document and reduced-motion CSS are present. Controlled configuration declares desktop/mobile/tablet Chromium profiles. These are source provisions, not proof of focus behavior, announcements, contrast or native-device compatibility. |
| Unresolved decisions | 9/10 | CLI-only location and evidence semantics are settled. Preserve existing UI. The new controlled case must distinguish upstream503 from the public response status. Later paid Gate B still needs separate owner authorization; metadata readiness cannot resolve provider availability. |

## Concrete findings and bounded refinements

1. **P1 verification refinement: label the503 case at the correct layer.** `pm_provider.py:255-289` classifies an upstream503 as `provider_unavailable`, uses “The AI provider is temporarily unavailable. No new plan was saved.”, and exposes public HTTP502. `test_pm_provider_unit.py` explicitly expects this mapping. A double returning503 directly would exercise the UI but would not reproduce the current provider adapter envelope. The planned case should record upstream503 in labeled controlled-provider diagnostics and assert the actual public category/status. Keep SDK mapping unit coverage; do not alter production mapping merely to name the test “503.”

   Seed and approve a clearly human-authored plan, submit a distinct brief/instructions, attempt repeated activation while pending, and assert exactly one generation POST and one failed run. Assert the brief/instructions remain, no new plan exists, and approval actor/time/hash remain unchanged through API/SQL checks. Reload, use Check status and Restore submitted brief, and verify recovery is GET-only and Retry is unavailable until the exact own terminal run is confirmed. Do not press Retry in this case unless that extra controlled attempt is explicitly part of its assertions. Existing timeout and response-loss tests provide the pattern. Run the three existing emulation profiles during authorized Gate A; they are not live-model evidence.

2. **P2 existing copy limitation, not a Stage03.2 UI blocker.** `product-plan.tsx:86-89` reconstructs only timeout failures with the full preservation sentence. A recovered unavailable/rate-limit/invalid-output run instead reads “Planning failed: [category]. No draft was created by this run.” It preserves truth and the failure category, but rate-limit recovery loses the initial instruction to wait. Preserve the interface; a small exhaustive category-to-safe-copy mapping is warranted only if the focused assertions or usability review require parity. Do not fetch raw provider bodies or invent retry estimates.

3. **Evidence boundary:429 and invalid-output browser behavior is not established by this pass.** Source routes a confirmed provider failure through the same terminal-run check; malformed output and provider429 have lifecycle unit-test cases. The controlled browser file currently covers timeout, lost response, saved-result read failure, initial-read failure, non-dispatch rejection, editor revision conflicts and active-project rejection. It does not contain explicit provider429 or invalid-output browser cases. Report these as source/unit-test coverage until executed evidence exists; do not call them browser-verified. This gap does not justify new readiness UI or an unrelated redesign.

## Failure and preservation checks

| Scenario | Source assessment | Existing test source / remaining limit |
|---|---|---|
| Upstream503 unavailable | Safe first-response copy; exact own terminal GET precedes Retry; existing selected plan remains. Public API currently502. | Provider mapping unit case exists; focused controlled browser case remains to add and execute. |
| Provider429 | Public429 with an actual failed run; initial copy says wait before explicitly starting another request. | Rate-limit lifecycle unit case exists; browser behavior not executed here. |
| Local admission429 | `rejectedBeforeAdmission` clears the new UUID without inventing a terminal run; input is unchanged. | Distinct from provider429; do not assert an admitted run for this rejection. |
| Provider504 timeout | Preservation copy identifies timeout and no new draft; retry performs fresh exact-run confirmation. | Controlled timeout test asserts brief, approval hash/time, explicit restoration, two deliberately distinct attempts and no new plan. Read only, not rerun. |
| Invalid model output | A failed validation must not become a successful draft; same exact-own-run recovery applies once failure is recorded. | Malformed-output lifecycle unit case exists; no explicit controlled browser case in the reviewed file. |
| Lost response / failed GET | UUID remains; Generate stays disabled; no clear-reference shortcut or automatic POST retry. | Controlled response-loss and saved-result-read-failure cases assert this behavior. |
| Brief and approved plan survival | Failure handlers do not replace brief/instructions; saved plan stays mounted. Reload intentionally resets form defaults until explicit authorized restoration. | Timeout case checks survival and restoration. The503 case must retain both UI and API/SQL assertions rather than infer persistence from a visible badge. |

## Litmus checks

| Check | Assessment |
|---|---|
| Can a user identify the object and next action? | Yes in source: Product Plan, brief, Generate/Retry and Check status. |
| Does failed generation preserve the useful object? | Yes in source: the selected saved document remains; assert approval preservation in the new case. |
| Is unknown distinct from failure and success? | Yes: retained UUID and GET-only recovery; a missing matching run does not enable Retry. |
| Is repeated activation bounded? | Synchronous `gate` ref and disabled busy controls prevent a second in-flight action; execute the planned count assertion. |
| Does success mean saved work? | Source waits for saved-result reload before announcing validated draft success; failed reload retains recovery reference. |
| Is every new surface necessary? | No new browser surface is needed for the operator CLI. |
| Does hierarchy depend on decoration? | No: headings, labels, saved-state text and spacing provide structure; no new cards or motion. |
| Is the evidence honestly labeled? | This review is static. Controlled provider behavior and authored fixtures cannot certify live Gemini success. |

The primary design direction is supported with the upstream/public-status refinement above. No application edit, new endpoint or broadened UI work is requested by this review. Sequential DX and engineering review can proceed; execution and any real live success remain separate gates.
