# Password policy CEO review

Mode: SELECTIVE EXPANSION, limited to the owner's explicit credential-policy scope. This is a review of real files and a proposed implementation, not executed-test evidence. The installed skill-start/probe helpers are absent, so interactive degraded defaults apply. The base branch is main with no remote; the current checkout is uncommitted above e3fccd6. No nested model/CLI or Gemini call is required for this review.

## Premises and reuse

The user chose15 explicitly, including grandfathered login, unchanged hashes/sessions and passphrase support. `LoginInput` already accepts1-128 and `RegisterInput` adds its own12-character check; preserving that separation directly addresses compatibility. `auth.py` has register/login/logout/me/csrf only, so a password-reset or change feature would add a new product/security flow rather than update an existing one. Shared credential-write validation is the complete policy extension now; future schemas must import it.

`auth-form.tsx` has a native password maxLength128. Browser maxlength can discard excess pasted text, contrary to the explicit no-truncation requirement. Explicit code-point validation with no native password maxlength is in the direct blast radius and avoids changing the value itself.

| Subproblem | Existing implementation to reuse |
|---|---|
| New credential validation | RegisterInput and Pydantic annotated types |
| Existing credential verification | LoginInput, verify_password, Argon2id in security.py |
| Sessions and CSRF | establish, optional_session and csrf_guard, unchanged |
| Throttling | Existing PostgreSQL advisory-lock account/IP limiter |
| UI states and account flow | AuthForm request helper, busy lock, server alert and session refresh |
| Verification | Existing guarded PostgreSQL fixtures and fixed Gate A runner |

## Alternatives and trajectory

| Approach | Coverage | Effort (human / agent) | Risk and tradeoff |
|---|---|---|---|
| Change12 to15 in the existing private registration validator | 7/10 | 1hour /10min | Smallest diff, but future writes have no named reusable contract and native paste truncation remains |
| Shared NewPassword type plus intact-value form validation and real compatibility tests | 10/10 | 3hours /40min | Selected: existing auth authority/flows stay intact; separate creation/login rules are explicit |
| New credential service with change/reset flows | Different product scope | 2days /3hours | Rejected for this task: new recovery/identity/session decisions and duplicate auth machinery |

```text
CURRENT: register12 / login1 + native paste limit
   -> THIS PLAN: shared new-credential15 / login1 + intact input + real regressions
   -> IDEAL: explicit policy reused by separately authorized recovery/change flows
```

The larger opportunity is verified recovery/MFA, already deferred in TODOS.md; it is not necessary for this policy rollout. Five relevant improvements were considered: accurate min/max help, password-manager autofill, paste preservation, Unicode-count parity and reusable future policy. All five are direct requirement coverage, not unrelated scope expansion. No new infrastructure or dependencies are justified. Temporal decisions are resolved now: hour1 separates new/login rules; hours2-3 preserve raw values; hours4-5 use guarded legacy fixtures; hour6 verifies full Gate A and rejects stale live proof (human estimate3hours / agent roughly40min, not a measured completion promise).

## 1. Architecture

The backend remains the only auth authority; no new endpoint or stored field is added. The proposed NewPassword type is consumed only by credential writes, while LoginInput stays independent. No user/session scanning or data migration is needed.

```text
signup form -> intact string -> RegisterInput(NewPassword15..128)
                               -> existing limiter -> Argon2id -> User/session
signin form -> intact string -> LoginInput(1..128)
                               -> existing limiter -> verify stored hash -> session
future change/reset schema --> same NewPassword (workflow not implemented)
```

## 2. Error and rescue

Existing Pydantic validation and AuthForm alerts already provide the error channels. New client validation must happen before the POST and before the busy lock is acquired, preserving the entered value. Server rejection remains authoritative when native/client checks are bypassed.

| Codepath | Failure / exception | Rescue and user result |
|---|---|---|
| RegisterInput | Missing/empty/wrong type/14 or129 characters; ValidationError | Existing422 error envelope, no user/session row |
| NewPassword | Whitespace-only value; ValueError | Same validation response, value never trimmed |
| AuthForm | Code-point length outside limits | Visible alert before POST, input unchanged and submit available |
| Existing login | Wrong legacy credential | Existing401; original hash/session records remain valid |
| request helper | API/CSRF/database unavailable | Existing safe error, no fake account success or auto POST retry |

## 3. Security

Argon2id, opaque sessions, session rotation, CSRF/Origin, role enforcement and throttling are read and remain unchanged. The relevant threat is accidentally applying the new minimum during verification, which would lock out valid legacy users. A second threat is truncated input authenticating against a different string; tests must vary the final character and check full-value hashes without printing them.

No composition classes, client-stored credentials, external secrets, new data access or third-party dependency is introduced. The15-character choice alone is not a claim of complete NIST/production-security compliance. All-whitespace rejection preserves existing behavior; surrounding spaces and Unicode remain significant.

## 4. Data and interaction edges

```text
nil/empty/wrong type -> schema422 -> no writes
14 new /129 any -> loud client/schema rejection -> input unchanged
15..128 new -> no transform -> hash full string -> actual user/session
12 legacy login -> verify existing hash -> actual session
double submit -> existing form lock; failed save -> error, not redirect
```

