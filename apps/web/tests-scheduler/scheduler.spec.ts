import { test, expect } from "@playwright/test";
import { createRun, setupOrchestration, zeroGeneration } from "../tests/orchestration-setup";
import { reloadProject } from "../tests/architect-preflight";
import { expectScheduling, protocol, provisionWorker, schedulerState, workerArgs } from "../tests/scheduler-setup";

test("durable queue and real protocol acknowledgment remain separate from execution", async ({ page, context }) => {
  // Measured real approval/setup alone reached115s on this Windows environment.
  // Bound this added multi-process journey separately; locator/request limits stay intact.
  test.setTimeout(240000);
  const { project, boundary } = await setupOrchestration(page, context);
  const run = await createRun(page, project.id);
  await expectScheduling(page, run, "No scheduler tick has been recorded");
  const worker = await provisionWorker("ui-provision", project.workspace_id, project.id);
  await protocol("ui-worker-no-work", "scripts.worker_client", ...workerArgs(worker, run.id));
  await protocol("ui-scheduler", "scripts.scheduler");
  await expectScheduling(page, run, "Dispatch: queued");
  await protocol("ui-worker-claim", "scripts.worker_client", ...workerArgs(worker, run.id));
  const panel = await expectScheduling(page, run, "Dispatch: leased");
  await panel.getByText("Local protocol verifier · acknowledged", { exact: true }).click();
  await expect(panel).toContainText("Worker handoff acknowledged. Awaiting an execution-capable agent.");
  const saved = await schedulerState(page, run);
  expect(saved.dispatches).toHaveLength(1);
  await reloadProject(page, project);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  await expectScheduling(page, run, "Dispatch: leased");
  expect((await schedulerState(page, run)).dispatches).toEqual(saved.dispatches);
  await zeroGeneration(page, boundary.budget);
});

test("browser session cannot impersonate a worker or forge completion", async ({ page, context }) => {
  const { project, boundary } = await setupOrchestration(page, context);
  const run = await createRun(page, project.id);
  const claim = await page.request.post("/api/v1/workers/claim", { data: { request_id: crypto.randomUUID(), run_id: run.id } });
  expect(claim.status()).toBe(401);
  const complete = await page.request.post(`/api/v1/workers/leases/${crypto.randomUUID()}/complete`, { data: { state: "verified_complete" } });
  expect([404,405]).toContain(complete.status());
  expect((await schedulerState(page, run)).dispatches).toEqual([]);
  await zeroGeneration(page, boundary.budget);
});

test("scheduling errors preserve the immutable task graph and do not invent success", async ({ page, context }) => {
  const { project } = await setupOrchestration(page, context);
  const run = await createRun(page, project.id);
  const panel = await expectScheduling(page, run, "Eligible root · not queued");
  // Narrow browser network failure: actual source/auth/API/PG remain real.
  await page.route(`**/orchestration-runs/${run.id}/scheduler`, route => route.abort("failed"));
  await panel.getByRole("button", { name: "Refresh scheduling state", exact: true }).click();
  await expect(panel.getByRole("alert")).toContainText("last observed data remains below");
  await expect(panel).toContainText("Eligible root · not queued");
  await expect(page.getByRole("img", { name: "Persisted orchestration dependency graph" })).toBeVisible();
});
