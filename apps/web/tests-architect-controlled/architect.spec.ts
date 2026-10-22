/** REAL auth/API/PG/browser. ONLY the model dependency is a controlled DOUBLE. */
import {test,expect,type Page} from "@playwright/test";
import {execFileSync} from "node:child_process";
import {writeFileSync} from "node:fs";
import {signup,createWorkspace,signout} from "../tests/helpers";
import {evidencePath} from "../tests/evidence";

const command=(...args:string[])=>execFileSync("uv",["run","--directory","../api","python","-m",...args],{encoding:"utf8",stdio:["ignore","pipe","pipe"]});
async function setup(page:Page,approve=true){
  command("scripts.prepare_tests");
  await signup(page,`architect-${Date.now()}-${test.info().project.name}@example.com`);
  await createWorkspace(page,"Architect controlled verification");
  await page.getByLabel("Project description",{exact:true}).fill("Track one daily habit.");
  const creating=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/api/v1/projects"));
  await page.getByRole("button",{name:"Create project",exact:true}).click();
  const project=await(await creating).json();
  const user=await(await page.request.get("/api/v1/auth/me")).json();
  const source=JSON.parse(command("scripts.seed_pm_fixture","--project",project.id,"--actor",user.id));
  await page.reload();
  if(approve){await page.getByRole("button",{name:"Approve plan",exact:true}).click();await page.getByRole("button",{name:"Confirm approval",exact:true}).click();await expect(page.getByTestId("plan-state")).toHaveText("approved");}
  await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
  const panel=page.getByRole("region",{name:"Architecture workspace"});
  await expect(panel.getByRole("heading",{name:"No architecture yet"})).toBeVisible();
  return {project,user,source,panel};
}
async function generate(page:Page){
  const response=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/architect-runs"));
  await page.getByRole("button",{name:"Generate Architecture",exact:true}).click();
  const result=await response;expect(result.status()).toBe(201);return result.json();
}

test("draft PRD is not an approved source; no generation is dispatched",async({page})=>{
  const {panel}=await setup(page,false);let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/architect-runs"))posts++;});
  await expect(panel.getByText("Approve a Product Plan before requesting architecture.",{exact:false})).toBeVisible();
  await expect(panel.getByRole("button",{name:"Generate Architecture",exact:true})).toBeDisabled();expect(posts).toBe(0);
});

test("controlled architecture persists, graph rejects a cycle, human edit and approval survive reload",async({page})=>{
  const {project,panel}=await setup(page);const run=await generate(page);
  await expect(panel.getByTestId("architecture-state")).toHaveText("draft");
  await panel.getByRole("button",{name:"Edit architecture draft",exact:true}).click();
  await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Task Graph",exact:true}).click();
  const graph=page.getByRole("region",{name:"Task Graph workspace"});
  await expect(graph.getByRole("img",{name:"Saved validated dependency graph"})).toBeVisible();
  await graph.getByLabel("Add prerequisite for Persist daily check-ins").selectOption("screen");
  await graph.getByRole("button",{name:"Add dependency",exact:true}).click();
  const invalid=page.waitForResponse(r=>r.request().method()==="PUT"&&r.url().includes("/architectures/"));
  await graph.getByRole("button",{name:"Save architecture draft",exact:true}).click();expect((await invalid).status()).toBe(422);
  await expect(graph.getByRole("alert")).toContainText("cycle");
  const saved=await(await page.request.get(`/api/v1/projects/${project.id}/architectures/${run.architecture_id}`)).json();
  expect(saved.revision).toBe(1);expect(saved.graph.valid).toBe(true);
  await graph.getByRole("button",{name:"Remove prerequisite screen",exact:true}).click();
  await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
  await panel.locator(".architect-editor > details").filter({has:page.locator("summary",{hasText:/^Tasks$/})}).locator(":scope > summary").click();
  const criteria=panel.getByLabel("Persist daily check-ins · Acceptance criteria",{exact:true});
  await criteria.fill("Given a saved check-in, when the page reloads, then my human-edited criterion remains visible.");
  await panel.getByRole("button",{name:"Save architecture draft",exact:true}).click();await expect(panel.getByRole("status")).toContainText("Human edits saved");
  await page.reload();await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
  await expect(panel.getByText("Given a saved check-in, when the page reloads, then my human-edited criterion remains visible.",{exact:true})).toBeAttached();
  await panel.getByRole("button",{name:"Review architecture approval",exact:true}).click();await panel.getByRole("button",{name:"Confirm architecture approval",exact:true}).click();
  await expect(panel.getByTestId("architecture-state")).toHaveText("approved");
  await page.reload();await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Task Graph",exact:true}).click();
  await expect(page.getByTestId("architecture-state")).toHaveText("approved");
  const database=JSON.parse(command("scripts.inspect_architect_run","--run",run.id));
  expect(database.architecture_validated).toBe(true);expect(database.graph_valid).toBe(true);expect(database.coverage_approvable).toBe(true);
  expect(database.counts.engineering_tasks).toBe(2);expect(database.state).toBe("approved");expect(database.revision).toBe(2);expect(database.approved_by).toBeTruthy();
  expect(database.execution_performed).toBe(false);
  writeFileSync(evidencePath(`architect-controlled-success-${test.info().project.name}.json`),JSON.stringify({execution_class:"controlled_provider_double",provider_double:true,database},null,2));
  await page.getByRole("button",{name:"Toggle color theme"}).click();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:evidencePath(`architect-graph-${test.info().project.name}.png`),fullPage:true});
});

