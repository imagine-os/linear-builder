---
identifier: "PAP-324"
title: "Digests, quiet hours and burst collapse"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: "PAP-136"
children: []
blockedBy: ["PAP-43", "PAP-323"]
blocks: ["PAP-325"]
key: "collab/notifications/digests-quiet-hours"
url: "https://linear.app/paperos/issue/PAP-324/digests-quiet-hours-and-burst-collapse"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:28.589Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-324: Digests, quiet hours and burst collapse

**Goal**

Make notifications (PAP-136) calm: per-kind hourly or daily digests, quiet hours in the user's timezone, collapse of bursts from one source, and per-tenant preferences with a global fallback.

**Scope**

In:

* `notification_preference.digest: none|hourly|daily` and `quiet_hours jsonb { start, end, tz }` columns and settings controls (added to sibling 1's matrix).
* Worker jobs (PAP-43): `notifications.digest.hourly`, `notifications.digest.daily` grouping held items per user and kind into one email (PAP-235 `renderEmail`) and one in-app row; quiet-hours hold and release job.
* Collapse rule in the core's pipeline hook: same kind and source within 10 minutes becomes one row with a count.
* Preference resolution: per-tenant row, else global row, else kind defaults.

Out: channels, inbox UI, Slack (siblings and core).

**Spec**

* Quiet hours computed with `@date-fns/tz`, DST-safe; a digest holds at most 50 items with a link to the inbox.
* Digest idempotency key `(user, kind, bucket)`.
* Collapse never merges items from different sources.

**Interface contract**

Exposes `resolvePreferences(userId, tenantId, kind)` extension with digest and quiet hours, jobs above, `collapse(notification, existing)` hook. Consumes the core's pipeline hooks and `notification_delivery`, `defineJob` and cron (PAP-43), `renderEmail` (PAP-235), settings controls (sibling 1).

**Definition of done**

* A mention during quiet hours is held and delivered at the window end; a daily digest email renders the grouped items; Linear comment with delivery logs.

**Test plan**

* Vitest: quiet hours across midnight and a DST change, digest grouping and the 50-item cap, collapse within and outside 10 minutes, preference fallback order, idempotency key stability.
* Integration: `/__test` clock (PAP-240) advanced past the window releases held items; digest job run twice produces one email.
* Snapshot: digest email HTML.

**Demo**

Set quiet hours to now, trigger a mention, see nothing arrive, advance the test clock past the window and watch it land; switch mentions to daily digest and run the job to receive one grouped email in Mailpit. Under two minutes.

**Edge cases**

* Timezone missing: fall back to tenant default.
* 300 items in a digest: 50 plus a link.
* User in two tenants: separate rows.

**Dependencies**

Notification core, PAP-43 (hard). PAP-235, PAP-240, sibling 1 (soft).

**Agent**

Built by Forge (Ops Runner) with Nova. Reviewed by Sentinel (Edge Case Hunter for time rules).

**Size**

S: jobs and rules over the core.
