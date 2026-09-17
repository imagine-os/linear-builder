---
key: "tables/time/gantt"
title: "Gantt view: frozen left grid, dependency arrows, critical path, progress and working days"
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
identifier: "PAP-346"
status: "created"
createdAt: "2026-09-17"
---

# Gantt view: frozen left grid, dependency arrows, critical path, progress and working days

**Goal**

Turn the timeline into a Gantt with a task grid, finish-to-start dependencies, critical path highlighting and working-day scheduling.

**Scope**

In: `views/time/{GanttView,deps,criticalPath,workdays}.tsx`. Out: resource levelling.

**Spec**

* Left grid (title, start, end, duration, assignee) reusing PAP-165 cells; dependencies from a self-relation field drawn as SVG paths; create by dragging a connector handle; delete via context menu.
* Dragging a bar with dependents offers "shift dependents" (Alt skips); cycles rejected with explanation; imported cycles dashed red.
* Critical path is the longest path, recomputed client-side; `progressField` fills bars; weekends shaded and skipped when `workingDays` set.

**Interface contract**

Provides: `<GanttView />`, `criticalPath(items, deps)`, `shiftDependents`. Consumes: timeline child, PAP-165 cells, relation type (PAP-164).

**Definition of done**

* Unit tests for critical path and working-day maths; Playwright dependency create and shift; replay at 1024 and 1920; screenshots at five widths.

**Test plan**

* Unit: longest path on fixtures; cycle detection; working-day arithmetic.
* E2E: add dependency, shift, reject cycle; keyboard-only reschedule.

**Demo**

Draw a dependency between two bars in `/demo/gantt` and move the predecessor.

**Edge cases**

* Zero-duration after resize clamps and warns; under 768 px the left grid hides.

**Dependencies**

Timeline child (hard), PAP-165, PAP-164.

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.
