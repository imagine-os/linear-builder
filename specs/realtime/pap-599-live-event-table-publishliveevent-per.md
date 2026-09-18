---
identifier: "PAP-599"
title: "`live_event` table, `publishLiveEvent()`, per-user Electric shape with SSE fallback, `useLiveEvents()` and `useJobProgress()` hooks, TTL job and the `LiveEventKind` registry"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: "PAP-381"
children: []
blockedBy: ["PAP-143", "PAP-267", "PAP-270", "PAP-326", "PAP-328"]
blocks: ["PAP-600"]
key: "r4/realtime/live-events-channel"
url: "https://linear.app/paperos/issue/PAP-599/live-event-table-publishliveevent-per-user-electric-shape-with-sse"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:54:36.377Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-599: `live_event` table, `publishLiveEvent()`, per-user Electric shape with SSE fallback, `useLiveEvents()` and `useJobProgress()` hooks, TTL job and the `LiveEventKind` registry

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First child of PAP-381 and the part four consumers poll for today: one server-to-client channel for notifications, job and import progress and agent status. Producers write a row, the row streams to the right user through an Electric shape, and when shapes are unavailable an SSE endpoint delivers the same rows, so `useLiveEvents()` has one output regardless of transport. Web Push is the sibling; mobile push lives in app-shell.

**Scope**

In: Table `live_event (id uuidv7, tenant_id, user_id?, kind, payload jsonb, created_at, expires_at)` with RLS and an index on `(user_id, created_at)`, `publishLiveEvent({ kind, tenantId, userId?, payload })` in `packages/sync/live/`, `LiveEventKind` registry (`notification.created`, `job.progress`, `job.finished`, `agent.status`, `import.progress`), per-user shape `live_events` registered through PAP-326 with `where user_id = <principal>` (proxy support added in PAP-270), `GET /api/live` SSE fallback with `Last-Event-ID`, hooks `useLiveEvents(kinds?)` and `useJobProgress(jobId)`, TTL job `live.prune` (24 h, PAP-43), sink adapter for the outbox dispatcher (PAP-556), `docs/platform/realtime/push.md` decision matrix (shape, SSE, push).

Out: Web Push, desktop OS notifications and mobile push (siblings), in-app inbox UI (PAP-136), marketing push.

**Spec**

* Delivery to open clients within 2 s through the shape; SSE fallback chosen automatically when the shape subscription fails twice (Firefox private mode, corporate proxies) and produces identical hook output; the transport in use is exposed to `useConnectionStatus()` (PAP-609).
* Payloads under 4 KB and free of PII beyond a title (PII refinement from PAP-559, soft); larger content is referenced by `EntityRef`.
* Per-user shapes: the proxy appends `user_id = <principal>` for shapes marked `perUser: true` in the registry, in addition to `tenant_id`; tenant-wide events (`userId` null) are a second shape filtered by audience (`agent.status` for staff only).
* Bursts: 10,000 events in a second are coalesced per kind per second for `job.progress` and `import.progress` (last value wins); other kinds are never dropped.
* `useJobProgress(jobId)` returns `{ percent, message, state }` from the latest `job.progress` and `job.finished` events for that job; PAP-43 emits them from `JobContext.progress()`.
* Prune job deletes expired rows hourly; Electric handles deletes as tombstones so clients drop them.

**Interface contract**

Provides: `publishLiveEvent()`, `useLiveEvents()`, `useJobProgress()`, `LiveEventKind` registry and `defineLiveEventKind()`, route `GET /api/live`, table `live_event`, job `live.prune`, dispatcher sink `live`.

Consumes: Shape registry and hooks (PAP-326), shape proxy with per-user predicate (PAP-270), API and SSE route (PAP-267), jobs and `JobContext.progress()` (PAP-43, soft), outbox dispatcher sink (PAP-556, soft), notification rows (PAP-136, soft). Consumed by the siblings, PAP-136, PAP-199, PAP-113, PAP-96, PAP-288, PAP-591, PAP-572.

**Definition of done**

* `publishLiveEvent` reaches a subscribed client within 2 s via shape and via forced SSE fallback (compose stack with Electric); TTL job deletes expired rows.
* Import progress bar in PAP-199's UI updates from 0 to 100 without polling (Playwright asserts no repeated `GET` calls); a tenant-wide `agent.status` event is not visible to a customer context.
* Docs decision matrix; changelog; Linear comment with the recording.

**Test plan**

* Unit: kind registry and payload size guard, coalescing per kind per second, SSE reconnect with `Last-Event-ID`, per-user predicate rendering, transport selection state machine.
* E2E: two contexts: staff sees `agent.status`, customer does not; progress bar test; SSE forced by blocking the shape route and asserting identical DOM updates.

**Demo**

Start a CSV import and watch the progress bar move without refresh; block `/api/sync/shape` in DevTools, reload and watch the same bar move over SSE. Under two minutes.

**Edge cases**

* User signed in on two devices: both shapes receive the row; the notification inbox (PAP-136) deduplicates by id.
* Electric restarts mid-stream: handle 409 and resubscribe (PAP-328); SSE reconnects with the last id.
* Event for a user who lost tenant access: RLS hides it; `permission.changed` triggers resubscribe.

**Dependencies**

Blocked by PAP-326, PAP-270, PAP-267 (hard). Soft: PAP-43, PAP-136, PAP-556, PAP-559, PAP-609. Blocks the sibling PAP-600.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Code Reviewer; Security Auditor for the per-user predicate).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 6 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-outbox-dispatcher` = PAP-556, `r4/data-layer/local-data-protection` = PAP-572, `r4/data-layer/pii-registry` = PAP-559, `r4/identity/permission-propagation` = PAP-591, `r4/realtime/connection-status` = PAP-609, `r4/realtime/web-push` = PAP-600.
