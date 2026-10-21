# Stage03.2 CEO review

Mode: SELECTIVE EXPANSION within the owner's fixed Stage03.2 boundary. This is a source/spec review, not executed application evidence. No outside paid CLI model probe runs inside the current Codex host; the independent in-host reviewer is identified separately.

## Audit and premise challenge

Read AGENTS, architecture, verification, TODOS, SDK adapter, PM routes/service, A/B/C verifier and current tests. Git has one local main checkpoint e3fccd6, no origin or stashes; existing changes belong to the owner. The initial Gate A receipt validates against119 source files and the stated19097...fingerprint. Existing pain points are provider503/504, uncertain dispatch and evidence applicability, not missing agent orchestration.

1. Exact gemini-3.8-flash validity was an assumption requiring verification. Official current model documentation and the real bounded account model-list response both name it and generateContent. This supports retaining the owner's model; it does not prove current generation capacity or quota.
2. A1.538-second503 is not evidence of an insufficient90-second local timeout. The saved diagnostic explicitly reports upstream_http, ServerError,503/UNAVAILABLE and1537.654ms. Preserve that reason; keep the distinct historical upstream504 deadline response.
3. A new readiness mechanism can improve diagnosis but cannot close Stage03. Closure requires the authorized browser generation, independent SQL, edit/approval and isolation on matching source. Doing nothing would preserve safe failures but leave operators unable to separate configuration from metadata access.

## What already exists

| Subproblem | Existing leverage | Decision |
|---|---|---|
| Configuration | Settings + scripts.check_pm_config | Extend explicit CLI flag, keep default offline |
| SDK and safe errors | pm_provider.LimitedTransport, error_metadata, no retries | Reuse metadata sanitizer and bounded transport |
| Durable execution | pm_service reservations, short phases, fencing, atomic graph | Preserve; add exact-key concurrent schedule coverage |
| Recovery UX | product-plan pending UUID, GET status and own terminal check | Review and retain, no dashboard/redesign |
| Gate identity | verification source/profile/artifact checks | Add metadata preflight evidence to B without paid probe |
| Existing negative paths | provider unit contracts, lifecycle/controlled browser suites | Retain all identities; add specific503 regression |

## Dream state and alternatives

```text
CURRENT                       THIS PLAN                         12-MONTH IDEAL
config present + safe errors -> explicit metadata diagnosis   -> measured provider suitability
separate A/B receipts          current A + one paid gate ready    genuine authorized agent evidence
unavailable upstream preserved no claim that metadata is PRD      owner-controlled later stages
```

| Approach | Effort / risk | Pros | Cons |
|---|---|---|---|
| A: docs-only metadata probe | human2h / agent20min; low | Few files; preserves source | No reusable readiness/error contract; repeats operator mistakes |
| B: typed read-only service + existing CLI + B preflight | human1day / agent1-2h; medium | One explicit operation; actionable states; no UI/network on load | Adds tests and re-fingerprinting; metadata still cannot prove generation |
| C: API readiness endpoint + polling UI dashboard | human2-3days / agent3h; medium | Visible in browser; reusable for later routing | New credential-backed request surface, throttling/cache policy and unnecessary Model Hub direction |

Choose B for complete current operator diagnosis with the smallest ongoing authority surface. A lacks the requested reusable readiness behavior; C solves broader product administration. Reversibility is5/5: no data migration, credential change or persistence contract change is planned.

## Mode, expansion and time interrogation

Minimum changes are one typed readiness module, extension of the existing config CLI, deterministic tests and B evidence validation. More than eight total files including tests/docs is acceptable only because every extra file proves this narrow path; do not alter generation/schema/prompt merely to make external availability appear fixed. Five candidate touches were assessed: safe JSON statuses (include), bounded metadata GET (include), plain operator next steps (include), readiness dashboard (defer to existing Model Hub TODO), auto-model fallback (reject, contradicts owner).

Hour1 foundations: current source/history and secret-safe settings. Hours2-3: define metadata-only statuses,10-second transport/12-second envelope and zero retries. Hours4-5: B readiness artifact must be source/profile-bound and cannot substitute for actual live proof. Hour6+: real concurrent same-key schedule,503 preservation, false-success exit1 and full A. These are human-team hours; agent execution estimate1-2h is planning, not a measured completion claim.

## 1. Architecture

Keep FastAPI as the sole application authority and put provider metadata interpretation in apps/api. The explicit operator CLI has no browser-supplied model/endpoint or account data. B preflight reuses the same function and writes an immutable metadata artifact before its single browser generation; no DB transaction stays open for metadata.

```text
operator --check-model -> Settings -> typed readiness -> official SDK models.get (GET)
                                                |                  |
                                                +-- safe status <--+
Gate B authorized/current A -> readiness artifact -> ONE browser POST -> existing lifecycle
missing/empty key/model -> not_configured, no HTTP
bad local value -> invalid_configuration, no HTTP
upstream/timeout/empty metadata -> typed non-ready/unknown, never generated success
```

## 2. Error and rescue registry

