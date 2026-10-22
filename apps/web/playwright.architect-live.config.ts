import {execFileSync} from "node:child_process";
import {defineConfig,devices} from "@playwright/test";
if(process.env.ORBA_ARCHITECT_LIVE_OPT_IN!=="1")throw new Error("BLOCKED: explicit fresh Architect live opt-in is required.");
execFileSync("uv",["run","--directory","../api","python","-m","scripts.architect_verification","live-preflight"],{stdio:"pipe"});
export default defineConfig({
  testDir:"./tests-architect-live",workers:1,retries:0,forbidOnly:true,timeout:300000,
  reporter:process.env.PLAYWRIGHT_JSON_OUTPUT_NAME?[["list"],["json"]]:"list",
  use:{baseURL:"http://localhost:3001",trace:"off",screenshot:"off",actionTimeout:15000,serviceWorkers:"block"},
  projects:[{name:"chromium-architect-live",use:{...devices["Desktop Chrome"]}}],
  webServer:[
    {command:"uv run --directory ../api uvicorn orba.main:app --host 127.0.0.1 --port 8001 --no-proxy-headers",url:"http://127.0.0.1:8001/health/ready",reuseExistingServer:false,timeout:60000,env:{DATABASE_URL:"postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",WEB_ORIGIN:"http://localhost:3001"}},
    {command:"pnpm exec next dev --hostname 127.0.0.1 --port 3001",url:"http://localhost:3001",reuseExistingServer:false,timeout:120000,env:{API_URL:"http://127.0.0.1:8001"}},
  ],
});
