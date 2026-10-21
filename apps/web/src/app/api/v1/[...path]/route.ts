import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  if (path.some((segment) => !/^[a-zA-Z0-9_-]+$/.test(segment))) return new Response(null, { status: 400 });
  const upstream = new URL(`/api/v1/${path.join("/")}${request.nextUrl.search}`, process.env.API_URL ?? "http://127.0.0.1:8000");
  const pm = path[0] === "projects" && ["pm-runs", "pm-plans"].includes(path[2]);
  const headers = new Headers();
  for (const name of ["cookie", "content-type", "origin", "x-csrf-token"]) {
    const value = request.headers.get(name); if (value) headers.set(name, value);
  }
  const started=performance.now();
  let upstreamDeadline:AbortSignal|undefined;
  let dispatched=false;
  try {
    let body: string | undefined;
    if (!["GET", "HEAD"].includes(request.method)) {
      if (pm) {
        const reader = request.body?.getReader();
        const chunks: Uint8Array[] = []; let size = 0;
        const cap = request.method === "PUT" ? 512 * 1024 : 256 * 1024;
        const deadline = AbortSignal.timeout(5000);
        if (reader) {
          const aborted = () => { void reader.cancel(); };
          deadline.addEventListener("abort", aborted, { once: true });
          try { while (true) { const part = await reader.read(); if (deadline.aborted) return Response.json({error:{code:"request_body_timeout",message:"The planning request body timed out."}}, {status:408}); if (part.done) break; size += part.value.length; if (size > cap) { await reader.cancel(); return Response.json({error:{code:"request_too_large",message:"The planning request exceeds its size limit."}}, {status:413}); } chunks.push(part.value); } }
          finally { deadline.removeEventListener("abort", aborted); reader.releaseLock(); }
        }
        const merged = new Uint8Array(size); let offset = 0; for (const chunk of chunks) { merged.set(chunk, offset); offset += chunk.length; }
        body = new TextDecoder().decode(merged);
      } else body = await request.text();
    }
    upstreamDeadline=AbortSignal.timeout(pm && request.method === "POST" && path[2] === "pm-runs" ? 290000 : 15000);
    dispatched=true;
    const response = await fetch(upstream, { method: request.method, headers,
      body,
      cache: "no-store", redirect: "manual", signal: AbortSignal.any([upstreamDeadline,request.signal]) });
    const outgoing = new Headers({ "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" });
    for (const name of ["content-type", "retry-after"]) { const value = response.headers.get(name); if (value) outgoing.set(name, value); }
    for (const cookie of response.headers.getSetCookie()) outgoing.append("Set-Cookie", cookie);
    return new Response(response.status === 204 ? null : response.body, { status: response.status, headers: outgoing });
  } catch {
    if(pm){
      const origin=upstreamDeadline?.aborted?"proxy_deadline":request.signal.aborted?"client_disconnect":"api_transport";
      console.info(JSON.stringify({event:"pm_proxy_failure",stage:"next_proxy",elapsed_ms:Math.round(performance.now()-started),error_category:"run_outcome_unknown",origin,attempt:1,final_state:"unknown"}));
      return Response.json({error:{code:dispatched?"run_outcome_unknown":"request_not_dispatched",message:dispatched?"ORBA could not confirm this request's result. Check status before starting another generation. Your input is preserved.":"The planning request was not sent to the API. Your input is preserved; reconnect before trying again."}},{status:503});
    }
    return Response.json({ error: { code: "api_unavailable", message: "Could not reach ORBA. The operation could not be confirmed. Check the workspace before retrying a save." } }, { status: 503 });
  }
}
export { proxy as GET, proxy as POST, proxy as PATCH, proxy as DELETE, proxy as PUT };
