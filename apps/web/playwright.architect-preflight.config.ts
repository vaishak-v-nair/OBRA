/** Phase1 only. No opt-in, no real credential, no model generation possible. */
import { defineConfig, devices } from "@playwright/test";
import { noGenerationServers } from "./tests/no-generation-config";
export default defineConfig({
  testDir: "./tests-architect-preflight", workers: 1, retries: 0, forbidOnly: true, timeout: 90000,
  reporter: process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ? [["list"], ["json"]] : "list",
  use: { baseURL: "http://localhost:3001", trace: "off", screenshot: "off", serviceWorkers: "block" },
  projects: [{ name: "chromium-architect-preflight", use: { ...devices["Desktop Chrome"] } }],
  webServer: noGenerationServers,
});
