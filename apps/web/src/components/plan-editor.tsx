"use client";

import { Button } from "@/components/ui/button";
import { useId } from "react";
import { label, listFields, scalarFields, type PlanDocument, type Priority, type Source, type Statement } from "@/lib/pm";

const newKey = (prefix: string) => `${prefix}_${crypto.randomUUID().replaceAll("-", "").slice(0, 12)}`;
const human: Source = {kind:"human"}; // Actual actor/provenance is assigned by the server on save.
const newStatement = (): Statement => ({key:newKey("req"), text:"", source:{...human}});
function Text({name, value, change, max = 2000}: {name:string; value:string; change:(s:string)=>void; max?:number}) {
  const id = useId();
  return <div className="pm-field"><label htmlFor={id}>{name}</label><textarea id={id} required rows={2} maxLength={max} value={value} onChange={(e) => change(e.target.value)} /></div>;
}
function PriorityField({name, value, change}: {name:string; value:Priority; change:(s:Priority)=>void}) {
  return <label>{name}<select value={value} onChange={(e)=>change(e.target.value as Priority)}>{["P0","P1","P2","P3"].map(p=><option key={p}>{p}</option>)}</select></label>;
}

export function PlanEditor({document: doc, change, disabled}: {document:PlanDocument; change:(d:PlanDocument)=>void; disabled:boolean}) {
  function edit(fn:(draft:PlanDocument)=>void) { const next = structuredClone(doc); fn(next); change(next); }
  const stories = doc.epics.flatMap(e=>e.stories);
  const requirements = [...doc.functional_requirements, ...doc.nonfunctional_requirements];
  const requiredLists = new Set(["target_users", "user_goals", "in_scope", "functional_requirements"]);
  return <fieldset className="pm-editor" disabled={disabled}><legend>Draft requirements</legend>
    <p className="form-note">Changes stay in this page until saved. The server records your identity on changed requirements; existing source evidence is preserved.</p>
    {scalarFields.map(field=><Text key={field} name={label(field)} value={doc[field].text} change={text=>edit(d=>{d[field].text=text;})} />)}
    {listFields.map(field=><details key={field} open={field === "functional_requirements"}><summary>{label(field)} ({doc[field].length})</summary><div className="pm-fields">
      {doc[field].map((item,i)=><div className="pm-edit-row" key={item.key}><Text name={`${label(field)} ${i+1}`} value={item.text} change={text=>edit(d=>{d[field][i].text=text;})} /><Button type="button" variant="outline" disabled={requiredLists.has(field) && doc[field].length <= 1} onClick={()=>edit(d=>{d[field].splice(i,1);})} aria-label={`Remove ${label(field)} ${i+1}`}>Remove</Button><small>{item.key}</small></div>)}
      <Button type="button" variant="outline" onClick={()=>edit(d=>{d[field].push(newStatement());})}>Add {label(field).toLowerCase()} item</Button>
    </div></details>)}
    <h3>Epics and stories</h3>
    {doc.epics.map((epic,ei)=><section className="pm-edit-card" key={epic.key} aria-label={`Edit epic ${ei+1}`}>
      <Text name={`Epic ${ei+1} title`} max={200} value={epic.title} change={text=>edit(d=>{d.epics[ei].title=text;})} />
      <Text name={`Epic ${ei+1} goal`} value={epic.goal} change={text=>edit(d=>{d.epics[ei].goal=text;})} />
      <PriorityField name={`Epic ${ei+1} priority`} value={epic.priority} change={p=>edit(d=>{d.epics[ei].priority=p;})} />
      <Button type="button" variant="outline" disabled={doc.epics.length===1} onClick={()=>edit(d=>{d.epics.splice(ei,1);})}>Remove epic {ei+1}</Button>
      {epic.stories.map((story,si)=><section className="pm-edit-card" key={story.key} aria-label={`Edit story ${story.key}`}>
        <Text name={`Story title (${story.key})`} max={200} value={story.title} change={v=>edit(d=>{d.epics[ei].stories[si].title=v;})} />
        <Text name={`User story (${story.key})`} max={1000} value={story.statement} change={v=>edit(d=>{d.epics[ei].stories[si].statement=v;})} />
        <p className="form-note">As a [user], I want [capability], so that [benefit].</p>
        <Text name={`Story description (${story.key})`} value={story.description} change={v=>edit(d=>{d.epics[ei].stories[si].description=v;})} />
        <PriorityField name={`Story priority (${story.key})`} value={story.priority} change={p=>edit(d=>{d.epics[ei].stories[si].priority=p;})} />
        <label>Requirement references ({story.key})<select multiple required value={story.requirement_refs} onChange={e=>{const v=Array.from(e.target.selectedOptions,o=>o.value); edit(d=>{d.epics[ei].stories[si].requirement_refs=v;});}}>{requirements.map(r=><option key={r.key} value={r.key}>{r.key}: {r.text}</option>)}</select></label>
        <label>Dependencies ({story.key})<select multiple value={story.dependencies} onChange={e=>{const v=Array.from(e.target.selectedOptions,o=>o.value); edit(d=>{d.epics[ei].stories[si].dependencies=v;});}}>{stories.filter(s=>s.key!==story.key).map(s=><option key={s.key} value={s.key}>{s.key}: {s.title}</option>)}</select></label>
        <p className="form-note">Use Ctrl or Command to select multiple items or clear a dependency. Removing a referenced requirement or story requires correcting its references before saving.</p>
        {story.acceptance_criteria.map((criterion,ci)=><div className="pm-criterion-edit" key={criterion.key}>
          {(["given","when","then"] as const).map(field=><Text key={field} name={`${label(field)} (${criterion.key})`} max={500} value={criterion[field]} change={v=>edit(d=>{d.epics[ei].stories[si].acceptance_criteria[ci][field]=v;})} />)}
          <Button type="button" variant="outline" disabled={story.acceptance_criteria.length===1} onClick={()=>edit(d=>{d.epics[ei].stories[si].acceptance_criteria.splice(ci,1);})}>Remove criterion {ci+1}</Button>
        </div>)}
        <div className="pm-actions"><Button type="button" variant="outline" onClick={()=>edit(d=>{d.epics[ei].stories[si].acceptance_criteria.push({key:newKey("criterion"),given:"",when:"",then:"",source:{...human}});})}>Add acceptance criterion</Button><Button type="button" variant="outline" disabled={epic.stories.length===1} onClick={()=>edit(d=>{d.epics[ei].stories.splice(si,1);})}>Remove story</Button></div>
      </section>)}
      <Button type="button" variant="outline" onClick={()=>edit(d=>{d.epics[ei].stories.push({key:newKey("story"),title:"",statement:"",description:"",priority:"P1",requirement_refs:requirements[0] ? [requirements[0].key] : [],dependencies:[],source:{...human},acceptance_criteria:[{key:newKey("criterion"),given:"",when:"",then:"",source:{...human}}]});})}>Add user story</Button>
    </section>)}
    <Button type="button" variant="outline" onClick={()=>edit(d=>{d.epics.push({key:newKey("epic"),title:"",goal:"",priority:"P1",source:{...human},stories:[{key:newKey("story"),title:"",statement:"",description:"",priority:"P1",requirement_refs:requirements[0] ? [requirements[0].key] : [],dependencies:[],source:{...human},acceptance_criteria:[{key:newKey("criterion"),given:"",when:"",then:"",source:{...human}}]}]});})}>Add epic</Button>
    <h3>Items requiring confirmation</h3>
    {doc.confirmations.map((item,i)=><div className="pm-edit-card" key={item.key}>
      <p><strong>{item.key}</strong> · {item.blocking ? "Blocking" : "Advisory"}{!item.active && " · Retired"}</p>
      {item.blocking ? <p>{item.text}</p> : <Text name={`Confirmation ${i+1}`} value={item.text} change={v=>edit(d=>{d.confirmations[i].text=v;})} />}
      <label>Disposition ({item.key})<select value={item.disposition} onChange={e=>{const v=e.target.value as typeof item.disposition;edit(d=>{d.confirmations[i].disposition=v;if(v==="unresolved"){d.confirmations[i].reason=null;d.confirmations[i].active=true;}});}}>{["unresolved","resolved","deferred"].map(v=><option key={v}>{v}</option>)}</select></label>
      {item.disposition!=="unresolved" && <Text name={`Disposition reason (${item.key})`} value={item.reason ?? ""} change={v=>edit(d=>{d.confirmations[i].reason=v;})} />}
      <p className="form-note">A blocking item retains its original wording and evidence. Resolve it or defer it with a reason before approval.</p>
    </div>)}
    <Button type="button" variant="outline" onClick={()=>edit(d=>{d.confirmations.push({...newStatement(),blocking:true,active:true,disposition:"unresolved",reason:null,actor_id:null,decided_at:null});})}>Add confirmation</Button>
  </fieldset>;
}
