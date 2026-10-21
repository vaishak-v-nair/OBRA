# ORBA password-policy verification record

Date:2026-10-19. Owner decision:15-character minimum for newly chosen credentials; preserve existing users/hashes/sessions and previously valid12-character login. No paid Gemini request, Stage04, migration, forced reset, commit or discarded uncommitted work is authorized or performed by this change. The preceding report is preserved verbatim in [VERIFICATION_BEFORE_PASSWORD_POLICY.md](VERIFICATION_BEFORE_PASSWORD_POLICY.md); Stage03/03.1 reports and immutable receipts remain historical evidence.

**Password-policy status: implemented and deterministically verified. Gate A PASS, native exit0:157 backend,60 core browser and18 controlled PM browser tests, no skips/retries. Stage03 verdict remains PARTIAL.** Gate A ran2026-10-19T17:43:50Z through17:51:56Z; all14 required commands exited0. [Immutable receipt](evidence/stage031/20261019T174350Z-A-6b1eb81c/receipt.json), [console](evidence/password-policy-gate-a-console.txt), [final audit](evidence/password-policy-final-audit.json). Relevant-source fingerprint across119 files: `19097cc5cb84c430e53bf68dee65299e8a6dbb0a4b5b6a5cb4996ac9849efed9`. No historical live success certifies this changed source, and the previous authorized Gemini503 failure remains visible.

## Implementation

- `apps/api/orba/schemas.py`: reusable `NewPassword` Pydantic type carries15-128 Unicode-code-point limits and the existing whitespace-only guard. `RegisterInput` uses it and publishes those bounds in OpenAPI. `LoginInput` stays1-128. Future change/reset request fields must reuse the new-credential type; verification/eligible rehash must not enforce creation length.
- `apps/web/src/components/auth-form.tsx`: signup help/minimum15, current-password signin retained, exact code-point validation before locking/POST, no native maxlength clipping, retained paste/autofill/native keyboard, associated help/error/invalid-field focus and editable correction. Password text is not trimmed, normalized, truncated, logged or browser-stored. No character-class requirements were added.
- `apps/api/tests/password_support.py`: explicitly authored historical12-character account fixture, guarded to loopback54330/orba_test before connection. It exposes no public endpoint or production flag. Actual authentication still verifies real Argon2id and sessions.
- New backend/browser cases and additive `verification_baseline.json` entries make the new coverage mandatory. All original102/139 backend and51/18 browser identities remain included. The current requirements are157 backend,60 core browser and18 controlled PM browser cases.
- README, AGENTS and ARCHITECTURE document separate creation/login contracts, exact-value passphrases, normal session rotation/eligible parameter upgrades, future schema reuse and existing recovery limitations. Sequential autoplan review/test artifacts are linked from [PASSWORD_POLICY_PLAN.md](PASSWORD_POLICY_PLAN.md).

There is no password-change or reset workflow in this stage. The reusable policy is ready and tested for future credential-write schemas; no endpoint/button is fabricated. No authentication/session/hash/authorization implementation outside the creation schema and existing form was rewritten. Normal login still rotates a presented session and may upgrade eligible Argon2 parameters; the policy rollout itself does not invalidate or rewrite existing records.

## Actual commands and exits

All pnpm commands use `npm exec --yes --package=pnpm@12.14.0 -- pnpm` on this checkout. Targeted native commands run through the existing verifier's deterministic environment, explicitly emptying both model-key aliases/model and selecting guarded PostgreSQL. Backend and browser commands run sequentially.

