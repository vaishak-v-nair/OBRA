# Stage03.3 provider reliability investigation

Investigation date: 2026-10-20. Stage03 remains PARTIAL. No model-generation request is authorized in this preparation task. Historical receipts are immutable; new evidence does not erase earlier failures.

## Findings versus hypotheses

| Observation | Evidence | What it establishes |
|---|---|---|
|Latest actual SDK request returned upstream504 DEADLINE_EXCEEDED|stage031/20261020T090120Z-B-0f70b66f receipt and API log; run c0078a43-d0ad-4036-93d6-5881ba886e66|Provider phase88,825.025ms, error_origin upstream_http, failed run,0plans; not a Next/browser timer firing|
|Previous503 UNAVAILABLE took1,537.654ms|stage031/20261019T170920Z-B-26bec4ac|Temporary upstream unavailability, not expiration of a90s local timer|
|Model/schema/usage identifiers unavailable on failed response|Independent READ ONLY SQL graph audits in stage032-authorized-live-20261020T090047Z|No model output or plan was fabricated; null usage cannot be priced as actual usage|
|Current SDK configuration is bounded|pm_provider.py and SDK transport tests|One candidate, attempts1, transport retries0, no tools, function calls or automatic continuation|
|Model metadata is reachable today|stage033-research-20261020/model-metadata.json|Three exact-model GET200 responses; advertised generateContent, not generation success|

The latest failure happened before response validation or plan persistence. Therefore neither a slow validation pass nor a plan-write transaction explains this recorded88.825s provider phase. The original session and database transaction are released before the model call. The API records separate admission/running/provider/validation/persistence timings; failure-commit acknowledgment in that attempt took11.984ms. The Next proxy did not substitute a model result.

Possible provider capacity/scheduling, generation complexity, reasoning allocation or grammar compilation costs remain hypotheses. No provider-side trace identifies their contribution. The request supplied LOW thinking already; a6000 combined thought/output cap can truncate output but no MAX_TOKENS response was received in these503/504 attempts. Smaller grammar or minimal thinking may reduce avoidable work; their latency/quality effects remain unmeasured. Do not present them as a demonstrated fix.

## Model comparison

These are three reviewed stable identifiers, not an automatic routing order. All three exact read-only SDK GETs succeeded using the configured account on2026-10-20; each advertises generateContent, input1,048,576 and output65,536 tokens. Metadata establishes neither quota nor successful schema acceptance/generation. SDK2.31.0 represents model IDs as strings and exposes the required structured-schema and thinking-level parameters; deterministic wire tests must exercise the actual SDK. No SDK update is needed solely to recognize these IDs.

| Model | Structured output / thinking | Fit and tradeoff | Standard paid USD / million input; output including thinking |
|---|---|---|---|
|gemini-3.8-flash|Documented JSON; low/medium/high, minimal unsupported|Owner's current model; broad complex-planning capability, observed upstream failures here|$0.75; $3.75 through2026-12-31|
|gemini-3.6-flash|Documented JSON; minimal/low/medium/high|Recommended **bounded trial**, balancing planning capability with an available lower reasoning setting; live reliability not established|$0.75; $3.75 through2026-12-31|
|gemini-3.5-flash-lite|Documented JSON; minimal/low/medium/high|Lower-cost/latency-oriented option; rich product traceability/quality unverified, so secondary recommendation|$0.30; $2.50|

Each is currently listed as stable with no announced shutdown date. Do not choose3.7/3.5 Flash aliases to pretend to diversify: Google documents provider-side routing to3.8/3.6 respectively. The2.5 family is not a preferred new option because Google currently restricts access to prior active users. None of these metadata results proves an SLA or a billable operation's accessibility.

