# ORBA verification plans

## Current Stage05A extension

Normal scripts/verify.ps1 retains every Stage01–04 check and adds orchestration
backend and desktop/mobile/tablet cases. A separate
scripts/verify-orchestration-local.ps1 verifies actual local services, source UI
approval, run creation, immutable task/edge snapshots, SQL checksum/ledger audit,
reload, idempotency and isolation. No model call or executor response is used.
See PLAN_STAGE05A.md, ARCHITECTURE_STAGE05A.md and VERIFICATION_STAGE05A.md for the
exact lifecycle, failure matrix and executed evidence. Backend and browser tests
remain sequential against guarded orba_test. The deliberately incorrect completion
assertion is outside normal discovery and must genuinely exit1 when explicitly run.

The Stage04 section below describes the preserved planning-agent regression scope.

## Current Stage04 extension

Run `pwsh -NoProfile -File scripts/verify.ps1` from the repository root. It retains
all Stage01-03 test identities and adds the Architect suites. Use migrated real
PostgreSQL `orba_test`; backend and browser suites run sequentially. Model doubles
are explicitly test-only and never establish real Architect generation.

Required new coverage includes exact approved PRD binding/current-source fencing,
strict output validation, relational persistence/atomic rollback, workspace roles,
CSRF/original-session checks, version/revision conflicts, immutable approvals, shared
admission and idempotency. Pure graph tests cover deterministic ordering, cycles,
missing/self/duplicate edges, readiness and transitive impact; PostgreSQL tests also
enforce cross-owner references, exact criterion parentage and structural coverage.
Controlled 503/504/malformed-output cases must preserve prior approvals and save no
successful-looking architecture.

The actual browser uses real authentication, API and PostgreSQL on desktop/mobile/
tablet. Exercise proposal/graph display, dependency edits, real cycle rejection,
save/reload/approval, Viewer/outsider restrictions and unsaved-navigation recovery
including a modal opened while the Architecture tab is hidden.

`uv run --directory apps/api python -m scripts.architect_false_success` launches a
separate deliberately incorrect failed==succeeded assertion. Its child must actually
exit1; wrapper0 only confirms that expected failure was observed, never a production
test pass. Normal discovery excludes the experiment.

`scripts/verify-architect-live.ps1 -AllowPaid` is a separate future authorized Gate B,
not part of this deterministic plan. It must use one real response for independent
SQL/DAG/coverage, browser/edit/approval/reload/isolation checks. No fresh owner
authorization means no generation. Gate C remains PARTIAL without matching passing
Stage04 A and real Architect B. Actual counts, exits and receipts are recorded in
[VERIFICATION.md](VERIFICATION.md).

## Historical Stage01 plan

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


## Stage05A proof-v2 repair regression

Preserve all478 previous backend identities and all186 browser cases. Add205
backend adversarial/integration cases for missing/null/empty/malformed/contradictory
proof, strict UUID/counter/hash types, raw normalization and bool/int differences,
API/SQL/graph/source reconciliation, full edge/event records, zero-edge validity,
native empty-task-query rejection and python -O integrity guards. Current required
backend total683. Real SQL positives and independent local Gate B remain distinct
from explicitly synthetic unit inputs. See VERIFICATION_STAGE05A_REPAIR.md.
