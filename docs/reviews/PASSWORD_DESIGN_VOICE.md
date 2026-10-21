# Password policy: independent form design review

Date: 2026-10-19. Scope: `docs/PASSWORD_POLICY_PLAN.md` and current repository source. No prior review artifact or skill definition was consulted. Only this review file was written. No browser, application, database, model, test suite or Git command was run.

Verdict: **PARTIAL — plan/source review only.** Proceed with the password change after making D1–D4 explicit acceptance criteria. The proposed journey and existing layout fit the request; no visual redesign or password-reset/change workflow is needed. Current UI still advertises 12–128 characters and still has native password `maxLength={128}` (`apps/web/src/components/auth-form.tsx:28–29`). This review does not establish implementation or runtime success.

## Findings

### D1 — Required: keep creation and sign-in rules distinct in the form

The plan correctly chooses 15–128 code points for creation and 1–128 for sign-in (`docs/PASSWORD_POLICY_PLAN.md:9–10,35–36`). The shared `AuthForm` currently branches the minimum and autocomplete by `signup` (`apps/web/src/components/auth-form.tsx:28`); retain that explicit distinction. Signup help should say **“Use 15 to 128 characters.”** Sign-in must never show the creation minimum or reject a legacy 12-character credential for being too short. Do not add composition rules, a strength meter, a second password field, normalization or trimming.

The current note combines the rule with two unavailable features (`auth-form.tsx:29`). Keep the length rule immediately after the password field and keep the truthful email-verification/recovery limitation as a separate short note. This improves scanning without inventing a recovery action. No new feature copy belongs on sign-in.

Acceptance: a legacy 12-character password can be submitted from sign-in; a 14-code-point signup password is rejected clearly; 15 code points are accepted. This must hold for ASCII and supplementary Unicode characters. Login with 1–14 code points must reach ordinary authentication rather than a creation-policy error.

### D2 — Required: untruncated values and one code-point rule on every submission path

Removing `maxLength` from both password inputs is necessary. The existing native cap is based on UTF-16 units and can clip a long paste before the application can explain the error. A native minimum alone does not prove the requested code-point lower bound either. The plan already identifies both risks (`docs/PASSWORD_POLICY_PLAN.md:10,36`); make them observable in browser acceptance rather than merely checking attributes.

Read the complete submitted password, count code points explicitly, validate the mode-specific bounds, and send the exact original value. Run this check before setting the submission lock or busy state; otherwise a local rejection could leave the form disabled (`auth-form.tsx:17–24`). Do not rely on typing handlers: paste, password-manager/autofill and Enter submission all need the same submit-time check. If native custom validity is used, clear stale validity on correction so it cannot prevent the next submit handler from running.

Acceptance: 129 ASCII code points and 129 supplementary code points remain intact in the field, show a clear over-limit message and cause no auth POST. Correcting either to a valid value permits one deliberate submission. A 128-supplementary-code-point value is not silently capped at 64. Exact leading/trailing/internal spaces and combining sequences survive the round trip; whitespace-only signup remains rejected without changing the value. Do not promise grapheme-cluster counting: the selected policy is code-point counting.

### D3 — Required: attach the policy and validation error to Password

The current nested label supplies the accessible name, and the form-level error has `role="alert"`, but the input has no `aria-describedby` and no field-invalid state (`auth-form.tsx:28–29`). The new custom length check needs a stable help ID, a password error ID and `aria-invalid` after a failed validation. Associate the help/error with the input, focus Password when custom validation blocks submission, and retain the entered email, name and password on failure. Avoid announcing an invalid state on the untouched empty form.

Use specific, mode-correct messages: **“Use 15 to 128 characters.”** for signup bounds, and **“Use no more than 128 characters.”** for a sign-in upper-bound failure. Keep ordinary incorrect-credential responses generic. `ApiError.details` already preserves server field identifiers (`apps/web/src/lib/api.ts:11,37–41`; `apps/api/orba/main.py:89–102`), so a server password-policy rejection can be associated with Password without mislabeling every auth error as a password-format problem. Do not render rejected password values in messages.

Acceptance: the visible help, invalid state and error association can be inspected in the browser; Tab/Shift+Tab and Enter still work; correction clears obsolete feedback; a real server rejection returns to an editable form with inputs preserved. This review has not established assistive-technology behavior.

### D4 — Required: specify the missing browser behaviors instead of inheriting a happy-path helper

The existing signup helper fills one ordinary password and clicks Create account (`apps/web/tests/helpers.ts:2–8`). It cannot establish the new boundaries, legacy sign-in, paste behavior, error correction or keyboard submission. Preserve baseline helpers and test identities; add focused cases as the plan requests.

For each configured desktop/mobile/tablet project, cover the 14/15 and 128/129 boundaries, supplementary Unicode, full-value paste with no POST when rejected, corrected-value resubmission, and long-passphrase sign-in. Include a seeded legacy 12-character account in the real browser sign-in path as well as API verification. Keep `new-password` on signup and `current-password` on sign-in, and assert those attributes. Exercise at least one native Tab/Enter journey instead of only locator clicks. A programmatic fill or synthetic paste event alone must not be described as real clipboard paste or password-manager verification.

The current projects all run Chromium, including iPhone/iPad emulation (`apps/web/playwright.config.ts:8–11`). Their success would support responsive browser behavior, not native Safari/iOS, a real on-screen keyboard, a particular password manager or every browser. Check visible errors, focus, overflow and reachable submission controls at the existing viewport sizes and in both themes. Keep the configured credential-safe trace/screenshot policy (`playwright.config.ts:5–7`).

### D5 — Existing concern, bounded follow-up: auth connection-error copy refers to Projects

