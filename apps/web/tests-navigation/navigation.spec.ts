/** Real auth/API/PostgreSQL. Controlled transport barriers/errors are labeled below. */
import { test, expect, type Page, type Route } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { architectBoundary } from "../tests/architect-boundary";
import { approveDraft, architectPreflight, createProject, expectNoGenerationRecords, expectPlan, expectProject, jsonGet, observeRoutes, preflightProof, prepareDraft, reloadProject, sqlSource, testCommand, type PreflightProof } from "../tests/architect-preflight";
import { createWorkspace, nav, signup } from "../tests/helpers";
import { evidencePath } from "../tests/evidence";
import type { Project } from "../src/lib/api";
import type { Plan } from "../src/lib/pm";

function latch() {
  let resolve!: () => void;
  const promise = new Promise<void>(done => { resolve = done; });
  return { promise, resolve };
}
async function holdRealResponse(page: Page, pattern: RegExp, accepts: (route: Route) => boolean = () => true) {
  const held = latch(), released = latch();
  let holding = true;
  await page.route(pattern, async route => {
    // React development effects may issue another request after cancelling the first.
    // Hold every matching real response until the observation is complete.
    if (!accepts(route) || !holding) { await route.continue(); return; }
    const response = await route.fetch(); // Actual service response and persistence, never canned content.
    proof.milestones.push({ at: new Date().toISOString(), event: "actual_response_held", path: new URL(route.request().url()).pathname, status: response.status() });
    held.resolve();
    await released.promise;
    await route.fulfill({ response }).catch(error => {
      if (!/Target page, context or browser has been closed|Invalid InterceptionId|already handled/i.test(String(error))) throw error;
      proof.milestones.push({ at: new Date().toISOString(), event: "cancelled_route_response", path: new URL(route.request().url()).pathname });
    });
  });
  return { held: held.promise, release: () => { holding = false; released.resolve(); } };
}
async function write(page: Page, path: string, data: unknown) {
  const csrf = await jsonGet<{ csrf_token: string }>(page, "/api/v1/auth/csrf");
  return page.request.post(path, { headers: { Origin: "http://localhost:3001", "X-CSRF-Token": csrf.csrf_token }, data });
}
async function accountProject(page: Page) {
  await signup(page, `navigation-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`);
  await createWorkspace(page, "Navigation A");
  return createProject(page, "First private project for navigation checks");
}

let proof: PreflightProof;
let blockedBefore = 0;
let boundary: Awaited<ReturnType<typeof architectBoundary>>;
test.beforeEach(async ({ context, page }) => {
  proof = preflightProof();
  observeRoutes(page, proof);
  boundary = await architectBoundary(context);
  Object.assign(proof, { execution_class: "no_generation_navigation_regression", generation_budget: boundary.budget });
  const counters = await jsonGet<{ blocked_generation_posts: number }>(page, "http://127.0.0.1:8001/__test/no-generation");
  blockedBefore = counters.blocked_generation_posts;
  testCommand("scripts.prepare_tests");
});
test.afterEach(async ({ page }, info) => {
  proof.case_result = info.status === info.expectedStatus ? "PASS" : "FAIL";
  try {
    const response = await page.request.get("http://127.0.0.1:8001/__test/no-generation");
    expect(response.status()).toBe(200);
    const counters = await response.json();
    proof.server_boundary = counters;
    expect(counters.provider_dependency_entries).toBe(0);
    expect(counters.blocked_generation_posts - blockedBefore).toBe(proof.expected_denied_posts ?? 0);
    expect(proof.generation_budget).toEqual({ attempted: 0, forwarded: 0, blocked: 0 });
  } catch (error) {
    proof.case_result = "FAIL"; throw error;
  } finally {
    writeFileSync(evidencePath(`navigation-${info.project.name}-${info.title.replaceAll(/[^a-z0-9]+/gi, "-")}.json`), JSON.stringify(proof, null, 2) + "\n");
  }
});

test("shared Phase1 approves the exact source, reloads and stops at Architect entry", async ({ page }) => {
  await architectPreflight(page, proof);
});

