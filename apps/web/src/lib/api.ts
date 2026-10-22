export type Project = {
  id: string; title: string; description: string; status: "created";
  created_at: string; updated_at: string;
  workspace_id: string; creator_id: string | null;
};
export type User = { id: string; email: string; display_name: string };
export type Role = "owner" | "admin" | "member" | "viewer";
export type Workspace = { id: string; name: string; slug: string; role: Role; created_at: string };
let authEpoch = 0;
export function advanceAuthEpoch() { authEpoch++; }
export class ApiError extends Error { constructor(message: string, public status: number, public code = "http_error", public runId: string | null = null, public diagnosticId: string | null = null, public details: {field: string; message: string}[] = []) { super(message); } }
export async function request<T>(path: string, options?: RequestInit & { timeoutMs?: number }): Promise<T> {
  const epoch = authEpoch;
  const { timeoutMs = 20000, ...init } = options ?? {};
  const signal = init.signal ? AbortSignal.any([init.signal, AbortSignal.timeout(timeoutMs)]) : AbortSignal.timeout(timeoutMs);
  let response: Response;
  let dispatched = false;
  try {
    const headers = new Headers(options?.headers);
    if (options?.method && options.method !== "GET") {
      const csrf = await fetch("/api/v1/auth/csrf", { cache: "no-store", credentials: "same-origin", signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]) });
      if (!csrf.ok) throw new Error("CSRF service unavailable");
      headers.set("X-CSRF-Token", (await csrf.json()).csrf_token);
      headers.set("Content-Type", "application/json");
    }
    dispatched = true;
    response = await fetch(path, { ...init, headers, credentials: "same-origin", cache: "no-store", signal });
  } catch {
    if (init.signal?.aborted) throw new DOMException("Request cancelled", "AbortError");
    if (path.includes("/pm-") || path.includes("/architect")) throw new ApiError(dispatched
      ? "Could not reach ORBA. The operation's outcome is unconfirmed. Use Check status before explicitly trying again. Your draft stays here."
      : "ORBA could not prepare the request. No generation request was sent. Your input stays here; reconnect before trying again.", 0, dispatched ? "run_outcome_unknown" : "request_not_dispatched");
    throw new Error(options?.method === "POST"
      ? "Could not reach ORBA. The save could not be confirmed. Check Projects before trying again to avoid a duplicate. Your draft is preserved here."
      : "Could not reach ORBA. Check that the API is running, then try again.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.error?.details?.map((item: { message: string }) => item.message).join(" ");
    if (response.status === 401 && !path.includes("/auth/") && epoch === authEpoch) window.dispatchEvent(new Event("orba-session-expired"));
    throw new ApiError(detail || body?.error?.message || "Something went wrong. Please try again.", response.status, body?.error?.code, body?.error?.run_id, body?.error?.diagnostic_id, body?.error?.details);
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}
export const projects = {
  list: (workspaceId: string, offset = 0) => request<Project[]>(`/api/v1/projects?workspace_id=${workspaceId}&limit=50&offset=${offset}`),
  get: (id: string) => request<Project>(`/api/v1/projects/${id}`),
  create: (title: string, description: string, workspaceId: string) => request<Project>("/api/v1/projects", {
    method: "POST", body: JSON.stringify({ title, description, workspace_id: workspaceId }),
  }),
};
