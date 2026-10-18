# ORBA Stage 01 verification record

Date: 2026-10-18. Environment: Windows, PowerShell 7.6.7, Node 26.7.0, pnpm 12.14.0, uv 0.12.13, uv-managed CPython 3.14.4, Docker Engine 29.8.1. Repository was empty and not a Git repository at intake; initialized local main branch, no remote configured, no commit/push/public deployment performed.

## A. Implementation summary

Built a real Next.js/FastAPI/PostgreSQL project foundation. Chat creates persisted projects and redirects to details; Projects supports explicit creation, paginated listing and retrieval. Detail shows the original description, timestamps and actual `created` status. Theme preference persists; responsive navigation includes keyboard focus and Escape handling. Five future sections explicitly say “Coming in a later stage”; no AI, uploads, GitHub, Skills installation or authentication is simulated.

The backend implements all five specified endpoints, strict Pydantic validation, database sessions, schema-aware readiness, structured expected errors, SQL constraints and Alembic migration 0001. Development and test PostgreSQL are separate containers, roles, ports and storage. Test cleanup is guarded to `orba_test` only.

## B. Important changed files

| File / directory | Responsibility |
|---|---|
| apps/api/orba/main.py | Live/ready/create/list/detail endpoints and error envelopes |
| apps/api/orba/config.py, db.py | Environment settings, engine/session lifecycle, timeouts and log parameter protection |
| apps/api/orba/models.py, schemas.py | Project storage and API validation contracts |
| apps/api/migrations/versions/0001_projects.py | Versioned projects schema |
| apps/api/tests | Actual PostgreSQL integration and outage tests |
| apps/api/scripts/prepare_tests.py | Guarded test migration and test-data reset |
| apps/web/src/app | Chat, Projects, detail/new, later-stage pages, semantic palette and responsive CSS |
| apps/web/src/components | Shared shell, theme provider, real project form and source-owned shadcn-style Button |
| apps/web/src/lib/api.ts | Typed real HTTP client, timeouts and uncertain-save warning |
| apps/web/tests, playwright.config.ts | Real browser/service integration, desktop/mobile/tablet |
| infra/compose.yaml | Loopback-only persistent dev PostgreSQL and separate ephemeral test PostgreSQL |
| pnpm-lock.yaml, apps/api/uv.lock | Resolved dependency locks |
| README.md, AGENTS.md | Reproduction instructions and persistent engineering rules |
| docs/ARCHITECTURE.md, ROADMAP.md, IMPLEMENTATION_PLAN.md, TEST_PLAN.md | Architecture, bounded scope and reviewed acceptance plan |
| scripts/verify.ps1 | Executed check sequence with real exit-code enforcement |

## C. Commands executed and observed outcomes

`pnpm` commands below were invoked through `npm exec --yes --package=pnpm@12.14.0 -- pnpm` because no global pnpm command was installed. Table rows show the actual command body. Grouped historical calls had a failing final exit where noted; individual success is supported by the command output and later isolated checks.

