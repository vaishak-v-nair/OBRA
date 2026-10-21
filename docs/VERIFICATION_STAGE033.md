# ORBA Stage03.3 verification report

Recorded 2026-10-20. **Stage03: PARTIAL.** Preparation and deterministic verification completed. No paid generation was authorized or dispatched in Stage03.3. Gate A PASS; current-source Gate B NOT RUN; Gate C PARTIAL. The latest historical Gate B remains FAIL, not erased or relabeled.

## A. Root-cause analysis

The latest live SDK ServerError was upstream HTTP504 DEADLINE_EXCEEDED after **88,825.025ms** in the provider phase. The real run `c0078a43-d0ad-4036-93d6-5881ba886e66` ended failed with zero persisted plans. Original-session and admission transactions were released before the call. Validation and plan publication were never reached; failure-commit acknowledgment took11.984ms. This was not a browser/Next proxy timeout. An earlier upstream503 UNAVAILABLE took1,537.654ms, not a local90-second deadline. Returned model, provider response/request identifiers and usage were null; none is invented.

Provider capacity/scheduling, grammar compilation, output complexity or thinking allocation remain hypotheses. There is no provider trace establishing their contribution. LOW thinking was already configured, and no MAX_TOKENS result was received. Request-local clients close in finally; no measured pooling bottleneck justifies a global async-client change. Local changes do not establish a fix for upstream availability.

[Original failed B receipt](evidence/stage031/20261020T090120Z-B-0f70b66f/receipt.json), [unchanged complete prior report](VERIFICATION_STAGE032_LIVE.md), [dated investigation](STAGE033_PROVIDER_RELIABILITY.md).

## B. Supported model comparison

Exactly three bounded official SDK `models.get` requests returned HTTP200 on 2026-10-20 using the configured account:3.8 in565.264ms,3.6 in356.520ms,3.5 Flash-Lite in308.680ms. Each advertises generateContent, input 1,048,576 / output 65,536. No generation, countTokens, pagination or retry was performed. Metadata proves visibility and advertised methods only. Alternative readiness reports originally remained unknown under the then-current single-model documentation policy; those records were not rewritten after review.

|Exact identifier|Documented structured output / thinking|Assessment|Standard paid USD/M input; output including thinking|
|---|---|---|---|
|[gemini-3.8-flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)|JSON; low/medium/high; minimal unsupported|Owner's unchanged runtime selection; observed upstream failures here|$0.75; $3.75 through2026-12-31|
|[gemini-3.6-flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash)|JSON; minimal/low/medium/high|Recommended bounded alternative trial; live quality/reliability unverified|$0.75; $3.75 through2026-12-31|
|[gemini-3.5-flash-lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)|JSON; minimal/low/medium/high|Cheaper latency-oriented candidate; complex PRD quality unverified|$0.30; $2.50|

