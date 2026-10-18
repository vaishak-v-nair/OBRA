# ORBA Stage 02 implementation plan and review

Date: 2026-10-18. Authority: the owner's Stage 02 request. Status: reviewed implementation plan; execution results belong in VERIFICATION.md. Nothing in this document establishes that a feature or test has executed successfully.

## Intake and boundaries

The existing source is a working Stage 01 monorepo, not a blank project. Read AGENTS.md, README.md, ARCHITECTURE.md, ROADMAP.md, VERIFICATION.md, API routes/models/schemas/config/session code, migration 0001, test fixtures/cleanup, verification script, browser configuration, HTTP client, shell, theme tokens, ProjectForm and project pages. The source has one unscoped projects table, direct browser-to-API requests, local single-user labels and real isolated PostgreSQL tests. Preserve these behaviors while adding authenticated ownership.

Git inspection found main with no commits and no configured remote; all existing files are untracked. `git log -1 --oneline` failed because main has no commits. Consequently no historical diff or Git restore point can be claimed; the existing Stage 01 plan and records remain untouched. The new Stage 02 plan did not exist at intake. Base branch falls back to main. No stash entries or TODO/FIXME/HACK/XXX source findings were returned by the inspection.

UI scope is present: authentication screens, forms, workspace switcher, members and invitations. Developer experience scope is present: versioned APIs, operator command, migration/configuration and verification. The autoplan skill and phase methodology were read from disk. Its startup/logging helper is absent as established by the primary session; use degraded startup, no onboarding consent/telemetry or helper-generated consensus is claimed. Review source is **codex+subagent**: this delegated Codex review plus one integrated same-family Codex CLI outside-voice pass, which completed with exit 0 and produced [STAGE02_INDEPENDENT_REVIEW.md](STAGE02_INDEPENDENT_REVIEW.md). Claude is unavailable, so no cross-model agreement is inferred. CLI exit 0 establishes review execution, not passing application verification.

The owner explicitly requested implementation now. Routine choices below stay within that authorization; no public deployment, data reset, automatic legacy claim or later-stage feature is authorized. Artifact writes in this review are limited to this plan and STAGE02_TEST_PLAN.md, so external helper JSONL/CEO-plan copies are omitted and their task data is represented here. This is a documented tooling limitation, not evidence of application success.

## Stage 02 outcome

A real signed-in person can create a private workspace, create and reload a project, invite another signed-in person by a manually shared link, and apply server-enforced roles. Unrelated people cannot discover the private project's contents through lists, exact IDs, modifications or workspace APIs. Existing Stage 01 rows survive in an inaccessible legacy ownership state until a local operator explicitly claims selected projects.

## Phase 1: CEO review

### 0A. Premise challenge

1. **Stage 01 reported VERIFIED means it can be trusted without rerunning.** Reject that inference. The prior record has real reported evidence, but dependencies, ports and source may have changed. Run the baseline first and retain its actual output before altering contracts.
2. **Identity alone creates secure workspaces.** False unless every read and mutation uses current database membership. A browser-selected workspace is a scope request, never permission. Require reusable server authorization and independent database assertions.
3. **The first new user can own old projects.** Explicitly reject. Existing project ownership is unknowable. Migrate to a fixed restricted legacy workspace without memberships and require an operator-selected target owner/workspace/project set.
4. **Secure cookies imply complete CSRF protection.** False. Require a session-bound token in a custom header and exact allowed-Origin validation for every unsafe method, including login/register through a preauthentication token.
5. **A complete Stage 02 is a production security certification.** Reject. This stage deliberately lacks verified email, recovery, distributed edge controls and independent penetration testing. Label the delivered scope as local development authentication and permissions.
6. **Team membership requires real-time agents or presence.** Reject the dependency. Persisted human memberships, roles and manual invitations establish the necessary boundary without implementing Stage 03.

### 0B. What already exists

| Sub-problem | Existing source | Reuse decision |
|---|---|---|
| FastAPI lifecycle, database errors and sessions | apps/api/orba/main.py, db.py | Keep lifecycle/timeouts/sanitized errors; split route-specific behavior into focused modules as needed |
| Input validation and project persistence | schemas.py, models.py, project API | Preserve limits, deterministic status and database-backed commits; extend with authorized ownership |
| Schema authority | migrations/env.py, versions/0001_projects.py | Add forward Stage 02 revision 0febbe526f54; do not edit away 0001 history or create_all |
| Project creation UX | components/project-form.tsx | Keep one shared creation component, draft retention and synchronous duplicate-submit guard |
| Design palette/navigation | globals.css, shell.tsx, providers.tsx | Reuse semantic tokens, theme provider, mobile focus trap and skip link |
| Browser HTTP behavior | lib/api.ts | Keep timeout/no-store/errors; change base to same-origin, add CSRF/session-aware typed errors |
| Real integration setup | tests/conftest.py, scripts/prepare_tests.py | Extend guarded orba_test cleanup for new tables; never clean development rows |
| Browser/service setup | playwright.config.ts, tests/projects.spec.ts | Preserve desktop/mobile/tablet behavioral coverage; authenticate through real UI/API |
| Reproduction/check orchestration | scripts/verify.ps1 | Extend the existing sequential process with frozen installation and drift checks |

Style references: shared ProjectForm, native labeled controls and semantic palette provide small readable boundaries. Avoid expanding the single main.py into a monolith and avoid carrying its generic HTTP error code into a frontend that must distinguish 401, 403, 404, 409 and 429. No parallel authentication authority inside Next.js is needed.

### 0C. Dream state and delta

```text
CURRENT                         STAGE 02                       12-MONTH IDEAL
local unscoped projects  ---->  identity + explicit workspace   trusted human/AI collaboration
real DB/browser evidence       permissions + safe legacy       on the same boundaries
no auth authority              ownership + invitation evidence external services reviewed separately
```

This plan establishes identity and authorization primitives future features must reuse. It does not establish verified email ownership, enterprise identity, agents, presence, sandboxes, provider integrations or public deployment readiness. Future work cannot bypass the membership/session boundary merely because it runs in an agent.

### 0C-bis. Implementation alternatives

| Approach | Coverage | Effort (human / agent-assisted) | Risk | Pros | Cons / reuse |
|---|---:|---|---|---|---|
| A: Minimal extension in main.py | 10/10 if fully tested | 3-4 days / several hours | Medium | Few file moves; reuses current app/session directly | One file would mix CSRF, sessions, roles, invitations and project queries; security review becomes harder |
| B: Focused FastAPI services and routers | 10/10 | 4-5 days / several hours | Medium | Clear reusable auth/authorization; ordinary SQL transactions; preserves framework and UI | More source files and explicit integration seams; best fit for this request |
| C: External identity service / Next auth authority | Conflicts with required architecture | Not selected | High integration risk | Could outsource some password flows in a different product stage | Changes explicit authority, adds an external dependency and duplicates/redirects session semantics |

Recommendation: B. Explicit service boundaries make permissions readable while retaining the existing FastAPI/PostgreSQL architecture. A is viable but increases the chance that one route forgets a shared policy. C is rejected within this stage because it changes the user's stated authentication architecture rather than completing it.

### 0D. Mode and selective scope scan

Mode: SELECTIVE EXPANSION, constrained by the owner's exact Stage 02 scope. More than eight files and two entities are unavoidable because the requested data model itself contains users, sessions, workspaces, members and invitations. Keep the implementation ordinary: no policy language, background queue, Redis, event bus, generic service framework or second session layer.

The tempting larger vision is invitation-driven collaborative delivery with live presence and agents. Defer it because authorization must be proven before those actors are introduced. Five small improvements within the current blast radius earn inclusion: preserve invite intent across sign-in; use fragment invitation links; provide honest manual-sharing copy; distinguish session expiry from API outage; show the target workspace beside project creation. A public audit dashboard and automated email delivery are deferred. Sanitized operational security events and the existing verification record cover the current debugging requirement.

### 0E. Temporal interrogation

| Human implementation window | Agent-assisted work order | Decision settled before coding |
|---|---|---|
| Hour 1 | Foundations | Fixed legacy UUID; nonnull project workspace FK; nullable legacy creator; timestamp preservation; no default memberships |
| Hours 2-3 | Auth and permissions | Session cookie authority; token hashes; preauth/session CSRF; role matrix; consistent workspace lock order |
| Hours 4-5 | Frontend integration | Same-origin proxy; auth loading gate; validated selected workspace; invite fragment survives auth without leaking to request logs |
| Hours 6+ | Tests and polish | Sequential shared test DB; isolated migration test; concurrency tests; deliberate incorrect-authorization expectation isolated from passing suite |

### 0F. Confirmed review posture

Choose approach B and maintain complete requested behavioral coverage. Auto-decisions apply only to reversible implementation choices within the requested stage. There is no user challenge that changes the requested product scope. The stage verdict remains conditional on actual runtime verification.

### 1. Architecture

The before graph is Browser -> direct FastAPI -> unscoped Project -> PostgreSQL. The after graph routes browser API requests through Next.js to the same FastAPI authority; it introduces sessions and memberships ahead of every protected resource query. The proxy handles transport, not password verification, identity claims or authorization.

```text
Browser: AuthProvider -> session gate -> workspace state -> existing ProjectForm/pages
   | HttpOnly cookie automatically sent; CSRF header held only in memory
   v
Next.js /api/v1/* same-origin transport proxy (no second auth system)
   v
FastAPI: validation -> active server session -> membership/policy -> service transaction
                        |                          |
                  users + sessions          workspaces -> members -> projects
                                                  \-> invitations
   v
PostgreSQL: constraints/indexes + row/advisory transaction locks
Alembic 0001 -> Stage 02 head legacy backfill; local operator -> explicit legacy claim only
```

PostgreSQL is the main availability boundary; an outage fails protected operations with 503 while liveness remains independent. Argon2 work and connection-pool pressure become the first load constraints, so bound input, throttle before hashing and avoid background/in-memory authorization caches. Local rollout must stop the old API before applying ownership migration: serving the old unscoped routes after migration would expose all project rows. Do not roll back to the unauthenticated Stage 01 service while serving requests.

### 2. Error and rescue registry

