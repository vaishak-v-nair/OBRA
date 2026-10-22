# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: navigation.spec.ts >> preflight closes before generation when approval prerequisite fails
- Location: tests-navigation\navigation.spec.ts:199:5

# Error details

```
Test timeout of 90000ms exceeded.
```

```
Error: page.waitForResponse: Test timeout of 90000ms exceeded.
```

# Page snapshot

```yaml
- generic [active] [ref=f1e1]:
  - generic [ref=f1e2]:
    - link "Skip to content" [ref=f1e3] [cursor=pointer]:
      - /url: "#main"
    - complementary "Workspace navigation" [ref=f1e4]:
      - link "orba ." [ref=f1e6] [cursor=pointer]:
        - /url: /
        - generic [aria-hidden] [ref=f1e7]: o
        - text: orba
        - generic [ref=f1e8]: .
      - generic [ref=f1e9]:
        - generic [ref=f1e10]: L
        - generic [ref=f1e11]:
          - generic [ref=f1e12]: Workspace
          - combobox "Workspace" [ref=f1e13]:
            - option "Select workspace" [disabled]
            - option "Live architecture verification" [selected]
      - link "New project" [ref=f1e14] [cursor=pointer]:
        - /url: /projects/new
      - paragraph [ref=f1e16]: WORKSPACE
      - navigation "Main navigation" [ref=f1e17]:
        - link "Chat" [ref=f1e18] [cursor=pointer]:
          - /url: /
        - link "Projects" [ref=f1e24] [cursor=pointer]:
          - /url: /projects
        - link "Skills" [ref=f1e28] [cursor=pointer]:
          - /url: /skills
        - link "Contribute" [ref=f1e33] [cursor=pointer]:
          - /url: /contribute
        - link "Workspaces" [ref=f1e39] [cursor=pointer]:
          - /url: /workspaces
        - link "Activity" [ref=f1e44] [cursor=pointer]:
          - /url: /activity
      - generic [ref=f1e48]:
        - link "Settings" [ref=f1e49] [cursor=pointer]:
          - /url: /settings
        - generic [ref=f1e53]:
          - generic [ref=f1e54]: O
          - group [ref=f1e55]:
            - generic "Account · ORBA Tester" [ref=f1e56] [cursor=pointer]
    - generic [ref=f1e57]:
      - banner [ref=f1e58]:
        - generic [ref=f1e59]:
          - generic [ref=f1e60]: Workspace
          - strong [ref=f1e63]: Chat
        - generic [ref=f1e64]:
          - generic [ref=f1e65]: Product planning
          - button "Toggle color theme" [ref=f1e66] [cursor=pointer]
      - main [ref=f1e73]:
        - generic [ref=f1e75]:
          - generic [ref=f1e76]:
            - paragraph [ref=f1e81]: A LITTLE CLARITY. A LOT OF POSSIBILITY.
            - heading "What would you like to build today?" [level=1] [ref=f1e82]
            - paragraph [ref=f1e83]: Your workspace for planning, building, testing, and delivering software with AI.
          - generic [ref=f1e84]:
            - form "Create project" [ref=f1e85]:
              - generic [ref=f1e86]:
                - generic [ref=f1e87]: Project description
                - textbox "Project description" [ref=f1e88]:
                  - /placeholder: Describe what you’d like to build...
                  - text: Personal daily habit check-in with saved status after reload. One user, no social features.
                - generic [ref=f1e89]:
                  - generic [ref=f1e90]:
                    - generic "Attachments are coming in a later stage" [ref=f1e91]:
                      - button "Attachments coming in a later stage" [disabled]
                    - generic "GitHub integration is coming in a later stage" [ref=f1e92]:
                      - button "GitHub integration coming in a later stage" [disabled]
                    - generic [ref=f1e93]: Start with an idea
                  - button "Create project" [ref=f1e94] [cursor=pointer]
              - alert [ref=f1e97]: Could not reach ORBA. The save could not be confirmed. Check Projects before trying again to avoid a duplicate. Your draft is preserved here.
              - paragraph [ref=f1e98]: Your description creates a project. AI collaboration is coming in a later stage.
            - generic [ref=f1e99]:
              - link [ref=f1e100] [cursor=pointer]:
                - /url: /projects/new
                - strong [ref=f1e103]: Start a project
                - paragraph [ref=f1e104]: Turn a fresh idea into a place to build.
              - link [ref=f1e108] [cursor=pointer]:
                - /url: /projects
                - strong [ref=f1e111]: Pick up where you left off
                - paragraph [ref=f1e112]: Find your ideas, all in one workspace.
            - generic [ref=f1e116]: Your next great project starts here
      - contentinfo [ref=f1e123]:
        - generic [ref=f1e124]: Built for the way you think.
        - generic [ref=f1e125]: Local development workspace
  - alert [ref=f1e126]: What would you like to build today?
```

