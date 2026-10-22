"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { createPortal } from "react-dom";
import { useRouter } from "next/navigation";
import { Layers3, LoaderCircle, Network } from "lucide-react";
import { ApiError, type Project } from "@/lib/api";
import { architect, type Architecture as SavedArchitecture, type ArchitectureDocument, type ArchitectCapability, type ArchitectRun, type ArchitectureSummary, type Json } from "@/lib/architect";
import { label, type Plan } from "@/lib/pm";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
import { ArchitectureEditor, architectureFieldId, ProposalValue } from "@/components/architecture-editor";
import { TaskGraph } from "@/components/task-graph";

export function Architecture({project,view,active,onProductPlan}:{project:Project;view:"architecture"|"graph";active:boolean;onProductPlan:()=>void}) {
  const {user,workspace}=useSession();
  const router=useRouter();
  const writable=workspace?.role!=="viewer", approver=workspace?.role==="owner"||workspace?.role==="admin";
  const [source,setSource]=useState<Plan|null>(null);
  const [value,setValue]=useState<SavedArchitecture>();
  const [history,setHistory]=useState<ArchitectureSummary[]>([]);
  const [runs,setRuns]=useState<ArchitectRun[]>([]);
  const [capability,setCapability]=useState<ArchitectCapability>();
  const [loading,setLoading]=useState(true),[loaded,setLoaded]=useState(false),[busy,setBusy]=useState("");
  const [error,setError]=useState(""),[notice,setNotice]=useState("");
  const [details,setDetails]=useState<{field:string;message:string}[]>([]);
  const [constraints,setConstraints]=useState("");
  const [editing,setEditing]=useState(false),[draft,setDraft]=useState<ArchitectureDocument>();
  const [latest,setLatest]=useState<SavedArchitecture>();
  const [pending,setPending]=useState(""),[copyPending,setCopyPending]=useState("");
  const [terminal,setTerminal]=useState<ArchitectRun>();
  const [confirm,setConfirm]=useState(false),[ack,setAck]=useState<Record<string,string>>({});
  const [leaving,setLeaving]=useState<(()=>void)|null>(null);
  const errorBox=useRef<HTMLDivElement>(null),gate=useRef(false),life=useRef<AbortController|null>(null),sequence=useRef(0);
  const navigationDialog=useRef<HTMLDialogElement>(null);
  const storage=`orba-architect-request:${user?.id}:${project.id}`;
  const copyStorage=`${storage}:copy`;
  const dirty=!!(editing&&draft&&value&&JSON.stringify(draft)!==JSON.stringify(value.document));
  const sourceCurrent=!!(source&&value&&source.id===value.source_plan_id&&source.version===value.source_version&&source.revision===value.source_revision&&source.content_hash===value.source_hash);
  const signal=()=>life.current?.signal;
  const own=(run:ArchitectRun,id:string)=>run.project_id===project.id&&run.initiator_id===user?.id&&run.client_request_id===id;
  const ended=(run:ArchitectRun)=>run.status==="failed"||run.status==="interrupted";
  const load=useCallback(async(abort?:AbortSignal,preferred?:string)=>{
    const current=++sequence.current;
    const [plans,records,approved]=await Promise.all([architect.list(project.id,abort),architect.runs(project.id,abort),architect.source(project.id,abort)]);
    const selected=preferred??plans.items[0]?.id;
    const artifact=selected?await architect.get(project.id,selected,abort):undefined;
    if(abort?.aborted||current!==sequence.current)return;
    setSource(approved);setHistory(plans.items);setRuns(records.items);setCapability(records.capability);setValue(artifact);setLoaded(true);
  },[project.id]);
  useEffect(()=>{
    const controller=new AbortController();life.current=controller;
    Promise.resolve().then(async()=>{if(controller.signal.aborted)return;setPending(sessionStorage.getItem(storage)??"");setCopyPending(sessionStorage.getItem(copyStorage)??"");await load(controller.signal);}).catch((e:unknown)=>{if(!controller.signal.aborted)setError(e instanceof Error?e.message:"Architecture could not be loaded.");}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
    return()=>controller.abort();
  },[load,storage,copyStorage]);
  useEffect(()=>{if(error)errorBox.current?.focus();},[error]);
  useEffect(()=>{const dialog=navigationDialog.current;if(leaving&&!dialog?.open)dialog?.showModal();return()=>dialog?.close();},[leaving]);
  useEffect(()=>{if(!active||!loaded)return;const controller=new AbortController();architect.source(project.id,controller.signal).then(setSource).catch(()=>{/* Explicit refresh reports connectivity errors; never erase the last source. */});return()=>controller.abort();},[active,loaded,project.id]);
  useEffect(()=>{
    if(!dirty)return;
    const warn=(event:BeforeUnloadEvent)=>event.preventDefault();
    const navigate=(event:Event)=>{const custom=event as CustomEvent<()=>void>;event.preventDefault();setLeaving(()=>custom.detail);};
    const link=(event:MouseEvent)=>{const anchor=(event.target as HTMLElement).closest("a");if(!anchor||event.defaultPrevented||event.metaKey||event.ctrlKey||anchor.target==="_blank")return;const url=new URL(anchor.href);if(url.origin===location.origin&&url.pathname!==location.pathname){event.preventDefault();event.stopPropagation();setLeaving(()=>()=>router.push(url.pathname+url.search+url.hash));}};
    window.addEventListener("beforeunload",warn);window.addEventListener("orba-draft-navigation",navigate);document.addEventListener("click",link,true);
    return()=>{window.removeEventListener("beforeunload",warn);window.removeEventListener("orba-draft-navigation",navigate);document.removeEventListener("click",link,true);};
  },[dirty,router]);
  function fail(e:unknown) {if(signal()?.aborted)return;setError(e instanceof Error?e.message:"The operation could not be confirmed.");if(e instanceof ApiError)setDetails([...e.details,...(e.runId?[{field:"run",message:`Run ${e.runId}${e.diagnosticId?` · Diagnostic ${e.diagnosticId}`:""}`}]:[])]);}
  async function action(name:string,operation:()=>Promise<void>) {if(gate.current)return;gate.current=true;setBusy(name);setError("");setDetails([]);setNotice("");try{await operation();}catch(e){fail(e);}finally{gate.current=false;if(!signal()?.aborted)setBusy("");}}
  function clearPending(){sessionStorage.removeItem(storage);setPending("");setTerminal(undefined);}
  function accept(saved:SavedArchitecture){setValue(saved);setDraft(undefined);setEditing(false);setLatest(undefined);setConfirm(false);setAck({});setHistory(old=>[saved,...old.filter(item=>item.id!==saved.id)].sort((a,b)=>b.version-a.version));}
  function failureMessage(run:ArchitectRun){return run.error_category==="provider_timeout"?"Architecture generation could not finish because the AI provider timed out. No new architecture was saved. Your project and existing plans are safe.":`Architecture generation ${run.status}: ${run.error_category?.replaceAll("_"," ")??"request did not complete"}. No new architecture was saved. No architecture was created by this run.`;}
  async function generate(event:FormEvent){event.preventDefault();if(!source||dirty)return;
    await action("generating",async()=>{
      if(pending){if(!terminal)throw new Error("Check the existing request before starting another generation.");const confirmed=await architect.run(project.id,terminal.id,signal());if(!own(confirmed,pending)||!ended(confirmed))throw new Error("The original request has not ended. No new request was sent.");}
      const id=crypto.randomUUID();sessionStorage.setItem(storage,id);setPending(id);setTerminal(undefined);
      try{const run=await architect.generate(project.id,source,constraints,id,signal());if(signal()?.aborted)return;if(run.status==="succeeded"){await load(signal(),run.architecture_id??undefined);clearPending();setEditing(false);setDraft(undefined);setNotice("The real response was validated and saved as a draft. Review the proposal; no engineering task has been executed.");}else setNotice(`Architect request is ${run.status}. Check status; no second request will be sent.`);}
      catch(e){if(e instanceof ApiError){if(e.code==="project_generation_active"||e.code==="request_not_dispatched"||(!e.runId&&[401,403,404,409,413,422,429].includes(e.status)))clearPending();else if(e.runId){try{const run=await architect.run(project.id,e.runId,signal());if(own(run,id)&&ended(run))setTerminal(run);}catch{/* GET-only recovery remains available. */}}}throw e;}
    });
  }
  async function checkStatus(){await action("checking status",async()=>{
    const records=await architect.runs(project.id,signal(),pending||undefined);setRuns(records.items);
    const run=records.items.find(item=>own(item,pending));
    if(copyPending){const copies=await architect.list(project.id,signal(),0,copyPending);if(copies.items[0]&&!editing){accept(await architect.get(project.id,copies.items[0].id,signal()));sessionStorage.removeItem(copyStorage);setCopyPending("");setNotice("The saved draft copy was independently confirmed.");}}
    if(editing&&value)setLatest(await architect.get(project.id,value.id,signal()));
    else if(run?.status==="succeeded"){await load(signal(),run.architecture_id??undefined);clearPending();setNotice("Saved architecture confirmed by GET.");}
    else {setSource(await architect.source(project.id,signal()));if(value){const fresh=await architect.get(project.id,value.id,signal());setValue(fresh);}}
    if(run&&ended(run)){setTerminal(run);setError(failureMessage(run));}
    else if(pending&&run)setNotice(`Architect request is ${run.status}. Checking status never generates again.`);
    else if(pending)setNotice("No matching run is confirmed yet. Keep this request reference and check again; no retry was sent.");
  });}
  async function save():Promise<boolean>{if(!value||!draft)return false;try{const saved=await architect.save(project.id,value,draft,signal());if(signal()?.aborted)return false;accept(saved);setNotice("Human edits saved to PostgreSQL.");return true;}catch(e){if(e instanceof ApiError&&e.status===409){try{setLatest(await architect.get(project.id,value.id,signal()));}catch{/* Retain both local draft and error. */}}throw e;}}
  function focusField(field:string){const path=field.replace(/^body\.document\.?/,"");const element=document.getElementById(architectureFieldId(path));if(element){let parent=element.parentElement;while(parent){if(parent instanceof HTMLDetailsElement)parent.open=true;parent=parent.parentElement;}element.focus();element.scrollIntoView({block:"center"});}}
  const currentDraft=draft??value?.document;
  return <section className="architect-panel" aria-label={view==="graph"?"Task Graph workspace":"Architecture workspace"}>
    <div className="pm-heading"><div><p className="eyebrow">TECHNICAL PLANNING</p><h2>{view==="graph"?<Network size={22}/>:<Layers3 size={22}/>} {view==="graph"?"Task Graph":"Architecture"}</h2></div><span className="status-badge">Proposals · not implemented</span></div>
    {error&&<div role="alert" tabIndex={-1} ref={errorBox} className="architect-error"><p>{error}</p>{details.length>0&&<ul>{details.map((item,index)=><li key={index}><button type="button" onClick={()=>focusField(item.field)}>{item.message}</button></li>)}</ul>}</div>}
    {notice&&<p role="status" className="pm-notice">{notice}</p>}
    {loading?<p role="status"><LoaderCircle className="animate-spin"/>Loading saved architecture and approved source…</p>:!loaded?<Button variant="outline" onClick={()=>void action("loading",()=>load(signal()))}>Retry loading architecture</Button>:<>
      <div className="architect-source"><strong>Current approved Product Plan</strong>{source?<><p>{source.document.product_name.text} · v{source.version} / r{source.revision}</p><button type="button" className="text-action" onClick={onProductPlan}>Open Product Plan</button></>:<><p>Approve a Product Plan before requesting architecture. Draft requirements cannot be used as approved work.</p><Button variant="outline" onClick={onProductPlan}>Review Product Plan</Button></>}</div>
      {writable?<form onSubmit={event=>void generate(event)} className="architect-generation"><label htmlFor="architect-constraints">Optional architectural constraints</label><textarea id="architect-constraints" value={constraints} onChange={event=>setConstraints(event.target.value)} maxLength={4000} rows={3} placeholder="For example: keep the first release deployable on one server."/><p className="form-note">Generation sends the exact approved PRD and these constraints to the configured model. It may incur provider usage. Nothing executes your proposed tasks.</p>{!capability?.configured&&<p id="architect-setup" className="architect-warning">{capability?.setup_message??"Architect provider configuration is unavailable."}</p>}<div className="pm-actions"><Button type="submit" disabled={!!busy||!source||!capability?.configured||dirty||!!copyPending||!!(pending&&!terminal)}>{busy==="generating"?"Generating architecture…":terminal?"Retry architecture generation":"Generate Architecture"}</Button><Button type="button" variant="outline" disabled={!!busy} onClick={()=>void checkStatus()}>Check architecture status</Button>{pending&&<Button type="button" variant="outline" disabled={!!busy||!terminal} onClick={()=>void action("restoring constraints",async()=>{if(!terminal)return;const saved=await architect.run(project.id,terminal.id,signal());if(!own(saved,pending))throw new Error("The input belongs to another request.");setConstraints(saved.input_snapshot.constraints);setNotice("Constraints restored from your authorized saved run.");})}>Restore submitted constraints</Button>}</div>{pending&&<p className="form-note">Request reference: {pending}. Status recovery uses GET only.</p>}</form>:<p className="form-note">Viewer access: you may inspect saved proposals. Generating and editing require Member, Admin or Owner; approval requires Admin or Owner.</p>}
      {value&&currentDraft?<>
        <div className="architect-review"><div className="pm-heading"><h3>Architecture v{value.version} / r{value.revision}</h3><span className="status-badge" data-testid="architecture-state">{value.state}</span></div><p>Generated against Product Plan v{value.source_version} / r{value.source_revision} · {sourceCurrent?"Current approved source":"Earlier source — review a new architecture before approval"}</p>{!sourceCurrent&&<p className="architect-warning">A newer PRD is approved. This architecture retains its original source; copying it does not rebase it.</p>}<p>{dirty?"Unsaved local draft — graph and coverage require validation on Save.":`Saved graph validated · ${value.coverage.covered_stories.length} linked stories · ${value.coverage.unaccounted_gaps.length} unaccounted gaps`}</p><p className="form-note">{value.coverage.meaning}</p>{value.generation&&<p className="form-note">Model requested: {value.generation.requested_model??"not configured"} · returned: {value.generation.returned_model??"not returned"} · Run {value.generation.id}</p>}{value.approved_at&&<p>Approved {new Date(value.approved_at).toLocaleString()} by {value.approved_by}</p>}
        <div className="pm-actions">{writable&&value.state==="draft"&&!editing&&<Button variant="outline" disabled={!!busy||!!copyPending} onClick={()=>{setDraft(structuredClone(value.document));setEditing(true);setConfirm(false);}}>Edit architecture draft</Button>}{editing&&<><Button disabled={!!busy} onClick={()=>void action("saving",async()=>{await save();})}>Save architecture draft</Button><Button variant="outline" disabled={!!busy} onClick={()=>{setDraft(undefined);setEditing(false);setLatest(undefined);setDetails([]);}}>Discard architecture edits</Button></>}{writable&&value.state!=="draft"&&<Button variant="outline" disabled={!!busy||!!copyPending||!!pending} onClick={()=>void action("copying draft",async()=>{const id=crypto.randomUUID();sessionStorage.setItem(copyStorage,id);setCopyPending(id);try{const saved=await architect.copy(project.id,value,id,signal());accept(saved);sessionStorage.removeItem(copyStorage);setCopyPending("");setNotice("A human draft copy was saved. The approved version remains immutable.");}catch(e){if(e instanceof ApiError&&[401,403,404,409,422].includes(e.status)){sessionStorage.removeItem(copyStorage);setCopyPending("");}throw e;}})}>Create architecture draft copy</Button>}{approver&&value.state==="draft"&&<Button disabled={!!busy||dirty||editing||!sourceCurrent||!value.coverage.approvable} onClick={()=>{setConfirm(true);setAck({});}}>Review architecture approval</Button>}</div>
        {latest&&<div className="architect-warning"><h4>Latest saved revision: r{latest.revision}</h4><p>Your editor remains bound to r{value.revision}. Local input has not been overwritten.</p><details><summary>Compare latest saved proposal</summary><ProposalValue value={latest.document as unknown as Json}/></details></div>}
        <details><summary>Coverage and review obligations</summary><p>Unaccounted gaps: {value.coverage.unaccounted_gaps.map(item=>item.id).join(", ")||"None"}</p><p>Tasks without clear source links: {value.coverage.orphan_tasks.join(", ")||"None"}</p><p>Component trace gaps: {value.coverage.component_gaps.join(", ")||"None"}</p><p>Needs clarification: {value.coverage.needs_clarification.join(", ")||"None"}</p>{value.coverage.review_obligations.map(item=><p key={item.id}><strong>{item.id}</strong>: {item.reason}</p>)}</details>
        <details><summary>Review exact source Product Plan v{value.source_version} / r{value.source_revision}</summary><ProposalValue value={value.source_document as unknown as Json}/></details>
        <details><summary>Inherited source assumptions, risks and questions</summary>{[...value.source_document.assumptions,...value.source_document.risks,...value.source_document.open_questions,...value.source_document.confirmations].map(item=><p key={item.key}>{item.text} <small>({item.source.kind})</small></p>)}</details></div>
        {confirm&&<div role="group" aria-label="Confirm architecture approval" className="architect-approval"><h3>Approve v{value.version} / r{value.revision}</h3><p>This approves the saved technical proposal and planning graph. It does not certify implementation, testing or deployment.</p>{value.coverage.review_obligations.map(item=><div className="form-field" key={item.id}><label htmlFor={`ack-${item.id}`}>{item.reason} — record your review disposition</label><textarea id={`ack-${item.id}`} value={ack[item.id]??""} onChange={event=>setAck({...ack,[item.id]:event.target.value})} maxLength={2000}/></div>)}<div className="pm-actions"><Button disabled={!!busy||value.coverage.review_obligations.some(item=>!ack[item.id]?.trim())} onClick={()=>void action("approving",async()=>{accept(await architect.approve(project.id,value,ack,signal()));setNotice("The exact saved architecture version was approved and persisted.");})}>Confirm architecture approval</Button><Button variant="outline" onClick={()=>setConfirm(false)}>Cancel approval</Button></div></div>}
        {view==="graph"?<TaskGraph document={currentDraft} graph={value.graph} editable={editing&&!busy} dirty={dirty} onChange={setDraft}/>:editing?<ArchitectureEditor key={`${value.id}:${value.revision}`} document={currentDraft} onChange={setDraft} errors={details}/>:<div className="architect-proposal"><h3>{value.document.overview.title}</h3>{Object.entries(value.document).filter(([key])=>key!=="schema_version").map(([key,item])=><details key={key} open={key==="overview"}><summary>{label(key)}{key==="api_design"||key==="database_design"?" · Proposed":""}</summary><ProposalValue value={item as Json}/></details>)}</div>}
      </>:<div className="state-box"><Layers3 size={28}/><h3>No architecture yet</h3><p>Generate a technical proposal from an approved Product Plan. Engineering tasks and dependencies will be saved for human review.</p><p className="form-note">No architecture, task execution or delivery evidence has been fabricated.</p></div>}
      <details className="architect-history"><summary>Architecture versions and real runs</summary>{history.length===0?<p>No saved versions.</p>:history.map(item=><Button key={item.id} variant="outline" disabled={!!busy||dirty||editing} onClick={()=>void action("opening version",async()=>accept(await architect.get(project.id,item.id,signal())))}>Architecture v{item.version} / r{item.revision} · {item.state}</Button>)}<ul>{runs.map(run=><li key={run.id}>{run.status} · {run.requested_model??"unconfigured"} · source v{run.source_version}/r{run.source_revision} · {run.error_category??"no failure recorded"} · {run.id}</li>)}</ul></details>
    </>}
    {leaving&&createPortal(<dialog ref={navigationDialog} aria-label="Unsaved architecture changes" className="architect-navigation" onCancel={()=>setLeaving(null)}><h3>Save architecture changes before leaving?</h3><p>Your local draft has unsaved edits.</p>{error&&<p role="alert" className="architect-error">{error}</p>}<div className="pm-actions"><Button disabled={!!busy} onClick={()=>void action("saving",async()=>{if(await save()){const go=leaving;setLeaving(null);go();}})}>Save and leave</Button><Button variant="outline" disabled={!!busy} onClick={()=>{const go=leaving;setLeaving(null);setDraft(undefined);setEditing(false);go();}}>Discard and leave</Button><Button variant="outline" onClick={()=>setLeaving(null)}>Cancel navigation</Button></div></dialog>,document.body)}
  </section>;
}
