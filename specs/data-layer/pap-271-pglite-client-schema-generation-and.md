---
identifier: "PAP-271"
title: "PGlite client, schema generation and read hooks (useShape, useLiveQuery)"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Developer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: "PAP-36"
children: []
blockedBy: ["PAP-31", "PAP-270"]
blocks: ["PAP-272"]
key: "child/PAP-36/16"
url: "https://linear.app/paperos/issue/PAP-271/pglite-client-schema-generation-and-read-hooks-useshape-uselivequery"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:36.535Z"
---

# PAP-271: PGlite client, schema generation and read hooks (useShape, useLiveQuery)

**Goal**

Ship `packages/sync` client pieces: `defineShape`, the shape registry, `SyncClient` lifecycle, PGlite 0.3 with IndexedDB and Tauri file persistence, `pnpm gen:pglite` schema generation from Drizzle with hash-based reset, and `useShape` and `useLiveQuery` hooks.

**Scope**

In: client package, generated `schema.sql`, hooks, persistence adapters, core shapes `workspaces`, `memberships`, `users`, `files`, demo route reads.

Out: proxy (child 1), writes (child 3).

**Spec**

* `gen:pglite` emits SQL for registered tables only; hash stored in `_sync_meta`; mismatch resets local data, keeps `_outbox`.
* `useLiveQuery(sql, params)` over PGlite live extension; `useShape(shape)` returns `{ rows, status }`.
* Tauri persistence in app data dir; Android falls back per PAP-31 findings.

**Interface contract**

Provides: `defineShape`, `registerShape`, `useShape`, `useLiveQuery`, `SyncClient`, generated schema file. Consumes: proxy (child 1), ADR decision (PAP-31), `useOnline` (PAP-18). Consumed by PAP-143, PAP-163.

**Definition of done**

* Demo route lists workspaces from PGlite; bench of 2k-row initial load under 1.5 s on CI committed.
* Vitest for registry, hash reset, hooks; screenshots of the demo route at seven widths.

**Test plan**

* Unit: hash reset preserves outbox; hook states loading, ready, error.
* Integration (CI compose with Electric): full shape load into PGlite, live update after a server write appears within 2 s.
* Bench: 2k rows timed.
* Visual: demo route at seven widths.

**Demo**

Reviewer opens `/_app/sync-demo`, sees workspaces load instantly on second visit, edits one in Drizzle Studio and watches the list update live. Under a minute.

**Edge cases**

* Safari private mode: in-memory PGlite with banner.
* Storage above 200 MB: warning and `columns` trimming advice.

**Dependencies**

Child 1 (hard), PAP-31. Blocks child 3.

**Agent**

Built by Forge with Nova. Reviewed by Sentinel.

**Size**

M
