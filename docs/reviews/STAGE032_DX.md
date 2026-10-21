# Stage03.2 developer experience review

Mode DX POLISH. Target: Windows local owner/operator who already has ORBA, Docker, uv, Node and the ignored runtime configuration. The developer wants to know why generation failed and what a single authorized next attempt would do. No general SDK, hosted playground, public support or model marketplace is in scope. Review judgments are not executed command results.

## Persona and developer perspective

I open README.md and see Stage03 is PARTIAL even though the deterministic suite passed. I want to separate a missing key, wrong model and temporary provider failure before spending another attempt. The current config command can tell me that two values exist, but it cannot tell me whether Google recognizes the exact model for my credential. A green configuration-only exit is useful only if I understand that limit. I need a second explicit flag that performs a read-only check and leaves my projects and usage admission unchanged.

I work from the repository root in PowerShell. The documented uv command changes the child working directory into apps/api, so a diagnostic script must use the repository ROOT helper for evidence paths. I do not want to open .env in the terminal or paste its contents into a support transcript. If the provider rejects metadata, I need a safe category and the next action, not a stack trace containing input values. Once metadata is positive, I still need the exact Gate A fingerprint, timeout/output limits and one-generation Gate B command. The metadata response should reduce uncertainty about identity and access while leaving generation availability honestly unresolved. I will authorize the paid attempt separately; the tool must not treat my config flag as that permission.

## Journey and benchmark

| Stage | Current path / pain | Planned outcome |
|---|---|---|
|Discover|README PARTIAL explains the blocker|Link readiness next to runtime config|
|Evaluate|Config presence cannot establish account metadata|Explain offline, metadata and live evidence separately|
|Install|Existing uv/pnpm lockfiles|No dependency or SDK upgrade|
|Hello world|Current config-only output|One explicit --check-model GET, no generation|
|Integrate|Existing PM UI/API/PG|No new endpoint or frontend authority|
|Debug|503 vs timeout can be confused|Safe status/category, actual code/origin, next action|
|Upgrade|Uncommitted tree and immutable history|No migrations/hash/session changes; fresh A fingerprint|
|Scale|Local admission differs from provider quotas|Report effective1/3/6 budgets and unknown upstream quota|
|Migrate|Future provider choice is separate|No silent model switch or Model Hub|

The comparable provider surfaces are Google's official Models metadata API, the pinned Python SDK models.get, and the existing ORBA gate runner. Their actual cold-start onboarding times were not measured; do not present skill reference examples as competitor evidence. For this installed checkout, target metadata diagnosis is one command and at most12s network envelope plus Python startup, comfortably under a5-minute operator target. Cold installation and paid generation time remain unmeasured and cannot inherit that target.

The useful moment is a real, narrow metadata answer with explicit next steps, delivered through the existing command. A hosted playground, video, new install wizard or background monitoring would add cost and unrelated scope. The current real-list sample took412.136ms; that is one observation, not a p99 promise.

## 1. Getting started:8/10

Put offline and explicit metadata commands together immediately after provider env setup, using repository-root PowerShell commands. A developer should not need to inspect SDK internals or run a paid probe to resolve a model identifier. Preserve the no-argument command's compatibility and make help describe the new flag and exit codes. A10/10 future onboarding flow would also measure cold install across supported platforms; that is not claimed here.

## 2. CLI/API ergonomics:9/10

Use `uv run --directory apps/api python -m scripts.check_pm_config --check-model` instead of another loosely named readiness executable. No argument means no network; the explicit flag means one metadata GET, never generation. Keep existing offline configured0/missing1 behavior, metadata ready0/non-ready2, safe invalid-settings2 and argparse help0/unknown-option2. The typed status should carry more meaning than its process exit and be script-readable JSON.

## 3. Errors and debugging:9/10

