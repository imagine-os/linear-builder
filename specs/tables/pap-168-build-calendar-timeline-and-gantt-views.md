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
children: ["PAP-344", "PAP-345", "PAP-346"]
blockedBy: ["PAP-163", "PAP-337"]
blocks: []
key: "tables/calendar-timeline-gantt"
url: "https://linear.app/paperos/issue/PAP-168/build-calendar-timeline-and-gantt-views-with-dependencies"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:14.431Z"
model: null
effort: null
---

# PAP-168: Build calendar, timeline and Gantt views with dependencies

**Goal**

Add the three time-based views on one `TimeScale` engine: calendar (month, week, day, agenda), a zoomable timeline with lanes, and a Gantt with dependency arrows and critical path. Any dataset with a date field is scheduled by dragging; Gantt additionally reads a self-relation for dependencies. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-344 `TimeScale` engine, range compilation, overlap packing and the calendar view (month, week, day, agenda).
* PAP-345 Timeline: two-axis virtualised canvas, lanes, zoom levels, today marker, move and resize.
* PAP-346 Gantt: frozen left grid, dependency arrows, critical path, progress fill, working days.

Out: recurring events, external calendar sync, resource levelling.

**Spec**

Decisions binding all children:

* `date-fns` 4.x with `@date-fns/tz`; all maths in the actor timezone; all-day values are calendar dates.
* Options `{ startField, endField?, allDay?, dependencyField?, milestoneField?, progressField?, laneField?, colorField?, workingDays, zoom: 'hour'|'day'|'week'|'month'|'quarter' }`.
* Fetch window is the visible range padded one period, compiled as `start <= rangeEnd AND coalesce(end, start) >= rangeStart` through PAP-163; page 500 with "n more" overflow chips.
* Edits write `startField`/`endField` optimistically through `mutate`, snapping to the zoom unit, ghost preview on drag.
* Every bar is a focusable button with `aria-label` "Title, from X to Y, lane Z"; arrows move, Shift+arrows resize; `LiveAnnouncer`; commands `time.*`.
* Under 768 px calendar defaults to agenda; timeline and Gantt hide the left grid.

**Interface contract**

Provides: `<CalendarView />`, `<TimelineView />`, `<GanttView />`, `<DateRangeNav />`, `TimeScale` (`toX(date)`, `toDate(x)`, `ticks(zoom)`), `packOverlaps(events)`, `criticalPath(items, deps)`, `onFilter` (click a day or lane) for dashboards, PNG export. Consumes: range query (PAP-163), date, relation and number cells (PAP-164), grid cells for the left pane (PAP-165), drag (PAP-155), pinch zoom (PAP-156). Consumed by PAP-190 social calendar (list fallback until Done), PAP-102 timeline.

**Definition of done**

* All three children Done.
* Storybook stories per view; screenshots at 375, 768, 1024, 1440, 1920 in three themes; Gantt drag replay at 1024 and 1920; axe clean; keyboard-only rescheduling works.
* `docs/views/time-views.md` with the options table; CHANGELOG; Linear comment with demo link.

**Test plan**

Umbrella `time-views.e2e.spec.ts` on a 2,000-item seed: switch calendar month to week to agenda and assert the same record appears in each; drag an event across a DST boundary in `America/Los_Angeles` and `Europe/Berlin` and assert the stored instant; resize on the timeline at day and week zoom; add a dependency in Gantt, shift the predecessor, accept "shift dependents", assert critical path highlight changes; reject a cycle. Unit fixtures shared by all three children live in `packages/views/test/time/fixtures.ts`.

**Demo**

Reviewer opens `/demo/calendar`, drags an event to next week, switches to the timeline and zooms with Ctrl+wheel, then opens the Gantt and draws a dependency between two bars, watching the critical path re-colour. Under two minutes.

**Edge cases**

* End before start after resize: clamp to zero duration and warn.
* Multi-month events render as spans with continuation arrows.
* Dependency cycles rejected on create; imported cycles render dashed red.
* 10,000 items in one lane keep 60 fps; labels hidden under 40 px bars.
* Missing `endField`: one-unit bars, resize disabled.

**Dependencies**

PAP-163 (hard), PAP-164 (hard), PAP-165 (Gantt left grid), PAP-155 (drag), PAP-156 (pinch, soft). Blocks nothing hard; PAP-190 prefers it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter for date maths, Visual Inspector).

**Size**

L, split into three M children; land the calendar child first.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
