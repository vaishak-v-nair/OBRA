import { expect, type Page } from "@playwright/test";
export async function signup(page: Page, email: string, fragment = "") {
  await page.goto(`/signup${fragment}`);
  await page.getByLabel("Display name", { exact: true }).fill("ORBA Tester");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByLabel("Password", { exact: true }).fill("A long browser password!");
  const [registered, account] = await Promise.all([
    page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === "/api/v1/auth/register", { timeout: 25000 }),
    page.waitForResponse(r => r.request().method() === "GET" && new URL(r.url()).pathname === "/api/v1/auth/me" && r.status() === 200, { timeout: 25000 }),
    page.getByRole("button", { name: "Create account", exact: true }).click(),
  ]);
  expect(registered.status(), "Registration must persist before waiting for navigation").toBe(201);
  expect((await account.json()).id, "Session must resolve the newly registered identity").toBe((await registered.json()).id);
  await expect(page, "Auth refresh and route commitment precede workspace setup").toHaveURL(url => url.pathname === (fragment ? "/invitations/accept" : "/"), { timeout: 15000 });
  if (!fragment) await expect(page.getByRole("heading", { name: "A home for your ideas" })).toBeVisible();
}
export async function createWorkspace(page: Page, name: string) {
  await page.goto("/workspaces/new");
  await page.getByLabel("Workspace name", { exact: true }).fill(name);
  const [saved] = await Promise.all([
    page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === "/api/v1/workspaces", { timeout: 25000 }),
    page.getByRole("button", { name: "Create workspace", exact: true }).click(),
  ]);
  expect(saved.status()).toBe(201);
  await expect(page.getByLabel("Workspace", { exact: true })).toHaveValue((await saved.json()).id, { timeout: 15000 });
  await expect(page).toHaveURL(url => url.pathname === "/", { timeout: 15000 });
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
  const [signedOut] = await Promise.all([
    page.waitForResponse(r => r.request().method() === "POST" && new URL(r.url()).pathname === "/api/v1/auth/logout", { timeout: 25000 }),
    page.getByRole("button", { name: "Sign out", exact: true }).click(),
  ]);
  expect(signedOut.status()).toBe(204);
  await expect(page).toHaveURL(url => url.pathname === "/signin", { timeout: 15000 });
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
}
