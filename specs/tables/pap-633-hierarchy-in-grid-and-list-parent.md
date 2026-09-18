---
identifier: "PAP-633"
title: "Hierarchy in grid and list: parent relation field drives indented sub-rows, expand and collapse, drag to re-parent and rollups along the tree"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-331", "PAP-340", "PAP-343"]
blocks: []
key: "r4/tables/tree-hierarchy-grid"
url: "https://linear.app/paperos/issue/PAP-633/hierarchy-in-grid-and-list-parent-relation-field-drives-indented-sub"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:35.486Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-633: Hierarchy in grid and list: parent relation field drives indented sub-rows, expand and collapse, drag to re-parent and rollups along the tree

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). ClickUp subtasks, Notion sub-items and Smartsheet hierarchy rows show work as a tree. Let a self-relation with `limitOne` act as `hierarchyField` so the grid and list render indented children with expand and collapse, drag to re-parent and tree-aware rollups.

**Scope**

In: `ViewSpec.options.hierarchyField` for `grid|list`; `compileTree` (recursive CTE, depth cap 10) in PAP-335; `TreeRow` indentation and toggles; re-parent via PAP-331 drop with `canDrop` preventing cycles; PM issues (PAP-102) as first consumer.

Out: mind map view, Gantt summary bars (PAP-346 reads `hierarchyField` later), cross-dataset trees.

**Spec**

* Root rows are those whose `hierarchyField` is empty or whose parent is filtered out (shown flat with a "parent hidden" chip); children load per parent via `views.query` with `groupPath`-style parent filter, page 100; expansion state persisted in `spec.options.expanded[]`.
* Sorting applies within siblings; grouping is disabled while `hierarchyField` is set (toast explains); aggregates in a parent row summarise its subtree through a `rollup` over the self-relation when `showSubtreeTotals`.
* Re-parent: drag a row onto another (PAP-331 `canDrop` rejects ancestors and depth over 10), keyboard `Alt+Right|Left` indents and outdents; writes the relation and `position` optimistically.
* Accessibility: `role="treegrid"`, `aria-level`, `aria-expanded`, `aria-setsize`; screen reader announces level on focus.
* Compiler: `WITH RECURSIVE` path array for `sortPath`, cycle guard by path containment; `EXPLAIN` on the 100k seed shows the relation index.

**Interface contract**

Provides: `hierarchyField` option, `compileTree`, `<TreeRow />`, commands `grid.indent|outdent|expand|collapse`. Consumes: grid columns and group headers (PAP-343), relation type (PAP-340), drag (PAP-331), compiler core (PAP-335). Consumed by PAP-102 issues, PAP-427 packs.

**Definition of done**

* Treegrid green in Vitest, integration and Playwright on a 5-level seed; screenshots at 375, 1024, 1920; axe treegrid rules clean; `docs/views/hierarchy.md`; CHANGELOG.

**Test plan**

* Unit: path sort; cycle detection; depth cap; indent/outdent reducer.
* Integration: recursive CTE on 100k rows with 10k roots under 150 ms p95.
* E2E: expand a parent, indent a sibling by keyboard, drag a row under another, see totals update.

**Demo**

Reviewer switches the demo tasks grid to hierarchy by `parent`, expands two levels and re-parents a task by drag. Under two minutes.

**Edge cases**

* Parent in trash: children shown as roots with a chip.
* Import creates a cycle: rows flagged, tree renders the cycle members flat.

**Dependencies**

PAP-343 (hard), PAP-340 (hard), PAP-331 (hard). Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.
