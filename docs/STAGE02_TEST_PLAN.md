# ORBA Stage 02 real-service test plan

Generated 2026-10-18 by the sequential autoplan engineering review. Repository: E:/BrosKi/OBRA, main (no commit at intake). This is a specification, not a passing-test record. Actual outcomes, counts, commands and exit statuses belong in docs/VERIFICATION.md.

## Test authority and isolation

Use existing pytest/FastAPI TestClient -> actual SQLAlchemy -> migrated PostgreSQL, plus Playwright -> actual Next.js -> actual FastAPI -> the same isolated PostgreSQL. No SQLite, mocked auth, fabricated API response, hardcoded user session, in-memory substitute or success-print driver. Every account/workspace/project/membership used for acceptance is actually persisted.

The only cleanup target is database **orba_test**, role **orba_test**, loopback port **54330**. Validate database and role before any truncate/schema-reset test. Backend and E2E suites run sequentially; neither may clear development data on port 54329. Use independent browser contexts/cookie jars for distinct people. No skipped mandatory test counts as passed.

Preserve and adapt Stage 01 tests rather than deleting them: project creation/independent-session persistence, deterministic list/pagination, exact retrieval, seven invalid payloads/no inserts, trimming, UUID/pagination validation, missing project, schema-aware readiness and real refused-database 503. Preserve ten existing browser behaviors across existing desktop/mobile/tablet configurations: empty state, Chat persistence, explicit title, theme/future-screen/skip-link, real not-found, offline draft recovery, whitespace/no POST, responsive navigation/Escape, screenshots and rapid double-submit.

All protected fixtures must register users and create workspaces through actual auth/workspace APIs. Database setup may explicitly construct preexisting migration rows or mutate expiration/revocation timestamps for deterministic edge cases; it must not bypass the app to establish the session under test. No arbitrary sleeps to expire credentials.

## Affected pages and routes

| Surface | What to verify |
|---|---|
| /sign-up, /sign-in (actual chosen paths) | Visible labeled fields, real server validation, cookies, pending/errors, safe invite return |
| / and /projects/new | Existing Chat/explicit form creates into currently authorized workspace |
| /projects and /projects/{id} | Selected scope, persistence, protected loading, hidden-resource errors |
| /workspaces, selected workspace settings | Create/switch, current role, real members, invite/manual link and authorized changes |
| /invitations/accept#token=... | Fragment handling, authenticate first, explicit accept, safe invalid/expired state |
| /api/v1/auth/register/login/logout/me/csrf | True user/session authority, secret-safe schemas, CSRF/Origin and throttling |
| /api/v1/workspaces/... | Membership-scoped lookup/list and role-enforced mutations |
| /api/v1/invitations/accept | Email-bound one-time atomic membership |
| /api/v1/projects/... | Authenticated scoped create/list/get/PATCH without forged ownership |
| /health/live, /health/ready | Live independent of DB; ready requires complete Stage 02 schema |
| Local scripts.claim_legacy command | Dry run and explicit all-or-nothing persisted claim; no public endpoint |

## Authentication integration cases

Use recommended test file tests/test_auth.py, with existing shared real-service fixtures.

