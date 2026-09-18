---
identifier: "PAP-726"
title: "Follow model: watch records, threads and docs with auto-follow rules and watcher fan-out for replies and record changes"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-317", "PAP-725"]
blocks: []
key: "r4/collab/watchers-subscriptions"
url: "https://linear.app/paperos/issue/PAP-726/follow-model-watch-records-threads-and-docs-with-auto-follow-rules-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:31.819Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-726: Follow model: watch records, threads and docs with auto-follow rules and watcher fan-out for replies and record changes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Linear, Notion and GitHub notify subscribers, not just mentioned people. PaperOS has mentions (PAP-317) but no way to follow an invoice, a thread or a doc, so `comment.replied` and `record.updated` have nobody to reach. Add a watcher table, auto-follow rules and a recipient expander the notification core uses.

**Scope**

In: `watcher(tenant_id, user_id, entity_type, entity_id, reason: author|mention|assigned|manual, muted, created_at)` with RLS; `watchers.follow|unfollow|list` oRPC; `expandWatchers(entityRef)` hook registered with PAP-725 recipient expansion; auto-follow on thread create, mention and assignment; `FollowButton` for record headers and doc pages (`record.panel.tabs` slot and PAP-128 footer). Out: digest rules (PAP-324), presence (PAP-141).

**Spec**

* Auto-follow: thread author and every mentioned user follow the thread; the record's `owner` field (PAP-361 entity grammar) follows the record; `muted: true` overrides auto-follow and survives re-mention.
* `comment.replied` and `thread.resolved` recipients = thread watchers minus actor; `record.updated` (PAP-38 audit trigger topic) recipients = record watchers, collapsed by PAP-324's burst rule.
* Customers may follow only entities they can read; `can()` re-checked at fan-out so a revoked customer is `suppressed`.
* Watcher count shown on `FollowButton`; unfollow from any notification row (`notifications.unfollowSource`).
* Cap 200 watchers per entity; beyond that, only `manual` watchers are notified and a warning is logged.

**Interface contract**

Provides: `watcher` table, `watchers.*` procedures, `expandWatchers()`, `useWatch(entityRef)`, `FollowButton`. Consumes: recipient expansion hook and `Notification` (PAP-725), `comment_thread` and events (PAP-317), `EntityRef` (PAP-302), `can()` (PAP-59), slot `record.panel.tabs` (PAP-438), audit topic `record.updated` (PAP-38). Consumed by: PAP-323 (unfollow action), PAP-333 record detail header, PAP-197 support inbox.

**Definition of done**

* Reply to a thread notifies the author and a manual follower, not the replier; unfollow stops it.
* Screenshots of `FollowButton` states at 375 and 1280 in light and dark; axe clean.
* `docs/collab/notifications.md` gains a Following section; CHANGELOG entry; Linear comment.

**Test plan**

* Unit: auto-follow rules, mute precedence, cap behaviour, recipient set equality.
* Integration: RLS `callAs` matrix for follow and list; revoked customer suppressed at fan-out.
* E2E (Playwright, two contexts): B follows a record, A comments, B's bell increments (PAP-323) within 2 s; B mutes, A comments again, nothing arrives.

**Demo**

Open an invoice, click Follow, comment on it from another browser and watch the first browser's bell; unfollow and repeat. Under two minutes.

**Edge cases**

* Entity deleted: watchers rows soft-deleted with the entity's `deleted_at` cascade job.
* User removed from tenant: watchers purged by the PAP-58 membership removal handler.
* Thread with 50 mentions: 50 auto-follows, one notification each, no duplicates.

**Dependencies**

Hard: PAP-725, PAP-317. Soft: PAP-38, PAP-323, PAP-361, PAP-438.

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/notification-core` = PAP-725.
