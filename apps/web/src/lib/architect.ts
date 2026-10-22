import { request } from "./api";
import type { Capability, Page, Plan, PlanDocument, Priority } from "./pm";

export type Json = string | number | boolean | null | Json[] | { [key: string]: Json };
export type ComponentProposal = {key:string; name:string; responsibility:string; inputs:string[]; outputs:string[]; dependencies:string[]; story_refs:string[]; security_considerations:string[]};
export type EngineeringTask = {key:string; title:string; description:string; scope:string; deliverables:string[]; acceptance_criteria:string[]; priority:Priority; category:string; complexity_estimate:"small"|"medium"|"large"|null; planning_state:"proposed"|"needs_clarification"; story_refs:string[]; requirement_refs:string[]; criterion_refs:string[]; component_refs:string[]; dependencies:string[]};
export type ArchitectureDocument = {
  schema_version:1;
  overview:{title:string; summary:string; architectural_style:string; design_goals:string[]; constraints:string[]; assumptions:string[]; non_goals:string[]};
  technologies:{technology:string; responsibility:string; reason:string; alternatives:string[]; tradeoffs:string[]; constraints:string[]; basis:"requirement"|"recommendation"}[];
  components:ComponentProposal[];
  database_design:{notes:string; entities:{key:string; name:string; fields:{name:string; logical_type:string; constraints:string[]}[]; constraints:string[]; indexes:string[]; data_ownership:string; privacy_considerations:string[]}[]; relationships:{source:string; target:string; description:string}[]};
  api_design:{notes:string; endpoints:{key:string; status:"proposed"; method:string; route:string; purpose:string; request_contract:string; response_contract:string; authentication:string; authorization:string; error_behavior:string[]}[]};
  security:{trust_boundaries:string[]; authentication_assumptions:string; authorization_model:string; sensitive_data:string[]; external_integrations:string[]; secret_management:string; threats:{threat:string; mitigation:string}[]};
  deployment:{topology:string; infrastructure_requirements:string[]; operational_considerations:string[]; uncertain_choices:string[]};
  risks:string[]; open_decisions:{key:string; question:string; blocking:boolean}[]; tasks:EngineeringTask[];
  coverage_exceptions:{kind:"story"|"requirement"|"criterion"|"source_dependency"; reference:string; reason:string}[];
};
export type GraphNode = {key:string; state:"ready"|"blocked"|"needs_clarification"; explanation:string; prerequisites:string[]; dependents:string[]; ancestors:string[]; impact:string[]};
export type TaskGraph = {valid:boolean; topological_order:string[]; edges:{prerequisite:string; dependent:string}[]; nodes:GraphNode[]; ready:string[]; blocked:string[]; execution_performed:false};
export type Coverage = {meaning:string; covered_stories:string[]; covered_requirements:string[]; covered_criteria:string[]; gaps:{id:string; kind:string; reference:string}[]; unaccounted_gaps:{id:string; kind:string; reference:string}[]; orphan_tasks:string[]; component_gaps:string[]; needs_clarification:string[]; review_obligations:{id:string; reason:string}[]; approvable:boolean};
export type ArchitectRun = {id:string; project_id:string; initiator_id:string; client_request_id:string; source_plan_id:string; source_version:number; source_revision:number; source_hash:string; status:"pending"|"running"|"succeeded"|"failed"|"interrupted"; requested_model:string|null; returned_model:string|null; architecture_id:string|null; error_category:string|null; diagnostic_id:string|null; provider_response_id:string|null; usage:Record<string,unknown>|null; created_at:string; deadline_at:string};
export type ArchitectureSummary = {id:string; project_id:string; source_plan_id:string; source_version:number; source_revision:number; source_hash:string; version:number; revision:number; state:"draft"|"approved"|"superseded"; content_hash:string; generating_run_id:string|null; copied_from_id:string|null; approved_by:string|null; approved_at:string|null; created_at:string; approval_dispositions:Record<string,{reason:string;actor_id:string;decided_at:string;revision:number}>|null};
export type Architecture = ArchitectureSummary & {document:ArchitectureDocument; source_document:PlanDocument; source_current:boolean; graph:TaskGraph; coverage:Coverage; generation:ArchitectRun|null};
const base = (project:string) => `/api/v1/projects/${project}`;
export const architect = {
  source:(project:string,signal?:AbortSignal) => request<Plan|null>(`${base(project)}/architect-source`,{signal}),
  runs:(project:string,signal?:AbortSignal,requestId?:string,offset=0) => request<Page<ArchitectRun>>(`${base(project)}/architect-runs?limit=20&offset=${offset}${requestId?`&client_request_id=${requestId}`:""}`,{signal}),
  run:(project:string,id:string,signal?:AbortSignal) => request<ArchitectRun & {input_snapshot:{constraints:string}}>(`${base(project)}/architect-runs/${id}`,{signal}),
  list:(project:string,signal?:AbortSignal,offset=0,copyId?:string) => request<Page<ArchitectureSummary>>(`${base(project)}/architectures?limit=20&offset=${offset}${copyId?`&copy_request_id=${copyId}`:""}`,{signal}),
  get:(project:string,id:string,signal?:AbortSignal) => request<Architecture>(`${base(project)}/architectures/${id}`,{signal}),
  generate:(project:string,source:{id:string;version:number;revision:number},constraints:string,clientId:string,signal?:AbortSignal) => request<ArchitectRun>(`${base(project)}/architect-runs`,{method:"POST",body:JSON.stringify({client_request_id:clientId,source_plan_id:source.id,source_version:source.version,source_revision:source.revision,constraints}),signal,timeoutMs:300000}),
  save:(project:string,value:Architecture,document:ArchitectureDocument,signal?:AbortSignal) => request<Architecture>(`${base(project)}/architectures/${value.id}`,{method:"PUT",body:JSON.stringify({expected_revision:value.revision,document}),signal}),
  approve:(project:string,value:Architecture,acknowledgments:Record<string,string>,signal?:AbortSignal) => request<Architecture>(`${base(project)}/architectures/${value.id}/approve`,{method:"POST",body:JSON.stringify({version:value.version,expected_revision:value.revision,acknowledgments}),signal}),
  copy:(project:string,value:Architecture,id:string,signal?:AbortSignal) => request<Architecture>(`${base(project)}/architectures/${value.id}/draft`,{method:"POST",body:JSON.stringify({version:value.version,expected_revision:value.revision,client_request_id:id}),signal}),
};
export type ArchitectCapability = Capability;
