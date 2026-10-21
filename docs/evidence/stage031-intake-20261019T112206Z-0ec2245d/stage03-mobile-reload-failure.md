# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: pm.spec.ts >> human-authored fixture: edit criterion, persist, approve exact version, history and isolation
- Location: tests\pm.spec.ts:31:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('#product-plan').getByText('The check-in stays complete after reloading the journal.').first()
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('#product-plan').getByText('The check-in stays complete after reloading the journal.').first() with timeout 5000ms
  - waiting for locator('#product-plan').getByText('The check-in stays complete after reloading the journal.').first()

```

```yaml
- link "Skip to content":
  - /url: "#main"
- banner:
  - button "Open navigation"
  - text: Workspace
  - strong: Projects
  - button "Toggle color theme"
- main:
  - link "All projects":
    - /url: /projects
  - paragraph: PROJECT OVERVIEW
  - heading "A personal habit journal with daily check-ins." [level=1]
  - text: Created Created
  - time: 10/19/2026, 11:18:24 AM
  - heading "Where it begins" [level=2]
  - paragraph: Your original project description
  - paragraph: A personal habit journal with daily check-ins.
  - button "Edit project"
  - region "Product Plan":
    - paragraph: PRODUCT MANAGER
    - heading "Product Plan" [level=2]
    - text: One planning agent
    - paragraph: Turn your idea into reviewable requirements. Generation uses your configured AI provider and may incur usage.
    - complementary:
      - heading "Configure the Product Manager" [level=3]
      - paragraph: Set GEMINI_API_KEY and ORBA_PM_MODEL in the root .env, then restart the API. Configuration does not prove provider access.
      - paragraph: Keep credentials on the API server. Set an explicit supported Gemini model. A configured key does not guarantee model access.
    - group: Generate another product plan
    - button "Check status"
    - text: Plan version
    - combobox "Plan version":
      - option "Version 1 · draft · revision 1" [selected]
    - text: draft
    - paragraph: Version 1 · revision 1 · Human-authored plan
    - heading "Product name" [level=3]
    - paragraph: Habit journal — human-authored test fixture
    - group: Human edited
    - heading "Summary" [level=3]
    - paragraph: Track a personal daily habit.
    - group: Human edited
    - heading "Problem statement" [level=3]
    - paragraph: A person needs a record of daily check-ins.
    - group: Human edited
    - heading "Proposed solution" [level=3]
    - paragraph: A dated check-in journal.
    - group: Human edited
    - heading "Target users" [level=3]
    - list:
      - listitem:
        - text: One person tracking a habit
        - group: Human edited
    - heading "User goals" [level=3]
    - list:
      - listitem:
        - text: See whether today's habit is complete
        - group: Human edited
    - heading "In scope" [level=3]
    - list:
      - listitem:
        - text: Daily check-ins
        - group: Human edited
    - heading "Out of scope" [level=3]
    - list:
      - listitem:
        - text: Social sharing
        - group: Human edited
    - heading "Functional requirements" [level=3]
    - list:
      - listitem:
        - text: Record one check-in per local day
        - group: Human edited
    - heading "Assumptions" [level=3]
    - list:
      - listitem:
        - text: A single local user is sufficient initially
        - group: Human edited
    - heading "Epics and user stories" [level=3]
    - article:
      - heading "Daily journal" [level=4]
      - text: P1
      - paragraph: Record a daily habit
      - group: Human edited
      - article:
        - heading "Record today's check-in P1" [level=5]
        - paragraph: As a habit tracker, I want to record a daily check-in, so that I can review my progress.
        - paragraph: Keep the saved date and completion state.
        - group: Human edited
        - paragraph: "Requirements: fr_checkin"
        - heading "Acceptance criteria" [level=6]
        - list:
          - listitem:
            - paragraph:
              - strong: Given
              - text: Today's habit is incomplete
            - paragraph:
              - strong: When
              - text: I record today's check-in
            - paragraph:
              - strong: Then
              - text: Today's habit is shown as complete after reload
            - group: Human edited
    - heading "Items requiring confirmation" [level=3]
    - paragraph: No confirmation items recorded. Review assumptions and open questions before approval.
    - button "Edit draft"
    - button "Approve plan"
    - group: Planning run history (0)
  - heading "Room for what comes next" [level=2]
  - paragraph: Architecture, tasks, additional agents, and delivery evidence will live here.
  - text: Coming in a later stage
- contentinfo: Local development workspace
- alert
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
  41 |   await panel.getByLabel("Then (criterion_checkin)",{exact:true}).fill(criterion);
  42 |   await panel.getByRole("button",{name:"Save draft",exact:true}).click();
  43 |   await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
  44 |   await page.reload();
> 45 |   await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
     |                                                                  ^ Error: expect(locator).toBeVisible() failed
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