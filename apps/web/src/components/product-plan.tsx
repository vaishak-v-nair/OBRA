"use client";

import { useCallback, useEffect, useId, useRef, useState, type FormEvent } from "react";
import { Check, Info, FileText, LoaderCircle } from "lucide-react";
import { ApiError, type Project } from "@/lib/api";
import { label, listFields, pm, scalarFields, type Capability, type Plan, type PlanDocument, type PlanSummary, type Run, type Source } from "@/lib/pm";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
import { PlanEditor } from "@/components/plan-editor";

function Evidence({source}: {source:Source}) {
  return <details className="pm-source"><summary>{source.kind === "human" ? "Human edited" : source.kind === "suggested" ? "AI suggestion" : source.kind === "assumption" ? "Assumption" : `From ${source.kind}`}{source.inherited_kind ? ` · originally ${source.inherited_kind}` : ""}</summary>
    {source.quote && <blockquote>{source.quote}</blockquote>}{source.context_key && <p>Context node: {source.context_key}</p>}{source.actor_id && <p>Editor: {source.actor_id}</p>}
  </details>;
}
function ReadDocument({document:doc}: {document:PlanDocument}) {
  return <div className="pm-document">
    <div className="pm-overview-grid">{scalarFields.map(field=><section key={field}><h3>{label(field)}</h3><p>{doc[field].text}</p><Evidence source={doc[field].source}/></section>)}</div>
    {listFields.map(field=>doc[field].length>0 && <section key={field}><h3>{label(field)}</h3><ul>{doc[field].map(item=><li key={item.key}><span>{item.text}</span><Evidence source={item.source}/></li>)}</ul></section>)}
    <section><h3>Epics and user stories</h3>{doc.epics.map(epic=><article className="pm-epic" key={epic.key}><div className="pm-heading"><h4>{epic.title}</h4><span className="status-badge">{epic.priority}</span></div><p>{epic.goal}</p><Evidence source={epic.source}/>
      {epic.stories.map(story=><article className="pm-story" key={story.key}><h5>{story.title} <small>{story.priority}</small></h5><p>{story.statement}</p><p className="form-note">{story.description}</p><Evidence source={story.source}/><p className="pm-reference">Requirements: {story.requirement_refs.join(", ")}{story.dependencies.length>0 && ` · Depends on: ${story.dependencies.join(", ")}`}</p><h6>Acceptance criteria</h6><ol>{story.acceptance_criteria.map(c=><li key={c.key}><p><strong>Given</strong> {c.given}</p><p><strong>When</strong> {c.when}</p><p><strong>Then</strong> {c.then}</p><Evidence source={c.source}/></li>)}</ol></article>)}
    </article>)}</section>
    <section><h3>Items requiring confirmation</h3>{doc.confirmations.length===0 ? <p className="form-note">No confirmation items recorded. Review assumptions and open questions before approval.</p> : doc.confirmations.map(c=><article className="pm-confirmation" key={c.key}><strong>{c.blocking ? "Blocking" : "Advisory"} · {c.disposition}{!c.active && " · Retired"}</strong><p>{c.text}</p>{c.reason && <p>Reason: {c.reason}</p>}{c.decided_at && <p className="form-note">Recorded {new Date(c.decided_at).toLocaleString()} by {c.actor_id}</p>}<Evidence source={c.source}/></article>)}</section>
  </div>;
}

