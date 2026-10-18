# ORBA Stage 02 architecture

Stage 01's Next.js/FastAPI/PostgreSQL monorepo is retained. Stage 02 replaces anonymous project access with real accounts, server sessions and workspace authorization. The current scope is local development; passing tests do not certify production security.

```text
Browser localhost:3000
  ThemeProvider -> SessionProvider -> Shell -> AuthGate -> protected page
  Session cookie (HttpOnly) | CSRF header | selected workspace preference
       |
Next /api/v1/[...path] proxy (API_URL, server-only)
  forwards Cookie/Origin/Content-Type/X-CSRF-Token; preserves Set-Cookie
  no authentication database, no claim/session authority, no credential logs
       |
FastAPI 127.0.0.1:8000 --no-proxy-headers
  auth: Argon2id, opaque sessions, CSRF+Origin, DB attempt buckets
  projects/workspaces: authenticated identity -> membership -> role -> transaction
       |
PostgreSQL 18.6 / Alembic 0001 -> 0febbe526f54
  users <- sessions
  users <-> workspace_members <-> workspaces <- projects
  workspace_invitations (email/role/token hash/expiry/terminal state)
  login_attempts (hashed account/IP keys + timestamps)

Tests: separate web:3001 -> API:8001 -> orba_test:54330
Dev:   web:3000 -> API:8000 -> orba:54329 (named persistent volume)
```

## Data and migration

Users have UUID, normalized unique email, salted Argon2id password hash, display name, status and aware timestamps. Sessions have UUID, user FK, unique token hash, created/expiration/revocation timestamps. Workspaces have UUID, name, unique readable slug with random suffix, creator FK, timestamps and a restricted-legacy flag. Memberships have unique workspace/user pairs, checked roles and joined timestamp. Invitations have unique token hashes, partial unique pending workspace/email index, checked role/status, inviter/email/expiry and terminal timestamps. Appropriate FK, membership/session/project lookup indexes are in the migration. SQLAlchemy models match Alembic (`alembic check`).

Projects retain UUID/title/description/created status/timestamps and gain a nonnull workspace FK plus nullable creator FK. New projects always use the validated session's user and an authorized supplied workspace. Existing rows are backfilled into the fixed restricted workspace `00000000-0000-0000-0000-000000000001`, with creator null and no members. No default signup membership is created there. The migration adds the workspace column nullable, inserts/backfills ownership, then enforces not-null; original values are untouched. Repeat upgrade is a no-op through the Alembic revision record. Before the ownership upgrade, a native loopback listener probe rejects a running local API at port 8000 (ORBA_API_PORT selects a custom port). The known isolated orba_test database/role is exempt; no application authentication check is bypassed. Operators must independently stop remote/custom deployments. Downgrade deliberately fails instead of re-exposing private data or dropping auth state.

The terminal-only claim command requires explicit target workspace, existing Owner and selected project UUIDs. It checks all rows under lock before making any transfer. Default is dry run; --apply changes only ownership/creator, preserving original updated_at explicitly. It refuses already-claimed rows. Local operator/database access is its authority; no HTTP claim route exists.

## Authentication, cookies and CSRF

FastAPI validates every protected request against a stored SHA-256 hash of a 32-byte random opaque token, unrevoked/unexpired session and active User. Login/register revokes the presented valid old session and creates a new one. Logout persists revocation and expires the cookie. The UI clears local protected state on every logout attempt and distinguishes an unconfirmed server revocation after network failure. Password verification uses maintained argon2-cffi Argon2id with unique salts; unknown users receive comparable dummy hash work. Passwords are not trimmed. User response schemas omit hashes/tokens.

Cookie: host-only, Path=/, HttpOnly, SameSite=Lax, explicit max-age. COOKIE_SECURE is configurable for local HTTP and required true when WEB_ORIGIN is HTTPS. Session lifetime is bounded and enforced server-side. Session cookie names and lifetimes are API configuration, not frontend claims.

GET /auth/csrf returns a token derived by HMAC from the currently validated opaque session credential; it is not stored in browser persistence. The client sends it on every POST/PATCH/DELETE. Before authentication, the endpoint creates a random HttpOnly SameSite=Strict cookie and returns its matching token. The exact configured Origin is independently required on all writes, including login/register, and no cross-origin read permission is granted. Tokens are compared as bytes so malformed non-ASCII headers produce 403 rather than TypeError. Responses are no-store. Invitation links use fragments and the root page declares no-referrer.

The same-origin Next handler forwards only required headers and preserves multiple Set-Cookie values. It does not trust browser-supplied forwarded IP headers and does not create a competing session. API_URL is server-only and read at request time. Upstream failure produces a truthful 503. The frontend never automatically retries a write; unknown outcomes retain drafts and warn about possible duplicates.

