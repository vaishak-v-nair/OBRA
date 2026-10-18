import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  if (path.some((segment) => !/^[a-zA-Z0-9_-]+$/.test(segment))) return new Response(null, { status: 400 });
  const upstream = new URL(`/api/v1/${path.join("/")}${request.nextUrl.search}`, process.env.API_URL ?? "http://127.0.0.1:8000");
  const headers = new Headers();
  for (const name of ["cookie", "content-type", "origin", "x-csrf-token"]) {
    const value = request.headers.get(name); if (value) headers.set(name, value);
  }
  try {
    const response = await fetch(upstream, { method: request.method, headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
      cache: "no-store", redirect: "manual", signal: AbortSignal.timeout(15000) });
    const outgoing = new Headers({ "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" });
    for (const name of ["content-type", "retry-after"]) { const value = response.headers.get(name); if (value) outgoing.set(name, value); }
    for (const cookie of response.headers.getSetCookie()) outgoing.append("Set-Cookie", cookie);
    return new Response(response.status === 204 ? null : response.body, { status: response.status, headers: outgoing });
  } catch {
    return Response.json({ error: { code: "api_unavailable", message: "Could not reach ORBA. The operation could not be confirmed. Check the workspace before retrying a save." } }, { status: 503 });
  }
}
export { proxy as GET, proxy as POST, proxy as PATCH, proxy as DELETE };