| Command | Exit / outcome |
|---|---|
| `git status --short` before initialization | 128, fatal: not a git repository |
| `git init -b main` | 0 |
| gstack startup helper existence / Git Bash preamble | Helper absent; degraded skill startup, no helper telemetry claimed |
| `docker info` initially | 1, Linux engine named pipe did not exist |
| `docker desktop start` | 0; subsequent engine query returned 29.8.1 |
| `npm view next version`, `npm view pnpm version` | 0; 16.4.2 and 12.14.0 |
| `uv sync` in apps/api | 0; real lockfile and virtualenv created |
| `docker compose -f infra/compose.yaml --profile test up -d --wait` | 0; both real PostgreSQL containers healthy |
| `uv run --directory apps/api alembic upgrade head` | 0; fresh development DB migrated; psql confirmed version 0001 |
| `pnpm install --save-exact` | 1; `unexpected argument '--save-exact' found` |
| First `pnpm install` | 1; `ERR_PNPM_IGNORED_BUILDS`, unrs-resolver script required explicit policy |
| Subsequent `pnpm install` | 0 after explicit workspace allowBuilds entry |
| First backend pytest | 0; 15 passed, Starlette httpx deprecation warning |
| First Ruff checks | 1; two I001 import-order errors in migrations |
| `uv run ruff check . --fix`, `uv run ruff format .` in apps/api | 0; imports and formatting fixed |
| `uv add --dev httpx2` in apps/api | 0; supported TestClient transport installed, warning removed |
| Initial typecheck / build | 1; Lucide 1.59.0 no longer exports Github; changed to GitFork |
| Initial lint with TypeScript 7.0.2 | 1 wrapper / ESLint reported 2; typescript-eslint explicitly rejects TS 7.0 |
| TypeScript 6 version / lint peer queries | 0; compatible 6.0.3 chosen |
| Subsequent lint | 1; anonymous default export warning in PostCSS config; fixed named config |
| `pnpm peers check` with ESLint 10.13.0 | 1; import/a11y/react plugins declare support only through 9 |
| `pnpm --filter @orba/web add --save-dev --save-exact eslint@9` | 0; resolved compatible 9.39.5; npm deprecation notice retained as limitation |
| `pnpm --filter @orba/web exec playwright install chromium` | 0; actual Chromium/FFmpeg/headless shell downloaded |
| First browser suite | 1; 8 passed, 4 failed due alert locator also matching Next route announcer |
| Expanded intermediate suite | 1; 26 passed, 1 failed because tablet preset was assumed to have narrow nav |
| `codex --version`, `codex login status` | 0; CLI 0.163.0, logged in via ChatGPT |
| Read-only independent `codex exec ... -o docs/INDEPENDENT_REVIEW.md` | 0; six findings, execution explicitly unverified by reviewer |
| `pwsh -File scripts/verify.ps1` | **0**; all ten commands in final sequence exited 0 |
| `pnpm peers check` after compatibility fix | **0**, no peer dependency issues |
| `pnpm install --frozen-lockfile` | **0**, lockfile up to date |
| `uv run --directory apps/api alembic check` | **0**, no new upgrade operations detected |
| `git diff --check` | 0; all project files are still untracked, so this is not a full whitespace audit |
| `uv run --directory apps/api uvicorn orba.main:app --host 127.0.0.1 --port 8000` | Running; startup complete, live and ready HTTP 200 |
| `pnpm --filter @orba/web start` | Running; Next.js ready in 211ms, HTTP 200 |
| Live web/API smoke probes | 0; web heading present, live 200/alive, ready 200/ready |
| Real negative-path diagnostic | 0; actual response bodies and DB counts saved in evidence/negative-path.json |

Final script sequence: Compose up, uv sync --locked, development Alembic upgrade, pytest, Ruff check, Ruff formatting check, typecheck, lint, production build, E2E. Native stdout appeared in the actual terminal/tool results; the PowerShell transcript captures the command/exit ledger but does not contain all native stdout. Counts below are copied from the observed terminal output, not inferred from that transcript.

## D. Verification matrix

| Requirement | Status | Evidence |
|---|---|---|
| Frontend starts | PASS | Next production start; HTTP 200 with Chat heading |
| Backend starts | PASS | Uvicorn startup complete; actual live/ready responses |
| PostgreSQL connection | PASS | Both Compose services healthy; real integration queries |
| Initial migration | PASS | Fresh dev/test DB upgrade; version 0001; Alembic check clean |
| Valid creation commits | PASS | Independent SQLAlchemy session reads committed UUID/fields |
| List returns persisted rows | PASS | API ordering/pagination tests and browser Projects navigation |
| Existing project retrieval | PASS | Exact response matches saved data; browser reload |
| Invalid input does not persist | PASS | Seven parameterized cases; real independent row count |
| Missing UUID yields expected error | PASS | API 404 envelope; browser not-found message |
| Readiness reflects real DB availability | PASS | Available schema 200; unreachable real endpoint 503; liveness remains 200 |
| Actual browser create/detail/reload/list | PASS | Chromium desktop, mobile and tablet; real API/PostgreSQL |
| Empty/loading/error/validation states | PASS | Real empty DB UI, async loads, actual 404 and offline browser handling, whitespace rejection |
| Theme toggle and persistence | PASS | Toggle/reload E2E in all three viewports |
| Responsive/keyboard navigation | PASS | Viewport overflow assertion, skip link, mobile Escape/focus restoration |
| Honest future-stage screens | PASS | Source inspection and Skills E2E; no connected services claimed |
| Strict TypeScript | PASS | next typegen + tsc --noEmit |
| ESLint | PASS | --max-warnings 0, no rule weakened |
| Python lint/format | PASS | Ruff check; 12 files already formatted |
| Production build | PASS | Next build generates all app routes successfully |
| Dependency pinning/compatibility | PASS | Both locks; frozen pnpm install; peer check clean; documented TS/ESLint compatibility pins |
| Reproduction documentation | PASS | README plus executed verification script and API/web environment examples |
| Public deployment / production auth | NOT RUN | Outside Stage 01; no deployment performed |
| Firefox/WebKit/native device audit | NOT RUN | Chromium viewport emulation only; not mandatory for this stage |

## E. Test evidence

Final observed backend output:

```text
...............                                                          [100%]
15 passed in 10.31s
```

Final observed browser output:

```text
Running 30 tests using 1 worker
30 passed (41.9s)
```