test("route confirmation precedes immediate reload even when real Next navigation is held", async ({ page }) => {
  await signup(page, `route-${Date.now()}@example.com`); await createWorkspace(page, "Route synchronization");
  const barrier = await holdRealResponse(page, /\/projects\/[a-f0-9-]+(?:\?.*)?$/, route => /^\/projects\/[a-f0-9-]+$/.test(new URL(route.request().url()).pathname));
  try {
    const creating = createProject(page, "Project created before its real route response arrives", proof);
    await barrier.held;
    expect(new URL(page.url()).pathname).toBe("/");
    await expect(page.getByTestId("project-detail")).toHaveCount(0);
    barrier.release();
    const project = await creating;
    await reloadProject(page, project, proof);
    expect((await jsonGet<Project>(page, `/api/v1/projects/${project.id}`)).id).toBe(project.id);
  } finally { barrier.release(); }
});

test("slow real project API stays on its project route without returning to Chat", async ({ page }) => {
  const project = await accountProject(page);
  await page.goto("/");
  const barrier = await holdRealResponse(page, new RegExp(`/api/v1/projects/${project.id}$`));
  try {
    await page.goto(`/projects/${project.id}`); await barrier.held;
    await expect(page).toHaveURL(`http://localhost:3001/projects/${project.id}`);
    await expect(page.getByRole("status").filter({ hasText: "Loading project" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "What would you like to build today?", exact: true })).toHaveCount(0);
    barrier.release(); await expectProject(page, project); await reloadProject(page, project);
  } finally { barrier.release(); }
});

test("asynchronous workspace restoration preserves the selected project and hides stale content", async ({ page }) => {
  const first = await accountProject(page);
  await createWorkspace(page, "Navigation B");
  const second = await createProject(page, "Second workspace private project");
  const toggle = page.getByRole("button", { name: "Open navigation", exact: true });
  if (await toggle.isVisible()) await toggle.click();
  await page.getByLabel("Workspace", { exact: true }).selectOption(first.workspace_id);
  await expect(page).toHaveURL("http://localhost:3001/projects");
  await page.goto(`/projects/${first.id}`); await expectProject(page, first);
  const barrier = await holdRealResponse(page, /\/api\/v1\/workspaces$/, route => route.request().method() === "GET");
  try {
    await page.reload(); await barrier.held;
    await expect(page.getByRole("status").filter({ hasText: "Checking your session" })).toBeVisible();
    await expect(page.getByRole("heading", { name: first.title, exact: true })).toHaveCount(0);
    await expect(page.getByRole("heading", { name: second.title, exact: true })).toHaveCount(0);
    barrier.release(); await expectProject(page, first);
    await expect(page.getByRole("heading", { name: second.title, exact: true })).toHaveCount(0);
  } finally { barrier.release(); }
});

test("a delayed second project cannot display the first project as its details", async ({ page }) => {
  const first = await accountProject(page);
  await page.goto("/"); const second = await createProject(page, "Another project with distinct protected content");
  await page.goto(`/projects/${first.id}`); await expectProject(page, first);
  const barrier = await holdRealResponse(page, new RegExp(`/api/v1/projects/${second.id}$`));
  try {
    await nav(page, "Projects"); await page.getByRole("link").filter({ has: page.getByRole("heading", { name: second.title, exact: true }) }).click();
    await barrier.held;
    await expect(page).toHaveURL(`http://localhost:3001/projects/${second.id}`);
    await expect(page.getByRole("heading", { name: first.title, exact: true })).toHaveCount(0);
    await expect(page.getByTestId("project-detail")).not.toHaveAttribute("data-project-id", first.id);
    barrier.release(); await expectProject(page, second);
  } finally { barrier.release(); }
});

