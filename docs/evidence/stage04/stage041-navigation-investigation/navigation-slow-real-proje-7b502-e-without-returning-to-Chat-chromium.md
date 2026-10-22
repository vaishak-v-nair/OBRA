# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: navigation.spec.ts >> slow real project API stays on its project route without returning to Chat
- Location: tests-navigation\navigation.spec.ts:81:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('status').filter({ hasText: 'Loading project' })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('status').filter({ hasText: 'Loading project' }) with timeout 5000ms
  - waiting for getByRole('status').filter({ hasText: 'Loading project' })

```

```yaml
- link "Skip to content":
  - /url: "#main"
- complementary "Workspace navigation":
  - link "orba .":
    - /url: /
  - text: N Workspace
  - combobox "Workspace":
    - option "Select workspace" [disabled]
    - option "Navigation A" [selected]
  - link "New project":
    - /url: /projects/new
  - paragraph: WORKSPACE
  - navigation "Main navigation":
    - link "Chat":
      - /url: /
    - link "Projects":
      - /url: /projects
    - link "Skills":
      - /url: /skills
    - link "Contribute":
      - /url: /contribute
    - link "Workspaces":
      - /url: /workspaces
    - link "Activity":
      - /url: /activity
  - link "Settings":
    - /url: /settings
  - text: O
  - group: Account · ORBA Tester
- banner:
  - text: Workspace
  - strong: Projects
  - text: Product planning
  - button "Toggle color theme"
- main:
  - link "All projects":
    - /url: /projects
  - paragraph: PROJECT OVERVIEW
  - heading "First private project for navigation checks" [level=1]
  - text: Created Created
  - time: 10/22/2026, 12:43:40 AM
  - heading "Where it begins" [level=2]
  - paragraph: Your original project description
  - paragraph: First private project for navigation checks
  - button "Edit project"
  - navigation "Project planning views":
    - button "Product Plan"
    - button "Architecture"
    - button "Task Graph"
  - region "Product Plan":
    - paragraph: PRODUCT MANAGER
    - heading "Product Plan" [level=2]
    - text: One planning agent
    - paragraph: Turn your idea into reviewable requirements. Generation uses your configured AI provider and may incur usage.
    - complementary:
      - heading "Configure the Product Manager" [level=3]
      - paragraph: Set GEMINI_API_KEY and ORBA_PM_MODEL in the root .env, then restart the API. Configuration does not prove provider access.
      - paragraph: Keep credentials on the API server. Set an explicit supported Gemini model. A configured key does not guarantee model access.
    - group:
      - text: Generate product plan
      - form "Generate product plan":
        - text: Product brief
        - textbox "Product brief": First private project for navigation checks
        - paragraph: This brief is saved with the run. It does not change your original project description.
        - text: Additional instructions (optional)
        - textbox "Additional instructions (optional)"
        - button "Generate Product Plan" [disabled]
    - button "Check status"
    - heading "Your requirements start here" [level=3]
    - paragraph: Generate a plan from your brief to review epics, stories, and testable acceptance criteria. No model call happens until you choose Generate Product Plan.
    - group: Planning run history (0)
  - heading "Room for what comes next" [level=2]
  - paragraph: Task execution, additional agents, and delivery evidence belong to later stages.
  - text: Coming in a later stage