`request()` gives every non-PM POST transport failure the project-creation message “Check Projects” and “Your draft is preserved here” (`apps/web/src/lib/api.ts:28–35`), and `AuthForm` displays it unchanged (`auth-form.tsx:24,29`). This is misleading after sign-in/signup and does not identify what the user can safely conclude. It predates this policy change. Do not claim the password work fixes it or broaden into a recovery system. If touched within the auth form, use an auth-specific message that says the outcome could not be confirmed, retains the fields and does not assert that account creation failed. Never automatically retry the POST.

### D6 — Existing concern, bounded follow-up: a successful auth POST can be followed by an unsuccessful session read

`AuthForm` awaits `refresh()` and then navigates (`auth-form.tsx:21–23`); `refresh()` catches session/workspace-read failures and resolves (`apps/web/src/components/session.tsx:30–40`). The protected gate subsequently presents a session/workspace state (`session.tsx:66–70`). This is a distinct partial-success journey, not proof that the submitted credential was invalid. Preserve the current protection and do not introduce a password-error message or blind duplicate signup for this state. Record it separately if observed during verification. Improving that broader journey is not necessary to invent for this narrow policy change.

## Seven design-dimension assessments

| Dimension | Assessment | Basis and required disposition |
|---|---|---|
| 1. Information hierarchy | Suitable with D1 refinement | One heading, a short description, labeled fields and one primary action already make a coherent form. Separate password guidance from feature-availability copy; do not add decorative policy UI. |
| 2. State completeness | Needs D2/D3; existing limits recorded | Initial, busy and generic error states exist. Add local invalid/corrected states without transient busy UI. Auth/session partial outcomes remain distinct from password errors; D5/D6 are pre-existing. |
| 3. User journey | Sound with explicit compatibility tests | Signup -> authenticated empty workspace or preserved invitation destination already exists. Sign-in retains current-password autofill and legacy credentials. Preserve invitation fragments and the success destination. |
| 4. Specificity and clarity | Needs D1/D3 | The plan names exact bounds, but does not yet define field association or correction behavior. Proposed messages state a concrete correction and never demand unnecessary character classes. |
| 5. Design-system alignment | Suitable | Reuse `.standard-form`, `.form-note`, `.error-message`, native inputs and shared `Button`. Light/dark semantic tokens and focus styles already live in `globals.css:3–6,14`; no new library, palette or abstraction is justified. |
| 6. Responsive behavior | Planned; runtime unverified | Form width is capped, inputs fill available width, mobile spacing already exists, and mobile buttons have a 44px minimum (`globals.css:9,14,18`). Long help/error text, zoom/overflow and keyboard-obscured controls need observation; source cannot prove them. |
| 7. Accessibility and input methods | Needs D3/D4 | Nested labels, required fields, native email/password types, autocomplete and focus rings are good foundations. Add help/error associations and invalid focus; retain native Tab/Enter and test submit-time validation for values supplied without typing. |

## Seven litmus judgments

| Litmus | Judgment | Reason |
|---|---|---|
| 1. Can a new user discover the required password length before submitting? | Pass after D1 | Signup help states 15–128 beside Password; no composition puzzle. Current 12-character copy has not yet been changed. |
| 2. Can an existing user sign in with a previously valid 12-character password? | Pass in plan; runtime unverified | Login remains 1–128 with current-password autofill. Add a real browser legacy case; do not infer it from new-account helpers. |
| 3. Can a user paste a long password without losing characters silently? | Needs D2/D4 | Remove both native caps and prove exact retained input, a clear 129-character rejection and no auth POST. |
| 4. Do ASCII, supplementary characters, spaces and autofilled values obey the same policy? | Needs D2/D4 | Count code points at submit, preserve the original value and test the boundaries. Do not count UTF-16 units or normalize visible equivalents. |
| 5. Can a keyboard or screen-reader user identify and correct the invalid field? | Needs D3/D4 | Accessible labels exist; help/error associations, invalid state, correction and focus behavior need explicit implementation and browser assertions. |
| 6. Does every state tell the user what happened without making up success or failure? | Partial | Busy lock and error retention exist. D5's transport copy and D6's auth/session partial outcome are pre-existing limits; do not label them solved or assert a failed account creation after an uncertain response. |
| 7. Is the work proportional to this request and consistent with the existing UI? | Pass | Small native form/schema changes and meaningful regression cases suffice. No redesign, reset workflow, forced re-enrollment, new dependency or paid model call is needed. |

## State and journey acceptance

| State | Expected user-facing behavior |
|---|---|
| Initial/empty | Labels and signup guidance are visible. Required native controls reject empty submission. No error is announced before a deliberate invalid submission. |
| Locally invalid | Keep the full value, name the correction, associate it with Password and keep the form editable. No POST and no stuck busy/lock state. |
| Submitting | Preserve the current single-submission lock and disabled controls. Retain `aria-busy`; button text communicates progress. Do not add a second password-specific asynchronous step. |
| Authoritative server failure | Show the real safe error; map a password-policy detail to Password when applicable. Preserve values, unlock the form and allow a deliberate correction/resubmission. |
| Transport outcome unconfirmed | Do not assert that registration or login failed; preserve values and avoid automatic POST retry. D5 records the existing copy limitation. |
| Confirmed success | Continue through current session checks to the empty-workspace/home or invitation destination. No invented password-success screen is needed. |
| Auth POST succeeded but session/workspace read failed | Keep protected content gated and show the existing session/workspace error state. Do not call this a password rejection or recommend duplicate account creation. D6 records the existing limitation. |

No unresolved owner preference is required for this change. The review recommends the existing layout, static length help, field-associated errors and native controls. The remaining work is implementation and real verification of those mechanical choices. Autofill-token checks and Chromium device emulation must remain accurately bounded evidence.
