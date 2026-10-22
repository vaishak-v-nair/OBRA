# Stage04.1 CEO review

Reviewed 2026-10-22. Mode: **HOLD SCOPE**. This is an independent in-host
Codex review of `docs/STAGE041_PLAN.md`, not a second model's opinion and not
execution evidence. The installed gstack native helper is unavailable; its
telemetry, outside-provider probes and global setup were not run. No production
code, historical evidence, model settings, credentials or database records were
changed during this review. Only this review document was written.

## Decision and findings

Proceed with the scoped repair. The owner's existing authorization covers the
recommended investigation and implementation below. Do not claim the historical
failure is a proven navigation race until it is reproduced with an observable
real-response barrier. Do not add a new routing/session service.

1. **WARNING: response receipt is not route completion.** The live test waits for
   the project POST response, invokes the human-authored fixture and reloads,
   without awaiting the intended project URL or loaded project identity.
   `ProjectForm` awaits JSON processing before `router.push`. The failed snapshot
   shows Chat and SQL confirms a persisted draft; these establish the symptom,
   not the exact causal ordering. Reproduce the ordering before naming the cause.
2. **WARNING: title-only synchronization is insufficient.** A successful setup
   must bind the returned project UUID, rendered project UUID, selected workspace,
   authored plan UUID and approved version/revision. A heading that happens to
   match cannot establish that the intended record was loaded.
3. **WARNING: a page route interceptor is not the full unpaid boundary.** It does
   not independently fence direct API-context requests or other clients. Use a
   guarded test-only server denial before either generation handler, retain the
   browser boundary and verify the denial through a direct API probe in a separate
   boundary test. No production bypass or provider double success is needed.
4. **OK: existing state fencing should be preserved.** `AuthGate` keys protected
   content by account, workspace and pathname. That already remounts project
   detail after these identities change. The absence of local state clearing in
   `ProjectDetail` does not establish a stale-state defect by itself. Test the
   delayed two-project and workspace-restoration cases before adding app changes.
5. **OK: repetition is evidence, not a retry policy.** Run five fixed, separately
   receipted, clean no-generation preflights after the complete deterministic gate.
   Preserve every result, including any early failure. A later pass does not
   rewrite an earlier failure or grant permission to call Gemini.

## 1. Architecture review

Reuse the current UI, authenticated FastAPI routes, PostgreSQL sessions, authored
draft fixture, existing approval workflow and verifier. Introduce a shared setup
helper and verification boundary, not a new application subsystem.

```text
Browser UI -> Next proxy -> existing FastAPI auth/project/plan routes -> test PG
     |                                 ^
     +-> exact URL + project/workspace --+
     +-> shared Phase1 -> UI approval -> independent SQL audit
     +-> Architect entry point
          |
          +-> unpaid mode: browser deny + guarded test-server deny -> STOP
          +-> future paid mode: explicit phase transition -> existing one-call B
```

Before: live test owns inline project/source setup and one-request allowance.
After: live and unpaid verification share identity-checked source setup; only the
paid workflow can open its generation phase. No model-request policy changes.

Happy: real project response -> exact route -> matching record -> exact draft ->
UI approval -> API/SQL agreement -> reload -> Architect entry. Missing: absent
project/plan/source fails the named setup phase. Empty: zero plans produces an
explicit prerequisite failure. Error: auth/network/approval denial stops before
generation and emits the last completed milestone. No silent continuation.

The frontend/backend/test database remain required dependencies. Ten concurrent
test runs would corrupt the shared reset assumptions; keep one worker and serial
suite execution. At 100x, isolation needs independent databases, outside this
repair. Rollback means owner-reviewed reversal of only this repair's source diff;
no migration or data rollback is warranted, and no reset is authorized.

## 2. Error and rescue map

| Path | Failure class or observation | Required action | Visible evidence |
|---|---|---|---|
| Project creation | HTTP error / interrupted response | Keep failure; do not resubmit automatically | HTTP status and setup phase |
| Route wait | Playwright timeout / wrong URL | Fail with expected and observed path/ID | Sanitized navigation timeline |
| Project GET | 401/404/network error | Respect existing auth/error state; stop | No protected prior project shown |
| Session/workspace restore | delayed response / revoked session | Wait for valid authority; never guess ownership | Resolved workspace or auth failure |
| Draft loading | missing plan / API failure | Stop; do not seek approval on Chat | Exact expected plan identity |
| Approval | 403/409/server failure | Preserve draft and fail setup | Actual response plus SQL unchanged |
| Reload | wrong route or lost approval | Fail identity/state check | Exact URL, source UUID/version/revision |
| Generation boundary | any generation POST in Phase1 | Deny before dispatch and fail applicable test | Browser/server counters and zero runs |
| Independent audit | unavailable DB / mismatched state | Fail preflight receipt | Actual subprocess exit and mismatch |
| Evidence writing | missing/hash-invalid artifact | Fail the verification result | Native exit and receipt validation |

