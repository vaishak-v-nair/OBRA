# Stage03.3 final engineering review

Date2026-10-20; final after CEO/design/DX. All findings below are plan acceptance requirements, not claims of code already changed or tests already passing. Primary and independent in-host voices use the same model family; external CLI/Claude unavailable, no cross-model agreement. No generation is authorized.

## Step0: Scope and leverage

Inspected config.py, pm_provider.py, pm_readiness.py, pm_service.py, pm_schemas.py, pm_timing.py, main.py, verification.py, check_pm_config.py, wrappers, existing unit/real-PG/controlled/live tests. Reuse the existing strict lifecycle, gates and output model. One small dependency-free model-policy module is sufficient. No new dependency, route, database migration, orchestrator, second provider or model-picker UI. Changes to source require a new A receipt and make old live evidence inapplicable.

## 1. Architecture and integrity

```text
env -> Settings -- model+thinking policy --------+
      | invalid: hidden-input ValidationError    |
      | missing: app remains available           |
      v                                         v
owner explicit metadata GET <- readiness <- model-policy (3 exact stable IDs)
      | no generation                            |
browser -> Next -> auth+CSRF+workspace -> snapshot helper -> input byte bound
                                      | admitted          | too large422:0run/0call
                                      v
                        pending + request-config diagnostic (DB COMMIT)
                        running/original-session check (DB COMMIT)
                        SDK + same policy/byte guard (no transaction)
                        JSON + authoritative Pydantic/source/graph
                        locked atomic draft/run COMMIT -> succeeded
                           | invalid/503/504 -> failed,0newplan
```

[P1, confidence9/10] config.py:46 currently accepts `re.fullmatch(r"(?:models/)?gemini-[A-Za-z0-9._-]{1,140}", value)`; syntax alone admits unreviewed/aliased models. Add a reviewed exact-ID policy and compatible thinking validation. Preserve prefix identity and no fallback. Missing model is distinct from invalid configuration. Guard direct model_copy/mutation at readiness and adapter entry as well. Invalid Settings may prevent API startup; use hide_input_in_errors and verify actual startup redaction. No new client-trusted permissions.

[P1, confidence9/10] pm_service.py:170 uses `if len(canonical(result)) > 48000:`. This excludes system/schema bytes and undercounts multibyte input. Keep existing snapshot/context guards and add a shared canonical UTF8 content budget before inserting a run. Default48000, permitted8192-96000; equality passes. Sum UTF8(PROMPT)+UTF8(canonical(provider hint))+UTF8(canonical(snapshot)), not wire bytes or provider tokens. The pure helper feeds adapter guard and safe diagnostic counts. Invalid Unicode encoding must safely reject rather than leak input.

[P2, confidence9/10] pm_provider.py:230-234 only adds LOW thinking for exact3.8; another accepted ID currently inherits a provider default. Model-aware explicit ORBA_PM_THINKING_LEVEL defaultsLOW and allows minimal only on documented3.6/3.5 Flash-Lite. Preserve timeouts90/95/100 and SDK attempts1/transport0. All failure states/fences/authorization remain authoritative; no paid rerun for validation.

Nil path: missing key/model -> honest not_configured, no SDK. Empty brief -> existing422. Invalid model/level -> fail closed and offline safe correction. Provider error -> actual failed/interrupted state and no plan. DB uncertainty -> independent terminal read/GET recovery, never duplicate POST. At10x requests admission rejects before dispatch; at100x local DB/lock budgets remain the bottleneck, no distributed throughput claim.

## 2. Code quality and data provenance

Use model policy helper in Settings, readiness and adapter; avoid duplicate matrices. Use one input metrics helper, not a second PRD representation. Build generation hints from ProductDocument then remove only optional server-owned source.actor_id/inherited_kind and confirmation.active/disposition/reason/actor_id/decided_at; exclude human from the generation-only source enum. Every required field, GWT criterion, source quote, graph and server-side validator stays unchanged. Bump prompt to pm-v2 for the omission/default instructions, retain v1 bytes for history. No hydration of arbitrary text or repair/fallback plan.

Snapshot admitted-run diagnostics should retain a nonsecret generation_configuration containing selected thinking, input/max bytes, max output and provider hint hash. Terminal failure/success must merge this small envelope rather than overwrite it; exact replay must not restamp a historical run with new configuration. No key, cookie, headers or brief enters it. Requested and returned model columns already exist and must remain independent. Add input/thinking/hint hash to execution_profile and exact readiness binding; resolve per-model official docs instead of3.8-only validation.

The change remains modest: one static policy, pure metrics, entry guards, hint projection and additive evidence. No global HTTP pool across asyncio.run loops, no caching of generated content, no private reasoning persistence. No catch-all swallowing, new automatic retries or weaker parser. Existing late metadata/uncertain commit handling must preserve terminal success fences.

