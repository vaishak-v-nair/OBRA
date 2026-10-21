/** Mandatory REAL model-backed browser flow. No fixture-generated responses or intercepts. */
import {test,expect} from "@playwright/test";
import {execFileSync} from "node:child_process";
import {writeFileSync} from "node:fs";
import {evidencePath} from "../tests/evidence";
import {signup,createWorkspace,signout} from "../tests/helpers";
import {allowOneGeneration} from "../tests/generation-budget";

test("real model plan, editable criteria, persisted approval and unrelated-user denial",async({page,browser})=>{
  const proof:Record<string,unknown>={execution_class:"real_gemini_browser",provider_double:false,result:"FAIL",stage:"setup",started_at:new Date().toISOString()};
  const budget=await allowOneGeneration(page);
  let posts=0;
  page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs")){posts++;proof.client_request_id=JSON.parse(r.postData()??"{}").client_request_id;}});
  try {
  execFileSync("uv",["run","--directory","../api","python","-m","scripts.prepare_tests"],{stdio:"pipe"});
  const email=`live-browser-${Date.now()}@example.com`;
  await signup(page,email);await signout(page);
  await page.getByLabel("Email",{exact:true}).fill(email);await page.getByLabel("Password",{exact:true}).fill("A long browser password!");await page.getByRole("button",{name:"Sign in",exact:true}).click();
  await expect(page.getByRole("heading",{name:"A home for your ideas"})).toBeVisible();
  await createWorkspace(page,"Live product planning");
  const brief="Build a personal daily habit check-in page for one user. Save whether today's habit is complete and show the saved result after reload. No social features.";
  await page.getByLabel("Project description",{exact:true}).fill(brief);
  const creation=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/api/v1/projects"));
  await page.getByRole("button",{name:"Create project",exact:true}).click();const project=await (await creation).json();
  const user=await (await page.request.get("/api/v1/auth/me")).json();proof.actor_id=user.id;proof.project_id=project.id;
  const panel=page.locator("#product-plan");
  await panel.getByLabel("Additional instructions (optional)").fill("Keep this small: exactly 1 epic, 1 story and at most 2 criteria. Use concise text. Identify missing decisions explicitly; do not add extra features.");
  const generation=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/pm-runs"),{timeout:260000});
  proof.stage="provider_request";
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();const response=await generation;
  if(response.status()!==201){const error=(await response.json()).error;proof.http_status=response.status();proof.run_id=error?.run_id;proof.error_category=error?.code;if(error?.run_id)proof.failure_sql=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.inspect_pm_run","--run",error.run_id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));await expect(panel.getByRole("alert")).toBeVisible();proof.failure_visible=true;}
  expect(response.status()).toBe(201);const run=await response.json();proof.run_id=run.id;proof.plan_id=run.plan_id;proof.stage="draft_audit";
  await expect(panel.getByTestId("plan-state")).toHaveText("draft");
  const apiPlan=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${run.plan_id}`)).json();
  expect(apiPlan.generation.id).toBe(run.id);expect(apiPlan.document.epics.length).toBeGreaterThan(0);expect(apiPlan.document.epics[0].stories.length).toBeGreaterThan(0);expect(apiPlan.approved_by).toBeNull();
  const draftSql=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.inspect_pm_run","--run",run.id,"--expect-state","draft"],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  expect(draftSql.content_hash).toBe(apiPlan.content_hash);expect(draftSql.plan_id).toBe(apiPlan.id);expect(draftSql.returned_model).toBe(run.returned_model);expect(draftSql.usage).toEqual(run.usage);proof.draft_sql=draftSql;proof.draft_api_hash=apiPlan.content_hash;
  proof.stage="edit_and_reload";
  await panel.getByRole("button",{name:"Edit draft",exact:true}).click();
  const criterion="The saved daily check-in is still visible after the page is reloaded.";
  await panel.getByLabel(/^Then \(/).first().fill(criterion);
  for(const item of apiPlan.document.confirmations){if(item.blocking){await panel.getByRole("combobox",{name:`Disposition (${item.key})`,exact:true}).selectOption("deferred");await panel.getByLabel(`Disposition reason (${item.key})`,{exact:true}).fill("The test owner explicitly defers this decision for this isolated planning verification.");}}
  const saveResponse=page.waitForResponse(r=>r.request().method()==="PUT" && r.url().endsWith(`/pm-plans/${run.plan_id}`));
  await panel.getByRole("button",{name:"Save draft",exact:true}).click();
  expect((await saveResponse).status()).toBe(200);
  await expect(panel.getByRole("form",{name:"Edit product plan",exact:true})).toHaveCount(0);
  await expect(panel.getByRole("status")).toContainText("saved");
  await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();await page.reload();await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
  proof.stage="approval_and_reload";
  await panel.getByRole("button",{name:"Approve plan",exact:true}).click();await panel.getByRole("button",{name:"Confirm approval",exact:true}).click();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  await page.reload();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  const approved=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${run.plan_id}`)).json();expect(approved.approved_at).toBeTruthy();expect(approved.document.epics[0].stories[0].acceptance_criteria[0].then).toBe(criterion);
  const approvedSql=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.inspect_pm_run","--run",run.id,"--expect-state","approved"],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  expect(approvedSql.content_hash).toBe(approved.content_hash);expect(approvedSql.approved_by).toBe(user.id);expect(approvedSql.revision).toBe(approved.revision);proof.approved_sql=approvedSql;proof.approved_api_hash=approved.content_hash;proof.stage="unrelated_user_isolation";
  const context=await browser.newContext();const outsider=await context.newPage();await signup(outsider,`live-outsider-${Date.now()}@example.com`);await createWorkspace(outsider,"Unrelated user");
  const denied=await outsider.request.get(`/api/v1/projects/${project.id}/pm-plans/${run.plan_id}`);expect(denied.status()).toBe(404);expect(await denied.text()).not.toContain(criterion);
  await outsider.goto(`/projects/${project.id}`);await expect(outsider.getByRole("main").getByRole("alert")).toHaveText("Project not found.");await expect(outsider.getByText(criterion,{exact:false})).toHaveCount(0);await context.close();
  Object.assign(proof,{result:"PASS",stage:"complete",scenario:"Real browser Generate -> edit -> reload -> approve -> reload -> unrelated denial",http_status:response.status(),run_id:run.id,plan_id:run.plan_id,provider:run.provider,model:run.returned_model,provider_response_id:run.provider_response_id,provider_request_id:run.provider_request_id,usage:run.usage,state:approved.state,version:approved.version,revision:approved.revision,approved_by:approved.approved_by,approved_at:approved.approved_at,unrelated_http_status:denied.status(),mocks:false});
  expect(budget).toEqual({attempted:1,forwarded:1,blocked:0});
  } finally {proof.generation_posts=posts;proof.generation_dispatches=budget.forwarded;proof.blocked_generation_posts=budget.blocked;proof.generation_budget=budget;writeFileSync(evidencePath("live-proof.json"),JSON.stringify(proof,null,2)+"\n");}
});
