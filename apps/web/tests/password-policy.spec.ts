/** Actual auth/API/PostgreSQL flows. No response stubs or mocked identities. */
import {execFileSync} from "node:child_process";
import {test, expect, type Locator, type Page} from "@playwright/test";
import {signout} from "./helpers";

test.beforeAll(() => {
  execFileSync("uv", ["run", "--directory", "../api", "python", "-m", "scripts.prepare_tests"], {stdio: "pipe"});
});

async function signupFields(page: Page, email: string) {
  await page.goto("/signup");
  await page.getByLabel("Display name", {exact: true}).fill("Password policy tester");
  await page.getByLabel("Email", {exact: true}).fill(email);
  return page.getByLabel("Password", {exact: true});
}

async function paste(page: Page, input: Locator, value: string) {
  await page.evaluate((text) => navigator.clipboard.writeText(text), value);
  await input.focus();
  await input.press("ControlOrMeta+A");
  await input.press("ControlOrMeta+V");
  await expect(input).toHaveValue(value);
}

test("new password boundaries reject fourteen and accept fifteen without composition rules", async ({page}) => {
  const suffix = `${test.info().project.name}-${Date.now()}`;
  const password = await signupFields(page, `boundary-${suffix}@example.com`);
  let posts = 0;
  page.on("request", (r) => {if (r.method() === "POST" && r.url().endsWith("/auth/register")) posts++;});
  await expect(password).toHaveAttribute("minlength", "15");
  await expect(password).toHaveAttribute("autocomplete", "new-password");
  expect(await password.getAttribute("maxlength")).toBeNull();
  expect(await password.getAttribute("pattern")).toBeNull();
  await expect(password).toHaveAccessibleDescription(/Use 15 to 128 characters/);
  await password.fill("a".repeat(14));
  await page.getByRole("button", {name: "Create account", exact: true}).click();
  expect(posts).toBe(0);
  // Bypass browser validation: the actual API must also reject this credential.
  const csrf = await (await page.request.get("/api/v1/auth/csrf")).json();
  const rejected = await page.request.post("/api/v1/auth/register", {
    headers: {Origin: "http://localhost:3001", "X-CSRF-Token": csrf.csrf_token},
    data: {email: `server-boundary-${suffix}@example.com`, password: "a".repeat(14), display_name: "Rejected"},
  });
  expect(rejected.status()).toBe(422);
  expect((await rejected.json()).error.details.some((d: {field: string}) => d.field === "body.password")).toBe(true);
  expect((await page.request.get("/api/v1/auth/me")).status()).toBe(401);
  // Fourteen astral code points have28 UTF-16 units; submit-time counting still rejects.
  await password.fill("🔐".repeat(14));
  await page.getByRole("button", {name: "Create account", exact: true}).click();
  await expect(page.getByRole("main").getByRole("alert")).toHaveText("Use a password of 15 to 128 characters.");
  await expect(password).toHaveAttribute("aria-invalid", "true");
  await expect(password).toBeFocused();
  expect(posts).toBe(0);
  await expect(page.getByRole("button", {name: "Create account", exact: true})).toBeEnabled();
  await password.fill("a".repeat(15));
  await expect(page.getByRole("main").getByRole("alert")).toHaveCount(0);
  const created = page.waitForResponse((r) => r.request().method() === "POST" && r.url().endsWith("/auth/register"));
  await password.press("Tab");
  await expect(page.getByRole("button", {name: "Create account", exact: true})).toBeFocused();
  await page.keyboard.press("Enter");
  expect((await created).status()).toBe(201);
  await expect(page.getByRole("heading", {name: "A home for your ideas"})).toBeVisible();
  expect(posts).toBe(1);
  await signout(page);
  const unicode = await signupFields(page, `unicode-boundary-${suffix}@example.com`);
  await unicode.fill("🔐".repeat(15));
  const unicodeCreated = page.waitForResponse((r) => r.request().method() === "POST" && r.url().endsWith("/auth/register"));
  await unicode.press("Enter");
  expect((await unicodeCreated).status()).toBe(201);
  await expect(page.getByRole("heading", {name: "A home for your ideas"})).toBeVisible();
});

