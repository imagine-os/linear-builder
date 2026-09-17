---
identifier: "PAP-385"
title: "Dashboard tables, layout engine, breakpoint layouts and drag or resize with keyboard moves"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: "PAP-173"
children: []
blockedBy: ["PAP-155", "PAP-172"]
blocks: ["PAP-386"]
key: "tables/dashboard/model-grid"
url: "https://linear.app/paperos/issue/PAP-385/dashboard-tables-layout-engine-breakpoint-layouts-and-drag-or-resize"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:42.311Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-385: Dashboard tables, layout engine, breakpoint layouts and drag or resize with keyboard moves

**Goal**

Store dashboards and lay blocks out on a responsive 12-column grid that users arrange by pointer or keyboard.

**Scope**

In: tables `dashboard`, `dashboard_block`; procedures `dashboards.*`, `dashboardBlocks.*`; `layout/` engine; `<DashboardEditor />` shell. Out: block kinds and cross-filter (sibling).

**Spec**

* Schema per the parent; RLS; visibility mirrors PAP-172.
* Grid 12/8/1 columns at `lg`/`md`/`sm`; row height 40 px; collisions push down; `sm` auto-derived from `y` unless customised.
* Drag and resize with 8-direction handles via PAP-155; keyboard select, arrows move one cell, Shift+arrows resize; announcements.

**Interface contract**

Provides: `Dashboard`, `DashboardBlock` types, procedures, `useLayoutEngine`, `<DashboardEditor />`. Consumes: PAP-155, PAP-172, PAP-34.

**Definition of done**

* Layout collision and derivation unit tests; Playwright drag, resize, keyboard move; screenshots at 375, 768, 1024, 1440, 1920.

**Test plan**

* Unit: collision, derivation, bounds.
* E2E: arrange six placeholder blocks by pointer and keyboard, reload, layout persisted.

**Demo**

Add three placeholder blocks in the editor, drag one wider, move another with the keyboard.

**Edge cases**

* 40 blocks warn at 30; min sizes enforced.

**Dependencies**

PAP-155, PAP-172 (hard). Blocks siblings.

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