| ID | Scenario | Required assertions |
|---|---|---|
| A01 | Valid registration | 201; independent DB session reads normalized email/display name; safe response has no password/hash/token |
| A02 | Duplicate normalized address | Whitespace/case variations collide; 409; exactly one DB user; no partial session/workspace |
| A03 | Hash security and salt uniqueness | Stored string is Argon2id; library verifies original password; plaintext absent; two same-password users have distinct hashes |
| A04 | Password boundaries | <12, >128, whitespace-only rejected; invalid email/name/extra user ID rejected; no user insert |
| A05 | Password exactness | Leading/trailing characters are not silently stripped; correct original signs in, trimmed variant does not |
| A06 | Valid login | Real 200 and active DB session; raw cookie differs from stored SHA-256 hash; cookie HttpOnly/SameSite/path/lifetime correct |
| A07 | Invalid identity/password | Generic 401 for absent address/wrong password; no valid session created; no raw values echoed |
| A08 | Unauthenticated protected reads/writes | 401 on valid protected request context; no project/member content and no write |
| A09 | Logout | Real revocation timestamp; cookie cleared; old raw cookie from separate client rejected |
| A10 | Expired session | Set expires_at in past in DB; me and project access 401; project rows unchanged |
| A11 | Revoked session | Set revoked_at; old credential rejected independent of browser state |
| A12 | Session rotation | Login with presented active session yields different raw cookie/hash/row; previous row revoked; old cookie denied |
| A13 | Cross-session CSRF | Valid token from user A does not authorize B's cookie; 403; no mutation |
| A14 | Missing/invalid CSRF | Missing/random/non-ASCII raw header rejected safely with 403 for workspace/project/member/invite/logout operations; no unhandled TypeError and DB unchanged |
| A15 | Origin validation | Missing, foreign, prefix/suffix-lookalike Origin rejected despite valid CSRF; exact allowed origin accepted |
| A16 | Preauthentication CSRF | Register/login without valid preauth cookie/header/Origin rejected; valid protection establishes session and rotates context |
| A17 | Login restriction | At configured attempt threshold, subsequent actual login is 429 with safe retry info; DB attempt events confirm count |
| A18 | Shared PostgreSQL limiter | Independent app instances use same DB, cannot each get a fresh allowance; concurrent attempts respect account limit |
| A19 | Limiter time window and IP | Expired attempt events stop counting; distinct accounts share bounded IP budget; raw spoofed proxy headers cannot substitute client identity under supported startup |
| A20 | Cookie environment | HTTPS configuration with Secure=false rejected; enabled HTTPS cookie contains Secure; no dev bypass setting exists |
| A21 | Database outage | Real unreachable database -> 503 for ready/auth/database paths; live 200; secrets absent from envelopes/log capture |
| A22 | Response privacy | Cache-Control no-store on auth/protected data; no hashes/session/invite tokens in me/list/member schemas |

Exact HTTP status precedence may depend on whether a malformed request is rejected by schema, session or CSRF first; use otherwise-valid requests to prove each specific boundary independently. Do not force an auth fixture onto the actual unavailable-database test if its purpose is connection failure.

## Workspace, role and invitation integration cases

Use tests/test_workspaces.py or equivalent focused files.

| ID | Scenario | Required assertions |
|---|---|---|
| W01 | Create workspace | 201; workspace and exactly one Owner committed together; creator user matches authenticated session |
| W02 | Workspace list/get | Only own memberships listed; nonmember exact UUID returns safe 404 |
| W03 | Members list | Real user fields/roles; no hashes/secrets; unrelated user cannot list exact workspace |
| W04 | Owner invite | Intended email/role persisted; token is random and hash-only in DB; raw link exists only in creation response |
| W05 | Intended recipient accepts | Authenticated recipient + proper CSRF returns membership; intended role and accepted timestamp committed together |
| W06 | Wrong email | Otherwise valid authenticated user denied; invitation pending and no membership |
| W07 | Expired invitation | Past DB expiration denied; no membership/accepted timestamp |
| W08 | Revoked invitation | Authorized revoke sets DB state; accept denied; repeated revoke handled explicitly |
| W09 | Used/replayed invitation | Second accept rejected; one membership only; accepted timestamp stable |
| W10 | Unknown/missing/invalid token | Safe 400/422; no secret/resource leak; no membership |
| W11 | Duplicate membership/invite | Already-member invitation or accept denied; pending duplicate invite cannot proliferate |
| W12 | Expired pending replacement | New authorized invite revokes old pending row and creates fresh hash; old token unusable |
| W13 | Member restriction | Member creates/edits project, but cannot invite, list restricted invitations or change/remove roles |
| W14 | Viewer restriction | Viewer sees shared project, but create/PATCH denied with DB title/description unchanged |
| W15 | Admin restriction | Can invite/manage Member/Viewer per documented policy; cannot self-promote, grant Owner, demote/remove Owner or manage Owner/Admin peers |
| W16 | Owner role management | Owner can promote/demote permitted members; DB role matches actual response |
| W17 | Final Owner | Removing/demoting sole Owner rejected; independent DB count remains one |
| W18 | Last-owner concurrency | Two Owners concurrently remove/demote themselves through separate clients/transactions; no committed state has zero Owners |
| W19 | Atomic invitation concurrency | Two concurrent accepts of same token -> one success, one safe rejection; exactly one membership and one accepted invitation |
| W20 | Revocation race | Member removal/demotion and privileged write serialize under workspace lock; outcome follows transaction order, never stale privilege after completed revocation |
| W21 | Inviter authorization changed | Removed/demoted inviter cannot grant stale invitation privilege; acceptance rechecks inviter role |
| W22 | Workspace spoofing | Extra creator/user/role/is_legacy fields rejected; malicious target workspace cannot become owned by request payload |

