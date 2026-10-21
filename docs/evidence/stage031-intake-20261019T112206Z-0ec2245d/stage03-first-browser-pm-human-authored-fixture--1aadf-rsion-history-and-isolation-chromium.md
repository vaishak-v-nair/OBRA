# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: pm.spec.ts >> human-authored fixture: edit criterion, persist, approve exact version, history and isolation
- Location: tests\pm.spec.ts:31:5

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('#product-plan').getByLabel('Then (criterion_checkin)', { exact: true })

```

# Page snapshot

```yaml
- generic [active] [ref=f2e1]:
  - generic [ref=f2e2]:
    - link "Skip to content" [ref=f2e3] [cursor=pointer]:
      - /url: "#main"
    - complementary "Workspace navigation" [ref=f2e4]:
      - link "orba ." [ref=f2e6] [cursor=pointer]:
        - /url: /
        - generic [aria-hidden] [ref=f2e7]: o
        - text: orba
        - generic [ref=f2e8]: .
      - generic [ref=f2e9]:
        - generic [ref=f2e10]: P
        - generic [ref=f2e11]:
          - generic [ref=f2e12]: Workspace
          - combobox "Workspace" [ref=f2e13]:
            - option "Select workspace" [disabled]
            - option "Product planning" [selected]
      - link "New project" [ref=f2e14] [cursor=pointer]:
        - /url: /projects/new
      - paragraph [ref=f2e16]: WORKSPACE
      - navigation "Main navigation" [ref=f2e17]:
        - link "Chat" [ref=f2e18] [cursor=pointer]:
          - /url: /
        - link "Projects" [ref=f2e22] [cursor=pointer]:
          - /url: /projects
        - link "Skills" [ref=f2e28] [cursor=pointer]:
          - /url: /skills
        - link "Contribute" [ref=f2e33] [cursor=pointer]:
          - /url: /contribute
        - link "Workspaces" [ref=f2e39] [cursor=pointer]:
          - /url: /workspaces
        - link "Activity" [ref=f2e44] [cursor=pointer]:
          - /url: /activity
      - generic [ref=f2e48]:
        - link "Settings" [ref=f2e49] [cursor=pointer]:
          - /url: /settings
        - generic [ref=f2e53]:
          - generic [ref=f2e54]: O
          - group [ref=f2e55]:
            - generic "Account · ORBA Tester" [ref=f2e56] [cursor=pointer]
    - generic [ref=f2e57]:
      - banner [ref=f2e58]:
        - generic [ref=f2e59]:
          - generic [ref=f2e60]: Workspace
          - strong [ref=f2e63]: Projects
        - generic [ref=f2e64]:
          - generic [ref=f2e65]: Stage 02 · Workspaces
          - button "Toggle color theme" [ref=f2e66] [cursor=pointer]
      - main [ref=f2e73]:
        - generic [ref=f2e75]:
          - link "All projects" [ref=f2e76] [cursor=pointer]:
            - /url: /projects
          - generic [ref=f2e79]:
            - generic [ref=f2e83]:
              - paragraph [ref=f2e84]: PROJECT OVERVIEW
              - heading "A personal habit journal with daily check-ins." [level=1] [ref=f2e85]
            - generic [ref=f2e86]: Created
          - generic [ref=f2e90]:
            - text: Created
            - time [ref=f2e91]: 10/19/2026, 10:58:52 AM
          - generic [ref=f2e92]:
            - heading "Where it begins" [level=2] [ref=f2e93]
            - paragraph [ref=f2e94]: Your original project description
            - paragraph [ref=f2e95]: A personal habit journal with daily check-ins.
            - button "Edit project" [ref=f2e96] [cursor=pointer]
          - region [ref=f2e97]:
            - generic [ref=f2e98]:
              - generic [ref=f2e99]:
                - paragraph [ref=f2e100]: PRODUCT MANAGER
                - heading "Product Plan" [level=2] [ref=f2e101]
              - generic [ref=f2e105]: One planning agent
            - paragraph [ref=f2e106]: Turn your idea into reviewable requirements. Generation uses your configured AI provider and may incur usage.
            - complementary [ref=f2e107]:
              - heading "Configure the Product Manager" [level=3] [ref=f2e108]
              - paragraph [ref=f2e109]: Set GEMINI_API_KEY and ORBA_PM_MODEL in the root .env, then restart the API. Configuration does not prove provider access.
              - paragraph [ref=f2e110]: Keep credentials on the API server. Set an explicit supported Gemini model. A configured key does not guarantee model access.
            - group [ref=f2e111]:
              - generic "Generate another product plan" [ref=f2e112] [cursor=pointer]
            - button "Check status" [ref=f2e114] [cursor=pointer]
            - generic [ref=f2e115]:
              - generic [ref=f2e116]:
                - generic [ref=f2e117]:
                  - text: Plan version
                  - combobox "Plan version" [ref=f2e118]:
                    - option "Version 1 · draft · revision 1" [selected]
                - generic [ref=f2e119]: draft
              - paragraph [ref=f2e120]: Version 1 · revision 1 · Human-authored plan
              - form "Edit product plan" [ref=f2e121]:
                - group "Draft requirements" [ref=f2e122]:
                  - paragraph [ref=f2e124]: Changes stay in this page until saved. The server records your identity on changed requirements; existing source evidence is preserved.
                  - generic [ref=f2e125]:
                    - text: Product name
                    - textbox "Product name" [ref=f2e126]: Habit journal — human-authored test fixture
                  - generic [ref=f2e127]:
                    - text: Summary
                    - textbox "Summary" [ref=f2e128]: Track a personal daily habit.
                  - generic [ref=f2e129]:
                    - text: Problem statement
                    - textbox "Problem statement" [ref=f2e130]: A person needs a record of daily check-ins.
                  - generic [ref=f2e131]:
                    - text: Proposed solution
                    - textbox "Proposed solution" [ref=f2e132]: A dated check-in journal.
                  - group [ref=f2e133]:
                    - generic "Target users (1)" [ref=f2e134] [cursor=pointer]
                  - group [ref=f2e135]:
                    - generic "User goals (1)" [ref=f2e136] [cursor=pointer]
                  - group [ref=f2e137]:
                    - generic "In scope (1)" [ref=f2e138] [cursor=pointer]
                  - group [ref=f2e139]:
                    - generic "Out of scope (1)" [ref=f2e140] [cursor=pointer]
                  - group [ref=f2e141]:
                    - generic "Functional requirements (1)" [ref=f2e142] [cursor=pointer]
                    - generic [ref=f2e143]:
                      - generic [ref=f2e144]:
                        - generic [ref=f2e145]:
                          - text: Functional requirements 1
                          - textbox "Functional requirements 1" [ref=f2e146]: Record one check-in per local day
                        - button "Remove Functional requirements 1" [disabled]: Remove
                        - generic [ref=f2e147]: fr_checkin
                      - button "Add functional requirements item" [ref=f2e148] [cursor=pointer]
                  - group [ref=f2e149]:
                    - generic "Nonfunctional requirements (0)" [ref=f2e150] [cursor=pointer]
                  - group [ref=f2e151]:
                    - generic "Prerequisites (0)" [ref=f2e152] [cursor=pointer]
                  - group [ref=f2e153]:
                    - generic "Assumptions (1)" [ref=f2e154] [cursor=pointer]
                  - group [ref=f2e155]:
                    - generic "Risks (0)" [ref=f2e156] [cursor=pointer]
                  - group [ref=f2e157]:
                    - generic "Open questions (0)" [ref=f2e158] [cursor=pointer]
                  - heading "Epics and stories" [level=3] [ref=f2e159]
                  - region "Edit epic 1" [ref=f2e160]:
                    - generic [ref=f2e161]:
                      - text: Epic 1 title
                      - textbox "Epic 1 title" [ref=f2e162]: Daily journal
                    - generic [ref=f2e163]:
                      - text: Epic 1 goal
                      - textbox "Epic 1 goal" [ref=f2e164]: Record a daily habit
                    - generic [ref=f2e165]:
                      - text: Epic 1 priority
                      - combobox "Epic 1 priority" [ref=f2e166]:
                        - option "P0"
                        - option "P1" [selected]
                        - option "P2"
                        - option "P3"
                    - button "Remove epic 1" [disabled]
                    - region "Edit story story_checkin" [ref=f2e167]:
                      - generic [ref=f2e168]:
                        - text: Story title (story_checkin)
                        - textbox "Story title (story_checkin)" [ref=f2e169]: Record today's check-in
                      - generic [ref=f2e170]:
                        - text: User story (story_checkin)
                        - textbox "User story (story_checkin)" [ref=f2e171]: As a habit tracker, I want to record a daily check-in, so that I can review my progress.
                      - paragraph [ref=f2e172]: As a [user], I want [capability], so that [benefit].
                      - generic [ref=f2e173]:
                        - text: Story description (story_checkin)
                        - textbox "Story description (story_checkin)" [ref=f2e174]: Keep the saved date and completion state.
                      - generic [ref=f2e175]:
                        - text: Story priority (story_checkin)
                        - combobox "Story priority (story_checkin)" [ref=f2e176]:
                          - option "P0"
                          - option "P1" [selected]
                          - option "P2"
                          - option "P3"
                      - generic [ref=f2e177]:
                        - text: Requirement references (story_checkin)
                        - listbox "Requirement references (story_checkin)" [ref=f2e178]:
                          - 'option "fr_checkin: Record one check-in per local day" [selected] [ref=f2e179]'
                      - generic [ref=f2e180]:
                        - text: Dependencies (story_checkin)
                        - listbox "Dependencies (story_checkin)" [ref=f2e181]
                      - paragraph [ref=f2e182]: Use Ctrl or Command to select multiple items or clear a dependency. Removing a referenced requirement or story requires correcting its references before saving.
                      - generic [ref=f2e183]:
                        - generic [ref=f2e184]:
                          - text: Given (criterion_checkin)
                          - textbox "Given (criterion_checkin)" [ref=f2e185]: Today's habit is incomplete
                        - generic [ref=f2e186]:
                          - text: When (criterion_checkin)
                          - textbox "When (criterion_checkin)" [ref=f2e187]: I record today's check-in
                        - generic [ref=f2e188]:
                          - text: Then (criterion_checkin)
                          - textbox "Then (criterion_checkin)" [ref=f2e189]: Today's habit is shown as complete after reload
                        - button "Remove criterion 1" [disabled]
                      - generic [ref=f2e190]:
                        - button "Add acceptance criterion" [ref=f2e191] [cursor=pointer]
                        - button "Remove story" [disabled]
                    - button "Add user story" [ref=f2e192] [cursor=pointer]
                  - button "Add epic" [ref=f2e193] [cursor=pointer]
                  - heading "Items requiring confirmation" [level=3] [ref=f2e194]
                  - button "Add confirmation" [ref=f2e195] [cursor=pointer]
                - generic [ref=f2e196]:
                  - button "Save draft" [ref=f2e197] [cursor=pointer]
                  - button "Cancel editing" [ref=f2e198] [cursor=pointer]
                  - button "Inspect latest saved revision" [ref=f2e199] [cursor=pointer]
            - group [ref=f2e200]:
              - generic "Planning run history (0)" [ref=f2e201] [cursor=pointer]
          - generic [ref=f2e207]:
            - heading "Room for what comes next" [level=2] [ref=f2e208]
            - paragraph [ref=f2e209]: Architecture, tasks, additional agents, and delivery evidence will live here.
            - generic [ref=f2e210]: Coming in a later stage
      - contentinfo [ref=f2e214]:
        - generic [ref=f2e215]: Built for the way you think.
        - generic [ref=f2e216]: Local workspace · No AI connected
  - alert [ref=f2e217]
