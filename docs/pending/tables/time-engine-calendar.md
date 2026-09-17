---
key: "tables/time/engine-calendar"
title: "TimeScale engine, range compilation, overlap packing and the calendar view (month, week, day, agenda)"
project: "tables"
parent: "PAP-168"
phase: "P1"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "All view types"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc"
status: "pending"
---

# TimeScale engine, range compilation, overlap packing and the calendar view (month, week, day, agenda)

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

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: date maths heavy.