Concurrency tests must use independent clients/connections and real PostgreSQL locks. A sequential pair of API calls does not prove race handling. Use bounded thread barriers/futures and join timeouts to detect deadlock instead of hanging verification. All paths use consistent workspace-before-invitation/member lock order.

## Tenant isolation and project regression cases

Create User A + Workspace A + Project A and User B + Workspace B + Project B through actual APIs. The assertions must inspect independent DB state after denied writes.

| ID | Scenario | Required assertions |
|---|---|---|
| P01 | Existing create/list/get tests | Preserve Stage 01 title/description/status/timestamps/UUID/pagination/error coverage with real auth/workspace |
| P02 | Exact-UUID private read | A GET B's known project UUID -> 404, no title/description returned; B's DB row remains intact |
| P03 | Exact-UUID private edit | A PATCH B's known UUID -> 404; independent DB title/description/workspace/creator unchanged |
| P04 | Forged workspace create/list | A submits/queries B's workspace_id -> 404; no inserted row and no B content |
| P05 | Forged creator/status | Extra fields ->422; creator always real authenticated user; no ownership injection |
| P06 | Valid member edits | Shared Member can create/PATCH only within membership; timestamp updates and saved fields verified |
| P07 | Viewer edit/create denial | Direct API attempts fail even if frontend button is absent; no DB mutation |
| P08 | Unknown resource hiding | Absent UUID and unrelated existing UUID use same safe project-not-found envelope |
| P09 | Workspace switch data | A user belonging to two workspaces sees exactly selected workspace records; list never returns combined private scope |
| P10 | Legacy invisibility | Freshly registered users cannot list/get/PATCH restricted legacy projects/workspace/member list |

## Populated migration and operator claim

Recommended tests/test_legacy.py exercises actual Alembic upgrade from revision 0001 to the Stage 02 head. The current Stage 02 migration is forward-only; do not call its downgrade as a test preparation shortcut. Prepare a genuinely isolated migration fixture within guarded orba_test (for example a temporary schema using an injected Alembic connection, or an explicitly guarded full test-schema recreation before restoring head). Never perform this operation against development data, and never run it beside E2E.

1. Apply real 0001, insert at least two rows with known distinct UUIDs, exact Unicode/whitespace-containing descriptions, statuses and timezone-aware original timestamps. Persist and retain an independent expected snapshot.
2. Execute the actual head upgrade, then execute head again to prove safe Alembic no-op behavior.
3. Compare every original ID, title, description, status, created_at and updated_at exactly; rows now reference the fixed restricted legacy workspace; creator remains unknown until a documented explicit claim.
4. Verify legacy workspace is_legacy=true, no creator and no memberships; no first registration is attached to it. Register unrelated users and prove list/get/PATCH/member/workspace access denial.
5. Create a real target workspace and Owner, invoke the actual operator command in dry-run mode with explicit project UUIDs, and prove rows unchanged.
6. Invoke with --apply, verify selected rows now belong to exact target with documented creator semantics; all Stage 01 fields/IDs/timestamps remain equal; unselected legacy rows remain restricted.
7. Owner can now read the selected project; unrelated user cannot. Missing target, non-Owner target, duplicate IDs, missing/nonlegacy project or replayed claim fails nonzero with no partial transfer.
8. Restore ordinary head/guarded clean fixture for following tests. Run alembic check to prove metadata alignment; record exact migration revision in verification.

