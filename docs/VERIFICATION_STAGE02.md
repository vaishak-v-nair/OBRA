# ORBA Stage 02 verification record

Date: 2026-10-18. Scope: authentication, workspaces, roles, project isolation and manual invitations only. Stage 03 has not begun. Stage 01's historical record is preserved in VERIFICATION_STAGE01.md.

## A. Implementation summary

Implemented real FastAPI registration/login/logout/me/CSRF, Argon2id password hashes, hashed opaque PostgreSQL sessions, explicit expiry/revocation/rotation, HttpOnly cookies, exact-Origin and CSRF enforcement, and PostgreSQL login-attempt limits. Next.js proxies same-origin browser API requests without becoming an authentication authority.

Implemented workspace creation/switching, Owner/Admin/Member/Viewer permissions, member listing/role management/removal, manual email-bound invitation creation/listing/revocation/acceptance, and authorized project create/list/read/edit. Authentication screens, account menu, workspace/settings/invitation pages, loading/error/permission handling and existing themes/Chat creation are connected to the real backend.

Migration 0febbe526f54 preserves old project fields and moves ownership into a restricted legacy workspace with no members. Registration never claims legacy data. A terminal-only dry-run/apply command transfers explicit selected UUIDs to an existing target Owner. The migration refuses a listening local API on its configured port before upgrading development ownership. No reset/drop of the development database was used.

## B. Changed files

| Files | Responsibility |
|---|---|
| apps/api/orba/auth.py, security.py | Argon2id, opaque sessions, CSRF/Origin, rate limits and shared authorization |
| apps/api/orba/workspaces.py | Real workspace, membership, invitation and role transactions |
| apps/api/orba/main.py | Authenticated project APIs, PATCH editing, full schema readiness and safe errors |
| apps/api/orba/models.py, schemas.py, config.py | Auth/workspace entities, validated API shapes and environment configuration |
| apps/api/orba/migration_safety.py | Actual local listener guard before ownership migration |
| apps/api/migrations/versions/0febbe526f54_auth_workspaces.py | Tables, constraints/indexes, non-destructive legacy backfill, forward-only safety |
| apps/api/migrations/env.py, script.py.mako | Migration tooling and explicit connection support for isolated migration tests |
| apps/api/scripts/claim_legacy.py | Explicit operator-only legacy claim, dry-run default |
| apps/api/scripts/prepare_tests.py, tests/conftest.py | Guarded real test schema/data setup and real account fixtures |
| apps/api/tests/test_projects.py | Retained Stage 01 scenarios adapted to authorized workspaces |
| apps/api/tests/test_auth_workspaces.py, test_legacy.py | Auth, isolation, roles, races, migrations and actual CLI tests |
| apps/api/tests/experiments/unauthorized_success_experiment.py | Explicit-only deliberately wrong authorization expectation |
| apps/web/src/app/api/v1/[...path]/route.ts | Same-origin proxy, cookie/header forwarding, no-store responses |
| apps/web/src/components/session.tsx, auth-form.tsx, shell.tsx | Session gate, signup/signin, actual account and workspace controls |
| apps/web/src/components/project-form.tsx, project-editor.tsx | Preserve Chat flow; workspace-scoped writes and editing |
| apps/web/src/app/workspaces, signin, signup, invitations/accept, settings | Real team and account flows |
| apps/web/src/lib/api.ts, use-hash.ts | Typed cookie/CSRF requests and safe invitation fragment flow |
| apps/web/tests, playwright.config.ts | Retained regression plus real multi-user browser flows |
| scripts/verify.ps1 | Existing workflow extended with frozen install, peer/drift checks and native output capture |
| README.md, AGENTS.md, docs/ARCHITECTURE.md, ROADMAP.md | Reproduction, scope, security contract and operational limits |
| docs/STAGE02_PLAN.md, STAGE02_TEST_PLAN.md, STAGE02_INDEPENDENT_REVIEW.md | Sequential autoplan and actual independent review evidence |
| apps/api/uv.lock, pyproject.toml, .env.example files | Maintained hashing/email libraries and configuration |

## C. Repository baseline and actual commands

Environment: Windows/PowerShell 7.6.7, Node 26.7.0, pnpm 12.14.0, uv 0.12.13, Python 3.14.4, Docker Engine 29.8.1, PostgreSQL 18.6. Existing Next/React/TypeScript/ESLint lock versions retained. Added argon2-cffi 25.1.0 and email-validator 2.3.0 through uv.lock.

