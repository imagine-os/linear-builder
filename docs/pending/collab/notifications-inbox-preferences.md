---
key: "collab/notifications/inbox-preferences"
title: "Inbox UI, bell badge and preferences page"
project: "collab"
parent: "PAP-136"
phase: "P2"
type: "Build"
priority: 2
size: null
surfaces: ["Customer", "Staff"]
milestone: "Knowledge surfaced everywhere"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
identifier: "PAP-323"
status: "created"
createdAt: "2026-09-17"
---

# Inbox UI, bell badge and preferences page

**Goal**

Give users the visible half of notifications (PAP-136): a bell with a live unread badge, a popover of the latest items, a full inbox with filters, and a preferences page where each kind is mapped to channels, all over the tables of PAP-136 work package 1 (the notification core).

**Scope**

In:

* `NotificationBell` with popover (latest 10, mark read, archive) in the console and portal shells (PAP-62, PAP-63).
* `/_app/inbox`: filters by kind and unread, grouped by day, keyboard navigation, bulk mark read.
* `/_app/settings/notifications`: matrix of kinds by channel (in-app, email, Slack), test send button.
* Live badge via Electric shape on `notification` for the current user (PAP-143) with 30 s polling fallback.
* oRPC `notifications.list|markRead|archive`, `preferences.get|set` (thin wrappers over core repositories).

Out: digests and quiet hours (sibling 2), Slack (sibling 3), delivery (core).

**Spec**

* Rows use the core's `Notification` type; no second schema.
* Popover `role="dialog"`; badge `aria-live="polite"` announcing counts at most once per 30 s.
* Under `md` the inbox is a full-screen list.

**Interface contract**

Exposes `NotificationBell`, `InboxList`, `PreferenceMatrix`, procedures above. Consumes `Notification`, `NotificationKind` registry and `resolvePreferences()` from PAP-136 work package 1 (the notification core), `subscribeShape` (PAP-143), shells (PAP-62, PAP-63), primitives (PAP-67).

**Definition of done**

* Badge updates within 2 s of a core insert; inbox and settings at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; Linear comment with screenshots.

**Test plan**

* Vitest: unread count derivation, day grouping across timezones, matrix state to preference rows.
* Integration: `callAs(userA)` cannot list userB's notifications.
* Playwright, two contexts: mention triggers a badge within 2 s; mark read clears it; toggle a kind off in settings and confirm the core suppresses the next one (via `/__test` clock and job run).
* Visual: Gate 3 baselines at the seven widths.

**Demo**

Get mentioned from a second account, watch the bell, open the popover, mark read, open the inbox and filter to mentions, open settings and switch email off for mentions. Under two minutes.

**Edge cases**

* 1,000 unread: badge shows 99+.
* Deleted source: item stays with "no longer available".
* Shape unavailable: polling fallback, no visible difference.

**Dependencies**

Notification core (hard). PAP-143, PAP-62, PAP-63 (soft). Blocks siblings 2 and 3 for UI slots.

**Agent**

Built by Nova with Iris on components. Reviewed by Sentinel (Visual Inspector).

**Size**

M: three screens over an existing API.