The CLI invocation shape currently proposed by source is:

```powershell
uv run --directory apps/api python -m scripts.claim_legacy --workspace <workspace-uuid> --owner <owner-user-uuid> --project <legacy-project-uuid>
uv run --directory apps/api python -m scripts.claim_legacy --workspace <workspace-uuid> --owner <owner-user-uuid> --project <legacy-project-uuid> --apply
```

These examples contain placeholders to be replaced deliberately by the operator; do not run an indiscriminate claim during setup.

The ownership migration now enforces a stopped local API before its DDL for non-test targets. Configure ORBA_API_PORT for a custom local API port; its default is 8000. The guard is exercised with a real listening socket (reject), then the same closed port (allow), without a mocked availability result. The guarded orba_test database/role is exempt because its schema is isolated from the development API. This is a local configured-port check, not a claim of universal orchestration or protection against manually restarting obsolete code.

## Browser E2E acceptance

Run actual frontend:3001, API:8001 and migrated isolated PostgreSQL:54330; same-origin proxy target must be server-only API_URL. Disable reuse of existing test services. Use real UI registration/creation/invitation actions and separate User B context, not context.addCookies with a fabricated session or route.fulfill with fake data.

Critical shared-workspace scenario in desktop and mobile, plus retained tablet regression coverage:

1. Open signed-out application; verify no protected project text while checking session.
2. Register User A with a unique address through UI. Confirm real registration response and no browser-readable authoritative session storage.
3. Create Workspace A through UI, verify visible real workspace identity/Owner role.
4. Create Project A through existing Chat composer; observe actual 201 and detail UUID. Reload and navigate Projects; title/description persisted.
5. Open workspace settings, invite User B as Viewer, copy the link from actual response. Confirm Manual sharing / no email sent text. Ensure invitation token is a fragment and absent from normal list response.
6. In a separate browser context open invite link, register User B or sign in, retain safe invite intent, explicitly accept.
7. Verify B sees Workspace A and Project A, including reload persistence. Role label is Viewer; create/edit/invite/role actions are unavailable and direct requests are rejected.
8. Owner promotes B to Member; B refreshes authorized state and creates a second real project. Both users see deliberately shared data.
9. B creates Workspace B and private project; A cannot read/edit exact private UUID, and A's UI never shows its content.
10. B switches between A/B; project lists clear/update without showing another workspace's records under the wrong label, including reload/back navigation.
11. Log out and prove server revocation, protected detail/list inaccessible, back/reload does not reveal project content.

Additional UI negative/edge cases: duplicate normalized email, invalid credentials, expired/revoked session, bad/expired/used invitation, wrong-account accept, API outage, whitespace validation, unconfirmed POST draft retention, rapid duplicate submission, role-removal cancel/confirm/final-owner error, long names/emails, theme persistence, keyboard switcher/form/dialog paths, mobile focus restoration and overflow. Mobile Tab order must reach the new native workspace select and Account summary/sign-out before wrapping within the navigation dialog. Actual unavailable-network tests may use browser offline mode; do not fabricate server success.

Failed/logout-offline coverage must first create and display a real private project, then make the browser offline and initiate logout. Assert protected title/content is removed immediately and the UI reports that server revocation could not be confirmed. After reconnect, assert the real server session remains active when no logout request reached it; that outcome verifies honest local clearing, not successful server revocation.

## Mandatory negative evidence

The passing negative-path test creates real private Project A, then User B requests its exact UUID without membership. Assert actual 404 safe envelope, absent title/description, and independent DB row still present with all original fields. Browser B visiting that URL must show the safe unavailable state and no project content. A denied PATCH must leave the row unchanged as well.

The deliberately incorrect expectation is a separate experiment outside default pytest testpaths/browser suite. It must call the same real application/database, establish two real users/workspaces, confirm the protected row exists, then assert that the unauthorized GET should return 200. The application must remain unchanged; the experiment is expected to exit nonzero with a real `404 != 200` assertion failure. Preserve the actual output/exit code, do not use xfail or a wrapper that prints PASS, and do not count it as a passing test or a production-suite failure.

