import { defineConfig, devices } from "@playwright/test";
import { noGenerationServers } from "./tests/no-generation-config";
export default defineConfig({
  // These journeys include multiple independent source-authoring/SQL processes.
  // A measured90s total expired after the real saved ledger was already visible.
  // Keep individual action/navigation bounds short; assertions retain their5s limit.
  testDir: "./tests-orchestration", workers: 1, retries: 0, forbidOnly: true, timeout: 180000,
  reporter: process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ? [["list"], ["json"]] : "list",
  use: { baseURL: "http://localhost:3001", actionTimeout: 30000, navigationTimeout: 30000, trace: "off", screenshot: "off", serviceWorkers: "block" },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" } },
    { name: "tablet", use: { ...devices["iPad Mini"], defaultBrowserType: "chromium" } },
  ],
  webServer: noGenerationServers,
});
