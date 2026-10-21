# Stage03.2 independent strategic review

Date: 2026-10-19. This is one independent in-host Codex-family voice, not a cross-model consensus. Review scope is the repository plan, provider adapter, config preflight, verification runner and recorded metadata. No paid request, live model call, credential read/output, source edit or test execution was performed by this reviewer. This review file is the only authored artifact.

Recommendation: proceed with an explicit operator-only metadata check, deterministic verification and a concrete authorization handoff. Keep Stage03 PARTIAL and stop before Gate B. A new browser readiness feature is not necessary for this scope.

## Problem and premise check

The actual unresolved acceptance problem is provider execution availability on current source. The preserved latest authorized attempt received upstream 503; an earlier Full 504 and earlier successful live calls remain separate outcomes. A metadata check can remove uncertainty about configured model identity and advertised actions. It cannot remove the uncertainty about generation, schema acceptance, LOW thinking configuration, quota, latency or atomic persistence.

The recorded `docs/evidence/stage032-model-metadata.json` reports one successful read-only model-list request, the exact configured `gemini-3.8-flash` entry with `generateContent`, and zero model-generation requests. Its source fingerprint matches the password-policy baseline recorded in VERIFICATION.md. These are point-in-time metadata facts, not current Stage03.2 live-generation evidence.

The existing browser already says that a configured key does not guarantee model access, warns that generation can incur usage, and requires a deliberate retry after exact-run recovery (`apps/web/src/components/product-plan.tsx:124`, `:179`, `:181`, `:189`). Adding another browser state does not resolve the observed upstream failure. The proposed CLI extension is the smaller useful product change.

## Findings and concrete fixes

### M1 — Medium: written scope still implies a browser readiness feature

`docs/STAGE032_PLAN.md:10` calls for operator/browser checks and `:23` names auth/project dependencies and the Next proxy. This leaves an endpoint or new browser status surface implied even though the proposed implementation is `scripts.check_pm_config --check-model`. That ambiguity can grow the change into a second generation-admission authority and expand the auth/network state under test.

Fix: amend S3 and the initial approach to specify the explicit operator CLI. Preserve the existing default config-only command and browser behavior. Add a browser change only if the design review identifies a concrete existing user error that cannot be addressed by the current setup/error/recovery flow. No metadata fetch on page load, no new provider dashboard and no metadata-based permission to generate are needed.

### M2 — Medium: readiness needs an exact, limited success contract

The current preflight correctly returns `live_generation_verified: false` but only checks config presence (`apps/api/scripts/check_pm_config.py:8-41`). The plan's boundary is sound, but it does not yet define the new metadata operation's result and exit semantics. A generic `ready: true` would overstate the result even when the latest generation failed.

Fix: define a typed metadata-only result with observation time, requested/returned model identity, advertised supported actions, a safe outcome/category, and `live_generation_verified: false`. Normalize only the optional `models/` prefix and require exact configured identity plus `generateContent`. Missing config, missing/mismatched metadata, unsupported action, upstream rejection, transport failure and timeout must remain distinguishable non-successes. Do not infer quota or grammar support. Use one bounded official-SDK metadata request with retries disabled; retain safe allowlisted diagnostics rather than exception bodies. Prove default invocation performs no network request and the explicit flag cannot call generation or create a run/admission record. Identified test-only HTTP doubles establish adapter/error handling, never live readiness.

### M3 — Medium: the paid handoff must be an executable, current evidence package

S5/S8 name the handoff but do not yet state its final acceptance checklist. The existing verifier already requires a passing current-source A and real configuration (`apps/api/scripts/verification.py:471-481`), and checks that B contains exactly one genuine successful browser generation plus SQL/approval/isolation evidence (`:272-325`). The metadata result must not replace either gate or become a reason to repeat a paid probe.

Fix: after final source changes, attach the actual Gate A receipt/fingerprint, native exits and report counts; record the isolated wrong-success experiment's expected actual exit 1 separately; include the exact `pwsh -NoProfile -File scripts/verify-live.ps1 -AllowPaid` command and its one-generation browser/SQL scope. Review the last 503 diagnostics and the effective nonsecret execution profile before asking for authorization. Preserve the latest-B pointer and all historical artifacts during this unpaid task. Ask for one next bounded attempt only after this package is concrete, then stop. A later failure still consumes that authorization; it does not permit a retry.

### M4 — Medium: portable defaults differ from the owner's local budget

The documented local profile is one concurrent request, three attempts/account/hour, six globally/hour and a 90-second server timeout. Code defaults are two/five/twenty and 60 seconds (`apps/api/orba/config.py:21-32`; `docs/ARCHITECTURE.md:95`). This is documented, not a newly discovered runtime violation. In six months, copied configuration or lost overrides could silently change both usage exposure and timeout behavior.

Fix within this stage: include the effective nonsecret limits and T/T+5/T+10 deadlines in the operator handoff, using the existing `execution_profile()` where practical. Compare them with the owner's intended profile before paid authorization. Preserve credentials and current defaults unless a separately justified source change is needed; do not introduce credential fingerprints, billing guesses or automatic config repair.

## Alternatives and six-month risks

- Minimal alternative: keep only the existing recorded metadata evidence and config command. This is sufficient to explain the present identity question, but leaves no repeatable supported operator check when access changes.
- Recommended: add the bounded explicit metadata CLI and focused deterministic tests. Keep generation lifecycle, UI authority and A/B/C semantics intact. It makes the uncertainty inspectable without adding another product state machine.
- Longer-term alternative: richer availability monitoring, background execution or another provider could address different reliability goals, but requires new owner decisions about cost, authority and recovery. None belongs in Stage03.2.

The main six-month risks are changing model availability/advertised capability, SDK behavior drift, configuration-budget drift, and a successful metadata result being reused as an availability guarantee. Timestamped narrow results, pinned SDK/source evidence and the existing explicit live gate address these risks proportionately. No finite metadata TTL can guarantee that a subsequent generation succeeds. Do not add polling or a circuit breaker to create that impression.

## Six-dimension assessment

| Dimension | Assessment | Completion condition |
|---|---|---|
| Problem fit | Sound when framed as diagnostic readiness; upstream availability remains open | Name the exact uncertainty removed and retain the provider blocker |
| Completeness | Conditional | Specify result/error contracts, focused tests, preservation audit and final handoff |
| Consistency | Sound gates; scope wording needs alignment | Make CLI-only scope explicit and keep metadata outside A/B/C success evidence |
| Clarity | Conditional | Avoid a broad ready/success label; identify metadata, deterministic and live evidence separately |
| Feasibility | High for the bounded CLI; live success remains externally uncertain | Reuse Settings/official SDK/bounded transport without a lifecycle rewrite |
| Verifiability | Strong existing runner, pending Stage03.2 execution | Current full A with no missing/skipped/retried cases; separate false-success exit 1; no B before authorization |

No strategic reason was found to expand to Stage04, new agents, an alternate model/provider or a browser readiness feature. This is a pre-implementation review, not a verified Stage03.2 result. The source reads completed; one read-only `rg` search initially failed on Windows wildcard path expansion (exit 1), then the corrected `-g` search exited 0. No application check failure or test result is inferred from those reads.
