/** Independent Gate B: actual local control plane. No fake executor or AI response. */
import { test, expect } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { createRun, expectSavedRun, post, setupOrchestration, sqlRun, zeroGeneration } from "../tests/orchestration-setup";
import { jsonGet, reloadProject } from "../tests/architect-preflight";
import { createWorkspace, signout, signup } from "../tests/helpers";
import { evidencePath } from "../tests/evidence";
import type { RunDetail } from "../src/lib/orchestration";

test("real local control-plane snapshot, graph, ledger, reload and isolation", async ({ page, context }) => {
  const startedAt = new Date().toISOString();
  const { project, user, source, architecture, boundary } = await setupOrchestration(page, context);
  let posts = 0;
  page.on("request", request => { if (request.method() === "POST" && new URL(request.url()).pathname === `/api/v1/projects/${project.id}/orchestration-runs`) posts++; });
  const run = await createRun(page, project.id, true);
  const panel = await expectSavedRun(page, project, run);
  const audit = sqlRun(run.id); // New native process, independent SQL connection, no API cache.
  expect(audit).toMatchObject({ run_id: run.id, project_id: project.id, workspace_id: project.workspace_id, creator_id: user.id,
    architecture_id: architecture.id, architecture_version: 1, architecture_revision: 1, source_plan_id: source.id,
    source_version: source.version, source_revision: source.revision, source_hash: source.content_hash,
    snapshot_hash: run.snapshot_hash, hash_valid: true, relational_snapshot_valid: true,
    status: "awaiting_executor", revision: 2, execution_performed: false, counts: { tasks: 2, dependencies: 1, traces: 3, events: 2 } });
  expect(audit.graph).toEqual(run.graph);
  expect(audit.events.map((event: { sequence: number }) => event.sequence)).toEqual([1, 2]);
  await expect(panel.getByRole("region", { name: "Orchestration event history" }).locator("li")).toHaveCount(audit.events.length);
  const identical = await post(page, `/api/v1/projects/${project.id}/orchestration-runs`, { client_request_id: run.client_request_id, architecture_id: architecture.id, architecture_version: 1, architecture_revision: 1 });
  expect(identical.status()).toBe(200); expect((await identical.json()).id).toBe(run.id);
  const forged = await post(page, `/api/v1/projects/${project.id}/orchestration-runs/${run.id}/tasks/${run.tasks[0].id}/complete`, { status: "verified_complete" });
  expect([404, 405]).toContain(forged.status());
  await reloadProject(page, project);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  await expectSavedRun(page, project, run);
  const recovered = await jsonGet<RunDetail>(page, `/api/v1/projects/${project.id}/orchestration-runs/${run.id}`);
  expect(recovered).toEqual(run); expect(posts).toBe(1);
  const secondAudit = sqlRun(run.id); expect(secondAudit).toEqual(audit);
  const boundaryProof = await zeroGeneration(page, boundary.budget);
  await page.screenshot({ path: evidencePath("local-control-plane.png"), fullPage: true });
  await signout(page); await signup(page, `local-control-outsider-${Date.now()}@example.com`); await createWorkspace(page, "Local Gate B outsider");
  const denial = await page.request.get(`/api/v1/projects/${project.id}/orchestration-runs/${run.id}`);
  expect(denial.status()).toBe(404); expect(await denial.text()).not.toContain(run.snapshot_hash);
  await page.goto(`/projects/${project.id}`); await expect(page.getByRole("main").getByRole("alert")).toContainText("Project not found");
  await expect(page.getByTestId("saved-orchestration-run")).toHaveCount(0);
  expect(sqlRun(run.id)).toEqual(audit);
  await zeroGeneration(page, boundary.budget);
  writeFileSync(evidencePath("local-proof.json"), JSON.stringify({ proof_version: 2, stage: "stage05a-orchestration", result: "PASS", execution_class: "real_local_control_plane",
    source_origin: "human_authored_test_fixture_approved_through_real_UI", provider_double: false, executor_available: false,
    started_at: startedAt, completed_at: new Date().toISOString(), run_id: run.id, project_id: project.id, workspace_id: project.workspace_id,
    model_generation_budget: boundary.budget, server_boundary: boundaryProof, model_generation_requests: 0,
    browser_create_posts: posts, explicit_idempotency_replay_status: identical.status(), forged_completion_status: forged.status(),
    unauthorized_status: denial.status(), protected_ui_hidden: true, reload_persisted: true,
    run_api: run, initial_sql: audit, reloaded_sql: secondAudit }, null, 2));
});
