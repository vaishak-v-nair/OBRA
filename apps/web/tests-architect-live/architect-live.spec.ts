/** PAID OPT-IN ONLY. One real Architect generation, no controlled responses. */
import {test,expect} from "@playwright/test";
import {execFileSync} from "node:child_process";
import {writeFileSync} from "node:fs";
import {signup,createWorkspace} from "../tests/helpers";
import {evidencePath} from "../tests/evidence";
import {architectBoundary} from "../tests/architect-boundary";
import {architectPreflight,observeRoutes,preflightProof} from "../tests/architect-preflight";

test("one real Architect response, persisted DAG, human editing, approval and isolation",async({page,browser})=>{
  const proof:Record<string,unknown>={stage:"stage04-architect",execution_class:"real_gemini_browser",provider_double:false,result:"FAIL",started_at:new Date().toISOString(),pm_generation_posts:0};
  const boundary=await architectBoundary(page.context(),true),budget=boundary.budget;
  const preflight=preflightProof();observeRoutes(page,preflight);
  const command=(...args:string[])=>execFileSync("uv",["run","--directory","../api","python","-m",...args],{encoding:"utf8",stdio:["ignore","pipe","pipe"]});
  try{
    command("scripts.prepare_tests");
    proof.step="phase1_preflight";
    const {project,user,source}=await architectPreflight(page,preflight);
    Object.assign(proof,{project_id:project.id,initiator_id:user.id,source_plan_id:source.id,source_version:source.version,source_revision:source.revision,source_hash:source.content_hash,source_origin:"human_authored",preflight_generation_budget:{...budget}});
    const panel=page.getByRole("region",{name:"Architecture workspace"});
    await panel.getByLabel("Optional architectural constraints").fill("Keep a compact single-server proposal: 1-2 components and 3-4 scoped tasks with concise criteria. No extra features. Proposed designs only.");
    const generating=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/architect-runs"),{timeout:260000});
    boundary.openOneRequest(preflight);
    proof.step="phase2_provider_request";await panel.getByRole("button",{name:"Generate Architecture",exact:true}).click();const response=await generating;
    proof.http_status=response.status();
    const body=await response.json();
    if(response.status()!==201){proof.run_id=body.error?.run_id;proof.error_category=body.error?.code;if(body.error?.run_id)proof.failure_sql=JSON.parse(command("scripts.inspect_architect_run","--run",body.error.run_id));await expect(panel.getByRole("alert")).toBeVisible();proof.failure_visible=true;}
    expect(response.status()).toBe(201);const run=body;proof.step="phase3_verification";
    Object.assign(proof,{run_id:run.id,architecture_id:run.architecture_id,requested_model:run.requested_model,returned_model:run.returned_model,provider_response_id:run.provider_response_id,usage:run.usage});
    await expect(panel.getByTestId("architecture-state")).toHaveText("draft");
    const url=`/api/v1/projects/${project.id}/architectures/${run.architecture_id}`;
    const draft=await(await page.request.get(url)).json();expect(draft.generation.id).toBe(run.id);expect(draft.document.tasks.length).toBeGreaterThan(0);expect(draft.graph.valid).toBe(true);expect(draft.coverage.approvable).toBe(true);expect(draft.approved_by).toBeNull();
    proof.draft_sql=JSON.parse(command("scripts.inspect_architect_run","--run",run.id));proof.draft_api_hash=draft.content_hash;
    await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Task Graph",exact:true}).click();await expect(page.getByRole("img",{name:"Saved validated dependency graph"})).toBeVisible();proof.browser_graph_rendered=true;
    await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();await panel.getByRole("button",{name:"Edit architecture draft",exact:true}).click();
    await panel.locator(".architect-editor > details").filter({has:page.locator("summary",{hasText:/^Tasks$/})}).locator(":scope > summary").click();
    const criterion="Given a saved daily check-in, when this page reloads, then the human-reviewed acceptance criterion remains persisted.";
    await panel.getByLabel(`${draft.document.tasks[0].title} · Acceptance criteria`,{exact:true}).fill(criterion);
    await panel.getByRole("button",{name:"Save architecture draft",exact:true}).click();await expect(panel.getByRole("status")).toContainText("Human edits saved");
    await page.reload();await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
    const edited=await(await page.request.get(url)).json();expect(edited.document.tasks[0].acceptance_criteria[0]).toBe(criterion);proof.edited_criterion_persisted=true;
    await panel.getByRole("button",{name:"Review architecture approval",exact:true}).click();
    for(const obligation of edited.coverage.review_obligations){await page.locator(`[id=${JSON.stringify(`ack-${obligation.id}`)}]`).fill("The test owner explicitly reviewed and accepts this recorded planning uncertainty for the isolated verification.");}
    await panel.getByRole("button",{name:"Confirm architecture approval",exact:true}).click();await expect(panel.getByTestId("architecture-state")).toHaveText("approved");
    await page.reload();await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();await expect(panel.getByTestId("architecture-state")).toHaveText("approved");
    const approved=await(await page.request.get(url)).json();proof.approved_api_hash=approved.content_hash;proof.approved_sql=JSON.parse(command("scripts.inspect_architect_run","--run",run.id));
    const context=await browser.newContext({serviceWorkers:"block"}),outsiderBoundary=await architectBoundary(context),outsider=await context.newPage();await signup(outsider,`architect-outsider-${Date.now()}@example.com`);await createWorkspace(outsider,"Unrelated workspace");
    const denied=await outsider.request.get(url);expect(denied.status()).toBe(404);expect(await denied.text()).not.toContain(criterion);await outsider.goto(`/projects/${project.id}`);await expect(outsider.getByRole("main").getByRole("alert")).toHaveText("Project not found.");await expect(outsider.getByText(criterion,{exact:true})).toHaveCount(0);await context.close();
    proof.unrelated_http_status=denied.status();proof.unrelated_generation_budget=outsiderBoundary.budget;expect(outsiderBoundary.budget).toEqual({attempted:0,forwarded:0,blocked:0});expect(budget).toEqual({attempted:1,forwarded:1,blocked:0});proof.result="PASS";proof.step="complete";
  }finally{proof.preflight=preflight;proof.phases=boundary.phases;proof.pm_generation_posts=boundary.pmPosts();proof.generation_budget=budget;proof.completed_at=new Date().toISOString();writeFileSync(evidencePath("live-proof.json"),JSON.stringify(proof,null,2)+"\n");}
});
