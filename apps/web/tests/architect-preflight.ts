/** Shared Phase1: real UI/auth/API/SQL source approval, never model generation. */
import { expect, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import type { Project, User } from "../src/lib/api";
import type { Plan } from "../src/lib/pm";
import { createWorkspace, signup } from "./helpers";

export type Milestone = { at: string; event: string; path: string; [key: string]: unknown };
export type PreflightProof = {
  result: "FAIL" | "PASS"; approved_source_reloaded: boolean; step: string;
  milestones: Milestone[]; [key: string]: unknown;
};
export const testCommand = (...args: string[]) => execFileSync("uv", ["run", "--directory", "../api", "python", "-m", ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
export function preflightProof(): PreflightProof {
  return { result: "FAIL", approved_source_reloaded: false, step: "initial", milestones: [] };
}
export function mark(page: Page, proof: PreflightProof, event: string, data: Record<string, unknown> = {}) {
  proof.step = event;
  proof.milestones.push({ at: new Date().toISOString(), event, path: new URL(page.url()).pathname, ...data });
}
export function observeRoutes(page: Page, proof: PreflightProof) {
  page.on("framenavigated", frame => {
    if (frame === page.mainFrame() && page.url().startsWith("http")) {
      proof.milestones.push({ at: new Date().toISOString(), event: "route_committed", path: new URL(page.url()).pathname });
    }
  });
}
export async function jsonGet<T>(page: Page, path: string): Promise<T> {
  const response = await page.request.get(path);
  expect(response.status(), `GET ${path} must succeed before the next preflight phase`).toBe(200);
  return response.json() as Promise<T>;
}
export async function expectProject(page: Page, project: Project, timeout = 15000) {
  await expect(page, `Project navigation must commit /projects/${project.id}; actual route is recorded in milestones`).toHaveURL(`http://localhost:3001/projects/${project.id}`, { timeout });
  const detail = page.getByTestId("project-detail");
  await expect(detail, "The requested project must load before reload or approval").toHaveAttribute("data-project-id", project.id, { timeout });
  await expect(detail).toHaveAttribute("data-workspace-id", project.workspace_id);
  await expect(page.getByLabel("Workspace", { exact: true })).toHaveValue(project.workspace_id);
  await expect(page.getByRole("heading", { name: project.title, exact: true })).toBeVisible();
}
export async function createProject(page: Page, description: string, proof?: PreflightProof) {
  await page.getByLabel("Project description", { exact: true }).fill(description);
  // The app's ordinary request budget is20s. Bound this response observation to25s,
  // instead of letting a missing response consume the whole browser test deadline.
  const [response] = await Promise.all([
    page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === "/api/v1/projects", { timeout: 25000 }),
    page.getByRole("button", { name: "Create project", exact: true }).click(),
  ]);
  expect(response.status(), "Project creation must succeed before waiting for its route").toBe(201);
  const project: Project = await response.json();
  if (proof) mark(page, proof, "project_post_received", { project_id: project.id, workspace_id: project.workspace_id, status: response.status() });
  // POST completion does not imply Next router commitment. Never reload before this.
  await expectProject(page, project);
  if (proof) mark(page, proof, "exact_project_loaded", { project_id: project.id, workspace_id: project.workspace_id });
  return project;
}
export async function reloadProject(page: Page, project: Project, proof?: PreflightProof) {
  await expectProject(page, project);
  if (proof) mark(page, proof, "reload_confirmed_project", { project_id: project.id });
  await page.reload();
  await expectProject(page, project);
}
export function sqlSource(project: Project, planId: string, actorId: string) {
  return JSON.parse(testCommand("scripts.inspect_architect_preflight", "--project", project.id, "--plan", planId, "--actor", actorId));
}
export function expectNoGenerationRecords(sql: { generation_records: Record<string, number> }) {
  expect(sql.generation_records).toEqual({ product_manager_runs: 0, architect_runs: 0, architecture_versions: 0, engineering_tasks: 0, task_dependencies: 0 });
}
export async function prepareDraft(page: Page, proof: PreflightProof) {
  await signup(page, `architect-preflight-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`);
  mark(page, proof, "authenticated");
  await createWorkspace(page, "Live architecture verification");
  mark(page, proof, "workspace_selected");
  const project = await createProject(page, "Personal daily habit check-in with saved status after reload. One user, no social features.", proof);
  const user = await jsonGet<User>(page, "/api/v1/auth/me");
  const authored = JSON.parse(testCommand("scripts.seed_pm_fixture", "--project", project.id, "--actor", user.id));
  expect(authored.model_call).toBe(false); expect(authored.origin).toBe("human_authored");
  Object.assign(proof, { project_id: project.id, workspace_id: project.workspace_id, actor_id: user.id, source_plan_id: authored.plan_id, source_origin: authored.origin });
  mark(page, proof, "authored_draft_persisted", { plan_id: authored.plan_id, version: authored.version });
  return { project, user, authored };
}
export async function expectPlan(page: Page, plan: Plan) {
  const saved = page.getByTestId("saved-product-plan");
  await expect(saved, "The exact persisted PRD must load before approval or architecture").toHaveAttribute("data-plan-id", plan.id);
  await expect(saved).toHaveAttribute("data-version", String(plan.version));
  await expect(saved).toHaveAttribute("data-revision", String(plan.revision));
  await expect(page.getByTestId("plan-state")).toHaveText(plan.state);
  await expect(page.getByLabel("Plan version", { exact: true })).toHaveValue(plan.id);
}
export async function approveDraft(page: Page, project: Project, user: User, planId: string, proof: PreflightProof) {
  await reloadProject(page, project, proof);
  const path = `/api/v1/projects/${project.id}/pm-plans/${planId}`;
  const draft = await jsonGet<Plan>(page, path);
  expect(draft.state).toBe("draft"); expect(draft.approved_by).toBeNull();
  await expectPlan(page, draft);
  mark(page, proof, "exact_draft_visible", { plan_id: draft.id, version: draft.version, revision: draft.revision });
  const panel = page.getByRole("region", { name: "Product Plan", exact: true });
  await expect(panel.getByRole("button", { name: "Approve plan", exact: true })).toBeEnabled();
  await panel.getByRole("button", { name: "Approve plan", exact: true }).click();
  const confirmation = panel.getByLabel("Confirm plan approval", { exact: true });
  await expect(confirmation.getByRole("heading", { name: `Approve version ${draft.version}, revision ${draft.revision}?`, exact: true })).toBeVisible();
  const [response] = await Promise.all([
    page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === `${path}/approve`, { timeout: 25000 }),
    confirmation.getByRole("button", { name: "Confirm approval", exact: true }).click(),
  ]);
  mark(page, proof, "approval_http_response", { status: response.status(), plan_id: draft.id });
  expect(response.status(), "PRD approval failed; generation must remain closed").toBe(200);
  const submitted = response.request().postDataJSON();
  expect(submitted).toEqual({ expected_revision: draft.revision, version: draft.version });
  const approved = await jsonGet<Plan>(page, path);
  expect(approved.id).toBe(draft.id); expect(approved.version).toBe(draft.version);
  // Approval binds the saved revision; it does not edit the document or increment it.
  expect(approved.revision).toBe(draft.revision); expect(approved.state).toBe("approved");
  expect(approved.approved_by).toBe(user.id); expect(approved.approved_at).toBeTruthy();
  await expectPlan(page, approved);
  await expect(panel.getByRole("button", { name: "Approve plan", exact: true })).toHaveCount(0);
  proof.approved_sql = sqlSource(project, planId, user.id);
  expect(proof.approved_sql).toMatchObject({ project_id: project.id, workspace_id: project.workspace_id, plan_id: planId, version: approved.version, revision: approved.revision, state: "approved", approved_by: user.id, content_hash: approved.content_hash, current_approved_plan_id: planId, document_validated: true });
  expectNoGenerationRecords(proof.approved_sql as ReturnType<typeof sqlSource>);
  mark(page, proof, "approval_independently_verified", { plan_id: planId, version: approved.version, revision: approved.revision });
  return approved;
}
export async function finishPreflight(page: Page, project: Project, user: User, approved: Plan, proof: PreflightProof) {
  await reloadProject(page, project, proof);
  await expectPlan(page, approved);
  const source = await jsonGet<Plan>(page, `/api/v1/projects/${project.id}/architect-source`);
  expect(source).toMatchObject({ id: approved.id, version: approved.version, revision: approved.revision, content_hash: approved.content_hash, state: "approved", approved_by: user.id });
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Architecture", exact: true }).click();
  const panel = page.getByRole("region", { name: "Architecture workspace", exact: true });
  await expect(panel.getByText(` ${source.document.product_name.text} · v${source.version} / r${source.revision}`.trim(), { exact: true })).toBeVisible();
  await expect(panel.getByRole("button", { name: "Generate Architecture", exact: true })).toBeEnabled();
  await expect(panel.getByLabel("Optional architectural constraints", { exact: true })).toBeEditable();
  const finalSql = sqlSource(project, source.id, user.id);
  expectNoGenerationRecords(finalSql);
  expect(finalSql).toMatchObject({ plan_id: source.id, version: source.version, revision: source.revision, state: "approved", content_hash: source.content_hash, approved_by: user.id });
  Object.assign(proof, { result: "PASS", approved_source_reloaded: true, source_version: source.version, source_revision: source.revision, source_hash: source.content_hash, final_sql: finalSql });
  mark(page, proof, "architect_entry_reached_without_generation", { source_plan_id: source.id, version: source.version, revision: source.revision });
  return { project, user, source };
}
export async function architectPreflight(page: Page, proof: PreflightProof) {
  const { project, user, authored } = await prepareDraft(page, proof);
  const approved = await approveDraft(page, project, user, authored.plan_id, proof);
  return finishPreflight(page, project, user, approved, proof);
}