# Test source

```ts
  1   | /** Shared Phase1: real UI/auth/API/SQL source approval, never model generation. */
  2   | import { expect, type Page } from "@playwright/test";
  3   | import { execFileSync } from "node:child_process";
  4   | import type { Project, User } from "../src/lib/api";
  5   | import type { Plan } from "../src/lib/pm";
  6   | import { createWorkspace, signup } from "./helpers";
  7   | 
  8   | export type Milestone = { at: string; event: string; path: string; [key: string]: unknown };
  9   | export type PreflightProof = {
  10  |   result: "FAIL" | "PASS"; approved_source_reloaded: boolean; step: string;
  11  |   milestones: Milestone[]; [key: string]: unknown;
  12  | };
  13  | export const testCommand = (...args: string[]) => execFileSync("uv", ["run", "--directory", "../api", "python", "-m", ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  14  | export function preflightProof(): PreflightProof {
  15  |   return { result: "FAIL", approved_source_reloaded: false, step: "initial", milestones: [] };
  16  | }
  17  | export function mark(page: Page, proof: PreflightProof, event: string, data: Record<string, unknown> = {}) {
  18  |   proof.step = event;
  19  |   proof.milestones.push({ at: new Date().toISOString(), event, path: new URL(page.url()).pathname, ...data });
  20  | }
  21  | export function observeRoutes(page: Page, proof: PreflightProof) {
  22  |   page.on("framenavigated", frame => {
  23  |     if (frame === page.mainFrame() && page.url().startsWith("http")) {
  24  |       proof.milestones.push({ at: new Date().toISOString(), event: "route_committed", path: new URL(page.url()).pathname });
  25  |     }
  26  |   });
  27  | }
  28  | export async function jsonGet<T>(page: Page, path: string): Promise<T> {
  29  |   const response = await page.request.get(path);
  30  |   expect(response.status(), `GET ${path} must succeed before the next preflight phase`).toBe(200);
  31  |   return response.json() as Promise<T>;
  32  | }
  33  | export async function expectProject(page: Page, project: Project, timeout = 15000) {
  34  |   await expect(page, `Project navigation must commit /projects/${project.id}; actual route is recorded in milestones`).toHaveURL(`http://localhost:3001/projects/${project.id}`, { timeout });
  35  |   const detail = page.getByTestId("project-detail");
  36  |   await expect(detail, "The requested project must load before reload or approval").toHaveAttribute("data-project-id", project.id, { timeout });
  37  |   await expect(detail).toHaveAttribute("data-workspace-id", project.workspace_id);
  38  |   await expect(page.getByLabel("Workspace", { exact: true })).toHaveValue(project.workspace_id);
  39  |   await expect(page.getByRole("heading", { name: project.title, exact: true })).toBeVisible();
  40  | }
  41  | export async function createProject(page: Page, description: string, proof?: PreflightProof) {
  42  |   await page.getByLabel("Project description", { exact: true }).fill(description);
> 43  |   const creating = page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === "/api/v1/projects");
      |                         ^ Error: page.waitForResponse: Test timeout of 90000ms exceeded.
  44  |   await page.getByRole("button", { name: "Create project", exact: true }).click();
  45  |   const response = await creating;
  46  |   expect(response.status(), "Project creation must succeed before waiting for its route").toBe(201);
  47  |   const project: Project = await response.json();
  48  |   if (proof) mark(page, proof, "project_post_received", { project_id: project.id, workspace_id: project.workspace_id, status: response.status() });
  49  |   // POST completion does not imply Next router commitment. Never reload before this.
  50  |   await expectProject(page, project);
  51  |   if (proof) mark(page, proof, "exact_project_loaded", { project_id: project.id, workspace_id: project.workspace_id });
  52  |   return project;
  53  | }
  54  | export async function reloadProject(page: Page, project: Project, proof?: PreflightProof) {
  55  |   await expectProject(page, project);
  56  |   if (proof) mark(page, proof, "reload_confirmed_project", { project_id: project.id });
  57  |   await page.reload();
  58  |   await expectProject(page, project);
  59  | }
  60  | export function sqlSource(project: Project, planId: string, actorId: string) {
  61  |   return JSON.parse(testCommand("scripts.inspect_architect_preflight", "--project", project.id, "--plan", planId, "--actor", actorId));
  62  | }
  63  | export function expectNoGenerationRecords(sql: { generation_records: Record<string, number> }) {
  64  |   expect(sql.generation_records).toEqual({ product_manager_runs: 0, architect_runs: 0, architecture_versions: 0, engineering_tasks: 0, task_dependencies: 0 });
  65  | }
  66  | export async function prepareDraft(page: Page, proof: PreflightProof) {
  67  |   await signup(page, `architect-preflight-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`);
  68  |   mark(page, proof, "authenticated");
  69  |   await createWorkspace(page, "Live architecture verification");
  70  |   mark(page, proof, "workspace_selected");
  71  |   const project = await createProject(page, "Personal daily habit check-in with saved status after reload. One user, no social features.", proof);
  72  |   const user = await jsonGet<User>(page, "/api/v1/auth/me");
  73  |   const authored = JSON.parse(testCommand("scripts.seed_pm_fixture", "--project", project.id, "--actor", user.id));
  74  |   expect(authored.model_call).toBe(false); expect(authored.origin).toBe("human_authored");
  75  |   Object.assign(proof, { project_id: project.id, workspace_id: project.workspace_id, actor_id: user.id, source_plan_id: authored.plan_id, source_origin: authored.origin });
  76  |   mark(page, proof, "authored_draft_persisted", { plan_id: authored.plan_id, version: authored.version });
  77  |   return { project, user, authored };
  78  | }
  79  | export async function expectPlan(page: Page, plan: Plan) {
  80  |   const saved = page.getByTestId("saved-product-plan");
  81  |   await expect(saved, "The exact persisted PRD must load before approval or architecture").toHaveAttribute("data-plan-id", plan.id);
  82  |   await expect(saved).toHaveAttribute("data-version", String(plan.version));
  83  |   await expect(saved).toHaveAttribute("data-revision", String(plan.revision));
  84  |   await expect(page.getByTestId("plan-state")).toHaveText(plan.state);
  85  |   await expect(page.getByLabel("Plan version", { exact: true })).toHaveValue(plan.id);
  86  | }
  87  | export async function approveDraft(page: Page, project: Project, user: User, planId: string, proof: PreflightProof) {
  88  |   await reloadProject(page, project, proof);
  89  |   const path = `/api/v1/projects/${project.id}/pm-plans/${planId}`;
  90  |   const draft = await jsonGet<Plan>(page, path);
  91  |   expect(draft.state).toBe("draft"); expect(draft.approved_by).toBeNull();
  92  |   await expectPlan(page, draft);
  93  |   mark(page, proof, "exact_draft_visible", { plan_id: draft.id, version: draft.version, revision: draft.revision });
  94  |   const panel = page.getByRole("region", { name: "Product Plan", exact: true });
  95  |   await expect(panel.getByRole("button", { name: "Approve plan", exact: true })).toBeEnabled();
  96  |   await panel.getByRole("button", { name: "Approve plan", exact: true }).click();
  97  |   const confirmation = panel.getByLabel("Confirm plan approval", { exact: true });
  98  |   await expect(confirmation.getByRole("heading", { name: `Approve version ${draft.version}, revision ${draft.revision}?`, exact: true })).toBeVisible();
  99  |   const approving = page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === `${path}/approve`);
  100 |   await confirmation.getByRole("button", { name: "Confirm approval", exact: true }).click();
  101 |   const response = await approving;
  102 |   mark(page, proof, "approval_http_response", { status: response.status(), plan_id: draft.id });
  103 |   expect(response.status(), "PRD approval failed; generation must remain closed").toBe(200);
  104 |   const submitted = response.request().postDataJSON();
  105 |   expect(submitted).toEqual({ expected_revision: draft.revision, version: draft.version });
  106 |   const approved = await jsonGet<Plan>(page, path);
  107 |   expect(approved.id).toBe(draft.id); expect(approved.version).toBe(draft.version);
  108 |   // Approval binds the saved revision; it does not edit the document or increment it.
  109 |   expect(approved.revision).toBe(draft.revision); expect(approved.state).toBe("approved");
  110 |   expect(approved.approved_by).toBe(user.id); expect(approved.approved_at).toBeTruthy();
  111 |   await expectPlan(page, approved);
  112 |   proof.approved_sql = sqlSource(project, planId, user.id);
  113 |   expect(proof.approved_sql).toMatchObject({ project_id: project.id, workspace_id: project.workspace_id, plan_id: planId, version: approved.version, revision: approved.revision, state: "approved", approved_by: user.id, content_hash: approved.content_hash, current_approved_plan_id: planId, document_validated: true });
  114 |   expectNoGenerationRecords(proof.approved_sql as ReturnType<typeof sqlSource>);
  115 |   mark(page, proof, "approval_independently_verified", { plan_id: planId, version: approved.version, revision: approved.revision });
  116 |   return approved;
  117 | }
  118 | export async function finishPreflight(page: Page, project: Project, user: User, approved: Plan, proof: PreflightProof) {
  119 |   await reloadProject(page, project, proof);
  120 |   await expectPlan(page, approved);
  121 |   const source = await jsonGet<Plan>(page, `/api/v1/projects/${project.id}/architect-source`);
  122 |   expect(source).toMatchObject({ id: approved.id, version: approved.version, revision: approved.revision, content_hash: approved.content_hash, state: "approved", approved_by: user.id });
  123 |   await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Architecture", exact: true }).click();
  124 |   const panel = page.getByRole("region", { name: "Architecture workspace", exact: true });
  125 |   await expect(panel.getByText(` ${source.document.product_name.text} · v${source.version} / r${source.revision}`.trim(), { exact: true })).toBeVisible();
  126 |   await expect(panel.getByRole("button", { name: "Generate Architecture", exact: true })).toBeEnabled();
  127 |   await expect(panel.getByLabel("Optional architectural constraints", { exact: true })).toBeEditable();
  128 |   const finalSql = sqlSource(project, source.id, user.id);
  129 |   expectNoGenerationRecords(finalSql);
  130 |   expect(finalSql).toMatchObject({ plan_id: source.id, version: source.version, revision: source.revision, state: "approved", content_hash: source.content_hash, approved_by: user.id });
  131 |   Object.assign(proof, { result: "PASS", approved_source_reloaded: true, source_version: source.version, source_revision: source.revision, source_hash: source.content_hash, final_sql: finalSql });
  132 |   mark(page, proof, "architect_entry_reached_without_generation", { source_plan_id: source.id, version: source.version, revision: source.revision });
  133 |   return { project, user, source };
  134 | }
  135 | export async function architectPreflight(page: Page, proof: PreflightProof) {
  136 |   const { project, user, authored } = await prepareDraft(page, proof);
  137 |   const approved = await approveDraft(page, project, user, authored.plan_id, proof);
  138 |   return finishPreflight(page, project, user, approved, proof);
  139 | }
  140 | 
```