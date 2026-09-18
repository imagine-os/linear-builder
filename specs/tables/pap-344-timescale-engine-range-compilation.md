---
identifier: "PAP-344"
title: "TimeScale engine, range compilation, overlap packing and the calendar view (month, week, day, agenda)"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: "PAP-168"
children: []
blockedBy: ["PAP-155", "PAP-163", "PAP-164", "PAP-331", "PAP-337", "PAP-627", "PAP-659"]
blocks: ["PAP-345", "PAP-863", "PAP-865", "PAP-884"]
key: "tables/time/engine-calendar"
url: "https://linear.app/paperos/issue/PAP-344/timescale-engine-range-compilation-overlap-packing-and-the-calendar"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:29.647Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-344: TimeScale engine, range compilation, overlap packing and the calendar view (month, week, day, agenda)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Build the shared time engine and the calendar view so any dataset with a date field is browsable and reschedulable by drag.

**Scope**

In: `views/time/{TimeScale,range,pack,CalendarView,DateRangeNav}.tsx`. Out: timeline and Gantt (siblings).

**Spec**

* `TimeScale` maps dates to pixels per zoom; `date-fns` 4.x with `@date-fns/tz`; all-day values are calendar dates.
* Range compilation `start <= rangeEnd AND coalesce(end, start) >= rangeStart` via PAP-163; window padded one period; page 500 with "+n" chips.
* Month grid with four events per cell then "+n"; week and day with 30-minute slots and column-packed overlaps; agenda reuses PAP-169 list rows.
* Drag to move, drag-select to create, keyboard `n` to create; every event a focusable button with a descriptive label.

**Interface contract**

Provides: `TimeScale`, `compileRange`, `packOverlaps`, `<CalendarView />`, `<DateRangeNav />`. Consumes: PAP-163, date cells (PAP-164), drag (PAP-155), list rows (PAP-169).

**Definition of done**

* DST fixtures for two zones; Playwright drag and create; screenshots at 375, 768, 1024, 1440, 1920 in three themes; axe clean.

**Test plan**

* Unit: range compile, packing, DST, month spans.
* E2E: reschedule across a DST boundary and verify the stored instant; agenda at 375 px.

**Demo**

Drag an event to next week in `/demo/calendar`, switch to week view and back.

**Edge cases**

* Multi-month spans with continuation arrows; travelling user offset change rerenders.

**Dependencies**

PAP-163, PAP-164, PAP-155 (hard). Blocks siblings.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-908 (recurrence-engine) (new, phase 2) would block this issue but sits in a later milestone (2026-09-30 > 2026-09-29); no `blocks` relation was created. Build against its interface and reconcile when it lands.

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: date maths heavy.