Trace three concrete paths. Missing config currently prints named missing settings and false live-generation evidence; retain that safe guidance without exposing values. Wrong credential metadata should emit credential_error plus a check-key/account action, not the SDK body; upstream503 should emit provider_unavailable, actual503/upstream origin and explicit later check, not recommend longer local timeout. Unknown or malformed metadata should say the metadata could not establish readiness rather than suggesting a model was unavailable universally.

All settings validation output must omit input values and secret-bearing exception repr. Structured report includes time, elapsed duration, fixed provider, safe requested/returned name and nonsecret budgets. No debug flag should dump raw headers, cookies, provider bodies or .env. Documentation is the next context for an operator who needs deeper run IDs and historical failure records.

## 4. Documentation and learning:9/10

README supplies a three-level command table: configuration-only, explicit read-only metadata, separately authorized paid Gate B. Architecture defines status meanings and deadlines; VERIFICATION retains native exits, exact fingerprints, provenance and failure history. Examples must include the current effective output/time/admission caps and demonstrate that ready_for_attempt is not a completed PRD. Keep each receipt immutable and link the preserved password-policy record instead of replacing it without an archive.

## 5. Upgrade safety:9/10

No package, migration, password, session, provider endpoint or selected model changes are required. Tests add to existing baseline identities rather than replacing counts with a lower minimum. The actual source manifest includes uncommitted new code and tests, so a new A is mandatory even though HEAD remains e3fccd6. Old503/504 and prior real successes remain historical and cannot be retrospectively stamped with the new hash.

## 6. Environment/tooling:8/10

Native Windows PowerShell, uv and npm-pinned pnpm remain the supported executed path. The observed relative-directory collector/sketch failures justify using scripts.verification.ROOT and explicit cwd in reproduction. Gate A empties key aliases/model, runs backend and browser sequentially against guarded PostgreSQL and kills only its owned process tree. No readiness check is inserted into normal A; synthetic HTTP tests use only explicitly identified isolated doubles.

## 7. Ecosystem and trust:7/10

ORBA has no Git remote/public support SLA established here; do not invent an external community or issue workflow. The official Google SDK/API are the relevant integration ecosystem, and current provider pricing can inform a bounded authorization estimate without inventing an invoice or account tier. No API key is injected into browser docs/examples. Existing future Model Hub/community TODOs cover broader expansion and should not be duplicated.

## 8. Measurement and feedback:9/10

Source/profile-bound receipts, native exits, elapsed durations and actual structured test results already provide a strong local feedback loop. Extend them with a real metadata artifact, while preserving distinct model generation count0 vs1. The wrong-success experiment must still exit1 independently. No telemetry, public analytics or synthetic success metric is needed to judge whether the current local preparation succeeded.

## Scorecard and implementation checklist

| Dimension | Score | Gap to10 |
|---|---:|---|
|Getting started|8|Cold install timing unmeasured|
|CLI ergonomics|9|Execute help/offline/explicit/error contracts|
|Errors|9|Execute safe failure matrix|
|Documentation|9|Record actual final commands and links|
|Upgrade|9|Fresh A and preservation audit pending|
|Environment|8|Only current Windows/Chromium environment tested|
|Ecosystem|7|Local scope; no public support claim|
|Measurement|9|Current-source actual receipts pending|

- Implement explicit flag with no-network default and safe Settings validation.
- Put metadata dispatch in execute_gate(B) once, after opt-in/current-A/profile/port checks; `require_live_opt_in`/`execution_profile` must stay non-generative and network-free because the browser config rechecks preflight.
- Document exact root commands, exits, unknown semantics, effective budgets and one-generation paid scope.
- Run every old identity plus new tests; record native wrong-success1 separately and stop before paid execution.

NOT in scope: hosted sandbox, general client SDK, arbitrary provider URL, auto-model switch, analytics, public support or global tool repairs. Existing code to reuse: check_pm_config, Settings, LimitedTransport, error_metadata, execution_profile, source_manifest and A/B/C receipts. The product is ORBA, not a distributed skill; the skill-distribution appendix is inapplicable. Independent DX findings/consensus must be recorded before final engineering review.
