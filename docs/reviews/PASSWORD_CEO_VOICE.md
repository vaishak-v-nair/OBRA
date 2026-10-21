# Independent password policy product and security review

Review date: 2026-10-19. Scope: the owner-selected 15–128-character creation policy, existing 12-character login compatibility, no new recovery workflow, no paid request. This is a source and plan review, not executed implementation verification.

**Judgment: proceed within the proposed scope, with the acceptance refinements below.** The plan identifies the right boundary: validate a newly chosen credential without reinterpreting an existing credential. No migration, bulk rehash, session invalidation, reset workflow, new dependency, or provider call is needed to achieve that outcome.

## Six dimension judgments

| Dimension | Judgment | Reason |
|---|---|---|
| Premises | Sound, with one clarification | The owner selected 15 for new credentials. Existing passwords remain valid. “Preserve every hash/session” must describe preservation through the policy change, while retaining normal login rotation and eligible Argon2 parameter upgrades. |
| Problem | Correctly bounded | The concrete problem is a 12-character registration rule plus corresponding browser guidance. Raising creation length does not establish complete password security or solve the unavailable live model. |
| Scope | Appropriate | Change the creation schema, shared auth form, focused tests and current documentation. Keep recovery, MFA, password changes, later agents and paid verification outside this work. |
| Alternatives | Minimal approach preferred | A reusable creation-only type and a small form validation change meet the decision. A global login minimum would strand existing users; a reset workflow creates a separate recovery and identity-verification product. Retaining 12 or allowing 6 would contradict the selected decision. |
| Product risk | Manageable after the required refinements | Silent truncation, Unicode disagreement and accidental lockout matter more than adding visual complexity. Password manager autofill, pasted passphrases, precise errors and preservation of input are the main user-facing requirements. |
| Six-month maintainability | Good if policy boundaries stay explicit | A single backend creation type, generated schema constraints, documented mirrored browser limits and mandatory boundary tests are sufficient. A policy service, shared package, database policy version or endpoint scaffold would add maintenance without a present use. |

## Findings and acceptance refinements

### P1 — Clarify preservation so compatibility tests do not disable existing session security

The plan's “preserve every existing user/hash/session” and “hash/session preservation” wording is broader than the current login behavior. `auth.py:27–40` revokes the presented active session and commits a fresh session; `auth.py:138–139` permits an Argon2 parameter rehash after successful verification. Existing tests explicitly require rotation and revocation (`test_auth_workspaces.py:55–66`).

Require the policy change itself to leave existing identities, hashes, sessions, memberships and projects untouched. The legacy fixture should prove its original session still authenticates before a new login, its 12-character password still signs in through the real endpoint, and normal rotation still occurs when that session is presented. For a current-parameter hash, assert the hash remains identical; for an eligible parameter upgrade, preserve successful login without routing through the creation minimum. Do not weaken the existing rotation assertion to satisfy a literal reading of preservation.

### P1 — Make code-point and no-truncation acceptance explicit for both auth modes

The shared password input currently applies `maxLength={128}` to signup and signin (`auth-form.tsx:28`). The server accepts up to 128 Python string characters (`schemas.py:43–54`). Browser string/HTML length handling must not become the authority for the server's code-point policy, particularly for supplementary-plane characters. The plan already recognizes the correction; its tests need precise examples.

Require ASCII 14/15/128/129 boundaries, an astral-character boundary case, and an accepted 128-code-point non-ASCII password that also logs in through the browser. Check that a pasted over-limit value remains complete in the input, receives a clear error, sends no auth POST and remains editable. Apply that upper-bound behavior to signin as well as signup. A test using only `fill()` does not establish actual paste behavior. Preserve `new-password`/`current-password` autofill and do not add clipboard interception or password-manager restrictions.

### P2 — Define exact-value semantics beyond a generic “Unicode/spaces” case

Creation currently rejects `value.isspace()` and otherwise returns the exact password (`schemas.py:50–55`); login verifies that exact value (`auth.py:134`). A browser `.trim()`-based policy would introduce different Unicode whitespace behavior and risks encouraging normalization.

Test an accepted password with leading and trailing spaces, whitespace-only rejection, and combining characters without normalization. Assert that registration followed by login uses the same exact value and that a meaningfully altered value fails. Keep the server authoritative for whitespace-only rejection unless a matching client rule is deliberately specified and tested. Help text should say 15–128 characters and allow passphrases; composition rules and strength promises are unnecessary.

### P2 — Reuse creation policy without spreading it into authentication

Today `RegisterInput` inherits `LoginInput`, then adds a validator (`schemas.py:43–55`). The proposed `NewPassword` should carry the creation constraints in Pydantic/OpenAPI as well as at runtime; hidden validator logic alone would leave client discovery advertising a minimum of 1. Login must retain its 1–128 schema. Future reset/change schemas should reuse `NewPassword` only when choosing a new credential, not when checking the current password or refreshing hash parameters.

No frontend package or generated-policy infrastructure is justified for one form. Keep the few mirrored browser limits obvious and verify them through API/browser boundary cases. Add the new test identities to the existing mandatory baseline without renaming or removing old cases. Existing policy coverage only rejects `short` and checks the user count (`test_auth_workspaces.py:71–86`); the new rejected-boundary test also needs unchanged session count and no authenticated-session establishment.

### P2 — Publish current policy separately from historical evidence

`README.md:68` describes the old 12–128 policy, and `docs/VERIFICATION.md:139` still describes an unresolved owner choice. Update current guidance to distinguish new creation from existing-password login and retain the visible statement that recovery is unavailable. Preserve historical reports and immutable receipts as historical facts.

After source changes, capture the actual new Gate A result and source fingerprint. Gate C must remain PARTIAL without current live evidence; the historical authorized 503/exit1 remains a failed attempt, not a new password-policy failure or a consumed authorization that can be reused. The current summary implementation retains a recorded FAIL even when receipt validation rejects source identity (`verification.py:590–616`), so describe both the historical failure and the lack of current-source live success accurately. Do not change verification semantics merely to obtain a preferred label, and do not run Gate B.

## Review limits

Reviewed the plan, authentication schemas/routes/security helpers, shared form/API helper, backend fixtures and auth tests, browser helpers/team coverage/configuration, verification baseline/summary code and current documentation. No implementation, database, browser or model tests were executed; no implementation or historical evidence was edited. The initial search for `apps/web/e2e` returned a missing-path error; the actual browser tests were then inspected under `apps/web/tests`. This review makes no runtime PASS or VERIFIED claim.
