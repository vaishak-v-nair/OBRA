# TODOS

Deferred by Stage03 /autoplan review2026-10-19. These are future proposals, not implemented capabilities or authorization to begin another stage. Mandatory Stage03 authentication/isolation/provider/browser/negative/regression verification is **not** deferred here. Owner approval of a later stage remains required.

## PM execution and evidence

### Durable disconnected execution and recovery

**What:** Evaluate a real durable job mechanism only if bounded request execution proves insufficient.
**Why:** A process crash currently interrupts generation; it is not automatically resumed.
**Context:** Stage03 proposes synchronous HTTP, durable deadlines/idempotency and honest interruption. Start from actual run/error/latency evidence; do not add Redis/Celery/LangGraph merely for appearance.
**Pros:** Better long-running/disconnected workflows.
**Cons:** Distributed ownership, retries, exactly-once/billing ambiguity and operational cost.
**Effort:** L
**Priority:** P3
**Depends on:** Verified Stage03, measured request-lifecycle limits and explicit owner scope.

### Per-edit audit and semantic version comparison

**What:** Consider append-only edit history and a useful cross-version requirement diff.
**Why:** Stage03 preserves approved versions but cannot reconstruct every intermediate draft edit or confirm an old save after later edits.
**Context:** Stable plan-local keys/source snapshots and optimistic revisions are the starting point. Do not imply full audit/semantic comparison already exists.
**Pros:** Better change review, recovery and downstream change impact.
**Cons:** Storage/retention policy, identity across copies and diff semantics.
**Effort:** L
**Priority:** P3
**Depends on:** Real version-history use, owner audit/retention policy and later-stage authorization.

### Private input and run retention policy

**What:** Define deletion/export/retention of briefs, snapshots, plans and diagnostics.
**Why:** Persisted execution evidence contains project information and grows over time.
**Context:** Stage03 applies current workspace authorization and keeps safe diagnostics; no generalized retention/deletion service is requested. Inventory actual data before designing cleanup.
**Pros:** Clear privacy/storage expectations.
**Cons:** Audit consistency, cascades and operator recovery complexity.
**Effort:** M
**Priority:** P3
**Depends on:** Owner policy and actual local data-growth evidence.

### Representative PM quality evaluations

**What:** Extend beyond the bounded live habit-tracker brief with representative authorized product briefs.
**Why:** One genuine response can establish runtime integration, not broad product-planning quality.
**Context:** Reuse fidelity/scope/uncertainty/observable-criteria rubric, actual prompt/model IDs and returned usage. No synthetic success percentages or leaked user briefs.
**Pros:** Better prompt/model regression decisions.
**Cons:** Paid usage, subjective review and dataset privacy.
**Effort:** M
**Priority:** P3
**Depends on:** Verified real Stage03 flow, owner-selected briefs and bounded evaluation budget.

## Later product stages

### Architect and downstream delivery agents

**What:** Implement Architect/coding/QA/orchestration only under their separately requested stages.
**Why:** The PM artifact should eventually feed implementation, but Stage03 is planning only.
**Context:** Begin with real approved plan versions, traceability, permissions and evidence contracts; no generated code/tool execution is authorized now.
**Pros:** Progress toward the unified delivery workspace.
**Cons:** Larger tool authority, sandboxing and failure/verification surface.
**Effort:** XL
**Priority:** P3
**Depends on:** Verified Stage03 and explicit next-stage request.

### Multi-provider Model Hub

**What:** Evaluate provider/model selection/routing and compatibility beyond one official adapter.
**Why:** Different future agents may need different models.
**Context:** Stage03 uses explicit runtime key/model with no default, fallback routing or custom endpoint. Full Model Hub belongs to the later planned stage.
**Pros:** Choice and potential workload fit.
**Cons:** Credential management, structured-schema differences and routing/cost ambiguity.
**Effort:** L
**Priority:** P3
**Depends on:** Actual provider evaluations and explicit Model Hub stage authorization.

### GitHub, Skills and external research capabilities

