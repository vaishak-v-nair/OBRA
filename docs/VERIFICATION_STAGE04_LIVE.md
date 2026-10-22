# Stage04 authorized live Gate B: FAIL before model dispatch

Executed 2026-10-22 IST (2026-10-21 UTC). **Stage04 verdict: PARTIAL.** The one
authorized command ran once and exited1. Its browser failed while preparing the
approved source, before any model-generation request. No retry/model switch/budget
increase/source edit/commit/push/Stage05 occurred.

## A. Actual A/B/C result

| Gate | Result | Native exit | Evidence |
|---|---|---:|---|
| A deterministic | PASS; existing applicable 15-command receipt; 386 backend, 60 core, 33 PM controlled, 33 Architect controlled browser tests; no skips/retries | 0 | [A receipt](evidence/stage04/20261021T174944Z-A-1ce59ebc/receipt.json) |
| B live Architect workflow | FAIL; 0 passed/1 failed/0 skipped/0 retries; generation dispatch0 | 1 | [B receipt](evidence/stage04/20261021T184000Z-B-c6b2865b/receipt.json), [browser log](evidence/stage04/20261021T184000Z-B-c6b2865b/live-browser.log) |
| C combined source-bound verdict | PARTIAL; matching source does not excuse failed B | 2 | [Actual C output](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/gate-c-console.log), [native exit](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/gate-c-native-exit.json) |

Gate A was revalidated against current source and all artifact hashes, not rerun or
claimed as new execution. No earlier PM live result substitutes for Architect B.

## B. Failure findings

Actual error at `apps/web/tests-architect-live/architect-live.spec.ts:27`:

```text
TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Approve plan', exact: true })
```

The [actual browser failure snapshot](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/browser-error-context.md) shows Chat,
not project detail, when the test waited for the PRD approval button. The project was
created and the human-authored PRD saved. Code waits for the POST response, seeds that
project, then calls page.reload without awaiting project-detail URL/navigation first.
This is consistent with a navigation synchronization race. The captured evidence does
not establish why the route had not committed; no application fix or test assertion
change was attempted under the source freeze.

This is a local 15-second browser locator timeout, **not** a Gemini503/504/provider/
transport/100-second generation timeout. Generation was never attempted. There is no
ArchitectRun to mark failed; inventing a failed run would misrepresent pre-dispatch
failure. The workflow receipt and browser test correctly remain FAIL.

## C. Runtime profile and real-provider evidence

Source start/end/current: `07bf0deb6c2a0cdaed19a4441619404fbda0f57674a0db9171cb3ea47628eab7` (165 relevant files).
A receipt SHA256 `64541615f31e619235fd60a2cecaedf702d6464a04855fab048466ed2bbc22ad`; B receipt SHA256 `0072d2974228355f28fcd973e07fb886503a9cf4bc598fb31336b91b80bfd71a`.
B records its actual A receipt/hash linkage and unchanged source/prompt/schema contract.

| Field | Actual evidence |
|---|---|
| Configured requested generation model | google-gemini / gemini-3.6-flash |
| Thinking/output | minimal /6000 combined output-thinking cap |
| Concurrency/retries |1 browser worker; WEB_CONCURRENCY=1; application concurrency1; SDK attempts1 (initial only), automatic retries0 |
| Deadlines |90s provider,95s transport,100s envelope; unchanged |
| Input bound |96000 UTF8 content bytes; no truncation/continuation |
| Official SDK | google-genai2.31.0 |
| Read-only metadata | one actual models.get, HTTP200, models/gemini-3.6-flash;540.161ms; child command2.222s |
| Metadata meaning | ready_for_attempt only; generation_verified=false |
| Real generation requests | attempted0, forwarded0, blocked0; PM generation0 |
| Generated response/model/response ID | NOT AVAILABLE; no generation response received |
| Provider generation duration/token usage | NOT AVAILABLE; no generation request |
| Architect run/architecture ID | none; no records created |
| Source PRD | `54e13891-3f85-497f-b35d-b0327e2952ea`, version1 / revision1, state draft |
| Source approval/binding to an Architect run | NOT RUN; source approval failed; no run exists |
| Test project | `575edc8a-cdcb-40c9-9059-003134c87a3a` |

[Unmodified B proof](evidence/stage04/20261021T184000Z-B-c6b2865b/live-proof.json),
[nonsecret authorization/profile](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/authorization-and-preflight.json),
[actual readiness output](evidence/stage04/20261021T184000Z-B-c6b2865b/architect-readiness.log).
Metadata model identity must not be confused with a returned generation model.
No fabricated architecture/tasks/dependencies/usage/response identifiers were used.

