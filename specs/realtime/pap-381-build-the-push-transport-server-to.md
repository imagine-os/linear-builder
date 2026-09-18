---
identifier: "PAP-381"
title: "Build the push transport: server-to-client notification and job-progress channel (Electric shape or SSE) plus Web Push and Tauri mobile push (APNs/FCM)"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: ["PAP-600", "PAP-599"]
blockedBy: ["PAP-143", "PAP-328"]
blocks: ["PAP-836", "PAP-850"]
key: "realtime/push-transport"
url: "https://linear.app/paperos/issue/PAP-381/build-the-push-transport-server-to-client-notification-and-job"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:34.463Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-381: Build the push transport: server-to-client notification and job-progress channel (Electric shape or SSE) plus Web Push and Tauri mobile push (APNs/FCM)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Replace polling with one live event channel: `useLiveEvents()` delivers notifications, import and job progress and agent status to open clients over an Electric shape (SSE fallback), and Web Push plus Tauri mobile push reach users when the app is closed. PAP-136, PAP-199, PAP-113 and PAP-20 currently fall back to polling or bundle a plugin with no server side.

**Scope**

In:

* Table `live_event(id uuidv7, tenant_id, user_id?, kind, payload jsonb, created_at, expires_at)` with a 24 h TTL job (PAP-43); producers write through `publishLiveEvent()`; Electric shape per user (PAP-143, PAP-270); SSE `GET /api/live` fallback when shapes are unavailable (Firefox private mode, corporate proxies).
* `useLiveEvents(kinds?)` and `useJobProgress(jobId)` in `packages/sync/live/`; `LiveEventKind` registry: `notification.created`, `job.progress`, `job.finished`, `agent.status`, `import.progress`.
* Web Push: `push_subscription(user_id, endpoint, keys, ua, created_at)`, VAPID keys via PAP-17, service worker handler in PAP-18's PWA, permission prompt only after an explicit user action.
* Tauri mobile: `tauri-plugin-notification` (PAP-260) device tokens registered to `push_device(user_id, platform, token)`; server sender adapters for APNs and FCM behind a `PushProvider` interface; APNs credentials are a Needs Justin ask filed by PAP-20's children, not here.
* Sender job: for `notification.created` events with `channels.push`, deliver to subscriptions and devices with retry and pruning of dead endpoints.

Out: in-app UI (PAP-136), marketing push, SMS.

**Spec**

* Delivery to open clients within 2 s; push within 30 s.
* Payloads under 4 KB; push bodies contain only title, body and deep link, never PII beyond the title.
* Dead endpoint (410) pruned after one failure; FCM invalid token pruned on `UNREGISTERED`.

*Round 4 amendment (2026-09-18):*
Per-user shapes need proxy support: PAP-270 appends only `tenant_id`; the registry entry for `live_events` declares `perUser: true` and the proxy then also appends `user_id = <principal>`; tenant-wide events are a separate audience-filtered shape. SSE fallback uses `Last-Event-ID` with the uuidv7 ordering. Work is split into PAP-599 and PAP-600; the Tauri mobile bullet (APNs, FCM, `push_device`) moves to PAP-516 (deferred), which implements the `PushProvider` interface from PAP-600.

**Interface contract**

Exposes: `publishLiveEvent({ kind, tenantId, userId?, payload })`, `useLiveEvents()`, `useJobProgress()`, `LiveEventKind` registry, `PushProvider { send(device, message) }` with `WebPushProvider`, `ApnsProvider`, `FcmProvider`, oRPC `push.subscribe|unsubscribe`, tables above. Consumes: shape subscriptions (PAP-143, PAP-270), API and SSE route (PAP-267), jobs (PAP-43), service worker (PAP-18), mobile plugin and tokens (PAP-260), secrets (PAP-17), notification rows (PAP-136 work package 1, the notification core) as the main producer, job progress hooks (PAP-43, PAP-199).

**Definition of done**

* Import progress bar in PAP-199's UI updates live without polling; a notification created while the tab is closed arrives as a Web Push on Chrome desktop and Android; Tauri Android receives an FCM push (APNs documented, pending credentials).
* `docs/platform/realtime/push.md` with the decision matrix (shape vs SSE vs push); changelog; Linear comment with a video.

**Test plan**

* Vitest: kind registry, payload size guard, endpoint pruning rules, provider selection per device, SSE reconnect with `Last-Event-ID`.
* Integration (compose stack): `publishLiveEvent` reaches a subscribed client within 2 s via shape and via forced SSE fallback; TTL job deletes expired rows; Web Push sent to a mock push service (`web-push` test server) and 410 prunes the subscription.
* Playwright: job progress bar on the import page updates from 0 to 100 without network polling (assert no repeated `GET` calls); permission prompt appears only after clicking "Enable notifications".
* Manual: Android emulator FCM delivery recorded.

**Demo**

Start a CSV import and watch the progress bar move without refresh; enable push, close the tab, trigger a mention from another account and see the desktop notification; click it to land on the thread. Under two minutes.

**Edge cases**

* Shape unavailable: SSE fallback with identical hook output.
* 10,000 events in a burst: coalesced per kind per second.
* User revokes browser permission: subscription marked `revoked` on the next 410.
* Tauri desktop: OS notifications via the plugin, no push service needed.

**Dependencies**

PAP-143 (hard). Soft: PAP-43, PAP-18, PAP-260, PAP-17, PAP-267, PAP-136 work package 1 (notification core). Consumed by PAP-136, PAP-199, PAP-113, PAP-96.

**Agent**

Built by Nova (CRDT Engineer) with Forge (Ops Runner) for providers and keys. Reviewed by Sentinel (Security Auditor for push payloads and VAPID handling).

**Size**

M: one table and hook family plus three provider adapters behind an interface.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/app-shell/native-push-registration` = PAP-516, `r4/realtime/live-events-channel` = PAP-599, `r4/realtime/web-push` = PAP-600.
