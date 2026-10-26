/** Real deterministic control-plane/browser tests. No provider or executor responses. */
import { test, expect } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { createRun, expectSavedRun, post, setupOrchestration, sqlRun, zeroGeneration } from "../tests/orchestration-setup";
import { jsonGet, reloadProject } from "../tests/architect-preflight";
import { createWorkspace, signup, signout } from "../tests/helpers";
import { evidencePath } from "../tests/evidence";
import type { RunDetail } from "../src/lib/orchestration";

test("approved source creates one persisted snapshot with roots, blockers, real events and reload", async ({ page, context }) => {
  const { project, architecture, boundary } = await setupOrchestration(page, context);
  let posts = 0;
  page.on("request", r => { if (r.method() === "POST" && new URL(r.url()).pathname === `/api/v1/projects/${project.id}/orchestration-runs`) posts++; });
  const run = await createRun(page, project.id, true);
  const panel = await expectSavedRun(page, project, run);
  const audit = sqlRun(run.id);
  expect(audit).toMatchObject({ run_id: run.id, architecture_id: architecture.id, status: "awaiting_executor", hash_valid: true, relational_snapshot_valid: true, execution_performed: false, counts: { tasks: 2, dependencies: 1, events: 2, traces: 3 } });
  expect(audit.snapshot_hash).toBe(run.snapshot_hash);
  expect(audit.generation_records).toEqual({ product_manager_runs: 0, architect_runs: 0 });
  const events = panel.getByRole("region", { name: "Orchestration event history" }).locator("li");
  await expect(events).toHaveCount(2); await expect(events.nth(0)).toContainText("#1 run created"); await expect(events.nth(1)).toContainText("#2 run awaiting executor");
  await reloadProject(page, project);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  await expectSavedRun(page, project, run);
  expect(await jsonGet<RunDetail>(page, `/api/v1/projects/${project.id}/orchestration-runs/${run.id}`)).toEqual(run);
  expect(posts).toBe(1);
  await panel.getByRole("button", { name: /Persist daily check-ins/ }).focus(); await page.keyboard.press("Enter");
  await expect(panel.getByTestId("task-blocker")).toContainText("Eligible for future dispatch");
  await page.getByRole("button", { name: "Toggle color theme" }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: evidencePath(`orchestration-${test.info().project.name}.png`), fullPage: true });
  const boundaryProof = await zeroGeneration(page, boundary.budget);
  writeFileSync(evidencePath(`orchestration-${test.info().project.name}.json`), JSON.stringify({ execution_class: "real_local_control_plane", audit, posts, boundary: boundaryProof }, null, 2));
});

test("unapproved architecture is rejected without run snapshots or false success", async ({ page, context }) => {
  const { project, architecture, execution, boundary } = await setupOrchestration(page, context, false);
  await expect(execution.getByRole("button", { name: "Create orchestration run", exact: true })).toBeDisabled();
  const response = await post(page, `/api/v1/projects/${project.id}/orchestration-runs`, { client_request_id: crypto.randomUUID(), architecture_id: architecture.id, architecture_version: 1, architecture_revision: 1 });
  expect(response.status()).toBe(409);
  const rows = await jsonGet<{ items: unknown[] }>(page, `/api/v1/projects/${project.id}/orchestration-runs`);
  expect(rows.items).toEqual([]);
  await zeroGeneration(page, boundary.budget);
});

test("unknown committed creation recovers by exact request ID without repeating POST", async ({ page, context }) => {
  const { project, execution, boundary } = await setupOrchestration(page, context);
  let posts = 0;
  await page.route(`**/api/v1/projects/${project.id}/orchestration-runs`, async route => {
    if (route.request().method() !== "POST") { await route.continue(); return; }
    posts++;
    const response = await route.fetch(); expect(response.status()).toBe(201);
    await route.abort("connectionfailed"); // Real server committed; response alone is lost.
  });
  await execution.getByRole("button", { name: "Create orchestration run", exact: true }).click();
  await expect(execution.getByRole("alert")).toContainText("unconfirmed");
  await expect(execution.getByRole("button", { name: "Create orchestration run", exact: true })).toBeDisabled();
  await execution.getByRole("button", { name: "Check creation status", exact: true }).click();
  await expect(execution.getByRole("status").filter({ hasText: "original saved run was recovered" })).toContainText("original saved run was recovered");
  expect(posts).toBe(1);
  const records = await jsonGet<{ items: RunDetail[] }>(page, `/api/v1/projects/${project.id}/orchestration-runs`);
  expect(records.items).toHaveLength(1);
  expect(sqlRun(records.items[0].id).counts).toMatchObject({ tasks: 2, dependencies: 1, events: 2 });
  await zeroGeneration(page, boundary.budget);
});

