import { expect, type Page } from "@playwright/test";
export async function signup(page: Page, email: string, fragment = "") {
  await page.goto(`/signup${fragment}`);
  await page.getByLabel("Display name", { exact: true }).fill("ORBA Tester");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByLabel("Password", { exact: true }).fill("A long browser password!");
  await page.getByRole("button", { name: "Create account", exact: true }).click();
  if (!fragment) await expect(page.getByRole("heading", { name: "A home for your ideas" })).toBeVisible();
}
export async function createWorkspace(page: Page, name: string) {
  await page.goto("/workspaces/new");
  await page.getByLabel("Workspace name", { exact: true }).fill(name);
  await page.getByRole("button", { name: "Create workspace", exact: true }).click();
  await expect(page.getByRole("heading", { name: "What would you like to build today?" })).toBeVisible();
}
export async function nav(page: Page, name: string) {
  const menu = page.getByRole("button", { name: "Open navigation", exact: true });
  if (await menu.isVisible()) await menu.click();
  await page.getByRole("navigation", { name: "Main navigation" }).getByRole("link", { name, exact: true }).click();
}
export async function signout(page: Page) {
  const menu = page.getByRole("button", { name: "Open navigation", exact: true });
  if (await menu.isVisible()) await menu.click();
  await page.locator("summary").filter({ hasText: "Account ·" }).click();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
}