test("wrong-route synchronization reports expected identity without approving or generating", async ({ page }) => {
  const project = await accountProject(page); await page.goto("/");
  // Isolated negative assertion: inspect the actual failure message; not a gate test retry.
  let message = "";
  try { await expectProject(page, project, 100); } catch (error) { message = String(error); }
  expect(message).toContain(`Project navigation must commit /projects/${project.id}`);
  expect(message).toContain("http://localhost:3001/");
  await expect(page.getByRole("button", { name: "Approve plan", exact: true })).toHaveCount(0);
});

test("real session revocation stops approval and leaves the exact PRD draft", async ({ page }) => {
  const { project, user, authored } = await prepareDraft(page, proof);
  await reloadProject(page, project);
  const draft = await jsonGet<Plan>(page, `/api/v1/projects/${project.id}/pm-plans/${authored.plan_id}`);
  await expectPlan(page, draft);
  const logout = await write(page, "/api/v1/auth/logout", {}); expect(logout.status()).toBe(204);
  // Session cookie removal is real; UI has not received its next authority check yet.
  await page.getByRole("button", { name: "Approve plan", exact: true }).click();
  await page.getByRole("button", { name: "Confirm approval", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Sign in to your workspace", exact: true })).toBeVisible();
  await expect(page.getByTestId("plan-state")).toHaveCount(0);
  const sql = sqlSource(project, authored.plan_id, user.id);
  expect(sql).toMatchObject({ state: "draft", revision: 1, approved_by: null, approved_at: null });
  expectNoGenerationRecords(sql); proof.sql_after_revocation = sql;
});

test("controlled PRD transport failure stops before approval and Architect entry", async ({ page }) => {
  const { project, user, authored } = await prepareDraft(page, proof);
  // Narrow controlled transport failure; project/auth/API/database remain real.
  await page.route(new RegExp(`/api/v1/projects/${project.id}/pm-plans\\?`), route => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: { code: "controlled_transport_failure", message: "PRD temporarily unavailable (controlled transport test)." } }) }));
  await reloadProject(page, project);
  await expect(page.getByRole("region", { name: "Product Plan", exact: true }).getByRole("alert")).toContainText("PRD temporarily unavailable");
  await expect(page.getByRole("button", { name: "Approve plan", exact: true })).toHaveCount(0);
  const sql = sqlSource(project, authored.plan_id, user.id); expect(sql.state).toBe("draft"); expectNoGenerationRecords(sql);
});

test("controlled approval API failure preserves draft and does not claim approval", async ({ page }) => {
  const { project, user, authored } = await prepareDraft(page, proof);
  await reloadProject(page, project);
  await expect(page.getByTestId("plan-state")).toHaveText("draft");
  await page.route(new RegExp(`/pm-plans/${authored.plan_id}/approve$`), route => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: { code: "controlled_approval_failure", message: "Approval unavailable (controlled transport test)." } }) }));
  await page.getByRole("button", { name: "Approve plan", exact: true }).click();
  await page.getByRole("button", { name: "Confirm approval", exact: true }).click();
  await expect(page.getByRole("region", { name: "Product Plan", exact: true }).getByRole("alert")).toContainText("Approval unavailable");
  await expect(page.getByTestId("plan-state")).toHaveText("draft");
  const sql = sqlSource(project, authored.plan_id, user.id); expect(sql.approved_by).toBeNull(); expect(sql.revision).toBe(1); expectNoGenerationRecords(sql);
});

