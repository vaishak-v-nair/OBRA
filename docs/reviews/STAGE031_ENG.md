# Stage03.1 engineering review

Scope: harden one existing synchronous PM agent and its verification boundaries. The current API already reserves and commits a durable request before dispatch, releases the authentication transaction, fences publication with original session authority, and reconciles uncertain commits. Replacing it with a queue, second authentication layer, background orchestrator or generalized workflow engine would introduce more failure paths without answering this stage's reliability question.

## Architecture

```text
Browser explicit action -> Next same-origin proxy -> authenticated FastAPI
  reserve(commit) -> running(commit) -> Gemini ONE request
    T server / T+5 transport / T+10 outer deadline
  -> strict Pydantic + provenance -> relational graph + success ONE commit
failure -> fenced failed/interrupted record; unknown commit -> authenticated GET

verify.ps1 -> shared verifier -> fixed Gate A commands -> structured reports
verify-live.ps1 -AllowPaid -> current A prerequisite -> ONE live browser flow
  actual API -> fresh draft SQL -> edit/reload -> approval/reload -> fresh SQL
stage summary -> manifests + effective nonsecret profile + immutable receipts
```

Reuse the existing provider abstraction and native FastAPI dependency injection. Test-owned overrides must guard the exact test database, with no production environment flag selecting a fake provider. The runner owns a local advisory lock, actual child exits, bounded command lifetimes and only its own child cleanup; it is not a distributed test scheduler or hostile-machine attestation.

## Code quality

One standard-library verifier owns command definitions, source manifests, report validation and summary decisions. Thin PowerShell entrypoints propagate its native exit without interpreting stdout. Structured diagnostics use bounded enums and finite monotonic measurements; the existing JSONB diagnostic column avoids another migration or duplicate status representation.

The UI needs explicit unknown, rejected-before-admission and confirmed-terminal states. Remove the unknown Clear-reference unlock, but allow a new deliberate submission after authoritative pre-admission rejection. Retain success references until the saved result is read; restore input only on explicit authorized GET and never place private briefs in browser storage.

## Tests

```text
SDK synthetic HTTP -> header/read/envelope bounds, 1 attempt, safe categories
real PG lifecycle -> valid graph, timeout/no graph, approval preserved, replay,
                    concurrency, original-session fences, lost-ack success
real API+PG+browser + labeled timeout double -> truthful error, retained input,
                    GET-only uncertainty, explicit new-UUID retry, restoration
real browser Gemini (later opt-in) -> API + independent draft/approval SQL
verifier unit fixtures -> missing/skipped/xfail/flaky/stale/mutated proof rejects
isolated real-PG wrong assertion -> actual pytest exit1, never mandatory suite
```

Preserve all 102 backend and 51 browser baseline behaviors, not just a lower-bound count. Capture JUnit/Playwright JSON, reject skips/xfail/retries/flaky results and neutralize inherited test filtering. Synthetic validator reports and provider doubles prove deterministic behavior only and can never satisfy Gate B.

## Performance and deadlines

Installed Google SDK2.31.0 derives X-Server-Timeout from HttpOptions unless explicitly supplied, and overrides HTTPX per-request timeout. Set all three envelopes deliberately; increasing only a client default would not solve the equal-deadline race. Keep the server budget unchanged and the total bound within existing lease/publication/proxy/browser fences; do not infer that an upstream timeout has been cured.

Measure admission, running confirmation, provider, validation and persistence flush separately. Store measurements known before terminal commit with that boundary named; log acknowledged commit duration after the transaction exits. Do not add a second status write solely to record timing, or overwrite terminal success after uncertain acknowledgement.

## Security

Empty overrides for both key aliases and model are necessary because deleting variables reactivates dotenv credentials. Migrations and drift checks must explicitly target guarded orba_test, and only that Compose service needs startup. Nonsecret execution provenance includes model, prompt/schema hashes, SDK version, timeout/output/admission limits; no credential value or credential fingerprint is recorded.

Every recovery GET, restore, retry, edit and approval retains current project membership checks. The retry must recheck the exact own request/run and not use an unrelated actor's history row as authority. Source manifests include newly added nonignored code and lockfiles so the uncommitted baseline is identifiable without committing user changes.

## Failure registry

| Failure | Correct result | Coverage / remaining boundary |
|---|---|---|
| Upstream504 / local timeout | failed, no new plan, safe origin/timing | SDK + PG + controlled browser |
| Browser/proxy disconnect | unknown, retain UUID, GET only | browser transport failure |
| Pre-admission validation/CSRF/limit | rejected, no invented run, deliberate resubmit | API/UI regression |
| Saved result read unavailable | retain recovery identity and local input | browser recovery |
| Lost commit acknowledgement | read committed success, never overwrite | existing PG test retained |
| Stale active lease | interrupted, no invented recovery | existing lifecycle tests |
| Command nonzero / incomplete report | failed gate, original exit retained | validator + wrong-assertion experiment |
| Source/config/artifact drift | no VERIFIED verdict | verifier contract tests |
| Missing paid authorization | BLOCKED before any provider dispatch | preflight tripwire |

Critical unaddressed implementation gaps: none in the amended design. Live verification remains deliberately pending owner authorization, and real external timeout behavior cannot be certified by controlled doubles.

## Independent voice and completion

The independent in-host review in STAGE031_ENG_VOICE.md agreed with this bounded architecture and supplied E1–E5: dotenv-safe overrides, pre-admission recovery, complete result validation, nonsecret profile identity and bounded owned-process cleanup. All five are adopted. This is primary plus independent same-family static review, not cross-model consensus or executed implementation proof.

Not in scope: Stage04, other agents, automatic paid retries, fallback PRDs, queue workers, deployment, database reset, credential changes, automatic commits or global tooling repair. Existing code and fixtures remain authoritative. A test-plan artifact and per-phase tasks are recorded under the local .gstack project folder; missing helper binaries are documented rather than claimed executed.