| Codepath | Failure / exception | Rescue | User sees | Verification |
|---|---|---|---|---|
| Registration validation | RequestValidationError | Structured 422, no insert | Specific safe field guidance | Missing/empty/bounds/password/email cases and independent count |
| Duplicate normalized email | IntegrityError from unique constraint | Roll back, safe 409 | Account cannot be created with those details | Concurrent and normalized duplicate registration |
| Password verification | VerifyMismatchError / InvalidHashError | Generic credentials rejection; invalid stored hash logged by event type only | 401 generic sign-in error | Wrong password, absent account, safe response |
| Login attempts | Threshold reached | 429 + bounded retry information; do not hash password | Wait before retrying | Real DB attempt count and concurrent requests |
| Session lookup | Missing/expired/revoked/inactive identity | Structured 401 | Sign in again; clear protected state | DB expiry/revocation mutation + protected requests |
| CSRF / Origin | Missing/mismatched token or foreign/missing origin | Structured 403 before mutation | Refresh protection and deliberately retry | State unchanged; no automatic POST replay |
| Workspace policy | Missing membership / wrong role | 404 for hidden resource; 403 for known workspace role | Not found or action unavailable | Two-user exact-ID and role matrix |
| Membership update | Last owner / forbidden promotion | 409 or 403, transaction unchanged | Explain owner requirement | Independent owner-count assertion and concurrent attempts |
| Invitation acceptance | Unknown/mismatched/expired/used/revoked | Safe validation error; rollback | Invitation cannot be accepted | Token-hash lookup + database membership checks |
| Slug/membership uniqueness | IntegrityError | Expected conflict, no partial commit | Choose another slug / already a member | Unique constraint test |
| DB connectivity / statement/lock timeout | OperationalError / DBAPIError / SQLAlchemyError | Rollback, sanitized 503 | Service unavailable, draft retained | Real refused TCP endpoint and DB state |
| Browser fetch | TypeError / TimeoutError / AbortError | Typed error and preserved input | Unconfirmed save warning; deliberate retry only | Browser offline and interrupted request |
| Legacy claim | Invalid UUID/target/not-owner/nonlegacy row | CLI nonzero before commit | Explicit operator error | Before/after row values and all-or-nothing claim |

Do not log exception strings containing SQL/credentials, passwords, token values, raw invitation URLs or descriptions. Operational events may identify operation type and safe UUIDs with request correlation, but no sensitive submitted values. Programming defects remain defects, not successful fallback responses.

### 3. Security and threat model

The new attack surface contains public registration/login/CSRF endpoints and protected workspace/project/membership/invitation routes. Parameterized ORM statements and strict extra-field rejection prevent payload-supplied creator/session claims. Normalize and validate email consistently, keep passwords untrimmed and bounded, hash with maintained Argon2id defaults at least meeting current OWASP guidance, and store only SHA-256 hashes of high-entropy session/invitation secrets.

Threats with high impact are cross-workspace object references, stale-role writes, owner-removal races, login CSRF, invitation replay, token logging and legacy auto-claim. Mitigations are mandatory server membership queries, transaction locks/rechecks, session/preauth token plus exact Origin, atomic acceptance, fragment links and a restricted migration state. Email binding is a local identifier guarantee only: without email verification, registering an address does not prove mailbox ownership, and documentation must say so. Session identifiers live only in HttpOnly cookies; browser-readable storage may retain theme or selected workspace preference, never authoritative identity.

### 4. Data flow and interaction edge cases

```text
Register/login input -> validate -> throttle/password -> transaction -> rotated cookie + safe user
 missing/empty        -> 422       wrong/blocked        -> 401/429     no identity on failure
                                                               DB error -> rollback/503

Project draft + selected workspace -> active session -> lock/recheck membership -> insert -> detail
 missing/empty                     -> 422/401          viewer/nonmember -> 403/404
                                                               DB error -> rollback + preserved draft

Invite role/email -> lock workspace -> current inviter policy -> hash-only insert -> manual fragment link
 missing/empty   -> 422               denied -> 403/404          conflict/error -> no link/success

Authenticated token -> lookup -> workspace lock -> invitation lock/recheck -> member + accepted commit
 missing/empty -> 422  invalid/wrong email/expired/revoked/used -> safe denial, no partial membership

Legacy selected UUIDs + target owner/workspace -> local CLI validation -> locked all-or-nothing update
 missing/empty/unauthorized target/nonlegacy project -> nonzero; existing rows unchanged
```

New state machines are explicit:

```text
User: absent -> registered(active); inactive -> session rejection (no activation UI this stage)
Session: created(active) -> expired OR revoked; either terminal state -> rejected
Login/register success: prior presented session -> revoked; fresh random session -> active
Workspace: created -> exactly one creator Owner; later owners >= 1 at every committed mutation
Invitation: pending -> accepted OR revoked OR expired; terminal -> cannot accept again
Project: unowned Stage01 -> restricted legacy -> explicitly claimed authorized workspace
```

Double submits use existing synchronous UI guards and database constraints. Navigating away must not replay a write; abort stale GETs or discard their results. Session expiry removes protected content before showing sign-in, workspace switching clears prior list before fetching the next workspace, and back/forward navigation revalidates session and membership. Invite acceptance is explicit after sign-in, not triggered automatically by merely opening a link. No new background jobs exist.

### 5. Code quality

Reuse Settings, make_engine/get_session and existing response handling rather than introducing a second configuration/session stack. Extract named authentication, authorization and invitation functions with narrow transaction ownership; every route must call the same policy rather than repeating role string checks. Keep database constraints as a second guard and express admin restrictions as explicit cases rather than an obscure role-ranking abstraction.

The HTTP client should expose status/code without throwing away safe field errors, and mutations must not use a generic retry wrapper. One session provider and one workspace provider should orchestrate protected state, with contextual project views keyed by workspace so an old fetch cannot repopulate a new selection. Avoid helpers that only rename one line of ORM code or a universal CRUD framework that obscures authorization.

### 6. Test review

Preserve all Stage 01 project boundaries, timestamps, trimming, pagination, not-found, unavailable database, draft retention, duplicate-submit, theme and navigation checks while supplying real registered sessions/workspaces. The Stage 02 test artifact maps each new codepath to happy, rejection and concurrency evidence. No mocked membership/session objects, auth bypass or SQLite is permitted in integration/E2E.

Friday-shipping evidence is a full two-user browser invitation flow plus exact-UUID denial checked against independent DB state. Hostile QA adds forged ownership, revoked/expired sessions, CSRF mismatch, wrong-email invitation, admin-to-owner escalation, simultaneous last-owner operations and replayed acceptance. Chaos evidence uses actual API/DB unavailability and preserves the protected UI boundary. Time-sensitive cases update persisted expirations deterministically instead of sleeping; test suites remain sequential against guarded orba_test.

### 7. Performance

Index normalized email and secret hashes uniquely; membership lookup uses workspace/user uniqueness; projects use workspace/created_at/id for filtered pagination; invitation lists/lookup use workspace and hash/status/expiry as appropriate. Query members with joined user projection rather than one query per display name, and never cache a role in the browser or session as the authorization truth. Paginate project lists and bound invitation/member reads if collection size can grow.

Argon2 verification, lock waits and per-request session/membership queries are likely slow paths, but no p99 values are claimed without measurement. Throttle before expensive hashing; document PostgreSQL attempt-event retention and trusted-client-IP assumptions. At 10x local use the current shared DB pool and workspace serialization are measurable limits; 100x distributed deployment is outside this stage and requires independent capacity/security review.

### 8. Observability and debuggability

Use sanitized security event names for authentication success/failure/throttle, session revoke, invitation accept/reject and role/member changes, with UUID/request correlation where safe. Never print token-bearing links or raw request models in exception logs. Readiness must query the new required schema, not merely the old projects columns.

Operational diagnosis should distinguish database unavailable, invalid session, CSRF rejection, inaccessible workspace and duplicate/terminal invitation without revealing hidden resource contents to callers. VERIFICATION.md records command exit codes and real test counts; a local legacy claim command prints selected counts/IDs only after success and clear nonzero errors otherwise. Public monitoring, SIEM, metrics dashboards and alert infrastructure are deferred rather than represented by decorative UI badges.

### 9. Migration and rollout

Stage 02 revision 0febbe526f54 creates users/sessions/workspaces/members/invitations/attempt state, inserts one fixed is_legacy workspace without creator/members, adds nullable project FKs, backfills only workspace_id, then enforces nonnull ownership. Do not update title, description, status, IDs or timestamps. DB uniqueness, check constraints and FK indexes must match SQLAlchemy metadata so alembic check stays clean.

```text
Stop old local API -> record existing UUID/data snapshot -> apply head -> compare preserved fields
 -> run new API + same-origin web -> liveness/readiness -> real sign-up/workspace smoke -> full suite

Failure -> stop serving -> inspect migration transaction/version and preserved rows
 -> forward fix under backup/owner control; no automatic destructive downgrade/reset
```

Fresh/test schema and populated upgrade must both run. The existing 0001 migration is preserved for test setup; destructive test downgrade is allowed only inside guarded isolated test DB preparation. No public deployment, production flag rollout or automatic database volume removal is part of this stage.

### 10. Long-term trajectory

FastAPI-authoritative sessions and reusable workspace authorization provide a clear boundary for later tools, agents and integrations without implementing them now. Opaque sessions keep immediate revocation ordinary; no JWT claim invalidation cache or second frontend identity database is needed. Human-facing names and roles remain separate from future machine permissions.

Reversibility is 3/5: service extraction and UI choices are easy to revise, while persisted ownership and credential formats require careful migrations. Operational debt is explicit: unverified emails, no password recovery, no enterprise SSO, bounded PostgreSQL brute-force protection and local cookie defaults. Documentation must remove stale claims that Stage 02 is unauthorized while retaining Stage 01 historical evidence.

### 11. Design and UX

Identity and workspace belong in the shell, with the existing Chat experience remaining the primary work area. Show selected workspace, account identity and real role; do not keep the Stage 01 fake-looking static profile/local workspace labels once signed in. Viewers see clear read-only context, while backend enforcement remains mandatory.