## Brute-force limits and concurrency

PostgreSQL stores attempt timestamps under SHA-256 account and peer-IP keys. Each request locks both bucket keys in sorted order using transaction advisory locks, checks a rolling window, persists attempts and commits before password verification. Failed and successful attempts count. Defaults: 5 per account / 15 minutes, 100 per shared peer IP / 15 minutes. Expired attempt rows are removed on future attempts. Uvicorn must run --no-proxy-headers; otherwise its loopback proxy defaults can trust forged X-Forwarded-For values. The Next proxy strips those headers regardless. This local limiter has shared-IP lockout/throughput limitations and is not a full internet abuse-control system.

All membership mutations, invitations and project writes first lock the workspace row, then read the caller's current role. Invitation acceptance locks workspace before invitation, refreshes the invite under lock, verifies pending/unexpired/email match, rechecks inviter privilege and inserts the unique membership and consumed state in one transaction. Consistent lock order prevents the obvious invite/role deadlock. Concurrent owner demotions preserve one Owner; concurrent accepts produce one membership. Reads use current membership joins. No frontend role control substitutes for backend enforcement.

## Roles and API contracts

Owner: read/write/invite/manage roles; cannot demote/remove final Owner. Admin: read/write, invite and manage only Member/Viewer; cannot promote self, affect Admin/Owner or issue Owner/Admin invitations. Member: read/write projects. Viewer: read only. Only an Owner can promote an existing member to Owner. Invitation creation never grants Owner.

Existing routes are retained: POST/GET /api/v1/projects and GET /api/v1/projects/{id}. Create and list now require workspace_id; create forbids creator_id/status injection. PATCH /projects/{id} edits bounded title/description after write-role enforcement. List remains newest-first with deterministic UUID tie-break and 50-row UI pagination. Unauthorized resources use the same 404 response as absent ones. Expected validation, unauthenticated, forbidden, missing, duplicate, throttled and DB failures use structured 422/401/403/404/409/429/503 envelopes. Readiness checks the new tables/columns, not only network connectivity. Liveness remains DB-independent.

Auth routes: register/login/logout/me/csrf. Workspace routes: create/list/detail/members, invitation create/list/revoke, role PATCH, membership DELETE. Invitation acceptance requires authentication and CSRF; no unauthenticated resource preview exposes workspace data. The invitation link is returned only from authorized creation and never reconstructed by listing. Expired is a derived read status; accepted/revoked timestamps and statuses are persisted. No email is sent.

## Frontend state and preserved design

Existing semantic palette, Button, navigation, ProjectForm, project list/detail, theme and responsive layouts are retained. Added auth forms, account menu, native workspace selector, creation page, member/invite settings and acceptance page. AuthGate blocks protected children while session checks are pending and clears component state on account/workspace/route changes. Request generations prevent stale session refresh responses overwriting newer identity. A workspace ID in sessionStorage is only a preference and is matched against authorized server workspaces. No password, session token or invitation token is stored there. CSRF tokens live per request; invitation fragments stay in URL/in-memory flow until consumed.

Mobile navigation includes native select/summary controls in its visibility-aware focus trap and restores focus on Escape. Destructive membership/role actions use confirmations and only update server state on real success. Viewer project creation and editing controls reflect the returned role, with backend checks independently enforcing it. Permission revocation is enforced on subsequent requests; no real-time push is claimed.

## Verification, observability and limits

Stage 01 test scenarios remain with real registration/workspace setup. Integration tests use the guarded PostgreSQL test database and fresh migration schema for old-record preservation. No SQLite/mock auth substitutes. Playwright exercises real UI/backend/database in Chromium desktop/mobile/tablet. Auth network traces are off because they contain credentials; safe home screenshots remain. An explicit-only pytest experiment intentionally expects unauthorized success and must fail independently of the passing suite.

Sanitized security event logs contain event codes and non-secret actor/workspace UUIDs only. DB errors log exception type only and SQL engines hide parameters. There is no durable audit store, production TLS/SSO/MFA/recovery, verified email ownership, full penetration test, provider/agent integration or public deployment. Legacy backups/production operations require an operator; no rollback/reset shortcut is authorized.

Dependencies: existing Next 16.4.2/React 19.3.1 stack and PostgreSQL 18.6 retained; argon2-cffi 25.1.0 and email-validator 2.3.0 added through uv.lock. TypeScript 6.0.3 is required by the present parser; ESLint 9.39.5 satisfies current Next plugin peer ranges although npm marks it deprecated. Upgrade when compatible, do not disable checks.

References checked during implementation: [OWASP CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [argon2-cffi API](https://argon2-cffi.readthedocs.io/en/stable/api.html), [Next rewrites/proxy documentation](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites) and installed Next route-handler documentation. These inform the design; they do not certify the implementation.

