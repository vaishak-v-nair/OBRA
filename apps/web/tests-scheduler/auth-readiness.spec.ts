/** Controlled startup delay only; real auth/API/PostgreSQL, no model or executor. */
import { test, expect } from "@playwright/test";
import { signup } from "../tests/helpers";

test("registration controls wait for client initialization", async ({ page }) => {
  let release!: () => void;
  const startup = new Promise<void>(resolve => { release = resolve; });
  let scripts = 0;
  let registrations = 0;
  page.on("request", request => {
    if (request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/auth/register") registrations++;
  });
  // Hold only the initial Next client scripts. Never record form values or headers.
  await page.route(/\/_next\/static\/.*\.js(?:\?.*)?$/, async route => {
    scripts++;
    await startup;
    await route.continue();
  });
  try {
    await page.goto("/signup", { waitUntil: "commit" });
    await expect(page.getByRole("heading", { name: "Create your account", exact: true })).toBeVisible();
    await expect.poll(() => scripts).toBeGreaterThan(0);
    await expect(page.getByRole("main").locator("form")).toHaveAttribute("method", "post");
    await expect(page.getByLabel("Display name", { exact: true })).toBeDisabled();
    await expect(page.getByLabel("Email", { exact: true })).toBeDisabled();
    await expect(page.getByLabel("Password", { exact: true })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Create account", exact: true })).toBeDisabled();
    expect(registrations).toBe(0);
  } finally { release(); }
  await expect(page.getByLabel("Display name", { exact: true })).toBeEditable();
  await signup(page, `client-ready-${test.info().project.name}-${Date.now()}@example.com`);
  expect(registrations).toBe(1);
});

test("registration waits for the initial authoritative session check", async ({ page }) => {
  let release!: () => void;
  const initialSession = new Promise<void>(resolve => { release = resolve; });
  let held = 0;
  let released = false;
  await page.route("**/api/v1/auth/me", async route => {
    // Development Strict Mode can start more than one initial effect. None of
    // those real requests may finish before this readiness assertion.
    if (!released) { held++; await initialSession; }
    await route.continue();
  });
  try {
    await page.goto("/signup");
    await expect.poll(() => held).toBeGreaterThan(0);
    await expect(page.getByLabel("Display name", { exact: true })).toBeDisabled();
    await expect(page.getByLabel("Email", { exact: true })).toBeDisabled();
    await expect(page.getByLabel("Password", { exact: true })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Create account", exact: true })).toBeDisabled();
  } finally { released = true; release(); }
  await expect(page.getByLabel("Display name", { exact: true })).toBeEditable();
  await signup(page, `session-ready-${test.info().project.name}-${Date.now()}@example.com`);
  test.info().annotations.push({ type: "controlled_initial_session_requests", description: String(held) });
});
