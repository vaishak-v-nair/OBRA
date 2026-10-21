<!-- /autoplan restore point: C:\Users\vaish\.gstack\projects\OBRA\main-autoplan-restore-password-20261019T172319Z.md -->
# ORBA password policy implementation plan

Owner decision: require15-128 characters for new credentials, preserve every existing user/hash/session and permit login with previously valid12-character passwords. Keep Argon2id, server throttling, CSRF, sessions and authorization. No paid Gemini call, historical receipt modification, automatic commit or Stage04.

Implementation sequence:
1. Inspect the existing independent login/register schemas, real authentication routes, form, fixtures and gates; capture source/evidence restore metadata.
2. Run sequential CEO, form-design, DX and engineering reviews. Reuse current schemas and native controls; no new infrastructure.
3. Introduce a reusable validated NewPassword type for credential writes. RegisterInput uses15-128; LoginInput remains1-128. Preserve the whitespace-only rejection without trimming, normalizing, truncating or adding composition rules.
4. Update signup help/minimum and Unicode-code-point validation. Keep current-password autofill and login compatibility. Remove password maxlength truncation and reject over-limit input clearly before POST.
5. Add real-PostgreSQL tests for14 rejection/no user or session,15 acceptance/real salted hash,64/128/Unicode/spaces round trips and129 rejection. Seed an explicitly identified legacy12-character account/session and verify real login plus hash/session preservation.
6. Add desktop/mobile/tablet real-browser cases for signup boundary/server rejection, paste/no truncation and long-passphrase login. Preserve all baseline identities and register additional mandatory cases.
7. Run targeted tests, then the complete fixed Gate A sequentially against guarded orba_test. No model credentials or calls in Gate A.
8. Record actual commands, counts, new source fingerprint and immutable receipts; recompute Gate C as PARTIAL with the historical failed live attempt retained.

Current repository has no password-change/reset endpoint. Do not invent one or claim it exists. Future change/reset request schemas must reuse NewPassword; ordinary login and hash parameter upgrades must never enforce creation length. No migration, forced reset or session invalidation is required.

UI scope: yes, signup form/validation/help and signin input. DX scope: yes, API schema, future policy reuse, verification commands and docs.

Task checklist:
- [x] Intake and restore metadata
- [x] CEO review
- [x] Design review
- [x] DX review
- [x] Engineering review and test plan
- [x] Policy/form implementation
- [x] Meaningful PostgreSQL/browser tests
- [x] Full deterministic Gate A
- [x] Evidence, documentation and final audit

## Decision audit trail

| ID | Phase | Decision | Class / principle | Reason |
|---|---|---|---|---|
| C1 | CEO | Separate reusable NewPassword from unchanged LoginInput | Mechanical / Explicit, complete | Future writes use15; existing12 credentials remain verifiable |
| C2 | CEO | Remove native password maxlength and count code points explicitly in both modes | Mechanical / Complete | Prevent silent paste clipping and UTF-16/server disagreement |
| C3 | CEO | Preserve ordinary rotation/eligible rehash while avoiding policy-induced mutations | Mechanical / DRY | Existing security behavior must not be disabled by compatibility assertions |
| C4 | CEO | Expose creation limits in OpenAPI and test exact-value spaces/Unicode | Mechanical / Complete | Private validators and ASCII-only cases are insufficient |
| C5 | CEO | Reuse current identity TODO rather than add a reset/change workflow | Mechanical / Pragmatic | No such endpoint exists and this request explicitly covers future policy |

CEO completion: primary PASSWORD_CEO.md plus independent in-host PASSWORD_CEO_VOICE.md examined actual schemas/routes/form/security/tests/gates. All6 strategic dimensions agree with acceptance refinements adopted; this is same-family independent review, not outside-model consensus. No taste or user-direction challenge remains. Design follows only after these artifacts are written.

Design completion: primary PASSWORD_DESIGN.md and independent PASSWORD_DESIGN_VOICE.md cover all7 passes and7 litmus judgments. Adopted helper/error association, pre-lock validation, no maxlength/paste interception, code-point checks in both modes, native Tab/Enter/autocomplete coverage. Existing generic network-copy/session-refresh concerns are bounded: protected content remains session-gated and these paths are not rewritten by the length policy. The external light/dark HTML sketch was rendered and actually inspected; it is not application verification. Proceed to DX only after this artifact is written.

| ID | Phase | Decision | Class / principle | Reason |
|---|---|---|---|---|
| D1 | Design | Associate helper and error with password input | Mechanical / Complete | Visible copy must also be available to assistive technology |
| D2 | Design | Validate before acquiring submit lock; keep input editable | Mechanical / Explicit | Invalid lengths must not leave a disabled form |
| D3 | Design | Keep current themes/layout/native autofill, paste and keyboard | Mechanical / DRY | Credential policy needs no new form/navigation system |

DX completion: PASSWORD_DX.md and independent PASSWORD_DX_VOICE.md cover all8 dimensions,9-stage journey, source walkthrough, honest unmeasured warm TTHW target, errors, safe upgrades and tooling. Six planned DX boundaries agree (no outside-model claim); no unresolved direction/taste choice. The active backend baseline is stage031_backend, so append new identities there without removing the original102/139 lists. Expose and test generated OpenAPI bounds, and keep the old503/exit1 historical. Proceed to Engineering on this amended plan.