- contentinfo: Built for the way you think. Local development workspace
- alert
```

# Test source

```ts
  1   | /** Real auth/API/PostgreSQL. Controlled transport barriers/errors are labeled below. */
  2   | import { test, expect, type Page, type Route } from "@playwright/test";
  3   | import { writeFileSync } from "node:fs";
  4   | import { architectBoundary } from "../tests/architect-boundary";
  5   | import { approveDraft, architectPreflight, createProject, expectNoGenerationRecords, expectPlan, expectProject, jsonGet, observeRoutes, preflightProof, prepareDraft, reloadProject, sqlSource, testCommand, type PreflightProof } from "../tests/architect-preflight";
  6   | import { createWorkspace, nav, signup } from "../tests/helpers";
  7   | import { evidencePath } from "../tests/evidence";
  8   | import type { Project } from "../src/lib/api";
  9   | import type { Plan } from "../src/lib/pm";
  10  | 
  11  | function latch() {
  12  |   let resolve!: () => void;
  13  |   const promise = new Promise<void>(done => { resolve = done; });
  14  |   return { promise, resolve };
  15  | }
  16  | async function holdRealResponse(page: Page, pattern: RegExp, accepts: (route: Route) => boolean = () => true) {
  17  |   const held = latch(), released = latch();
  18  |   let matched = false;
  19  |   await page.route(pattern, async route => {
  20  |     if (!accepts(route) || matched) { await route.continue(); return; }
  21  |     matched = true;
  22  |     const response = await route.fetch(); // Actual service response and persistence, never canned content.
  23  |     held.resolve();
  24  |     await released.promise;
  25  |     await route.fulfill({ response }).catch(() => { /* A deliberate navigation cancellation may close it. */ });
  26  |   });
  27  |   return { held: held.promise, release: released.resolve };
  28  | }
  29  | async function write(page: Page, path: string, data: unknown) {
  30  |   const csrf = await jsonGet<{ csrf_token: string }>(page, "/api/v1/auth/csrf");
  31  |   return page.request.post(path, { headers: { Origin: "http://localhost:3001", "X-CSRF-Token": csrf.csrf_token }, data });
  32  | }
  33  | async function accountProject(page: Page) {
  34  |   await signup(page, `navigation-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`);
  35  |   await createWorkspace(page, "Navigation A");
  36  |   return createProject(page, "First private project for navigation checks");
  37  | }
  38  | 
  39  | let proof: PreflightProof;
  40  | let blockedBefore = 0;
  41  | let boundary: Awaited<ReturnType<typeof architectBoundary>>;
  42  | test.beforeEach(async ({ context, page }) => {
  43  |   testCommand("scripts.prepare_tests");
  44  |   proof = preflightProof();
  45  |   observeRoutes(page, proof);
  46  |   boundary = await architectBoundary(context);
  47  |   Object.assign(proof, { execution_class: "no_generation_navigation_regression", generation_budget: boundary.budget });
  48  |   const counters = await jsonGet<{ blocked_generation_posts: number }>(page, "http://127.0.0.1:8001/__test/no-generation");
  49  |   blockedBefore = counters.blocked_generation_posts;
  50  | });
  51  | test.afterEach(async ({ page }, info) => {
  52  |   const response = await page.request.get("http://127.0.0.1:8001/__test/no-generation");
  53  |   const counters = await response.json();
  54  |   proof.server_boundary = counters;
  55  |   expect(counters.provider_dependency_entries).toBe(0);
  56  |   expect(counters.blocked_generation_posts - blockedBefore).toBe(proof.expected_denied_posts ?? 0);
  57  |   expect(proof.generation_budget).toEqual({ attempted: 0, forwarded: 0, blocked: 0 });
  58  |   proof.case_result = info.status === info.expectedStatus ? "PASS" : "FAIL";
  59  |   writeFileSync(evidencePath(`navigation-${info.project.name}-${info.title.replaceAll(/[^a-z0-9]+/gi, "-")}.json`), JSON.stringify(proof, null, 2) + "\n");
  60  | });
  61  | 
  62  | test("shared Phase1 approves the exact source, reloads and stops at Architect entry", async ({ page }) => {
  63  |   await architectPreflight(page, proof);
  64  | });
  65  | 
  66  | test("route confirmation precedes immediate reload even when real Next navigation is held", async ({ page }) => {
  67  |   await signup(page, `route-${Date.now()}@example.com`); await createWorkspace(page, "Route synchronization");
  68  |   const barrier = await holdRealResponse(page, /\/projects\/[a-f0-9-]+(?:\?.*)?$/, route => /^\/projects\/[a-f0-9-]+$/.test(new URL(route.request().url()).pathname));
  69  |   try {
  70  |     const creating = createProject(page, "Project created before its real route response arrives", proof);
  71  |     await barrier.held;
  72  |     expect(new URL(page.url()).pathname).toBe("/");
  73  |     await expect(page.getByTestId("project-detail")).toHaveCount(0);
  74  |     barrier.release();
  75  |     const project = await creating;
  76  |     await reloadProject(page, project, proof);
  77  |     expect((await jsonGet<Project>(page, `/api/v1/projects/${project.id}`)).id).toBe(project.id);
  78  |   } finally { barrier.release(); }
  79  | });
  80  | 
  81  | test("slow real project API stays on its project route without returning to Chat", async ({ page }) => {
  82  |   const project = await accountProject(page);
  83  |   await page.goto("/");
  84  |   const barrier = await holdRealResponse(page, new RegExp(`/api/v1/projects/${project.id}$`));
  85  |   try {
  86  |     await page.goto(`/projects/${project.id}`); await barrier.held;
  87  |     await expect(page).toHaveURL(`http://localhost:3001/projects/${project.id}`);
> 88  |     await expect(page.getByRole("status").filter({ hasText: "Loading project" })).toBeVisible();
      |                                                                                   ^ Error: expect(locator).toBeVisible() failed
  89  |     await expect(page.getByRole("heading", { name: "What would you like to build today?", exact: true })).toHaveCount(0);
  90  |     barrier.release(); await expectProject(page, project); await reloadProject(page, project);
  91  |   } finally { barrier.release(); }
  92  | });
  93  | 
  94  | test("asynchronous workspace restoration preserves the selected project and hides stale content", async ({ page }) => {
  95  |   const first = await accountProject(page);
  96  |   await createWorkspace(page, "Navigation B");
  97  |   const second = await createProject(page, "Second workspace private project");
  98  |   const toggle = page.getByRole("button", { name: "Open navigation", exact: true });
  99  |   if (await toggle.isVisible()) await toggle.click();
  100 |   await page.getByLabel("Workspace", { exact: true }).selectOption(first.workspace_id);
  101 |   await expect(page).toHaveURL("http://localhost:3001/projects");
  102 |   await page.goto(`/projects/${first.id}`); await expectProject(page, first);
  103 |   const barrier = await holdRealResponse(page, /\/api\/v1\/workspaces$/, route => route.request().method() === "GET");
  104 |   try {
  105 |     await page.reload(); await barrier.held;
  106 |     await expect(page.getByRole("status").filter({ hasText: "Checking your session" })).toBeVisible();
  107 |     await expect(page.getByRole("heading", { name: first.title, exact: true })).toHaveCount(0);
  108 |     await expect(page.getByRole("heading", { name: second.title, exact: true })).toHaveCount(0);
  109 |     barrier.release(); await expectProject(page, first);
  110 |     await expect(page.getByRole("heading", { name: second.title, exact: true })).toHaveCount(0);
  111 |   } finally { barrier.release(); }
  112 | });
  113 | 
  114 | test("a delayed second project cannot display the first project as its details", async ({ page }) => {
  115 |   const first = await accountProject(page);
  116 |   await page.goto("/"); const second = await createProject(page, "Another project with distinct protected content");
  117 |   await page.goto(`/projects/${first.id}`); await expectProject(page, first);
  118 |   const barrier = await holdRealResponse(page, new RegExp(`/api/v1/projects/${second.id}$`));
  119 |   try {
  120 |     await nav(page, "Projects"); await page.getByRole("link").filter({ has: page.getByRole("heading", { name: second.title, exact: true }) }).click();
  121 |     await barrier.held;
  122 |     await expect(page).toHaveURL(`http://localhost:3001/projects/${second.id}`);
  123 |     await expect(page.getByRole("heading", { name: first.title, exact: true })).toHaveCount(0);
  124 |     await expect(page.getByTestId("project-detail")).not.toHaveAttribute("data-project-id", first.id);
  125 |     barrier.release(); await expectProject(page, second);
  126 |   } finally { barrier.release(); }
  127 | });
  128 | 
  129 | test("wrong-route synchronization reports expected identity without approving or generating", async ({ page }) => {
  130 |   const project = await accountProject(page); await page.goto("/");
  131 |   // Isolated negative assertion: inspect the actual failure message; not a gate test retry.
  132 |   let message = "";
  133 |   try { await expectProject(page, project, 100); } catch (error) { message = String(error); }
  134 |   expect(message).toContain(`Project navigation must commit /projects/${project.id}`);
  135 |   expect(message).toContain("http://localhost:3001/");
  136 |   await expect(page.getByRole("button", { name: "Approve plan", exact: true })).toHaveCount(0);
  137 | });
  138 | 
  139 | test("real session revocation stops approval and leaves the exact PRD draft", async ({ page }) => {
  140 |   const { project, user, authored } = await prepareDraft(page, proof);
  141 |   await reloadProject(page, project);
  142 |   const draft = await jsonGet<Plan>(page, `/api/v1/projects/${project.id}/pm-plans/${authored.plan_id}`);
  143 |   await expectPlan(page, draft);
  144 |   const logout = await write(page, "/api/v1/auth/logout", {}); expect(logout.status()).toBe(204);
  145 |   // Session cookie removal is real; UI has not received its next authority check yet.
  146 |   await page.getByRole("button", { name: "Approve plan", exact: true }).click();
  147 |   await page.getByRole("button", { name: "Confirm approval", exact: true }).click();
  148 |   await expect(page.getByRole("heading", { name: "Sign in to your workspace", exact: true })).toBeVisible();
  149 |   await expect(page.getByTestId("plan-state")).toHaveCount(0);
  150 |   const sql = sqlSource(project, authored.plan_id, user.id);
  151 |   expect(sql).toMatchObject({ state: "draft", revision: 1, approved_by: null, approved_at: null });
  152 |   expectNoGenerationRecords(sql); proof.sql_after_revocation = sql;
  153 | });
  154 | 
  155 | test("controlled PRD transport failure stops before approval and Architect entry", async ({ page }) => {
  156 |   const { project, user, authored } = await prepareDraft(page, proof);
  157 |   // Narrow controlled transport failure; project/auth/API/database remain real.
  158 |   await page.route(new RegExp(`/api/v1/projects/${project.id}/pm-plans\\?`), route => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: { code: "controlled_transport_failure", message: "PRD temporarily unavailable (controlled transport test)." } }) }));
  159 |   await reloadProject(page, project);
  160 |   await expect(page.getByRole("region", { name: "Product Plan", exact: true }).getByRole("alert")).toContainText("PRD temporarily unavailable");
  161 |   await expect(page.getByRole("button", { name: "Approve plan", exact: true })).toHaveCount(0);
  162 |   const sql = sqlSource(project, authored.plan_id, user.id); expect(sql.state).toBe("draft"); expectNoGenerationRecords(sql);
  163 | });
  164 | 
  165 | test("controlled approval API failure preserves draft and does not claim approval", async ({ page }) => {
  166 |   const { project, user, authored } = await prepareDraft(page, proof);
  167 |   await reloadProject(page, project);
  168 |   await expect(page.getByTestId("plan-state")).toHaveText("draft");
  169 |   await page.route(new RegExp(`/pm-plans/${authored.plan_id}/approve$`), route => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: { code: "controlled_approval_failure", message: "Approval unavailable (controlled transport test)." } }) }));
  170 |   await page.getByRole("button", { name: "Approve plan", exact: true }).click();
  171 |   await page.getByRole("button", { name: "Confirm approval", exact: true }).click();
  172 |   await expect(page.getByRole("region", { name: "Product Plan", exact: true }).getByRole("alert")).toContainText("Approval unavailable");
  173 |   await expect(page.getByTestId("plan-state")).toHaveText("draft");
  174 |   const sql = sqlSource(project, authored.plan_id, user.id); expect(sql.approved_by).toBeNull(); expect(sql.revision).toBe(1); expectNoGenerationRecords(sql);
  175 | });
  176 | 
  177 | test("a real Member cannot approve the Owner source or access another workspace", async ({ page, browser }) => {
  178 |   const { project, user, authored } = await prepareDraft(page, proof);
  179 |   const email = `member-navigation-${Date.now()}@example.com`;
  180 |   const inviteResponse = await write(page, `/api/v1/workspaces/${project.workspace_id}/invitations`, { email, role: "member" }); expect(inviteResponse.status()).toBe(201);
  181 |   const invitation = await inviteResponse.json();
  182 |   const otherContext = await browser.newContext();
  183 |   try {
  184 |     const other = await otherContext.newPage(); await signup(other, email);
  185 |     const token = new URLSearchParams(new URL(invitation.invitation_link).hash.slice(1)).get("token");
  186 |     const accepted = await write(other, "/api/v1/invitations/accept", { token }); expect(accepted.status()).toBe(200);
  187 |     await other.goto(`/projects/${project.id}`); await expectProject(other, project);
  188 |     await expect(other.getByTestId("plan-state")).toHaveText("draft");
```