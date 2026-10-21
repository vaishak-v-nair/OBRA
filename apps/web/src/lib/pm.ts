import { request } from "./api";

export type Source = { kind: "brief" | "title" | "description" | "instructions" | "context" | "suggested" | "assumption" | "human"; quote?: string | null; context_key?: string | null; actor_id?: string | null; inherited_kind?: string | null };
export type Statement = { key: string; text: string; source: Source };
export type Confirmation = Statement & {blocking: boolean; active: boolean; disposition: "unresolved" | "resolved" | "deferred"; reason: string | null; actor_id: string | null; decided_at: string | null};
export type Priority = "P0" | "P1" | "P2" | "P3";
export type Criterion = { key: string; given: string; when: string; then: string; source: Source };
export type Story = {key: string; title: string; statement: string; description: string; priority: Priority; requirement_refs: string[]; dependencies: string[]; source: Source; acceptance_criteria: Criterion[]};
export type Epic = {key: string; title: string; goal: string; priority: Priority; source: Source; stories: Story[]};
export const scalarFields = ["product_name", "summary", "problem_statement", "proposed_solution"] as const;
export const listFields = ["target_users", "user_goals", "in_scope", "out_of_scope", "functional_requirements", "nonfunctional_requirements", "prerequisites", "assumptions", "risks", "open_questions"] as const;
export type PlanDocument = {schema_version: 1; epics: Epic[]; confirmations: Confirmation[]} & Record<typeof scalarFields[number], Statement> & Record<typeof listFields[number], Statement[]>;
export type Capability = {provider: string; configured: boolean; model: string | null; timeout_seconds: number; max_output_tokens: number; setup_message: string | null};
export type Run = {id: string; project_id: string; initiator_id: string; status: "pending" | "running" | "succeeded" | "failed" | "interrupted"; client_request_id: string; provider: string; requested_model: string | null; returned_model: string | null; prompt_version: string; plan_id: string | null; created_at: string; completed_at: string | null; deadline_at: string; error_category: string | null; diagnostic_id: string | null; provider_response_id: string | null; provider_request_id: string | null; usage: Record<string, unknown> | null};
export type RunDetail = Run & { input_snapshot: {brief: string; instructions: string; context_plan?: {id: string; revision: number}} };
export type PlanSummary = {id: string; project_id: string; version: number; revision: number; state: "draft" | "approved" | "superseded"; origin: "generated" | "human_copy" | "human_authored"; content_hash: string; editor_id: string; approved_by: string | null; approved_at: string | null; created_at: string; source_plan_id: string | null; source_revision: number | null; copy_request_id: string | null};
export type Plan = PlanSummary & {document: PlanDocument; generation: Run | null; inputs: {title: string; description: string; brief: string; instructions: string} | null};
export type Page<T> = {items: T[]; limit: number; offset: number; next_offset: number | null; capability?: Capability};
const base = (project: string) => `/api/v1/projects/${project}`;
export const pm = {
  runs: (project: string, signal?: AbortSignal, requestId?: string, offset = 0) => request<Page<Run>>(`${base(project)}/pm-runs?limit=20&offset=${offset}${requestId ? `&client_request_id=${requestId}` : ""}`, {signal}),
  run: (project: string, id: string, signal?: AbortSignal) => request<RunDetail>(`${base(project)}/pm-runs/${id}`, {signal}),
  plans: (project: string, signal?: AbortSignal, offset = 0, copyId?: string) => request<Page<PlanSummary>>(`${base(project)}/pm-plans?limit=20&offset=${offset}${copyId ? `&copy_request_id=${copyId}` : ""}`, {signal}),
  plan: (project: string, id: string, signal?: AbortSignal) => request<Plan>(`${base(project)}/pm-plans/${id}`, {signal}),
  generate: (project: string, body: {client_request_id: string; brief: string; instructions: string; context_plan_id?: string; context_revision?: number}, signal?: AbortSignal) => request<Run>(`${base(project)}/pm-runs`, {method:"POST", body:JSON.stringify(body), signal, timeoutMs:300000}),
  save: (project: string, plan: Plan, document: PlanDocument, signal?: AbortSignal) => request<Plan>(`${base(project)}/pm-plans/${plan.id}`, {method:"PUT", body:JSON.stringify({expected_revision:plan.revision, document}), signal}),
  approve: (project: string, plan: Plan, signal?: AbortSignal) => request<Plan>(`${base(project)}/pm-plans/${plan.id}/approve`, {method:"POST", body:JSON.stringify({expected_revision:plan.revision, version:plan.version}), signal}),
  copy: (project: string, plan: Plan, requestId: string, signal?: AbortSignal) => request<Plan>(`${base(project)}/pm-plans/${plan.id}/draft`, {method:"POST", body:JSON.stringify({expected_revision:plan.revision, version:plan.version, client_request_id:requestId}), signal}),
};
export function label(field: string) { return field.replaceAll("_", " ").replace(/^./, (c) => c.toUpperCase()); }
