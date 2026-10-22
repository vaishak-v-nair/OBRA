/** Verification transport boundary. No provider responses are stubbed here. */
import { expect, type BrowserContext } from "@playwright/test";

export async function architectBoundary(context: BrowserContext, paidOptIn = false) {
  let phase: "preflight" | "generation" | "post_generation" = "preflight";
  const budget = { attempted: 0, forwarded: 0, blocked: 0 };
  const phases = [{ phase, at: new Date().toISOString() } as { phase: string; at: string }];
  let pmPosts = 0;
  // BrowserContext routing does not intercept APIRequestContext calls. Guard its
  // public fetch method too (the installed SDK's post method delegates to fetch).
  // A paid allowance is exclusively for the one UI request, never a direct API POST.
  const apiFetch = context.request.fetch.bind(context.request);
  context.request.fetch = async (target, options) => {
    const url = typeof target === "string" ? target : target.url();
    const method = options?.method ?? (typeof target === "string" ? "GET" : target.method());
    const path = new URL(url, "http://localhost:3001").pathname;
    if (method.toUpperCase() === "POST" && /^\/api\/v1\/projects\/[^/]+\/(pm-runs|architect-runs)\/?$/.test(path)) {
      budget.attempted++; budget.blocked++;
      if (path.replace(/\/$/, "").endsWith("/pm-runs")) pmPosts++;
      throw new Error("MODEL_API_REQUEST_FORBIDDEN: verification generation is allowed only through the explicitly authorized browser action.");
    }
    return apiFetch(target, options);
  };
  await context.route(/\/api\/v1\/projects\/[^/]+\/(pm-runs|architect-runs)\/?(?:\?.*)?$/, async route => {
    if (route.request().method() !== "POST") { await route.continue(); return; }
    budget.attempted++;
    const pm = new URL(route.request().url()).pathname.replace(/\/$/, "").endsWith("/pm-runs");
    if (pm) pmPosts++;
    if (pm || phase !== "generation" || budget.forwarded !== 0) {
      budget.blocked++; await route.abort("blockedbyclient"); return;
    }
    budget.forwarded++;
    phase = "post_generation";
    phases.push({ phase, at: new Date().toISOString() });
    await route.continue();
  });
  return {
    budget, phases,
    pmPosts: () => pmPosts,
    openOneRequest(preflight: { result: string; approved_source_reloaded: boolean }) {
      expect(paidOptIn && process.env.ORBA_ARCHITECT_LIVE_OPT_IN === "1", "Fresh live opt-in is required; preflight cannot authorize generation").toBe(true);
      expect(preflight.result, "Phase1 must pass before paid dispatch").toBe("PASS");
      expect(preflight.approved_source_reloaded).toBe(true);
      expect(phase).toBe("preflight");
      expect(budget).toEqual({ attempted: 0, forwarded: 0, blocked: 0 });
      phase = "generation"; phases.push({ phase, at: new Date().toISOString() });
    },
  };
}
