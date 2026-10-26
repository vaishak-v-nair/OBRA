/** Real browser, API/auth/CSRF and PostgreSQL. ONLY model behavior is a labeled
 * deterministic provider DOUBLE. Transport faults below are explicitly injected.
 * None of these tests are live Gemini evidence. */
import {test,expect,type Page} from "@playwright/test";
import {execFileSync} from "node:child_process";
import {signup,createWorkspace} from "../tests/helpers";
import {evidencePath} from "../tests/evidence";
import {writeFileSync} from "node:fs";
import {allowOneGeneration} from "../tests/generation-budget";
import {createProject} from "../tests/architect-preflight";

async function setup(page:Page) {
  execFileSync("uv",["run","--directory","../api","python","-m","scripts.prepare_tests"],{stdio:"pipe"});
  await signup(page,`controlled-${test.info().project.name}-${Date.now()}@example.com`);
  await createWorkspace(page,"Controlled provider verification");
  const project=await createProject(page,"Track one daily habit.");
  await expect(page.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeEnabled();
  const user=await (await page.request.get("/api/v1/auth/me")).json();
  return {project,user,panel:page.locator("#product-plan")};
}

for(const scenario of [
  {name:"upstream503/public502",instructions:"unavailable",status:502,category:"provider_unavailable",message:"temporarily unavailable",upstream:503},
  {name:"provider429",instructions:"rate limited",status:429,category:"provider_rate_limited",message:"rate limit was reached",upstream:429},
  {name:"malformed structured response",instructions:"invalid response",status:502,category:"invalid_model_response",message:"product-document contract",upstream:null},
]) {
  test(`controlled ${scenario.name} preserves approval and input without repeated-click dispatch`,async({page})=>{
    const {project,user,panel}=await setup(page);
    const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
    await page.reload();await panel.getByRole("button",{name:"Approve plan",exact:true}).click();
    await panel.getByRole("button",{name:"Confirm approval",exact:true}).click();
    await expect(panel.getByTestId("plan-state")).toHaveText("approved");
    const path=`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`;
    const before=await (await page.request.get(path)).json();
    await panel.getByText("Generate another product plan",{exact:true}).click();
    const brief=`Keep this brief during controlled ${scenario.name}.`;
    const instructions=`Controlled provider DOUBLE: ${scenario.instructions}`;
    await panel.getByLabel("Product brief",{exact:true}).fill(brief);
    await panel.getByLabel("Additional instructions (optional)").fill(instructions);
    let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs"))posts++;});
    const failure=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/pm-runs"));
    await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).evaluate((button:HTMLButtonElement)=>{button.click();button.click();});
    const response=await failure;expect(response.status()).toBe(scenario.status);
    const failed=(await response.json()).error;expect(failed.code).toBe(scenario.category);
    await expect(panel.getByRole("alert")).toContainText(scenario.message);
    await expect(panel.getByRole("button",{name:"Retry generation",exact:true})).toBeEnabled();
    await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
    await expect(panel.getByLabel("Additional instructions (optional)")).toHaveValue(instructions);
    await expect(panel.getByTestId("plan-state")).toHaveText("approved");expect(posts).toBe(1);
    const history=(await (await page.request.get(`/api/v1/projects/${project.id}/pm-runs`)).json()).items;
    expect(history).toHaveLength(1);expect(history[0].status).toBe("failed");expect(history[0].plan_id).toBeNull();
    const database=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.inspect_pm_run","--run",failed.run_id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
    expect(database.status).toBe("failed");expect(database.project_plans).toHaveLength(1);
    expect(database.project_plans[0].id).toBe(fixture.plan_id);expect(database.project_plans[0].state).toBe("approved");
    if(scenario.upstream!==null)expect(database.diagnostic.provider_http_status).toBe(scenario.upstream);
    else expect(database.diagnostic.exception_type).toBe("ValidationError");
    const after=await (await page.request.get(path)).json();
    for(const key of ["content_hash","approved_by","approved_at","revision","version"])expect(after[key]).toEqual(before[key]);
    await page.reload();await panel.getByRole("button",{name:"Check status",exact:true}).click();
    await expect(panel.getByRole("alert")).toContainText("No draft was created by this run");
    await panel.getByRole("button",{name:"Restore submitted brief",exact:true}).click();
    await panel.getByText("Generate another product plan",{exact:true}).click();
    await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
    await expect(panel.getByLabel("Additional instructions (optional)")).toHaveValue(instructions);
    await expect(panel.getByTestId("plan-state")).toHaveText("approved");expect(posts).toBe(1);
    writeFileSync(evidencePath(`controlled-${scenario.category}-${test.info().project.name}.json`),JSON.stringify({execution_class:"controlled_provider_double",provider_double:true,posts,database,preservation:{content_hash:after.content_hash,approved_by:after.approved_by,approved_at:after.approved_at}},null,2));
  });
}

