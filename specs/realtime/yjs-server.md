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
blockedBy: ["PAP-139", "PAP-224", "PAP-229", "PAP-25", "PAP-57", "PAP-59"]
blocks: ["PAP-131", "PAP-132", "PAP-141", "PAP-142", "PAP-145", "PAP-147"]
key: "realtime/yjs-server"
url: "https://linear.app/paperos/issue/PAP-140/deploy-a-hocuspocus-yjs-server-with-auth-hook-postgres-persistence-and"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-140: Deploy a Hocuspocus (Yjs) server with auth hook, Postgres persistence and room-per-document

**Goal**

Stand up the multiplayer backbone: a self-hosted Hocuspocus server that authenticates every WebSocket connection with a Better Auth session or agent API key, persists one Yjs document per room to Postgres, and enforces per-document read/write permissions. Every later realtime feature (presence, collaborative text, canvas, multi-window) connects to this server.

**Scope**

In:
- `apps/collab-server/` (Node 22, TypeScript) running `@hocuspocus/server` 3.x with extensions `@hocuspocus/extension-database` (custom Postgres store via Drizzle), `@hocuspocus/extension-logger`, `@hocuspocus/extension-throttle`, and `@hocuspocus/extension-redis` behind a flag for horizontal scaling.
- Room naming `doc:<tenantId>:<entityType>:<entityId>`; one Yjs doc per room; awareness enabled.
- Auth hook (`onAuthenticate`) validating a Better Auth session token or `pos_agent_` API key, resolving a principal, and calling the permission engine for `document.read` / `document.write`; read-only connections get `connection.readOnly = true`.
- Persistence: table `yjs_documents(room text pk, tenant_id uuid, state bytea, vector bytea, updated_at, size_bytes)` plus `yjs_updates` append log (compacted into `state` every 500 updates or 60 s, whichever first). RLS by tenant per `data-layer/rls-tenancy`.
- Docker image and Coolify service definition in `ops/compose/collab-server.yml`, exposed at `wss://collab.<domain>` behind Caddy; health endpoint `GET /healthz`; Prometheus metrics at `/metrics` (connections, rooms, messages/s, persistence latency).
- Client package `packages/collab/src/provider.ts` exporting `createDocProvider({ room, token })` wrapping `@hocuspocus/provider` with reconnect/backoff and an `y-indexeddb` local cache.

Out: presence UI (`realtime/presence`), editors, load tuning (`realtime/load-test`), Electric record sync.

**Spec**

- Server config: `port 1234`, `timeout 30000`, `debounce 2000`, `maxDebounce 10000`, `quiet true`; `onLoadDocument` reads `state` from Postgres, `onStoreDocument` writes `Y.encodeStateAsUpdateV2`; `onChange` appends to `yjs_updates`.
- Token passed as `token` in the provider handshake; server verifies via `packages/auth` `verifySessionToken()` or `verifyApiKey()`; `context` carries `{ principalId, principalType, tenantId, scopes }` used by all later hooks.
- Permission check reuses `packages/permissions` `can(principal, action, resource)`; resource derived from the room name; unknown entity types are rejected (`4403`).
- Limits: 2 MB max message, 20 MB max document (reject with `4413` and emit `collab.document.too_large`), 100 connections per principal.
- Room lifecycle: unload after 30 s with zero connections; `DELETE /admin/rooms/:room` (admin scope) forces unload and snapshot.
- Env via `app-shell/env-config`: `COLLAB_DATABASE_URL`, `COLLAB_REDIS_URL?`, `COLLAB_PUBLIC_URL`, `AUTH_BASE_URL`.
- Docs: `docs/platform/realtime/server.md` with a sequence diagram (connect, auth, load, sync, store) and a runbook.

**Definition of done**

- `docker compose up collab-server` connects from `apps/web` on localhost; two browsers editing a `Y.Text` converge.
- Vitest integration tests: auth rejects expired token, read-only principal cannot write (update dropped and logged), persistence round-trip after server restart, compaction reduces `yjs_updates` rows.
- RLS test proves tenant A cannot load tenant B's room even with a forged room name.
- Deployed on the VPS at `wss://collab.<domain>` with TLS; `/healthz` monitored by `data-layer/observability`.
- Metrics visible on a Grafana panel; screenshot attached to the PR.
- Provider reconnects within 5 s after the server restarts (Playwright test toggles the container).
- Docs, changelog entry, and a Linear comment with the wss URL and demo instructions.

**Edge cases**

- Token expires mid-session: server sends `4401`, provider refreshes the session via Better Auth and reconnects without losing local edits.
- Postgres unavailable on `onStoreDocument`: retry with backoff, keep the doc in memory, alert after 3 failures; never drop updates silently.
- Two server instances without Redis: reject start with a clear error when `REPLICAS > 1` and no Redis URL.
- Client sends updates for a room it authenticated for but whose permission has since been revoked: re-check permissions every 5 minutes and on `permission.changed` events.
- Corrupt state blob: fall back to replaying `yjs_updates`; if that fails, quarantine the row and start empty with an audit event.
- Room names with unexpected characters or over 255 bytes are rejected.

**Dependencies**

- `identity/better-auth` (session/API-key verification), `identity/rbac-abac` (permission engine), `data-layer/drizzle-schema` and `data-layer/rls-tenancy` (tables and policies), `app-shell/env-config` (secrets), `realtime/realtime-research` (encoding decision). Consumed by `realtime/presence`, `realtime/collab-text`, `collab/canvas-view`, `realtime/multi-window-sync`.

**Agent**

Builder: Forge (Ops Runner sub-agent) for deployment and persistence, pairing with Nova (CRDT Engineer) for the provider. Reviewer: Sentinel (Security Auditor) on auth and RLS; Sentinel (Code Reviewer) on the rest.

**Size**

M: well-trodden library integration, but auth, RLS and deployment must all be right.