```text
unknown session -> quiet loading gate -> signed out: sign in/sign up
                                 \-> signed in, no workspace: create workspace
                                  -> selected workspace: Chat / Projects
                                  -> settings: members -> invite -> manual link -> recipient accepts
expired/revoked session -> protected state cleared -> sign in with safe local return path
```

Every flow needs loading, empty, error and confirmed-success states; mutation success appears only after the real response. Preserve token colors and mobile focus behavior, support long workspace/email strings with wrapping, and add keyboard/focus checks for switcher, dialogs and destructive member confirmation. This review passes design details to Phase 2 rather than claiming visual correctness from a plan.

### CEO failure modes registry

| Codepath | Failure | Handled by plan | Test required | User impact | Safe operational evidence |
|---|---|---|---|---|---|
| Auth | DB write succeeds but network fails | Yes | UI draft/uncertain outcome | No fabricated sign-in/success | HTTP failure, no secrets |
| Session | Expired/revoked cookie | Yes | API + browser protected gate | Sign in required | Rejection event |
| Scope | Exact ID from unrelated workspace | Yes | GET/PATCH/member-list denial + DB intact | Hidden resource stays hidden | Status/code only |
| Membership | Two owners concurrently leave/demote | Yes | Real concurrent transactions | At least one Owner remains | Conflict response |
| Invitation | Two accepts use same token | Yes | Real concurrent accepts | One membership and one acceptance | Terminal status |
| Legacy | New user accesses restricted workspace | Yes | Migration + list/get isolation | No inherited ownership | DB snapshot and denial |
| UI | Old project fetch completes after switching | Yes | Browser delayed/stale state behavior | No cross-workspace visible row | Selected-scope assertions |
| Rollout | Old unscoped API survives migration | Yes | Process/source rollout check | Must stop old service | Local process inventory |

All eight are mandatory plan controls; implementation coverage remains unverified until executed. No registry row silently marks a missing test as passed.

### CEO completion summary

| Item | Outcome |
|---|---|
| Mode / approach | SELECTIVE EXPANSION / focused FastAPI services |
| System audit | Existing Stage 01 source; untracked tree/no history; local real DB tests |
| Architecture | Same-origin transport, single auth authority, reusable policy, safe rollout |
| Error map | 13 named codepaths, explicit safe rescue and verification |
| Security | Seven high-impact threat classes mapped to mandatory controls |
| Data / UX | Five data flows and six state machines; no background jobs |
| Quality | Avoid monolithic route growth and duplicated policy; retain shared ProjectForm |
| Tests | Integration/E2E/concurrency/migration/incorrect-expectation plan required |
| Performance | Indexes, bounded hashing and connection/lock assumptions documented |
| Observability | Sanitized event evidence and real schema readiness; no dashboard fiction |
| Deployment | Stop old API, preserve dev data, migrate, forward fix; no public deployment |
| Future | Reversibility 3/5; explicit security limitations |
| Design | Authentication gate, selected scope, role-aware states and mobile focus |
| Registries | Error/rescue and eight failure modes written |
| Lake score | Complete requested coverage selected in every coverage decision |
| Unresolved scope decisions | None; four independent CLI findings reconciled in the disposition record below |

### CEO voice availability and consensus

Source: codex+subagent, same model family. The CLI artifact explicitly reviewed CEO -> Design -> DX -> Engineering in one integrated static pass; it did not publish separate numerical dimension grades.

| Dimension | Delegated Codex review | Actual CLI outside voice | Agreement / coverage |
|---|---|---|---|
| Premises | Quarantine must survive real upgrade | F2 flags surviving old unscoped API | Corroborated risk; enforcement added |
| Right problem | Establish ownership before agents | No scope reframe proposed | Reviewed; no separate verdict supplied |
| Scope | Exact Stage 02 only | Four in-scope corrections | No scope change requested |
| Alternatives | Three compared | No alternative-specific verdict | Not independently rated |
| Market risk | Security trust outranks decorative breadth | No market-specific verdict | Not independently rated |
| Six-month trajectory | Reuse auth boundaries for later features | No trajectory-specific verdict | Not independently rated |

No absent grade or missing Claude voice is counted as confirmed consensus. This product stage does not need a competitive-market claim to justify its explicit safety boundary.

## Decision audit trail

| ID | Phase | Decision | Classification | Principle | Rationale | Rejected alternative |
|---|---|---|---|---|---|---|
| D01 | CEO | Preserve Stage 01 source and run baseline | Mechanical | Completeness | Prior evidence does not prove current runtime | Re-scaffold or assume prior verdict |
| D02 | CEO | Focused FastAPI services/routers, one auth authority | Taste | Explicit over clever | Security policy stays readable with same architecture | Monolithic main.py or external auth |
| D03 | CEO | Fixed inaccessible legacy workspace and explicit CLI claim | Mechanical | Completeness | Ownership cannot be inferred | First registrant auto-claim |
| D04 | CEO | Same-origin proxy with exact Origin plus session/preauth CSRF | Mechanical | Completeness | Cookie transport alone does not prevent unsafe requests | SameSite-only protection |
| D05 | CEO | Workspace-first lock/recheck for security mutations | Mechanical | Completeness | Serialize final-owner, role-revocation and invitation races | Check-then-write without lock |
| D06 | CEO | Fragment invitation links, explicit acceptance, manual sharing | Taste | Explicit over clever | Avoid access-log token leak and misleading email claims | Query tokens or automatic accept |
| D07 | CEO | Stop old API before migrating, no live auth rollback | Mechanical | Completeness | Old routes are unscoped | Serve Stage 01 after migration |
| D08 | CEO | Include scope label, expiry state and invite intent retention | Mechanical | Completeness | Avoid wrong-workspace writes and lost joining context | Silent reset or fake success |

## Phase 2: Design review

### Design scope, reference and tooling

This is an APP UI, not a marketing landing page. The seven dimensions below assess plan specificity, not the quality of an unrendered implementation. Initial completeness is 7/10: themes and broad screens are defined, but protected loading, invitation return paths and long/mobile member rows needed concrete rules. There is no DESIGN.md; globals.css, Shell, Button and ProjectForm provide the existing design authority the user explicitly asked to preserve.

The gstack designer binary was probed at repository-local, .Codex and .agents paths; every probe returned false. No visual mockup or vision check was executed and none is claimed. Existing Stage 01 layout and the wireframes below guide implementation; actual screenshots and keyboard checks remain required. No typography/site redesign is added under a generic skill preference because the owner's instruction is to preserve the existing visual design.

### Pass 1. Information architecture (7/10 -> 9/10 specification)

The shell must answer three things immediately: whose account is active, which workspace is selected, and what action is available in that workspace. Keep ORBA's sidebar and Chat-first main area; replace static Personal/Your workspace labels with database-backed names and an account control. Authentication pages use the same background/surface tokens but a restrained narrow form, not a new promotional hero or decorative card grid.

```text
Public sign-in/sign-up                  Signed-in workspace
+--------------------------------+     +----------------+------------------------------+
| orba.             theme toggle |     | orba.          | Selected workspace / page    |
| Sign in / Create account       |     | [workspace v]  |                              |
| Email        [____________]    |     | New project    | Chat composer OR project list |
| Password     [____________]    |     | Chat           | OR settings/members          |
| [Primary submit]               |     | Projects       |                              |
| Alternate auth link            |     | Workspaces     | One main action per area      |
| Safe field/server error        |     | ...            |                              |
+--------------------------------+     | Account / out  |                              |
                                       +----------------+------------------------------+
```

Workspaces opens a list/create screen; workspace settings displays name, slug, current role and members, then a distinct invitation area visible only to authorized roles. Project list and creation state the selected workspace near the title/composer. A direct project URL requires an active session and server-authorized lookup; choosing a workspace in the shell cannot grant access to that project.

### Pass 2. Interaction states (7/10 -> 9/10 specification)

| Feature | Loading | Empty | Error | Confirmed success | Partial / stale |
|---|---|---|---|---|---|
| Session gate | Quiet Checking session status; no protected children | Signed-out sign-in/sign-up | API unavailable, retry GET | Real account/shell | Expired/revoked session clears project/member data before sign-in |
| Sign up/sign in | Submit label changes; fields/submit locked | Labeled blank form and password guidance | Safe inline field/form error | Navigate only after actual session/me | Ambiguous response does not invent a signed-in identity; recheck me deliberately |
| Sign out | Button states Signing out | N/A | Error, protected client state cleared; explain server sign-out unconfirmed | Server revocation confirmed and sign-in shown | Another tab's revoked session fails its next protected request |
| Workspace list | Loading workspaces | Create your first workspace + one action | Retry list, account still identified | Real membership-derived list | Removed membership clears selected workspace |
| Switch workspace | Clear prior projects, show loading in current target scope | Target empty-state copy names workspace | Show scoped retry; never prior workspace items | Target list from API | Ignore old in-flight results using scope key/abort |
| Workspace create | Locked submit | Name/slug guidance | Validation/slug conflict, preserve values | Newly persisted owner workspace selected | No automatic POST replay after timeout |
| Project create | Existing Creating state | Existing composer | Preserve description/title and uncertain-save warning | Existing detail URL | Disable workspace change during a pending write or clearly bind captured target |
| Members | Loading members | At least creator owner; no fabricated teammates | Denied/not-found/503 distinguished safely | Real names/emails/roles | Re-fetch after authorized change; stale permission denied by server |
| Invitation create | Creating invitation, no link yet | Email + allowed role selector | Safe validation/denial | Actual link in copy field; Manual sharing, no email sent | Clipboard failure leaves link selectable with manual-copy guidance |
| Invitation accept | Checking account/session, then accepting after click | Missing fragment -> invalid invitation | Invalid/expired/used/wrong account cannot accept | Workspace joined after committed response | Sign-in retains fragment in a safe local return path; no automatic accept |
| Role change/remove | Confirm dialog names person/workspace/operation | N/A | Explain final-owner/permission denial | Refresh actual member list | Cancellation changes nothing; no optimistic destructive removal |

Keep async status messages announced with role=status and errors with role=alert without conflating the Next route announcer with a form error. Retain form labels after input, associate guidance/errors with fields and focus the first invalid input or concise error summary after submission. API outage must not look like invalid credentials or a nonexistent workspace.

### Pass 3. Journey and emotional arc (7/10 -> 9/10 specification)

