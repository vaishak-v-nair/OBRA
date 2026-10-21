import { evidencePath } from "./evidence";
import { test, expect, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { signup, createWorkspace } from "./helpers";

test.beforeAll(() => { execFileSync("uv", ["run", "--directory", "../api", "python", "-m", "scripts.prepare_tests"], { stdio: "pipe" }); });
test.beforeEach(async ({ page }) => {
  await signup(page, `stage01-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`);
  await createWorkspace(page, "Regression workspace");
});

test("empty Projects gives a usable first-project action", async ({ page }) => {
  await page.goto("/projects");
  await expect(page.getByRole("heading", { name: "Every project starts with an idea" })).toBeVisible();
  await page.getByRole("link", { name: "Create your first project" }).click();
  await expect(page.getByLabel("Project title")).toBeVisible();
});

async function navigate(page: Page, name: string) {
  const menu = page.getByRole("button", { name: "Open navigation", exact: true });
  if (await menu.isVisible()) await menu.click();
  await page.getByRole("navigation", { name: "Main navigation" }).getByRole("link", { name, exact: true }).click();
}

test("chat creates a real project, survives reload, and appears in Projects", async ({ page }) => {
  const description = `Persistence ${test.info().project.name} ${Date.now()}\nBuild a thoughtful reading workspace.`;
  const title = description.split("\n")[0];
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "What would you like to build today?" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Attachments coming in a later stage" })).toBeDisabled();
  await page.getByLabel("Project description", { exact: true }).fill(description);
  const save = page.waitForResponse((response) => response.url().endsWith("/api/v1/projects") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  const response = await save;
  expect(response.status()).toBe(201);
  const record = await response.json();
  await expect(page).toHaveURL(new RegExp(`/projects/${record.id}$`));
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  // The editable PM brief also contains this text; verify the saved overview explicitly.
  const originalDescription = page.locator("p.original-description");
  await expect(originalDescription).toBeVisible();
  await expect(originalDescription).toHaveText(description);
  await expect(page.getByRole("textbox", { name: "Product brief", exact: true })).toHaveValue(description);
  await page.reload();
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  await expect(originalDescription).toHaveText(description);
  await expect(page.getByRole("textbox", { name: "Product brief", exact: true })).toHaveValue(description);
  await navigate(page, "Projects");
  await expect(page.getByRole("link").filter({ has: page.getByRole("heading", { name: title, exact: true }) })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("explicit project form saves title and description", async ({ page }) => {
  const title = `Named project ${test.info().project.name} ${Date.now()}`;
  await page.goto("/projects/new");
  await page.getByLabel("Project title").fill(title);
  await page.getByLabel("Project description", { exact: true }).fill("A project with a deliberate title.");
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
});

test("theme persists, future sections are honest, keyboard navigation works", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "What would you like to build today?" })).toBeVisible();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  const before = await page.locator("html").getAttribute("class");
  await page.getByRole("button", { name: "Toggle color theme" }).click();
  await expect(page.locator("html")).not.toHaveAttribute("class", before ?? "");
  const after = await page.locator("html").getAttribute("class");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("class", after!);
  await navigate(page, "Skills");
  await expect(page.getByRole("heading", { name: "Coming in a later stage" })).toBeVisible();
});

test("nonexistent project shows an actual API not-found error", async ({ page }) => {
  await page.goto("/projects/00000000-0000-0000-0000-000000000000");
  await expect(page.getByRole("main").getByRole("alert")).toHaveText("Project not found.");
});

test("network failure preserves the draft and permits deliberate retry", async ({ page, context }) => {
  const description = `Recoverable draft ${test.info().project.name} ${Date.now()}`;
  await page.goto("/");
  await page.getByLabel("Project description", { exact: true }).fill(description);
  await context.setOffline(true);
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Could not reach ORBA");
  await expect(page.getByLabel("Project description", { exact: true })).toHaveValue(description);
  await context.setOffline(false);
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  await expect(page.getByRole("heading", { name: description, exact: true })).toBeVisible();
});

test("whitespace cannot create a project", async ({ page }) => {
  await page.goto("/");
  let posts = 0;
  page.on("request", (request) => { if (request.method() === "POST" && request.url().endsWith("/api/v1/projects")) posts++; });
  await page.getByLabel("Project description", { exact: true }).fill("   ");
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Enter a project description");
  expect(posts).toBe(0);
});

test("navigation supports mobile Escape and focus restoration", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "What would you like to build today?" })).toBeVisible();
  const menu = page.getByRole("button", { name: "Open navigation", exact: true });
  if (await menu.isVisible()) {
    await menu.click();
    await expect(page.getByRole("dialog", { name: "Workspace navigation" })).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(menu).toBeFocused();
    await expect(page.getByRole("link", { name: "Settings", exact: true })).toBeHidden();
  } else {
    await expect(page.getByRole("navigation", { name: "Main navigation" })).toBeVisible();
  }
});

test("home layout in both themes", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "What would you like to build today?" })).toBeVisible();
  await page.screenshot({ path: evidencePath(`${test.info().project.name}-home.png`), fullPage: true });
  await page.getByRole("button", { name: "Toggle color theme" }).click();
  await page.screenshot({ path: evidencePath(`${test.info().project.name}-home-alternate.png`), fullPage: true });
});

test("rapid duplicate submission sends a single creation request", async ({ page }) => {
  const title = `Single save ${test.info().project.name} ${Date.now()}`;
  let posts = 0;
  page.on("request", (request) => { if (request.method() === "POST" && request.url().endsWith("/api/v1/projects")) posts++; });
  await page.goto("/");
  await page.getByLabel("Project description", { exact: true }).fill(title);
  await page.getByRole("form", { name: "Create project", exact: true }).evaluate((form: HTMLFormElement) => { form.requestSubmit(); form.requestSubmit(); });
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  expect(posts).toBe(1);
});

