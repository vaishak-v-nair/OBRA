import { defineConfig, devices } from "@playwright/test";
import { noGenerationServers } from "./tests/no-generation-config";
export default defineConfig({
  testDir: "./tests-scheduler", workers: 1, retries: 0, forbidOnly: true, timeout: 120000,
  reporter: process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ? [["list"], ["json"]] : "list",
  use: { baseURL: "http://localhost:3001", trace: "off", screenshot: "off", serviceWorkers: "block" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }, { name: "mobile", use: { ...devices["iPhone 13"] } }, { name: "tablet", use: { ...devices["iPad (gen 7)"] } }],
  webServer: noGenerationServers,
});