for(const scenario of [{mode:"timeout",status:504,message:"AI provider timed out"},{mode:"unavailable",status:502,message:"temporarily unavailable"},{mode:"invalid",status:502,message:"failed schema"},{mode:"cycle",status:502,message:"failed schema"},{mode:"rate limited",status:429,message:"rate limit"}]){
  test(`controlled ${scenario.mode} preserves prior approval and permits only explicit recovery`,async({page})=>{
    const {project,panel}=await setup(page);const prior=await generate(page);
    await panel.getByRole("button",{name:"Review architecture approval",exact:true}).click();await panel.getByRole("button",{name:"Confirm architecture approval",exact:true}).click();
    await expect(panel.getByTestId("architecture-state")).toHaveText("approved");
    const before=await(await page.request.get(`/api/v1/projects/${project.id}/architectures/${prior.architecture_id}`)).json();
    await panel.getByLabel("Optional architectural constraints").fill(`Controlled provider DOUBLE: ${scenario.mode}`);
    let posts=0;page.on("request",r=>{if(r.method()==="POST"&&r.url().endsWith("/architect-runs"))posts++;});
    const failing=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/architect-runs"));
    await panel.getByRole("button",{name:"Generate Architecture",exact:true}).evaluate((button:HTMLButtonElement)=>{button.click();button.click();});
    const response=await failing;expect(response.status()).toBe(scenario.status);
    const failure=(await response.json()).error;
    await expect(panel.getByRole("alert")).toContainText(scenario.message);
    await expect(panel.getByRole("button",{name:"Retry architecture generation",exact:true})).toBeEnabled();
    await expect(panel.getByLabel("Optional architectural constraints")).toHaveValue(`Controlled provider DOUBLE: ${scenario.mode}`);expect(posts).toBe(1);
    const after=await(await page.request.get(`/api/v1/projects/${project.id}/architectures/${prior.architecture_id}`)).json();
    expect(after.content_hash).toBe(before.content_hash);expect(after.approved_at).toBe(before.approved_at);
    const database=JSON.parse(command("scripts.inspect_architect_run","--run",failure.run_id));
    expect(database.status).toBe("failed");expect(database.architecture_id).toBeNull();expect(database.project_architectures).toHaveLength(1);
    await page.reload();await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
    await panel.getByRole("button",{name:"Check architecture status",exact:true}).click();
    await expect(panel.getByRole("alert")).toContainText("No new architecture");
    await panel.getByRole("button",{name:"Restore submitted constraints",exact:true}).click();
    await expect(panel.getByLabel("Optional architectural constraints")).toHaveValue(`Controlled provider DOUBLE: ${scenario.mode}`);
    expect(posts).toBe(1);
    writeFileSync(evidencePath(`architect-controlled-${scenario.mode.replaceAll(" ","-")}-${test.info().project.name}.json`),JSON.stringify({execution_class:"controlled_provider_double",provider_double:true,posts,database},null,2));
  });
}

test("unrelated user cannot see architecture or run content",async({page})=>{
  const {project}=await setup(page);const run=await generate(page);await signout(page);
  await signup(page,`outsider-${Date.now()}@example.com`);await createWorkspace(page,"Unrelated workspace");
  await page.goto(`/projects/${project.id}`);await expect(page.getByRole("main").getByRole("alert")).toContainText("Project not found");
  for(const suffix of [`architectures/${run.architecture_id}`,`architect-runs/${run.id}`,`architectures/${run.architecture_id}/graph`]){const response=await page.request.get(`/api/v1/projects/${project.id}/${suffix}`);expect(response.status()).toBe(404);expect(await response.text()).not.toContain("Habit journal — controlled test proposal");}
  const database=JSON.parse(command("scripts.inspect_architect_run","--run",run.id));expect(database.status).toBe("succeeded");expect(database.counts.engineering_tasks).toBe(2);
});