| ID | Phase | Decision | Class / principle | Reason |
|---|---|---|---|---|
| X1 | DX | Publish new-vs-login limits and future workflow limits in current docs | Mechanical / Explicit | No forced reset, misleading recovery feature or old live certification |
| X2 | DX | Add identities to active stage031_backend and every browser viewport | Mechanical / Complete | New tests must be mandatory, not merely discoverable |
| X3 | DX | Guard any legacy fixture seeder to exact testDSN before connecting | Mechanical / Explicit | Browser compatibility setup must never mutate development data |

Engineering completion: PASSWORD_ENG.md and independent PASSWORD_ENG_VOICE.md evaluated architecture, code quality, every new branch/test and performance. Six engineering boundaries agree after refinements; no outside-model consensus is claimed. Tests will preserve both normal presented-session rotation and an independent old session, and separately cover eligible12-character Argon2 parameter upgrades. Server whitespace rejection stays authoritative; client checks length only. The test plan exists in docs and external gstack project storage. No new model/prompt eval is authorized.

| ID | Phase | Decision | Class / principle | Reason |
|---|---|---|---|---|
| E1 | Eng | Test current and eligible-old legacy hash parameters separately | Mechanical / Complete | Compatibility must not disable normal security upgrades |
| E2 | Eng | Seed only guarded test accounts; never weaken registration fixtures | Mechanical / Explicit | Legacy setup is not a production bypass |
| E3 | Eng | Run a real14-policy red assertion before implementation | Mechanical / Complete | Establish observed old behavior, then verify the new rejection |
| E4 | Eng | Freeze source for full Gate A and preserve all historical artifacts | Mechanical / Complete | Changed auth needs a new fingerprint; no paid attempt is authorized |

## Cross-phase themes and implementation tasks

Creation/verification separation, exact string/paste/Unicode behavior, real legacy fixtures, and honest source-bound evidence recurred independently across all phases. All are covered in the amended plan. No owner preference is unresolved: the user explicitly authorized implementation of15 and the full deterministic verification. This authorization takes precedence over asking for another generic plan confirmation. No deployment/commit/paid approval is inferred.

- [x] C1: Implement named NewPassword15..128; keep LoginInput unchanged.
- [x] C2: Validate intact code-point lengths in both form modes without native clipping.
- [x] D1: Associate help/field errors and support invalid focus/correction.
- [x] E1: Add real-PostgreSQL bounds/exact-value/legacy/session/rehash tests.
- [x] E2: Add a strictly guarded test-only legacy account seeder.
- [x] E3: Add real clipboard/keyboard/Unicode/legacy browser journeys on3 viewports.
- [x] X2: Preserve all baseline identities and append new active mandatory cases.
- [x] E4: Run full Gate A and document actual results, fingerprint and PARTIAL.

Implementation progress: the new14-character test actually failed on old behavior (201 vs422), then the policy passed18 PostgreSQL/backend cases after correcting a fixture cookie-domain error. The failure log retains CookieConflict with two ephemeral cookie values redacted. All9 new browser cases passed after exact alert assertions were scoped to main to exclude Next route announcer. No assertion was weakened. Source is now frozen for the full deterministic gate; no paid request occurred.

Final execution: full Gate A actually exited0 with157 backend/60 core browser/18 controlled PM browser, all14 commands0 and zero skips/retries. Fingerprint19097cc5cb84c430e53bf68dee65299e8a6dbb0a4b5b6a5cb4996ac9849efed9 is stable across both manifests. Gate C actually exited2/PARTIAL. Final audit checked313 historical artifacts unchanged, latest-B unchanged,113 pre-existing source files unchanged and exactly6 intended source additions/modifications. One audit reader first rejected the expected latest-A update because of Windows separators; normalization fixed the comparison without altering receipts. No paid request, commit or development reset occurred. Task status: DONE_WITH_CONCERNS only for the separately unverified Stage03 live gate; password-policy implementation and full deterministic verification are complete.

Operational learnings: use the actual testserver.local cookie domain when exercising real session rotation; a domainless test cookie creates ambiguous cookies and can expose ephemeral values in exception repr. Scope exact form alerts to main because Next has a separate route-announcer alert. Normalize Windows inventory paths before applying a narrow allowed-pointer comparison, without loosening immutable artifact checks. These learnings are recorded here and in local project artifacts; memory storage is unchanged.

## GSTACK REVIEW REPORT

| Phase | Artifact / coverage | Independent voice | Status |
|---|---|---|---|
| CEO | PASSWORD_CEO.md,11 sections + alternatives/registries | PASSWORD_CEO_VOICE.md,6 judgments | Clear |
| Design | PASSWORD_DESIGN.md,7 passes + rendered fallback sketch | PASSWORD_DESIGN_VOICE.md,7 dimensions/litmus | Clear with adopted refinements |
| DX | PASSWORD_DX.md,8 passes +9-stage journey | PASSWORD_DX_VOICE.md,8 judgments | Clear |
| Engineering | PASSWORD_ENG.md,4 sections + full test matrix | PASSWORD_ENG_VOICE.md,6 judgments | Clear |

[running under Codex — nested codex passes skipped; set GSTACK_FORCE_CODEX_REVIEW=1 to force]

All independent voices are in-host Codex-family reviews, not external-model consensus. Missing skill helpers use degraded defaults; no global repair, telemetry consent change or paid provider probe. Cross-phase findings are reconciled and the owner has already directed implementation. Review/implementation status is DONE_WITH_CONCERNS: password-policy Gate A passed; overall Stage03 remains PARTIAL solely without applicable live success. No new paid request is authorized.

NO UNRESOLVED DECISIONS
