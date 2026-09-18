---
identifier: "PAP-345"
title: "Timeline view: two-axis virtualised canvas, lanes, zoom levels and bar editing"
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
blockedBy: ["PAP-344", "PAP-651"]
blocks: ["PAP-346", "PAP-634"]
key: "tables/time/timeline"
url: "https://linear.app/paperos/issue/PAP-345/timeline-view-two-axis-virtualised-canvas-lanes-zoom-levels-and-bar"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:03.017Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-345: Timeline view: two-axis virtualised canvas, lanes, zoom levels and bar editing

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Render thousands of items across lanes on a horizontally scrolling, zoomable timeline with drag to move and resize.

**Scope**

In: `views/time/{TimelineView,lanes,zoom}.tsx`, PNG export. Out: dependencies and critical path (Gantt sibling).

**Spec**

* Virtualised on both axes with `@tanstack/react-virtual`; lanes from `laneField` groups; two-tier sticky headers per zoom; Ctrl+wheel zoom and pinch (PAP-156); today marker; milestones as diamonds.
* Move and resize snap to the zoom unit with a ghost preview; keyboard arrows move, Shift+arrows resize.
* Labels hidden under 40 px; export visible range with `html-to-image`.

**Interface contract**

Provides: `<TimelineView />`, `useTimelineViewport`, bar renderer reused by Gantt. Consumes: engine child, PAP-155, PAP-156.

**Definition of done**

* Playwright zoom, pan, move, resize on a 2,000-item seed; 60 fps assertion; screenshots at five widths in three themes.

**Test plan**

* Unit: zoom tick generation; snapping.
* E2E: flows above plus keyboard resize.

**Demo**

Zoom from month to day in `/demo/timeline`, drag a bar and resize another.

**Edge cases**

* 10,000 items in one lane stay smooth; missing `endField` disables resize.

**Dependencies**

Engine child (hard), PAP-155, PAP-156 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
