import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./tests", forbidOnly: true, fullyParallel: false, workers: 1, retries: 0,
  reporter: process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ? [["list"], ["json"]] : [["list"], ["html", { open: "never" }]],
  // Network traces include passwords/cookies. Keep auth credentials out of artifacts.
  // Safe home screenshots are captured explicitly by the regression test.
  use: { baseURL: "http://localhost:3001", trace: "off", screenshot: "off" },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" } },
    { name: "tablet", use: { ...devices["iPad Mini"], defaultBrowserType: "chromium" } },
  ],
  webServer: [
    { command: "uv run --directory ../api uvicorn orba.main:app --host 127.0.0.1 --port 8001 --no-proxy-headers", url: "http://127.0.0.1:8001/health/ready", reuseExistingServer: false, env: { DATABASE_URL: "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test", WEB_ORIGIN: "http://localhost:3001", ORBA_PM_API_KEY:"", GEMINI_API_KEY:"", ORBA_PM_MODEL:"" }, timeout: 60000 },
    { command: "pnpm exec next dev --hostname 127.0.0.1 --port 3001", url: "http://localhost:3001", reuseExistingServer: false, env: { API_URL: "http://127.0.0.1:8001" }, timeout: 120000 },
  ],
});


