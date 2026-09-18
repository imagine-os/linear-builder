---
identifier: "PAP-866"
title: "Build calendar sync: ICS feeds, Google Calendar and Microsoft 365 two-way sync with busy-time import, push into external calendars, webhooks and conflict handling"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Messaging channels, help center and surveys"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-57", "PAP-121", "PAP-226", "PAP-353", "PAP-565", "PAP-864"]
blocks: []
key: "r4/engagement/calendar-sync"
url: "https://linear.app/paperos/issue/PAP-866/build-calendar-sync-ics-feeds-google-calendar-and-microsoft-365-two"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-866: Build calendar sync: ICS feeds, Google Calendar and Microsoft 365 two-way sync with busy-time import, push into external calendars, webhooks and conflict handling

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Make PaperOS availability agree with the calendars staff already live in: a `CalendarSyncPort` with Google Calendar and Microsoft Graph adapters (OAuth through the PAP-57 plumbing, tokens encrypted with PAP-353), busy-time import into `AvailabilityRule(kind blocked, source calendar-sync)`, bookings pushed as events with updates and cancellations, incremental sync via webhooks with polling fallback, and read-only ICS feeds for everyone else.

**Scope**

In: `packages/engagement/src/calendar/`: `calendar_connection` (provider, account, encrypted tokens, calendars selected for busy import, target calendar for push, sync cursor, webhook channel); adapters `google` (Calendar API v3 with `syncToken` and push channels) and `microsoft` (Graph delta queries and subscriptions); `ics` feed adapter (signed per-resource URL, PAP-172 token semantics). Import: busy intervals become blocked rules tagged with the external event id; private details are never stored, only start, end and an opaque id; free/transparent events are ignored by default. Push: booking events create external events with description, location and a manage link; reschedule and cancel update or delete; external edits to a pushed event raise a `calendar.conflict` for staff (PaperOS wins unless staff accept the change). Settings UI in `/console/settings/calendars` and per-user connection in the profile; connector files for PAP-121 (`google-calendar.connector.yaml`, `microsoft-graph.connector.yaml`).

Out: CalDAV (v0.3). Meeting links (Zoom, Meet) beyond a text field. Customer calendars (customers get ICS attachments).

**Spec**

* Sync is incremental and idempotent: cursors persisted per connection; a full resync is an explicit staff action with progress
* Token refresh failures pause the connection and notify the owner; nothing books against stale availability for more than the configured staleness (default 15 minutes) without a visible warning on the calendar
* Webhook receivers verify provider signatures and are rate-limited (PAP-304); every inbound triggers a job, never inline work
* Deleting a connection removes imported blocked rules and leaves pushed events in place with a note (external data is the user's)

**Interface contract**

Provides: `CalendarSyncPort` with `google`, `microsoft`, `ics` adapters, `calendar_connection`, settings pages, `calendar.synced|conflict` events, connector files. Consumes: booking engine and availability rules, OAuth plumbing (PAP-57), field encryption (PAP-353), jobs (PAP-43), connector registry (PAP-121), tokens (PAP-172), rate limits (PAP-304). Consumed by: booking pages (ICS), commerce HR (staff busy time), assistant ("am I free Thursday?").

**Definition of done**

* Google and Microsoft connections sync a test account both ways on staging with recorded fixtures in CI; ICS feed validates in two clients; conflict path visible; connection removal proven clean
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: delta processing with moved, deleted and recurring events; conflict detection; privacy filter.
* Integration: recorded provider fixtures (msw) for initial, incremental and expired-cursor sync; webhook signature rejection; token refresh failure pause.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Connect a Google calendar for a stylist, add a dentist appointment there, watch the booking page lose that slot within a minute; book a client and see it appear in Google with the manage link.

**Edge cases**

* Recurring external event with exceptions: each instance becomes its own blocked interval; the exception is honoured
* Two staff share one external calendar: each connection imports it; pushes go to the resource owner's connection only
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-864 (hard), PAP-57, PAP-353 (hard), PAP-43 (hard), PAP-121, PAP-172, PAP-304 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/engagement/booking-engine` = PAP-864.
