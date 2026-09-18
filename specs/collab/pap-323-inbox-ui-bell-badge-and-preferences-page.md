---
identifier: "PAP-323"
title: "Inbox UI, bell badge and preferences page"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: "PAP-136"
children: []
blockedBy: ["PAP-131", "PAP-319", "PAP-725"]
blocks: ["PAP-324"]
key: "collab/notifications/inbox-preferences"
url: "https://linear.app/paperos/issue/PAP-323/inbox-ui-bell-badge-and-preferences-page"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-323: Inbox UI, bell badge and preferences page

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

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

*Round 4 amendment (2026-09-18):*
Rows support snooze (`snoozed_until`, presets 1 h, tomorrow 09:00, next Monday) and "mark all read" for the current filter; a snoozed row returns to unread at the time and is exempt from PAP-324 quiet hours. Add an "unfollow source" action once PAP-726 lands.

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

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/watchers-subscriptions` = PAP-726.
