import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { signup, createWorkspace, nav, signout } from "./helpers";
import { createProject, expectProject, reloadProject } from "./architect-preflight";

test.beforeAll(() => { execFileSync("uv", ["run", "--directory", "../api", "python", "-m", "scripts.prepare_tests"], { stdio: "pipe" }); });

test("two people join a real workspace with Viewer restrictions, persistence and logout", async ({ page, browser }) => {
  // This full two-account lifecycle exceeded the old30s total budget during
  // actual verification. Keep every locator/HTTP assertion and zero retries;
  // named phases expose the step that fails within a bounded120s journey.
  test.setTimeout(120000);
  page.setDefaultTimeout(30000);
  page.setDefaultNavigationTimeout(30000);
  const suffix = `${test.info().project.name}-${Date.now()}`;
  const emailA = `owner-${suffix}@example.com`; const emailB = `viewer-${suffix}@example.com`;
  const title = `Shared project ${suffix}`;
  const { project, projectUrl, link } = await test.step("Owner creates a persisted project and a real Viewer invitation", async () => {
    await signup(page, emailA); await createWorkspace(page, "Shared team");
    const project = await createProject(page, title);
    await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
    const projectUrl = page.url();
    await reloadProject(page, project); await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
    await nav(page, "Workspaces"); await page.getByRole("link", { name: "Workspace settings", exact: true }).click();
    await page.getByLabel("Teammate email").fill(emailB);
    await page.getByLabel("Invitation role").selectOption("viewer");
    await page.getByRole("button", { name: "Create invitation link", exact: true }).click();
    const invitation = page.getByLabel("Invitation link · share privately", { exact: true });
    await expect(invitation).toBeVisible();
    const link = await invitation.inputValue();
    expect(link).toContain("#token=");
    await expect(page.getByText("Manual invitation sharing. ORBA does not send email.")).toBeVisible();
    return { project, projectUrl, link };
  });
  const secondContext = await browser.newContext({ viewport: page.viewportSize() ?? undefined, isMobile: !!test.info().project.use.isMobile, hasTouch: !!test.info().project.use.hasTouch });
  try {
    const second = await secondContext.newPage();
    second.setDefaultTimeout(30000);
    second.setDefaultNavigationTimeout(30000);
    await test.step("Intended teammate registers and accepts the email-bound invitation", async () => {
      await second.goto(link);
      await second.getByRole("link", { name: "Create an account to accept", exact: true }).click();
      await second.getByLabel("Display name", { exact: true }).fill("Teammate B");
      await second.getByLabel("Email", { exact: true }).fill(emailB);
      await second.getByLabel("Password", { exact: true }).fill("A long browser password!");
      await second.getByRole("button", { name: "Create account", exact: true }).click();
      await expect(second.getByRole("button", { name: "Accept invitation", exact: true })).toBeVisible();
      await second.getByRole("button", { name: "Accept invitation", exact: true }).click();
      await expect(second.getByRole("heading", { name: title, exact: true })).toBeVisible();
    });
    await test.step("Viewer visibility persists while the actual API rejects project writes", async () => {
      await second.goto(projectUrl);
      await expectProject(second, project);
      await expect(second.getByRole("heading", { name: title, exact: true })).toBeVisible();
      await expect(second.getByRole("button", { name: "Edit project", exact: true })).toHaveCount(0);
      await expect(second.getByText("Viewer access · You can read this project.")).toBeVisible();
      await second.goto("/");
      await expect(second.getByRole("button", { name: "Create project", exact: true })).toBeDisabled();
      const spaces = await second.request.get("/api/v1/workspaces"); const space = (await spaces.json())[0];
      const csrf = await second.request.get("/api/v1/auth/csrf");
      const denied = await second.request.post("/api/v1/projects", { headers: { Origin: "http://localhost:3001", "X-CSRF-Token": (await csrf.json()).csrf_token }, data: { title: "Forbidden viewer write", description: "Denied", workspace_id: space.id } });
      expect(denied.status()).toBe(403);
    });
    await test.step("Owner role change persists and Member creates a real project", async () => {
      await page.reload();
      const roleForm = page.getByRole("form", { name: `Role for ${emailB}`, exact: true });
      await roleForm.getByLabel(`Role for ${emailB}`, { exact: true }).selectOption("member");
      page.once("dialog", (dialog) => dialog.accept());
      const changed = page.waitForResponse((response) => response.request().method() === "PATCH" && response.url().includes("/members/"));
      await roleForm.getByRole("button", { name: "Save role", exact: true }).click();
      expect((await changed).status()).toBe(200);
      await second.reload();
      await expect(second.getByRole("button", { name: "Create project", exact: true })).toBeEnabled();
      const memberTitle = `Member contribution ${suffix}`;
      await createProject(second, memberTitle);
      await expect(second.getByRole("heading", { name: memberTitle, exact: true })).toBeVisible();
    });
    await test.step("Logout hides protected content; real sign-in restores authorized access", async () => {
      await signout(second);
      await second.goto(projectUrl);
      await expect(second.getByRole("heading", { name: "Sign in to your workspace" })).toBeVisible();
      await expect(second.getByText(title, { exact: true })).toHaveCount(0);
      await second.getByRole("main").getByRole("link", { name: "Sign in", exact: true }).click();
      await second.getByLabel("Email", { exact: true }).fill(emailB);
      await second.getByLabel("Password", { exact: true }).fill("A long browser password!");
      await second.getByRole("button", { name: "Sign in", exact: true }).click();
      await expect(second.getByRole("heading", { name: "What would you like to build today?" })).toBeVisible();
      await second.goto(projectUrl);
      await expectProject(second, project);
      await expect(second.getByRole("heading", { name: title, exact: true })).toBeVisible();
    });
  } finally { await secondContext.close(); }
});

