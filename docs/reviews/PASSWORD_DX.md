# Password policy DX review

Product type: local developer workspace with an HTTP API and browser UI, not a public auth SDK or hosted service. Persona: the owner/contributor maintaining this Windows checkout, who expects exact commands, safe data boundaries and verifiable backward compatibility. Mode: DX POLISH. This is plan/source analysis, not executed installation or timing evidence. No Gemini, hosted playground, new package or public support claim is needed.

## Developer journey and empathy

| Stage | Actual surface | Friction / disposition |
|---|---|---|
| 1. Discover | README auth/local-scope section | Replace12 creation guidance while preserving legacy-login explanation |
| 2. Install | pnpm wrapper and uv locked dependencies | No dependency changes; reuse current commands |
| 3. Start | Compose test-postgres, API and web commands | Keep loopback/testDSN guard; no development reset |
| 4. First account | Signup and /api/v1/auth/register |15..128 shown before submit and in schema |
| 5. Real use | Existing signin/session/workspace flow | Old12-password account still authenticates |
| 6. Debug |422 details, form alert, safe logs | Specific password field/limit without echoing value |
| 7. Upgrade | Source-only policy rollout | No migration, hash rewrite, session invalidation or forced reset |
| 8. Verify | scripts/verify.ps1 | All identities retained, new tests mandatory; no paid call |
| 9. Extend | Future change/reset schema | Import NewPassword for new value, LoginInput for verification only |

First-person source walkthrough (roleplay, not a claimed execution): I open README and find a local application, not a hosted identity service. I already have users in the database and want a clear answer about whether this update changes their passwords. I read the authentication paragraph before touching a terminal. It should say15-128 for newly chosen credentials,1-128 for existing login, and no forced reset. I use the existing uv and pinned pnpm commands because installing a second auth library would make this harder to trust. In the signup form I want to paste a passphrase and know the entire value was used. If it is too long, I want a short limit error and the value still present so I can correct it. When I sign in with my existing12-character password, I expect the same authenticated workspace and secure session behavior as before. I look for the14/15 API test, the legacy fixture explanation and the actual Gate A receipt. I do not want a historical successful Gemini flow presented as proof for changed source, and I do not want this password check to spend another model request.

Reference patterns, not invented competitive timings: Pydantic's reusable annotated validation keeps a contract explicit; FastAPI's structured validation errors identify the field; MDN documents password maxlength/minlength as UTF-16 units. These are first-party technical references, not measured ORBA/competitor onboarding results. Existing warm-service account-to-workspace time is not newly measured; target is under2minutes with services already running. Cold dependency/Docker startup and the full regression gate are separate and are not claimed to finish in that time. The feedback moment is real registration plus a still-working legacy login, delivered through the existing UI and tests rather than a new demo command.

## 1. Getting started —8/10

No new installation, credential or environment setting is required. README must make the new/old distinction visible in the existing auth section and link exact deterministic reproduction commands. The local Docker/Windows prerequisites remain honest; a hosted zero-install experience is outside the owner's scope.

## 2. API and schema design —9/10

RegisterInput advertises minLength15/maxLength128 and runtime validation; LoginInput keeps minLength1/maxLength128. NewPassword is a narrow reusable Pydantic type for future credential-write schemas, not a parallel auth system. Test both runtime and OpenAPI contracts so future callers do not infer the old minimum from a hidden validator.

## 3. Errors and debugging —9/10

Three paths were traced: new14/129 value ->422 field details; wrong existing credential ->generic401; local over-limit paste ->associated length alert with no POST. The first and third name a corrective bound, while the second must not reveal account/hash state. Existing transport copy/session-read limitations are documented separately; no credential values or validation bodies belong in logs.

## 4. Documentation and learning —9/10

Update README, ARCHITECTURE, AGENTS and the current verification record together. Explain code-point counting, significant surrounding spaces, no normalization/truncation and no character-class requirements. Preserve historical reports and explicitly state that change/reset workflows do not yet exist; future implementers reuse the creation type.

## 5. Upgrade and migration —9/10

This is a source-policy change without Alembic/data updates. Test an explicitly seeded pre-policy12-character account/hash/session through real authentication and retain normal rotation and eligible parameter rehash behavior. No migration guide may suggest deleting users, resetting hashes, revoking sessions or applying15 to current-password verification.

## 6. Tooling and environment —8/10

Reuse the fixed14-command Gate A and guarded real PostgreSQL fixtures. A small test-only legacy seeder may create an old account for browser testing only after validating the exact test DSN; it must expose no public seed endpoint or production bypass. All backend/browser commands remain sequential, with complete no-skip structured reports and new identities added to the baseline.

## 7. Ecosystem —4/10, intentionally local

No Git remote/public support channel or hosted service is established here. That limits external onboarding, but it does not block the owner's local password-policy change. Existing TODOs already cover production identity and public support; adding a community, SDK or pricing feature would not improve this credential boundary.

## 8. Measurement and feedback —8/10

Actual test counts, exits, source fingerprints and artifact hashes will be recorded after execution. Do not log password length/value events or introduce third-party analytics to measure a local rule. Gate C must remain PARTIAL when the new source has no applicable successful live proof, and the prior503 remains historical failure evidence.

## Implementation checklist and scope

- [ ] Expose15/128 creation and1/128 login schema bounds.
- [ ] Show actionable, field-associated client errors without modifying input.
- [ ] Verify legacy hash/session behavior through actual HTTP/PostgreSQL.
- [ ] Add mandatory browser identities and guarded fixture setup.
- [ ] Update current docs and preserve prior evidence byte-for-byte.
- [ ] Run full Gate A; report a new fingerprint and PARTIAL stage summary.

No additional TODO is proposed: recovery/MFA/hosted onboarding already has a deferred owner-controlled scope. The skill-specific appendix does not apply because ORBA is an application, not a distributed skill. Planned DX coverage is8/10 locally, with ecosystem limits stated rather than hidden. Independent judgments/consensus will be appended before engineering begins.

## Independent in-host consensus

| Dimension | Primary | Independent | Result |
|---|---|---|---|
| Getting started | Existing commands, honest warm target | No new setup/forced reset | Plan agrees; timing unmeasured |
| API naming | NewPassword vs LoginInput | Explicit generated schema limits | Agrees |
| Errors | Safe field details/unchanged input | Same, pre-existing transport-copy limit | Agrees |
| Documentation |15 new /1 login /future reuse | Same, recovery remains unavailable | Agrees |
| Upgrade | No bulk mutation; retain ordinary rotation/rehash | Same; distinguish presented/independent sessions | Agrees |
| Environment | Fixed Gate A, guarded fixtures, add identities | Same; active stage031_backend must be extended | Agrees |

The independent artifact is PASSWORD_DX_VOICE.md. Both are Codex-family source reviews, not independent provider/model or runtime proof. All refinements are incorporated into the engineering handoff. No new TODO outside the already tracked production-identity scope.