Git status showed every source file untracked; main had no commits and no origin. It was not possible to distinguish later user changes with Git. Read the source and required documents; preserved a source snapshot at `C:/Users/vaish/AppData/Local/Temp/orba-stage01-before-stage02.zip` before editing. No commit, push or deployment occurred. The default development database contained zero projects before migration and still zero afterward; preservation is additionally established with seeded old-schema records in real PostgreSQL, rather than claiming nonexistent development records were observed.

The full pre-change scripts/verify.ps1 exited **0**: 15 backend tests passed in 12.43s and 30 browser tests passed in 40.3s, with original lint/type/build checks passing. The old local API/frontend processes were then stopped before migration. Historical baseline ledger is in docs/evidence/stage01-baseline.txt.

`pnpm` commands were executed through `npm exec --yes --package=pnpm@12.14.0 -- pnpm` because pnpm is not globally installed. Final exact script invocation: `pwsh -File scripts/verify.ps1`, exit **0**. Its constituent commands:

| Actual command | Exit | Observed result |
|---|---:|---|
| docker compose -f infra/compose.yaml --profile test up -d --wait | 0 | Both real PostgreSQL containers healthy |
| uv sync --locked --directory apps/api | 0 | Locked environment checked |
| pnpm install --frozen-lockfile | 0 | Lockfile up to date |
| pnpm peers check | 0 | No peer dependency issues |
| uv run --directory apps/api alembic upgrade head | 0 | Development revision at 0febbe526f54 |
| uv run --directory apps/api alembic check | 0 | No new upgrade operations detected |
| uv run --directory apps/api pytest -q | 0 | **44 passed in 27.94s** |
| uv run --directory apps/api ruff check . | 0 | All checks passed |
| uv run --directory apps/api ruff format --check . | 0 | 21 files already formatted |
| pnpm typecheck | 0 | next typegen + strict tsc --noEmit |
| pnpm lint | 0 | ESLint --max-warnings 0 |
| pnpm build | 0 | Next production build generated all expected routes |
| pnpm test:e2e | 0 | **42 passed (2.0m)** |

Other executed commands:

| Command | Exit / result |
|---|---|
| git log before changes | 128, main has no commits |
| gstack startup preamble probe | Helper absent; degraded mode, no helper telemetry/consensus invented |
| uv add --directory apps/api 'argon2-cffi>=25,<26' 'email-validator>=2,<3' | 0 |
| Alembic revision --autogenerate | 0; rendered unnamed-downgrade warning, corrected names and replaced downgrade with explicit forward-only refusal before execution |
| Initial Stage 02 pytest | 1; 14 passed/1 failed because anonymous protection now correctly returns 401 before DB access |
| Updated Stage 02 pytest | 0; 15 then 36, 38, 40, 43 and final 44 actual passing cases as coverage grew |
| Initial frontend typecheck | 2 wrapper; old list call still passed offset where workspace ID was required; fixed together with API client |
| Intermediate lint/Ruff checks | Nonzero for import order, explicit subprocess check flags and React effect/ref patterns; fixed without disabling rules |
| First Stage 02 browser suite | 1; 32 passed/4 failed: async session gate/skip focus assumptions and early responsive-nav probe |
| Focused keyboard suite | 1; 8 passed/1 failed: closed-details hidden button was included in focusables |
| Focused mobile account regression after fix | 0; 1 passed in 12.4s |
| Intermediate full scripts/verify.ps1 | 0; 40/39 then 43/42 backend/browser passing results before final additions |
| codex --version / login status | 0; CLI 0.163.0, authenticated |
| Read-only independent codex exec | 0; four material findings with actual source dispositions |
| uv run --directory apps/api pytest -q tests/experiments/unauthorized_success_experiment.py | **1, intentional**; `assert 404 == 200`, separate from passing suite |
| Uvicorn --host 127.0.0.1 --port 8000 --no-proxy-headers | Running; startup complete, live/ready HTTP 200 |
| pnpm --filter @orba/web start | Running; Next ready in 201ms, signup HTTP 200 |
| Production web/API smoke probes | 0; anonymous API 401, same-origin CSRF 200 and HttpOnly/Strict preauth cookie |
| git diff --check | 0; bounded evidence because files remain untracked |

