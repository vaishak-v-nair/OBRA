/** Real independent local Gate B, one real protocol lease reused, zero execution. */
import { test, expect } from "@playwright/test";
import { readFileSync, writeFileSync } from "node:fs";
import { createRun, expectSavedRun, post, setupOrchestration, sqlRun, zeroGeneration } from "../tests/orchestration-setup";
import { jsonGet, reloadProject, testCommand } from "../tests/architect-preflight";
import { createWorkspace, signout, signup } from "../tests/helpers";
import { evidencePath } from "../tests/evidence";
import { expectScheduling, protocol, provisionWorker, schedulerState, sqlScheduler, startProtocol, workerArgs, workerHeaders, type ProcessReceipt } from "../tests/scheduler-setup";

test("actual scheduler, authenticated protocol client, fencing, restart and reconciliation", async ({ page, context }) => {
  const started = new Date().toISOString();
  const commands: ProcessReceipt[] = [];
  const { project, boundary } = await setupOrchestration(page, context);
  const run = await createRun(page, project.id);
  await expectSavedRun(page, project, run);
  const initial = sqlRun(run.id);
  const replay = await post(page, `/api/v1/projects/${project.id}/orchestration-runs`, { client_request_id: run.client_request_id, architecture_id: run.architecture_id, architecture_version: run.architecture_version, architecture_revision: run.architecture_revision });
  expect(replay.status()).toBe(200);
  const forged = await post(page, `/api/v1/projects/${project.id}/orchestration-runs/${run.id}/tasks/${run.tasks[0].id}/complete`, { status: "verified_complete" });
  expect([404,405]).toContain(forged.status());
  await reloadProject(page, project);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  await expectSavedRun(page, project, run);
  const reloaded = sqlRun(run.id);
  expect(reloaded).toEqual(initial);
  const worker = await provisionWorker("provision", project.workspace_id, project.id); commands.push(worker.receipt);
  commands.push((await protocol("worker-start", "scripts.worker_client", ...workerArgs(worker, run.id))).receipt);
  const registered = await jsonGet<Record<string, unknown>>(page, "/api/v1/auth/me"); expect(registered.id).toBe(run.creator_id);
  const headers = workerHeaders(worker.credential);
  const workerIdentity = await page.request.get("http://127.0.0.1:8001/api/v1/workers/me", { headers }); expect(workerIdentity.status()).toBe(200);
  const workerInfo = await workerIdentity.json();
  commands.push((await protocol("scheduler-start", "scripts.scheduler")).receipt);
  await expectScheduling(page, run, "Dispatch: queued");
  const interruption = startProtocol("scheduler-interrupted", "scripts.scheduler", ["--ticks", "60", "--interval", "5"], true);
  try { await expect.poll(async () => (await schedulerState(page, run)).tick_count, { timeout: 15000 }).toBeGreaterThanOrEqual(2); }
  finally { interruption.child.kill("SIGTERM"); }
  commands.push((await interruption.completed).receipt);
  commands.push((await protocol("scheduler-restart", "scripts.scheduler")).receipt);
  expect((await schedulerState(page, run)).dispatches).toHaveLength(1);
  commands.push((await protocol("worker-claim", "scripts.worker_client", ...workerArgs(worker, run.id))).receipt);
  const leased = await schedulerState(page, run);
  const lease = leased.dispatches[0].leases[0];
  const acknowledged = await page.request.get(`http://127.0.0.1:8001/api/v1/workers/claims/${JSON.parse(requireRead(worker.state)).request_id}`, { headers });
  expect(acknowledged.status()).toBe(200);
  const ack = await acknowledged.json(); expect(ack.lease.state).toBe("acknowledged");
  // Wait against authoritative DB observation for the policy's real heartbeat interval.
  await expect.poll(async () => Date.parse((await schedulerState(page, run)).observed_at)-Date.parse(ack.lease.acknowledged_at), { timeout: 20000, intervals: [250,500,1000] }).toBeGreaterThanOrEqual(10000);
  commands.push((await protocol("worker-restart", "scripts.worker_client", ...workerArgs(worker, run.id))).receipt);
  const heartbeatResponse = await page.request.get(`http://127.0.0.1:8001/api/v1/workers/claims/${JSON.parse(requireRead(worker.state)).request_id}`, { headers });
  const heartbeat = await heartbeatResponse.json(); expect(heartbeat.lease.last_heartbeat_at).toBeTruthy(); expect(heartbeat.lease.id).toBe(lease.id);
  await expectScheduling(page, run, "Dispatch: leased");
  // The stopped acknowledged protocol process produces no side effects. Recovery
  // deliberately still treats acknowledgment as uncertainty, never safe redispatch.
  await expect.poll(async () => Date.parse((await schedulerState(page, run)).observed_at)-Date.parse(heartbeat.lease.expires_at), { timeout: 40000, intervals: [500,1000] }).toBeGreaterThanOrEqual(0);
  commands.push((await protocol("scheduler-expiration", "scripts.scheduler")).receipt);
  const stale = await page.request.post(`http://127.0.0.1:8001/api/v1/workers/leases/${lease.id}/heartbeat`, { headers, data: { fence_epoch: lease.fence_epoch, contract_version: 1, manifest_checksum: ack.manifest.checksum, request_id: crypto.randomUUID() } });
  expect(stale.status()).toBe(409);
  await expectScheduling(page, run, "Manual reconciliation is required before safe redispatch.");
  const final = await schedulerState(page, run);
  expect(final.dispatches[0].state).toBe("needs_reconciliation");
  await reloadProject(page, project);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  await expectScheduling(page, run, "Manual reconciliation is required before safe redispatch.");
  expect((await schedulerState(page, run)).dispatches).toEqual(final.dispatches);
  const independent = sqlScheduler(run.id);
  await expect(page.getByRole("region", { name: "Orchestration event history" }).locator("li")).toHaveCount(independent.orchestration.events.length);
  expect(independent.orchestration.tasks.every((task: { execution_status: string }) => task.execution_status === "awaiting_executor")).toBe(true);
  const revoked = await provisionWorker("revoked-provision", project.workspace_id, project.id); commands.push(revoked.receipt);
  commands.push((await protocol("revoke", "scripts.worker_admin", "revoke", "--worker", revoked.worker_id)).receipt);
  const revokedResponse = await page.request.post("http://127.0.0.1:8001/api/v1/workers/claim", { headers: workerHeaders(revoked.credential), data: { request_id: crypto.randomUUID(), run_id: run.id } }); expect(revokedResponse.status()).toBe(401);
  const boundaryProof = await zeroGeneration(page, boundary.budget);
  await signout(page); await signup(page, `scheduler-outsider-${Date.now()}@example.com`); await createWorkspace(page, "Foreign worker scope");
  const workspaces = await jsonGet<{ id: string }[]>(page, "/api/v1/workspaces");
  const foreign = await provisionWorker("foreign-provision", workspaces[0].id); commands.push(foreign.receipt);
  const foreignResponse = await page.request.post("http://127.0.0.1:8001/api/v1/workers/claim", { headers: workerHeaders(foreign.credential), data: { request_id: crypto.randomUUID(), run_id: run.id } }); expect(foreignResponse.status()).toBe(404);
  const denial = await page.request.get(`/api/v1/projects/${project.id}/orchestration-runs/${run.id}/scheduler`); expect(denial.status()).toBe(404);
  await page.goto(`/projects/${project.id}`); await expect(page.getByRole("main").getByRole("alert")).toContainText("Project not found");
  await expect(page.getByRole("region", { name: "Scheduling and handoffs" })).toHaveCount(0);
  const incomplete = await protocol("incomplete-proof", "scripts.check_scheduler_proof", "--reject-empty"); commands.push(incomplete.receipt);
  const foundation = { proof_version: 2, stage: "stage05a-orchestration", result: "PASS", execution_class: "real_local_control_plane", source_origin: "human_authored_test_fixture_approved_through_real_UI", provider_double: false, executor_available: false,
    started_at: started, completed_at: new Date().toISOString(), run_id: run.id, project_id: project.id, workspace_id: project.workspace_id,
    model_generation_budget: boundary.budget, server_boundary: boundaryProof, model_generation_requests: 0, browser_create_posts: 1,
    explicit_idempotency_replay_status: replay.status(), forged_completion_status: forged.status(), unauthorized_status: denial.status(), protected_ui_hidden: true, reload_persisted: true,
    run_api: run, initial_sql: initial, reloaded_sql: reloaded };
  const proof = { proof_version: 1, stage: "stage05b-scheduler", result: "PASS", execution_class: "real_local_worker_protocol", started_at: started, completed_at: new Date().toISOString(), foundation,
    worker: workerInfo, acknowledged_api: ack, heartbeat_api: heartbeat, final_api: final, independent_sql: independent, process_commands: commands,
    stale_epoch_status: stale.status(), foreign_worker_status: foreignResponse.status(), unauthorized_user_status: denial.status(), revoked_worker_status: revokedResponse.status(),
    model_generation_requests: 0, executed_tasks: 0, browser_rendered: true, reload_persisted: true, protected_ui_hidden: true, incomplete_proof_rejected: true };
  writeFileSync(evidencePath("scheduler-proof.json"), JSON.stringify(proof, null, 2));
  // Invoke the exact production evidence validator against the actual assembled proof.
  expect(JSON.parse(testCommand("scripts.check_scheduler_proof", "--file", evidencePath("scheduler-proof.json"))).result).toBe("PASS");
});

function requireRead(path: string) { return readFileSync(path, "utf8"); }