Catch-all continuation is unacceptable. Safe diagnostics identify phase, route,
IDs and status, excluding passwords, cookies, CSRF tokens and private brief text.
Provider refusal, malformed output and timeout remain existing Stage04 cases;
Phase1 must not reach those codepaths.

## 3. Security and threat model

| Threat | Likelihood / impact | Mitigation |
|---|---|---|
| Accidental paid dispatch during unpaid setup | Medium / high | Test-server denial before handler plus browser guard; direct API contract test |
| Wrong project/workspace substituted by stale UI | Medium / high | Exact identity checks plus existing AuthGate remount and backend membership checks |
| Approval claimed from a screenshot | Medium / high | Actual approval response and independent SQL actor/time/version/revision checks |
| Test reset against development data | Low / high | Existing exact `orba_test` DSN/role guard; no new production mode |
| Credentials leaked in browser trace | Medium / high | Sanitized route/status/ID timeline; do not publish raw auth traces or headers |
| Historical failure overwritten | Low / high | Intake hashes, immutable receipts and new attempt paths |

No new user-facing endpoint, credential, dependency or authorization policy is
needed. A test-only server wrapper must fail closed outside the guarded test DSN.
Normal application auth, Origin, CSRF and role enforcement remain authoritative.

## 4. Data flow and interaction edge cases

```text
POST response -> validate status/UUID/workspace -> await exact route and record
   | missing/error              | mismatch                     | incomplete
   +----------------------------+------------------------------+-> FAIL
draft fixture -> verify authored origin -> UI approval -> API + independent SQL
   | absent                  | wrong revision          | conflict/denied
   +-------------------------+-------------------------+-> FAIL
reload exact route -> same approved source -> Architect action -> unpaid STOP
```

The plan includes double-click protection through existing app behavior, expired
sessions, denied approval, slow successful reads, missing PRD data and two-project
stale-state tests. Add no automatic retries. Route synchronization must await an
observable identity, rather than a button count or elapsed delay. Preserve a
failed form's original data. A successful metadata check cannot repair a failed
project or approval prerequisite.

## 5. Code quality review

The shared Phase1 helper should own project/source setup once, with a short typed
result containing project, workspace and approved source identity. Paid and
unpaid callers must not duplicate approval setup. Keep the boundary separate from
the setup steps so an error cannot implicitly enable generation. Avoid changing
`SessionProvider` or `ProjectDetail` solely to improve test timing; the test may
be the only defective layer. More than eight touched files is acceptable only
where the additional files are independent tests, evidence or documentation;
more than two new runtime services is a scope warning. No new service is needed.

## 6. Test review

| New path | Test level | Required happy/failure/edge evidence |
|---|---|---|
| Shared source setup | Real-service browser + PostgreSQL | Exact project route, draft, UI approval, reload and exact approved source |
| Response/navigation ordering | Real-response barrier browser regression | Demonstrated old ordering failure and synchronized behavior without sleeps |
| Delayed project/workspace reads | Browser regression with controlled transport barriers | Requested route stays correct, prior/wrong protected content absent |
| Approval and auth failures | Real authorization/session tests; labeled transport error case | Denial/error cannot become approval; SQL actor/state unchanged |
| Unpaid boundary | Test-server integration plus browser contract | Direct API and browser requests denied; zero provider dispatch/runs |
| Receipt propagation | Deterministic verifier test | Required failing subprocess cannot yield PASS; no missing artifacts accepted |
| Repeated preflight | Five independent clean receipts | No retry/skips; each outcome and model-request count visible |
| False-success assertion | Isolated actual pytest experiment | Genuine nonzero exit, excluded from green suite |

The strongest shipping test is the complete clean UI-to-independent-SQL preflight
with a held real response, followed by reload. Hostile QA changes workspace or
revokes the session between load and approval. The controlled chaos case delays
the successful real project response while routing and reload are exercised.
No LLM prompt/schema/model changes are in scope, so live evals are explicitly
not run. All previous regression identities must remain mandatory in Gate A.

## 7. Performance review

No new production query or cache is proposed. The slowest expected work remains
browser startup/service compilation and the existing full deterministic suite;
do not invent p99 measurements. Reuse service ownership safely but make each
preflight's database setup clean and its outcome independently visible. One
worker and serial backend/browser execution protect database correctness. Avoid
polling many endpoints in loops or logging full payloads to compensate for weak
synchronization.

