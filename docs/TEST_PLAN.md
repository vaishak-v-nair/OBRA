# ORBA Stage 01 test plan

All cases below are planned until actual output is recorded in VERIFICATION.md. Use real PostgreSQL and migrated schema. No SQLite, fake API responses, fake AI, or dummy PASS drivers satisfy this plan.

## Isolation and setup

Use a dedicated database such as `orba_test` with credentials/configuration distinct from the development database. Fail before cleanup if the configured database lacks an explicit test suffix or equals the dev URL. Apply Alembic upgrade head to the test database. Run browser API/web services with that URL, and do not reuse an unrelated already-running dev server. Preserve test output and actual exit statuses.

## Backend cases

| Case | Exercise | Required assertion |
|---|---|---|
| B1 | POST valid title/description | 201, real UUID, server-owned created status, aware timestamps; fresh SQLAlchemy session finds committed row |
| B2 | GET list after B1 | Persisted record and same description; deterministic order if specified |
| B3 | GET UUID | Exact saved title, description, status and timestamps |
| B4 | POST missing/empty/whitespace/wrong-type/oversized fields | Structured 422; fresh DB count unchanged |
| B5 | GET unused valid UUID | Structured 404 with stable error code |
| B6 | GET malformed UUID | Structured 422, no 500 |
| B7 | GET list with empty isolated DB | 200 empty collection |
| B8 | GET live/ready with migrated DB | Both 200; readiness actually queries database/schema |
| B9 | App configured with unreachable PostgreSQL port | Ready returns 503 within bounded timeout; live remains 200; real connection failure, no monkeypatch |
| B10 | Migration application | Alembic head on clean dedicated DB; table columns and constraints present |

Use FastAPI TestClient against real application routes for backend integration, with real DB sessions. These are in-process HTTP integration tests, not evidence of a listening production server. Separately probe the actual running API and report that evidence.

## Browser cases

| Case | Exercise | Required assertion |
|---|---|---|
| E1 mandatory | Open real Chat, type unique description, submit | Actual API request creates record; navigates to UUID detail; original text appears |
| E2 mandatory | Reload E1 detail | Same UUID and description remain, proving durable backend read |
| E3 mandatory | Navigate Projects | Same persisted record appears and opens same UUID |
| E4 | Projects create flow | Shared form creates real second project |
| E5 | Empty state | Empty isolated DB renders useful message and working create action |
| E6 | Validation | Blank/whitespace cannot submit; visible accessible explanation |
| E7 | Genuine service failure | Run service with unavailable DB or stop test API; form shows actionable failure and preserves text |
| E8 | Rapid double submit | Pending form suppresses second same-form mutation |
| E9 | Unknown project URL | Useful not-found state and recovery link |
| E10 | Future navigation entries | Explicit Coming in a later stage; no connected-state fiction |
| E11 | Theme | Light/dark switch changes tokens and persists through reload |
| E12 | Mobile and keyboard | At 375px no horizontal overflow; nav/form/theme usable by keyboard; labels and focus visible |

The mandatory E1–E3 journey uses running real web, API and PostgreSQL with no route interception, mock response, stubbed network or pre-seeded hardcoded array. Additional isolated error-display unit tests may mock a helper only if explicitly identified; they do not replace E7 or real outage detection.

## Negative-path evidence

At minimum execute B4 with count before and after, or B9 with real failed connection and response status. A 422 or 503 is the expected underlying failure. The test passes only because the application detects and handles it; never call the rejected write or unavailable database successful. Preserve response body/status and relevant real stderr.

## Verification commands and pass criteria

Exact runnable commands must match generated package names and scripts in README. Required categories: pnpm locked install, uv locked sync, Docker Compose health, Alembic upgrade, Pytest, ESLint, TypeScript noEmit, Next.js production build, real HTTP live/ready probes, Playwright browser install and E2E. Capture every exit status; skipped/not-run checks are not passing. A missing external dependency makes dependent cases BLOCKED, while independent checks should still run.

## Final evidence record

Record actual test counts, command outputs, mocks/stubs if any, API/browser/database process scope, DB isolation details, negative failure handling, remaining blockers and exact reproduction commands. Stage verdict is VERIFIED only when every mandatory definition-of-done item passes; otherwise PARTIAL, BLOCKED or FAILED. Do not automatically start Stage 02.

