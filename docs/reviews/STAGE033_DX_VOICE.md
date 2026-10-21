# Stage03.3 independent DX voice

Date: 2026-10-20. This is an independent in-host Codex-family source review of the Stage03.3 plan and DX review. It is not cross-model agreement or an executed usability, provider, database or browser result. No tests, network requests, generation, configuration edits or historical-evidence edits were performed for this review. The only authored artifact is this file.

## Review result

The proposed scope fits the local Windows owner/contributor workflow: explicit server configuration, one offline diagnostic, deterministic Gate A, then a separately authorized single-generation Gate B and network-free Gate C. A model picker, retry/fallback mechanism or additional setup layer would add complexity without answering the observed upstream failures. No strategic scope blocker was found. The acceptance refinements below should be included before implementation is evaluated; this review does not certify implementation readiness or live reliability.

Inspected authorities include STAGE033_PLAN.md, STAGE033_DX.md, STAGE033_CEO.md, STAGE033_PROVIDER_RELIABILITY.md, README.md, TEST_PLAN.md, verify*.ps1, check_pm_config.py, verification.py and the current Settings, readiness, provider, admission, schema and startup source. Existing source still reflects the pre-Stage03.3 policy. Planned changes are described as planned.

## Eight dimensions

| Dimension | Assessment and concrete acceptance condition |
|---|---|
|Getting started|The existing PowerShell/uv path is appropriate. Put the exact three supported IDs, model/level compatibility and the offline command together in README rather than requiring the contributor to reconstruct them from review artifacts. Explain that missing provider configuration permits the rest of the app, while an invalid configured value can prevent startup. Offline success means configuration present, not readiness or a generated plan.|
|Naming and configuration|ORBA_PM_MODEL, ORBA_PM_THINKING_LEVEL and ORBA_PM_MAX_INPUT_BYTES describe the intended settings. Keep an explicit empty model default and LOW default; accept only the optional models/ prefix around the reviewed stable IDs. State accepted case/whitespace behavior once, and use the same canonical identity in policy, readiness and adapter checks. A direct model_copy must not bypass the adapter guard.|
|Safe actionable errors|The offline CLI currently suppresses raw ValidationError input, but its generic correction does not identify the new model/level combination. Report safe field names and static allowed choices without reflecting supplied values. Startup needs the same confidentiality boundary. input_too_large must remain a pre-admission422 with an actionable remedy, retained input and no invented run.|
|Documentation|The current README still describes any account-supported explicit ID and one reviewed model. Update that claim with the intentional three-ID restriction, the thinking matrix, the local byte formula and the unchanged6000 output cap. Show a shell-scoped alternative configuration that carries unchanged into the later authorized B command without replacing either dotenv file. Distinguish proposed commands from recorded executions.|
|Migration and history|No database migration, password/session rollout or historical model rewrite is justified. New policy applies to new generation, not deserialization of old run model strings or approved documents. Real-PostgreSQL coverage must retrieve an older run and its approved graph after changing the runtime selection to another supported model. Preserve old prompt files and receipt bytes.|
|Tooling and environment|Reuse locked uv/pnpm and the pinned official SDK. A already sets UTF8 in child environments; the PowerShell entry wrappers currently launch the outer Python process without that guarantee. Set UTF8 there too. Retain sequential backend/browser ownership of guarded orba_test and do not introduce Bash/global-tool repair.|
|Ecosystem fit|A dependency-free three-entry reviewed policy table is sufficient. Give each entry its dated official capability reference, keep the owner's selected3.8 unchanged, and describe3.6/minimal as an unverified future trial. Account metadata visibility is distinct from provider availability and quota. Updating a retired ID requires a reviewed change, not an automatic alias or fallback.|
|Measurement and feedback|Record prompt bytes, canonical provider-hint bytes/hash, snapshot bytes, total local bytes, selected thinking and configured limit. Keep the authoritative ProductDocument hash separate from the lean provider-hint hash. New A and B must bind the changed source/profile; C must reject stale, controlled or mismatched evidence without another GET. These measurements establish reproducibility, not latency improvement or output quality.|

## Findings and refinements

### DX-V1 / P1: Invalid startup can bypass the safe CLI diagnostic

Source: apps/api/scripts/check_pm_config.py:23-33 catches Settings ValidationError without printing it. In contrast, apps/api/orba/main.py:32 constructs Settings during module-level app creation and does not catch that validation exception. Once model/level validation becomes stricter, a typo can stop the API before HTTP error handlers exist. Pydantic's ordinary validation rendering can include supplied inputs, including a credential accidentally pasted into a configuration field. This is a source-derived exposure risk; no actual leak was induced in this review.