## 8. Observability and debuggability review

Persist a minimal ordered timeline: phase, monotonic elapsed time, page path,
HTTP method/path/status, expected and rendered project/workspace IDs, source plan
ID/version/revision/state, approval actor/time, reload checkpoint and generation
guard counts. Record both attempted and forwarded generation counts distinctly;
zero rows alone does not prove no remote request was sent. Each failed receipt
must identify the last successful prerequisite and exact failed one. Independent
SQL must verify source approval and absence of PM/Architect runs/architectures.
This is local verification observability, not a new production dashboard.

## 9. Deployment and rollout review

No public deployment, migration, production toggle or data cleanup is needed.

```text
inspect + preserve -> reproduce -> smallest repair -> focused checks
 -> final-source Gate A -> isolated regression -> five clean preflights
 -> immutable new evidence + PARTIAL report -> STOP for fresh paid authority

failure -> preserve exact failed attempt -> fix actual cause -> rerun applicable
checks; never overwrite an earlier receipt or relabel it PASS
```

The test-server deny mechanism belongs only to test infrastructure and must not
be a production authentication bypass. Source changes invalidate the old Gate A
fingerprint; a final-source A receipt is mandatory. Historical B remains failed.

## 10. Long-term trajectory review

Reversibility: 5/5 for the proposed test/helper repair, provided artifacts remain
immutable and no database schema change is added. A shared setup with explicit
phase boundaries reduces future paid-verification risk. Document why response
receipt was insufficient, so a later maintainer does not remove the identity
wait. Full orchestration, automatic retries, model selection and production
readiness changes remain outside scope. No new TODO is required to satisfy this
repair; unresolved live Architect proof is an explicit acceptance blocker rather
than hidden technical debt.

## 11. Design and UX review

```text
Sign up -> workspace -> Chat creation -> exact Project detail
 -> Product Plan loading -> draft -> review approval -> approved
 -> reload same detail -> Architecture empty state / generation entry
```

Keep existing themes and accessible navigation. Loading remains loading; absent
draft, unavailable API and revoked session remain honest errors. An unpaid
preflight may prove the entry point is present and correctly permission-gated;
it must report actual provider configuration separately and must not call a
disabled action ready for paid execution. No fake architecture or completion
state should appear. Reuse existing mobile/tablet coverage; add targeted viewport
cases where the helper's navigation or approval controls differ. No redesign is
justified.

## Not in scope and dream-state delta

- Paid Gemini calls and provider configuration tuning: fresh explicit authority
  is required and this repair investigates local setup.
- Routing/session refactor without a reproduced application defect: existing
  identity remounts may already be sufficient.
- New graph, PRD generation or architecture approval behavior: preserve the
  verified implementation and existing coverage.
- Stage05, task execution, deployment, commits and evidence rewriting: forbidden
  by the owner's scope.

The repair makes a reliable unpaid prerequisite gate available. It does not prove
the Architect model works or close Stage04. Live Gate B remains a separate
one-request, source-bound future verification after owner authorization.

## Implementation tasks

- [ ] T1 (P1) Reproduce the response/navigation ordering with real persisted API
  data and record safe phase/route evidence before concluding causality.
- [ ] T2 (P1) Add shared exact project/workspace/source synchronization and use it
  in both unpaid setup and future live B; preserve actual UI approval.
- [ ] T3 (P1) Add the guarded test-server generation denial and direct API/browser
  boundary tests; keep generation counters and SQL absence independent.
- [ ] T4 (P1) Preserve all regressions and add delayed response, restored workspace,
  stale project, expired auth, denied/error approval and failed prerequisite cases.
- [ ] T5 (P1) Run final-source Gate A, isolated regressions, five clean preflights
  and the separate false-success experiment; retain every actual outcome.

Estimated review-to-repair effort: human team about one working day; agent time
depends mainly on the existing full Gate A runtime. These are estimates, not
measured execution results.

## GSTACK REVIEW REPORT

| Review | Runs | Status | Findings |
|---|---:|---|---|
| CEO review | 1 | CLEAR within HOLD SCOPE | Exact identity synchronization and independent unpaid generation denial are required; causal reproduction precedes diagnosis |
| Outside model | 0 | NOT RUN | In-host review only; no provider probe or invented cross-model consensus |
| Design/DX/Engineering | 0 here | PENDING sequential phases | Main agent coordinates those reviews |

VERDICT: CEO scope is clear for the authorized investigation and repair. This
review is not Gate A, live evidence or Stage04 completion. Engineering review is
still required. Main agent accepted the concrete identity/server-denial approach
and the rule against an unproven routing refactor.

NO UNRESOLVED DECISIONS
