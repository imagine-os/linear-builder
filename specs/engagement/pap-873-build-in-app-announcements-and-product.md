---
identifier: "PAP-873"
title: "Build in-app announcements and product messaging: banners, modals and a What's new feed from the changelog, targeting by segment, audience and flag, scheduling, dismissal and metrics"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Memberships, loyalty, announcements and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-133", "PAP-136", "PAP-195", "PAP-366", "PAP-725"]
blocks: []
key: "r4/engagement/announcements"
url: "https://linear.app/paperos/issue/PAP-873/build-in-app-announcements-and-product-messaging-banners-modals-and-a"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-873: Build in-app announcements and product messaging: banners, modals and a What's new feed from the changelog, targeting by segment, audience and flag, scheduling, dismissal and metrics

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Let tenants talk to their users inside the app: announcements as banners, modals and a What's new panel fed by the PAP-133 per-tenant changelog, targeted by audience, segment (PAP-195) and flag (PAP-366), scheduled with start and end, dismissible per user, with view and click metrics, so release notes and business notices (holiday hours, price changes) reach the right people without an email blast.

**Scope**

In: `announcement` (kind banner|modal|feed, body Tiptap JSON, cta, targeting: audiences, segment, flag, routes, start, end, priority, dismissible), `announcement_view` (user, viewed, dismissed, clicked); `AnnouncementPort.forPrincipal(route)` evaluated server-side and streamed via the flag snapshot channel (PAP-366). Shell fills: `shell.banner` (one banner at a time by priority), modal on first eligible route, What's new bell entry in the PAP-323 inbox area merging changelog entries (PAP-133) and feed announcements. Console page `/console/announcements` with editor, preview per audience, schedule, metrics (views, dismissals, clicks) as dashboard blocks; approval optional via the approvals framework.

Out: Email or SMS delivery (use notifications or campaigns). Behavioural targeting by product events (platform-ops product analytics; v0.3).

**Spec**

* Targeting is evaluated with the same evaluator as flags so a segment or flag change applies within the snapshot refresh; the client never decides eligibility
* Banners respect reduced motion and the PAP-234 state components; modals never stack with system dialogs and can be deferred once
* Dismissal is per user per announcement version; editing the body creates a version and may re-show only when `reshowOnEdit`
* Metrics are counts, not per-user tracking beyond dismissal state; no third-party scripts

**Interface contract**

Provides: `AnnouncementPort`, tables, shell fills, console page, metrics blocks, `announcement.viewed|dismissed|clicked` events. Consumes: changelog feed (PAP-133), segments (PAP-195), flags and snapshot channel (PAP-366), inbox UI (PAP-323), notifications (PAP-136), state components (PAP-234), approvals (soft). Consumed by: platform-ops (platform-wide announcements to all tenants use the same mechanism with `scope: platform`), growth (campaign follow-through in-app), assistant (announcements as grounding for "what changed?").

**Definition of done**

* Holiday-hours banner targeted at customers in one segment shows only to them, dismisses, and reports metrics; What's new merges the last release notes; screenshots at three widths
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: targeting evaluation parity with flags; priority selection; version and dismissal logic.
* E2E: banner and modal on portal and console, keyboard dismissal, reduced motion.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Publish "Closed Monday" as a portal banner for the VIP segment starting tomorrow, preview as a VIP and a non-VIP, then show the What's new panel with the latest changelog.

**Edge cases**

* Two banners eligible: higher priority wins; the other appears after dismissal; ties break by start date
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-133 (hard: feed), PAP-195, PAP-366 (hard: targeting), PAP-323, PAP-136 (soft), PAP-234 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.