test("live-test allowance aborts a simultaneous second controlled generation before dispatch",async({page})=>{
  const {project}=await setup(page);
  const budget=await allowOneGeneration(page);
  const outcomes=await page.evaluate(async projectId=>{
    const {csrf_token}=await (await fetch("/api/v1/auth/csrf")).json();
    const send=()=>fetch(`/api/v1/projects/${projectId}/pm-runs`,{method:"POST",headers:{"Content-Type":"application/json","X-CSRF-Token":csrf_token},body:JSON.stringify({client_request_id:crypto.randomUUID(),brief:"Controlled allowance test only"})}).then(r=>r.status).catch(()=>"blocked");
    return Promise.all([send(),send()]);
  },project.id);
  expect(outcomes).toContain(504);expect(outcomes).toContain("blocked");
  expect(budget).toEqual({attempted:2,forwarded:1,blocked:1});
  const runs=(await (await page.request.get(`/api/v1/projects/${project.id}/pm-runs`)).json()).items;
  expect(runs).toHaveLength(1);expect(runs[0].status).toBe("failed");expect(runs[0].plan_id).toBeNull();
  writeFileSync(evidencePath(`controlled-live-budget-${test.info().project.name}.json`),JSON.stringify({execution_class:"controlled_provider_double",provider_double:true,budget,run_id:runs[0].id,status:runs[0].status},null,2));
});

