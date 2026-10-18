# ORBA engineering contract

Stage authority is the owner's request. Stage 02 adds real accounts and workspace authorization for local development. Stage 01 project behavior and data must be preserved. Do not start later stages automatically. No public deployment, destructive operations, credential changes, or external messages without owner authorization.

## Truth and verification

- Never claim success from files existing. Execute the implementation and relevant checks.
- Never fabricate terminal output, screenshots, API responses, DB records, agents, test results or evidence.
- No dummy success states, fake authentication, fake AI agents, fake GitHub services or fake Skills installation.
- Tests exercise application code. Only isolated unit tests may use justified, explicitly identified mocks. Integration/E2E use real PostgreSQL/API/browser. A skipped test is not passed.
- Preserve real command failures and fix their causes. Never weaken assertions, disable checks or remove tests to get green.
- If a required dependency cannot be reached, report BLOCKED with actual error and missing dependency. Distinguish implemented, planned, blocked and verified.
- Mandatory checks must pass before a VERIFIED verdict. Otherwise use PARTIAL, BLOCKED or FAILED. Update docs/VERIFICATION.md with commands, exit statuses, counts and limitations.
- Test cleanup is allowed only against the guarded isolated `orba_test` database and role. Never clear development project data. Do not run backend and E2E tests simultaneously: both use this test database.

## Architecture and development

Use Next.js App Router, strict TypeScript, Tailwind, shadcn/ui, Lucide; FastAPI, Pydantic v2, SQLAlchemy 2, Alembic and PostgreSQL. Use pnpm and uv with committed lockfiles. Select current compatible stable releases; document compatibility exceptions. Do not substitute SQLite. Alembic migrations are the schema authority; no startup create_all.

Keep business API behavior in apps/api; apps/web is the UI. Semantic theme tokens live in globals.css. Shared creation logic lives in ProjectForm. Use native controls and existing helpers before adding abstractions or dependencies. No empty shared packages.

Handle invalid input, missing records, database failure, loading, empty and error states. Keep drafts on save failures. Never automatically retry a POST. Do not log credentials or project descriptions in error logs. Bind local services and database ports to loopback. Do not claim production security certification. Stage 02 must enforce real authentication and workspace isolation.

Required verification: migrated real test PostgreSQL; persistence/list/retrieve/invalid/not-found/readiness tests; actual browser creation -> detail -> reload -> list; meaningful negative paths; lint; strict typecheck; production build. See README.md and docs/TEST_PLAN.md. Browser/device emulation does not establish native-device or all-browser compatibility.

## Stage 02 security rules

- FastAPI alone authenticates. Use Argon2id and hashed opaque PostgreSQL sessions; no hardcoded users, auth bypass, browser-stored authority or client-trusted ownership.
- All cookie-authenticated writes require validated Origin and CSRF. Start Uvicorn with --no-proxy-headers. Never log passwords, hashes, cookie/session/CSRF/invitation tokens.
- Every resource request validates current membership. All membership, invitation and project writes lock the workspace before role checks. Preserve the final Owner; Admins only manage Member/Viewer. Invitation acceptance must be atomic, email-bound, expiry/revocation/use checked, and recheck inviter privilege.
- Never assign legacy projects to the first registrant. Preserve every original field. Legacy ownership is restricted; only scripts.claim_legacy with explicit IDs and --apply may transfer data. No public claim endpoint. No production database reset or migration downgrade to avoid complexity.
- Keep the intentionally incorrect authorization experiment outside normal test discovery. Its actual exit1 is expected and must never be called a passing production test. Mandatory suites must contain no skips, xfail or dummy drivers.
- Use same-origin Next API proxy without duplicating auth. SessionStorage may hold a selected workspace preference only. Never render protected content until session checks succeed. Manual invitation sharing is not email delivery.
- Run scripts/verify.ps1 plus relevant schema/migration/auth/role/tenant/legacy and browser tests. Do not begin Stage 03. Preserve user changes; current source is uncommitted/untracked, so Git diffs alone cannot establish changes.