## D. Reached and unreached verification

| Step | Result in this live attempt |
|---|---|
| Database startup and guarded test schema | PASS |
| Read-only exact-model metadata readiness | PASS; not generation evidence |
| Real account/workspace/project creation | PASS; SQL confirms records |
| Human-authored PRD creation | PASS; persisted draft,1 epic/1 story/1 criterion; no PM call |
| PRD approval through browser | FAIL; approval button unavailable on Chat |
| Gemini Architect request/response | NOT RUN |
| Architecture schema/source/traceability/DAG validation | NOT RUN against live output |
| Architecture/components/tasks/dependencies persistence | NOT RUN; all counts0 |
| Architecture/graph browser rendering | NOT RUN |
| Human architecture editing/reload/approval | NOT RUN |
| Architecture approval actor/version/revision | NOT RUN |
| Unrelated-workspace isolation on generated architecture | NOT RUN |
| Independent failure-state database inspection | PASS; confirms absence, not successful generation |

Existing Gate A negative/isolation/DAG tests remain passing deterministic evidence,
not a substitute for the unreached live steps.

## E. Independent PostgreSQL evidence

A separate connection used `SET TRANSACTION READ ONLY` on guarded orba_test:
1 user,1 project,1 draft PRD,1 epic,1 story,1 criterion; **0 PM runs,0 Architect runs,
0 architectures,0 components,0 tasks,0 dependency edges,0 requirement traces**.
The source remains version1/revision1 with null approver/timestamp.
[Actual SQL audit](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/independent-database-audit.json).
No valid-looking architecture was saved. Development data was never test-cleaned;
the existing test fixture legitimately resets only guarded orba_test.

## F. Actual commands and exits

| Command | Exit | Duration(s) |
|---|---:|---:|
| docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres |0|1.131|
| uv run --directory apps/api alembic upgrade head (guarded test environment) |0|2.363|
| uv run --directory apps/api python -m scripts.check_architect_config --check-model (inside B) |0|2.222|
| npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:architect:live (inside B) |1|47.299|
| pwsh -NoProfile -File scripts/verify-architect-live.ps1 -AllowPaid |1|56.444|
| uv run --directory apps/api python -m scripts.architect_verification summary (separate, no provider request) |2|1.897|

Only the authorized command was paid-capable, executed once with process-local model/
thinking overrides. No runtime dotenv was edited. [Actual command/native exit](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/live-command-native-exit.json),
[console](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/live-command-console.log). Gate C was run separately after the
failed script because that script invokes C automatically only when B succeeds.

Two operator audit helper errors are preserved separately from B: a read-only query
used created_by instead of the existing creator_id and exited1 before any write;
its corrected read-only query succeeded. An initial preservation assertion exited1
because it included the mutable gate.lock with historical artifacts. Reading the
unchanged verifier proves this exact runtime lock appends b0 on invocation. The
corrected audit verifies every other original evidence file unchanged and records
that one control file separately. Neither correction changes implementation,
assertions in the application suites, or Gate B's failed result.

## G. Preservation and limits

[Preservation/execution audit](evidence/stage04/authorized-live-20261021T183928Z-86e120e3/preservation-and-execution-audit.json)
checks 965 preexisting immutable evidence files byte-identically, including receipts
and referenced artifacts. The sole changed preexisting evidence-directory file is
runtime `docs/evidence/stage04/gate.lock`, expected from the unchanged standard
verifier. No historical transcript/receipt/result was modified. The new latest-B
pointer records this genuine failure. Credentials, Git HEAD/checkpoint/index and
relevant implementation source remain unchanged. Owned browser/API ports were released.

No code/engineering task/generated SQL/migration/deployment was executed from AI
output. Repo-authored Alembic setup ran only against isolated test PostgreSQL.

## H. Next step and verdict

Proposed next work, **not performed**: investigate/fix the missing project-navigation
synchronization before source approval, add a meaningful cold-start deterministic
regression, then rerun Gate A if relevant source changes. A future live workflow
requires a separately agreed applicable source/profile and explicit authorization.
No additional generation or workflow retry ran in this attempt.

**Stage04 verdict: PARTIAL.** Gate A passes; Gate B failed before model dispatch;
Gate C is PARTIAL. There is no live Architect success evidence.