test("viewer can inspect saved architecture but cannot generate, edit or approve",async({page})=>{
  const {project}=await setup(page);const run=await generate(page);
  const email=`viewer-${Date.now()}@example.com`;
  const {csrf_token}=await(await page.request.get("/api/v1/auth/csrf")).json();
  const invited=await page.request.post(`/api/v1/workspaces/${project.workspace_id}/invitations`,{headers:{Origin:"http://localhost:3001","X-CSRF-Token":csrf_token},data:{email,role:"viewer"}});
  expect(invited.status()).toBe(201);const invitation=await invited.json();
  await signout(page);await signup(page,email);await page.goto(invitation.invitation_link);const accepting=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/invitations/accept"));await page.getByRole("button",{name:"Accept invitation",exact:true}).click();expect((await accepting).status()).toBe(200);await expect(page).toHaveURL(/\/projects$/);
  await page.goto(`/projects/${project.id}`);await page.getByRole("navigation",{name:"Project planning views"}).getByRole("button",{name:"Architecture",exact:true}).click();
  const panel=page.getByRole("region",{name:"Architecture workspace"});await expect(panel.getByText("Viewer access:",{exact:false})).toBeVisible();
  await expect(panel.getByRole("button",{name:"Edit architecture draft",exact:true})).toHaveCount(0);await expect(panel.getByRole("button",{name:"Generate Architecture",exact:true})).toHaveCount(0);
  const csrf=(await(await page.request.get("/api/v1/auth/csrf")).json()).csrf_token;
  const denied=await page.request.post(`/api/v1/projects/${project.id}/architectures/${run.architecture_id}/approve`,{headers:{Origin:"http://localhost:3001","X-CSRF-Token":csrf},data:{version:1,expected_revision:1}});expect(denied.status()).toBe(403);
});

test("explicit retry creates a fresh auditable run and unsaved navigation preserves draft",async({page})=>{
  const {panel,project}=await setup(page);
  await panel.getByLabel("Optional architectural constraints").fill("Controlled provider DOUBLE: timeout");
  const failing=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/architect-runs"));await panel.getByRole("button",{name:"Generate Architecture",exact:true}).click();const failed=(await(await failing).json()).error;
  await expect(panel.getByRole("button",{name:"Retry architecture generation",exact:true})).toBeEnabled();await panel.getByLabel("Optional architectural constraints").fill("Explicit human retry after the previous terminal run");
  const succeeding=page.waitForResponse(r=>r.request().method()==="POST"&&r.url().endsWith("/architect-runs"));await panel.getByRole("button",{name:"Retry architecture generation",exact:true}).click();const run=await(await succeeding).json();expect(run.id).not.toBe(failed.run_id);expect(run.status).toBe("succeeded");
  await panel.getByRole("button",{name:"Edit architecture draft",exact:true}).click();await panel.getByLabel("Overview · Title",{exact:true}).fill("Unsaved human architecture title");
  await page.getByRole("link",{name:"All projects",exact:true}).click();const dialog=page.getByRole("dialog",{name:"Unsaved architecture changes"});await expect(dialog).toBeVisible();await dialog.getByRole("button",{name:"Cancel navigation",exact:true}).click();await expect(panel.getByLabel("Overview · Title",{exact:true})).toHaveValue("Unsaved human architecture title");
  await page.getByRole("link",{name:"All projects",exact:true}).click();await dialog.getByRole("button",{name:"Save and leave",exact:true}).click();await expect(page).toHaveURL(/\/projects$/);
  const saved=await(await page.request.get(`/api/v1/projects/${project.id}/architectures/${run.architecture_id}`)).json();expect(saved.document.overview.title).toBe("Unsaved human architecture title");
});

test("hidden architecture tab retains a visible navigation dialog and rejected graph edits",async({page})=>{
  const {project,panel}=await setup(page);const run=await generate(page);
  await panel.getByRole("button",{name:"Edit architecture draft",exact:true}).click();
  const views=page.getByRole("navigation",{name:"Project planning views"});
  await views.getByRole("button",{name:"Task Graph",exact:true}).click();
  const graph=page.getByRole("region",{name:"Task Graph workspace"});
  await graph.getByLabel("Add prerequisite for Persist daily check-ins").selectOption("screen");
  await graph.getByRole("button",{name:"Add dependency",exact:true}).click();
  await views.getByRole("button",{name:"Product Plan",exact:true}).click();
  await page.getByRole("link",{name:"All projects",exact:true}).click();
  const dialog=page.getByRole("dialog",{name:"Unsaved architecture changes"});
  await expect(dialog).toBeVisible();
  expect(await dialog.evaluate(element=>element.contains(document.activeElement))).toBe(true);
  const rejected=page.waitForResponse(r=>r.request().method()==="PUT"&&r.url().includes("/architectures/"));
  await dialog.getByRole("button",{name:"Save and leave",exact:true}).click();
  expect((await rejected).status()).toBe(422);
  await expect(dialog).toBeVisible();await expect(dialog.getByRole("alert")).toContainText("cycle");
  await expect(page).toHaveURL(new RegExp(`/projects/${project.id}$`));
  const saved=await(await page.request.get(`/api/v1/projects/${project.id}/architectures/${run.architecture_id}`)).json();
  expect(saved.revision).toBe(1);expect(saved.graph.valid).toBe(true);
  await dialog.getByRole("button",{name:"Cancel navigation",exact:true}).click();
  await views.getByRole("button",{name:"Task Graph",exact:true}).click();
  await expect(graph.getByRole("button",{name:"Remove prerequisite screen",exact:true})).toBeVisible();
  await graph.getByRole("button",{name:"Remove prerequisite screen",exact:true}).click();
  await graph.getByRole("button",{name:"Save architecture draft",exact:true}).click();
  await expect(graph.getByRole("status")).toContainText("Human edits saved");
});
