**DONE_WITH_CONCERNS.** The architecture is viable, but the remaining contract and test gaps below need closure. These are planning findings, not claims of implemented PM defects. Stage02’s **44 backend / 42 browser** results remain baseline evidence; Stage03 has no live AI success.

The plan already resolves separate request/snapshot hashes, composite ownership FKs, graph validation, immutable exact approval, logout serialization, lease fencing, and unknown final-commit outcomes. Those decisions should stand.

| Dimension | Verdict | Engineering assessment |
|---|---|---|
| Architecture | CONDITIONAL | Synchronous SQLAlchemy phases plus scoped `asyncio.run`/AsyncOpenAI fit the existing stack; dispatch boundaries need precision. |
| Test coverage | CONDITIONAL | Strong coverage map; several decisive interleavings need explicit assertions. |
| Performance | CONDITIONAL | Bounded documents and eager loading are appropriate; complete transport/body budgets remain unsettled. |
| Security | CONDITIONAL | Final authority checks are specified; clock semantics and uncertainty provenance need tightening. |
| Error handling | CONDITIONAL | Final commit ambiguity is handled; start-commit ambiguity and obsolete write responses need coverage. |
| Upgrade safety | NO | The preservation test targets a nonexistent migration revision; hash compatibility also needs an explicit contract. |

Ranked remaining blind spots:

1. **P1: Blocking confirmations can disappear through editing. Confidence: high.**  
   [Plan:120](E:/BrosKi/OBRA/docs/STAGE03_PLAN.md:120) requires reasoned resolution/deferral, while full-document editing permits structural removal. Stable keys and human attribution alone do not prevent deleting, rekeying, or changing `blocking` to bypass that obligation. Compare against stored blocker identities and require a server-recorded disposition before removal or downgrade. Retain that evidence through copies. Add deletion/rekey/downgrade approval tests; current open-blocker tests do not establish this.

2. **P1: Deadline arithmetic needs both transport hops and pre-buffer enforcement. Confidence: high.**  
   The current [proxy:14](E:/BrosKi/OBRA/apps/web/src/app/api/v1/[...path]/route.ts:14) buffers `request.text()` before constructing its timeout. Adding a longer fetch timeout cannot bound that read. Apply streamed byte limits and absolute read deadlines before buffering in both Next and ASGI. Account for proxy upload time separately: a 40-second proxy read plus the proposed 295-second API budget already exceeds 330 seconds. Include response consumption, client closure and `asyncio.run` teardown in measured bounds. Token limits alone do not bound transport-envelope bytes before decoding.

3. **P1: “Database UTC time” must mean time after lock acquisition. Confidence: high.**  
   [Plan:85](E:/BrosKi/OBRA/docs/STAGE03_PLAN.md:85) correctly serializes publication against [logout’s UPDATE/commit](E:/BrosKi/OBRA/apps/api/orba/auth.py:148). Specify a fresh authorization query after all required locks, using `clock_timestamp()` rather than transaction-start `now()`. Otherwise expiry during lock waiting can be evaluated against stale time. Add forced PostgreSQL schedules for logout-first, publication-first, and session/lease expiry while waiting. The existing logout-first assertion is insufficient to prove all three.

4. **P1: Unknown commits before provider dispatch need their own fence. Confidence: medium.**  
   The lifecycle has separate pending and running commits; [commit-ambiguity coverage](E:/BrosKi/OBRA/docs/STAGE03_TEST_PLAN.md:123) emphasizes preserving final success. Explicitly require confirmed running-state ownership before dispatch. After an uncertain reservation/start acknowledgement, either establish ownership safely or return unknown and allow lease expiry. A replay must never take over execution. Test acknowledgement loss at both commits and process loss immediately before dispatch, separately from finalization ambiguity.

5. **P1: Prior-plan context needs transitive provenance. Confidence: medium.**  
   [Plan:97](E:/BrosKi/OBRA/docs/STAGE03_PLAN.md:97) permits prior-plan context, while provenance distinguishes supplied context from suggestions. An earlier AI assumption could therefore acquire a “supplied context” label on regeneration despite remaining unresolved. Preserve originating node identity, original attribution and human disposition in the context snapshot and resulting evidence display. Prior approval accepts disclosed uncertainty; it does not confirm every assumption. Add a two-generation provenance case, including copied context.

6. **P1: Copy/version races need forced schedules, not only invariant summaries. Confidence: high.**  
   The shared locking policy is already correct. Expand [version-copy coverage](E:/BrosKi/OBRA/docs/STAGE03_TEST_PLAN.md:125) to force: identical keys returning one copy even after approval; identical keys with changed source revision returning 409; distinct keys receiving distinct versions; copy competing with generation/version allocation; and source Save competing with copy. Assert an exact captured source revision/hash or rejection, correct child ownership, and preserved provenance using independent PostgreSQL sessions. Provider doubles must remain isolated units.

7. **P2: An obsolete generation’s 401 can clear a newly authenticated account. Confidence: high.**  
   [api.ts:29](E:/BrosKi/OBRA/apps/web/src/lib/api.ts:29) unconditionally emits session expiry; [session.tsx:45](E:/BrosKi/OBRA/apps/web/src/components/session.tsx:45) clears current identity. After logout/login, an old long request can fail its original-session check and clear the new account’s UI. Extend the session-generation guard to write completions and global error side effects, not only reads. Add an account-switch browser journey with an outstanding request.

8. **P2: Make upgrade identities executable and durable. Confidence: high.**  
   [Test plan:160](E:/BrosKi/OBRA/docs/STAGE03_TEST_PLAN.md:160) says `Apply0002`; the actual [Stage02 revision](E:/BrosKi/OBRA/apps/api/migrations/versions/0febbe526f54_auth_workspaces.py:6) is `0febbe526f54`. Correct the target and new migration parent. Also version canonical request/content hashing so later normalization or serializer changes cannot invalidate old replay identities or reinterpret approved hashes. This preserves the already-correct separation from execution snapshots.

These are correctness and verification requirements. Relational layout, inline editing, provenance presentation and admission numbers remain genuine taste choices.

Full verification still requires actual PostgreSQL/API/browser checks and **separate real API and live-browser generations**. Runtime key/model were absent at intake; development Codex authentication supplies no runtime credential. No tests, edits, commits, external messages or subagents were performed.