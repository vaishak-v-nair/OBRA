# Stage03.3 CEO review

Date: 2026-10-20. Mode: SELECTIVE EXPANSION. Review concerns the owner's Stage03.3 request, not Stage04. Primary review is source inspection and reasoning, not executed reliability or cross-model evidence. The external gstack startup/CLI wrapper is unavailable; an independent in-host Codex-family reviewer will supply the second perspective. No nested model CLI probe or paid Gemini generation is permitted.

## Step0A: Premises

The desired outcome is a genuine validated, editable, approved product plan, not a green provider health icon. The last HTTP504 is proven upstream: actual SDK ServerError, HTTP status504, origin upstream_http and 88,825.025ms provider phase. It does not prove that schema, thinking, pooling, local deadlines or output limits caused the failure. A prior 503 took 1,537.654ms, inconsistent with a local90s timeout explanation. The account exposes exact model metadata for3.8/3.6/3.5 Flash-Lite via today's bounded GETs; that establishes metadata visibility and advertised methods only. No alternative has demonstrated live generation on current code. All these limits stay explicit.

## Step0B: Existing code leverage

| Problem | Existing authority | Action |
|---|---|---|
|Settings and key secrecy|orba/config.py, SecretStr, root/API dotenv|Add explicit reviewed model/thinking/request-byte policy, no credential rewrite|
|Official SDK and safe failures|orba/pm_provider.py, LimitedTransport|Retain endpoint, one candidate, one attempt, no tools/continuation; simplify only generation hints|
|Read-only readiness|orba/pm_readiness.py, scripts/check_pm_config.py|Reuse exact GET; reviewed policies replace one hardcoded capability reference|
|Lifecycle/isolation/history|orba/pm_service.py, pm_schemas.py, relational models|Keep locks, original session fences, provenance and strict validation; add pre-dispatch byte admission|
|Real evidence|scripts/verification.py, verify*.ps1, tests-live/pm-live.spec.ts|Keep independent gates; bind thinking/input/provider-schema profile as well as source|
|UX recovery|ProductPlan current states and request UUID recovery|Preserve honest errors, retained brief, terminal-only explicit retry|

## Step0C: Dream and delta

```text
CURRENT                          THIS PLAN                        IDEAL (not implemented)
3.8 + LOW, upstream503/504  -> 3 reviewed explicit choices    -> measured model quality/latency corpus
one documented model GET     model-aware bounded thinking      evidence-based owner selection
rich shared output grammar   lean generation-only hints        multiple planning agents/Model Hub
strict graph + A/B/C gates   same strict graph + current A      Stage04+ only by new authorization
```

This plan creates safe choices and measurable request bounds. It cannot promise provider uptime, bill accuracy without usage, or improved live latency without a separately authorized generation. The 12-month platform ideal is deliberately excluded.

## Step0C-bis: Approaches

| Approach | Effort/risk | Benefit | Cost/decision |
|---|---|---|---|
|Document503/504, keep arbitrary Gemini IDs and current grammar|Small/low|No implementation churn|Does not meet explicit model validation or alternative-thinking request; reject|
|Small reviewed policy table + configurable thinking/byte cap + lean hints|Moderate/local, additive tests|Explicit compatible choices, less irrelevant grammar, bounded inputs|Choose; no generation-quality claim and no migration|
|Fallback router, retries, persistent HTTP pool, split multi-call PRD|Large/high paid/scope risk|Potential throughput improvement|Reject; violates one-request/manual selection and adds unmeasured complexity|

## Step0D: Scope decisions

Accept model policy, request-budget diagnostics and strict deterministic tests because they directly control the authorized request. Accept pruning optional human-owned output-hint fields because models may never set them and Pydantic defaults/security remain authoritative. Preserve every required overview/scope/requirements/epics/stories/criteria/uncertainty field. Defer live latency benchmarks, multi-provider routing, new UI selection and model quality scoring; no request is paid here. Keep existing .env3.8 unchanged and recommend3.6/minimal separately; the next owner authorization must name the actual configuration.

## Step0E: Temporal interrogation

Hour1: verify immutable baseline and classify503 versus504. Hour2: bounded account metadata and official capability/pricing/lifecycle references; offline grammar metrics. Hour3: sequential design/DX/engineering review and typed policy. Hour4: SDK contract and real-PG negatives. Hour5+: full A, isolated wrong-success experiment, preservation audit, source-bound receipts. A new paid call is a later owner decision, not a time-saving shortcut. If A fails, fix the actual defect and retain the failed receipt; never spend to compensate.

## Step0F: Mode

SELECTIVE EXPANSION holds the product concept. Only directly related safe configuration and diagnostics are accepted. No commercial/market reframing or new product workflow is necessary; developer truthfulness is the differentiator here.