| Step | Person does | Likely feeling | Specified support |
|---|---|---|---|
| 1 | Opens ORBA signed out | Wants to reach work | Obvious sign-in/sign-up; no false workspace identity |
| 2 | Registers | Trusts a credential form | Visible labels, brief policy, real pending/error behavior |
| 3 | Creates workspace | Needs a place for the idea | One primary create action, then selected workspace label |
| 4 | Describes a project | Wants continuity | Same Chat composer; real persisted detail/reload |
| 5 | Invites teammate | Needs confidence who gets access | Intended email and role visible; honest manual link label |
| 6 | Recipient opens link | Unsure about account/scope | Authenticate first, explicit Accept invitation, wrong-account guidance |
| 7 | Recipient views shared project | Understands belonging and limits | Workspace name and actual role; viewer read-only explanation |
| 8 | Owner changes access | Wants control without mistakes | Confirmation names target; final-owner safeguards explained |
| 9 | Logs out / session expires | Expects privacy | Protected state removed; back/reload cannot reveal content |

In the first five seconds the next action should be obvious. Within five minutes the person should have one durable project and understand manual sharing. The longer-term trust promise is that identity, permissions and persistence match actual server state, not decorative badges or optimistic success copy.

### Pass 4. Specificity and visual restraint (8/10 -> 9/10 specification)

Use utility copy such as Sign in, Create workspace, Invite teammate and Copy invitation link. New settings screens are labeled form sections and a member list/table, not stacks of decorative summary cards. Keep existing restrained radii, borders and spacing scale; do not add gradient illustrations, fake activity, security certification seals or progress bars.

The strongest visual anchor remains the primary task: the account form on auth screens and Chat composer in a selected workspace. Every other section must earn its space through a real action or real record. Preserve existing font/layout authority; any future typography revision requires a separate design scope, not a prerequisite for auth.

### Pass 5. Design-system alignment (8/10 -> 9/10 specification)

All new surfaces use background/surface/elevated/foreground/secondary/primary/border/danger/ring variables already defined in globals.css. Reuse the existing Button variants and native inputs/selects where possible; add shared labeled field styling rather than per-screen hardcoded colors. The theme toggle stays reachable on signed-out screens and in the authenticated shell.

Long email addresses, workspace names and slugs must wrap or truncate with an accessible full label rather than widen the viewport. Destructive removal uses the danger token plus explicit text, not color alone. Owner/Admin/Member/Viewer labels communicate permissions; no new visual language implies an unavailable real-time collaboration service.

### Pass 6. Responsive and accessibility (7/10 -> 9/10 specification)

Desktop retains the existing sidebar/main split and a readable settings width. Tablet must be assessed at the actual preset width rather than assuming its navigation is mobile. At <=720px keep the existing focus-trapped navigation overlay, put workspace/account controls within it, and show member entries in readable wrapped rows with per-member actions placed next to their labels instead of overflowing a wide table.

Auth forms fit narrow screens with visible labels and 16px input text; controls have at least 44px touch targets where mobile. Keyboard paths cover skip link, theme, workspace selector, account menu, invite form and role/removal confirmation. Prefer native select semantics; dialogs need a label, initial focus, Escape/cancel, focus containment and restoration. Alert/status content must remain understandable in both palettes, and actual contrast/focus/overflow checks belong in verification rather than an unsupported WCAG claim.

### Pass 7. Resolved design ambiguities (6/10 -> 9/10 specification)

| Ambiguity | Decision | Why |
|---|---|---|
| Landing after new registration | Workspace list/create when no membership exists | Avoid arbitrary default workspace or legacy ownership |
| Invite intent through auth | Safe same-origin return path containing fragment; preserve only as needed | No lost token and no open redirect |
| Empty viewer workspace | Read-only context and Ask an Owner/Admin for write access guidance | Do not offer an operation known to be forbidden |
| Workspace settings reachability | Workspaces list and selected-workspace settings action | Discoverable without changing main Chat navigation |
| Removal confirmation | Name target and workspace; Cancel is non-destructive default | Prevent accidental membership loss |
| Unexpected 401 | Clear all protected state, then route to sign-in | No content while authority is unknown |
| Unexpected 403/404 | Safe action-denied/not-found state; revalidate membership | Do not reveal existence of unrelated resource |
| Role restrictions | Hide/disable inappropriate actions with concise real explanation | Server remains authoritative, UI avoids misleading choices |

No unresolved taste choice requires changing the owner's scope. Workspace creation may be a page rather than a modal; a page is recommended because it gives reliable mobile/error navigation and avoids adding dialog infrastructure. This is a reversible presentation choice.

### Design litmus scorecard

| Check | Delegated Codex specification review | Actual CLI outside voice | Consensus |
|---|---|---|---|
| ORBA clear on first screen | Existing brand retained | Litmus not separately rated | N/A |
| One visual anchor | Form/composer | Litmus not separately rated | N/A |
| Headlines scan | Explicit task/area names | Litmus not separately rated | N/A |
| One job per section | Account/workspace/members/invites separated | Litmus not separately rated | N/A |
| Cards necessary | Clickable projects retained; no settings mosaic | Litmus not separately rated | N/A |
| Motion useful | Existing reduced-motion-safe feedback only | Litmus not separately rated | N/A |
| Premium without shadows | Hierarchy, spacing and tokens carry structure | Litmus not separately rated | N/A |

Source: codex+subagent, same family; no Claude voice or independent visual grading is available. The actual CLI Design finding F1 concerned failed logout retaining protected content. Source now clears identity/workspace state before the network request and separately warns that server revocation is unconfirmed; the added real offline browser test must execute in the final suite. This is a behavioral disposition, not an invented 7/7 visual consensus.

Hard-rejection evaluation found no newly proposed marketing grid, busy imagery, carousel, repeated mood sections or decorative widget mosaic. The existing Stage 01 composition remains user-authorized visual context. Mockups and runtime screenshot evaluation are unavailable at plan time, so design scores remain specifications, not visual certification.

### Design completion and decisions

All seven dimensions were evaluated. Nine interaction areas plus their partial states are specified, the journey includes nine steps, and the shell/auth/mobile wireframes extend the existing palette. Final specification quality is 9/10; actual browser rendering, focus and contrast require execution. No design debt is hidden as a later-stage TODO: required accessibility and state handling stay within Stage 02.

| ID | Phase | Decision | Classification | Principle | Rationale | Rejected alternative |
|---|---|---|---|---|---|---|
| D09 | Design | Dedicated workspace-create page is default | Taste | Explicit over clever | Stable mobile/error navigation without new dialog stack | Modal-only creation |
| D10 | Design | Session gate renders before protected children | Mechanical | Completeness | Unknown identity cannot display cached project content | Render then redirect |
| D11 | Design | Clear scoped data immediately on switch/revocation | Mechanical | Completeness | Prevent stale project/member visibility | Leave old results under new scope |
| D12 | Design | Reuse token palette, font and shell authority | Mechanical | DRY | Preserve owner's existing product visual language | Opportunistic redesign |

## Phase 2.5: Developer experience review

### Product, persona and mode

Primary product type: local developer workspace with API/service, operator CLI and documentation surfaces. Mode: DX POLISH. The README explicitly targets a local single-user foundation with PowerShell, uv, pnpm and Docker, so the primary persona is the owner or a full-stack contributor extending this monorepo, not an anonymous SaaS customer or external SDK consumer. They expect one reproducible path, preserved local data, typed API calls, meaningful failures and a verification command whose result can be trusted.

### Developer perspective

I open README.md and see “ORBA · Stage 01.” That tells me what used to work, but I am here to add authentication and need to know whether the new stage is implemented or merely planned. The prerequisites list Node, pnpm, Python, uv and Docker, and the PowerShell setup commands are copyable. I appreciate that environment copies are optional and I am told not to overwrite existing files. I also notice that NEXT_PUBLIC_API_URL sends my browser directly to a different local port, which no longer matches the planned cookie architecture. I need the new server-only API_URL name, the correct localhost origin and a warning that cookie behavior depends on HTTPS configuration.

Once I start the two processes, I want to register a real user, create a workspace and reload a project before reading a long architecture document. Existing projects should not disappear, but I should not be allowed to inherit them by registering first. I need a separate operator command with explicit project IDs and an owner target, plus an explanation of why no legacy records appear in my account. When a test fails I want its actual command and response, not a “PASS” wrapper. The existing sequential verification script is the right home for the new checks. Before changing code, I need to know that pytest and Playwright share the test database so I do not accidentally run them together.

This is an evidence-grounded roleplay, not an observed timed usability session.

### Competitive/reference benchmark and TTHW

