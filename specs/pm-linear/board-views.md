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
blockedBy: ["PAP-100", "PAP-167"]
blocks: []
key: "pm-linear/board-views"
url: "https://linear.app/paperos/issue/PAP-102/render-pm-board-list-and-timeline-views-using-the-tablesviews-engine"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-102: Render PM board, list and timeline views using the tables/views engine

**Goal**

Show project management inside the product: the PM entities from `pm-linear/pm-data-model` rendered as a kanban board grouped by workflow state, a filterable list and a timeline of projects and milestones, all built as configurations of the table and views engine rather than bespoke components. Dragging a card between columns changes state and (through sync) moves the issue in Linear.

**Scope**

In:
- Route `/pm` in `apps/web` with sub-routes `/pm/board`, `/pm/list`, `/pm/timeline` and `/pm/issues/:identifier`, declared through page specs `specs/pm/board.spec.yaml`, `list.spec.yaml`, `timeline.spec.yaml` (detail spec from the data-model issue).
- Board: `tables/kanban-view` configured with data source `pm_issue`, group by `state_id` ordered by `pm_workflow_state.position`, swimlanes optional by `project_id` or assignee, card fields (identifier, title, priority icon, assignee avatar, labels, estimate), WIP limit on `In Review` and `Needs Justin` (5) with a visual warning, drag to change state via `pm.issues.update`.
- List: `tables/grid-view` with columns identifier, title, state, priority, assignee, labels, project, updated; inline edit for state, priority, assignee; filter builder and multi-sort from `tables/filter-sort-group-ui`; saved views "My issues", "Ready for Claude", "Needs Justin" seeded.
- Timeline: `tables/calendar-timeline-gantt` timeline mode over `pm_project` and `pm_milestone` by `target_date`, with issues nested when a project is expanded.
- Issue detail page: title, description (rendered markdown), state control, metadata sidebar, comments thread (plain list; rich threading arrives with `collab/comments`), external link chip to the Linear issue from `pm_external_ref`.
- Agent visibility: cards assigned to agent principals show the character badge and, when a session is active, a pulsing "working" indicator sourced from the orchestrator `/status` endpoint via oRPC `pm.sessions.active`.
- Keyboard: `j/k` navigate cards, `enter` opens, `1-6` moves to state n (registered in `input/command-registry`).

Out: creating projects/cycles UI beyond a minimal "new issue" dialog, roadmap views, notifications, comment editing.

**Spec**

- Views are stored as `view` records per `tables/view-model-spec`, seeded by `pnpm db:seed pm-views`; no hard-coded column configs in components.
- Components come only from `packages/ui` and `packages/views`; the PM feature adds `apps/web/src/features/pm/` with cell renderers for priority, state and character badge registered in the views cell registry.
- Optimistic updates through the local-first layer (`data-layer/local-first-sync`) so drag feels instant; failures roll back with a toast.
- Responsive: at widths under 768 px the board becomes a single-column state picker with horizontal swipe between columns; list hides secondary columns; timeline switches to a vertical milestone list.
- Empty, loading and error states declared in the page specs and implemented.

**Definition of done**

- Three page specs validate; conformance tests from `spec-builder/conformance-tests` pass.
- Playwright screenshots of board, list, timeline and detail at 320, 375, 768, 1024, 1280, 1920 and 2560 px in light and dark themes, attached to the PR and Linear comment.
- Drag a card on staging and see the Linear issue change state within 10 s (screen recording).
- Vitest for cell renderers; Playwright e2e for filter, sort, drag, keyboard shortcuts.
- axe passes on all four pages; keyboard-only drag alternative works (from `input/drag-drop`).
- GitHub Pages demo link with seeded data; changelog entry; Linear comment with demo and screenshots.

**Edge cases**

- 2000 issues in one column: virtualised column; group counts computed server-side.
- Drag to `Needs Justin` when five are already open: block with an explanation, mirroring the governor in `pm-linear/justin-queue`.
- Sync conflict after a drag (Linear wins): card snaps back with a "changed in Linear" toast.
- Issue with no project on the timeline: shown in an "Unscheduled" lane.
- User lacks permission to change state (permission engine): drag handle disabled, tooltip explains.
- Offline: drag queues locally with a pending badge; resolved on reconnect.
- Character badge for a session that died without ending: indicator times out after 15 minutes of no heartbeat.

**Dependencies**

- `pm-linear/pm-data-model` (tables, procedures, detail spec).
- `tables/kanban-view` (and through it `tables/query-compiler`, `input/drag-drop`); also uses `tables/grid-view`, `tables/filter-sort-group-ui`, `tables/calendar-timeline-gantt`.
- Live Linear reflection requires `pm-linear/linear-sync`; the views work without it against local data.

**Agent**

Built by Nova (Views Engineer sub-agent); reviewed by Sentinel (Visual Inspector, Code Reviewer) and Iris for design-system conformance.

**Size**

M: configuration of existing views plus one detail page and custom cells.
