---
identifier: "PAP-475"
title: "Publish @paperos/contract-realtime v0.1 with manifest"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-139", "PAP-140", "PAP-433"]
blocks: ["PAP-146", "PAP-149", "PAP-321", "PAP-411", "PAP-478", "PAP-481"]
key: "module/realtime/contract"
url: "https://linear.app/paperos/issue/PAP-475/publish-paperoscontract-realtime-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:58:04.356Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-475: Publish @paperos/contract-realtime v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-realtime` v0.1 and the `realtime` module manifest so every other module codes against a versioned package instead of `apps/collab-server, packages/collab (presence, window bus), packages/sync extensions` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `high`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/realtime/` published as `@paperos/contract-realtime` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-realtime', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Nova', project: 'realtime' }`, `swapRisk: 'high'`, `kind: 'runtime and service'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/realtime.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-139, PAP-140 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `CollabDocPort`: `openRoom(roomName)`, `close`, `awareness`, room-name grammar `<entityType>:<entityId>`, 20 MB cap, auth hook input (PAP-140, PAP-142)
* `PresencePort` (cursors, avatars, selections, viewers; PAP-141) and `FollowPort` (PAP-149)
* `LiveRecordPort`: `useLiveRecords(shape)`, shape registry additions, `ReconcilerPort` with `sync.conflict` semantics (PAP-326 to PAP-328, PAP-144)
* `PushTransportPort` (server to client notifications and job progress; PAP-381) and `WindowBusPort` (BroadcastChannel and Tauri events; PAP-145)
* `OfflineQueuePort` status (PAP-148)

Events declared with `defineTopic()` (payload schemas, version 1): `sync.conflict`, `presence.joined|left`, `doc.saved`, `push.delivered`.

Requires (manifest `requires[]`): \* `@paperos/contract-data-layer` ^0.1 (shapes, outbox, idempotency)

* `@paperos/contract-identity` ^0.1 (auth hook, `can` for rooms)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-realtime@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.realtime`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-139 (Benchmark Yjs vs Automerge vs Loro for document CRDT and wri), PAP-140 (Deploy a Hocuspocus (Yjs) server with auth hook, Postgres pe). Consumed by: PAP-321 (canvas overlay), PAP-146 (agents as participants), PAP-149 (follow mode), PAP-411 (support chat), PAP-142 rich text, PAP-131 comments live updates, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (six room names (valid and malformed), three awareness traces, four reconciler cases (clean, stale, conflict, offline replay), one 19 MB and one 21 MB document, two window-bus sequences); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Forge confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/realtime.md` generated; short ADR `docs/adr/00xx-contract-realtime.md` recording what was pinned.
* Comments on PAP-321, PAP-146, PAP-149, PAP-411 that their Interface contract sections now import from `@paperos/contract-realtime`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-139, PAP-140. Blocks PAP-321, PAP-146, PAP-149, PAP-411, `module/realtime/conformance` and `module/realtime/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Nova (Multiplayer & Realtime owner). Reviewed by Forge and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show realtime` and sees the ports; runs the reconciler fixtures through the reference implementation in the contract and gets the four expected outcomes. Under a minute.