| Codepath | Failure | Exception / observation | Rescue / operator sees |
|---|---|---|---|
| Settings | missing or invalid values | ValidationError without input serialization | not_configured/invalid_configuration; fix local config |
| Metadata GET |401/403/API_KEY_INVALID | SDK APIError | credential_error; check key/access, no secret body |
| Metadata GET |404 or explicit absent generateContent | APIError / supported_actions | model_not_supported for this operation/account; no automatic switch |
| Metadata GET |429 | APIError | rate_limited; wait and explicitly retry read-only check |
| Metadata GET |503/5xx | APIError | provider_unavailable; preserve status, do not call generation |
| Metadata GET |timeout / network | TimeoutError/HTTPX/OSError | timeout/unavailable with safe origin |
| Metadata decode |missing/mismatched model/limits | typed SDK response | unknown; incomplete evidence cannot mean ready |
| B preflight |not-ready metadata | EvidenceError | BLOCKED/nonzero; no browser paid request |

Catch only named failure classes and keep actual status/allowlisted reason/request IDs. Existing generation still handles malformed/refusal/empty response using its stricter separate contract; a metadata success cannot rescue a generation failure.

## 3. Security

The main new threat is accidental credential/raw provider-body exposure in a diagnostic command (medium likelihood/high impact). Emit only allowlisted scalar fields, never ValidationError input, exception repr, headers or .env. Fixed Google HTTPS endpoint, no redirects, no environment proxy, no arbitrary URLs/models from browsers, capped response transport and no tools prevent new execution/data authority. No public endpoint means no new cross-workspace read or abuse surface.

## 4. Data and interaction edges

Metadata is ephemeral diagnosis with timestamp, source/profile and a false generation_verified flag; it must never create a run or plan. Empty actions/limits/mismatched returned model produce unknown, not negative certainty or readiness. Existing generation double-click and network recovery retain exact UUID/GET-only handling; explicit retry uses a new recorded run after terminal confirmation. Navigation/expired sessions retain existing protected-state gates.

## 5. Code quality

Reuse the current CLI instead of a competing readiness executable and reuse bounded SDK transport/error metadata. The generation adapter is mature and already has retry/deadline contract tests; avoid refactoring it into a broad client framework. A small typed report plus explicit classification is easier to audit than a provider registry or model router. Document SDK-supported input versus actual account metadata rather than hardcoding a list as authority.

## 6. Tests

The required confidence test is one real PostgreSQL simultaneous exact-key schedule: one held provider call, a second202/running reference and one eventual complete graph. Hostile tests send malformed metadata/secret-bearing errors and prove no generation POST. Chaos coverage keeps mid-graph rollback, lost commit acknowledgement and stale-lease fencing from the baseline;503 and malformed output leave no new plan and prior approval unchanged. Live tests remain forbidden until the owner grants the next single attempt.

## 7. Performance

The new explicit operation has at most one GET, no pagination/loop/retry,10s transport and12s outer deadline. No database query or worker is added to application requests, and no readiness cache can imply a fresh successful generation. The slowest path remains the existing bounded provider generation; no p99 improvement is claimed from static analysis or one metadata roundtrip.

## 8. Observability

Readiness JSON records checked time, elapsed duration, exact requested/returned metadata name, safe status/code, SDK version and generation count0. Gate B captures this alongside profile/source, while actual run diagnostics remain the generation authority. The earlier collector AttributeError and restore-path diagnostic are preserved as exit1 tooling errors, not silently turned into successful metadata evidence. The corrected read-only response is separate.

## 9. Rollout

No migrations, dependencies, credential edits or public deployment are required. Run targeted deterministic tests and all A commands after final source edits; update documentation after the fingerprint stabilizes. Never revert the owner tree as a rollback: a future removal would touch only this task's intentional source diff with permission. Historical files stay byte-identical apart from the explicitly mutable latest-A pointer.

## 10. Trajectory

Metadata readiness is a narrow diagnostic interface, not a first version of Model Hub routing. It can later be reused after explicit Stage11 scope without granting other agents or automatic model selection. Current known limits remain lack of production certification, provider quota visibility and paid live success for changed source; report all three honestly. This plan should remain obvious to an engineer in12months because the status semantics and gate boundaries are explicit.

## 11. UX

Review the existing calm project panel and its configured/setup, waiting, failed/retry, status-unknown and persisted draft/approved states. No new badge should imply that a GET proved model generation. The operator readiness command belongs in setup documentation; existing browser error copy already distinguishes unavailability, rate limiting, timeout and validation. Preserve the brief, draft editor and approval across failed regeneration with real desktop/mobile/tablet tests.

```text
project -> explicit Generate -> waiting for ORBA -> persisted draft -> edit -> explicit approve
                              | error -> safe failed + brief kept -> GET confirm -> explicit Retry
                              | network unknown -> GET-only recovery (no second POST)
```

## Failure modes and completion

| Failure | Critical gap before implementation? | Required protection |
|---|---|---|
| Metadata mistaken for live PRD proof | Yes, if status is vague | Explicit ready_for_attempt + generation_verified=false |
| Readiness invokes generation | Yes | SDK GET-only transport assertion and no DB writes |
| Duplicate concurrent same key | Coverage gap | Forced schedule + independent graph count |
| Existing503/504 relabeled/fixed claim | Yes | Preserve immutable history and exact status |
| B uses old source or synthetic proof | Already guarded, extend | Source/profile/artifact audit and current A |

NOT in scope: model switch/fallback, readiness dashboard, polling, multi-provider Hub, orchestration, new password flows, recovery/MFA, public deployment and Stage04. Existing deferred TODOs already cover these broader concerns, so no duplicate TODO is created.

Completion: all11 sections evaluated, three alternatives compared, threat/error/failure registries and flows written. Implementation tasks are typed readiness/CLI, one-request B preflight evidence, additive deterministic tests, actual A/false-success execution and preservation/report. Independent voice/consensus follow before design begins.
