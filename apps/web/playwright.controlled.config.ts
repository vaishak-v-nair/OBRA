/** Deterministic failure tests: ONLY model behavior is doubled; API/PG/browser real. */
import {defineConfig,devices} from "@playwright/test";
export default defineConfig({
  testDir:"./tests-controlled",workers:1,retries:0,forbidOnly:true,timeout:60000,
  reporter:process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ? [["list"],["json"]] : "list",
  use:{baseURL:"http://localhost:3001",trace:"off",screenshot:"off"},
  projects:[
    {name:"chromium",use:{...devices["Desktop Chrome"]}},
    {name:"mobile",use:{...devices["iPhone 13"],defaultBrowserType:"chromium"}},
    {name:"tablet",use:{...devices["iPad Mini"],defaultBrowserType:"chromium"}},
  ],
  webServer:[
    {command:"uv run --directory ../api uvicorn --app-dir . tests.controlled_app:create_controlled_app --factory --host 127.0.0.1 --port 8001 --no-proxy-headers",url:"http://127.0.0.1:8001/health/ready",reuseExistingServer:false,timeout:60000,env:{DATABASE_URL:"postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",ORBA_PM_API_KEY:"",GEMINI_API_KEY:"",ORBA_PM_MODEL:""}},
    {command:"pnpm exec next dev --hostname 127.0.0.1 --port 3001",url:"http://localhost:3001",reuseExistingServer:false,timeout:120000,env:{API_URL:"http://127.0.0.1:8001"}},
  ],
});
