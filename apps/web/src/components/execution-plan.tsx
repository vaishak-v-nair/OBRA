"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Workflow } from "lucide-react";
import { ApiError, type Project } from "@/lib/api";
import type { ArchitectureSummary } from "@/lib/architect";
import { orchestration, type OrchestrationRun, type RunDetail, type RunEvent, type RunInput } from "@/lib/orchestration";
import { ExecutionGraph } from "@/components/execution-graph";
import { SchedulerStatus } from "@/components/scheduler-status";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";

export function ExecutionPlan({ project, onArchitecture }: { project: Project; onArchitecture: () => void }) {
  const { user, workspace } = useSession();
  return <ExecutionPlanBody key={`${user?.id}:${workspace?.id}:${project.id}`} project={project} onArchitecture={onArchitecture} />;
}

function ExecutionPlanBody({ project, onArchitecture }: { project: Project; onArchitecture: () => void }) {
  const { user, workspace } = useSession();
  const writable = !!workspace && workspace.role !== "viewer";
  const identity = `${user?.id}:${workspace?.id}:${project.id}`;
  const storage = `orba-orchestration-request:${identity}`;
  const [loadedIdentity, setLoadedIdentity] = useState("");
  const [source, setSource] = useState<ArchitectureSummary | null>(null);
  const [sourceError, setSourceError] = useState("");
  const [history, setHistory] = useState<OrchestrationRun[]>([]);
  const [nextOffset, setNextOffset] = useState<number | null>(null);
  const [run, setRun] = useState<RunDetail>();
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [nextSequence, setNextSequence] = useState<number | null>(null);
  const [pending, setPending] = useState("");
  const pendingInput = useRef<RunInput | null>(null);
  const [canRetry, setCanRetry] = useState(false);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [confirm, setConfirm] = useState(false);
  const gate = useRef(false), life = useRef<AbortController | null>(null), sequence = useRef(0);
  const alert = useRef<HTMLDivElement>(null), dialog = useRef<HTMLDialogElement>(null), cancelButton = useRef<HTMLButtonElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const signal = () => life.current?.signal;
  const selectRun = useCallback(async (id: string, abort?: AbortSignal) => {
    const ticket = ++sequence.current;
    const [saved, ledger] = await Promise.all([orchestration.get(project.id, id, abort), orchestration.events(project.id, id, abort)]);
    if (abort?.aborted || ticket !== sequence.current) return;
    setRun(saved); setEvents(ledger.items); setNextSequence(ledger.next_sequence); setConfirm(false);
  }, [project.id]);
  const load = useCallback(async (abort?: AbortSignal) => {
    // A stale current source must not hide immutable historical runs.
    const [records, approved] = await Promise.all([orchestration.list(project.id, abort), orchestration.source(project.id, abort).then(value => ({ value, error: "" })).catch((e: unknown) => ({ value: null, error: e instanceof Error ? e.message : "The approved architecture could not be loaded." }))]);
    if (abort?.aborted) return;
    setHistory(records.items); setNextOffset(records.next_offset); setSource(approved.value); setSourceError(approved.error);
    if (records.items[0]) await selectRun(records.items[0].id, abort);
  }, [project.id, selectRun]);
  useEffect(() => {
    const controller = new AbortController(); life.current = controller;
    Promise.resolve().then(async () => { if (controller.signal.aborted) return; const stored = sessionStorage.getItem(storage); if (stored) { try { const value = JSON.parse(stored) as RunInput; if (!/^[0-9a-f-]{36}$/.test(value.client_request_id) || !/^[0-9a-f-]{36}$/.test(value.architecture_id) || !Number.isSafeInteger(value.architecture_version) || value.architecture_version < 1 || !Number.isSafeInteger(value.architecture_revision) || value.architecture_revision < 1) throw new Error("Invalid saved request reference"); pendingInput.current = value; setPending(value.client_request_id); } catch { sessionStorage.removeItem(storage); } } await load(controller.signal); if (!controller.signal.aborted) setLoadedIdentity(identity); }).catch((e: unknown) => { if (!controller.signal.aborted) { setError(e instanceof Error ? e.message : "Execution plans could not load."); setLoadedIdentity(identity); } }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => { controller.abort(); };
  }, [identity, storage, load]);
  useEffect(() => { if (error) alert.current?.focus(); }, [error]);
  useEffect(() => { if (notice) heading.current?.focus(); }, [notice]);
  useEffect(() => { if (confirm) dialog.current?.showModal(); else dialog.current?.close(); }, [confirm]);
  async function action(operation: () => Promise<void>) {
    if (gate.current) return; gate.current = true; setBusy(true); setError(""); setNotice("");
    try { await operation(); } catch (e) { if (!signal()?.aborted) setError(e instanceof Error ? e.message : "The saved state could not be confirmed. Refresh before another action."); }
    finally { gate.current = false; if (!signal()?.aborted) setBusy(false); }
  }
  function clearPending() { sessionStorage.removeItem(storage); pendingInput.current = null; setPending(""); setCanRetry(false); }
  async function submit(input: RunInput) {
    try {
      const saved = await orchestration.create(project.id, input, signal());
      if (signal()?.aborted) return;
      clearPending(); setRun(saved); setHistory(old => [saved, ...old.filter(item => item.id !== saved.id)]); await selectRun(saved.id, signal());
      setNotice("Orchestration plan created. Engineering tasks are awaiting an execution agent. No code has been run.");
    } catch (e) {
      if (e instanceof ApiError && ((e.status >= 400 && e.status < 500) || e.code === "request_not_dispatched")) clearPending();
      throw e;
    }
  }
  async function create() {
    if (!source || pending) return;
    const input = { client_request_id: crypto.randomUUID(), architecture_id: source.id, architecture_version: source.version, architecture_revision: source.revision };
    // Only nonsecret request/source identifiers; never an authentication authority or snapshot.
    pendingInput.current = input; sessionStorage.setItem(storage, JSON.stringify(input)); setPending(input.client_request_id);
    await submit(input);
  }
  async function recover() {
    const records = await orchestration.list(project.id, signal(), pending);
    if (signal()?.aborted) return;
    if (records.items.length) { await load(signal()); await selectRun(records.items[0].id, signal()); clearPending(); setNotice("The original saved run was recovered by request ID. No creation request was repeated."); }
    else { setCanRetry(true); setNotice("No saved run was found. You may explicitly retry the original creation with the same request ID and source binding. ORBA will reuse an existing run if the original request later commits."); }
  }
  function closeConfirmation() { setConfirm(false); cancelButton.current?.focus(); }
  if (loading || loadedIdentity !== identity) return <section className="architect-panel" aria-label="Execution Plan"><p role="status">Loading saved execution plans…</p></section>;
  return <section className="architect-panel execution-panel" aria-label="Execution Plan">
    <div className="pm-heading"><h2 ref={heading} tabIndex={-1}><Workflow size={23} />Execution Plan</h2><span className="status-badge">Control plane · no execution</span></div>
    <p>No code has been run. Create a durable snapshot of your approved architecture for a future execution agent.</p>
    {error && <div className="architect-error" role="alert" ref={alert} tabIndex={-1}>{error}</div>}
    {notice && <p role="status" className="architect-warning">{notice}</p>}
    {sourceError && <p role="alert" className="architect-warning">{sourceError}</p>}
    <div className="architect-source">{source ? <><h3>Approved source architecture</h3><p>{source.id} · v{source.version} / r{source.revision}</p><p className="form-note">Product Plan {source.source_plan_id} · v{source.source_version} / r{source.source_revision}</p></> : <><h3>Approve an architecture first</h3><p>A run requires a validated, approved architecture bound to the current approved Product Plan.</p></>}
      <div className="pm-actions"><Button variant="outline" onClick={onArchitecture}>Review architecture</Button>{writable ? <Button disabled={!source || busy || !!pending} onClick={() => void action(create)}>Create orchestration run</Button> : <p className="form-note">Viewer access: inspect saved plans. Creating or cancelling a run requires Member, Admin or Owner permissions.</p>}<Button variant="outline" disabled={busy} onClick={() => void action(async () => { await load(signal()); })}>Refresh execution plans</Button></div>
    </div>
    {pending && <div className="architect-warning"><p>A creation request is unconfirmed. Do not submit another run until its outcome is resolved.</p><p className="form-note">Request ID: {pending}</p><Button disabled={busy} variant="outline" onClick={() => void action(recover)}>Check creation status</Button>{canRetry && <Button disabled={busy || !writable} variant="outline" onClick={() => void action(async () => { if (pendingInput.current) { setCanRetry(false); await submit(pendingInput.current); } })}>Retry original creation</Button>}</div>}
    {history.length > 0 && <div className="form-field"><label htmlFor={`orchestration-history-${project.id}`}>Saved orchestration run</label><select id={`orchestration-history-${project.id}`} value={run?.id ?? ""} disabled={busy} onChange={event => void action(() => selectRun(event.target.value, signal()))}>{history.map(item => <option key={item.id} value={item.id}>{item.id} · {item.status.replaceAll("_", " ")}</option>)}</select>{nextOffset !== null && <Button variant="outline" disabled={busy} onClick={() => void action(async () => { const page = await orchestration.list(project.id, signal(), undefined, nextOffset); if (!signal()?.aborted) { setHistory(old => [...old, ...page.items]); setNextOffset(page.next_offset); } })}>Load older runs</Button>}</div>}
    {run ? <div data-testid="saved-orchestration-run" data-run-id={run.id} data-source-id={run.architecture_id}>
      <h3>Saved run <span data-testid="orchestration-state">{run.status.replaceAll("_", " ")}</span></h3><p>Run ID: <strong>{run.id}</strong></p><p>Architecture v{run.architecture_version} / r{run.architecture_revision} · Product Plan v{run.source_version} / r{run.source_revision}</p>
      {!run.source_current && <p className="architect-warning">This immutable run references an earlier approved source. It has not been rebased.</p>}
      <p className="form-note">Run revision {run.revision}. No executor, artifacts, tests or completion evidence exist.</p>
      <details><summary>Source binding and snapshot checksum</summary><p>Architecture: {run.architecture_id}</p><p>Product Plan: {run.source_plan_id}</p><p>{run.hash_version}: {run.snapshot_hash}</p></details>
      <ExecutionGraph key={run.id} run={run} />
      <SchedulerStatus key={`scheduler-${run.id}`} run={run} />
      <section aria-label="Orchestration event history"><h3>Recorded event history</h3><ol className="execution-events">{events.map(event => <li key={event.id} data-event-sequence={event.sequence}><strong>#{event.sequence} {event.event_type.replaceAll("_", " ")}</strong><p><time dateTime={event.occurred_at}>{new Date(event.occurred_at).toLocaleString()}</time> · {event.actor_type}{event.actor_id ? ` ${event.actor_id}` : ""} · run revision {event.run_revision}</p><p>{event.previous_state?.replaceAll("_", " ") ?? "No previous state"} → {event.new_state.replaceAll("_", " ")}{event.task_id ? ` · task ${event.task_id}` : ""}</p></li>)}</ol>{nextSequence !== null && <Button variant="outline" disabled={busy} onClick={() => void action(async () => { const page = await orchestration.events(project.id, run.id, signal(), nextSequence); if (!signal()?.aborted) { setEvents(old => [...old, ...page.items]); setNextSequence(page.next_sequence); } })}>Load more events</Button>}</section>
      {writable && run.status === "awaiting_executor" && <Button ref={cancelButton} variant="outline" disabled={busy} onClick={() => setConfirm(true)}>Cancel orchestration run</Button>}
      <dialog ref={dialog} aria-label="Confirm orchestration cancellation" onCancel={() => setConfirm(false)} onClose={() => { setConfirm(false); cancelButton.current?.focus(); }}><h3>Cancel run {run.id}?</h3><p>This cancels the saved plan for future dispatch. No code has been run. The immutable snapshot and event history remain available.</p><div className="pm-actions"><Button autoFocus variant="outline" onClick={closeConfirmation} disabled={busy}>Keep run</Button><Button disabled={busy} onClick={() => void action(async () => { try { const saved = await orchestration.cancel(project.id, run, signal()); if (!signal()?.aborted) { setRun(saved); await selectRun(saved.id, signal()); setNotice("Cancellation was saved. No task was executed."); setConfirm(false); } } finally { if (!signal()?.aborted) setConfirm(false); } })}>Confirm cancellation</Button></div></dialog>
    </div> : <div className="state-box"><h3>No orchestration runs yet</h3><p>Your approved engineering plan can be saved here. Engineering tasks remain unexecuted. A local operator starts scheduling independently of this page.</p></div>}
  </section>;
}
