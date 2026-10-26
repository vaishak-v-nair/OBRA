/** Actual bounded native processes. No model/executor and no synthetic process receipts. */
import { expect, type Page } from "@playwright/test";
import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { evidencePath } from "./evidence";
import { jsonGet, testCommand } from "./architect-preflight";
import type { RunDetail } from "../src/lib/orchestration";
import type { SchedulerState } from "../src/components/scheduler-status";

export type ProcessReceipt = { receipt_id: string; name: string; argv: string[]; pid: number; exit_code: number | null; signal: string | null; expected_termination: boolean; started_at: string; completed_at: string };
export function startProtocol(name: string, module: string, args: string[] = [], terminate = false) {
  const python = resolve("../api/.venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
  const argv = [python, "-m", module, ...args];
  const started = new Date().toISOString();
  const child = spawn(python, argv.slice(1), { cwd: resolve("../api"), windowsHide: true, stdio: ["ignore", "pipe", "pipe"], env: {
    ...process.env, DATABASE_URL: "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",
    TEST_DATABASE_URL: "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",
    ORBA_PM_API_KEY: "", GEMINI_API_KEY: "", ORBA_PM_MODEL: "", ORBA_ARCHITECT_API_KEY: "", ORBA_ARCHITECT_MODEL: "", PYTHONIOENCODING: "utf-8",
  } });
  let output = "", errors = "";
  child.stdout.on("data", value => { output += String(value); });
  child.stderr.on("data", value => { errors += String(value); });
  const completed = new Promise<{ receipt: ProcessReceipt; output: string }>((accept, reject) => {
    const deadline = setTimeout(() => { child.kill(); reject(new Error(`Bounded protocol process ${name} exceeded its60s deadline`)); }, 60000);
    child.once("error", error => { clearTimeout(deadline); reject(error); });
    child.once("close", (code, signal) => {
      clearTimeout(deadline);
      const receipt: ProcessReceipt = { receipt_id: randomUUID(), name, argv, pid: child.pid ?? 0, exit_code: code, signal, expected_termination: terminate, started_at: started, completed_at: new Date().toISOString() };
      writeFileSync(evidencePath(`${receipt.receipt_id}-process.json`), JSON.stringify(receipt, null, 2), { flag: "wx" });
      writeFileSync(evidencePath(`${receipt.receipt_id}-process.log`), output+errors, { flag: "wx" });
      if (!terminate && code !== 0) reject(new Error(`Protocol process ${name} exited ${code}; see its sanitized receipt/log`));
      else accept({ receipt, output });
    });
  });
  return { child, completed };
}
export async function protocol(name: string, module: string, ...args: string[]) { return startProtocol(name, module, args).completed; }
export function privateWorkerFiles() {
  const dir = mkdtempSync(join(tmpdir(), "orba-protocol-"));
  return { credential: join(dir, "worker.credential"), state: join(dir, "claim-state.json") };
}
export async function provisionWorker(name: string, workspace: string, project?: string) {
  const files = privateWorkerFiles();
  const result = await protocol(name, "scripts.worker_admin", "provision", "--workspace", workspace, ...(project ? ["--project", project] : []), "--name", "Local protocol verifier", "--capability", "backend", "--credential-file", files.credential);
  return { ...files, receipt: result.receipt, worker_id: JSON.parse(result.output.trim()).worker_id as string };
}
export const workerArgs = (files: { credential: string; state: string }, run: string) => ["--api-url", "http://127.0.0.1:8001", "--credential-file", files.credential, "--state-file", files.state, "--run", run, "--cycles", "1"];
export const workerHeaders = (credential: string) => ({ Authorization: `Bearer ${readFileSync(credential, "ascii").trim()}` });
export const sqlScheduler = (run: string) => JSON.parse(testCommand("scripts.inspect_scheduler", "--run", run));
export const schedulerState = (page: Page, run: RunDetail) => jsonGet<SchedulerState>(page, `/api/v1/projects/${run.project_id}/orchestration-runs/${run.id}/scheduler`);
export async function expectScheduling(page: Page, run: RunDetail, text: string) {
  const panel = page.getByRole("region", { name: "Scheduling and handoffs", exact: true });
  await panel.getByRole("button", { name: "Refresh scheduling state", exact: true }).click();
  await expect(panel).toContainText(text);
  await expect(panel.getByTestId("dispatch-task")).toHaveCount(run.tasks.length);
  return panel;
}
