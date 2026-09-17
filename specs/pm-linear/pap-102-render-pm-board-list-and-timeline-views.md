---
identifier: "PAP-102"
title: "Render PM board, list and timeline views using the tables/views engine"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-100", "PAP-167", "PAP-288", "PAP-333"]
blocks: []
key: "pm-linear/board-views"
url: "https://linear.app/paperos/issue/PAP-102/render-pm-board-list-and-timeline-views-using-the-tablesviews-engine"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:18.155Z"
---

# PAP-102: Render PM board, list and timeline views using the tables/views engine

**Goal**

Show project management inside the product: the PM entities rendered as a kanban board grouped by workflow state, a filterable list and a timeline of projects and milestones, all as configurations of the views engine rather than bespoke components. Dragging a card changes state and, through sync, moves the Linear issue.

**Scope**

* In: routes `/pm`, `/pm/board`, `/pm/list`, `/pm/timeline`, `/pm/issues/:identifier` with page specs; view records seeded; cell renderers for priority, state and character badge; keyboard-only drag; character heartbeat badge.
* Out: the sync itself (PAP-101), custom views UI beyond saved filters (PAP-166), comments on issues (PAP-131).

**Spec**

* Board: `tables/kanban-view` (PAP-167) with data source `pm_issue`, group by `state_id` ordered by `pm_workflow_state.position`, optional swimlanes by project or assignee, card fields identifier, title, priority, assignee, labels, estimate; WIP limit 5 on `In Review` and `Needs Justin` mirroring PAP-94; drag calls `pm.issues.update`.
* List: `tables/grid-view` columns identifier, title, state, priority, assignee, labels, project, updated; inline edit for state, priority, assignee; saved views "My issues", "Ready for Claude", "Needs Justin", "Blocked".
* Timeline: `tables/calendar-timeline-gantt` with projects as rows, milestones as markers, an "Unscheduled" lane.
* Character badge reads `SessionStatus` from PAP-288; `working` when `lastHeartbeat` is under 15 minutes old, else `stale`.
* Responsive: under 768 px the board is a single-column state picker with swipe; the list hides secondary columns; the timeline becomes a vertical milestone list. Optimistic updates through PAP-36 with rollback toast.

**Interface contract**

* Provides: view seeds `pnpm db:seed pm-views`, cell renderers `pm.priority`, `pm.state`, `pm.character` registered in the views cell registry (PAP-71), page specs consumed by PAP-122 conformance tests, route `/pm/issues/:identifier` used by PAP-113 drawer links.
* Consumers: PAP-113 (deep links), PAP-136 (notification links), PAP-204 (import preview reuses the list).
* Requires: PAP-100 tables and procedures, PAP-167 kanban, PAP-165 grid, PAP-166 filter UI, PAP-155 drag-drop keyboard alternative, PAP-101 for live Linear reflection (works locally without it), PAP-288 for the badge.

**Definition of done**

* Three page specs validate; conformance tests pass.
* Screenshots of board, list, timeline and detail at 320, 375, 768, 1024, 1280, 1920 and 2560 px in light and dark attached.
* Drag on staging changes the Linear issue within 10 s (recording).
* axe passes on all four pages; keyboard-only drag works.
* Pages demo with seeded data; changelog; Linear comment with demo and screenshots.

**Test plan**

* Unit: cell renderers, WIP-limit guard, badge staleness computation with a fake clock.
* Integration: `pm.issues.update` optimistic path and rollback with a failing mock.
* e2e (Playwright): filter, sort, drag with mouse and keyboard, offline drag queued then applied on reconnect, at 375 and 1280 px.
* Visual: seven-width matrix in both themes through gate 3 (PAP-82); the 768 px breakpoint switch is asserted explicitly.

**Demo**

Open `/pm/board` on a phone-width window, swipe to `Ready for Claude`, drag a card to `In Progress`, then open the same issue in Linear and see the state changed. Ninety seconds.

**Edge cases**

* 2000 issues in one column: virtualised; counts computed server-side.
* Drag into a full `Needs Justin`: blocked with explanation.
* Sync conflict after drag: card snaps back with "changed in Linear" toast.
* No permission to change state: handle disabled with tooltip.
* Orchestrator status unreachable: badge shows "unknown", not spinner.

**Dependencies**

Blocked by PAP-100, PAP-167, PAP-288. Soft: PAP-101, PAP-155.

**Agent**

Built by Nova (Views Engineer sub-agent); reviewed by Sentinel (Visual Inspector).

**Size**

M
