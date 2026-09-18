---
identifier: "PAP-140"
title: "Deploy a Hocuspocus (Yjs) server with auth hook, Postgres persistence and room-per-document"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-57", "PAP-59", "PAP-139", "PAP-224", "PAP-229"]
blocks: ["PAP-131", "PAP-132", "PAP-141", "PAP-142", "PAP-145", "PAP-147", "PAP-317", "PAP-321", "PAP-354", "PAP-475", "PAP-481", "PAP-540", "PAP-563", "PAP-601", "PAP-603", "PAP-605", "PAP-607", "PAP-609", "PAP-610", "PAP-612"]
key: "realtime/yjs-server"
url: "https://linear.app/paperos/issue/PAP-140/deploy-a-hocuspocus-yjs-server-with-auth-hook-postgres-persistence-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:41.490Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-140: Deploy a Hocuspocus (Yjs) server with auth hook, Postgres persistence and room-per-document

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — security-sensitive title keyword: auth

**Goal**

Stand up the multiplayer backbone: a self-hosted Hocuspocus server that authenticates every WebSocket with a Better Auth session or agent key, persists one Yjs document per room to Postgres under RLS and enforces per-document read and write permissions. Presence, collaborative text, canvas and multi-window sync all connect here.

**Scope**

In:

* `apps/collab-server/` (Node 22) on `@hocuspocus/server` 3.x with `extension-database` (Drizzle Postgres store), `extension-logger`, `extension-throttle`, `extension-redis` behind a flag.
* Rooms `doc:<tenantId>:<entityType>:<entityId>`, `page:<tenantId>:<routeId>` (ephemeral) and `canvas:<appId>`; one Yjs doc per room; awareness on.
* `onAuthenticate`: verify session token or `pos_agent_` key, resolve principal, call PAP-59 `can()` for `document.read|write`; read-only connections get `connection.readOnly`.
* Persistence: `yjs_documents(room pk, tenant_id, state bytea, vector bytea, updated_at, size_bytes)` plus `yjs_updates` append log compacted every 500 updates or 60 s; RLS by tenant (PAP-34).
* Compose and Coolify definition `ops/compose/collab-server.yml` at `wss://collab.<domain>` behind Caddy; `/healthz`; Prometheus `/metrics`.
* Client `packages/collab/src/provider.ts` `createDocProvider({ room, token })` wrapping `@hocuspocus/provider` with backoff and `y-indexeddb`.

Out: presence UI (PAP-141), editors (PAP-142), load tuning (PAP-147), Electric record sync (PAP-143).

**Spec**

* Config `port 1234`, `timeout 30000`, `debounce 2000`, `maxDebounce 10000`; `onLoadDocument` reads `state`, `onStoreDocument` writes `encodeStateAsUpdateV2` (PAP-139), `onChange` appends to `yjs_updates`.
* `context = { principalId, principalType, tenantId, scopes }` for all hooks; unknown entity types rejected `4403`.
* Limits: 2 MB message, 20 MB document (`4413`, event `collab.document.too_large`), 100 connections per principal; permissions re-checked every 5 minutes and on `permission.changed`.
* Rooms unload 30 s after the last connection; `DELETE /admin/rooms/:room` forces snapshot and unload.
* Env via PAP-17: `COLLAB_DATABASE_URL`, `COLLAB_REDIS_URL?`, `COLLAB_PUBLIC_URL`, `AUTH_BASE_URL`.

*Round 4 amendment (2026-09-18):*
Add: (1) `createDocProvider` takes `getToken()` and on `4401` refreshes once and reconnects without losing buffered edits; (2) the provider listens to `visibilitychange`, `online` and Tauri `resume` and probes before retrying, using the shared `reconnectPolicy` from PAP-609; (3) permission re-check subscribes to the `permission.changed` topic (PAP-591) in addition to the 5-minute timer; (4) `verifySessionToken()` and `verifyApiKey()` come from PAP-223 and PAP-586 (amendment on PAP-223); (5) `yjs_updates` gains `principal_id` and `origin jsonb` so PAP-607 can attribute versions.

**Interface contract**

Exposes: `createDocProvider({ room, token, ephemeral? }) -> { provider, doc, awareness, status$ }`, `roomName(kind, tenantId, ...parts)` and `parseRoom()` in `packages/collab/rooms.ts`, close codes `4401` (expired), `4403` (denied), `4413` (too large); tables above; metrics `collab_connections`, `collab_rooms`, `collab_messages_total`, `collab_store_latency_seconds`; admin route above; event `collab.document.too_large`. Consumes: `verifySessionToken()` and `verifyApiKey()` from `@paperos/auth` (PAP-223), `can(principal, action, resource)` from `@paperos/permissions` (PAP-227), migrations and RLS helpers (PAP-32, PAP-34, PAP-228), env schema (PAP-17), VPS, Caddy and Coolify (PAP-25), encoding decision (PAP-139).

**Definition of done**

* `docker compose up collab-server` connects from `apps/web`; two browsers editing a `Y.Text` converge.
* RLS test proves tenant A cannot load tenant B's room even with a forged room name.
* Deployed at `wss://collab.<domain>` with TLS; `/healthz` monitored by PAP-40; Grafana panel screenshot on the PR.
* `docs/platform/realtime/server.md` with sequence diagram and runbook; changelog entry; Linear comment with wss URL and demo steps.

**Test plan**

* Vitest integration (Postgres in CI): expired token → `4401`; read-only principal's update dropped and logged; persistence round-trip across a server restart; compaction reduces `yjs_updates` below 500 rows; corrupt `state` falls back to replaying updates; oversize message → `4413`.
* RLS: PAP-34 harness with two tenants and a forged room name.
* Playwright: two contexts converge on `Y.Text` within 1 s; container restart via `docker compose restart` and the provider reconnects within 5 s without losing an offline edit.
* Ops: `/healthz` and `/metrics` scraped in the compose test; Caddy WebSocket idle timeout verified at 10 minutes idle.

**Demo**

Open the `/_app/dev/collab-demo` page in two browsers, type in one, see the other; stop the container, keep typing, start it and watch the text merge; open Grafana's collab panel. Under two minutes.

**Edge cases**

* Token expires mid-session: `4401`, provider refreshes and reconnects without losing edits.
* Postgres down on store: retry with backoff, keep in memory, alert after 3 failures.
* `REPLICAS > 1` without Redis: refuse to start.
* Room name over 255 bytes or with odd characters: rejected.

**Dependencies**

PAP-25, PAP-57, PAP-59, PAP-139 (hard, encoded). Soft: PAP-32, PAP-34, PAP-17, PAP-40. Blocks PAP-131, PAP-132, PAP-141, PAP-142, PAP-145, PAP-147 and the planned runtime docs store.

**Agent**

Builder: Forge (Ops Runner) for deployment and persistence with Nova (CRDT Engineer) for the provider. Reviewer: Sentinel (Security Auditor) on auth and RLS, Sentinel (Code Reviewer) on the rest.

**Size**

M: well-trodden library integration; auth, RLS and deployment must all be right.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/identity/agent-keys` = PAP-586, `r4/identity/permission-propagation` = PAP-591, `r4/realtime/connection-status` = PAP-609, `r4/realtime/doc-history` = PAP-607.