| Reference | Observed onboarding choice | Time claim | Source |
|---|---|---|---|
| Supabase local development | Docker-compatible runtime plus start/migration workflow | No measured TTHW available from reviewed docs | [Official local workflow](https://supabase.com/docs/guides/local-development/cli-workflows) |
| Next.js | Explicit install/start commands and App Router guide | No measured TTHW available from reviewed docs | [Official installation](https://nextjs.org/docs/app/getting-started/installation) |
| FastAPI | Small first-steps app and development server entry | No measured TTHW available from reviewed docs | [Official first steps](https://fastapi.tiangolo.com/tutorial/first-steps/) |
| ORBA | Existing locked install + migration + two processes + real browser form | Not measured; cold dependency/container downloads dominate | Current README and verification script |

Do not invent competitor times or claim an under-five-minute cold install. Target: under five minutes from already-installed prerequisites/dependencies and available local DB image to a signed-in persisted project. Record actual command duration and prerequisites in verification; unmeasured targets remain targets. Deliver the meaningful moment through the existing application: register, create workspace, create Chat project, reload, see the same UUID. Hosted playgrounds, demo videos, auto-seeded accounts and fake output do not solve this local reproducibility goal.

### Nine-stage developer journey

| Stage | Developer action | Current friction / required resolution | Plan state |
|---|---|---|---|
| 1. Discover | Read README opening | Stale Stage 01 heading/auth exclusions | Update current stage and link preserved historical record |
| 2. Evaluate | Read architecture and limitations | Need exact auth/role/legacy guarantees | Add explicit scope and current security limits |
| 3. Install | Frozen pnpm/uv install; start Compose | Global pnpm unavailable on observed machine | Retain exact npm exec launcher; do not alter global tooling |
| 4. Hello world | Start API/web, register, workspace, project | New cookie proxy/env bootstrap | One golden PowerShell path, actual response expectations |
| 5. Integrate | Extend project/workspace client | Authentication/CSRF contract changed | Typed client and one complete authenticated API example |
| 6. Debug | Run failing request/readiness/checks | Generic old HTTP code obscures 401/403/409/429 | Status/code preserving errors and sanitized diagnostics |
| 7. Upgrade | Apply Stage 02 head to populated local DB | Ownership cannot be inferred | Stop old API, preserve fields, no-reset guide |
| 8. Scale | Consider multiple API workers/users | PostgreSQL limiter/locks have bounds | Document concurrency/IP/retention assumptions; no distributed claim |
| 9. Migrate/operate | Explicitly claim selected legacy rows | No automatic trusted owner | Local CLI, explicit IDs/owner/target; no public claim endpoint |

### First-time contributor confusion report

```text
T+0:00 Read current README; Stage 01 is clear, new scope is absent.
T+0:30 Find install commands; global pnpm fallback is documented and useful.
T+1:00 Inspect environment examples; public direct API URL must become server-only proxy target.
T+2:00 Read tests; pytest and E2E share guarded orba_test, so run sequentially.
T+3:00 Ask where old projects went; restricted legacy state and explicit operator claim must explain it.
```

These timestamps organize a simulation and are not measured execution times. Resolve every listed confusion point within the requested docs/config/testing work.

### Pass 1. Getting started (6/10 -> target 8/10)

Keep the existing golden path: locked installs and Compose/migration, two terminal commands, then a real browser signup/workspace/project flow. With prerequisites installed, no provider keys, credit card, email delivery or hosted account is needed. Health responses are useful diagnostics, but the first meaningful result is persisted authenticated project data, not a server “hello” or fabricated seed record.

README must list exact ports, startup commands, same-origin configuration and useful expected results without promising unmeasured times. Reproduction should not require reading architecture first. A one-command universal installer would add new platform/tooling scope; the existing verification orchestration is extended instead.

### Pass 2. API and operator ergonomics (7/10 -> target 9/10)

Retain /api/v1/projects and UUID detail conventions; add workspace_id explicitly to creation/listing and document why unauthenticated calls now return 401. Auth uses register/login/logout/me/csrf consistently, workspace resources are plural, and member mutations identify user UUIDs. The frontend client handles cookie transport and CSRF once rather than every form learning security details.

Operator claiming should expose ordinary named flags for target workspace, owner and repeated explicit project UUIDs, with --help, nonzero error status and all-or-nothing behavior. It is intentionally unavailable over HTTP. Never automatically retry a project, invite, role-change or claim write; describe the current uncertain-response limitation rather than implying idempotency. OpenAPI and typed TypeScript responses provide discoverability without an unnecessary SDK package.

### Pass 3. Errors and debugging (7/10 -> target 9/10)

Three specific traces need improved actionability. The existing database error says “Database unavailable. Try again shortly.” Preserve that safe public response; README diagnostics should direct the operator to Compose health, DATABASE_URL and Alembic readiness without exposing credentials. The old generic HTTP envelope must distinguish session-required (sign in again), action-forbidden (current role lacks permission), hidden resource-not-found and login-throttled (wait and retry).

CSRF failures must explain that request protection could not be validated and a refresh is needed, while preserving the draft and requiring deliberate resubmission. Invitation errors should state that the link cannot be accepted and suggest the inviter or correct account, without returning raw tokens or unrelated workspace details. Do not follow the skill's illustrative “actual submitted values” advice for passwords, tokens, PII or private resource names; safe structured code/status plus documentation is the correct evidence here.

### Pass 4. Documentation and learning (7/10 -> target 9/10)

README is the golden path, ARCHITECTURE explains cookie/CSRF/session/workspace policy, ROADMAP separates current scope from future stages, AGENTS preserves verification/security rules, and VERIFICATION records actual commands and bounded evidence. Include a complete authenticated API example with cookie handling and CSRF flow plus the exact operator claim command. Put the role matrix, manual invitation wording and no-email-verification limitation within easy reach of setup instructions.

Preserve the Stage 01 historical record instead of rewriting its 15/30 results as Stage 02 evidence. Update obsolete environment names and exact expected API contracts together with the frontend/tests. Do not add a separate docs site, marketing tutorial or fabricated interactive playground; existing local OpenAPI and actual UI are enough for this stage.

### Pass 5. Upgrade and legacy migration (7/10 -> target 9/10)

The deliberate breaking contract is authentication plus explicit authorized workspace scope for project create/list. Document it as Stage 02 behavior; do not silently preserve unauthenticated success or create an auth bypass for old tests. A forward Alembic migration upgrades existing rows without deleting or reidentifying them, and the operator command is the only supported legacy handoff.

Provide separate fresh-install and populated-upgrade instructions: stop old API, snapshot/backup, migrate, start new services, verify readiness/ownership preservation, then explicitly claim only chosen rows. Do not run downgrade/reset or automatically assign a creator to records whose authorship is unknown. Full preservation evidence must compare all original Stage 01 fields, not just row counts.

### Pass 6. Environment and tooling (7/10 -> target 8/10)

Keep uv/pnpm lockfiles and the established Windows PowerShell verification entry point. Extend scripts/verify.ps1 with frontend frozen install, backend locked sync, development upgrade, schema drift, backend/lint/typecheck/build and sequential real browser tests. Test services keep dedicated loopback ports and reuseExistingServer=false, and cleanup still validates both database and role before clearing any table.

Use server-only API_URL for Next's proxy target and document WEB_ORIGIN, cookie secure flag/session lifetime and invitation expiry. Local defaults may remain loopback HTTP with Secure=false; HTTPS-enabled configurations must use Secure cookies and no development bypass. Verified Windows behavior does not establish Linux/macOS/ARM/remote-CI compatibility; record unrun platforms honestly.

### Pass 7. Community and ecosystem (6/10, intentionally bounded)

The repository currently has no remote, published package or demonstrated contributor community. Do not invent a monitored support channel, public issue response SLA, open-source license decision or plugin ecosystem. The contribution surface at this stage is the local monorepo, AGENTS.md rules, reproducible setup and meaningful tests.

No required Stage 02 capability depends on launching a public community. Preserve standard FastAPI/Next/OpenAPI conventions so contributors can inspect code with ordinary tools, while leaving pricing, public support, external messaging and extension installation for separately authorized work. This bounded score is not a mandatory functionality gap or a request to expand scope.

### Pass 8. Measurement and feedback (6/10 -> target 8/10)

Record command exit status, real test counts, skipped tests, cold/warm prerequisites and runtime scope in VERIFICATION.md. Capture command output through a reliable mechanism because the prior record states that PowerShell Start-Transcript omitted native stdout in this environment. A script exiting 0 is useful only when each mandatory command and meaningful assertion actually executes.

Measure the first real authenticated persisted-project flow if reporting a setup time, and label any unmeasured under-five-minute goal explicitly. Browser/E2E failures and isolated expected-failure output are useful friction evidence; no telemetry, analytics service, NPS widget or fabricated dashboard is required. The next reviewer should compare implementation evidence with these documented targets rather than replacing tests with screenshots.

### DX scorecard

| Dimension | Initial specification | Amended target | Remaining evidence |
|---|---:|---:|---|
| Getting started | 6 | 8 | Run documented path; no cold-install timing claim |
| API/CLI | 7 | 9 | Execute actual CSRF/cookie requests and claim CLI |
| Error messages | 7 | 9 | Assert real safe envelopes and UI messages |
| Documentation | 7 | 9 | Reproduction review after implementation |
| Upgrade path | 7 | 9 | Real 0001 populated migration + preserved UUID/fields |
| Dev environment | 7 | 8 | Full existing script; cross-platform still unverified |
| Community | 6 | 6 | Local-only, no public ecosystem claim |
| Measurement | 6 | 8 | Actual exit/count evidence, no invented duration |
| Overall | 6.6 | 8.3 | Specification quality; execution still pending |

TTHW: not measured -> target <5 minutes with installed prerequisites/dependencies and local images. Competitive rank cannot be measured before a timed run. Meaningful moment: a reloaded authenticated project with unchanged UUID through the existing UI. Tooling exceptions and public ecosystem scope are explicit, not hidden failures.

### DX implementation checklist

- [ ] README current-stage description and exact golden install/start/verify path.
- [ ] Copyable npm-based pnpm launcher retained; no global tool repair required.
- [ ] Same-origin API_URL and complete cookie/CSRF configuration documented.
- [ ] Real signup -> workspace -> project -> reload flow executed.
- [ ] Structured 401/403/404/409/422/429/503 cases have safe guidance.
- [ ] Explicit workspace project contract documented in typed client and API example.
- [ ] Populated forward migration and operator-only selected-project claim demonstrated.
- [ ] Existing verify.ps1 extended; frozen install/drift checks execute.
- [ ] Real backend/E2E suite runs sequentially with guarded test cleanup.
- [ ] Native stdout, command exits, test counts and isolated expected-failure output retained.
- [ ] No production-security, all-platform, public-community or measured-TTHW claim without evidence.

### DX voice availability and consensus

| Dimension | Delegated Codex review | Actual CLI outside voice | Agreement / coverage |
|---|---|---|---|
| Getting started <5 min | Target only, not measured | No timing measurement supplied | Not measured |
| Naming | Versioned conventions retained | No naming-specific verdict | Not independently rated |
| Errors actionable | Safe recovery specified | F1 requires honest unconfirmed-logout state | Corroborated and amended |
| Docs complete | Exact required sections mapped | F2/F3 expose migration/startup mismatch | Corrections observed in README/source |
| Upgrade safe | Stop old API before migration | F2 requires enforced stop rather than prose alone | Corroborated; local guard added |
| Environment friction | Explicit local proxy/IP boundary | F3 README omitted --no-proxy-headers | Startup instructions corrected |

Source: codex+subagent, same family. The integrated CLI pass ran with exit 0 and supplied the findings above; it did not measure TTHW or certify cross-platform startup. Claude and cross-model consensus remain unavailable.

### DX decisions

| ID | Phase | Decision | Classification | Principle | Rationale | Rejected alternative |
|---|---|---|---|---|---|---|
| D13 | DX | DX POLISH, local full-stack contributor persona | Mechanical | Pragmatic | Matches README and requested local scope | Hosted SaaS onboarding expansion |
| D14 | DX | <5min warm-start target, no claimed cold-start benchmark | Mechanical | Completeness | Timing must be observed, dependencies vary | Invented competitor/setup durations |
| D15 | DX | Extend existing verify.ps1 and record native output correctly | Mechanical | DRY | One repeatable check path, truthful evidence | Unrelated verifier or green print driver |
| D16 | DX | Document project API auth/scope break and explicit legacy path | Mechanical | Explicit over clever | Users and contributors can upgrade safely | Silent bypass for old consumers |

## Phase 3: Engineering review of amended plan

### Step 0. Scope and source check

Read the actual Stage 01 routes/models/test fixtures/client/pages and, as implementation became available, the Stage 02 security.py, auth.py, workspaces.py, schemas, models, migration and claim command. This is a plan/security review, not a declaration those newly written files are verified. The five new entities and required screens justify touching more than eight files; no scope reduction is recommended, and no new infrastructure is necessary.

Reuse SQLAlchemy Session transactions, PostgreSQL constraints/locks, Argon2's maintained library and native cookie/header controls. The implemented Next transport proxy preserves separate Set-Cookie headers and forwards only the necessary request headers; it contains no authentication decisions. The existing meaningful pytest and Playwright frameworks are detected in pyproject.toml/playwright.config.ts and actual tests, not inferred from test filenames alone. There are no new publishable binary/package/container artifacts; public distribution/CI publishing is deferred, and the operator command runs from the existing Python environment.

Verified source motivations:

| Finding | Confidence | Evidence and required response |
|---|---:|---|
| Old API cannot remain live after ownership migration | 10/10 | Original main.py returned `select(Project).order_by(...)` and `session.get(Project, project_id)` without membership; stop old process before migration and never serve it as auth rollback |
| Same-origin client/proxy must replace direct origin | 10/10 | Original api.ts used `NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"`; new client must use relative /api and server-only API_URL |
| Test fixtures must preserve real behavior while adding auth | 10/10 | Original tests call real `/api/v1/projects`; extend fixtures with actual register/workspace endpoints, not an injected identity |
| Verification script lacks frozen frontend/drift checks | 10/10 at intake | Original verify.ps1 ran Compose/uv/upgrade/pytest/Ruff and four frontend tasks; add locked pnpm installation and alembic check |
| Uvicorn proxy default can undermine claimed peer-IP trust | 10/10 | Installed uvicorn/config.py:225 says `proxy_headers: bool = True`; :363 defaults `FORWARDED_ALLOW_IPS` to `127.0.0.1,::1`; middleware reads `x-forwarded-for`. Use --no-proxy-headers for supported local startup or explicitly sanitize trusted forwarding |
| Security mutation events need safe diagnostics | 9/10 at source read | Newly read auth/workspace paths committed changes without event logs, while main.py logged only DB exception type; add sanitized operation/UUID/status events, no secrets |
| Non-ASCII CSRF header triggers an unhandled exception | 10/10 | security.py calls `secrets.compare_digest(expected, supplied)` on strings; actual guard execution with raw 0xff header raised `TypeError: comparing strings with non-ASCII characters is not supported`. Reject malformed token encoding as 403 and test it |
| Mobile account action is excluded by focus trap | 9/10 | Shell's `querySelectorAll('a[href], button:not([disabled])')` omits the new Account summary and workspace select; Settings can become the last recognized control, wrapping Tab before Account. Include visible native focusables and test keyboard sign-out |

Speculative load p99, account takeover prevalence or public deployment readiness are not promoted as verified findings. Current dependency guidance was checked against primary OWASP/PostgreSQL documentation; this is a design reference, not a penetration test.

### Section 1. Architecture and contracts

```text
apps/web
  theme + Shell (existing)              auth session state -> signed-in gate
  ProjectForm (existing)                selected workspace -> keyed scoped pages
            \                                  /
             typed relative HTTP + CSRF headers
                              |
                   Next same-origin API transport proxy
                              |
apps/api                     FastAPI
 config -> DB/session -> active identity -> resource membership -> allowed action
                           |                    |
                       auth routes        project/workspace routes
                           |                    |
                    token hashes        locked role/invite mutations
                              \       /
                         PostgreSQL/Alembic
                   users -> sessions; workspace -> members/projects/invitations
                                      ^
                            explicit local legacy CLI
```

The Next process is a transport dependency, not a new credential authority. FastAPI alone verifies password, session, CSRF, membership and role. Client-selected workspace IDs and copied invitation links remain untrusted inputs. Database availability gates all authorization decisions; no “allow while DB offline” behavior is permitted.

| Route family | Caller | Scope / mutation policy | Success / refusal contract |
|---|---|---|---|
| register/login | Public with valid preauth or session-bound CSRF + exact Origin | Normalize email; hash/verify; DB limiter; rotate session | 201/200; 422/409/401/429/403/503 |
| auth/me | Valid active server session | Return safe current user only | 200;401/503 |
| auth/csrf | Browser preauth/session context | Return token bound to current context, no-store | 200;503 if session lookup DB unavailable |
| auth/logout | Active session + CSRF/Origin | Revoke current record, clear cookie | 204;401/403/503 |
| workspaces create/list | Active session; CSRF for create | Creator + Owner atomic; lists memberships only | 201/200;401/422/403/503 |
| workspace detail/members | Active workspace member | Hidden missing/unrelated/legacy workspace | 200;404/401/503 |
| invitation create/list/revoke | Owner/Admin; CSRF for mutations | Admin grants/manages only permitted lower roles; workspace-first lock | 201/200/204;403/404/409/422/503 |
| invitation accept | Active intended user + CSRF | Workspace then invitation lock; fresh inviter/expiry/terminal/email/member checks | 200;400/409/422/401/403/503 |
| member PATCH/DELETE | Owner or limited Admin + CSRF | Fresh caller/target roles; prevent zero owners; no Admin promotion to Owner | 200/204;403/404/409/422/503 |
| project create/PATCH | Owner/Admin/Member + CSRF | Authorized workspace lock/recheck, server creator, no ownership edit fields | 201/200;403/404/422/401/503 |
| project list/get | Any current member | Explicit list scope; joined membership for exact UUID; no legacy visibility | 200;404/422/401/503 |

Permissions resolve from current membership, not long-lived cookie claims. Workspace lock serialization applies to membership/invitation operations and project writes so a completed role revocation cannot be bypassed by a stale pre-lock check. Consistent lock order is workspace -> invitation/member/project; login limiter advisory keys are sorted before acquisition. A timeout is a visible failed operation with rollback, not an implicit retry.

The supported local server command must disable Uvicorn proxy-header trust if rate_limit treats request.client.host as actual peer. If a future proxy is introduced, sanitize headers at that trusted boundary and document the shared-IP budget. HTTPS cookie mode must fail configuration if Secure is false, and exact-origin configuration should reject path/query/fragment/userinfo rather than pretending those are valid browser origins.

### Section 2. Code quality and state ownership

The extracted auth/security/workspace modules fit the accepted focused design. Keep business decisions in FastAPI; Next components coordinate forms/state and must not infer authorization from localStorage. Use one dependency for current session, one membership/policy service and named helpers for role-management rules; do not duplicate unscoped object fetches in new routes.

The source now implements pending-invitation uniqueness and revalidates inviter membership/role at acceptance, which avoids stale privilege grants. Operator claiming uses explicit UUIDs/dry-run and must retain original timestamps; authorship semantics after claim must be documented rather than silently suggesting the selected Owner originally wrote the Stage 01 description. Password normalization must remain separate from email normalization.

New mutation errors should be differentiated enough for safe client recovery without leaking private resource existence. Do not catch all exceptions as success, print raw HTTP bodies containing secrets, or use tests that assert only HTTP 200. Update the old architecture diagram's direct-browser/API arrow and old roadmap's “no Stage 02 authorization” statement in the implementation documentation, while preserving historical Stage 01 evidence.

### Section 3. Tests and branch coverage

The actual preexisting tests use migrated PostgreSQL and independent SQLAlchemy reads for persistence. Preserve those strengths: a 201 alone does not prove creator/workspace ownership, and a 404 alone does not prove a denied write left data unchanged. Stage02_TEST_PLAN.md is written as the concrete artifact, with existing coverage preservation, all auth/role/invitation/isolation/migration branches, browser flows and a deliberately incorrect isolated expectation.

```text
Entry / branch                                   Planned coverage type and artifact IDs
register: valid/invalid/normalized duplicate      PostgreSQL integration A01-A05 + UI signup
login: good/bad/missing/throttled/concurrent      integration A06-A07,A12,A17-A19 + UI sign-in
session: active/missing/expired/revoked/rotated    integration A08-A12 + protected browser gate
CSRF: preauth/session/missing/mismatch/origin      integration A13-A16,A20 + real browser cookies
workspace: atomic creator-owner/list/hidden       integration W01-W03,W22 + create/switch E2E
roles: each role/target/final owner/concurrency   integration W13-W18,W20 + Viewer/Member E2E
invite: create/duplicate/revoke/manual link       integration W04,W08,W11-W12 + actual copied link
accept: email/time/state/duplicate/concurrency    integration W05-W10,W19,W21 + two-context joining
projects: create/list/get/PATCH/forged scope       Stage01 regressions + P01-P10 + Chat reload/list
legacy: populated upgrade/hidden/repeat head     actual Alembic + snapshot assertions
claim: dryrun/apply/bad target/partial/replay      actual operator CLI + independent DB assertions
upstream failure: refused DB/network timeout     real driver/offline browser, no fake response
incorrect policy: unauthorized should be 200     isolated real assertion -> expected nonzero
```

Every new group is a coverage obligation; none is marked TESTED before execution. Concurrent owner/acceptance/limiter cases need separate actual connections and bounded barriers/timeouts, not sequential requests labeled as races. Deterministically update persisted expiry/revocation for clock edges. E2E uses real user contexts and same-origin cookies, with no storage-injected identity or fulfilled fake API response.

No new AI/provider/prompt/agent path exists, so no LLM eval applies. The main suite must stay green with zero required skips. The isolated wrong-expectation experiment is deliberately red and must remain outside default test collection; record its nonzero exit and actual assertion, never alter application policy to make it pass.

### Section 4. Performance and operational limits

Uniqueness/indexes support email/session/invitation lookup and membership filtering. Project lists remain bounded/paginated, while the model should support an indexed workspace/created_at/id query as data grows. Member projection should join User once, and invitation lists must omit secret fields even if collection size increases.

Argon2 and DB lock waits dominate new expensive work. Limit password/request size and count login attempts before expensive hashing. PostgreSQL attempt buckets serialize application instances, but this is a local basic restriction, not a claim of distributed edge abuse protection; successful attempts, registration consumption, shared proxy IP budget and event cleanup need documentation. Do not cache sessions/roles in a way that delays revocation, and do not invent latency numbers or load-test results.

### Engineering failure and critical-gap assessment

| Failure mode | Required handling | Required test | Critical-gap verdict at plan time |
|---|---|---|---|
| Password/email invalid | Safe 422, no insert | A02-A05 | Specified; execution pending |
| DB fails during login/create/invite | Rollback, sanitized 503, no false success | A21 + browser outage | Specified; execution pending |
| Stale/replayed cookie | DB active session check | A09-A12 | Specified; execution pending |
| CSRF/Origin forged | 403 before mutation | A13-A16 | Specified; execution pending |
| Login workers race | Sorted advisory locks, persistent counts | A18-A19 | Specified; execution pending |
| Workspace ID/UUID guessed | Hidden 404, no read/write | P02-P05,W02-W03 | Specified; execution pending |
| Final owners race | Lock and count under transaction | W17-W18 | Specified; execution pending |
| Invitation reused/concurrent | Locked one-time state + unique membership | W09,W19 | Specified; execution pending |
| Inviter loses role | Recheck current inviter privilege | W21 | Specified; execution pending |
| Legacy ownership unknown | Restricted workspace/no memberships | Legacy snapshot + P10 | Specified; execution pending |
| Claim partly invalid | All-or-nothing operator validation | Legacy step 7 | Specified; execution pending |
| Old API or stale frontend data leaks | Stop old server; session/scope gate | Rollout inspection + browser switch/logout | Specified; execution pending |

There are no silent/unhandled failures accepted by this plan. Any missing implemented handler/test becomes a blocking acceptance gap until executed and resolved. This is not a statement that all code branches are covered already.

### Engineering completion summary and voice availability

| Item | Result |
|---|---|
| Scope challenge | Requested Stage 02 retained; no new infrastructure or future-stage implementation |
| Architecture | Eight concrete source findings; cookie/proxy/membership/lock boundaries and route table written |
| Quality | Reuse existing session/client/form patterns, focused services, no duplicate auth authority |
| Tests | Full branch diagram and STAGE02_TEST_PLAN.md written; all new groups pending real execution |
| Performance | Bounded hashing, indexed scope, pool/lock/IP assumptions documented |
| Exclusions / existing reuse | Written in CEO and final scope ledger |
| Failure modes | Twelve engineering failure classes mapped; no silent gaps accepted |
| Parallelization | API foundations -> UI integration/tests -> sequential full verification; no concurrent test DB use |
| Outside voice | Actual integrated Codex CLI review exit 0; four findings reconciled, same-family source codex+subagent; Claude unavailable |
| Lake score | Complete required behavior chosen; no shortcut authentication or isolation test substitutions |

| Dimension | Delegated engineering review | Actual CLI outside voice | Agreement / coverage |
|---|---|---|---|
| Architecture | Ordinary FastAPI/PostgreSQL authority | F2 requires enforced offline legacy migration | Corroborated local boundary; guard added |
| Test coverage | Real-service race/claim obligations | F4 identifies missing independent-instance/revocation/mixed-batch checks | Added tests/source reviewed; final run pending |
| Performance | Documented local limits | No performance-specific finding/grade | Not independently rated |
| Security | Session/CSRF/roles/legacy/races specified | F1/F2/F3 expose client-state/rollout/IP-trust gaps | Dispositions recorded below |
| Error paths | Clear protected state; honest uncertain outcomes | F1 requires local clear despite failed logout | Source correction and offline test observed |
| Rollout | Stop old API, preserve data, no deployment | F2/F3 require guard and consistent launch flags | Source/docs corrections observed |

Source: codex+subagent, same family, with one integrated CLI pass rather than four claimed CLI executions. Neither a missing dimension grade nor CLI exit 0 is application test evidence.

| ID | Phase | Decision | Classification | Principle | Rationale | Rejected alternative |
|---|---|---|---|---|---|---|
| D17 | Eng | Preserve every Stage01 behavioral test with real auth fixtures | Mechanical | Completeness | New boundary must not hide persistence regressions | Delete tests or bypass identity |
| D18 | Eng | Require real independent-connection race tests | Mechanical | Completeness | Sequential checks do not prove lock behavior | Label sequential requests concurrency |
| D19 | Eng | Keep deliberately wrong expectation outside passing suite | Mechanical | Explicit over clever | Show real assertion failure without fake green wrappers | xfail/stub or policy weakening |
| D20 | Eng | Disable local proxy-header trust for actual peer-IP limiter | Mechanical | Completeness | Installed Uvicorn otherwise trusts loopback XFF | Claim spoof-resistant IP without boundary |
| D21 | Eng | Forward-only ownership migration and explicit CLI dry run | Mechanical | Completeness | Avoid exposing private data or partial legacy transfer | Automatic downgrade/claim |
| D22 | Eng | Reject malformed non-ASCII CSRF tokens safely | Mechanical | Completeness | Reproduced TypeError must become safe rejection | Treat invalid input as 500 |
| D23 | Eng | Include new native focusables in mobile navigation trap | Mechanical | Completeness | Account summary must be reachable by keyboard | Leave Account keyboard-inaccessible |
| D24 | CLI / Design | Clear local protected state before logout request; warn on unconfirmed server revoke | Mechanical | Completeness | F1 must not leave private content visible or fabricate revocation | Clear only after network success |
| D25 | CLI / DX | Enforce configured local API port stopped inside ownership migration | Mechanical | Completeness | F2 requires a concrete guard against the old unscoped process | Rely only on upgrade prose |
| D26 | CLI / DX | Use --no-proxy-headers consistently in documented local starts | Mechanical | Explicit over clever | F3 must match the supported peer-IP trust model | Different README/test launch policy |
| D27 | CLI / Eng | Add bounded barriers, independent-instance/revocation races and mixed-claim assertions | Mechanical | Completeness | F4 exposes unproven concurrency/all-or-nothing behavior | Treat sequential or unsynchronized checks as sufficient |

## Independent CLI review and disposition record

Actual artifact: [STAGE02_INDEPENDENT_REVIEW.md](STAGE02_INDEPENDENT_REVIEW.md). The primary session executed the independent CLI review and reported exit **0**. The artifact states it was a static review, with no application/tests executed or source changed by that reviewer. It reviewed CEO -> Design -> DX -> Engineering and found four issues. The delegated review then reread the amended source and tests below. Review source is **codex+subagent**, both in the same model family; no Claude or cross-model consensus is claimed.

| Finding | Actual review concern | Disposition observed in source | Verification obligation / state |
|---|---|---|---|
| F1, P2 Design | Logout failure retained identity/workspace/project content; auth-route 401 did not clear it | session.tsx now increments generation and clears user/workspaces/selected preference before calling logout; a failed request sets explicit unconfirmed-server-sign-out warning. AuthGate unmounts protected content. No false server revocation claim | teams.spec.ts adds actual browser-offline logout, asserts project title disappears and warning appears, then confirms still-active server session after reconnect. Final suite outcome pending |
| F2, P1 DX/legacy | Applying ownership migration while Stage 01 API remains live leaves its unscoped queries usable | Stage 02 upgrade calls migration_safety.require_stopped_api before DDL for non-test targets. Guard uses a real loopback TCP connection to configured ORBA_API_PORT (default 8000), rejects a listener, and exempts only the specifically named orba_test role/database. README requires stopped local API and custom-port configuration | test_legacy.py uses an actual bound/listening socket to assert rejection, then closes it and asserts allowed offline state. Populated Alembic preservation still runs in a temporary test schema. Final suite outcome pending; guard is a local configured-port safeguard, not universal deployment orchestration |
| F3, P2 DX/auth | README launch omitted the peer-IP protection already present in Playwright | README Uvicorn command now includes --no-proxy-headers; limiter section explains caller-controlled forwarded headers, shared local proxy IP and limits. Same-origin transport forwards only allowlisted cookie/content-type/origin/CSRF headers | Source/startup configuration reread. Final suite starts test Uvicorn with the documented policy; no unexecuted forged-header experiment is claimed |
| F4, P2 Engineering | Tests lacked synchronized overlap, independent-instance limiter race, revocation/write race and mixed valid/invalid operator batch | Owner demotion and invitation acceptance tests now use barriers and bounded waits. Two separate app instances race the same DB-backed login bucket. Member revocation races a real project write and post-revocation write is rejected. CLI test attempts valid+unknown IDs and verifies failure leaves valid legacy project restricted before later successful explicit claim | Actual test source inspected in test_auth_workspaces.py and test_legacy.py. These exercise real API/DB/CLI with no fake responses or in-memory substitute. Final counts/outcomes remain pending in VERIFICATION.md |

All four recommendations remain inside the original Stage 02 authorization and have source/test dispositions. They do not create a user challenge or authorize a later stage. The final orchestrated verification is rerunning after these corrections; neither earlier totals nor a successful static review are substituted for its result.

No remaining high-severity authorization defect was found in this read of the amended auth/workspace/project/legacy source. That is a bounded static finding, not a penetration-test or production-security certification.

## Cross-phase themes

1. **Authority before presentation.** CEO, Design and Eng analysis all require that current session/membership decide visible resources; loading gates and scoped state are part of isolation. CLI F1 independently identified the failed-logout gap in fresh context. This corroborates the behavioral risk within the same model family, not cross-model confirmation.
2. **Preservation before convenience.** CEO, DX and Eng require restricted legacy ownership, exact field comparison and explicit operator claim. CLI F2/F4 separately identified unenforced upgrade order and missing mixed-claim evidence. No shorter signup path justifies automatic legacy ownership or resetting the database.
3. **Real evidence before a verdict.** Every phase distinguishes specifications from executed implementation. Tests, screenshots, command exits, DB assertions and security limitations must describe what actually ran.
4. **One ordinary architecture.** Reuse FastAPI authority, PostgreSQL transactions and existing Next components. No second frontend auth system, fake team activity, hosted service or later-stage agent infrastructure is introduced.

## NOT in scope and deferred ledger

These are explicit exclusions from the owner's Stage 02 request, not silently cut acceptance requirements. No TODOS.md existed at intake; this review is permitted to write only its two plan artifacts, so the deferred ledger lives here and should be reflected in ROADMAP.md by the implementation owner.

| Deferred work | Why / value later | Cost or risk | Upgrade trigger / dependency | Priority |
|---|---|---|---|---|
| AI agents, orchestration, model providers, Skills installation, GitHub OAuth/contributions | Later product capabilities should reuse proven workspace boundaries | New external services, privileges and evidence requirements | Separate Stage 03+ authorization and plan | Future stage |
| Real-time presence/multiplayer transport | Live collaboration could improve awareness | New connection authorization/state/liveness surface | Separate collaboration stage; current memberships proven | Future stage |
| Email delivery and verification | Establish mailbox control and send invitations | Delivery provider, abuse handling, token lifecycle | Before interpreting email identifier as verified identity | Security follow-up |
| Password recovery/passkeys/SSO/OAuth | Account recovery and enterprise identity | New flows/security review | Separately scoped identity stage | Security follow-up |
| Public deployment/TLS/edge abuse controls | Needed for Internet exposure | Hosting, secrets, trusted proxy, auditing and operations | Explicit deployment permission + independent hardening | Before public use |
| Security monitoring dashboard / external telemetry | Broader operating visibility | New infrastructure and privacy scope | Operational requirements beyond local logs/evidence | Future operations |
| Distributed edge limiter and load testing | Handle abuse/capacity across ingress | Infrastructure and tuning | Multi-node/public ingress requirements | Before public scale |
| All-browser/native-device/accessibility certification | Broader compatibility evidence | Additional environments/manual assistive-tech work | Separate QA scope; current Chromium evidence documented | Verification follow-up |
| Public community, packaging and publishing | External adoption/contribution | License, support and distribution decisions | Owner authorizes public project/distribution | Future distribution |

No deferred item is represented by a simulated connection, fabricated record or success message. Required role, CSRF, session, isolation, migration and E2E checks stay in Stage 02.

## Implementation tasks aggregated across phases

All entries are implementation/verification obligations, not completed-work claims. The parent session tracks actual completion and execution evidence. External JSONL aggregation was not run: helper unavailable, no commit window exists, and this delegated review may write only these two documents.

| Task | Priority | Component / files | Work | Source | Verify | Effort (human / agent-assisted) |
|---|---|---|---|---|---|---|
| T01 | P1 | Existing source/docs/scripts | Inspect baseline, preserve untracked files and existing dev snapshot | CEO intake, Eng scope | Existing verify.ps1 actual result | 1-2h / 15-30min |
| T02 | P1 | API models/migration/claim script | Add auth/workspace entities and safe populated migration; explicit dry-run/apply claim | CEO 0A/9; Eng legacy risks | Migration/claim tests + dev snapshot comparison | 1 day / 1-2h |
| T03 | P1 | API security/auth/config | Argon2id, hashed opaque sessions, rotation/revocation/expiry, safe cookie configuration | CEO security; Eng architecture | A01-A12,A20-A22 | 1 day / 1-2h |
| T04 | P1 | API CSRF/login limiter/start commands | Exact Origin/session/preauth tokens; persistent limiter; correct proxy trust | CEO 2/3; Eng source finding | A13-A19 with actual concurrency/proxy boundary | 0.5-1 day / 45-90min |
| T05 | P1 | Workspace/invitation/member services | Reusable membership policy, atomic invites/accept/revoke and final-owner controls | CEO roles; Eng contracts | W01-W22 | 1 day / 1-2h |
| T06 | P1 | Project routes/schema/client | Authenticate and scope create/list/get/PATCH; server-owned creator | Stage01 preservation; Eng contract | P01-P10 + original behaviors | 0.5 day / 30-60min |
| T07 | P1 | Web auth/provider/proxy/shell | Session gate, real forms/account, same-origin relative client and safe expiry | Design passes 1-3; DX pass2 | Actual signup/signin/logout/browser denial | 1 day / 1-2h |
| T08 | P1 | Web workspace/member/invite/pages | Switch scope, settings/invites/roles, explicit acceptance and manual copy | Design state matrix | Two-context desktop/mobile E2E | 1 day / 1-2h |
| T09 | P1 | Test fixtures/backend/browser/experiment | Preserve old tests, add authorization/legacy/concurrency paths and isolated wrong expectation | Eng test artifact | All actual tests and deliberate nonzero experiment | 1-2 days / several hours |
| T10 | P1 | scripts/verify.ps1 and lockfiles | Full frozen install/migration/drift/lint/typecheck/build/E2E orchestration | DX tooling | Final script exit 0, no mandatory skipped checks | 0.5 day / 30-60min |
| T11 | P1 | README/AGENTS/ARCHITECTURE/ROADMAP/VERIFICATION | Exact setup/upgrade/roles/security limits and actual outcomes | Every review phase | Self-contained reproduction and final matrix | 0.5 day / 30-60min |
| T12 | P2 | Safe logging and rendered web | Sanitized operation evidence; focus/overflow/theme screenshot review | CEO observability; Design pass6 | No secret logs, actual visual/keyboard checks | 0.5 day / 30-60min |

Dependencies: T01 -> T02 -> T03/T04 -> T05/T06 -> T07/T08 -> T09 -> T10/T11. Backend/test fixtures and frontend/test fixtures share contracts; coordinate edits without overwriting existing work. Runtime backend/E2E tests must remain strictly sequential because they share orba_test. Reviews ran CEO -> Design -> DX -> Eng in that order; implementation concurrency does not establish review consensus.

## Pre-gate verification of review artifacts

| Required output | Artifact / state |
|---|---|
| CEO specific premises, alternatives, reuse, dream delta, 11 sections | Written above |
| Error/rescue and failure registries | CEO and engineering tables written |
| Seven design dimensions, states/journey/litmus | Written; no generated mockup/runtime score claimed |
| Eight DX dimensions, persona/empathy/journey/TTHW/checklist | Written; setup-time target explicitly unmeasured |
| Engineering scope/code analysis/dependency/test diagrams | Written against inspected actual source |
| Test plan artifact | docs/STAGE02_TEST_PLAN.md, external copy not written under delegated file boundary |
| Scope exclusions, deferred work and aggregated tasks | Written above; no third-file TODOS/helper log mutation |
| Decision audit | D01-D27 written incrementally across phases and CLI disposition |
| Independent voices | Source codex+subagent, same family: actual integrated CLI review exit 0 and four dispositions recorded; Claude/cross-model consensus unavailable |
| Final review footer | Terminal GSTACK REVIEW REPORT below |

This is a concrete review of the authorized Stage 02 implementation. The owner's instruction to implement supplies execution authorization; no extra deployment/destructive permission is inferred and no redundant approval gate is requested. Any later scope/security change outside this plan must be surfaced separately rather than treated as an auto-approved preference.

## Primary references consulted

The token-plus-Origin and session lifecycle design was checked against [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) and [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html). Those references support using explicit request protection and server-controlled session lifecycle; they do not certify this application.

Transaction lock behavior was checked against [PostgreSQL 18 explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html). This plan uses row locks and transaction advisory locks to serialize specific state changes; actual concurrency assertions are still required.

## Durable operational findings

The installed Uvicorn trusts loopback proxy headers by default, so the supported limiter startup must explicitly control that trust. This repository's prior native stdout transcript gap and shared test database require careful evidence capture and sequential execution. These findings are documented here; no global memory or unavailable gstack learning log was modified.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|---|---|---|---:|---|---|
| CEO | /autoplan -> plan-ceo-review | Scope, preservation and trust boundaries | 1 | Reviewed with tooling concerns | 11 sections, named premises, error/failure registries, no scope-changing challenge |
| Design | /autoplan -> plan-design-review | Auth/workspace state and responsive UX | 1 | Reviewed; F1 reconciled; runtime evidence in VERIFICATION.md | Seven dimensions, logout local clear/unconfirmed warning, native focus fix; designer unavailable |
| DX | /autoplan -> plan-devex-review | Reproduction and safe upgrades | 1 | Reviewed; F2/F3 reconciled; full verification exit 0 | Eight dimensions, local migration guard, consistent proxy launch; no invented setup duration |
| Eng | /autoplan -> plan-eng-review | Architecture, races, isolation and tests | 1 + source reread | Reviewed; F4 reconciled; 44 backend / 42 browser passed | Dependency/coverage diagrams, bounded concurrency/independent-instance/revocation/mixed-claim tests and test artifact |
| Independent CLI | Actual Codex CLI outside voice | Fresh-context static challenge, same family | 1 | Exit 0; four findings dispositioned | Source codex+subagent; static reviewer executed no application tests; no cross-model/dimension consensus invented |

**CODEX:** Actual CLI artifact contains four findings: local logout retention, unenforced old-API migration stop, inconsistent proxy launch documentation and concurrency/mixed-claim evidence gaps. All have observed source/test dispositions above. Source is codex+subagent in the same model family; no cross-model consensus is claimed.

**VERDICT:** Plan and CLI dispositions reviewed for the already-authorized Stage 02 implementation. Review tooling remained bounded: helper/designer were unavailable and no cross-model consensus is claimed. The subsequent complete verification exited 0 with 44 backend and 42 browser tests passing; the separate incorrect-policy experiment exited 1 as intended. Runtime was restored and probed again at handoff. See docs/VERIFICATION.md for the Stage 02 delivery verdict and exact execution evidence.

NO UNRESOLVED DECISIONS
