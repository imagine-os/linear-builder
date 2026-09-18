---
identifier: "PAP-610"
title: "Headless Yjs client for agents and jobs: `openRoomHeadless(room, credential)` in Node with transaction-origin attribution, batch edit helpers, a `doc.edit` job wrapper and the import writer used by Notion and template imports"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140", "PAP-586"]
blocks: []
key: "r4/realtime/headless-client"
url: "https://linear.app/paperos/issue/PAP-610/headless-yjs-client-for-agents-and-jobs-openroomheadlessroom"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:16.509Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-610: Headless Yjs client for agents and jobs: `openRoomHeadless(room, credential)` in Node with transaction-origin attribution, batch edit helpers, a `doc.edit` job wrapper and the import writer used by Notion and template imports

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Agents and jobs need to write documents, not only be seen near them: the Notion importer (PAP-419) writes pages into the runtime docs store, the spec agent (PAP-118) and content agent (PAP-192) draft text, the canvas reset (PAP-321) rewrites layout, and PAP-146 gives agents presence but no pen. Each would open `@hocuspocus/provider` from Node with its own auth and origin handling; this makes it one helper with attribution built in.

**Scope**

In: `packages/collab/src/headless/{client,batch,job}.ts`: `openRoomHeadless({ room, credential: { agentKey } | { serviceToken }, tenantId }) -> { doc, awareness?, transact(fn, origin), close }` over `@hocuspocus/provider` with `ws`, auth through `verifyApiKey` or service tokens (PAP-593, soft) on the server side (PAP-140 hook), origin `{ principalId, character?, issueKey?, sessionId?, reason }` attached to every transaction and persisted to `yjs_updates.origin` (PAP-607); batch helpers `replaceFragment(doc, 'default', richTextJson)` and `applyMarkdown(doc, md)` built on the editor's converters (PAP-604, soft); job `doc.edit({ room, op, payload, reason })` on PAP-43 with idempotency by `(room, op hash)`; optional presence join through PAP-146's client; rate limit per agent key on writes (PAP-140 throttle); `docs/platform/realtime/headless.md`.

Out: Agent presence visuals (PAP-146), the importers' mapping logic (migration), doc store routes (PAP-379), permission rules (PAP-227, consumed).

**Spec**

* Every write requires `document.write` for the principal behind the credential; `connection.readOnly` connections throw on `transact` instead of silently dropping; agent writes require a `reason` (PAP-38 rule) stored in the origin.
* `transact` batches into one Yjs transaction so peers see one change and undo managers treat it as one step; large imports chunk at 1 MB per transaction with a short sleep to respect the server throttle.
* Connection lifecycle: connect, wait for `synced`, apply, wait for the server `stored` acknowledgement (PAP-140 `onStoreDocument` hook echo), then close; timeouts fail the job with a retryable error.
* Awareness optional: when `presence: true` the client joins with PAP-146's `agent` payload and activity `editing`; off by default for bulk imports to avoid presence noise.
* Test double: the same API against an in-memory provider from PAP-612 for unit tests without a server.

**Interface contract**

Provides: `openRoomHeadless`, `replaceFragment`, `applyMarkdown`, job `doc.edit`, origin schema `HeadlessOrigin`, test double binding.

Consumes: Collab server auth hook, throttle and store acknowledgement (PAP-140), agent keys (PAP-586), service tokens (PAP-593, soft), converters (PAP-604, soft), history origin column (PAP-607, soft), jobs (PAP-43, soft), presence client (PAP-146, soft), test kit (PAP-612, soft). Consumed by PAP-419, PAP-379, PAP-118, PAP-192, PAP-321, PAP-208, PAP-426.

**Definition of done**

* A job replaces a doc's content from markdown while a browser has it open: the browser sees one transaction, the caret survives, history shows the agent as author with the reason (Playwright plus job run on the compose stack).
* Read-only credential throws; missing reason refused; 5 MB import chunks without tripping the throttle; idempotent rerun makes no second change.
* Docs; changelog; Linear comment with the recording.

**Test plan**

* Unit: origin schema, chunking, lifecycle state machine with timeouts, idempotency key derivation, read-only refusal.
* E2E: Notion-style import of 50 pages through `doc.edit` jobs into the docs store with a browser watching one page; presence join optional path with PAP-146's mock.

**Demo**

Run `pnpm tsx examples/headless-edit.ts doc:acme:page:welcome --markdown hello.md --reason 'demo'` while the page is open in a browser and watch the content replace in one step with the agent badge in history. Under a minute.

**Edge cases**

* Server restarts mid-import: provider reconnects and the pending transaction reapplies; the `stored` acknowledgement guards completion.
* Room over the 20 MB cap after the write: server returns `4413`; job fails with the size and no partial state (transaction rejected).
* Agent key revoked mid-job: `4401`, job fails retryable; a new key is minted by the orchestrator on retry.

**Dependencies**

Blocked by PAP-140 and PAP-586 (hard). Soft: PAP-43, PAP-146, PAP-593, PAP-604, PAP-607, PAP-612. Consumed by PAP-419, PAP-379, PAP-118, PAP-192, PAP-321.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Code Reviewer; Security Auditor for credential handling).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/identity/agent-keys` = PAP-586, `r4/identity/service-principals` = PAP-593, `r4/realtime/doc-history` = PAP-607, `r4/realtime/editor-features` = PAP-604, `r4/realtime/test-kit` = PAP-612.
