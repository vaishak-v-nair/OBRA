# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: architect-live.spec.ts >> one real Architect response, persisted DAG, human editing, approval and isolation
- Location: tests-architect-live\architect-live.spec.ts:8:5

# Error details

```
TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Approve plan', exact: true })

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
        - generic [ref=f2e10]: L
        - generic [ref=f2e11]:
          - generic [ref=f2e12]: Workspace
          - combobox "Workspace" [ref=f2e13]:
            - option "Select workspace" [disabled]
            - option "Live architecture verification" [selected]
      - link "New project" [ref=f2e14] [cursor=pointer]:
        - /url: /projects/new
      - paragraph [ref=f2e16]: WORKSPACE
      - navigation "Main navigation" [ref=f2e17]:
        - link "Chat" [ref=f2e18] [cursor=pointer]:
          - /url: /
        - link "Projects" [ref=f2e24] [cursor=pointer]:
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
          - strong [ref=f2e63]: Chat
        - generic [ref=f2e64]:
          - generic [ref=f2e65]: Product planning
          - button "Toggle color theme" [ref=f2e66] [cursor=pointer]
      - main [ref=f2e73]:
        - generic [ref=f2e75]:
          - generic [ref=f2e76]:
            - paragraph [ref=f2e81]: A LITTLE CLARITY. A LOT OF POSSIBILITY.
            - heading "What would you like to build today?" [level=1] [ref=f2e82]
            - paragraph [ref=f2e83]: Your workspace for planning, building, testing, and delivering software with AI.
          - generic [ref=f2e84]:
            - form "Create project" [ref=f2e85]:
              - generic [ref=f2e86]:
                - generic [ref=f2e87]: Project description
                - textbox "Project description" [ref=f2e88]:
                  - /placeholder: Describe what you’d like to build...
                - generic [ref=f2e89]:
                  - generic [ref=f2e90]:
                    - generic "Attachments are coming in a later stage" [ref=f2e91]:
                      - button "Attachments coming in a later stage" [disabled]
                    - generic "GitHub integration is coming in a later stage" [ref=f2e92]:
                      - button "GitHub integration coming in a later stage" [disabled]
                    - generic [ref=f2e93]: Start with an idea
                  - button "Create project" [ref=f2e94] [cursor=pointer]
              - paragraph [ref=f2e97]: Your description creates a project. AI collaboration is coming in a later stage.
            - generic [ref=f2e98]:
              - link [ref=f2e99] [cursor=pointer]:
                - /url: /projects/new
                - strong [ref=f2e102]: Start a project
                - paragraph [ref=f2e103]: Turn a fresh idea into a place to build.
              - link [ref=f2e107] [cursor=pointer]:
                - /url: /projects
                - strong [ref=f2e110]: Pick up where you left off
                - paragraph [ref=f2e111]: Find your ideas, all in one workspace.
            - generic [ref=f2e115]: Your next great project starts here
      - contentinfo [ref=f2e122]:
        - generic [ref=f2e123]: Built for the way you think.
        - generic [ref=f2e124]: Local development workspace
  - alert [ref=f2e125]
```

# Test source

