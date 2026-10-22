/** Credential-free, test-only generation-denying API. Not live provider evidence. */
import type { PlaywrightTestConfig } from "@playwright/test";
export const noGenerationServers: NonNullable<PlaywrightTestConfig["webServer"]> = [
  {
    command: "uv run --directory ../api uvicorn --app-dir . tests.no_generation_app:create_no_generation_app --factory --host 127.0.0.1 --port 8001 --no-proxy-headers",
    url: "http://127.0.0.1:8001/health/ready", reuseExistingServer: false, timeout: 60000,
    env: { DATABASE_URL: "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test", WEB_ORIGIN: "http://localhost:3001", ORBA_PM_API_KEY: "", GEMINI_API_KEY: "", ORBA_PM_MODEL: "", ORBA_ARCHITECT_API_KEY: "", ORBA_ARCHITECT_MODEL: "", ORBA_ARCHITECT_LIVE_OPT_IN: "" },
  },
  {
    command: "pnpm exec next dev --hostname 127.0.0.1 --port 3001",
    url: "http://localhost:3001", reuseExistingServer: false, timeout: 120000,
    env: { API_URL: "http://127.0.0.1:8001" },
  },
];
