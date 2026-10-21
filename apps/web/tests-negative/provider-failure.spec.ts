/** A REAL official SDK request with an intentionally invalid test credential.
 * No owner credential is changed, no response is intercepted, no model success is claimed. */
import {test,expect} from "@playwright/test";
import {execFileSync} from "node:child_process";
import {writeFileSync} from "node:fs";
import {evidencePath} from "../tests/evidence";
import {signup,createWorkspace} from "../tests/helpers";

test("provider rejection is a saved failure, preserves approval, and appears in the UI",async({page})=>{
  execFileSync("uv",["run","--directory","../api","python","-m","scripts.prepare_tests"],{stdio:"pipe"});
  await signup(page,`negative-provider-${Date.now()}@example.com`);await createWorkspace(page,"Provider failure verification");
  await page.getByLabel("Project description",{exact:true}).fill("A small habit journal with daily check-ins.");
  const creation=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/api/v1/projects"));
  await page.getByRole("button",{name:"Create project",exact:true}).click();const project=await (await creation).json();
  const user=await (await page.request.get("/api/v1/auth/me")).json();
  const fixture=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.seed_pm_fixture","--project",project.id,"--actor",user.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  await page.reload();await page.getByRole("button",{name:"Approve plan",exact:true}).click();await page.getByRole("button",{name:"Confirm approval",exact:true}).click();
  await expect(page.getByTestId("plan-state")).toHaveText("approved");
  const before=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  const panel=page.locator("#product-plan");
  await panel.getByText("Generate another product plan",{exact:true}).click();
  const responsePromise=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/pm-runs"));
  await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();
  const response=await responsePromise;expect(response.status()).toBeGreaterThanOrEqual(400);
  const error=(await response.json()).error;expect(error.run_id).toBeTruthy();
  await expect(panel.getByRole("alert")).toContainText("provider");
  await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  const run=await (await page.request.get(`/api/v1/projects/${project.id}/pm-runs/${error.run_id}`)).json();
  expect(run.status).toBe("failed");expect(run.plan_id).toBeNull();expect(run.diagnostic_id).toBeTruthy();
  const after=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${fixture.plan_id}`)).json();
  expect(after.content_hash).toBe(before.content_hash);expect(after.approved_at).toBe(before.approved_at);
  const plans=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans`)).json();expect(plans.items).toHaveLength(1);
  await page.reload();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  await panel.getByRole("button",{name:"Check status",exact:true}).click();
  await expect(panel.getByRole("alert")).toContainText("No draft was created");
  const database=JSON.parse(execFileSync("uv",["run","--directory","../api","python","-m","scripts.inspect_pm_run","--run",run.id],{encoding:"utf8",stdio:["ignore","pipe","pipe"]}));
  expect(database.status).toBe("failed");expect(database.project_plans).toHaveLength(1);expect(database.project_plans[0].state).toBe("approved");expect(database.project_plans[0].content_hash).toBe(before.content_hash);
  writeFileSync(evidencePath("external-provider-failure.json"),JSON.stringify({scenario:"Actual SDK call with intentionally invalid test key",http_status:response.status(),run_id:run.id,status:run.status,error_category:run.error_category,diagnostic_id:run.diagnostic_id,plan_id:run.plan_id,previous_approved_hash:after.content_hash,previous_approval_unchanged:true,mocks:false,database},null,2)+"\n");
});
