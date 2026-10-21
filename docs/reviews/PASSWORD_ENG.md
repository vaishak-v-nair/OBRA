# Password policy engineering review

Final scope after CEO/design/DX: a creation-only Pydantic contract, the existing shared form, focused real tests and additive gate identities. No schema migration, password-change/reset endpoint, provider change, dependency or deployment is needed. Source reads covered schemas.py, auth.py, security.py, main.py, db.py, models.py, AuthForm/API helper, existing fixtures, browser helpers/configs and the active baseline. This is review evidence only.

## Scope challenge and architecture

The existing `LoginInput.password = Field(min_length=1, max_length=128)` is the correct verification boundary. `RegisterInput` currently checks `len(value) < 12 or value.isspace()` privately; replace that with an explicitly constrained reusable NewPassword type, retaining the whitespace-only guard. The shared form currently has `maxLength={128}` in both modes, so replacing clipping with intact-value validation is a direct importer change, not a new component system. Runtime/test changes are limited to two product files, one test-only fixture module, two test files and the active identity registry; additional files are requested docs/reviews/evidence, not extra services.

```text
native AuthForm
  |- signup -> code-point15..128 -> RegisterInput(NewPassword)
  |                                  -> existing rate_limit -> Argon2id -> User/session
  |- signin -> code-point1..128 -> LoginInput
  |                                  -> existing rate_limit -> stored hash -> rotation
  |- invalid -> associated alert/focus, intact value, no lock/POST
  `- request failure -> existing safe alert/retained fields