All three are currently stable with no announced shutdown. The 3.7 Flash and3.5 Flash aliases route to3.8/3.6 and are not independent alternatives. Pinned official google-genai 2.31.0 supports these string identifiers and the required request parameters; real-SDK synthetic HTTP tests verify serialization, not generation. [Account metadata evidence](evidence/stage033-research-20261020/model-metadata.json), [thinking](https://ai.google.dev/gemini-api/docs/generate-content/thinking), [pricing](https://ai.google.dev/gemini-api/docs/pricing), [lifecycle](https://ai.google.dev/gemini-api/docs/deprecations). Review scheduled3.8/3.6 price increases before2027-01-01 use.

## C. Recommended explicit configuration

Recommend **gemini-3.6-flash + minimal** for one separately authorized trial because it retains documented structured planning support while exposing a lower reasoning setting unavailable on3.8. This is a testable recommendation, not a demonstrated reliability improvement. Minimal does not guarantee zero thinking. The actual ignored runtime file remains3.8/LOW unchanged.

Keep 6,000 combined output/thinking tokens,48,000 input-content UTF8 bytes, one concurrent generation, candidate 1, SDK attempts1 and transport retries0. No automatic continuation, fallback or model switch. Current runtime server/model90s, transport95s, local envelope100s; browser response260s/test300s, Next proxy290s. The verification command900s includes startup, browser, SQL, editing and isolation, not a900s model deadline. Do not inflate all timers after an upstream error.

At today's standard published rate the 6,000 output/thinking-token component is at most **$0.0225** on3.6/3.8, or$0.015 on3.5 Flash-Lite. This is not a total request cap or actual bill: input tokenization, account/tier, taxes/currency and failure billing remain unknown. No token-count request was made.

## D. Changes made

|Important files|Responsibilities|
|---|---|
|`apps/api/orba/pm_models_policy.py`, `config.py`|Three explicit reviewed IDs, compatible thinking levels, LOW default, safe startup error redaction and configurable input byte limit; no model default/fallback|
|`pm_provider.py`, `prompts/product_manager_v2.txt`|Lean provider-only hints and concise versioned prompt; full ProductDocument validation, source/graph/security rules retained; exact shared UTF8 content accounting and pre-dispatch guards|
|`pm_service.py`|Reject oversized/invalid Unicode before admission, retain original generation configuration in safe diagnostics; exact authorized replay precedes changed-budget checks; original models/history remain immutable|
|`pm_readiness.py`, `scripts/check_pm_config.py`|Per-model reviewed documentation/configuration, safe errors, offline default; explicit bounded one-GET metadata remains non-generative|
|`scripts/verification.py`, `verification_baseline.json`|Thinking/input/provider-hint identity in profile/readiness/SQL audits; required identities extended additively to285 backend/33 controlled browser cases|
|`scripts/verify.ps1`, `scripts/verify-live.ps1`|Outer UTF8 console configuration; native exits and explicit live opt-in unchanged|
|`tests/test_pm_model_policy.py`, `test_pm_model_integration.py`|Real-SDK synthetic wire contracts and actual authenticated API/CSRF/PostgreSQL byte/history/failure/graph tests|
|`apps/web/tests-controlled/pm-recovery.spec.ts`|Actual API byte422 before run admission; brief/instructions/context/approved plan retained, explicit recovery across desktop/mobile/tablet|
|README, AGENTS, ARCHITECTURE, ROADMAP, dated investigation/reviews/test plan|Operator configuration, boundaries, exact workflow and current evidence; no unrelated UI redesign|

No schema migration, dependency/lock change, password/hash/session policy change, project-data rewrite or new agent. Offline prompt bytes2935->2642; provider hint3892->3489, anyOf7->2, properties54->47. Authoritative ProductDocument schema and original promptv1 are unchanged. These are byte/grammar measurements, not billed token counts, live quality or latency improvements. [Offline comparison](evidence/stage033-research-20261020/offline-after.json).

## E. Actual deterministic results and commands

`pwsh -NoProfile -File scripts/verify.ps1` exited **0**. Started2026-10-20T16:24:58.2399232Z, completed16:34:52.5793545Z. All 14 commands below actually executed sequentially; backend and browser suites use the guarded real PostgreSQL orba_test database. The command environment empties both credential aliases and model. All original Stage01/02, password, PM, isolation, concurrent/replay, recovery and evidence-integrity test identities are retained. Controlled/synthetic provider responses prove application behavior only.

**285 backend passed;60 core browser passed;33 controlled-provider browser passed. Zero skipped, xfail, flaky or retried cases.** The backend reports one upstream-SDK Python deprecation warning, not a failed check. Browser color-environment warnings are retained in logs. Browser coverage is Chromium desktop/mobile/tablet emulation, not native/all-browser certification.

|Gate A child|Actual command|Exit|Seconds|
|---|---|---:|---:|
|database|`docker compose -f infra/compose.yaml --profile test up -d --wait test-postgres`|0|0.988|
|python-lock|`uv sync --locked --directory apps/api`|0|0.038|
|frontend-lock|`npm exec --yes --package=pnpm@12.14.0 -- pnpm install --frozen-lockfile`|0|1.263|
|peers|`npm exec --yes --package=pnpm@12.14.0 -- pnpm peers check`|0|1.116|
|migration|`uv run --directory apps/api alembic upgrade head`|0|1.532|
|schema-drift|`uv run --directory apps/api alembic check`|0|1.479|
|backend|`uv run --directory apps/api pytest -q --junitxml=E:\BrosKi\OBRA\docs\evidence\stage031\20261020T162458Z-A-dca02afc\backend.xml`|0|65.037|
|ruff|`uv run --directory apps/api ruff check .`|0|1.637|
|format|`uv run --directory apps/api ruff format --check .`|0|0.076|
|typecheck|`npm exec --yes --package=pnpm@12.14.0 -- pnpm typecheck`|0|5.063|
|eslint|`npm exec --yes --package=pnpm@12.14.0 -- pnpm lint`|0|50.345|
|build|`npm exec --yes --package=pnpm@12.14.0 -- pnpm build`|0|10.788|
|core-browser|`npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e`|0|187.632|
|controlled-browser|`npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:controlled`|0|261.452|

[Immutable A receipt](evidence/stage031/20261020T162458Z-A-dca02afc/receipt.json), [outer native exit](evidence/stage033-gate-a-command-20261020T162458Z/native-exit.json), [backend output](evidence/stage031/20261020T162458Z-A-dca02afc/backend.log). Receipt SHA256: `26b645c85a516fd84f41c5f9b3be42f464af96bfefbfcd978f0f878f73107f19`.

Earlier targeted outcomes are preserved rather than overwritten:

|Evidence directory / operation|Actual exit / result|
|---|---|
|stage033-targeted-20261020T142343Z-19e821|Scoped Ruff fix0/format0; database1 missing Linux-engine pipe; tests NOT RUN|
|stage033-docker-start-20261020T142435Z-88eb37|Managed Desktop start0, not proof of a stable daemon|
|stage033-targeted-20261020T142551Z-2e8dec;142725Z-78e0b6|Database1 each; tests NOT RUN|
|stage033-targeted-20261020T142837Z-78e954|Database0; backend1:22 failed /133 passed /15 errors; fixture expected wrong nested wire key and Desktop disappeared during PG tests|
|stage033-local-checks-20261020T161548Z-4fc33e|Unit contracts0:117 passed; collection0:285 collected (not pass evidence)|
|stage033-targeted-20261020T161914Z-08ee3f|Database0/format0/backend0:170 passed|
|stage033-browser-20261020T162109Z-76209a|Focused controlled browser0:3 passed|
|Real-pg wrong-success experiment|1, expected; actual incorrect assertion detected|
|Network-free Gate C summary|2, PARTIAL|
|Source/artifact/credential preservation audit|0|
|Offline current and proposed model CLI|0 each; status unknown,0metadata/0generation requests|
|Initial offline evidence collector|1:KeyError for nonexistent network_request_made field after CLI0; corrected using actual typed counts without source changes|

The actual pinned SDK nested key is `thinking_level`; the corrected test still requires the exact model/explicit thinking/bounds/one call. No assertion was removed. Docker logs showed an explicit Desktop shutdown and disappearing engine pipe; its initiator is unknown. The dependency was restored without replacing PostgreSQL or altering development data. Earlier failing receipts remain intact. The targeted subsets overlap the full suite and are not added to its counts.

## F. Negative-path and false-success evidence

Gate A confirms synthetic SDK HTTP503/504 -> truthful failed runs, zero new/partial plan graph and unchanged approved plan/actor/time/hash. Malformed JSON, invalid/incomplete PRD structure, forbidden human provenance, truncation and invalid Unicode fail safely. Same-key simultaneous requests dispatch once; explicit new-key retry is auditable; partial graph rollback is independently invisible; unrelated requests cannot change an earlier failure. Workspace/project/run/plan authorization and login/CSRF/roles/legacy protections remain real-PG tested. Evidence tests reject stale/controlled/tampered success and failed child commands.

The isolated `uv run --directory apps/api python -m scripts.verify_false_success` exited **1** after a real API configuration failure and independent PostgreSQL run read. Actual assertion: `assert 'failed' == 'succeeded'`; output **1 failed, 1 warning**. The harness detected that exact incorrect assertion. It is outside normal test discovery and is neither an application regression nor a passing production test. [Experiment receipt](evidence/stage031/20261020T163512Z-wrong-success-b0919537/experiment.json), [actual assertion log](evidence/stage031/20261020T163512Z-wrong-success-b0919537/wrong-success.log), [native exit](evidence/stage033-closure-20261020T163512Z/false-success-native-exit.json).

## G. Source fingerprint and evidence integrity

```text
661f2828f7adbdc368a31616280ebec5d27048b2dc6f9feb1ecada06505b282d
```

127 relevant source files. Start/end/current manifests match; A was independently validated after execution. Prior baseline `2a2128d0f21c914b4640db6eb7c31ddf446ad00076a9a28e52d03bfcbe44b098` remains historical. Thirteen existing relevant files changed, four added, none removed; all other intake source files including auth/workspace/password/migrations/locks and promptv1 retain their hashes. HEAD remains e3fccd63e88162065189b00be1696617f616eea3. No commit/discard/reset.

Of 588 pre-existing evidence files,587 remain byte-identical; only documented mutable latest-A advanced. No historical receipt or latest-B was modified. Root .env bytes and API .env absence remain unchanged. Prior VERIFICATION was archived byte-for-byte against intake hash before the current status was added. Literal configured-key scan found0matches in767 Git-visible files at audit time; this is not a full security certification. See the actual audit for the exact scanned count.

[Preservation/source/profile audit](evidence/stage033-closure-20261020T163512Z/preservation-and-gate-a-audit.json), [final documentation/source check](evidence/stage033-closure-20261020T163512Z/post-documentation-check.json), [intake](evidence/stage033-intake-20261020T092221Z/intake.json), [network-free Gate C output](evidence/stage033-closure-20261020T163512Z/gate-c-console.log), [Gate C native2](evidence/stage033-closure-20261020T163512Z/gate-c-native-exit.json). Gate C correctly retains historical B FAIL and Stage03 PARTIAL. No current-source B has been executed.

## H. Prepared one-request live verification / reproduction

From the repository root, with Docker Desktop running and this checkout's development Next server stopped:

```powershell
pwsh -NoProfile -File scripts/verify.ps1
uv run --directory apps/api python -m scripts.verification summary
# Expected while B lacks a matching pass: summary exit2/PARTIAL.
uv run --directory apps/api python -m scripts.verify_false_success
# Expected deliberate incorrect assertion: exit1, outside mandatory suites.
```

Both current3.8/LOW and temporary child-shell3.6/minimal settings were actually checked offline and exited0; each accurately reports unknown readiness, metadata_requests0 and generation_requests0. [Command receipt](evidence/stage033-closure-20261020T163512Z/offline-configuration-checks.json), [preserved collector error](evidence/stage033-closure-20261020T163512Z/offline-collector-first-error.json). No runtime file was edited.

Offline configuration inspection (no external request):

```powershell
uv run --directory apps/api python -m scripts.check_pm_config
```

**Do not execute the following without fresh explicit authorization for this model and one paid attempt. These are proposed shell overrides, not edits already made.**

```powershell
$env:ORBA_PM_MODEL = 'gemini-3.6-flash'
$env:ORBA_PM_THINKING_LEVEL = 'minimal'
$env:ORBA_PM_TIMEOUT_SECONDS = '90'
$env:ORBA_PM_MAX_OUTPUT_TOKENS = '6000'
$env:ORBA_PM_MAX_INPUT_BYTES = '48000'
$env:ORBA_PM_MAX_CONCURRENT = '1'
pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid
uv run --directory apps/api python -m scripts.verification summary
```

The live gate requires a matching passing A, captures source/profile/A-receipt linkage, runs one bounded read-only metadata GET, then one browser worker with retries0. At most one actual generation POST is forwarded; a second attempted POST is aborted before dispatch and fails B. SDK attempts1/transport0, candidate1, no continuation/tools. Use the existing small habit-tracker brief and the **same** real resulting plan for strict validation, API graph retrieval, independent fresh SQL draft audit, browser display, human acceptance-criterion edit/reload, explicit exact-version approval/reload, independent SQL approval graph/hash audit and unrelated-user denial. No extra generation probe or second plan is created by verification. Any provider/validation/DB/browser failure stops the attempt without fallback/retry. Do not promise successful generation.

## I. Remaining limitations

Live generation, new pm-v2 semantic quality, minimal-thinking output completeness/latency, schema acceptance and actual quota on the proposed model remain unverified. Read-only metadata cannot establish these. Historical live successes cannot certify changed provider/prompt/lifecycle code. The next paid attempt requires fresh owner authorization; none was consumed here. Actual billing and remote cancellation after request dispatch remain uncertain.

The static reviewed policy needs deliberate review when Google changes models/lifecycle; unsupported configuration intentionally fails startup safely. The48,000-byte content guard excludes protocol overhead and is not a token bill. Test emulation/local owner-controlled receipts are not native-device coverage or hostile-machine attestation. Existing local-development authentication/security limitations remain documented; no production certification is claimed. The SDK deprecation warning remains visible. No Stage04, new provider router, other agent or public deployment.

## J. Stage03 verdict

**PARTIAL.** Gate A PASS/native0 on the new source. Current-source live Gate B NOT RUN; latest historical B FAIL/upstream504, with prior503/504 preserved. Gate C PARTIAL/native2. A future single authorized, matching-source Gate B must actually pass generation/schema/persistence/editing/approval/isolation before VERIFIED is permitted.
