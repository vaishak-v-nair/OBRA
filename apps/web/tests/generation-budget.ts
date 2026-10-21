/** Test-only transport allowance, not a provider-wide production quota.
 * The first request/response stays real. Extra POSTs fail before forwarding. */
import type {Page} from "@playwright/test";

export async function allowOneGeneration(page:Page) {
  const budget={attempted:0,forwarded:0,blocked:0};
  await page.route("**/api/v1/projects/*/pm-runs",async route=>{
    if(route.request().method()!=="POST"){await route.continue();return;}
    // All counters advance before await, so simultaneous activations cannot race.
    budget.attempted++;
    if(budget.forwarded>=1){budget.blocked++;await route.abort("blockedbyclient");return;}
    budget.forwarded++;
    await route.continue();
  });
  return budget;
}
