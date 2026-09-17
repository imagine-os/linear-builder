---
key: "tables/grid/core"
title: "Grid core: virtualisation, data binding, selection model and keyboard navigation"
project: "tables"
parent: "PAP-165"
phase: "P1"
type: "Build"
priority: 1
size: "M"
surfaces: []
milestone: "Grid with sort, filter, group"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc"
identifier: "PAP-341"
status: "created"
createdAt: "2026-09-17"
---

# Grid core: virtualisation, data binding, selection model and keyboard navigation

**Goal**

Render 100k rows and 30 columns at 60 fps with a correct selection model and full keyboard navigation, as the foundation the editing and column children extend.

**Scope**

In: `views/grid/{GridView,useGridSelection,useGridKeyboard,virtual}.tsx`, sticky header, frozen columns, density, empty and skeleton states. Out: editing, clipboard, bulk bar, column menu, `RecordPanel` (siblings).

**Spec**

* TanStack Table with both axes virtualised; `useViewQuery` page 100 and prefetch; row heights 32, 40, 56, 88 px.
* Selection `{ anchor, focus }` ranges plus checkbox rows; "Select all N matching" confirms above 500.
* Keyboard: arrows, Shift+arrows, Tab, Home, End, PageUp, PageDown, Ctrl+Home, Ctrl+End, Space; commands `grid.*` via PAP-151; roving tabindex per PAP-153; `role="grid"` with `aria-rowindex`, `aria-colindex`, `aria-activedescendant`.
* Frozen columns with `position: sticky` and a scroll shadow; frozen total capped at 60 percent.

**Interface contract**

Provides: `<GridView />` shell with `cellRenderer`, `headerSlot`, `toolbarSlot`, `useGridSelection`, `useGridKeyboard`, commands `grid.*`. Consumes: `useViewQuery` (PAP-163), cells (PAP-164), `EmptyState` (PAP-71), commands (PAP-151), focus (PAP-153).

**Definition of done**

* Selection and keyboard reducers unit-tested; 10k-row story; screenshots at 375, 768, 1024, 1440, 1920 in three themes and four densities; performance trace meets budgets; axe clean.

**Test plan**

* Unit: reducers; frozen cap maths.
* E2E: scroll to row 50,000 under 2 s; keyboard traversal; screen-reader announcements spot check.
* Visual: matrix above.

**Demo**

Open `/demo/grid`, scroll fast, select a range with Shift+arrows, freeze a column.

**Edge cases**

* 375 px first column frozen; denied `update` shows a read-only cursor.

**Dependencies**

PAP-163, PAP-164, PAP-71, PAP-151 (hard). Blocks the sibling children.

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

M: performance work.
