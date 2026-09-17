---
identifier: "PAP-168"
title: "Build calendar, timeline and Gantt views with dependencies"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-163"]
blocks: []
key: "tables/calendar-timeline-gantt"
url: "https://linear.app/paperos/issue/PAP-168/build-calendar-timeline-and-gantt-views-with-dependencies"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-168: Build calendar, timeline and Gantt views with dependencies

**Goal**

Add the three time-based views: a calendar (month, week, day, agenda), a horizontal timeline with zoom, and a Gantt with dependency arrows and critical path highlighting. Any dataset with a date field can be scheduled by dragging; Gantt additionally reads a self-relation field for dependencies.

**Scope**

In:
- `packages/views/src/views/time/`: shared `TimeScale` engine, `<CalendarView />`, `<TimelineView />`, `<GanttView />`, `<DateRangeNav />`.
- Options: `{ startField, endField?, allDay?: boolean, dependencyField?, milestoneField?, progressField?, laneField? (timeline/Gantt grouping), colorField?, workingDays: number[], zoom: 'hour'|'day'|'week'|'month'|'quarter' }`.
- Drag to move, resize to change duration, create by drag-selecting a range.

Out: recurring events, external calendar sync (Google/Outlook, future project), resource levelling.

**Spec**

- Dates: `date-fns` 4.x and `@date-fns/tz`; all math in the actor's timezone; all-day dates treated as calendar dates. Fetch window is the visible range padded by one period, compiled as `startField <= rangeEnd AND coalesce(endField, startField) >= rangeStart` via `tables/query-compiler`; page size 500 with an "n more" overflow chip per day cell.
- Calendar: CSS grid 7 columns; month cells show up to 4 events then "+n"; week/day show a time axis with 30-minute slots and overlapping events laid out with a column-packing algorithm; agenda is a grouped list by day reusing `tables/gallery-list-form` list rows. Navigation: prev/next/today, keyboard arrows move day focus, Enter opens the record panel, `n` creates.
- Timeline: horizontal virtualised canvas (`@tanstack/react-virtual` on both axes), lanes from `laneField` groups, zoom levels with sticky date headers (two-tier: month over day, quarter over week); wheel plus Ctrl zooms, drag pans; today marker line; items as bars with title, milestone as diamond.
- Gantt: timeline plus a left frozen grid (title, start, end, duration, assignee) reusing grid cells; dependencies drawn as SVG paths (finish-to-start) from `dependencyField` (relation to same dataset); dragging a bar with dependents offers "shift dependents" (Alt to skip); critical path computed client-side (longest path) and highlighted; `progressField` (number 0-100) fills the bar; working days shade weekends and skip them when `workingDays` is set.
- Editing: move/resize writes `startField`/`endField` optimistically through `mutate`; snapping to the zoom unit; a ghost bar previews the drop; dependency create by dragging from a bar's connector handle to another bar; delete dependency via context menu.
- Accessibility: every bar is a focusable button with `aria-label` "Title, from X to Y, lane Z"; keyboard move with arrows and Shift+arrows to resize; announcements via `LiveAnnouncer`. Commands `time.*` registered.
- Printing/export: "Export PNG" renders the visible timeline with `html-to-image`.
- Responsive: under 768 px calendar defaults to agenda, timeline/Gantt hide the left grid and show a compact lane header.

**Definition of done**

- Vitest for range compilation, overlap packing, critical path, working-day math and DST cases (fixtures for America/Los_Angeles and Europe/Berlin).
- Playwright: drag to reschedule, resize, create by drag, add dependency, zoom; 2,000-item seed.
- Storybook stories per view tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920, three themes; video replay of the Gantt drag at 1024 and 1920.
- axe clean; keyboard-only rescheduling works.
- `docs/views/time-views.md` with options table; CHANGELOG entry; Linear comment with demo link.

**Edge cases**

- End before start after a resize: clamp to zero duration and warn.
- Events spanning months in month view render as multi-row spans with continuation arrows.
- Dependency cycles (A→B→A): reject on create with explanation; existing cycles from imports render dashed red.
- 10,000 items in one timeline lane: virtualisation keeps 60 fps; label collision hides labels under 40 px bar width.
- Missing `endField`: bars are one unit wide, resize disabled.
- Timezone change mid-session (travelling user): rerender on `visibilitychange` if the offset changed.

**Dependencies**

- `tables/query-compiler`, `tables/field-types` (date, relation, number), `tables/grid-view` (left grid cells), `input/drag-drop`, `input/touch-gestures` for pinch zoom.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter for date math, Visual Inspector).

**Size**

L: three views sharing one engine, with heavy date logic; plan two sessions and land calendar first.