| Command / attempt | Actual exit and result |
|---|---|
| New14-policy test before implementation |1; actual201 vs required422,1 failed in0.41s. This is a deliberate new-policy red test against the original12 rule, not a historical regression; [log](evidence/password-policy-red.txt), [native exit](evidence/password-policy-red-exit.json) |
| `uv run --directory apps/api ruff format orba/schemas.py tests/password_support.py tests/test_password_policy.py` |0;1 file formatted,2 unchanged |
| Targeted Ruff check |0; all checks passed |
| First `pytest -q tests/test_password_policy.py` |1;17 passed/1 failed in6.17s. Actual login succeeded; the new fixture's domainless cookie conflicted with the real testserver.local rotation cookie during inspection. Fixed fixture domain, preserving rotation assertions. Ephemeral test-cookie repr values were redacted from this new log, with actual CookieConflict/error/counts retained; [log](evidence/password-policy-backend-first.txt), [redaction record](evidence/password-policy-targeted-redaction.json) |
| Corrected `pytest -q tests/test_password_policy.py` |0;18 passed,1 installed-SDK deprecation warning in6.08s; [log](evidence/password-policy-backend-final.txt), [exit](evidence/password-policy-backend-final-exit.json) |
| Standalone `pnpm typecheck` |0; route type generation and strict TypeScript passed |
| Standalone `pnpm lint` |0; ESLint max-warnings0 passed |
| First new Playwright file, all3 viewports |1;9 failed,0 skipped. Exact form alerts were ambiguous with Next's separate route announcer. Scoped assertions to main without changing expected text or removing assertions; [report/log/exit](evidence/password-policy-browser-first/) |
| Corrected new Playwright file, all3 viewports |0;9 passed in36.1s,0 skipped/retries; actual API/auth/PostgreSQL and native clipboard, no auth/provider response stubs; [report/log/exit](evidence/password-policy-browser-final/) |
| Diagnostic report reader |1 once for Windows cp1252 decoding a UTF-8 Playwright JSON; corrected explicit UTF-8 reader0. Application/test behavior was unaffected |
| `git diff --check` |0 after implementation |
| `pwsh -NoProfile -File scripts/verify.ps1` |0; full14-command Gate A,157 backend in61.25s,60 core browser and18 controlled PM browser; complete no-skip/no-retry reports |
| `uv run --directory apps/api python -m scripts.verification summary` |2; current A PASS, historical B FAIL/no applicable current live success, Stage03 PARTIAL; [output](evidence/password-policy-stage-summary.txt) |
| Final preservation/security audit |0 after correcting one Windows separator comparison in the audit allowlist;313 pre-existing artifacts unchanged, only latest-A pointer advances, zero paid requests; [audit](evidence/password-policy-final-audit.json), [initial audit-reader error](evidence/password-policy-audit-first-error.json) |
| Paid/live provider commands in this task |NOT RUN; zero requests, no authorization |