export function ProductPlan({project}: {project:Project}) {  const briefId = useId();  const instructionsId = useId();
  const {user, workspace} = useSession();
  const canWrite = workspace?.role !== "viewer";
  const canApprove = workspace?.role === "owner" || workspace?.role === "admin";
  const [capability, setCapability] = useState<Capability>();
  const [plans, setPlans] = useState<PlanSummary[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [nextPlans, setNextPlans] = useState<number | null>(null);
  const [nextRuns, setNextRuns] = useState<number | null>(null);
  const [plan, setPlan] = useState<Plan>();
  const [loading, setLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);
  const [terminal, setTerminal] = useState<Run>();
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [noticeSuccess, setNoticeSuccess] = useState(false);
  function announce(message:string, confirmed=false) {setNotice(message);setNoticeSuccess(confirmed);}
  const [diagnostic, setDiagnostic] = useState("");
  const [brief, setBrief] = useState(project.description);
  const [instructions, setInstructions] = useState("");
  const [useContext, setUseContext] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<PlanDocument>();
  const [latest, setLatest] = useState<Plan>();
  const [confirmApproval, setConfirmApproval] = useState(false);
  const [pendingId, setPendingId] = useState("");
  const [copyId, setCopyId] = useState("");
  const gate = useRef(false);
  const life = useRef<AbortController | null>(null);
  const current = useRef(0);
  const storageKey = `orba-pm-request:${user?.id}:${project.id}`;
  const copyKey = `${storageKey}:copy`;
  const dirty = !!(editing && draft && plan && JSON.stringify(draft)!==JSON.stringify(plan.document));

  const load = useCallback(async (signal?:AbortSignal, preferred?:string) => {
    const sequence = ++current.current;
    const [p,r] = await Promise.all([pm.plans(project.id, signal),pm.runs(project.id, signal)]);
    const selected = preferred ?? p.items[0]?.id;
    const value = selected ? await pm.plan(project.id, selected, signal) : undefined;
    if (signal?.aborted || sequence !== current.current) return;
    setPlans(p.items); setRuns(r.items); setNextPlans(p.next_offset); setNextRuns(r.next_offset); setCapability(r.capability); setPlan(value); setLoaded(true);
  }, [project.id]);
  useEffect(()=>{
    const controller = new AbortController(); life.current=controller;
    const pending = sessionStorage.getItem(storageKey) ?? ""; const copying = sessionStorage.getItem(copyKey) ?? "";
    Promise.resolve().then(async()=>{if(!controller.signal.aborted){setPendingId(pending);setCopyId(copying);}await load(controller.signal);}).catch((e:unknown)=>{if(!controller.signal.aborted)setError(e instanceof Error?e.message:"Could not load product plans.");}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
    return ()=>{controller.abort();};
  },[load,storageKey,copyKey]);
  useEffect(()=>{ if(!dirty)return; const warn=(e:BeforeUnloadEvent)=>{e.preventDefault();}; window.addEventListener("beforeunload",warn);return()=>window.removeEventListener("beforeunload",warn); },[dirty]);
  const signal = () => life.current?.signal;
  function failed(e:unknown) { if(signal()?.aborted)return; setError(e instanceof Error?e.message:"The operation could not be confirmed."); if(e instanceof ApiError)setDiagnostic([e.runId && `Run ${e.runId}`,e.diagnosticId && `Diagnostic ${e.diagnosticId}`].filter(Boolean).join(" · ")); }
  async function action(name:string, operation:()=>Promise<void>) {
    if(gate.current)return;gate.current=true;setBusy(name);setError("");announce("");setDiagnostic("");
    try{await operation();}catch(e){failed(e);}finally{gate.current=false;if(!signal()?.aborted)setBusy("");}
  }
  function clearPending() { sessionStorage.removeItem(storageKey);setPendingId(""); }
  function ownRequest(run:Run, id:string) {return run.project_id===project.id && run.initiator_id===user?.id && run.client_request_id===id;}
  function ended(run:Run) {return run.status==="failed" || run.status==="interrupted";}
  function runFailure(run:Run) {
    return run.error_category==="provider_timeout"
      ? "Plan generation could not finish because the AI provider timed out. No new plan was saved. Your project and existing plans are safe. No draft was created by this run."
      : `Planning ${run.status}: ${run.error_category?.replaceAll("_"," ") ?? "request did not complete"}. No draft was created by this run.`;
  }
  function rejectedBeforeAdmission(e:unknown) {
    return e instanceof ApiError && (e.code==="project_generation_active" || (!e.runId && (e.code==="request_not_dispatched" ||
      ["generation_admission_limited","context_conflict","context_too_large","input_too_large","validation_error","request_too_large","request_body_timeout"].includes(e.code) || [401,403].includes(e.status))));
  }
  async function generate(e:FormEvent) {
    e.preventDefault(); if(!brief.trim()){setError("Enter a product brief.");return;}
    if(dirty){setError("Save or discard draft changes before generation.");return;}
    if(pendingId && !terminal){setError("Check the existing request before starting another generation.");return;}
    await action("generating",async()=>{
      if(pendingId){
        if(!terminal) return;
        const confirmed=await pm.run(project.id,terminal.id,signal());
        if(!ownRequest(confirmed,pendingId)||!ended(confirmed))throw new Error("The earlier request has not been confirmed as ended. Check status; no retry was sent.");
      }
      const id=crypto.randomUUID(); sessionStorage.setItem(storageKey,id);setPendingId(id);setTerminal(undefined);
      try {
        const run = await pm.generate(project.id,{client_request_id:id,brief:brief.trim(),instructions:instructions.trim(),...(useContext && plan?{context_plan_id:plan.id,context_revision:plan.revision}:{})},signal());
        if(signal()?.aborted)return;
        await load(signal(),run.plan_id??undefined);
        if(run.status==="succeeded")clearPending();
        setEditing(false);setDraft(undefined);
        announce(run.status==="succeeded"?"The model response was validated and saved as a draft. Review it before approval.":"Request recorded. Check status to see its actual result.",run.status==="succeeded");
      } catch(e) {
        if(rejectedBeforeAdmission(e)){
          clearPending();
          // project_generation_active references the EXISTING request, not a
          // newly admitted run. Refresh only history, preserving any open editor.
          if(e instanceof ApiError && e.code==="project_generation_active"){
            const recoverySignal=signal();
            try{const history=await pm.runs(project.id,recoverySignal);if(!recoverySignal?.aborted){setRuns(history.items);setNextRuns(history.next_offset);}}catch{/* The new request's rejection is still confirmed. */}
          }
        }
        else if(e instanceof ApiError && e.runId){
          // A failure response alone does not unlock Retry: confirm the exact own run.
          try {const run=await pm.run(project.id,e.runId,signal());if(ownRequest(run,id)&&ended(run)){setTerminal(run);await load(signal(),plan?.id);}}catch{/* Unknown remains GET-only. */}
        }
        throw e;
      }
    });
  }
  async function checkStatus() {
    await action("checking",async()=>{
      const result=await pm.runs(project.id,signal(),pendingId||undefined);
      const run=result.items.find(r=>ownRequest(r,pendingId));
      let selected=plan?.id;
      if(run?.status==="succeeded")selected=run.plan_id??selected;
      let confirmedCopy=false;
      if(copyId){const copies=await pm.plans(project.id,signal(),0,copyId);if(copies.items[0]){selected=copies.items[0].id;confirmedCopy=true;}}
      // An open editor stays bound to its exact original revision, even before
      // the first local change. Otherwise a refresh could pair old draft content
      // with a newer revision and silently replace a concurrent writer's changes.
      if(editing){const saved=plan?await pm.plan(project.id,plan.id,signal()):undefined;setLatest(saved);setRuns(result.items);}
      else await load(signal(),selected);
      if(pendingId && run){
        if(run.status==="succeeded"){if(!editing)clearPending();announce("The saved product plan was confirmed.",true);}
        else if(ended(run)){setTerminal(run);setError(runFailure(run));setDiagnostic(`Run ${run.id}${run.diagnostic_id?` · Diagnostic ${run.diagnostic_id}`:""}`);}
        else announce(`Planning is ${run.status}. Deadline ${new Date(run.deadline_at).toLocaleTimeString()}. Checking status never starts another model call.`);
      }else if(pendingId)announce("No matching run was found yet. Its outcome remains unconfirmed. Check again before starting another request.");
      else announce("Status refreshed from the server.");
      if(confirmedCopy&&!editing){sessionStorage.removeItem(copyKey);setCopyId("");announce("The saved draft copy was confirmed.",true);}
    });
  }
  async function restoreInput() {
    const candidate=runs.find(r=>ownRequest(r,pendingId))??terminal;
    if(!candidate)return;
    await action("restoring input",async()=>{
      const run=await pm.run(project.id,candidate.id,signal());
      if(!ownRequest(run,pendingId))throw new Error("The submitted input does not belong to this request.");
      if((brief!==project.description||instructions) && !window.confirm("Replace the text in the generation form with this request's submitted brief and instructions?"))return;
      setBrief(run.input_snapshot.brief);setInstructions(run.input_snapshot.instructions);
      const context=run.input_snapshot.context_plan;
      setUseContext(!!context && context.id===plan?.id && context.revision===plan.revision);
      announce("Submitted brief and instructions restored. Review the context selection before generating.");
    });
  }
  async function selectPlan(id:string) {
    if(dirty && !window.confirm("Discard your unsaved draft changes to open another version?"))return;
    await action("loading version",async()=>{const value=await pm.plan(project.id,id,signal());if(signal()?.aborted)return;setPlan(value);setEditing(false);setDraft(undefined);setLatest(undefined);setConfirmApproval(false);});
  }
  async function save(e:FormEvent) {
    e.preventDefault();if(!plan||!draft)return;
    await action("saving",async()=>{const saved=await pm.save(project.id,plan,draft,signal());if(signal()?.aborted)return;setPlan(saved);setDraft(saved.document);setEditing(false);setLatest(undefined);await load(signal(),saved.id);announce(`Draft version ${saved.version}, revision ${saved.revision} saved.`,true);});
  }
  async function approve() { if(!plan)return;await action("approving",async()=>{const saved=await pm.approve(project.id,plan,signal());if(signal()?.aborted)return;setPlan(saved);setConfirmApproval(false);await load(signal(),saved.id);announce(`Version ${saved.version} approved and saved.`,true);}); }
  async function copy() { if(!plan)return;await action("copying",async()=>{const id=copyId||crypto.randomUUID();sessionStorage.setItem(copyKey,id);setCopyId(id);const saved=await pm.copy(project.id,plan,id,signal());if(signal()?.aborted)return;await load(signal(),saved.id);sessionStorage.removeItem(copyKey);setCopyId("");announce("Draft copy saved. This action did not call a model.",true);}); }
  const active = runs.some(r=>r.status==="running"||r.status==="pending");
  return <section className="pm-panel" aria-labelledby="product-plan-heading" id="product-plan">
    <div className="pm-heading"><div><p className="eyebrow">PRODUCT MANAGER</p><h2 id="product-plan-heading"><FileText size={21}/> Product Plan</h2></div><span className="later-label">One planning agent</span></div>
    <p className="section-subtitle">Turn your idea into reviewable requirements. Generation uses your configured AI provider and may incur usage.</p>
    {loading ? <p className="pm-loading" role="status"><LoaderCircle className="animate-spin" size={17}/>Loading saved plans…</p> : <>
      {capability && !capability.configured && <aside className="pm-setup" id="pm-setup"><h3>Configure the Product Manager</h3><p>{capability?.setup_message??"The API could not confirm provider configuration. Check status after reconnecting."}</p><p>Keep credentials on the API server. Set an explicit supported Gemini model. A configured key does not guarantee model access.</p></aside>}
      <details className="pm-generator" open={!plan}><summary>{plan?"Generate another product plan":"Generate product plan"}</summary><form onSubmit={generate} className="pm-fields" aria-label="Generate product plan">
        <div className="pm-field"><label htmlFor={briefId}>Product brief</label><textarea id={briefId} rows={5} required maxLength={10000} value={brief} onChange={e=>setBrief(e.target.value)} disabled={!!busy}/></div>
        <p className="form-note">This brief is saved with the run. It does not change your original project description.</p>
        <div className="pm-field"><label htmlFor={instructionsId}>Additional instructions (optional)</label><textarea id={instructionsId} rows={2} maxLength={4000} value={instructions} onChange={e=>setInstructions(e.target.value)} disabled={!!busy}/></div>
        {plan && <label className="pm-checkbox"><input type="checkbox" checked={useContext} onChange={e=>setUseContext(e.target.checked)} disabled={!!busy}/>Include saved version {plan.version}, revision {plan.revision} as context. Unresolved blockers carry forward.</label>}
        {!canWrite && <p className="form-note">Viewers can read plans. A Member, Admin, or Owner can generate and edit drafts.</p>}
        <Button type="submit" disabled={!loaded||!canWrite||!capability?.configured||!!busy||active||(!!pendingId&&!terminal)||dirty}>{busy==="generating"?<><LoaderCircle size={16} className="animate-spin"/>Waiting for ORBA…</>:(terminal?"Retry generation":"Generate Product Plan")}</Button>
        {terminal && <p className="form-note">Retry starts one new model request and may incur additional usage. The previous failed run remains in history.</p>}
      </form></details>
    </>}
    {busy==="generating" && <p className="pm-loading" role="status">Waiting for ORBA to confirm the result. Leaving this page may not stop provider usage. Return here and check status before submitting again.</p>}
    {error && <div className="error-message" role="alert"><p>{error}</p>{diagnostic && <p className="pm-reference">{diagnostic}</p>}</div>}
    {notice && <p className={noticeSuccess?"pm-notice":"pm-information"} role="status">{noticeSuccess?<Check size={16}/>:<Info size={16}/>} {notice}</p>}
    <div className="pm-actions"><Button type="button" variant="outline" disabled={!!busy} onClick={()=>void checkStatus()}>Check status</Button>{pendingId && <span className="pm-reference">Request {pendingId}</span>}{pendingId && (terminal || runs.some(r=>ownRequest(r,pendingId))) && <Button type="button" variant="outline" disabled={!!busy} onClick={()=>void restoreInput()}>Restore submitted brief</Button>}</div>
    {plan && <div className="pm-saved">
      <div className="pm-heading"><label className="pm-version">Plan version<select aria-label="Plan version" value={plan.id} disabled={!!busy} onChange={e=>void selectPlan(e.target.value)}>{plans.map(p=><option key={p.id} value={p.id}>Version {p.version} · {p.state} · revision {p.revision}</option>)}</select></label><span className="status-badge" data-testid="plan-state">{plan.state}</span></div>
      {nextPlans!==null && <Button type="button" variant="outline" disabled={!!busy} onClick={()=>void action("loading history",async()=>{const more=await pm.plans(project.id,signal(),nextPlans);setPlans(old=>[...old,...more.items]);setNextPlans(more.next_offset);})}>Load earlier versions</Button>}
      <p className="pm-reference">Version {plan.version} · revision {plan.revision} · {plan.origin==="generated"?"AI generated draft":plan.origin==="human_copy"?"Human-created draft copy":"Human-authored plan"}</p>
      {plan.approved_at && <p className="pm-reference">Approved {new Date(plan.approved_at).toLocaleString()} by {plan.approved_by}. This version is immutable.</p>}
      {plan.generation && <details className="pm-evidence"><summary>Generation evidence · {plan.generation.returned_model??"model identifier not returned"}</summary><p>Provider: {plan.generation.provider} · Prompt: {plan.generation.prompt_version}</p><p>Run: {plan.generation.id}</p>{plan.generation.provider_response_id && <p>Response: {plan.generation.provider_response_id}</p>}{plan.generation.provider_request_id && <p>Request: {plan.generation.provider_request_id}</p>}<p>Usage: {plan.generation.usage?JSON.stringify(plan.generation.usage):"Not returned by provider. No estimated cost recorded."}</p><p>Content SHA256: {plan.content_hash}</p></details>}
      {plan.source_plan_id && <p className="pm-reference">Copied from plan {plan.source_plan_id}, revision {plan.source_revision}. Source evidence remains in version history.</p>}
      {plan.inputs && <details className="pm-evidence"><summary>Exact generation input snapshot</summary><h4>{plan.inputs.title}</h4><p>{plan.inputs.description}</p><h4>Brief</h4><p>{plan.inputs.brief}</p>{plan.inputs.instructions && <><h4>Additional instructions</h4><p>{plan.inputs.instructions}</p></>}</details>}
      {editing && draft ? <form onSubmit={save} aria-label="Edit product plan"><PlanEditor document={draft} change={setDraft} disabled={!!busy}/><div className="pm-actions"><Button type="submit" disabled={!!busy}>Save draft</Button><Button type="button" variant="outline" disabled={!!busy} onClick={()=>{if(!dirty||window.confirm("Discard unsaved draft changes?")){setEditing(false);setDraft(undefined);setLatest(undefined);}}}>Cancel editing</Button><Button type="button" variant="outline" disabled={!!busy} onClick={()=>void action("inspecting latest",async()=>{setLatest(await pm.plan(project.id,plan.id,signal()));})}>Inspect latest saved revision</Button></div>{dirty && <p className="form-note" role="status">Unsaved changes. Approval is unavailable until they are saved.</p>}</form> : <><ReadDocument document={plan.document}/><div className="pm-actions">{canWrite && plan.state==="draft" && <Button type="button" disabled={!!busy} onClick={()=>{setDraft(structuredClone(plan.document));setEditing(true);setConfirmApproval(false);}}>Edit draft</Button>}{canApprove && plan.state==="draft" && <Button type="button" variant="outline" disabled={!!busy} onClick={()=>setConfirmApproval(true)}>Approve plan</Button>}{canWrite && plan.state!=="draft" && <Button type="button" variant="outline" disabled={!!busy||!!copyId} onClick={()=>void copy()}>Create draft copy</Button>}</div></>}
      {confirmApproval && !editing && <aside className="pm-approval" aria-label="Confirm plan approval"><h3>Approve version {plan.version}, revision {plan.revision}?</h3><p>Review requirements, suggestions, assumptions, and confirmations. Approval records your identity and time and makes this version immutable. An earlier approval will remain in history.</p><div className="pm-actions"><Button type="button" disabled={!!busy} onClick={()=>void approve()}>Confirm approval</Button><Button type="button" variant="outline" disabled={!!busy} onClick={()=>setConfirmApproval(false)}>Keep as draft</Button></div></aside>}
      {latest && <aside className="pm-approval"><h3>Latest saved revision {latest.revision}</h3><p>Your unsaved draft is preserved above. Compare it with the saved document below.</p><ReadDocument document={latest.document}/><Button type="button" variant="outline" disabled={!!busy} onClick={()=>{if(window.confirm("Discard your local edits and use the latest saved revision?")){setPlan(latest);setDraft(structuredClone(latest.document));setLatest(undefined);}}}>Use latest and discard my edits</Button></aside>}
    </div>}
    {loaded && !loading && !plan && !pendingId && <div className="pm-empty"><h3>Your requirements start here</h3><p>Generate a plan from your brief to review epics, stories, and testable acceptance criteria. No model call happens until you choose Generate Product Plan.</p></div>}
    {loaded && <details className="pm-history"><summary>Planning run history ({runs.length})</summary>{runs.length===0?<p className="form-note">No planning runs recorded.</p>:<ul>{runs.map(run=><li key={run.id}><strong>{run.status}</strong> · {new Date(run.created_at).toLocaleString()}<p className="pm-reference">{run.id} · {run.returned_model??run.requested_model??"No model configured"}{run.error_category?` · ${run.error_category.replaceAll("_"," ")}`:""}</p>{run.plan_id && <button type="button" disabled={!!busy} onClick={()=>void selectPlan(run.plan_id!)}>Open resulting plan</button>}</li>)}</ul>}{nextRuns!==null && <Button type="button" variant="outline" disabled={!!busy} onClick={()=>void action("loading runs",async()=>{const more=await pm.runs(project.id,signal(),undefined,nextRuns);setRuns(old=>[...old,...more.items]);setNextRuns(more.next_offset);})}>Load earlier runs</Button>}</details>}
  </section>;
}