Use input-hidden validation errors for Settings and retain sanitized CLI output. Add a real local invalid-startup subprocess assertion that exits unsuccessfully without echoing a sentinel supplied as model/thinking input; it must not contact the provider or database. Keep safe corrective instructions available through the offline command/help. A test of only the CLI redaction does not cover Uvicorn import/startup.

The primary reviewer accepted Settings hide_input_in_errors=True plus an invalid-startup subprocess test as a scope refinement. Acceptance is not execution evidence.

### DX-V2 / P1: Define exactly what the new byte limit measures

Source: apps/api/orba/pm_service.py:170 currently bounds canonical snapshot characters, while pm_provider.py supplies PROMPT and gemini_output_schema() separately. The plan rightly replaces the incomplete bound, but the name MAX_INPUT_BYTES alone cannot tell an operator whether the number means brief bytes, serialized wire bytes or provider tokens.

Use one helper shared by admission, adapter and diagnostics:

```text
local_content_bytes = UTF8(PROMPT)
                    + UTF8(canonical(provider_hint))
                    + UTF8(canonical(snapshot))
```

Here each term denotes its encoded byte length. Specify that equality is allowed and exceeding the configured cap rejects before admission/dispatch. This is a local content-envelope bound, not full HTTP/SDK wire bytes, token accounting or a total bill ceiling. Tests should include multibyte text, JSON escaping and the exact boundary, with real PostgreSQL proving zero new runs/plans on rejection. Retain the separate selected-context bound and label it accurately. If configuration can make the fixed prompt/hint overhead exceed the cap, fail with an operator configuration remedy rather than telling a user to shorten an already empty brief.

The primary reviewer accepted this canonical formula/shared helper and documentation clarification. The minimum supported configured cap remains an implementation detail to make explicit in bounds/help.

### DX-V3 / P2: Keep one nonsecret profile intact across commands

Source: README.md:41 correctly states process environment overrides root/API dotenv; verify-live.ps1 forwards the inherited environment; verification.py:117-147 currently profiles model/schema/timeouts but has no thinking, input-byte limit or provider-hint identity. validate_model_readiness also checks one fixed documentation reference and an exact set of generation-limit fields.

The final runbook should show one temporary shell-scoped model/thinking selection with an offline inspection command and a clearly marked future B command. The selection must reach both B's native readiness command and its browser/API process. Extend the profile and strict readiness validation together; resolve the documented capability reference from the selected policy rather than retaining a3.8-only constant. Prove that changing thinking, byte cap, provider-hint hash or model invalidates readiness/profile linkage before dispatch and that C performs no external request. Avoid an extra standalone live API probe before the browser.

The primary reviewer accepted the shell-scoped example and outer-wrapper UTF8 setting. Existing X2 already covers profile expansion and tamper rejection; this finding clarifies the complete path it must cover.

### DX-V4 / P2: Explain the lean hint without implying weaker plans or a proven fix

Source: gemini_output_schema() is expressly a provider grammar hint, while ProductDocument and validate_generated remain authoritative. The planned removal of optional human-owned provenance/disposition hints should not be described as removing product requirements or making503/504 disappear.

Keep a before/after offline manifest with separate full-schema and hint hashes, counts and the preserved required PRD fields. Test omitted optional server-owned fields receive their normal validated defaults, and malicious explicit human/disposition values still reject. Existing real-PG publication and browser recovery identities must remain. No measured latency or quality claim follows until the one future model-backed flow actually runs.

## Future-call boundary

Preparation should end with a current passing A receipt/hash, final source fingerprint, safe effective profile, byte/hint measurements, actual false-success experiment exit and unchanged historical evidence. The proposed next profile is explicit gemini-3.6-flash/minimal,6000 output/thinking tokens,90/95/100s deadlines, concurrency1 and zero retries. It is a recommendation requiring fresh owner authorization, not a configuration change or permission inferred from metadata.

That authorization should name one Gate B browser generation. B's one native metadata GET is subordinate readiness evidence; the one resulting draft supplies the API/SQL/browser/edit/approval/isolation journey. Non-ready metadata, failed generation or duplicate attempted POST ends the attempt with its real outcome. Gate C remains PARTIAL/BLOCKED as appropriate until current genuine live evidence qualifies. Prior Full504, standalone503 and later failed B records stay separate and immutable.

No current model call, usability timing, application check or cross-model result is claimed by this review.