test("unrelated exact project UUID stays private and workspace switching clears projects", async ({ page, browser }) => {
  const suffix = `${test.info().project.name}-${Date.now()}`;
  await signup(page, `private-${suffix}@example.com`); await createWorkspace(page, "Private A");
  const title = `Private exact UUID ${suffix}`;
  await page.getByLabel("Project description", { exact: true }).fill(title);
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  const url = page.url(); const id = url.split("/").at(-1);
  await createWorkspace(page, "Private B"); await nav(page, "Projects");
  await expect(page.getByRole("heading", { name: "Every project starts with an idea" })).toBeVisible();
  await expect(page.getByText(title, { exact: true })).toHaveCount(0);
  const toggle = page.getByRole("button", { name: "Open navigation", exact: true }); if (await toggle.isVisible()) await toggle.click();
  const select = page.getByLabel("Workspace", { exact: true });
  const options = await select.locator("option").allTextContents(); expect(options).toContain("Private A");
  await select.selectOption({ label: "Private A" });
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  const otherContext = await browser.newContext({ viewport: page.viewportSize() ?? undefined }); const other = await otherContext.newPage();
  await signup(other, `outsider-${suffix}@example.com`); await createWorkspace(other, "Outsider");
  const denied = await other.request.get(`/api/v1/projects/${id}`); expect(denied.status()).toBe(404); expect(await denied.text()).not.toContain(title);
  await other.goto(url); await expect(other.getByRole("main").getByRole("alert")).toHaveText("Project not found.");
  await expect(other.getByText(title, { exact: true })).toHaveCount(0);
  const stillExists = await page.request.get(`/api/v1/projects/${id}`); expect(stillExists.status()).toBe(200); expect((await stillExists.json()).title).toBe(title);
  await otherContext.close();
});

test("account menu and signout remain keyboard accessible", async ({ page }) => {
  await signup(page, `keyboard-${test.info().project.name}-${Date.now()}@example.com`);
  await createWorkspace(page, "Keyboard team");
  const toggle = page.getByRole("button", { name: "Open navigation", exact: true });
  const account = page.locator("summary").filter({ hasText: "Account ·" });
  if (await toggle.isVisible()) {
    await toggle.click();
    await expect(page.getByRole("dialog", { name: "Workspace navigation" }).getByRole("link").first()).toBeFocused();
    await page.keyboard.press("Shift+Tab");
    await expect(account).toBeFocused();
  } else { await account.focus(); }
  await page.keyboard.press("Enter");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Sign out", exact: true })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
});

test("unconfirmed logout clears protected content without claiming server revocation", async ({ page, context }) => {
  await signup(page, `offline-logout-${test.info().project.name}-${Date.now()}@example.com`);
  await createWorkspace(page, "Offline logout");
  const title = `Private before offline logout ${Date.now()}`;
  await page.getByLabel("Project description", { exact: true }).fill(title);
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  const toggle = page.getByRole("button", { name: "Open navigation", exact: true });
  if (await toggle.isVisible()) await toggle.click();
  await page.locator("summary").filter({ hasText: "Account ·" }).click();
  await context.setOffline(true);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Server sign-out could not be confirmed" })).toBeVisible();
  await expect(page.getByRole("heading", { name: title, exact: true })).toHaveCount(0);
  await context.setOffline(false);
  // The server was unreachable; never fabricate that its session was revoked.
  expect((await page.request.get("/api/v1/auth/me")).status()).toBe(200);
});