## 1. Architecture

```text
env -> Settings -> reviewed Gemini policy (ID, supported thinking, docs)
                       |                         |
                    admission                 metadata GET (explicit only)
browser -> Next proxy -> FastAPI auth/CSRF/workspace -> reserve run -> release DB
  |                                                   |
  |                                    byte bound + SDK generate (one call)
  |                                                   |
  +-- truthful error <- failed/interrupted      strict ProductDocument + source graph
                                                     |
                              short authorized atomic plan+run commit -> draft UI
```

New coupling is only Settings/readiness/provider to a dependency-free model-policy module. Snapshot admission may reuse the existing provider-schema size helper, not duplicate the PRD model. At10x load local admission rejects, and at100x PostgreSQL locks/rate admission remain the first local bottleneck; no distributed readiness or production scale claim follows. Provider availability remains the external single point of failure. No DB migration is needed. Rollback is operator restoration of these specific code/config additions, preserving run/plan rows and old prompt files.

## 2. Error and rescue registry

| Codepath | Failure / exception | Handling | User/operator outcome |
|---|---|---|---|
|Settings policy|Unknown ID, blank/unsupported level, numeric bounds / ValidationError|Reject configuration, CLI safe sanitized response|No provider dispatch; supported options documented|
|Snapshot budget|UTF8 request exceeds configured byte envelope / PMError422|Reject before admission/SDK|Brief retained, reduce input explicitly|
|Direct adapter guard|Unvalidated model_copy bypass or oversized snapshot / ProviderFailure|Recheck supported policy/bound before client construction|Honest failure, zero requests|
|Metadata|401/403/404/429/503/504 / SDK APIError|Existing status distinctions, one GET|No readiness claim and no generation|
|Generation|503/504 / SDK ServerError|Existing failed terminal state with actual status/origin|No new plan, prior approved plan intact|
|Transport/envelope|httpx.TimeoutException/TimeoutError|Distinct diagnostic origin, no retry|Bounded failed attempt; possible billing uncertainty|
|Response validation|Malformed JSON/invalid graph/human authority / ValidationError or ValueError|Record safe validation failure|No valid-looking partial plan|
|Publication|DB failure/cancellation / SQLAlchemyError or CancelledError|Atomic rollback or independent read for uncertain commit|No invented terminal success; GET-only recovery|

No catch-all secret-bearing logging, raw bodies or hidden retries are introduced. Model refusal/empty/multiple/unfinished candidates already reject independently of JSON validation; preserve those paths.

## 3. Security/threat model

Unknown/alias model routing is medium likelihood/medium impact: reject IDs outside three reviewed stable identifiers, preserve the optional models/ prefix without switching. Configuration is server-only and no model-picker endpoint is added. Large multibyte context is medium likelihood/medium impact: count UTF8 bytes including prompt/schema, reject before paid dispatch. Generated human provenance is high impact: omit from generation hint and still reject if returned. Credential exfiltration is high impact: fixed official host, trust_env false, no redirects, no diagnostics containing input/headers/keys. Existing real membership, session, CSRF, approval and immutable-history checks remain unchanged and must regress through A.

## 4. Data flow and edge cases

```text
explicit model/level -> policy -> snapshot bytes -> persisted pending -> running -> provider
       | nil: not configured   | empty brief422       | duplicate UUID: replay only
       | unknown/incompatible: reject              | new UUID while active409
provider -> JSON -> Pydantic/source graph -> locked transaction -> draft
   | 503/504: failed +0plans      | invalid: failed       | uncertain COMMIT: read, no resubmit
```

Empty configuration remains usable for the rest of ORBA with an honest setup state. Prefix and whitespace normalization must not change the requested model to a different one. Timeout/network unknown UUIDs remain GET-only until terminal confirmation. Existing browser terminal-only retry preserves the brief and creates a new auditable UUID. Editing/approval/reload and outsider isolation use one generated plan in future B; metadata never appears as that plan.

## 5. Code quality

Use a frozen small policy type with three entries, not a strategy engine. Avoid copying provider error maps, session logic or Pydantic output models. Keep request-bound helpers pure and reusable in admission and adapter. Policy checks must also guard model_copy in direct adapter tests so configuration validation is not the only line of defense. Add profile fields additively; historical receipt bytes remain immutable and stale receipts simply cease to certify changed code.

## 6. Tests

```text
NEW settings branches -> table-driven valid/invalid model/level/prefix/bounds (unit)
NEW SDK body          -> synthetic HTTP through real Google SDK for every supported choice (unit)
NEW byte guard        -> exact boundary + Unicode + no HTTP + real-PG no run/plan (integration)
NEW lean hint         -> schema metrics + every required field kept + malicious authority rejected
EXISTING lifecycle    -> real PG503/504/malformed/no-plan/approved preservation/concurrency/replay
EXISTING UX           -> 60 core +30 controlled browser identities, zero retries/skips
LIVE boundary         -> no generation here; existing one-call future B, stale C remains PARTIAL
```

