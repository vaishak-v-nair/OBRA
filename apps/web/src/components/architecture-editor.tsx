"use client";

import type { ArchitectureDocument, Json } from "@/lib/architect";
import { label } from "@/lib/pm";
import { Button } from "@/components/ui/button";

export const architectureFieldId = (path:string) => `architect-field-${path.replaceAll(".","-")}`;
const options:Record<string,string[]> = {
  priority:["P0","P1","P2","P3"], category:["frontend","backend","database","infrastructure","integration","security","testing","documentation"],
  planning_state:["proposed","needs_clarification"], basis:["requirement","recommendation"], method:["GET","POST","PUT","PATCH","DELETE","HEAD","OPTIONS"],
  complexity_estimate:["","small","medium","large"], kind:["story","requirement","criterion","source_dependency"],
};
function template(field:string):Json|undefined {
  const key=`new_${crypto.randomUUID().slice(0,8)}`;
  const templates:Record<string,Json> = {
    tasks:{key,title:"New engineering task",description:"",scope:"",deliverables:[],acceptance_criteria:[],priority:"P1",category:"backend",complexity_estimate:null,planning_state:"proposed",story_refs:[],requirement_refs:[],criterion_refs:[],component_refs:[],dependencies:[]},
    components:{key,name:"New component",responsibility:"",inputs:[],outputs:[],dependencies:[],story_refs:[],security_considerations:[]},
    technologies:{technology:"",responsibility:"",reason:"",alternatives:[],tradeoffs:[],constraints:[],basis:"recommendation"},
    entities:{key,name:"New entity",fields:[{name:"id",logical_type:"identifier",constraints:[]}],constraints:[],indexes:[],data_ownership:"",privacy_considerations:[]},
    fields:{name:key,logical_type:"",constraints:[]}, relationships:{source:"",target:"",description:""},
    endpoints:{key,status:"proposed",method:"GET",route:"/",purpose:"",request_contract:"",response_contract:"",authentication:"",authorization:"",error_behavior:[]},
    threats:{threat:"",mitigation:""},open_decisions:{key,question:"",blocking:true},coverage_exceptions:{kind:"story",reference:"",reason:""},
  };
  return templates[field];
}
function Field({value,path,context,onChange,errors}:{value:Json;path:string;context:string;onChange:(value:Json)=>void;errors:{field:string;message:string}[]}) {
  const field=path.split(".").at(-1) ?? path;
  const title=`${context} · ${label(field)}`;
  const id=architectureFieldId(path);
  const issues=errors.filter(item=>item.field.replace(/^body\.document\.?/,"")===path);
  const description=issues.length?`${id}-error`:undefined;
  if(Array.isArray(value)) {
    if(templateFields.has(field)) return <fieldset className="architect-array"><legend>{label(field)}</legend>{value.map((item,index)=><details key={index} open={field==="tasks" && index===0}><summary>{typeof item==="object"&&item!==null&&!Array.isArray(item)?String(item.title??item.name??item.key??`${label(field)} ${index+1}`):`${label(field)} ${index+1}`}</summary><Field value={item} path={`${path}.${index}`} context={typeof item==="object"&&item!==null&&!Array.isArray(item)?String(item.title??item.name??item.key??context):context} onChange={next=>onChange(value.map((old,i)=>i===index?next:old))} errors={errors}/><Button type="button" variant="outline" onClick={()=>onChange(value.filter((_,i)=>i!==index))}>Remove {label(field)} {index+1}</Button></details>)}<Button type="button" variant="outline" onClick={()=>{const next=template(field);if(next)onChange([...value,next]);}}>Add {field==="tasks"?"engineering task":label(field).toLowerCase()}</Button></fieldset>;
    return <div className="form-field"><label htmlFor={id}>{title}</label><textarea id={id} defaultValue={value.join("\n")} rows={Math.max(2,Math.min(value.length+1,6))} onChange={event=>onChange(event.target.value.split("\n").filter(item=>item.trim().length>0))} aria-invalid={issues.length>0} aria-describedby={description}/><small>One item per line.{field.endsWith("_refs")?" Use exact keys from the source or component list.":""}</small>{issues.length>0&&<p id={description} className="form-error">{issues.map(item=>item.message).join(" ")}</p>}</div>;
  }
  if(value!==null && typeof value==="object") return <div className="architect-fields">{Object.entries(value).filter(([key])=>key!=="schema_version"&&!(path.startsWith("tasks.")&&key==="dependencies")).map(([key,item])=><Field key={key} value={item} path={path?`${path}.${key}`:key} context={context} onChange={next=>onChange({...value,[key]:next})} errors={errors}/>)}</div>;
  if(typeof value==="boolean") return <label className="architect-check" htmlFor={id}><input id={id} type="checkbox" checked={value} onChange={event=>onChange(event.target.checked)}/>{title}</label>;
  if(options[field]) return <div className="form-field"><label htmlFor={id}>{title}</label><select id={id} value={String(value??"")} onChange={event=>onChange(field==="complexity_estimate"&&!event.target.value?null:event.target.value)}>{options[field].map(option=><option key={option} value={option}>{option?label(option):"No estimate"}</option>)}</select></div>;
  return <div className="form-field"><label htmlFor={id}>{title}</label><textarea id={id} rows={field==="key"||field==="name"||field==="title"||field==="route"?1:2} value={String(value??"")} readOnly={field==="status"} onChange={event=>onChange(event.target.value)} aria-invalid={issues.length>0} aria-describedby={description}/>{issues.length>0&&<p id={description} className="form-error">{issues.map(item=>item.message).join(" ")}</p>}</div>;
}
const templateFields=new Set(["tasks","components","technologies","entities","fields","relationships","endpoints","threats","open_decisions","coverage_exceptions"]);

export function ArchitectureEditor({document,onChange,errors}:{document:ArchitectureDocument;onChange:(value:ArchitectureDocument)=>void;errors:{field:string;message:string}[]}) {
  return <div className="architect-editor"><p className="form-note">Human edits update this draft only. Dependencies are edited in Task Graph. Source PRD keys remain authoritative.</p>{Object.entries(document).filter(([key])=>key!=="schema_version").map(([key,value])=><details key={key} open={key==="overview"}><summary>{label(key)}</summary><Field value={value as Json} path={key} context={label(key)} onChange={next=>onChange({...document,[key]:next})} errors={errors}/></details>)}</div>;
}

export function ProposalValue({value}:{value:Json}) {
  if(Array.isArray(value)) return value.length?<ul>{value.map((item,index)=><li key={index}><ProposalValue value={item}/></li>)}</ul>:<p className="form-note">None proposed.</p>;
  if(value!==null&&typeof value==="object") return <dl className="architect-read-fields">{Object.entries(value).map(([key,item])=><div key={key}><dt>{label(key)}</dt><dd><ProposalValue value={item}/></dd></div>)}</dl>;
  return <span>{value===null?"Not estimated":typeof value==="boolean"?(value?"Yes":"No"):String(value)}</span>;
}
