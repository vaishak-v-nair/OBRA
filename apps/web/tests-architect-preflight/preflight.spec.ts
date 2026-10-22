/** No provider double response: only real source setup/approval and dispatch denial. */
import { test, expect } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { architectBoundary } from "../tests/architect-boundary";
import { architectPreflight, observeRoutes, preflightProof, testCommand } from "../tests/architect-preflight";
import { evidencePath } from "../tests/evidence";

test("Phase1 reaches exact approved Architect source without generation", async ({ page, context }) => {
  const proof = preflightProof();
  const boundary = await architectBoundary(context);
  observeRoutes(page, proof);
  try {
    testCommand("scripts.prepare_tests");
    await architectPreflight(page, proof);
    const counters = await page.request.get("http://127.0.0.1:8001/__test/no-generation");
    expect(counters.status()).toBe(200);
    proof.server_boundary = await counters.json();
    expect(proof.server_boundary).toEqual({ execution_class: "no_generation_test_boundary", provider_readiness_verified: false, blocked_generation_posts: 0, provider_dependency_entries: 0 });
    expect(boundary.budget).toEqual({ attempted: 0, forwarded: 0, blocked: 0 });
  } catch (error) {
    proof.result = "FAIL"; throw error;
  } finally {
    Object.assign(proof, { stage: "stage04-architect", execution_class: "no_generation_preflight", provider_readiness_verified: false, generation_budget: boundary.budget, phases: boundary.phases, completed_at: new Date().toISOString() });
    writeFileSync(evidencePath("preflight-proof.json"), JSON.stringify(proof, null, 2) + "\n");
  }
});