test("controlled timeout preserves approval and brief; explicit retry records a fresh failed attempt",async({page})=>{
  const {project,user,panel}=await setup(page);
  const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  await page.reload();await panel.getByRole("button",{name:"Approve plan",exact:true}).click();
  await panel.getByRole("button",{name:"Confirm approval",exact:true}).click();
  await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  const before=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  await panel.getByText("Generate another product plan",{exact:true}).click();
  const brief="Keep my original product brief during a controlled timeout.";
  await panel.getByLabel("Product brief",{exact:true}).fill(brief);
  await panel.getByLabel("Additional instructions (optional)").fill("Keep these instructions too.");
  let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs"))posts++;});
  const failure=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/pm-runs"));
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  const response=await failure;expect(response.status()).toBe(504);const first=(await response.json()).error;
  await expect(panel.getByRole("alert")).toContainText("AI provider timed out");
  await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
  await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  await expect(panel.getByRole("button",{name:"Retry generation",exact:true})).toBeEnabled();
  expect(posts).toBe(1);
  await page.reload();await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByRole("alert")).toContainText("No draft was created");
  await panel.getByRole("button",{name:"Restore submitted brief",exact:true}).click();
  await panel.getByText("Generate another product plan",{exact:true}).click();
  await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
  await expect(panel.getByLabel("Additional instructions (optional)")).toHaveValue("Keep these instructions too.");
  expect(posts).toBe(1);
  const retry=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/pm-runs"));
  await panel.getByRole("button",{name:"Retry generation",exact:true}).click();
  const second=(await (await retry).json()).error;expect(second.run_id).not.toBe(first.run_id);
  await expect(panel.getByRole("button",{name:"Retry generation",exact:true})).toBeEnabled();
  const runs=(await (await page.request.get(`/api/v1/projects/${project.id}/pm-runs`)).json()).items;
  expect(runs).toHaveLength(2);expect(runs.every((r:{status:string;plan_id:null})=>r.status==="failed"&&r.plan_id===null)).toBe(true);
  expect(new Set(runs.map((r:{client_request_id:string})=>r.client_request_id)).size).toBe(2);expect(posts).toBe(2);
  const after=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  expect(after.content_hash).toBe(before.content_hash);expect(after.approved_at).toBe(before.approved_at);
  const database=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.inspect_pm_run","--run",second.run_id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  expect(database.status).toBe("failed");expect(database.diagnostic.provider_double).toBe(true);expect(database.project_plans).toHaveLength(1);
  writeFileSync(evidencePath(`controlled-timeout-${test.info().project.name}.json`),JSON.stringify({execution_class:"controlled_provider_double",provider_double:true,posts,database},null,2));
  await page.getByRole("button",{name:"Toggle color theme"}).click();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test("lost HTTP response stays unknown and GET-only until the exact failed run is confirmed",async({page})=>{
  const {project,panel}=await setup(page);
  const brief="Preserve this brief after an injected response loss.";
  await panel.getByLabel("Product brief",{exact:true}).fill(brief);
  let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs"))posts++;});
  // Execute the real request against the controlled API, then lose its HTTP response.
  await page.route("**/pm-runs",async route=>{await route.fetch();await route.abort("failed");});
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  await expect(panel.getByRole("alert")).toContainText("outcome is unconfirmed");
  await expect(panel.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeDisabled();
  await expect(panel.getByRole("button",{name:"Retry generation",exact:true})).toHaveCount(0);
  await expect(panel.getByRole("button",{name:"Clear request reference",exact:true})).toHaveCount(0);
  await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
  expect(posts).toBe(1);await page.unroute("**/pm-runs");
  // Explicit transport failure for a recovery GET cannot unlock a POST either.
  await page.route("**/pm-runs?**",route=>route.abort("failed"));
  await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeDisabled();
  expect(posts).toBe(1);await page.unroute("**/pm-runs?**");
  await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByRole("alert")).toContainText("AI provider timed out");
  await expect(panel.getByRole("button",{name:"Retry generation",exact:true})).toBeEnabled();expect(posts).toBe(1);
  const runs=(await (await page.request.get(`/api/v1/projects/${project.id}/pm-runs`)).json()).items;
  expect(runs).toHaveLength(1);expect(runs[0].status).toBe("failed");expect(runs[0].plan_id).toBeNull();
});

test("controlled success retains recovery UUID when the saved-result read fails",async({page})=>{
  const {project,panel}=await setup(page);
  await panel.getByLabel("Additional instructions (optional)").fill("Controlled provider DOUBLE: valid response");
  let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs"))posts++;});
  // A genuine controlled API success is followed by a deliberately lost GET.
  const generation=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/pm-runs"));
  await page.route("**/pm-plans?**",route=>route.abort("failed"));
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  const run=await (await generation).json();expect(run.status).toBe("succeeded");
  await expect(panel.getByRole("alert")).toBeVisible();
  await expect(panel.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeDisabled();
  const key=await page.evaluate(()=>Object.keys(sessionStorage).find(k=>k.startsWith("orba-pm-request:")&&!k.endsWith(":copy")));
  expect(key).toBeTruthy();expect(await page.evaluate(k=>sessionStorage.getItem(k!),key)).toBe(run.client_request_id);
  await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByRole("alert")).toBeVisible();expect(await page.evaluate(k=>sessionStorage.getItem(k!),key)).toBe(run.client_request_id);
  await page.unroute("**/pm-plans?**");await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByTestId("plan-state")).toHaveText("draft");
  expect(await page.evaluate(k=>sessionStorage.getItem(k!),key)).toBeNull();expect(posts).toBe(1);
  const plans=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans`)).json();
  expect(plans.items).toHaveLength(1);expect(plans.items[0].id).toBe(run.plan_id);
});

test("failed initial history read is unavailable; non-dispatch rejection preserves input without inventing a run",async({page})=>{
  const {project,panel}=await setup(page);
  await page.route("**/pm-plans?**",route=>route.abort("failed"));await page.reload();
  await expect(panel.getByRole("alert")).toBeVisible();
  await expect(panel.getByRole("heading",{name:"Your requirements start here"})).toHaveCount(0);
  await expect(panel.getByRole("heading",{name:"Configure the Product Manager"})).toHaveCount(0);
  await expect(panel.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeDisabled();
  await page.unroute("**/pm-plans?**");await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeEnabled();
  await expect(panel.locator(".pm-information")).toContainText("Status refreshed");
  const brief="Keep my brief when CSRF preparation is unavailable.";
  await panel.getByLabel("Product brief",{exact:true}).fill(brief);
  let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs"))posts++;});
  await page.route("**/api/v1/auth/csrf",route=>route.abort("failed"));
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  await expect(panel.getByRole("alert")).toContainText("No generation request was sent");
  await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
  await expect(panel.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeEnabled();expect(posts).toBe(0);
  await page.unroute("**/api/v1/auth/csrf");
  const runs=await (await page.request.get(`/api/v1/projects/${project.id}/pm-runs`)).json();expect(runs.items).toHaveLength(0);
});

test("status recovery never advances the revision beneath an open unchanged editor",async({page})=>{
  const {project,user,panel}=await setup(page);
  const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  await page.reload();await panel.getByRole("button",{name:"Edit draft",exact:true}).click();
  const url=`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`;
  const other=await (await page.request.get(url)).json();
  const summary="Another member saved this summary while the first editor was open.";
  other.document.summary.text=summary;
  const csrf=await (await page.request.get("/api/v1/auth/csrf")).json();
  const saved=await page.request.put(url,{headers:{Origin:"http://localhost:3001","X-CSRF-Token":csrf.csrf_token},data:{expected_revision:1,document:other.document}});
  expect(saved.status()).toBe(200);
  await panel.getByRole("button",{name:"Check status",exact:true}).click();
  const criterion="Keep this local criterion until the revision conflict is resolved.";
  await panel.getByLabel("Then (criterion_checkin)",{exact:true}).fill(criterion);
  const saving=page.waitForResponse(r=>r.request().method()==="PUT"&&r.url().endsWith(`/pm-plans/${fixture.plan_id}`));
  await panel.getByRole("button",{name:"Save draft",exact:true}).click();
  const response=await saving;
  const persisted=await (await page.request.get(url)).json();
  expect(persisted.document.summary.text).toBe(summary);
  expect(response.status()).toBe(409);
  expect(persisted.revision).toBe(2);
  await expect(panel.getByLabel("Then (criterion_checkin)",{exact:true})).toHaveValue(criterion);
  await expect(panel.getByRole("heading",{name:"Latest saved revision 2",exact:true})).toBeVisible();
  writeFileSync(evidencePath(`editor-revision-${test.info().project.name}.json`),JSON.stringify({
    scenario:"Real authenticated API/PostgreSQL competing human draft edits; no model call",
    plan_id:fixture.plan_id,save_http_status:response.status(),persisted_revision:persisted.revision,
    competing_summary_preserved:persisted.document.summary.text===summary,
    local_unsaved_criterion_preserved:true,model_call:false,
  },null,2));
});

test("known active-project rejection creates no run and never strands a request reference",async({page})=>{
  const {project,user,panel}=await setup(page);
  const brief="Keep this brief when another request wins project admission.";
  await panel.getByLabel("Product brief",{exact:true}).fill(brief);
  const url=`/api/v1/projects/${project.id}/pm-runs`;
  const csrf=await (await page.request.get("/api/v1/auth/csrf")).json();
  const firstId=crypto.randomUUID();
  const first=page.request.post(url,{headers:{Origin:"http://localhost:3001","X-CSRF-Token":csrf.csrf_token},data:{client_request_id:firstId,brief:"Hold a controlled planning request",instructions:"Controlled provider DOUBLE: hold admission"}});
  await expect.poll(async()=>{
    const result=await (await page.request.get(`${url}?client_request_id=${firstId}`)).json();
    return result.items[0]?.status;
  },{timeout:5000,intervals:[50,100,200]}).toBe("running");
  let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs"))posts++;});
  const rejected=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/pm-runs"));
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  const rejection=await rejected;expect(rejection.status()).toBe(409);
  expect((await rejection.json()).error.code).toBe("project_generation_active");
  expect((await first).status()).toBe(504);
  await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeEnabled();
  await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
  expect(await page.evaluate(key=>sessionStorage.getItem(key),`orba-pm-request:${user.id}:${project.id}`)).toBeNull();
  expect(posts).toBe(1);
  const runs=await (await page.request.get(url)).json();expect(runs.items).toHaveLength(1);
  expect(runs.items[0].client_request_id).toBe(firstId);expect(runs.items[0].status).toBe("failed");
});

test("combined UTF8 input rejection retains context brief and approved plan before explicit recovery",async({page})=>{
  const {project,user,panel}=await setup(page);
  const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  await page.reload();await panel.getByRole("button",{name:"Approve plan",exact:true}).click();
  await panel.getByRole("button",{name:"Confirm approval",exact:true}).click();
  await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  const path=`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`;
  const before=await (await page.request.get(path)).json();
  await panel.getByText("Generate another product plan",{exact:true}).click();
  const brief="界".repeat(10000),instructions="字".repeat(4000);
  await panel.getByLabel("Product brief",{exact:true}).fill(brief);
  await panel.getByLabel("Additional instructions (optional)").fill(instructions);
  const context=panel.getByRole("checkbox");await context.check();
  let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/pm-runs"))posts++;});
  const rejection=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/pm-runs"));
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  const rejected=await rejection;expect(rejected.status()).toBe(422);
  const error=(await rejected.json()).error;expect(error.code).toBe("input_too_large");expect(error.run_id).toBeNull();
  await expect(panel.getByRole("alert")).toContainText("No generation was started");
  await expect(panel.getByRole("alert")).toContainText("Shorten");
  await expect(panel.getByLabel("Product brief",{exact:true})).toHaveValue(brief);
  await expect(panel.getByLabel("Additional instructions (optional)")).toHaveValue(instructions);
  await expect(context).toBeChecked();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  expect((await (await page.request.get(`/api/v1/projects/${project.id}/pm-runs`)).json()).items).toHaveLength(0);
  expect(await page.evaluate(key=>sessionStorage.getItem(key),`orba-pm-request:${user.id}:${project.id}`)).toBeNull();
  expect(await (await page.request.get(path)).json()).toEqual(before);expect(posts).toBe(1);
  // Only this deliberate corrected submission reaches the labeled timeout double.
  await panel.getByLabel("Product brief",{exact:true}).fill("Track one habit; retain the original approved plan.");
  await panel.getByLabel("Additional instructions (optional)").fill("Controlled provider DOUBLE: timeout");
  const retry=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/pm-runs"));
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  expect((await retry).status()).toBe(504);await expect(panel.getByRole("button",{name:"Retry generation",exact:true})).toBeEnabled();
  expect(posts).toBe(2);expect(await (await page.request.get(path)).json()).toEqual(before);
  writeFileSync(evidencePath(`input-byte-recovery-${test.info().project.name}.json`),JSON.stringify({execution_class:"controlled_provider_double",provider_double:true,rejection_http:422,rejected_run_id:error.run_id,retained_brief:true,retained_instructions:true,retained_context:true,approved_hash:before.content_hash,corrected_http:504,posts},null,2));
});
