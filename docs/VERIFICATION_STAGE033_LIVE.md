# ORBA Stage03.3: authorized live A/B/C report

Recorded 2026-10-20. **Stage03 verdict: VERIFIED** for the source and explicit `gemini-3.6-flash` / `minimal` profile below. The owner authorized one bounded generation. Exactly one was dispatched, it succeeded, and no retry, fallback, model switch, continuation or further generation occurred. This result does not erase historical503/504 failures or establish a provider uptime guarantee.

## A. Deterministic gate and source identity

Gate A **PASS**, original native exit **0**; all **14 commands exited0**, with **285 backend,60 regression browser and33 controlled-provider browser tests passed**. No mandatory skips, xfail, flaky or retried cases. Auth/workspace/legacy/password/project/PM negative-path coverage remains included. Controlled/synthetic provider tests are deterministic application evidence, never live-model evidence.

A was independently revalidated before and after this attempt. It was not rerun against a different implementation: no relevant source file changed. The verified start/end/current manifest contains127 files:

```text
661f2828f7adbdc368a31616280ebec5d27048b2dc6f9feb1ecada06505b282d
```

[A receipt](evidence/stage031/20261020T162458Z-A-dca02afc/receipt.json), SHA256 `26b645c85a516fd84f41c5f9b3be42f464af96bfefbfcd978f0f878f73107f19`. The complete actual14-command table and earlier targeted failures/fixes remain in [the preparation report](VERIFICATION_STAGE033.md).

## B. Authorized real Gemini gate

**PASS**, native exit **0** from exactly one invocation:

```powershell
$env:ORBA_PM_MODEL = 'gemini-3.6-flash'
$env:ORBA_PM_THINKING_LEVEL = 'minimal'
pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid
```

Outer command started2026-10-20T16:51:08.0060279Z and completed16:51:48.9556964Z. [Native exit](evidence/stage033-authorized-live-20261020T165054Z/live-native-exit.json), [actual console](evidence/stage033-authorized-live-20261020T165054Z/live-console.log), [authorization/intake](evidence/stage033-authorized-live-20261020T165054Z/authorization-intake.json).

|Actual B child command|Exit|Seconds|
|---|---:|---:|
|`uv run --directory apps/api python -m scripts.check_pm_config --check-model`|0|1.424|
|`npm exec --yes --package=pnpm@12.14.0 -- pnpm test:e2e:live`|0|33.727|

The first command performed one bounded read-only SDK model metadata GET. It did not generate a plan. The subsequent browser flow made the single actual SDK generation, using the production provider adapter and real application auth/API/PostgreSQL. No provider double or fabricated response was used. One browser worker, retries0; transport retries0, SDK attempts1, candidate1, no automatic continuation/tools/function calling. The pass-through request allowance recorded attempted1/forwarded1/blocked0; any second POST would have failed before dispatch. No separate generation probe was used.

[B immutable receipt](evidence/stage031/20261020T165108Z-B-88c8d84b/receipt.json), SHA256 `5d64a767a291579c85f165947bea525c845992ff8507d6b713fb43fed868a7fd`. [Complete real browser proof](evidence/stage031/20261020T165108Z-B-88c8d84b/live-proof.json), [structured browser report](evidence/stage031/20261020T165108Z-B-88c8d84b/live-browser.json), [actual browser log](evidence/stage031/20261020T165108Z-B-88c8d84b/live-browser.log). Browser result: **1 passed**, zero failures/skips/retries. Core desktop/mobile/tablet coverage remains the applicable passing Gate A; this single live flow uses desktop Chromium.

### Actual model and execution evidence

|Field|Actual recorded value|
|---|---|
|Provider / SDK|google-gemini / google-genai2.31.0|
|Requested model|gemini-3.6-flash|
|Returned model|gemini-3.6-flash|
|Thinking setting|minimal|
|Combined output/thinking limit|6000tokens|
|Concurrency / retries|1 /0|
|Provider / transport / envelope deadline|90s /95s /100s|
|Content input cap / measured content|48000 /6786 UTF8bytes; not provider-token estimates|
|Prompt version|pm-v2|
|Run ID|3079738f-3dd5-43f5-bc59-ded3362de3a3|
|Project ID|e256e2ed-95f0-4e14-b4b3-ade741ec1348|
|Plan ID|1acc58d7-4d76-4234-8399-27411dd29708|
|Provider response ID|GJzXavy_AdLtg8UPqLuBiAw|
|Provider request ID|null; not supplied|
|Provider call duration|8491.347ms (8.491347s)|
|Strict output validation duration|1.394ms|
|Relational persistence flush duration|31.676ms|
|Acknowledged publication transaction|55.261ms, separately logged|
|Input tokens|684|
|Candidate output tokens|1072|
|Total tokens|1756|
|Separate thinking-token usage|Not returned; not invented as zero|
|Final run / public generation response|succeeded /HTTP201|