test("a real Member cannot approve the Owner source or access another workspace", async ({ page, browser }) => {
  const { project, user, authored } = await prepareDraft(page, proof);
  const email = `member-navigation-${Date.now()}@example.com`;
  const inviteResponse = await write(page, `/api/v1/workspaces/${project.workspace_id}/invitations`, { email, role: "member" }); expect(inviteResponse.status()).toBe(201);
  const invitation = await inviteResponse.json();
  const otherContext = await browser.newContext();
  try {
    const other = await otherContext.newPage(); await signup(other, email);
    const token = new URLSearchParams(new URL(invitation.invitation_link).hash.slice(1)).get("token");
    const accepted = await write(other, "/api/v1/invitations/accept", { token }); expect(accepted.status()).toBe(200);
    await other.goto(`/projects/${project.id}`); await expectProject(other, project);
    await expect(other.getByTestId("plan-state")).toHaveText("draft");
    await expect(other.getByRole("button", { name: "Approve plan", exact: true })).toHaveCount(0);
    const denied = await write(other, `/api/v1/projects/${project.id}/pm-plans/${authored.plan_id}/approve`, { version: 1, expected_revision: 1 }); expect(denied.status()).toBe(403);
    const sql = sqlSource(project, authored.plan_id, user.id); expect(sql.state).toBe("draft"); expect(sql.approved_by).toBeNull(); expectNoGenerationRecords(sql);
    await createWorkspace(page, "Unrelated to invited member");
    const privateProject = await createProject(page, "Private other workspace content must stay hidden");
    await other.goto(`/projects/${privateProject.id}`); await expect(other.getByRole("main").getByRole("alert")).toHaveText("Project not found.");
    await expect(other.getByRole("heading", { name: privateProject.title, exact: true })).toHaveCount(0);
  } finally { await otherContext.close(); }
});

test("preflight closes before generation when approval prerequisite fails", async ({ page }) => {
  const { project, user, authored } = await prepareDraft(page, proof);
  await reloadProject(page, project);
  await page.route(new RegExp(`/pm-plans/${authored.plan_id}/approve$`), route => route.fulfill({ status: 409, contentType: "application/json", body: JSON.stringify({ error: { code: "controlled_revision_conflict", message: "Saved revision changed (controlled test)." } }) }));
  let message = "";
  try { await approveDraft(page, project, user, authored.plan_id, proof); } catch (error) { message = String(error); }
  expect(message).toContain("PRD approval failed; generation must remain closed");
  expect(proof.result).toBe("FAIL"); expect(proof.approved_source_reloaded).toBe(false);
  expectNoGenerationRecords(sqlSource(project, authored.plan_id, user.id));
});

test("unpaid server boundary rejects direct model POSTs before creating any run", async ({ page, request }) => {
  const { project, user, authored } = await prepareDraft(page, proof);
  proof.expected_denied_posts = 2;
  for (const name of ["pm-runs", "architect-runs"]) {
    // An independent API context deliberately probes the SERVER boundary, bypassing
    // the browser context's client guard. The factory rejects even before auth.
    const denied = await request.post(`http://127.0.0.1:8001/api/v1/projects/${project.id}/${name}`, { data: { client_request_id: crypto.randomUUID() } });
    expect(denied.status()).toBe(409); expect((await denied.json()).error.code).toBe("unpaid_generation_boundary");
  }
  const counters = await jsonGet<{ blocked_generation_posts: number; provider_dependency_entries: number }>(page, "http://127.0.0.1:8001/__test/no-generation");
  expect(counters.blocked_generation_posts - blockedBefore).toBe(2); expect(counters.provider_dependency_entries).toBe(0);
  expectNoGenerationRecords(sqlSource(project, authored.plan_id, user.id));
});

test("unpaid browser boundary cannot open generation even with a claimed passing preflight", async ({ browser }) => {
  let message = "";
  try { boundary.openOneRequest({ result: "PASS", approved_source_reloaded: true }); } catch (error) { message = String(error); }
  expect(message).toContain("Fresh live opt-in is required");
  expect(boundary.phases.map(item => item.phase)).toEqual(["preflight"]);
  expect(boundary.budget).toEqual({ attempted: 0, forwarded: 0, blocked: 0 });
  const probeContext = await browser.newContext({ serviceWorkers: "block" });
  try {
    const probe = await architectBoundary(probeContext);
    let rejected = "";
    try { await probeContext.request.post("http://localhost:3001/api/v1/projects/00000000-0000-0000-0000-000000000099/architect-runs", { data: {} }); } catch (error) { rejected = String(error); }
    expect(rejected).toContain("MODEL_API_REQUEST_FORBIDDEN");
    expect(probe.budget).toEqual({ attempted: 1, forwarded: 0, blocked: 1 });
    proof.explicit_api_guard_probe = { ...probe.budget };
  } finally { await probeContext.close(); }
});
