"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { request } from "@/lib/api";
import type { RunDetail } from "@/lib/orchestration";
import { Button } from "@/components/ui/button";

type Lease = { id: string; worker_id: string; fence_epoch: number; state: string; acknowledge_by: string; expires_at: string; acknowledged_at: string | null; last_heartbeat_at: string | null; reason: string | null };
type Dispatch = { id: string; task_id: string; required_capability: string; state: string; attempts: number; fence_epoch: number; worker_name: string | null; leases: Lease[] };
export type SchedulerState = { run_id: string; snapshot_hash: string; observed_at: string; last_tick_at: string | null; tick_count: number; dispatches: Dispatch[]; execution_performed: false };
const label = (value: string) => value.replaceAll("_", " ");

export function SchedulerStatus({ run }: { run: RunDetail }) {
  const [saved, setSaved] = useState<SchedulerState>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const life = useRef<AbortController | null>(null);
  const load = useCallback(async (signal: AbortSignal) => {
    setLoading(true); setError("");
    try {
      const value = await request<SchedulerState>(`/api/v1/projects/${run.project_id}/orchestration-runs/${run.id}/scheduler`, { signal });
      if (value.run_id !== run.id || value.snapshot_hash !== run.snapshot_hash) throw new Error("Scheduler state did not match the selected run. Refresh before reviewing ownership.");
      if (!signal.aborted) setSaved(value);
    } catch (e) { if (!signal.aborted) setError(e instanceof Error ? e.message : "Scheduling state could not load."); }
    finally { if (!signal.aborted) setLoading(false); }
  }, [run.id, run.project_id, run.snapshot_hash]);
  useEffect(() => { const controller = new AbortController(); life.current = controller; void Promise.resolve().then(() => { if (!controller.signal.aborted) return load(controller.signal); }); return () => controller.abort(); }, [load]);
  return <section className="scheduler-status" aria-label="Scheduling and handoffs">
    <h3>Scheduling and handoffs</h3>
    <p>Leases establish temporary ownership. Acknowledgment confirms receipt; no engineering execution or completion has been verified.</p>
    {loading && <p role="status">Loading saved scheduling state…</p>}
    {error && <p role="alert">{error}{saved ? " The last observed data remains below; refresh to confirm current ownership." : ""}</p>}
    <Button variant="outline" disabled={loading} onClick={() => { if (life.current) void load(life.current.signal); }}>Refresh scheduling state</Button>
    {saved && <>
      <p>{saved.last_tick_at ? <>Last recorded scheduler tick: <time dateTime={saved.last_tick_at}>{new Date(saved.last_tick_at).toLocaleString()}</time> · tick {saved.tick_count}. This timestamp does not prove the process is still running.</> : "No scheduler tick has been recorded. The local operator can start the scheduler and provision a scoped protocol worker."}</p>
      <ul className="scheduler-tasks">{run.tasks.map(task => {
        const dispatch = saved.dispatches.find(item => item.task_id === task.id);
        const lease = dispatch?.leases.at(-1);
        return <li key={task.id} data-testid="dispatch-task" data-task-id={task.id}>
          <h4>{task.definition.title}</h4>
          <p>{dispatch ? `Dispatch: ${label(dispatch.state)}` : task.eligibility === "eligible" ? "Eligible root · not queued" : "Waiting for prerequisites to complete with verified evidence"}</p>
          {dispatch && <p>Capability: {dispatch.required_capability} · attempts {dispatch.attempts} · fencing epoch {dispatch.fence_epoch}</p>}
          {lease && <details><summary>{dispatch?.worker_name ?? "Registered worker"} · {label(lease.state)}</summary><p>Lease ID: {lease.id}</p><p>Worker ID: {lease.worker_id}</p><p>Lease expires: <time dateTime={lease.expires_at}>{new Date(lease.expires_at).toLocaleString()}</time></p><p>{lease.acknowledged_at ? "Worker handoff acknowledged. Awaiting an execution-capable agent." : "Handoff is available. Receipt has not been acknowledged."}</p>{lease.last_heartbeat_at && <p>Last accepted heartbeat: {new Date(lease.last_heartbeat_at).toLocaleString()}. A heartbeat is not useful-work evidence.</p>}</details>}
          {dispatch?.state === "needs_reconciliation" && <p className="architect-warning">Worker ownership ended after acknowledgment. Manual reconciliation is required before safe redispatch.</p>}
          {dispatch?.state === "exhausted" && <p>Unacknowledged claim attempts exhausted. Ask the local operator to review; no task was executed.</p>}
        </li>;
      })}</ul>
    </>}
  </section>;
}
