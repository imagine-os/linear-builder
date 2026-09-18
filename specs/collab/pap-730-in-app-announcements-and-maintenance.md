---
identifier: "PAP-730"
title: "In-app announcements and maintenance banners: staff-authored, audience-targeted, scheduled, dismissible, flag-aware"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-55", "PAP-725"]
blocks: []
key: "r4/collab/announcements-banners"
url: "https://linear.app/paperos/issue/PAP-730/in-app-announcements-and-maintenance-banners-staff-authored-audience"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:32.769Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-730: In-app announcements and maintenance banners: staff-authored, audience-targeted, scheduled, dismissible, flag-aware

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Beamer and Headway pair the changelog with announcements: a banner or modal that staff write, target at an audience and schedule. PAP-133 generates changelogs from commits; nothing lets a tenant admin say 'maintenance Sunday 02:00' or 'new billing page for Pro customers'. Add a small announcement object rendered in the shell and delivered as a notification kind.

**Scope**

In: `announcement(id, tenant_id?, title, body_md, kind: banner|modal|toast, audiences[], starts_at, ends_at, dismissible, flag?, link?, created_by)` and `announcement_seen(user_id, announcement_id, seen_at)`; oRPC `announcements.list|create|update|archive|dismiss`; `AnnouncementBar` and `AnnouncementModal` filled into `shell.header.actions` and a new `shell.banner` slot (declared with PAP-438); settings page `/_app/settings/announcements` (admin); kind `announcement.published` in the notification core. Out: marketing email (PAP-191), changelog entries (PAP-133), status page.

**Spec**

* Platform announcements (`tenant_id null`) reach every tenant; tenant announcements are scoped by RLS; audiences resolve through PAP-55 segments.
* Optional `flag` shows the announcement only when a PAP-366 flag is on for the viewer (ties 'new feature' banners to rollouts).
* Scheduling by `starts_at|ends_at` in the tenant timezone; a job (PAP-43) emits `announcement.published` at start so the notification core fans out once.
* Dismissal per user; non-dismissible maintenance banners reappear each session; at most one banner and one modal visible at a time (priority by `starts_at`).
* Body is Markdown rendered by `renderMdx` with links only (no components); 500 characters for banners, 2k for modals.

**Interface contract**

Provides: tables, procedures, `AnnouncementBar`, `AnnouncementModal`, slot `shell.banner` props schema, kind `announcement.published`. Consumes: notification core (`defineKind`), audiences (PAP-55), `can()` (PAP-59), flags (PAP-366, soft), slots (PAP-438), `renderMdx` (PAP-128), jobs (PAP-43), shells (PAP-62, PAP-63). Consumed by: PAP-88 release train (maintenance notice), PAP-133 (link from What's new), PAP-195 in-app targeting.

**Definition of done**

* Admin schedules a customer-only banner; a staff user never sees it; a customer sees it at start time and can dismiss it; screenshots at 375 and 1280 in light and dark; axe clean.
* `docs/collab/announcements.md`; CHANGELOG entry; Linear comment.

**Test plan**

* Unit: audience resolution, schedule window with timezone, dismissal precedence, one-visible rule.
* Integration: RLS `callAs` matrix; `/__test` clock advances past `starts_at` and the kind fires once.
* E2E (Playwright): create, see as customer, dismiss, reload, absent; maintenance banner not dismissible.

**Demo**

Create a 'Maintenance tonight' banner for all audiences and a 'New invoices page' modal for `customer.pro`, sign in as each audience and see the right one. Under two minutes.

**Edge cases**

* Overlapping banners: newest `starts_at` wins; the other waits.
* Announcement edited after publish: no second notification; banner updates live via shape or on reload.
* Flag removed: announcement hidden and flagged `stale` in settings.

**Dependencies**

Hard: PAP-725, PAP-55. Soft: PAP-366, PAP-438, PAP-43, PAP-62, PAP-63.

**Agent**

Builder: Nova with Iris on the bar and modal. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/notification-core` = PAP-725.