test("actual clipboard paste preserves over-limit values and full unicode passphrase login", async ({page, context}) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"], {origin: "http://localhost:3001"});
  const email = `paste-${test.info().project.name}-${Date.now()}@example.com`;
  const password = await signupFields(page, email);
  let posts = 0;
  page.on("request", (r) => {if (r.method() === "POST" && /\/auth\/(register|login)$/.test(r.url())) posts++;});
  for (const value of ["a".repeat(129), "🔐".repeat(129)]) {
    await paste(page, password, value);
    await password.press("Enter");
    await expect(page.getByRole("main").getByRole("alert")).toHaveText("Use a password of 15 to 128 characters.");
    await expect(password).toHaveValue(value);
    await expect(password).toBeFocused();
    expect(posts).toBe(0);
  }
  const accepted = "🔐".repeat(128);
  await paste(page, password, accepted);
  const created = page.waitForResponse((r) => r.request().method() === "POST" && r.url().endsWith("/auth/register"));
  await password.press("Enter");
  expect((await created).status()).toBe(201);
  await expect(page.getByRole("heading", {name: "A home for your ideas"})).toBeVisible();
  expect(posts).toBe(1);
  await signout(page);
  await page.getByLabel("Email", {exact: true}).fill(email);
  const signin = page.getByLabel("Password", {exact: true});
  await expect(signin).toHaveAttribute("autocomplete", "current-password");
  await expect(signin).toHaveAttribute("minlength", "1");
  expect(await signin.getAttribute("maxlength")).toBeNull();
  await paste(page, signin, "🔐".repeat(129));
  await signin.press("Enter");
  await expect(page.getByRole("main").getByRole("alert")).toHaveText("Use a password of 1 to 128 characters.");
  expect(posts).toBe(1);
  await paste(page, signin, accepted);
  const loggedIn = page.waitForResponse((r) => r.request().method() === "POST" && r.url().endsWith("/auth/login"));
  await signin.press("Enter");
  expect((await loggedIn).status()).toBe(200);
  await expect(page.getByRole("heading", {name: "A home for your ideas"})).toBeVisible();
  expect(posts).toBe(2);
  await page.reload();
  await expect(page.getByRole("heading", {name: "A home for your ideas"})).toBeVisible();
  expect((await page.request.get("/api/v1/auth/me")).status()).toBe(200);
});

test("a real legacy twelve-character account signs in and keeps ordinary credential rejection", async ({page}) => {
  const email = `legacy-${test.info().project.name}-${Date.now()}@example.com`;
  const seeded = JSON.parse(execFileSync("uv", ["run", "--directory", "../api", "python", "-m", "tests.password_support", "--email", email], {encoding: "utf8", stdio: ["ignore", "pipe", "pipe"]}));
  await page.goto("/signin");
  await page.getByLabel("Email", {exact: true}).fill(email);
  const password = page.getByLabel("Password", {exact: true});
  await expect(password).toHaveAttribute("minlength", "1");
  await password.fill("oldpassword!");
  const loggedIn = page.waitForResponse((r) => r.request().method() === "POST" && r.url().endsWith("/auth/login"));
  await password.press("Enter");
  expect((await loggedIn).status()).toBe(200);
  await expect(page.getByRole("heading", {name: "A home for your ideas"})).toBeVisible();
  expect((await (await page.request.get("/api/v1/auth/me")).json()).id).toBe(seeded.user_id);
  await page.reload();
  await expect(page.getByRole("heading", {name: "A home for your ideas"})).toBeVisible();
  await signout(page);
  await page.getByLabel("Email", {exact: true}).fill(email);
  await password.fill("wrong");
  const denied = page.waitForResponse((r) => r.request().method() === "POST" && r.url().endsWith("/auth/login"));
  await password.press("Enter");
  expect((await denied).status()).toBe(401);
  await expect(page.getByRole("main").getByRole("alert")).toHaveText("Email or password is incorrect.");
  await expect(password).toHaveValue("wrong");
  await expect(page.getByRole("button", {name: "Sign in", exact: true})).toBeEnabled();
});