Sources, reviewed2026-10-20: [3.8 capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [3.6 capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash), [3.5 Flash-Lite capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite), [Generate Content thinking levels and combined token cutoff](https://ai.google.dev/gemini-api/docs/generate-content/thinking), [pricing](https://ai.google.dev/gemini-api/docs/pricing), [lifecycle](https://ai.google.dev/gemini-api/docs/deprecations). Use specific model pages over older generic guides where their defaults differ. Pricing for3.8/3.6 is scheduled to increase2027-01-01; review before later use.

## Request path and bounds

```text
browser (test300s, response260s; UI300s)
 -> Next same-origin proxy290s
 -> FastAPI short admission transaction, model phase (no DB transaction held)
 -> Google SDK server/model90s -> transport95s -> asyncio envelope100s
 -> strict JSON/Pydantic/source/graph validation
 -> original-session and workspace recheck -> atomic draft/run publication
```

The server/model budget is configurable5-180s, transport adds5s and local envelope10s. Running lease adds45s; publication has a285s outer backstop. Verification's command deadline900s also includes server startup/browser setup/SQL/editing/approval/isolation, not a900s model request. These bounds already leave room above the model phase. Do not raise every timer to disguise upstream503/504. HTTP503 stays provider_unavailable; upstream504 stays provider_timeout with upstream_http origin, distinct from transport_timeout/local_envelope_timeout. The synchronous API cannot cancel a remote bill after bytes have been sent, and disconnects require GET-only outcome confirmation.

The adapter creates a fresh async client per generation and closes it in finally. Within a request the transport owns its pool. No measured connection establishment bottleneck justifies cross-request pooling, especially with separate asyncio.run lifetimes and low local concurrency. No automatic retry/continuation/model switch is introduced.

## Proposed bounded trial and cost

Recommend a separately authorized explicit gemini-3.6-flash/minimal trial,6000 combined output/thinking tokens,90/95/100s deadlines, concurrency1, one browser worker and zero retries. Minimal is a relative reasoning allowance, not a guarantee of no thinking. Keep the same small habit-tracker brief and single-epic/story instructions in the existing live test. Reuse that one actual plan for validation, independent SQL, browser rendering, editing, approval/reload and outsider denial.

At the current published standard rate,6000 output/thinking tokens correspond to **at most$0.0225 for that token component** on3.6/3.8, or$0.015 on3.5 Flash-Lite. This is not a full-request bill or promise: actual input tokenization, account tier, taxes/currency and failure billing remain unknown. No countTokens request was made. Request-byte admission is a local size bound, not a token measurement or total dollar ceiling.

## Implementation and verification

See [the implementation plan](STAGE033_PLAN.md), sequential review artifacts in docs/reviews, and [the full A-J verification report](VERIFICATION_STAGE033.md). Gate A actually exited **0**: all 14 commands succeeded, with **285 backend, 60 regression browser and 33 controlled-provider browser tests passed**, no skips/retries. The isolated deliberately incorrect success assertion exited **1**; Gate C exited **2/PARTIAL**. Gate B is deliberately not run here; fresh explicit authorization is required.

The start/end/current source fingerprint is `661f2828f7adbdc368a31616280ebec5d27048b2dc6f9feb1ecada06505b282d` (127 relevant files). [A receipt](evidence/stage031/20261020T162458Z-A-dca02afc/receipt.json), [preservation/profile audit](evidence/stage033-closure-20261020T163512Z/preservation-and-gate-a-audit.json). All historical receipts remain unchanged: 587 of 588 prior evidence files are byte-identical and only the documented mutable latest-A pointer advanced. Root .env, API dotenv presence and HEAD are unchanged. No paid model-generation or token-count request was made.

Both current 3.8/LOW and proposed 3.6/minimal settings passed the actual **offline** CLI with exit 0 and `status=unknown`, `metadata_requests=0`, `generation_requests=0`, `live_generation_verified=false`. Only temporary child-shell values were used; no runtime file was changed. This proves configuration acceptance, not provider availability. [Offline command receipt](evidence/stage033-closure-20261020T163512Z/offline-configuration-checks.json). An initial evidence collector expected a nonexistent boolean field and exited1 after the CLI had exited0; its error/log were preserved, and the corrected collector validates the actual typed count fields without weakening assertions or changing source.