```

# Test source

```ts
  1  | /** Real UI/API/PostgreSQL. Plans seeded below are explicitly HUMAN-AUTHORED,
  2  |  * and are never presented as live model verification. No HTTP interceptions. */
  3  | import { test, expect, type Page } from "@playwright/test";
  4  | import { execFileSync } from "node:child_process";
  5  | import { createWorkspace, signup, signout } from "./helpers";
  6  | 
  7  | test.beforeAll(()=>{execFileSync("uv",["run","--directory","../api","python","-m","scripts.prepare_tests"],{stdio:"pipe"});});
  8  | async function setup(page:Page) {
  9  |   await signup(page,`pm-${test.info().project.name}-${Date.now()}@example.com`);
  10 |   await createWorkspace(page,"Product planning");
  11 |   await page.getByLabel("Project description",{exact:true}).fill("A personal habit journal with daily check-ins.");
  12 |   const save=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/api/v1/projects"));
  13 |   await page.getByRole("button",{name:"Create project",exact:true}).click();
  14 |   const project=await (await save).json();
  15 |   await expect(page.getByRole("heading",{name:"Product Plan",exact:true})).toBeVisible();
  16 |   const user=await (await page.request.get("/api/v1/auth/me")).json();
  17 |   return {project,user};
  18 | }
  19 | 
  20 | test("provider setup and empty state are honest; visiting a project makes no model request",async({page})=>{
  21 |   let posts=0;page.on("request",r=>{if(r.method()==="POST" && r.url().endsWith("/pm-runs"))posts++;});
  22 |   await setup(page);
  23 |   await expect(page.getByRole("heading",{name:"Configure the Product Manager"})).toBeVisible();
  24 |   await expect(page.getByRole("heading",{name:"Your requirements start here"})).toBeVisible();
  25 |   await expect(page.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeDisabled();
  26 |   await page.reload();
  27 |   await expect(page.getByRole("heading",{name:"Product Plan",exact:true})).toBeVisible();
  28 |   expect(posts).toBe(0);
  29 | });
  30 | 
  31 | test("human-authored fixture: edit criterion, persist, approve exact version, history and isolation",async({page,browser})=>{
  32 |   const {project,user}=await setup(page);
  33 |   const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  34 |   expect(fixture.origin).toBe("human_authored");expect(fixture.model_call).toBe(false);
  35 |   await page.reload();
  36 |   const panel=page.locator("#product-plan");
  37 |   await expect(panel.getByTestId("plan-state")).toHaveText("draft");
  38 |   await expect(panel.getByRole("heading",{name:"Daily journal",exact:true})).toBeVisible();
  39 |   await panel.getByRole("button",{name:"Edit draft",exact:true}).click();
  40 |   const criterion="The check-in stays complete after reloading the journal.";
> 41 |   await panel.getByLabel("Then (criterion_checkin)",{exact:true}).fill(criterion);
     |                                                                   ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  42 |   await panel.getByRole("button",{name:"Save draft",exact:true}).click();
  43 |   await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
  44 |   await page.reload();
  45 |   await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
  46 |   const saved=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  47 |   expect(saved.revision).toBe(2);expect(saved.document.epics[0].stories[0].acceptance_criteria[0].then).toBe(criterion);
  48 |   await panel.getByRole("button",{name:"Approve plan",exact:true}).click();
  49 |   await expect(panel.getByRole("heading",{name:"Approve version 1, revision 2?",exact:true})).toBeVisible();
  50 |   await panel.getByRole("button",{name:"Confirm approval",exact:true}).click();
  51 |   await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  52 |   await page.reload();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  53 |   await expect(panel.getByRole("button",{name:"Edit draft",exact:true})).toHaveCount(0);
  54 |   const approved=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  55 |   expect(approved.approved_by).toBe(user.id);expect(approved.approved_at).toBeTruthy();
  56 |   await panel.getByRole("button",{name:"Create draft copy",exact:true}).click();
  57 |   await expect(panel.getByTestId("plan-state")).toHaveText("draft");
  58 |   await expect(panel.getByLabel("Plan version",{exact:true})).toContainText("Version 2");
  59 |   await panel.getByLabel("Plan version",{exact:true}).selectOption(fixture.plan_id);
  60 |   await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  61 |   await page.getByRole("button",{name:"Toggle color theme"}).click();
  62 |   await expect(panel.getByRole("heading",{name:"Daily journal",exact:true})).toBeVisible();
  63 |   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  64 |   await page.screenshot({path:`../../docs/evidence/stage03-${test.info().project.name}-human-plan.png`,fullPage:true});
  65 |   const other=await browser.newContext();const outsider=await other.newPage();
  66 |   await signup(outsider,`pm-outsider-${Date.now()}@example.com`);await createWorkspace(outsider,"Unrelated private space");
  67 |   const denied=await outsider.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`);
  68 |   expect(denied.status()).toBe(404);expect(await denied.text()).not.toContain(criterion);
  69 |   await outsider.goto(`/projects/${project.id}`);
  70 |   await expect(outsider.getByRole("main").getByRole("alert")).toHaveText("Project not found.");
  71 |   await expect(outsider.getByText(criterion,{exact:false})).toHaveCount(0);
  72 |   await other.close();
  73 |   await signout(page);await page.goto(`/projects/${project.id}`);
  74 |   await expect(page.getByRole("heading",{name:"Sign in to your workspace"})).toBeVisible();
  75 |   await expect(page.getByText(criterion,{exact:false})).toHaveCount(0);
  76 | });
  77 | 
  78 | test("a save conflict preserves local edits for comparison",async({page})=>{
  79 |   const {project,user}=await setup(page);
  80 |   const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  81 |   await page.reload();await page.getByRole("button",{name:"Edit draft",exact:true}).click();
  82 |   const field=page.getByLabel("Then (criterion_checkin)",{exact:true});
  83 |   await field.fill("My preserved local criterion");
  84 |   const original=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  85 |   original.document.summary.text="A competing editor saved this first.";
  86 |   const csrf=await (await page.request.get("/api/v1/auth/csrf")).json();
  87 |   const other=await page.request.put(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`,{headers:{Origin:"http://localhost:3001","X-CSRF-Token":csrf.csrf_token},data:{expected_revision:1,document:original.document}});
  88 |   expect(other.status()).toBe(200);
  89 |   await page.getByRole("button",{name:"Save draft",exact:true}).click();
  90 |   await expect(page.locator("#product-plan").getByRole("alert")).toContainText("exact saved draft revision");
  91 |   await expect(field).toHaveValue("My preserved local criterion");
  92 |   await page.getByRole("button",{name:"Inspect latest saved revision",exact:true}).click();
  93 |   await expect(page.getByRole("heading",{name:"Latest saved revision 2"})).toBeVisible();
  94 |   await expect(field).toHaveValue("My preserved local criterion");
  95 | });
  96 | 
```