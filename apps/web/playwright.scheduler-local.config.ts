import { defineConfig, devices } from "@playwright/test";
import { noGenerationServers } from "./tests/no-generation-config";
export default defineConfig({
  testDir: "./tests-scheduler-local", workers: 1, retries: 0, forbidOnly: true, timeout: 360000,
  reporter: process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ? [["list"], ["json"]] : "list",
  use: { baseURL: "http://localhost:3001", trace: "off", screenshot: "off", serviceWorkers: "block" },
  projects: [{ name: "chromium-scheduler-control-plane", use: { ...devices["Desktop Chrome"] } }],
  webServer: noGenerationServers,
});
