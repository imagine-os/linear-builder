---
identifier: "PAP-600"
title: "Web Push and desktop notifications: VAPID keys, `push_subscription`, service-worker handler, permission prompt after an explicit action, sender job with 410 pruning and Tauri desktop OS notifications"
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
blockedBy: ["PAP-18", "PAP-599"]
blocks: ["PAP-836", "PAP-850"]
key: "r4/realtime/web-push"
url: "https://linear.app/paperos/issue/PAP-600/web-push-and-desktop-notifications-vapid-keys-push-subscription"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:14.897Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-600: Web Push and desktop notifications: VAPID keys, `push_subscription`, service-worker handler, permission prompt after an explicit action, sender job with 410 pruning and Tauri desktop OS notifications

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Second child of PAP-381: reach people when the app is closed. Notifications marked for the push channel are sent to browser subscriptions through Web Push and to Tauri desktop through OS notifications, with the permission prompt shown only after the user asks for it and dead subscriptions pruned on the first 410.

**Scope**

In: Table `push_subscription (user_id, endpoint, keys jsonb, ua, created_at, revoked_at)`, VAPID key pair through PAP-17 env (`VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`), oRPC `push.subscribe|unsubscribe|test`, service-worker `push` and `notificationclick` handlers in PAP-18's worker (deep link to the notification target), `EnableNotificationsButton` and preference wiring in PAP-136's preferences page (soft: portal notifications page from PAP-585), sender job `push.deliver` (PAP-43) consuming `notification.created` events with `channels.push`, `PushProvider` interface with `WebPushProvider` (`web-push` library), Tauri desktop path through `tauri-plugin-notification` (PAP-255) when the app is running, docs section.

Out: APNs and FCM device registration and adapters (PAP-516, deferred, which implements this issue's `PushProvider`), notification content and kinds (PAP-136), marketing push.

**Spec**

* Prompt only after clicking Enable notifications; the button explains what will be sent; denied permission is remembered and the button shows how to re-enable in browser settings.
* Push bodies contain title, body and a deep link only, never PII beyond the title (same rule as the live channel); payload under 4 KB; `urgency` from the notification kind.
* Delivery: within 30 s of the notification row; retry 3 times with backoff on 5xx; 404 or 410 marks the subscription revoked immediately; `PushProvider.send(device, message)` is the seam PAP-516 plugs `ApnsProvider` and `FcmProvider` into.
* Tauri desktop: when the desktop app is running it receives the event over the live channel and shows an OS notification through the plugin; no push service involved; clicking focuses the window and navigates.
* Test send `push.test` delivers a sample to the caller's own subscriptions for the preferences page.
* Subscriptions are per user per browser; sign-out unsubscribes the current browser; `session.revoked` (PAP-581) revokes the matching subscription by user agent.

**Interface contract**

Provides: Table `push_subscription`, procedures `push.*`, `PushProvider` interface and `WebPushProvider`, job `push.deliver`, service-worker handlers, `EnableNotificationsButton`, env names above.

Consumes: Live channel and kind registry (sibling), service worker (PAP-18), env schema (PAP-17), jobs (PAP-43), notification rows and preferences (PAP-136, soft), desktop plugin (PAP-255, soft), portal preferences page (PAP-585, soft), sessions (PAP-581, soft). Consumed by PAP-136, PAP-94 decision cards, PAP-88 digests.

**Definition of done**

* A notification created while the tab is closed arrives as a Web Push on Chrome desktop and Android Chrome; clicking it lands on the thread (recording).
* 410 from the mock push service prunes the subscription after one failure; permission prompt appears only after clicking Enable (Playwright).
* Tauri desktop shows an OS notification while running; docs; changelog; Linear comment with the video.

**Test plan**

* Unit: payload size guard and PII rule, retry classification (404, 410, 5xx), subscription dedupe by endpoint, urgency mapping.
* E2E: Playwright with a `web-push` test server: subscribe, trigger a mention from another account, assert delivery and click navigation; 410 path.

**Demo**

Enable notifications on the portal, close the tab, trigger a mention from another account, click the desktop notification and land on the thread. Under two minutes.

**Edge cases**

* Browser revokes permission later: next send returns 410; subscription revoked and the button reappears.
* Private window: subscription not persisted; button explains.
* Ten subscriptions for one user: each gets the push; the inbox marks read across devices via the live channel.

**Dependencies**

Blocked by PAP-599 and PAP-18 (hard). Soft: PAP-17, PAP-43, PAP-136, PAP-255, PAP-585, PAP-581. Consumed by PAP-516 (mobile adapters, deferred).

**Agent**

Builder: Nova (CRDT Engineer) with Forge (Ops Runner) for keys. Reviewer: Sentinel (Security Auditor for VAPID handling).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/app-shell/native-push-registration` = PAP-516, `r4/identity/portal-account-pages` = PAP-585, `r4/identity/sessions-stepup` = PAP-581, `r4/realtime/live-events-channel` = PAP-599.
