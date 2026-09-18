---
identifier: "PAP-734"
title: "Staff comment triage: unanswered customer threads as a saved view with assignment, age and SLA badges"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-161", "PAP-317"]
blocks: []
key: "r4/collab/customer-comment-triage"
url: "https://linear.app/paperos/issue/PAP-734/staff-comment-triage-unanswered-customer-threads-as-a-saved-view-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:33.151Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-734: Staff comment triage: unanswered customer threads as a saved view with assignment, age and SLA badges

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Customers will comment on invoices, appointments and records because PAP-131 lets them. Intercom and Zendesk exist because somebody has to see those comments in one place. Register `comment_thread` as a dataset and ship a staff triage view of unanswered `shared` threads with assignment and age, reusing the views engine instead of a bespoke inbox.

**Scope**

In: `registerDataset('comment_thread')` (PAP-161) in `packages/collab/comments/dataset.ts` with fields `anchor`, `status`, `visibility`, `created_by`, `last_activity_at`, `last_author_kind`, `assignee_id`, `waiting_on: customer|staff|none`, `age`; `assignee_id` column and `comments.threads.assign` procedure (PAP-317 extension); `ViewSpec` `staff-comment-triage` (grid, filter `visibility = shared and waiting_on = staff`, sort `last_activity_at asc`, saved as a shared view); route `/_staff/comments` rendering PAP-165's grid with a `RecordPanel` opening `ThreadView` (PAP-318); SLA badge from a tenant setting `comments.slaHours` (default 24). Out: email or chat channels (PAP-197), macros, customer-facing status.

**Spec**

* `waiting_on` derives from the last comment's `author_kind` and audience: last customer comment on an open thread means `staff`; last staff or agent comment means `customer`; resolved means `none`.
* Assignment sets `assignee_id`, emits `thread.assigned` (kind added to the notification core; recipients: assignee) and auto-follows the assignee (PAP-726 when merged).
* Row actions: open thread, assign to me, resolve; bulk assign through PAP-342's bulk bar when available.
* Agents may be assignees only when their character allows `comments.reply` (PAP-106 scope); customers never see the view (`staff.*` access in the page spec).
* Counts of overdue threads exposed as `comments.triage.stats` for the staff dashboard (PAP-363) and a `record.panel.tabs` badge.

**Interface contract**

Provides: dataset registration, `assignee_id`, `threads.assign`, `waiting_on` derivation, ViewSpec, route and page spec, `comments.triage.stats`, kind `thread.assigned`. Consumes: `comment_thread` and procedures (PAP-317), `ThreadView` (PAP-318), `registerDataset` and `ViewSpec` (PAP-161), grid (PAP-165, soft: plain table fallback), notification core (soft), `can()` (PAP-59), tenant settings (PAP-58). Consumed by: PAP-363 staff console dashboard, PAP-197 support inbox (later merge).

**Definition of done**

* Seeded threads (PAP-729) show the right `waiting_on`; assigning notifies the assignee; overdue badge appears past the SLA with the `/__test` clock.
* Screenshots at 375 (card list) and 1280 in light and dark; axe clean; `docs/collab/comments.md` gains a Triage section; CHANGELOG entry.

**Test plan**

* Unit: `waiting_on` derivation matrix, SLA computation across timezones, stats aggregation.
* Integration: dataset compiles through PAP-163 with the filter; `callAs(customer)` gets 403 on the view and never sees `internal` rows.
* E2E (Playwright): open the view, assign to me, reply from the panel, row leaves the list.

**Demo**

Sign in as a customer and comment on an invoice; sign in as staff, open Comments, see it at the top with its age, assign to yourself and reply; watch it drop out. Under two minutes.

**Edge cases**

* Thread anchor deleted: shown with `orphaned` badge, still assignable.
* 500 unanswered threads: grid paginates by cursor; stats cached 60 s.
* Grid engine unmerged: TanStack Table fallback with a documented TODO, as PAP-135 does.

**Dependencies**

Hard: PAP-317, PAP-161. Soft: PAP-318, PAP-165, PAP-163, PAP-725, PAP-726, PAP-729, PAP-342.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor for visibility).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/collab/collab-demo-seeds` = PAP-729, `r4/collab/notification-core` = PAP-725, `r4/collab/watchers-subscriptions` = PAP-726.