## 3. Test review (every new branch mapped)

```text
new model policy
  valid3models x prefix/level -> actual SDK synthetic HTTP body/call-count [unit]
  unknown/alias/case/blank/unsupported minimal -> Settings rejection + adapter0HTTP [unit]
  missing provider -> existing setup state; invalid startup -> real subprocess redaction [unit]
new input metrics
  ASCII/Unicode/escaping, exactlimit and+1 -> pure metric and zero-client test [unit]
  oversize -> actual authenticated API422 + independent PG0run/0plan [integration]
  equality -> labeled provider response validated + relational graph read [integration]
  form context/brief/instructions retained, approved untouched -> actual422 [E2E controlled]
new lean schema/prompt
  all required fields/limits intact, fewer unions/properties, no mutation [unit]
  optional server defaults accepted; human/resolved claims still reject [unit/integration]
  semantic planning quality / latency -> [EVAL GAP: future authorized one-model B]
new safe configuration diagnostics
  failed/succeeded/replayed runs preserve original configuration [real PG]
  change runtime model -> historical requested/returned + approval/graph intact [real PG]
new evidence profile
  wrong thinking/byte limit/hint/model-doc link -> fail before B, no external call [unit]
  all old test identities + new hardening identities required [validator]
existing regression
  simultaneous sameUUID, newUUID explicit retry,503/504, malformed JSON/invalid schema
  prior approved plan survives, no partial commit, auth/session/workspace boundaries
  60 core +30 original controlled cases across desktop/mobile/tablet retained [A]
isolated wrong-success -> actual assert failed==succeeded exits1 [separate experiment]
```

No smoke-only assertion is sufficient for persistence. SDK MockTransport proves serialization/error contracts, not live generation; lifecycle doubles are explicitly labeled with real PG/API. New real-PG tests must independently inspect rows after commit/rejection and verify approved actor/time/hash untouched. The browser bound case uses actual API rejection, not route.fulfill. Existing generation budget guard forwards one POST and aborts later POSTs before dispatch; preserve it unchanged. Add baseline identities additively, never edit prior stage arrays, and make A enforce the new set.

Friday2am confidence: one model-aware syntheticSDK success persists a strictly valid graph through the real API plus unauthorized access regression. Hostile case: unvalidated Settings copy or Unicode exact boundary attempts to reach paid SDK; assert0HTTP on rejection. Chaos: existing simultaneous replay/cancellation/uncertain COMMIT tests, no timing-sensitive p99 assertions. Full A is serial against guarded orba_test. Future live quality and current source B cannot be supplied by old or controlled fixtures. See STAGE033_TEST_PLAN.md for exact acceptance matrix.

## 4. Performance

No added DB query or index requirement. The immutable source schema is small; recomputing a few-kilobyte projected grammar per admission/adapter is bounded and avoids shared mutable-cache defects. Compare offline before/after serialized bytes and union/property counts, not provider tokens or latency. Input size8192-96000 and response stream1MiB cap bound memory; full PRD validation retains80000-character/512KiB constraints and graph limits. Do not increase deadlines as an unproven fix. Request-local async clients close in finally; connection pooling changes are unnecessary absent actual timing evidence. Google remains the external availability bottleneck.

## Failure registry / rollback

| Failure | Acceptance | Residual gap |
|---|---|---|
|Invalid model/level / startup|Static safe error,0network, documented correction|Configured typo can stop API until corrected|
|Oversized/invalidUnicode|422 before admission, retained form/approved plan|Local bytes are not billed tokens|
|503/504 / transport / envelope|Distinct origin/status and failed run,0newplans|No demonstrated uptime improvement|
|Malformed/schema/authority|Strict rejection, no approval|Semantic quality needs real review|
|Config drift/replay/history|Persist original config, retain old plan/model/approval|New live B required for material source changes|
|Evidence tampering/stale doubles|Fail-closed A/B/C|Only owner can authorize paid next attempt|

Rollback restores just the scoped source additions through operator-selected files, never resets Git/db/data/receipts. No migration or automatic credential change. Defer Model Hub/fallback/multi-call/pooling/paid benchmarks; existing TODOS.md already tracks later-stage features, so avoid duplicate TODOs. No deployment/commit is authorized.

## Completion and tasks

E1 policy/config/safe startup; E2 lean hints+versioned prompt+canonical byte guard; E3 preserve configuration diagnostics/history; E4 current profile/readiness and additive required identities; E5 actual API/browser boundary regression and complete A/false-success; E6 dated comparison/fingerprint/preservation/paid-stop report. All are P1 acceptance tasks except measured live quality, which is blocked by deliberate authorization boundary. Independent engineering voice must finish before implementation. No claimed test pass in this review.