backend tests -> guarded migrated orba_test <- real API <- Next proxy <- Playwright
test-only legacy seeder -> guard_test_url -> same User/Argon2id -> no public endpoint
Gate A -> same fixed checks + complete baseline reports -> new source receipt
Gate C -> new A + old failed/no-current B -> PARTIAL
```

No new auth authority or client-supplied identity is introduced. Every existing membership/session/CSRF route remains unchanged. Shared production NewPassword is importable by future credential-write schemas, while fixture construction remains filesystem/test-only and refuses development DSNs before connecting. Distribution is unchanged because no new public artifact/package is created.

## Code quality and exact-value findings

E1 [P1, confidence9/10]: the existing native `maxLength={128}` can clip pasted values and counts UTF-16, while Python uses code points. Remove it in both modes, count `Array.from(password).length` before the busy lock, and send the original string. Keep native required/minimum as convenience and server validation as authority; no trim, normalization or case/number/symbol policy.

E2 [P1, confidence9/10]: creation-only policy must not leak into `verify_password` or `passwords.check_needs_rehash` in auth.py. Leave both functions and all session code unchanged. The policy installation makes no data writes; normal successful login may still rotate its presented session and upgrade an eligible Argon2 parameter hash, as it already does.

E3 [P2, confidence9/10]: existing RegisterInput's private validator hides the actual creation minimum from its inherited JSON schema. Put15/128 into the annotated type and test OpenAPI, including LoginInput's unchanged1/128 bounds. Reuse Pydantic's installed Field/AfterValidator rather than add a policy service, shared package or new dependency.

E4 [P2, confidence9/10]: client rejection must not occur after `lock.current=true`. Validate first, associate the helper/error with Password, focus it on custom rejection, and clear obsolete field error when input changes. Server field details can identify a password validation error; generic credential/network errors must not become password-format errors. Never put the value in logs/error text.

## Test review and coverage map

Detected frameworks are real pytest/FastAPI/SQLAlchemy PostgreSQL integration plus Playwright, with mandatory no-skip report validation. Existing14-character registration is allowed under the old12 rule; add and actually run the new14-rejection test before changing policy to capture a meaningful red result, then rerun it after the fix. This is a new-policy red test, not a historical production failure.

| Codepath / user flow | Required coverage | Existing or new |
|---|---|---|
| Missing/empty/wrong type/14/129 new value |422, field details and no user/session writes | New real API/PG cases |
|15 lowercase-only credential |201, salted Argon2id/session and real me | New real API/PG case |
|64/128 ASCII,128 astral, spaces and combining text | Exact full-value verify; altered suffix/normalized/trimmed value rejected | New real API/PG cases |
| Whitespace-only creation |422 without mutating existing account/session | New case preserving old behavior |
| Legacy12 current-parameter hash/session | Old session me200; real login200; original independent session/hash unchanged; normal presented rotation | New real API/PG and real browser |
| Eligible legacy12 parameter rehash | Login succeeds, new hash verifies same12; no creation policy in rehash | New real API/PG case |
| Future creation-type reuse | TypeAdapter rejects14/129, accepts15; no invented route | New unit contract |
| OpenAPI create/login split |15/128 versus1/128 | New actual app OpenAPI test |
| Invalid local length / correction | No POST, associated error/focus, intact value, unlocked form | New real browser on3 viewports |
| Native paste >128 / valid128 astral | Actual clipboard, no clipping, rejected oversize, exact accepted login | New real browser on3 viewports |
| Autofill and keyboard | Retain current/new-password, no pattern, Tab/Enter | New browser assertions |
| Fixture unsafe DSN | Guard rejects before connection/mutation | New fixture-boundary unit |
| Existing auth/tenant/projects/PM | All baseline identities unchanged | Full existing Gate A |
| Wrong/stale/controlled live certification | Conservative summary | Existing verifier contracts and actual Gate C |

```text
schema bounds ----------> pure contract + actual OpenAPI
registration -----------> HTTP + fresh SQL + Argon2 verification
legacy verification ----> seeded historical fixture + actual login/session/rehash
form invalid/corrected -> actual browser/API, no mocked auth
paste/long/legacy ------> actual clipboard and browser -> real PostgreSQL
errors/tenant/regression -> original complete A, plus new mandatory identities
```

No background job, external integration or prompt/model behavior changes; no paid eval is authorized or necessary for this policy. The legacy fixture is explicitly authored historical setup, not mocked verification: authentication still runs the real hash/session/CSRF paths. Clipboard emulation proves Chromium behavior only; password-manager attribute checks do not certify an actual manager. New backend cases are appended to stage031_backend; new browser identities are appended to core_browser for every viewport, with no old identity renamed/removed.

## Performance and operations

Accepted credential size remains bounded at128 code points, and Argon2 parameters/limiter cost stay unchanged. Removing the browser-only clip cannot increase the backend accepted-input bound; over-limit inputs fail before hashing. There are no new joins, indexes, connection pools, caches or background jobs. The guard rejects unsafe fixture DSNs before an engine is created; no development database is reset.

| Failure | Handling | Verification | Critical plan gap |
|---|---|---|---|
| Accidental legacy lockout | Separate schemas |12 hash/session/login tests | None after tests added |
| Paste clipped / UTF-16 mismatch | Original value + code-point validation | Actual clipboard,128/129 astral | None after tests added |
| Client invalid remains busy | Validate before lock | Error/correction/no POST | None after tests added |
| New invalid account persisted | Pydantic before handler | Real row counts | None after tests added |
| Fixture touches dev | Exact DSN guard before connection | Unsafe-DSN test | None after tests added |
| Old live success reused | Source-bound A/C, B not executed | Current summary stays PARTIAL | None |

What exists: hashing, sessions, CSRF, throttling, safe validation envelopes, form components, fixtures and gates. Not in scope: reset/change features, MFA, global tooling repair, deployment, paid model requests or commits. Existing TODOs cover those deferred product features; no new durable debt item is introduced. Current diagrams remain accurate with the explicit creation/login branch added here.

Completion:4 review sections completed,6 failure modes planned with no unresolved critical coverage gap,6 focused runtime/test files and requested docs, zero new services/dependencies/migrations. Main test plan is written to docs/PASSWORD_POLICY_TEST_PLAN.md and mirrored to the external gstack project before implementation. Independent review is attached before final clearance; tests and Gate A must still actually execute.
