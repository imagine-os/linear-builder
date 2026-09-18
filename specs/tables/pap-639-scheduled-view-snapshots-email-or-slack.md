---
identifier: "PAP-639"
title: "Scheduled view snapshots: email or Slack a view or dashboard export on a cron with the recipient's permissions"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-388", "PAP-625", "PAP-725"]
blocks: []
key: "r4/tables/scheduled-view-snapshots"
url: "https://linear.app/paperos/issue/PAP-639/scheduled-view-snapshots-email-or-slack-a-view-or-dashboard-export-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:20.791Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-639: Scheduled view snapshots: email or Slack a view or dashboard export on a cron with the recipient's permissions

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). Airtable, ClickUp and Monday send a saved view or dashboard to a channel every Monday. Compose the existing pieces: automation schedule trigger, export writers, dashboard print route and the notification centre.

**Scope**

In: automation action `view.snapshot({ viewId | dashboardId, format: 'csv'|'xlsx'|'pdf'|'png', recipients: userId[] | channel })` registered via PAP-389 `defineAction`; "Schedule" entry in the export menu that creates an automation with a schedule trigger; per-recipient rendering.

Out: public distribution, inline HTML tables in email (attachment only), retention beyond 7 days.

**Spec**

* The action runs once per recipient as that recipient's principal (PAP-60 impersonation for system jobs with audit reason `snapshot:<automationId>`) so permissions and field masks apply; files via the export issue or `/print/d/:id` PDF (PAP-387) and PNG through the Gate 3 Playwright image.
* Delivery through PAP-136 kinds `view.snapshot` (in-app with attachment, email, Slack webhook); attachments over 10 MB become a signed link.
* Schedule UI: preset (daily, weekly, monthly) plus cron, timezone from tenant; the export menu shows existing schedules with pause and delete.
* Idempotent per `(automation_id, trigger_event_id)` via PAP-388; failures surface in the run log.

**Interface contract**

Provides: action `view.snapshot`, `ScheduleSnapshotDialog`, notification kind `view.snapshot`. Consumes: export writers (PAP-625), schedule trigger and runtime (PAP-388), actions (PAP-389), notifications (PAP-136), print route (PAP-387), impersonation (PAP-60).

**Definition of done**

* Action and dialog green in Vitest, integration and Playwright with a fixed clock; screenshots at 375 and 1280; `docs/views/snapshots.md`; CHANGELOG.

**Test plan**

* Unit: recipient fan-out; format selection; size threshold to link.
* Integration: weekly schedule across a DST boundary fires once; recipient without access receives a "no access" note, not data.
* E2E: schedule the demo dashboard weekly to two users, advance the clock, open the in-app notification with the PDF.

**Demo**

Reviewer schedules a CSV of Open tasks every Monday, fires it manually and opens the email in Mailpit. Under two minutes.

**Edge cases**

* View deleted: automation disabled with reason.
* Recipient removed from tenant: skipped, run continues.

**Dependencies**

Export issue (hard), PAP-388 (hard), PAP-136 (hard). Soft: PAP-389, PAP-387, PAP-60. Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/view-export-csv-xlsx-ics-print` = PAP-625.
