import {execFileSync} from "node:child_process";
if(process.env.ORBA_LIVE_OPT_IN!=="1")throw new Error("BLOCKED: explicit live opt-in required. Use scripts/verify-live.ps1 -AllowPaid after Gate A.");
execFileSync("uv",["run","--directory","../api","python","-m","scripts.verification","live-preflight"],{stdio:"pipe"});
import {defineConfig,devices} from "@playwright/test";
export default defineConfig({
  testDir:"./tests-live",workers:1,retries:0,forbidOnly:true,reporter:process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ? [["list"],["json"]] : "list",timeout:300000,
  use:{baseURL:"http://localhost:3001",trace:"off",screenshot:"off",actionTimeout:15000},
  projects:[{name:"chromium-live",use:{...devices["Desktop Chrome"]}}],
  webServer:[
    {command:"uv run --directory ../api uvicorn orba.main:app --host 127.0.0.1 --port 8001 --no-proxy-headers",url:"http://127.0.0.1:8001/health/ready",reuseExistingServer:false,timeout:60000,env:{DATABASE_URL:"postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",WEB_ORIGIN:"http://localhost:3001"}},
    {command:"pnpm exec next dev --hostname 127.0.0.1 --port 3001",url:"http://localhost:3001",reuseExistingServer:false,timeout:120000,env:{API_URL:"http://127.0.0.1:8001"}},
  ],
});
