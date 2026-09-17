---
identifier: "PAP-374"
title: "Linear sync: conflict rule (Linear wins), sync status page and runbook"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: "PAP-101"
children: []
blockedBy: ["PAP-372", "PAP-373"]
blocks: []
key: "pm-linear/linear-sync/conflicts"
url: "https://linear.app/paperos/issue/PAP-374/linear-sync-conflict-rule-linear-wins-sync-status-page-and-runbook"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:42.475Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-374: Linear sync: conflict rule (Linear wins), sync status page and runbook

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Make the two-way sync safe and observable: when both sides changed the same field, Linear wins and PaperOS records a conflict with an in-app notice; a status page shows lag, outbox depth, dead letters and conflicts; and a runbook explains backfill, retry, dead-letter handling and key rotation.

**Scope**

* In: conflict detection in the inbound path, `pm_sync_conflict` table, `specs/pm/sync-status.spec.yaml` page at `/pm/sync`, `pm.sync.status()` procedure, `docs/pm/linear-sync.md`.
* Out: cutover tooling (flipping the winner), notification delivery beyond the event (PAP-136).

**Spec**

* Rule: on inbound `update`, for each field in `updatedFrom`, if a `pm_outbox` row for the same entity touching that field is `pending` or was `sent` after `external_updated_at` of the last applied inbound change, discard the local value, apply Linear's, and insert `pm_sync_conflict(entity_type, entity_id, field, local_value, remote_value, resolved: "linear", at)`; emit `pm.sync.conflict`.
* Status: `{ lagSeconds (now minus last inbound applied), outboxDepth, deadCount, conflicts24h, lastWebhookAt, backfillState }`; page renders cards plus a table of dead rows with a `Retry` action and conflicts with a link to the entity; refresh every 10 s.
* Runbook: first backfill, resuming, retrying dead rows, rotating the API key and webhook secret, what "Linear wins" means for board users.

**Interface contract**

* Provides: `pm.sync.status()`, `pm.sync.conflicts({ since })`, table `pm_sync_conflict`, event `pm.sync.conflict { entity, id, field }`, page `/pm/sync` (staff.admin), the "changed in Linear" toast hook consumed by PAP-102.
* Consumers: PAP-102 toast and banner, PAP-136 notification kind `pm.sync.conflict`, PAP-306 (dead count and lag in its health section).
* Requires: both sibling children, PAP-114 spec schema for the page, PAP-71 data display components.

**Definition of done**

* Simultaneous edit test: edit a title in both systems within the same second; Linear's value wins locally and one conflict row exists.
* Status page screenshots at 375, 768 and 1280 px in light and dark; Playwright coverage through gate 3.
* Runbook reviewed by Nova; changelog; Linear comment with screenshots.

**Test plan**

* Unit: conflict rule matrix (pending, sent-before, sent-after, disjoint fields).
* Integration: staged race with recorded webhook and outbox timestamps.
* e2e (Playwright): status page renders, `Retry` re-queues a dead row; run at 375 and 1280 px.
* Visual: three widths, two themes.

**Demo**

Rename an issue in PaperOS and, within a second, in Linear; refresh PaperOS to see Linear's title and a conflict entry on `/pm/sync`; retry a dead row from the same page. Ninety seconds.

**Edge cases**

* Same value on both sides: not a conflict.
* Conflict on a field PaperOS does not surface (cycle): recorded, not notified.
* Clock skew: compare Linear timestamps only.
* Thousands of conflicts (bad script): table paginated; banner shows count.
* Status called while backfill runs: `backfillState: running` with progress.

**Dependencies**

Blocked by PAP-372, PAP-373. Soft: PAP-136.

**Agent**

Built by Nova (Views Engineer sub-agent); reviewed by Sentinel (Visual Inspector).

**Size**

S
