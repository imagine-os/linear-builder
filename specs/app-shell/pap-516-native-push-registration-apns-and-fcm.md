---
identifier: "PAP-516"
title: "Native push registration (APNs and FCM) behind `NativeCapabilitiesPort.notify`, device token storage per principal and a bridge from the push transport to OS notifications"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-259", "PAP-260"]
blocks: []
key: "r4/app-shell/native-push-registration"
url: "https://linear.app/paperos/issue/PAP-516/native-push-registration-apns-and-fcm-behind"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:56.055Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-516: Native push registration (APNs and FCM) behind `NativeCapabilitiesPort.notify`, device token storage per principal and a bridge from the push transport to OS notifications

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (past 2026-10-01). PAP-381 builds the server-to-client push transport for connected clients and PAP-136 the notification centre; a closed mobile app receives nothing. This issue registers device tokens through the native capability shim and forwards notification deliveries to APNs and FCM.

**Scope**

In:

* `notify.register()` in the PAP-259 capability returning a device token via the Tauri notification plugin on iOS and Android; table `push_device` (`principal_id`, `platform`, `token`, `app_version`, `last_seen`) with RLS.
* Delivery adapter in `packages/email`-style provider shape: `PushProvider` with `ApnsProvider` (token-based auth, key in sops) and `FcmProvider` (service account), selected per device; `notification_delivery` channel `push` (PAP-136).
* Tap handling: payload carries the route; `onDeepLink` (PAP-257 API) navigates; badge count set from `unreadCount`.

Out: web push (PWA) for browsers, marketing push, the notification kinds and preferences (PAP-136).

**Spec**

* Tokens rotate: `register()` on every launch upserts; stale tokens (APNs 410, FCM `UNREGISTERED`) are deleted.
* Payloads contain no PII beyond the notification title; body fetched on open when `sensitive`.
* Quiet hours and preferences (PAP-324) apply before sending; a delivery row records provider response.
* Preview builds use APNs sandbox and an FCM test project.

**Interface contract**

Provides: `push_device` table, `PushProvider` interface and two adapters, channel `push`; consumed by PAP-136 (channel), PAP-381 (fallback when disconnected), PAP-260 (capability wiring).

Consumes: capability shim and plugins (PAP-259, PAP-260), push transport (PAP-381), notification centre and preferences (PAP-136, PAP-324), sops (PAP-25), signing entitlements (PAP-369).

**Definition of done**

* Emulator and simulator recordings: comment mention with the app closed shows an OS notification; tap opens the record.
* Stale token cleanup tested with provider fixtures; `docs/shell/mobile.md` push section; CHANGELOG; Linear comment.

**Test plan**

* Unit: provider payload builders; token rotation and cleanup; quiet-hours gate.
* E2E: Maestro with a mock provider endpoint asserting a delivery row and tap navigation.

**Demo**

Reviewer closes the app on the emulator, mentions themselves from the web, the notification arrives and opens the comment. Under 2 minutes.

**Edge cases**

* User declines notification permission: `status: denied` and settings deep link (PAP-260 rule); no token row.
* Same principal on three devices: each gets the push; read state syncs back through PAP-136.

**Dependencies**

Hard: PAP-260, PAP-259. Soft: PAP-381 (disconnected-client fallback wiring), PAP-136, PAP-324, PAP-369, PAP-257.

**Agent**

Builder: Forge (Tauri Smith) with Nova on the transport. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