Final transcript: docs/evidence/verification-transcript.txt. It now includes native stdout and all 13 exit statuses; some host-native lines appear twice because of PowerShell transcript behavior. Test counts above come from actual executed summaries, not duplicate transcript-line counting. Normal E2E retries are 0; no skipped or xfail tests exist in the passing suite.

### Continuation runtime check, 2026-10-18 23:22 IST

On resuming the handoff, ports 8000/3000 refused connections and `docker compose -f infra/compose.yaml ps` exited **1**: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` Docker Desktop was stopped. Started the installed per-user Docker Desktop with `Start-Process -FilePath 'C:\Users\vaish\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe' -WindowStyle Hidden`; its status changed from starting to running. No database reset or source change was needed.

`docker compose -f infra/compose.yaml --profile test up -d --wait`, `docker compose -f infra/compose.yaml ps`, `uv run --directory apps/api alembic current` and `uv run --directory apps/api alembic check` each exited **0**. Both PostgreSQL containers became healthy, development revision remained `0febbe526f54 (head)`, and no new upgrade operations were detected. Restarted the documented Uvicorn command and the existing production web build; both reported ready (Next: 6.0s).

Fresh HTTP assertions exited **0**: live/ready/signup/CSRF **200**, anonymous same-origin `/auth/me` **401**, signup form present, and pre-auth cookie HttpOnly/SameSite=Strict. Sanitized results are in `docs/evidence/stage02-resume-smoke.json`; no token or cookie value was recorded. The 44/42 counts above remain the actual complete verification run, archived in `docs/evidence/stage02-final-verification.txt`; tests were not claimed to have rerun during this runtime restart.

## D. Verification matrix

| Requirement | Result | Actual evidence |
|---|---|---|
| Valid registration persists user | PASS | Real API + independent SQL queries; browser signup |
| Normalized duplicate email rejected | PASS | Mixed-case/whitespace duplicate returns 409; DB still one user |
| Salted Argon2id password storage | PASS | Library verifies hashes; equal passwords produce distinct hashes |
| Valid login and session persistence | PASS | API rotation/me assertions and browser sign-in after logout |
| Invalid login rejected | PASS | Actual 401 safe error |
| Unauthenticated protected request rejected | PASS | Real 401, including production smoke |
| Logout revokes session | PASS | Stored revoked_at and replayed-cookie 401; browser content blocked |
| Expired/revoked sessions rejected | PASS | Real DB lifecycle states produce 401 |
| Session rotation | PASS | New cookie differs; presented prior session revoked in DB |
| HttpOnly/SameSite/Secure configuration | PASS | HTTP cookie flags; real HTTPS TestClient/Secure cookie; invalid HTTPS/false startup rejected |
| CSRF/Origin protections | PASS | Missing/wrong/stale/non-ASCII token and wrong Origin produce 403 |
| Brute-force restriction | PASS | Persisted sequential limit; synchronized independent-instance race yields 401/429 |
| Workspace creation and Owner membership | PASS | API/DB assertions and real UI creation |
| Workspace switching | PASS | Old component state cleared; real selected-space project lists and empty state |
| Owner invitation | PASS | Real authorized 201, one-time link, stored token hash |
| Intended user joins shared workspace | PASS | Email-bound authenticated acceptance and unique persisted membership; two real browser contexts |
| Expired/revoked/used/wrong-email invitation rejected | PASS | Real DB/token/API cases; no unauthorized member row |
| Atomic invitation acceptance | PASS | Barrier-synchronized requests yield 200/400 and one DB membership |
| Viewer cannot create/edit | PASS | API 403 and unchanged storage; browser disabled controls + actual denied request |
| Member can create/edit | PASS | API/DB writes; UI promotion then real Member project contribution |
| Member cannot invite/manage roles | PASS | Server-side 403 assertions |
| Admin cannot promote self/affect Owners | PASS | Actual PATCH/DELETE denial |
| Final Owner protected | PASS | 409 direct paths; synchronized owner demotions yield 200/409, one Owner remains |
| Revocation versus project write | PASS | Real synchronized requests; either valid pre-revocation commit or denied write; all subsequent writes denied |
| Private project exact UUID isolation | PASS | Other user read/edit 404; original DB row and ownership unchanged |
| Private member list isolation | PASS | Other user's request 404 |
| Forged workspace/creator IDs denied | PASS | Unauthorized workspace 404; extra creator field 422 |
| Original project create/list/retrieve/persist | PASS | All 15 original backend cases retained/adapted; all 30 original browser scenarios retained |
| Legacy IDs/data/timestamps survive migration | PASS | Fresh Stage 01 schema/seed -> actual Alembic head -> exact field comparison; repeated head remains one row |
| First registration cannot claim legacy data | PASS | Project exists before first registration; no workspace access/creator assignment afterward |
| Explicit operator claiming | PASS | Actual CLI dry run/apply/replay rejection; mixed batch rejects atomically; original fields/times unchanged |
| Safe local upgrade | PASS | Actual listener causes migration guard refusal; closed port accepted |
| Negative authorization detection | PASS | 404 with no secret content + independent DB existence check + UI absence |
| Incorrect-success experiment really fails | PASS | Separate actual pytest exit1 at the deliberately incorrect assertion |
| Themes/responsive/keyboard | PASS | Desktop/mobile/tablet Chromium regressions and account-menu/skip/Escape checks |
| Build, lint, typecheck, locks, migration/drift | PASS | Final complete verification script exit0 |
| Documentation/reproduction | PASS | Updated README, AGENTS, architecture/roadmap, test plan and this execution record |
| Public deployment/production security certification | NOT RUN | Outside current local scope; not claimed |
| Firefox/WebKit/physical devices/load/penetration testing | NOT RUN | Not part of the executed Chromium local acceptance |

## E. Test evidence and scope

Final actual backend summary:

```text
............................................                             [100%]
44 passed in 27.94s
```

Final actual browser summary:

```text
Running 42 tests using 1 worker
42 passed (2.0m)
```

Backend uses actual FastAPI handlers, SQLAlchemy, psycopg, Argon2id, Alembic and PostgreSQL. TestClient is the real application transport; no authentication/authorization mocks or SQLite substitutions. Password/session/invitation state is queried independently. Expiry/revocation tests put real persisted rows into those lifecycle states. Concurrency tests use synchronized threads, separate sessions/clients (and independent app instances for the limiter), real locks and time-bounded results.

Browser tests use actual Next.js, a real separate Uvicorn process and isolated PostgreSQL. Four team/security scenarios plus ten retained Stage 01 scenarios run in each of three Chromium viewports (42). Team flow includes UI registration, workspace/project creation, reload, manual invitation, recipient registration/acceptance, shared visibility, actual Viewer denial, UI role promotion, Member contribution, logout, protected-content rejection and actual sign-in. Separate contexts verify exact UUID isolation and switching. Offline mode is a genuine browser network failure, not an intercepted fake API response. Offline logout asserts local content clearing and explicitly observes that an unreachable server session remains valid; it never fabricates revocation.

Zero skipped/xfail tests and zero configured retries. The intentional wrong-policy file does not match normal pytest discovery and is invoked explicitly only. Auth network traces/failure screenshots are disabled to avoid storing cookies/passwords/invitation secrets; safe home screenshots are still explicitly generated, and all behavioral assertions remain intact.

Artifacts: docs/evidence/verification-transcript.txt, stage02-final-verification.txt, stage02-authorization.json, stage02-expected-failure.txt, stage02-api-smoke.json, stage02-web-smoke.json, stage02-resume-smoke.json; apps/web/playwright-report/index.html and test-results/.last-run.json (passed, no failed tests); six safe home screenshots. Generated browser artifacts are ignored. Desktop light home was visually inspected after Stage 02 integration. Browser device emulation does not establish native-device compatibility or full WCAG conformance.

## F. Negative-path evidence

The actual independent-user probe recorded:

```json
{
  "project_id": "e0dfc13c-2861-40c5-a621-5700a5e27872",
  "http_status": 404,
  "response": {"error": {"code": "not_found", "message": "Project not found."}},
  "database_project_still_exists": true,
  "database_workspace_unchanged": true
}
```

The test verifies original private title/description/ownership in a separate database session at the denial observation. Subsequent test cleanup intentionally clears only isolated test data. Browser tests separately show no private project content to the unrelated signed-in user. The correct test passes because the operation was denied; unauthorized access did not succeed.

The isolated wrong-policy experiment used another real user and exact private UUID, verified that the DB still contained the project, then asserted unauthorized HTTP success. Actual output:

```text
E       assert 404 == 200
E        + where 404 = <Response [404 Not Found]>.status_code
1 failed in 0.62s
EXPECTED_FAILURE_EXPERIMENT_EXIT=1
```

This is an explicitly expected-failure experiment. It is neither a production test failure nor an xfail/green stub. Its original output remains in stage02-expected-failure.txt. No application change was made to satisfy the incorrect expectation.

Other genuine negative paths: CSRF/origin/role denial, login throttling, invitation expiry/reuse/revocation/email mismatch, final-owner protection, unavailable database readiness, and actual offline browser requests. Their expected denial/handling behavior is asserted in the normal passing suite.

## G. Security limitations and review dispositions

This is local development authentication, not certified production security. No verified email ownership, recovery, SSO/OAuth, MFA/passkeys, production TLS/reverse-proxy deployment, durable audit store, full distributed deployment qualification, penetration/load test or background session-cleanup worker. Duplicate-email registration can reveal account existence. The basic limiter can affect legitimate users behind a shared local proxy; it is documented and server-enforced, not advertised as complete abuse protection.

Cookie Secure defaults false only for local HTTP; HTTPS configuration requires true. Services/DB bind loopback and public deployment was not attempted. Migration guard covers the configured local API port; operators must inventory/stop custom or remote processes independently. Legacy migration is forward-only. Terminal/database access is operator authority; the claim command is not available to web users.

No real-time permission push: every subsequent protected request enforces current membership. A network failure may prevent server logout; the UI clears protected state and warns that revocation is unconfirmed. Project writes have no server idempotency contract; drafts persist and writes are not automatically retried.

Autoplan ran sequential CEO → Design → DX → Eng review, with delegated and actual same-family read-only CLI review. Helper/designer tooling was absent; no Claude/cross-model consensus was invented. CLI exit0 reported four source findings: failed logout retained local data, unsafe old-API upgrade path, stale proxy launch instructions, and concurrency/mixed-claim test gaps. Resolved with local safe-clear/warning, migration listener guard, --no-proxy-headers startup, synchronized races and actual mixed-batch CLI verification. Delegated review also reproduced the non-ASCII CSRF exception and found mobile native focus controls missing; both were fixed and exercised. Review artifacts preserve findings as historical observations, not current unresolved failures.

Earlier real failures were preserved above and fixed: anonymous 401 versus old availability assumption; workspace API client mismatch; lint/effect/ref rules; async gated skip/navigation focus; hidden closed-details focus target. No assertions were removed or rules disabled. Original backend availability test now supplies an opaque invalid credential to force the genuinely unavailable database session lookup; it does not fabricate an authenticated identity. The plain anonymous path is separately required to return 401.

Source remains uncommitted/untracked as at intake. No remote CI, commit, push or deployment is claimed. Durable operational findings are documented in this repository: Uvicorn proxy-header trust, byte-safe CSRF comparison, native focus visibility, migration shutdown requirements and credential-safe test artifacts. No global memory was modified.

## H. Exact reproduction

Fresh setup and configuration are in README.md. From repository root:

```powershell
npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile
uv sync --locked --directory apps/api
npm exec --yes --package=pnpm@12.14.0 -- pnpm --filter @orba/web exec playwright install chromium
pwsh -File scripts/verify.ps1
```

Docker Desktop must be running. Do not run backend/E2E concurrently; both use the isolated orba_test database. Free 8001/3001 before E2E; the runner refuses service reuse. Development 8000/3000 may run once already at Stage 02; fresh ownership migration requires the old API stopped. Use exact localhost WEB_ORIGIN and server-only API_URL examples.

Start application in two terminals:

```powershell
uv run --directory apps/api uvicorn orba.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
```

```powershell
npm exec --yes --package=pnpm@12.14.0 -- pnpm dev
```

Open http://localhost:3000. Real accounts must register; no seeded development identity/bypass exists. For production-built local serving use `pnpm build` then `pnpm --filter @orba/web start`. The current production-built server is running locally. Follow README's explicit dry-run/--apply procedure to claim legacy projects; never drop/reset development data.

## I. Stage verdict

**VERIFIED**

All mandatory Stage 02 checks executed successfully within the recorded local PostgreSQL/Chromium scope. No Stage 03 functionality was implemented.
