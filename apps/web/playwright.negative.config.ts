if(process.env.ORBA_EXTERNAL_FAILURE_OPT_IN!=="1")throw new Error("BLOCKED: set ORBA_EXTERNAL_FAILURE_OPT_IN=1 deliberately for this external invalid-key diagnostic; Gate A uses controlled doubles.");
import {defineConfig, devices} from "@playwright/test";
export default defineConfig({
  testDir:"./tests-negative", workers:1, retries:0, reporter:"list", timeout:60000,
  use:{baseURL:"http://localhost:3001",trace:"off",screenshot:"off"},
  projects:[{name:"chromium",use:{...devices["Desktop Chrome"]}}],
  webServer:[
    {command:"uv run --directory ../api uvicorn orba.main:app --host 127.0.0.1 --port 8001 --no-proxy-headers",url:"http://127.0.0.1:8001/health/ready",reuseExistingServer:false,timeout:60000,env:{DATABASE_URL:"postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",WEB_ORIGIN:"http://localhost:3001",ORBA_PM_API_KEY:"orba-invalid-credential-for-negative-verification",ORBA_PM_MODEL:"gemini-3.8-flash",ORBA_PM_TIMEOUT_SECONDS:"15"}},
    {command:"pnpm exec next dev --hostname 127.0.0.1 --port 3001",url:"http://localhost:3001",reuseExistingServer:false,timeout:120000,env:{API_URL:"http://127.0.0.1:8001"}},
  ],
});
