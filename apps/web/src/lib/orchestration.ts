import { request } from "./api";
import type { ArchitectureSummary, EngineeringTask } from "./architect";
import type { Page } from "./pm";

export type RunInput = { client_request_id: string; architecture_id: string; architecture_version: number; architecture_revision: number };
export type OrchestrationRun = {
  id: string; project_id: string; workspace_id: string; architecture_id: string;
  architecture_version: number; architecture_revision: number; architecture_hash: string;
  source_plan_id: string; source_version: number; source_revision: number; source_hash: string;
  creator_id: string; client_request_id: string; snapshot_hash: string; hash_version: string;
  status: "created" | "awaiting_executor" | "cancelled"; revision: number; last_event_sequence: number;
  created_at: string; updated_at: string; cancelled_at: string | null; execution_performed: false;
};
export type OrchestrationTask = {
  id: string; run_id: string; source_task_id: string; key: string; definition: EngineeringTask;
  eligibility: "eligible" | "waiting_prerequisites"; execution_status: "awaiting_executor" | "cancelled";
};
export type EligibilityNode = {
  key: string; eligibility: OrchestrationTask["eligibility"]; execution_status: OrchestrationTask["execution_status"];
  explanation: string; prerequisites: string[]; dependents: string[]; ancestors: string[]; impact: string[];
};
export type EligibilityGraph = {
  valid: true; edge_convention: "prerequisite -> dependent"; execution_performed: false;
  topological_order: string[]; roots: string[]; eligible: string[]; blocked: string[];
  edges: { prerequisite: string; dependent: string }[]; nodes: EligibilityNode[];
};
export type RunDetail = OrchestrationRun & { tasks: OrchestrationTask[]; graph: EligibilityGraph; source_current: boolean };
export type RunEvent = {
  id: string; run_id: string; task_id: string | null; sequence: number; run_revision: number;
  event_type: "run_created" | "run_awaiting_executor" | "run_cancelled" | "task_cancelled";
  actor_type: "user" | "system"; actor_id: string | null; occurred_at: string;
  previous_state: string | null; new_state: string; details: { execution_performed: false };
};
const base = (project: string) => `/api/v1/projects/${project}/orchestration-runs`;
export const orchestration = {
  source: (project: string, signal?: AbortSignal) => request<ArchitectureSummary | null>(`${base(project)}/source`, { signal }),
  list: (project: string, signal?: AbortSignal, requestId?: string, offset = 0) => request<Page<OrchestrationRun>>(`${base(project)}?limit=20&offset=${offset}${requestId ? `&client_request_id=${requestId}` : ""}`, { signal }),
  get: (project: string, id: string, signal?: AbortSignal) => request<RunDetail>(`${base(project)}/${id}`, { signal }),
  create: (project: string, payload: RunInput, signal?: AbortSignal) => request<RunDetail>(base(project), { method: "POST", body: JSON.stringify(payload), signal }),
  events: (project: string, id: string, signal?: AbortSignal, after = 0) => request<{ run_id: string; items: RunEvent[]; next_sequence: number | null }>(`${base(project)}/${id}/events?after=${after}`, { signal }),
  cancel: (project: string, run: OrchestrationRun, signal?: AbortSignal) => request<RunDetail>(`${base(project)}/${run.id}/cancel`, { method: "POST", body: JSON.stringify({ expected_revision: run.revision }), signal }),
};