```ts
  1  | /** PAID OPT-IN ONLY. One real Architect generation, no controlled responses. */
  2  | import {test,expect} from "@playwright/test";
  3  | import {execFileSync} from "node:child_process";
  4  | import {writeFileSync} from "node:fs";
  5  | import {signup,createWorkspace} from "../tests/helpers";
  6  | import {evidencePath} from "../tests/evidence";
  7  | 
  8  | test("one real Architect response, persisted DAG, human editing, approval and isolation",async({page,browser})=>{
  9  |   const proof:Record<string,unknown>={stage:"stage04-architect",execution_class:"real_gemini_browser",provider_double:false,result:"FAIL",started_at:new Date().toISOString(),pm_generation_posts:0};
  10 |   const budget={attempted:0,forwarded:0,blocked:0};
  11 |   const command=(...args:string[])=>execFileSync("uv",["run","--directory","../api","python","-m",...args],{encoding:"utf8",stdio:["ignore","pipe","pipe"]});
  12 |   await page.route(/\/api\/v1\/projects\/[^/]+\/(pm-runs|architect-runs)(\?.*)?$/,async route=>{
  13 |     if(route.request().method()!=="POST"){await route.continue();return;}
  14 |     budget.attempted++;
  15 |     if(route.request().url().includes("/pm-runs")){proof.pm_generation_posts=Number(proof.pm_generation_posts)+1;budget.blocked++;await route.abort("blockedbyclient");return;}
  16 |     if(budget.forwarded>=1){budget.blocked++;await route.abort("blockedbyclient");return;}
  17 |     budget.forwarded++;await route.continue();
  18 |   });
  19 |   try{
  20 |     command("scripts.prepare_tests");
  21 |     await signup(page,`architect-live-${Date.now()}@example.com`);await createWorkspace(page,"Live architecture verification");
  22 |     await page.getByLabel("Project description",{exact:true}).fill("Personal daily habit check-in with saved status after reload. One user, no social features.");
  23 |     const creating=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/api/v1/projects"));await page.getByRole("button",{name:"Create project",exact:true}).click();
  24 |     const project=await(await creating).json(),user=await(await page.request.get("/api/v1/auth/me")).json();
  25 |     const authored=JSON.parse(command("scripts.seed_pm_fixture","--project",project.id,"--actor",user.id));
  26 |     expect(authored.model_call).toBe(false);expect(authored.origin).toBe("human_authored");
> 27 |     await page.reload();await page.getByRole("button",{name:"Approve plan",exact:true}).click();await page.getByRole("button",{name:"Confirm approval",exact:true}).click();await expect(page.getByTestId("plan-state")).toHaveText("approved");
     |                                                                                         ^ TimeoutError: locator.click: Timeout 15000ms exceeded.
  28 |     const source=await(await page.request.get(`/api/v1/projects/${project.id}/architect-source`)).json();
  29 |     Object.assign(proof,{project_id:project.id,initiator_id:user.id,source_plan_id:source.id,source_version:source.version,source_revision:source.revision,source_hash:source.content_hash,source_origin:authored.origin});
  30 |     await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
  31 |     const panel=page.getByRole("region",{name:"Architecture workspace"});
  32 |     await panel.getByLabel("Optional architectural constraints").fill("Keep a compact single-server proposal: 1-2 components and 3-4 scoped tasks with concise criteria. No extra features. Proposed designs only.");
  33 |     const generating=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/architect-runs"),{timeout:260000});
  34 |     proof.step="provider_request";await panel.getByRole("button",{name:"Generate Architecture",exact:true}).click();const response=await generating;
  35 |     proof.http_status=response.status();
  36 |     const body=await response.json();
  37 |     if(response.status()!==201){proof.run_id=body.error?.run_id;proof.error_category=body.error?.code;if(body.error?.run_id)proof.failure_sql=JSON.parse(command("scripts.inspect_architect_run","--run",body.error.run_id));await expect(panel.getByRole("alert")).toBeVisible();proof.failure_visible=true;}
  38 |     expect(response.status()).toBe(201);const run=body;
  39 |     Object.assign(proof,{run_id:run.id,architecture_id:run.architecture_id,requested_model:run.requested_model,returned_model:run.returned_model,provider_response_id:run.provider_response_id,usage:run.usage});
  40 |     await expect(panel.getByTestId("architecture-state")).toHaveText("draft");
  41 |     const url=`/api/v1/projects/${project.id}/architectures/${run.architecture_id}`;
  42 |     const draft=await(await page.request.get(url)).json();expect(draft.generation.id).toBe(run.id);expect(draft.document.tasks.length).toBeGreaterThan(0);expect(draft.graph.valid).toBe(true);expect(draft.coverage.approvable).toBe(true);expect(draft.approved_by).toBeNull();
  43 |     proof.draft_sql=JSON.parse(command("scripts.inspect_architect_run","--run",run.id));proof.draft_api_hash=draft.content_hash;
  44 |     await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Task Graph",exact:true}).click();await expect(page.getByRole("img",{name:"Saved validated dependency graph"})).toBeVisible();proof.browser_graph_rendered=true;
  45 |     await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();await panel.getByRole("button",{name:"Edit architecture draft",exact:true}).click();
  46 |     await panel.locator(".architect-editor > details").filter({has:page.locator("summary",{hasText:/^Tasks$/})}).locator(":scope > summary").click();
  47 |     const criterion="Given a saved daily check-in, when this page reloads, then the human-reviewed acceptance criterion remains persisted.";
  48 |     await panel.getByLabel(`${draft.document.tasks[0].title} · Acceptance criteria`,{exact:true}).fill(criterion);
  49 |     await panel.getByRole("button",{name:"Save architecture draft",exact:true}).click();await expect(panel.getByRole("status")).toContainText("Human edits saved");
  50 |     await page.reload();await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
  51 |     const edited=await(await page.request.get(url)).json();expect(edited.document.tasks[0].acceptance_criteria[0]).toBe(criterion);proof.edited_criterion_persisted=true;
  52 |     await panel.getByRole("button",{name:"Review architecture approval",exact:true}).click();
  53 |     for(const obligation of edited.coverage.review_obligations){await page.locator(`[id=${JSON.stringify(`ack-${obligation.id}`)}]`).fill("The test owner explicitly reviewed and accepts this recorded planning uncertainty for the isolated verification.");}
  54 |     await panel.getByRole("button",{name:"Confirm architecture approval",exact:true}).click();await expect(panel.getByTestId("architecture-state")).toHaveText("approved");
  55 |     await page.reload();await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();await expect(panel.getByTestId("architecture-state")).toHaveText("approved");
  56 |     const approved=await(await page.request.get(url)).json();proof.approved_api_hash=approved.content_hash;proof.approved_sql=JSON.parse(command("scripts.inspect_architect_run","--run",run.id));
  57 |     const context=await browser.newContext(),outsider=await context.newPage();await signup(outsider,`architect-outsider-${Date.now()}@example.com`);await createWorkspace(outsider,"Unrelated workspace");
  58 |     const denied=await outsider.request.get(url);expect(denied.status()).toBe(404);expect(await denied.text()).not.toContain(criterion);await outsider.goto(`/projects/${project.id}`);await expect(outsider.getByRole("main").getByRole("alert")).toHaveText("Project not found.");await expect(outsider.getByText(criterion,{exact:true})).toHaveCount(0);await context.close();
  59 |     proof.unrelated_http_status=denied.status();expect(budget).toEqual({attempted:1,forwarded:1,blocked:0});proof.result="PASS";proof.step="complete";
  60 |   }finally{proof.generation_budget=budget;proof.completed_at=new Date().toISOString();writeFileSync(evidencePath("live-proof.json"),JSON.stringify(proof,null,2)+"\n");}
  61 | });
  62 | 
```