**What:** Build repository/contribution/Skills/retrieval integrations through later authorized stages.
**Why:** Planning may eventually benefit from repository and external evidence.
**Context:** No GitHub OAuth/App, Skills installation, external fact verification or automatic repository context is in Stage03. Treat retrieved instructions as untrusted and preserve data/source authority.
**Pros:** Richer project context and delivery paths.
**Cons:** New credentials, external effects, privacy and prompt-injection boundaries.
**Effort:** XL
**Priority:** P3
**Depends on:** Owner scope/permissions and separately designed real integrations.

### Multiplayer, canvas and cloud environments

**What:** Add real presence/collaboration, optional visual canvas and secure cloud execution later.
**Why:** They support the long-term unified workspace vision.
**Context:** Stage03 keeps current project pages and local sessions; it does not imply realtime activity or an execution sandbox.
**Pros:** Broader collaboration/development experience.
**Cons:** Distributed state, access control, billing and sandbox operations.
**Effort:** XL
**Priority:** P3
**Depends on:** Explicit future stage and security/resource design.

## Operations and developer experience

### Authoritative pricing and currency budgets

**What:** Consider real model pricing/versioned spend policy if the owner needs cost estimates.
**Why:** Actual usage tokens alone cannot establish dollar costs or a provider-wide spending cap.
**Context:** Stage03 has bounded output/time/admitted attempts and no invented prices. Use current authoritative pricing/account evidence before displaying cost.
**Pros:** Better spend planning.
**Cons:** Pricing drift, incomplete usage and distributed billing accounting.
**Effort:** M
**Priority:** P3
**Depends on:** Actual pricing source, owner currency/budget policy and later scope.

### Production identity, email and deployment readiness

**What:** Evaluate verified email, recovery/MFA/SSO, mail delivery, TLS/deployment and operational security under a separate request.
**Why:** Local account/model tests do not certify an internet-facing service.
**Context:** Stage02 lacks verified email/recovery/production certification; invitations are manually shared. No public deployment or secret changes are authorized by this TODO.
**Pros:** Potential wider safe usage.
**Cons:** Significant security, abuse, delivery and operational work.
**Effort:** XL
**Priority:** P3
**Depends on:** Explicit deployment/identity scope and a dedicated environment/security review.

### Hosted onboarding, general CLI/SDK and public support

**What:** Revisit a hosted playground, general developer clients, public docs/community/support after actual demand.
**Why:** Current local owners need a reproducible root PowerShell path before additional surfaces.
**Context:** No Git remote/public support SLA/license claim is established here. Stage03 uses existing UI and explicit verification commands.
**Pros:** Easier external adoption.
**Cons:** Hosting, support ownership, distribution and API compatibility burden.
**Effort:** L
**Priority:** P3
**Depends on:** Owner distribution decisions, user evidence and verified local workflow.

### Broader OS, browser and native-device certification

**What:** Build a defined compatibility matrix if additional platforms matter.
**Why:** Windows Chromium emulation does not establish macOS/Linux, native iOS/Android or every-browser behavior.
**Context:** Preserve current tested versions separately from broad runtime ranges. Stage03 must still execute existing desktop/mobile/tablet Chromium coverage; that requirement is not deferred.
**Pros:** Reliable platform claims.
**Cons:** Hardware/CI resources and maintenance.
**Effort:** M
**Priority:** P3
**Depends on:** Owner target-platform choices and access to actual target environments.

## Completed

No deferred item has been implemented by this planning review.

## Bounded findings from password-policy review

### Authentication transport and session-read feedback

**What:** Revisit auth-specific network copy and the partial outcome after a successful auth POST followed by a failed session read.
**Why:** The existing generic POST helper refers to Projects; session refresh can resolve after reporting a read error. Protected content remains gated, but clearer auth-specific guidance would reduce uncertainty.
**Context:** Observed in apps/web/src/lib/api.ts and components/session.tsx/auth-form.tsx during the password review. Not caused or fixed by the15-character rule. Preserve truthful unknown outcomes and never retry POST automatically; do not weaken AuthGate or invent a reset flow.
**Pros:** Clearer recovery guidance without suggesting duplicate account creation.
**Cons:** Needs explicit UX and negative-network regression coverage across account/session transitions.
**Effort:** S (human2-3hours / agent20-40min)
**Priority:** P2
**Depends on:** A separately scoped follow-up; not required to preserve password-policy compatibility. No automatic implementation authorization.