## Coverage diagram

```text
New backend paths                              Real-service tests              New/retained user flows
register -> validate/hash/unique/session        A01-A05,A12,A16               signup -> workspace create [E2E]
login -> DB limiter -> verify -> rotate         A06-A07,A12,A17-A19           sign in / safe failure [E2E]
session -> active/absent/expired/revoked         A08-A11,A22                   protected loading/logout [E2E]
CSRF -> origin + preauth/session comparison     A13-A16,A20                   stale request/draft retention [E2E]
workspaces -> create/list/member projection     W01-W03,W22                   create/switch/settings [E2E]
roles -> lock/recheck/last-owner                 W13-W18,W20                   role restrictions/confirmation [E2E]
invite -> authorize/hash/duplicate/revoke        W04,W08,W11-W12,W21           manual link/copy [E2E]
accept -> email/expiry/terminal/atomic commit    W05-W10,W19,W21               register B/explicit join [E2E]
projects -> membership CRUD/filter              P01-P10                       Chat/detail/reload/list [E2E]
migration -> preserve/restrict/repeat head       legacy steps 1-4,8            no implicit legacy access
operator -> dryrun/validate/lock/claim           legacy steps 5-7              explicit local operator only
DB/fetch failure -> rollback/safe 503            A21 + Stage01 outage          offline/error recovery [E2E]
wrong policy expectation -> real assertion      isolated experiment           expected nonzero, not main suite
```

All Stage 02 groups are requirements pending execution. Existing Stage 01 evidence is historical, not reused as proof that new branches passed. No LLM/prompt/provider code is in scope, so no AI eval suite applies.

## Verification order

1. Baseline existing scripts/verify.ps1 before source changes where possible; retain actual failure if environment blocks it.
2. Locked frontend/backend dependencies, Compose startup, development Alembic upgrade and preservation snapshot comparison.
3. Real backend tests, then Ruff check/format, schema drift, frontend strict typecheck/ESLint/production build.
4. Browser install if missing, then complete Playwright suite with one worker/no fake service/no retries masking failure.
5. Isolated incorrect-expectation experiment, record nonzero status separately; rerun passing suite if fixes followed.
6. Run extended scripts/verify.ps1 as the final orchestrated check. Do not run backend and E2E simultaneously.
7. Inspect final diff, current service readiness, actual screens in both themes and sanitized artifacts; document commands, counts, skipped/unrun scope and one exact stage verdict.

Every mandatory failure/skipped/unrun authorization/isolation/persistence check prevents VERIFIED. Browser emulation establishes the tested Chromium viewport scope only; no all-browser/native-device/penetration-test/production-security certification is inferred.

## Independent review follow-through

Source **codex+subagent**, same model family. One actual CLI static review completed with exit 0 and wrote [STAGE02_INDEPENDENT_REVIEW.md](STAGE02_INDEPENDENT_REVIEW.md); it did not execute application tests. Its four findings are dispositioned in STAGE02_PLAN.md. No separate per-dimension or cross-model grades were supplied or invented.

Observed test additions after that review:

| Finding | Actual test source added/amended | Required result |
|---|---|---|
| F1 logout content retention | teams.spec.ts, unconfirmed logout clears protected content without claiming server revocation | Real offline browser removes private content while acknowledging active server session after reconnect |
| F2 old API migration guard | test_legacy.py, actual socket listener guard check | Listener raises explicit stop-API error; closed port permits offline migration precondition |
| F3 proxy launch mismatch | README and Playwright Uvicorn commands include --no-proxy-headers | Supported actual service starts use the documented peer-IP policy |
| F4 concurrency/evidence | test_auth_workspaces.py barriers/bounded futures for owner/invite races; separate application-instance limiter race; member-revocation/project-write race; test_legacy.py mixed valid/invalid CLI batch | Correct real status/state under each interleaving; no duplicate member, zero owners, stale post-revocation write or partial legacy transfer |

Final complete-suite rerun is pending at this review update. No previous test totals are carried forward as evidence that these new assertions passed; final commands/counts belong in VERIFICATION.md after actual execution.
