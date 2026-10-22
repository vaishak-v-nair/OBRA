# Stage04.1 targeted implementation review

Read-only implementation review after the first focused checks and unpaid
preflight. No provider, database or test command was executed by this reviewer.
Implementation files were not edited. This report is static review evidence,
not proof that any verification gate passed.

## Finding requiring correction

P2, confidence9/10: `apps/api/scripts/architect_preflight.py:validate_preflight`
does not require source identities to exist before comparing them. For example:

```python
or sql.get("approved_by") != proof.get("actor_id")
or sql.get("plan_id") != proof.get("source_plan_id")
or sql.get("project_id") != proof.get("project_id")
or sql.get("workspace_id") != proof.get("workspace_id")
or sql.get("version") != proof.get("source_version")
or sql.get("revision") != proof.get("source_revision")
or sql.get("content_hash") != proof.get("source_hash")
or sql.get("current_approved_plan_id") != proof.get("source_plan_id")
```

When a field is absent on both sides these comparisons are false, so they do not
reject it. A malformed proof retaining the required PASS/classification/approval
labels, nonempty approval timestamp, ordered milestone names and zero-generation
counters can omit the project/workspace/actor/plan/hash/version/revision identities
and evade these identity checks. This is a parser integrity gap, not an observed
failure in the browser helper, which does check the actual records.

Require nonempty source/project/workspace/actor/hash values and valid positive
integer version/revision before equality checks. Add mutation tests that start
from otherwise complete synthetic parser input and remove each identity from both
SQL and proof, plus invalid version/revision values. Label these parser-unit inputs
as synthetic. `require_live_setup` already uses `any(not value or ...` for its
corresponding live-evidence identity check and does not have the same missing-on-
both-sides gap.

## Diagnostic improvement

P3, confidence9/10: `apps/web/tests-navigation/navigation.spec.ts:test.afterEach`
performs its boundary assertions before writing the per-case proof:

```typescript
expect(counters.provider_dependency_entries).toBe(0);
expect(counters.blocked_generation_posts - blockedBefore).toBe(proof.expected_denied_posts ?? 0);
expect(proof.generation_budget).toEqual({ attempted: 0, forwarded: 0, blocked: 0 });
proof.case_result = info.status === info.expectedStatus ? "PASS" : "FAIL";
writeFileSync(...);
```

If an unexpected generation attempt or boundary failure occurs, the assertion
correctly fails the browser test, but its partial safe timeline is never written.
The verifier still fails from the Playwright report, so this does not manufacture
a green result. Preserve the partial proof in a `finally`, marking a failed
afterEach boundary check as FAIL while rethrowing the original assertion. This
would meet the stated observability goal for the most safety-relevant failure.

## Reviewed paths without further blocking findings

- `architect-preflight.ts` now waits exact project URL, loaded project/workspace
  attributes, selected workspace and heading before reload. It checks real draft
  identity/version/revision, actual approval HTTP200 and submitted version/revision,
  approver/time, independent SQL hash/current approval and zero generated records.
  It reloads and rechecks the exact approved source before reaching Architecture.
- `architect-boundary.ts` starts closed at BrowserContext level, rejects all PM
  requests, requires live opt-in plus passing source setup, admits one Architect
  request and closes before dispatch. Unexpected attempts remain counted and cause
  final live/preflight evidence checks to fail.
- `no-generation-config.ts` clears provider credentials/live opt-in for its test
  API process. `tests/no_generation_app.py` guards the exact test DSN, refuses live
  opt-in, reads no dotenv, uses an explicitly labeled non-credential control
  sentinel, denies generation before dependencies and installs provider tripwires.
  Direct API calls bypass browser routing but still hit this server denial.
- `inspect_architect_preflight.py` uses a fresh engine/session and an explicit
  repeatable-read, read-only transaction; checks exact project/source membership;
  reconstructs and hashes the relational PRD; returns metadata/counts without
  credentials, body content or approval writes.
- The standalone runner records native child exit codes, stops after nonzero,
  rejects invalid/missing reports, checks unchanged source and writes separate
  non-live receipts. Successful unpaid execution cannot itself certify live B.
- The live spec reuses shared Phase1, opens its generation boundary only afterward,
  preserves the one-request budget and uses the same architecture for later SQL,
  UI editing, approval and isolation. The unrelated browser context has a closed
  boundary. Its proof is saved in `finally`.
- New navigation scenarios cover held real responses, delayed session/workspace
  restoration, different project identity, exact reload/approval, revoked session,
  denied role, controlled API failures and generation-denial boundaries. Controlled
  cases are labeled and no arbitrary sleep or automatic retry was introduced.

Full network traces remain disabled; the new diagnostics contain allowlisted
paths, status, identifiers and timestamps. No new model configuration change,
fabricated architecture response or production authentication bypass was found.

Review result: fix the unpaid parser identity gap before final Gate A; retain
PARTIAL until a fresh authorized real Architect Gate B passes. No paid request
was performed during this review.