The hostile case is an exact-bound multibyte request or invalid model_copy that reaches the SDK despite config rejection. Chaos cases are cancellation, uncertain commit and simultaneous identical UUID; retain existing real-PG tests. Deterministic SDK/doubles prove behavior only. Live provider latency/quality remains untested. Do not add timing-sensitive performance assertions or mock integration persistence.

## 7. Performance

Offline baseline: prompt2935 UTF8 bytes; projected schema3892bytes,99 JSON object nodes,7 anyOfs,54 properties. The authoritative schema is6181bytes. Remove only optional server-owned source/confirmation hints and the forbidden human source enum; preserve required fields and server validation. These changes reduce grammar/output overhead, not proven failure cause. No new queries/N+1/indexes, background jobs or connections. A per-generation client is intentional: low admission, deterministic cleanup and synchronous asyncio.run make a shared async pool risky; no evidence of TLS/connect bottleneck justifies pooling. SDK90/transport95/envelope100 remain bounded and unchanged.

## 8. Observability and debugging

Keep safe run ID, stage timings, upstream status and true returned metadata. Add requested thinking and byte/output limits to nonsecret execution profile and fresh run diagnostics, plus provider-hint hash for reproduction. Never log the brief or credential. Failures that have no returned model/usage remain null. Point-in-time GET evidence includes date/model/action/limits/duration, not a green generation badge. Operational response: inspect own run, correct configuration or wait, then obtain explicit paid authorization; no automated alerting/dashboard claim in this local stage.

## 9. Rollout

No schema mutation or data ownership change. Preserve root/API dotenv and every existing receipt. DefaultLOW keeps existing3.8 behavior; alternatives require explicit ORBA_PM_MODEL and optional compatible level. Unknown identifiers now fail early instead of allowing an unreviewed paid call; document that intentional tightening. Run A after all relevant source changes and compare old evidence hashes afterwards. Gate C must reject old B for new source/profile even though historical successful/failing artifacts remain readable. Do not deploy or commit.

## 10. Trajectory

Reversibility4/5: code and explicit nonsecret configuration are local; historical run model IDs remain untouched. The model policy has dated official references and must be deliberately reviewed when provider lifecycle changes. This is not a claim of permanently stable availability. Future Model Hub may reuse evidence contracts but not be built now. The six-month regret is a false causal claim or static allowlist becoming stale; solve with clear limitations and a documented review procedure, not live fallback.

## 11. UX

Current hierarchy remains project brief, explicit Generate, real run outcome, persisted draft then approval. Examine loading, no-provider, rate-limit, unavailable, timeout, invalid-response and network-unknown states; no new progress theater. A failed request keeps the editable brief and previous approved version. No model selector is added to the application; server-only selection is clear in docs and safe capability metadata. Existing themes, keyboard/focus and desktop/mobile/tablet coverage remain required. Full design review evaluates these states next rather than redesigning them.

## Failure modes registry

| Failure | Evidence/mitigation | Residual |
|---|---|---|
|Actual provider503/504|Recorded upstream status, failed run,0newplans|Cannot fix provider uptime locally|
|Minimal thinking truncates/lowers plan quality|Full validation and6000cap remain; no partial publish|Only future live B can establish output usability|
|Wrong model/unsupported level|Static reviewed policy + SDK wire tests|Account quota can change after GET|
|Large request/Unicode|Complete prompt+hint+snapshot UTF8 cap|Byte envelope is not measured provider tokens|
|Duplicate click/retry|Existing durable UUID and terminal-only UI recovery|User must deliberately authorize any paid retry|
|Stale evidence|Source+profile bound A/B/C|New B required after material code change|

## Not in scope

No paid generation, credential/config-file mutation, API fallback, retry loops, multiple-call planning, production pooling, Model Hub, new agents, Stage04, deployment, commits or history edits. Those are outside the owner's current authorization or need actual benchmark evidence first.

## Completion summary

| Area | Result |
|---|---|
|Premises|Provider failures proven, cause not inferred; metadata != generation|
|Approaches|3 evaluated; small static policy selected|
|Accepted scope|Model validation/thinking, lean hints, byte bounds, diagnostics/tests|
|Deferred|Fallback/router/pool/benchmark/new UI/stage expansion|
|Critical gaps|Current live generation unverified; cannot close in this task|
|Review completeness|0A-0F and sections1-11 evaluated; registries/diagrams above|
|Next|Independent CEO voice, then design/DX/engineering in order|
