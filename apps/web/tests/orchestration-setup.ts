/** Authored source fixtures only. Actual auth, approval UI, API and PostgreSQL. */
import { expect, type Page, type BrowserContext } from "@playwright/test";
import { approveDraft, expectProject, jsonGet, preflightProof, prepareDraft, reloadProject, testCommand } from "./architect-preflight";
import { architectBoundary } from "./architect-boundary";
import type { RunDetail } from "../src/lib/orchestration";

export const sqlRun = (id: string) => JSON.parse(testCommand("scripts.inspect_orchestration", "--run", id));
export async function post(page: Page, path: string, data: unknown) {
  const csrf = await jsonGet<{ csrf_token: string }>(page, "/api/v1/auth/csrf");
  return page.request.post(path, { headers: { Origin: "http://localhost:3001", "X-CSRF-Token": csrf.csrf_token }, data });
}
export async function setupOrchestration(page: Page, context: BrowserContext, approveArchitecture = true) {
  testCommand("scripts.prepare_tests");
  const boundary = await architectBoundary(context);
  const proof = preflightProof();
  const { project, user, authored } = await prepareDraft(page, proof);
  const source = await approveDraft(page, project, user, authored.plan_id, proof);
  const architecture = JSON.parse(testCommand("scripts.seed_orchestration_fixture", "--project", project.id, "--actor", user.id, "--plan", source.id));
  expect(architecture.origin).toBe("human_authored_test_fixture"); expect(architecture.model_requests).toBe(0);
  await reloadProject(page, project);
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Architecture", exact: true }).click();
  const panel = page.getByRole("region", { name: "Architecture workspace", exact: true });
  await expect(panel.getByTestId("architecture-state")).toHaveText("draft");
  if (approveArchitecture) {
    await panel.getByRole("button", { name: "Review architecture approval", exact: true }).click();
    const [response] = await Promise.all([
      page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === `/api/v1/projects/${project.id}/architectures/${architecture.id}/approve`),
      panel.getByRole("button", { name: "Confirm architecture approval", exact: true }).click(),
    ]);
    expect(response.status()).toBe(200);
    await expect(panel.getByTestId("architecture-state")).toHaveText("approved");
  }
  await page.getByRole("navigation", { name: "Project planning views" }).getByRole("button", { name: "Execution Plan", exact: true }).click();
  const execution = page.getByRole("region", { name: "Execution Plan", exact: true });
  await expect(execution.getByRole("heading", { name: "No orchestration runs yet", exact: true })).toBeVisible();
  if (approveArchitecture) await expect(execution.getByRole("button", { name: "Create orchestration run", exact: true })).toBeEnabled();
  return { project, user, source, architecture, execution, boundary };
}
export async function createRun(page: Page, projectId: string, doubleClick = false): Promise<RunDetail> {
  const [response] = await Promise.all([
    page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === `/api/v1/projects/${projectId}/orchestration-runs`),
    doubleClick ? page.getByRole("button", { name: "Create orchestration run", exact: true }).evaluate((button: HTMLButtonElement) => { button.click(); button.click(); }) : page.getByRole("button", { name: "Create orchestration run", exact: true }).click(),
  ]);
  expect(response.status()).toBe(201);
  return response.json() as Promise<RunDetail>;
}
export async function expectSavedRun(page: Page, project: { id: string; workspace_id: string; title: string }, run: RunDetail) {
  await expectProject(page, project as Parameters<typeof expectProject>[1]);
  const panel = page.getByRole("region", { name: "Execution Plan", exact: true });
  await expect(panel.getByTestId("saved-orchestration-run")).toHaveAttribute("data-run-id", run.id);
  await expect(panel.getByTestId("saved-orchestration-run")).toHaveAttribute("data-source-id", run.architecture_id);
  await expect(panel.getByTestId("orchestration-state")).toHaveText("awaiting executor");
  await expect(panel.getByRole("img", { name: "Persisted orchestration dependency graph" })).toBeVisible();
  await expect(panel.getByRole("button", { name: /Persist daily check-ins/ })).toContainText("Eligibility: eligible for future dispatch");
  await panel.getByRole("button", { name: /Display saved check-ins/ }).click();
  await expect(panel.getByTestId("task-blocker")).toHaveText("Waiting for storage to complete with verified evidence.");
  await expect(panel.getByRole("article", { name: "Selected orchestration task" })).toContainText("Execution: awaiting executor");
  await expect(panel.getByText("No executor, artifacts, tests or completion evidence exist.", { exact: false })).toBeVisible();
  return panel;
}
export async function zeroGeneration(page: Page, budget: { attempted: number; forwarded: number; blocked: number }) {
  expect(budget).toEqual({ attempted: 0, forwarded: 0, blocked: 0 });
  const guard = await jsonGet<{ blocked_generation_posts: number; provider_dependency_entries: number }>(page, "http://127.0.0.1:8001/__test/no-generation");
  expect(guard.blocked_generation_posts).toBe(0); expect(guard.provider_dependency_entries).toBe(0);
  return guard;
}