Backend: FastAPI TestClient executes actual handlers and SQLAlchemy sessions against real migrated PostgreSQL. Valid creation is checked in a separate session. No mocks/stubs/SQLite. The outage test attempts a real refused TCP connection. Browser: ten scenarios in each of three Chromium configurations. Next.js, Uvicorn and PostgreSQL are real. Browser offline mode causes genuine network failure; no intercepted/fabricated API response is supplied. Zero skipped tests and zero configured retries.

Browser scenarios: empty project collection; Chat creation/detail/reload/list; explicit-title creation; theme persistence + future screen + keyboard skip; actual missing-project error; offline failure/draft retention/manual recovery; whitespace rejection without POST; responsive navigation/Escape; screenshots of both themes; two rapid submits produce one creation request. The synchronous ref lock was added to address the last case.

Artifacts present locally: `apps/web/playwright-report/index.html`, `apps/web/test-results/.last-run.json` (`status: passed`, `failedTests: []`), `docs/evidence/verification-transcript.txt`, `live-smoke.json`, `negative-path.json`, and six home screenshots. Generated screenshots/reports are ignored; regenerate with the commands in README. Desktop light and mobile dark screenshots were visually inspected after the final suite. Screenshots establish observed layout, not complete WCAG conformance.

## F. Negative-path evidence

Actual post-suite diagnostic against the isolated real DB:

```json
{
  "invalid_creation": {
    "status": 422,
    "error_code": "validation_error",
    "field": "body.title",
    "rows_before": 4,
    "rows_after": 4
  },
  "unavailable_database": {
    "ready_status": 503,
    "error_code": "database_unavailable",
    "elapsed_seconds": 3.014,
    "live_status": 200
  }
}
```

The rejected request used a whitespace title. Its actual body explains “String should have at least 1 character.” The unavailable app was configured to connect to PostgreSQL at 127.0.0.1:1, using the real driver. Its logged error was `Database operation failed (OperationalError)`; the response contains “Database unavailable. Try again shortly.” Tests pass because failure is detected and handled; neither the invalid creation nor unavailable database is called successful. Full unabridged response envelopes are in negative-path.json.

## G. Known limitations and review resolutions

- Local single-user only: no auth, tenant isolation, public TLS, rate limiting or deployment hardening. Local Compose credentials are public development values. All services are bound to loopback.
- No AI, GitHub, Skills installation, multiplayer, canvas, execution sandbox, cloud workspace or agent/evidence generation. Stage 02 has not started.
- No project edits/deletes/status transitions in Stage 01. Status is `created`, now consistent in plan/schema/UI/tests.
- There is no server-side idempotency guarantee after an ambiguous POST response. The UI prevents rapid duplicates, retains drafts, does not auto-retry, and asks users to inspect Projects before retrying.
- Browser E2E uses a real Next development server; the production build/start received separate live HTTP smoke checks. Firefox, WebKit, physical devices, broad assistive-technology testing and load testing were not run.
- ESLint 9.39.5 is a documented compatible but npm-deprecated line until the Next lint plugins support 10. TypeScript 6.0.3 is required by the present parser. No peer checks or lint rules were disabled.
- Exact test DB role/name guards protect cleanup; test suites must run sequentially. No remote/CI run is claimed.
- Independent review findings were addressed: lifecycle consistency; invisible mobile focus targets/focus management; uncertain-save warning; README/evidence and automatic test migration setup; sanitized DB logging; more failure/empty/duplicate-submit tests. Not all aspirational test-plan cases were automated: a dedicated unmigrated-schema readiness test and full production-browser matrix remain future verification improvements; the required available/unavailable readiness and fresh migration checks did execute.
- Autoplan used the delegated Codex review and an additional real read-only Codex CLI review. No distinct Claude model was available, so cross-model consensus is not claimed. Startup helper/telemetry/automatic review-log machinery was missing. The primary session's explicit implementation instruction supplied authorization; no additional permission was inferred for deployment.

Durable operational findings: this environment requires the npm-based pnpm launcher; pnpm 12 enforces explicit build-script allowance; current TS7/ESLint10 are incompatible with the chosen lint toolchain; PowerShell's host transcript omits native stdout here. These are documented in this repository; no global memory was modified.

## H. Reproduction

Use README.md for installation, environment files and exact two-terminal startup. To rerun the executed verification:

```powershell
npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile
uv sync --locked --directory apps/api
npm exec --yes --package=pnpm@12.14.0 -- pnpm --filter @orba/web exec playwright install chromium
pwsh -File scripts/verify.ps1
```

Docker Desktop must be running. The script starts both DB containers, applies the dev migration, and test setup migrates only orba_test. Stop or free any existing 3001/8001 service before E2E. Development 3000/8000 can remain running. Do not run pytest concurrently with Playwright.

## I. Stage verdict

**VERIFIED**

All mandatory Stage 01 acceptance checks executed successfully. This verdict is limited to the local foundation and the environment/browser scope recorded above.