Native HTML counts UTF-16 code units while Python counts Unicode code points. The client must count code points explicitly; its native minimum is only an additional convenience, never the authority. Removing maxlength prevents silent paste clipping, while explicit maximum validation keeps the existing128-character resource bound. Failed registration must not revoke an existing session.

## 5. Code quality

Reuse one Pydantic alias and the existing AuthForm rather than add an auth-policy service or duplicate routes. Name the shared type NewPassword to communicate that it must not be used for login. Keep the client limit check short and local, with backend limits documented and tested rather than invent a shared package for two constants.

## 6. Tests

The existing auth/workspace and all Stage01/03 tests remain mandatory. Add real PostgreSQL boundary, hash/full-string, legacy12 hash/session and schema-contract cases; explicitly authored legacy fixtures are setup, not mocked authentication. Add three browser journeys on every existing viewport: boundary/new account, paste/long passphrase and legacy signin.

```text
NewPassword bounds/space/type -> Pydantic contract tests
register14/no rows + register15/real salted hash -> HTTP/PostgreSQL tests
64/128/unicode/spaces/full suffix -> real hash + login + negative suffix
legacy12 hash/session unchanged -> real stored rows + HTTP verification
client14/15, overlimit intact paste, legacy UI -> actual browser/API/PostgreSQL
no paid calls + all regressions -> fixed Gate A environment/result validation
```

Hostile tests bypass the form and submit14 directly, supply129, use astral Unicode and remove the final passphrase character at login. Friday-confidence coverage is a real12-character legacy account and old session accepted by the new app while a new14-character account is rejected with no writes. No timed external service or model evaluation is needed because provider/prompt/lifecycle behavior is unchanged.

## 7. Performance

The maximum accepted credential stays128 code points, so Argon2 cost and DB access do not grow. Explicit string-length validation is bounded and occurs before credential work. No new association traversal, index, cache or background process is introduced; the existing account/IP limiter remains the load boundary.

## 8. Observability

The existing safe validation envelopes and security event names are sufficient. Logging password text, hashes or length-specific credential diagnostics would add risk without helping rollout. Native test reports, actual SQL assertions and source-bound receipts establish verification; no new dashboard or metric pipeline is justified.

## 9. Rollout

No migration, hash rewrite, session revocation or forced reset is part of rollout. Frontend and backend need the coordinated policy release; an old frontend can still submit14 but the new backend correctly rejects it. Rollback is a deliberate source-policy reversal with tests, never a database downgrade or reset; local services should be restarted by their normal commands after review.

## 10. Long-term trajectory

Named creation-only validation makes future credential writes clear while protecting verification compatibility. Reversibility is5/5 for code, with no data mutation beyond ordinary authorized registration/login. Future reset/change features remain on the existing production-identity TODO and must not inherit LoginInput by mistake.

## 11. Design

The form retains the current themes, structure, labeled password field, autocomplete, busy state and alert role. Help explains15-128 and passphrases/pasting without composition requirements. Mobile, tablet and keyboard coverage remain mandatory; this scope needs validation-state checking, not a visual redesign.

```text
signup idle -> invalid input/alert (editable) -> corrected valid submit/busy -> account
signin idle -> existing12 valid/busy -> workspace
any server error -> alert + same intact input, never invented success
```

## Failure modes, scope and completion

| Failure mode | Handling | Planned test | Critical gap after plan |
|---|---|---|---|
| Creation rule applied to legacy login | Separate types | Real12 account/hash/session | None |
| Password pasted then clipped | Remove maxlength, reject without mutation | Real clipboard/browser roundtrip | None |
| Unicode length differs | Code-point count + server authority | Astral boundary test | None |
| Invalid registration writes rows | Existing schema-before-handler | User/session row counts | None |
| New auth edit certified by old live proof | New source fingerprint/Gate A | Conservative Gate C | None |

Not in scope: change/reset workflow, email delivery/verification, forced resets, MFA, public deployment, PM edits or paid calls. Existing TODOs already cover production identity, so no duplicate TODO is added. Existing architectural diagrams remain accurate; this artifact adds the new policy branch and preserves the login branch.

Completion summary:11 sections evaluated;5 failure classes mapped; no unresolved critical plan gap; one bounded reusable type and existing UI, with real integration/browser tests. Selected complete approach covers all explicit policy requirements without inventing a password-change feature. Independent voice/consensus is attached after it finishes; review completion is not test success.

## Primary and independent in-host consensus

| Dimension | Primary Codex | Independent Codex | Result |
|---|---|---|---|
| Premises | Creation and verification differ | Same; retain normal session rotation/rehash | Confirmed |
| Problem |15-only writes without lockout | Same; no production-certification claim | Confirmed |
| Scope | Shared type and form, no new flow | Same; no duplicate recovery feature | Confirmed |
| Alternatives | Reuse schemas, no service | Same; named type plus OpenAPI | Confirmed |
| Product risk | Exact value/paste/Unicode | Same; test both modes and exact spaces | Confirmed |
| Six-month trajectory | Explicit reusable write contract | Same; preserve historical evidence | Confirmed |

The independent voice is PASSWORD_CEO_VOICE.md. Adopted refinements: preserve normal rotation/eligible parameter upgrades; expose min/max in OpenAPI; reject client lengths without trimming; let the backend remain authoritative for whitespace-only values; cover actual clipboard paste and128-code-point astral input. Zero disagreement or owner-direction challenge. No extra model call was made.