test("pre-dispatch connection failure requires explicit original-key retry", async ({ page, context }) => {
  const { project, execution, boundary } = await setupOrchestration(page, context);
  let posts = 0;
  const keys: string[] = [];
  await page.route(`**/api/v1/projects/${project.id}/orchestration-runs`, async route => {
    if (route.request().method() !== "POST") { await route.continue(); return; }
    posts++; keys.push(route.request().postDataJSON().client_request_id);
    if (posts === 1) await route.abort("connectionfailed"); else await route.continue();
  });
  await execution.getByRole("button", { name: "Create orchestration run", exact: true }).click();
  await expect(execution.getByRole("alert")).toContainText("unconfirmed");
  await execution.getByRole("button", { name: "Check creation status", exact: true }).click();
  await expect(execution.getByRole("button", { name: "Retry original creation", exact: true })).toBeEnabled();
  await execution.getByRole("button", { name: "Retry original creation", exact: true }).click();
  await expect(execution.getByTestId("orchestration-state")).toHaveText("awaiting executor");
  expect(posts).toBe(2); expect(keys[0]).toBe(keys[1]);
  const records = await jsonGet<{ items: RunDetail[] }>(page, `/api/v1/projects/${project.id}/orchestration-runs`);
  expect(records.items).toHaveLength(1);
  await zeroGeneration(page, boundary.budget);
});

test("cancellation requires confirmation and persists ordered events with no execution", async ({ page, context }) => {
  const { project, execution, boundary } = await setupOrchestration(page, context);
  const run = await createRun(page, project.id);
  await expectSavedRun(page, project, run);
  await execution.getByRole("button", { name: "Cancel orchestration run", exact: true }).click();
  const dialog = execution.getByRole("dialog", { name: "Confirm orchestration cancellation" });
  await expect(dialog.getByRole("button", { name: "Keep run", exact: true })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(execution.getByTestId("orchestration-state")).toHaveText("awaiting executor");
  await execution.getByRole("button", { name: "Cancel orchestration run", exact: true }).click();
  await dialog.getByRole("button", { name: "Confirm cancellation", exact: true }).click();
  await expect(execution.getByTestId("orchestration-state")).toHaveText("cancelled");
  await expect(execution.getByTestId("task-blocker")).toContainText("This run is cancelled");
  for (const task of await execution.getByRole("navigation", { name: "Orchestration tasks" }).getByRole("button").all()) await expect(task).toContainText("Eligibility: not dispatchable (cancelled)");
  expect(sqlRun(run.id)).toMatchObject({ status: "cancelled", revision: 3, counts: { events: 5 }, execution_performed: false });
  await reloadProject(page, project);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  await expect(execution.getByTestId("orchestration-state")).toHaveText("cancelled");
  await zeroGeneration(page, boundary.budget);
});

test("unrelated workspace cannot inspect or forge completion of a persisted run", async ({ page, context }) => {
  const { project, boundary } = await setupOrchestration(page, context);
  const run = await createRun(page, project.id);
  await expectSavedRun(page, project, run);
  const unsupported = await post(page, `/api/v1/projects/${project.id}/orchestration-runs/${run.id}/tasks/${run.tasks[0].id}/complete`, { status: "verified_complete" });
  expect([404, 405]).toContain(unsupported.status());
  await signout(page); await signup(page, `orchestration-outsider-${Date.now()}@example.com`); await createWorkspace(page, "Unrelated orchestration workspace");
  for (const suffix of ["", "/tasks", "/graph", "/events"]) {
    const denied = await page.request.get(`/api/v1/projects/${project.id}/orchestration-runs/${run.id}${suffix}`);
    expect(denied.status()).toBe(404); expect(await denied.text()).not.toContain(run.snapshot_hash);
  }
  await page.goto(`/projects/${project.id}`);
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Project not found");
  await expect(page.getByTestId("saved-orchestration-run")).toHaveCount(0);
  expect(sqlRun(run.id)).toMatchObject({ status: "awaiting_executor", counts: { tasks: 2, events: 2 }, execution_performed: false });
  await zeroGeneration(page, boundary.budget);
});

test("viewer can inspect real snapshots but cannot create or cancel", async ({ page, context }) => {
  const { project, architecture, boundary } = await setupOrchestration(page, context);
  const run = await createRun(page, project.id);
  await expectSavedRun(page, project, run);
  const email = `orchestration-viewer-${Date.now()}@example.com`;
  const invitationResponse = await post(page, `/api/v1/workspaces/${project.workspace_id}/invitations`, { email, role: "viewer" });
  expect(invitationResponse.status()).toBe(201);
  const invitation = await invitationResponse.json();
  await signout(page); await signup(page, email);
  const token = new URL(invitation.invitation_link).hash.slice("#token=".length);
  const joined = await post(page, "/api/v1/invitations/accept", { token }); expect(joined.status()).toBe(200);
  await page.goto(`/projects/${project.id}`);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  const execution = await expectSavedRun(page, project, run);
  await expect(execution.getByText("Viewer access:", { exact: false })).toBeVisible();
  await expect(execution.getByRole("button", { name: "Create orchestration run", exact: true })).toHaveCount(0);
  await expect(execution.getByRole("button", { name: "Cancel orchestration run", exact: true })).toHaveCount(0);
  expect((await post(page, `/api/v1/projects/${project.id}/orchestration-runs`, { client_request_id: crypto.randomUUID(), architecture_id: architecture.id, architecture_version: 1, architecture_revision: 1 })).status()).toBe(403);
  expect((await post(page, `/api/v1/projects/${project.id}/orchestration-runs/${run.id}/cancel`, { expected_revision: run.revision })).status()).toBe(403);
  await zeroGeneration(page, boundary.budget);
});
