import { evidencePath } from "./evidence";
/** Real UI/API/PostgreSQL. Plans seeded below are explicitly HUMAN-AUTHORED,
 * and are never presented as live model verification. No HTTP interceptions. */
import { test, expect, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { createWorkspace, signup, signout } from "./helpers";

test.beforeAll(()=>{execFileSync("uv",["run","--directory","../api","python","-m","scripts.prepare_tests"],{stdio:"pipe"});});
async function setup(page:Page) {
  await signup(page,`pm-${test.info().project.name}-${Date.now()}@example.com`);
  await createWorkspace(page,"Product planning");
  await page.getByLabel("Project description",{exact:true}).fill("A personal habit journal with daily check-ins.");
  const save=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/api/v1/projects"));
  await page.getByRole("button",{name:"Create project",exact:true}).click();
  const project=await (await save).json();
  await expect(page.getByRole("heading",{name:"Product Plan",exact:true})).toBeVisible();
  const user=await (await page.request.get("/api/v1/auth/me")).json();
  return {project,user};
}

test("provider setup and empty state are honest; visiting a project makes no model request",async({page})=>{
  let posts=0;page.on("request",r=>{if(r.method()==="POST" && r.url().endsWith("/pm-runs"))posts++;});
  await setup(page);
  await expect(page.getByRole("heading",{name:"Configure the Product Manager"})).toBeVisible();
  await expect(page.getByRole("heading",{name:"Your requirements start here"})).toBeVisible();
  await expect(page.getByRole("button",{name:"Generate Product Plan",exact:true})).toBeDisabled();
  await page.reload();
  await expect(page.getByRole("heading",{name:"Product Plan",exact:true})).toBeVisible();
  expect(posts).toBe(0);
});

test("human-authored fixture: edit criterion, persist, approve exact version, history and isolation",async({page,browser})=>{
  // Two accounts, repeated reloads, editing, approval and version history need a
  // bounded journey budget; retain every assertion and the per-expect deadlines.
  test.setTimeout(90000);
  const {project,user}=await setup(page);
  const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id,"--blocking-confirmation"],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  expect(fixture.origin).toBe("human_authored");expect(fixture.model_call).toBe(false);
  await page.reload();
  const panel=page.locator("#product-plan");
  await expect(panel.getByTestId("plan-state")).toHaveText("draft");
  await expect(panel.getByRole("heading",{name:"Daily journal",exact:true})).toBeVisible();
  await panel.getByRole("button",{name:"Edit draft",exact:true}).click();
  const criterion="The check-in stays complete after reloading the journal.";
  await panel.getByLabel("Then (criterion_checkin)",{exact:true}).fill(criterion);
  await panel.getByRole("combobox",{name:"Disposition (confirmation_platform)",exact:true}).selectOption("deferred");
  await panel.getByLabel("Disposition reason (confirmation_platform)",{exact:true}).fill("The test owner defers the platform decision until architecture review.");
  const saveResponse=page.waitForResponse(r=>r.request().method()==="PUT" && r.url().endsWith(`/pm-plans/${fixture.plan_id}`));
  await panel.getByRole("button",{name:"Save draft",exact:true}).click();
  expect((await saveResponse).status()).toBe(200);
  await expect(panel.getByRole("form",{name:"Edit product plan",exact:true})).toHaveCount(0);
  await expect(panel.getByRole("status")).toContainText("revision 2 saved");
  await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
  await page.reload();
  await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
  const saved=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  expect(saved.revision).toBe(2);expect(saved.document.epics[0].stories[0].acceptance_criteria[0].then).toBe(criterion);
  expect(saved.document.confirmations[0].disposition).toBe("deferred");expect(saved.document.confirmations[0].actor_id).toBe(user.id);expect(saved.document.confirmations[0].decided_at).toBeTruthy();
  await panel.getByRole("button",{name:"Approve plan",exact:true}).click();
  await expect(panel.getByRole("heading",{name:"Approve version 1, revision 2?",exact:true})).toBeVisible();
  await panel.getByRole("button",{name:"Confirm approval",exact:true}).click();
  await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  await page.reload();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  await expect(panel.getByRole("button",{name:"Edit draft",exact:true})).toHaveCount(0);
  const approved=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  expect(approved.approved_by).toBe(user.id);expect(approved.approved_at).toBeTruthy();
  await panel.getByRole("button",{name:"Create draft copy",exact:true}).click();
  await expect(panel.getByTestId("plan-state")).toHaveText("draft");
  await expect(panel.getByLabel("Plan version",{exact:true})).toContainText("Version 2");
  await panel.getByLabel("Plan version",{exact:true}).selectOption(fixture.plan_id);
  await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  await page.getByRole("button",{name:"Toggle color theme"}).click();
  await expect(panel.getByRole("heading",{name:"Daily journal",exact:true})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:evidencePath(`${test.info().project.name}-human-plan.png`),fullPage:true});
  const other=await browser.newContext();const outsider=await other.newPage();
  await signup(outsider,`pm-outsider-${Date.now()}@example.com`);await createWorkspace(outsider,"Unrelated private space");
  const denied=await outsider.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`);
  expect(denied.status()).toBe(404);expect(await denied.text()).not.toContain(criterion);
  await outsider.goto(`/projects/${project.id}`);
  await expect(outsider.getByRole("main").getByRole("alert")).toHaveText("Project not found.");
  await expect(outsider.getByText(criterion,{exact:false})).toHaveCount(0);
  await other.close();
  await signout(page);await page.goto(`/projects/${project.id}`);
  await expect(page.getByRole("heading",{name:"Sign in to your workspace"})).toBeVisible();
  await expect(page.getByText(criterion,{exact:false})).toHaveCount(0);
});

test("a save conflict preserves local edits for comparison",async({page})=>{
  const {project,user}=await setup(page);
  const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  await page.reload();await page.getByRole("button",{name:"Edit draft",exact:true}).click();
  const field=page.getByLabel("Then (criterion_checkin)",{exact:true});
  await field.fill("My preserved local criterion");
  const original=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  original.document.summary.text="A competing editor saved this first.";
  const csrf=await (await page.request.get("/api/v1/auth/csrf")).json();
  const other=await page.request.put(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`,{headers:{Origin:"http://localhost:3001","X-CSRF-Token":csrf.csrf_token},data:{expected_revision:1,document:original.document}});
  expect(other.status()).toBe(200);
  await page.getByRole("button",{name:"Save draft",exact:true}).click();
  await expect(page.locator("#product-plan").getByRole("alert")).toContainText("exact saved draft revision");
  await expect(field).toHaveValue("My preserved local criterion");
  await page.getByRole("button",{name:"Inspect latest saved revision",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Latest saved revision 2"})).toBeVisible();
  await expect(field).toHaveValue("My preserved local criterion");
});