The first-party schema/native-control references used during review are [Pydantic annotated validators](https://docs.pydantic.dev/latest/concepts/validators/), [FastAPI validation errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) and [MDN password input UTF-16 bounds](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/password). These references explain implementation choices; actual test and gate receipts establish behavior.

## Final Gate A command record

| Native command | Exit | Duration |
|---|---|---|
| `docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres` | 0 | 0.851s |
| `uv sync --locked --directory apps/api` | 0 | 0.054s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile` | 0 | 1.199s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm peers check` | 0 | 1.247s |
| `uv run --directory apps/api alembic upgrade head` | 0 | 1.572s |
| `uv run --directory apps/api alembic check` | 0 | 1.623s |
| `uv run --directory apps/api pytest -q --junitxml=E:\BrosKi\OBRA\docs\evidence\stage031\20261019T174350Z-A-6b1eb81c\backend.xml` | 0 | 65.195s |
| `uv run --directory apps/api ruff check .` | 0 | 0.135s |
| `uv run --directory apps/api ruff format --check .` | 0 | 0.091s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm typecheck` | 0 | 4.197s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm lint` | 0 | 9.833s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm build` | 0 | 8.106s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e` | 0 | 225.708s |
| `npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:controlled` | 0 | 160.859s |

## Requirement matrix and test evidence

| Requirement | Evidence / current status |
|---|---|
|14 new characters rejected, no account/session write |PASS: real422 and fresh PostgreSQL counts; browser bypass also receives422 |
|15 new characters accepted without composition rules |PASS: lowercase-only actual201, real Argon2id/session; ASCII and astral browser cases |
| At least64, maximum128 with no silent truncation |PASS:64/128 ASCII and128 astral exact hash/login;129 rejected with full pasted value retained |
| Passphrases/spaces/combining Unicode preserved |PASS: real hash and login roundtrip; stripped/normalized/altered values do not authenticate |
| Existing12-character user/hash/session compatibility |PASS: real fixture hash, old-session me200, actual login200, original current-parameter hash unchanged, independent old session still valid |
| Normal security rotation/parameter upgrades retained |PASS: presented session rotated/revoked, independent session preserved; eligible legacy12 hash upgrades normally and still verifies |
| Future new-password policy reuse |PASS: NewPassword contract14/129/whitespace reject and15 accept; future change/reset workflows NOT IMPLEMENTED |
| OpenAPI creation/login distinction |PASS: actual app schema15/128 versus1/128 |
| Paste/autocomplete/keyboard/correction/accessibility |PASS:9 actual browser cases across desktop/mobile/tablet; field help/error/focus and no POST on invalid custom bounds |
| Existing auth/CSRF/throttling/tenant/project/PM regressions |PASS: full157 backend/60 core browser/18 controlled PM browser; prior coverage retained |
| Current full Gate A / fingerprint |PASS: all14 native exits0, current fingerprint19097cc5...49efed9 |
| New applicable live AI success |NOT RUN; explicitly forbidden in this task |
| Stage03 verdict |PARTIAL |

The18 new backend cases include real PostgreSQL/auth/hash integration and narrowly scoped direct schema/DSN-guard unit cases; no authentication mocks are used. Legacy fixture rows are test setup, not fabricated application identities. The9 new browser cases use actual cookies, CSRF, Next proxy, FastAPI and PostgreSQL; clipboard operations really use Chromium's clipboard API and paste shortcut. Existing18 controlled PM browser cases are explicitly labeled provider doubles and never live model evidence. No skip/xfail/retry counts as pass.

## History, preservation and blockers

The latest authorized live attempt `20261019T170920Z-B-26bec4ac` on prior source c5c705e057e346e2d1f9059110b2927f86d6493dc94a3332065e4aa5dc32a9e1 actually exited1 after one Gemini HTTP503 UNAVAILABLE. Its persisted failed/no-plan audit and visible error remain preserved. No response ID, returned model or usage was available. That failed historical receipt cannot certify current auth source; no further paid request is authorized. The earlier Full504 and genuine earlier live successes remain separately recorded.

[password-policy-intake.json](evidence/password-policy-intake.json) captures the pre-change source map, Git status and314 existing evidence-file hashes. The final audit compared313 pre-existing artifacts, excluding only the deliberately advanced latest-A pointer; every checked artifact and latest-B remained byte-identical. Only the six intended policy source/test files changed:3 modified,3 added, none removed;113 pre-existing source files are byte-identical. Git checkpoint e3fccd6 stayed unchanged; no commit or staged-state mutation occurred, and root dotenv remains ignored. A scoped literal runtime-key scan found no match across490 Git-visible files and177 current client assets; it recorded no credential value/hash and is not a universal secret audit. The first audit reader incorrectly compared Windows backslashes with its forward-slash allowlist and exited1 for that allowed pointer; normalized exact comparison then audited all hashes successfully without altering any receipt.

The application remains local-development scope, without production-security certification, MFA, email verification or recovery/change workflows.15-character validation alone does not certify a complete identity-security standard. Chromium emulation and autocomplete attributes do not establish native iOS/Safari/all-browser/password-manager certification. Existing auth-specific transport-copy and post-auth session-read feedback limitations are bounded in TODOS.md; protected content remains gated.

## Reproduction

From E:\BrosKi\OBRA with Docker running, stop this checkout's development Next server to avoid its shared development lock. Do not run backend/browser/fixture commands concurrently.

```powershell
pwsh -NoProfile -File scripts/verify.ps1
uv run --directory apps/api python -m scripts.verification summary
```

The first command is the full deterministic gate, with model credentials/selection explicitly empty in child processes. The summary must exit2/PARTIAL until both required current-source gates genuinely pass. Do not run verify-live.ps1 or a live diagnostic under this task. Historical intentionally wrong-success experiments remain separate from the green suite.

## Verdict

Stage03: PARTIAL. The password-policy task is complete with actual passing full deterministic evidence. Live verification is not authorized or performed on the new source; the preserved prior live503 failure is not reclassified or retried.
