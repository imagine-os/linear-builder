---
identifier: "PAP-908"
title: "Build the shared recurrence engine: RRULE (RFC 5545) parsing and expansion with time zones, exceptions and bounds, used by jobs schedules, recurring invoices, calendar views, bookings and maintenance"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-27", "PAP-43", "PAP-302", "PAP-565"]
blocks: []
key: "r4/data-layer/recurrence-engine"
url: "https://linear.app/paperos/issue/PAP-908/build-the-shared-recurrence-engine-rrule-rfc-5545-parsing-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-908: Build the shared recurrence engine: RRULE (RFC 5545) parsing and expansion with time zones, exceptions and bounds, used by jobs schedules, recurring invoices, calendar views, bookings and maintenance

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Stop five modules from each re-implementing "every second Tuesday": one `packages/core/recurrence` with an RFC 5545 `RRULE` model (rrule.js under the hood, wrapped in our types), time-zone-correct expansion across DST, exception dates and bounded iteration, a Zod schema for storing rules on any row, and a job helper that schedules the next occurrence.

**Scope**

In: `Recurrence` Zod schema (`rrule` string, `dtstart` with zone, `exdates[]`, `rdates[]`, `until|count`), `expand(rule, range, { zone, limit })`, `next(rule, after)`, `describe(rule, locale)` (human text via PAP-27 catalogs), `validate` (rejects unbounded rules without a range), and a Drizzle column helper `recurrence()`. PAP-43 helper `scheduleRecurring(job, rule)` that enqueues the next occurrence with `singletonKey` and re-schedules after each run, replacing ad-hoc cron strings where a business rule is involved. UI: `<RecurrenceEditor/>` in `@paperos/ui` (presets, custom builder, human preview) on the PAP-233 pickers.

Out: Calendar rendering (PAP-344 consumes). iCalendar import/export beyond the RRULE string (engagement calendar sync).

**Spec**

* Expansion is deterministic and zone-aware: a 9:00 weekly rule in Europe/London stays 9:00 local across DST; tests cover forward and back transitions and non-existent local times
* Hard limit 10,000 occurrences per expansion call; callers page by range
* `describe` output is localised and used verbatim by calendar, booking and invoice UIs

**Interface contract**

Provides: `packages/core/recurrence` (`Recurrence`, `expand`, `next`, `describe`, `recurrence()` column), `scheduleRecurring`, `<RecurrenceEditor/>`. Consumes: contract-zero types (PAP-302), Intl and catalogs (PAP-27), jobs (PAP-43), pickers (PAP-233). Consumed by: PAP-344 calendar (recurring events), PAP-180 WP4 recurring invoices, PAP-43 business schedules, engagement availability rules and maintenance schedules (commerce), workflows schedule triggers.

**Definition of done**

* Library merged with 100 percent branch coverage on expansion; editor in Storybook; PAP-344 and PAP-180 WP4 comment confirming adoption
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: RFC 5545 examples suite; DST fixtures for London, New York, Sydney and Kathmandu; exdates; limits.
* Property: fast-check: `next(rule, t)` equals the first element of `expand(rule, [t, ∞))` for random rules.

**Demo**

Build "first Monday of every month at 9:00 Sydney" in the editor, read the human description, and print the next twelve occurrences across the April DST change.

**Edge cases**

* Rule with `BYSETPOS` and `BYDAY` combinations rrule.js mishandles: covered by the RFC suite with documented deviations

**Dependencies**

PAP-302, PAP-27 (hard), PAP-43, PAP-233 (soft).

* Soft dependency (round 4): PAP-344 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-30) is later than PAP-344's (2026-09-29), so it must not block it; build against its interface and reconcile when it lands.
  **Agent**

Builder: Forge. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.