Usage is actual provider metadata, also retrieved independently from PostgreSQL; no actual dollar charge is inferred. [Post-browser fresh SQL output](evidence/stage033-authorized-live-20261020T165054Z/approved-sql-fresh.json). The provider phase succeeded in this one sample; it does not establish which code/configuration change caused the improvement over earlier failures.

### Schema, persistence, editing, approval and isolation

|Mandatory check|Actual evidence|
|---|---|
|Strict real-output validation|Authoritative Pydantic/source/graph validation passed before atomic draft publication; no fallback or example content|
|Initial draft|Version1, revision1, approver/timestamp null; independent SQL reconstructed and validated the graph and source snapshot|
|Relational graph|1epic,1story,2acceptance criteria; linked IDs/counts/content hash match API and fresh SQL|
|Draft API/SQL hash|`6cacde2013d400b6d3c0513e7f482cbefe7f0ef40c11164766bc1a5c14a110fb`|
|Browser content|Actual persisted generated draft displayed through the real frontend/API|
|Edit and reload|Owner changed a criterion through the UI; PUT returned200; exact edited criterion remained after reload|
|Explicit approval and reload|Separate Approve/Confirm actions; approved state persisted after reload|
|Approved version/revision|1 /2|
|Approver|09c6bd65-4543-4c98-af23-3258d9f07642|
|Approval timestamp|2026-10-20T16:51:42.466719Z|
|Approved API/SQL hash|`cdab65de285cf00397e76426f824088ab989a692f73775b0260caa8366b1354e`|
|Fresh independent approved SQL|New process/session after browser exit: same run/plan/model/usage/hash/graph, actor, version/revision and timestamp; native0|
|Workspace isolation|A separate real user/workspace received HTTP404 from the plan API; the project UI showed Project not found and did not render the edited criterion|
|No unintended duplicate|One generation POST, one provider attempt, exactly one project plan; same plan used through all checks|

The run became succeeded only after validation and atomic publication. Editing did not silently regenerate or replace the plan. Existing source-bound negative-path and isolated wrong-success evidence remain unchanged: HTTP503/504/malformed/invalid output cannot publish success; the deliberately incorrect failed==succeeded assertion previously exited1 and is not part of the normal green suite. It was not rerun after B because doing so would reset the shared isolated test database.

## C. Verdict, preservation and command exits

`uv run --directory apps/api python -m scripts.verification summary` ran under the **same explicit3.6/minimal profile**, exited **0** and calculated **VERIFIED** after independently validating A/B source, profile, command/results and immutable artifacts. [Actual Gate C output](evidence/stage033-authorized-live-20261020T165054Z/gate-c-console.log), [native exit](evidence/stage033-authorized-live-20261020T165054Z/gate-c-native-exit.json).

|Command or check|Actual exit|
|---|---:|
|Read-only source/A/profile/intake validation|0|
|Read-only Docker test-postgres health inspection|0|
|Authorized pwsh verify-live invocation|0|
|Native read-only SDK readiness child|0|
|Native real-model browser child|0|
|Network-free Gate C summary|0|
|uv run --directory apps/api python -m scripts.inspect_pm_run --run 3079738f-3dd5-43f5-bc59-ded3362de3a3 --expect-state approved|0|
|Independent evidence/source/SQL/preservation audit|0|

[SQL native exit/duration](evidence/stage033-authorized-live-20261020T165054Z/approved-sql-native-exit.json), [source/profile/preservation audit](evidence/stage033-authorized-live-20261020T165054Z/verification-and-preservation-audit.json).

Before current documentation was updated, **771 of772 prior Git-visible files remained byte-identical**. Only documented mutable latest-B advanced. All historical receipts, including503/504 failures and old failed latest-B receipt, remained unchanged. Relevant source, dotenv presence/bytes, Git HEAD and index were unchanged. Current README and VERIFICATION were archived byte-for-byte before status updates; the final audit records these two intentional documentation changes separately. No source implementation or original project data was changed; browser setup resets only guarded orba_test per the existing contract. No commit/discard, credential change, public deployment or Stage04.

The ignored root.env remains byte-identical with the prior3.8/LOW setting. This successful live evidence applies to the authorized **3.6/minimal environment overrides**, not a claim that unchanged3.8 now succeeds. To revalidate the evidence without another model call:

```powershell
$env:ORBA_PM_MODEL = 'gemini-3.6-flash'
$env:ORBA_PM_THINKING_LEVEL = 'minimal'
uv run --directory apps/api python -m scripts.verification summary
```

Do not run verify-live again: this authorization has been consumed. Further paid requests require fresh owner authorization. A different source or runtime profile cannot inherit this passing B. Local-development security, emulated browser and model semantic/reliability limitations remain documented. One passing live sample is not an SLA or production-security certification.

**Stage03: VERIFIED.** Stop after Stage03.
