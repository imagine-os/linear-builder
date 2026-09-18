---
identifier: "PAP-634"
title: "Workload view: capacity per person per period from an assignee field and an effort field, with over-allocation highlighting"
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
blockedBy: ["PAP-336", "PAP-345"]
blocks: []
key: "r4/tables/workload-view"
url: "https://linear.app/paperos/issue/PAP-634/workload-view-capacity-per-person-per-period-from-an-assignee-field"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:36.278Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-634: Workload view: capacity per person per period from an assignee field and an effort field, with over-allocation highlighting

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). ClickUp Workload and Box views and Monday's Workload widget answer "who is overloaded next week". Build an eleventh view kind on the timeline engine: one lane per assignee, one cell per period, filled by summed effort against a capacity.

**Scope**

In: `views/workload/{WorkloadView,register}.tsx`; options `{ assigneeField (user), effortField? (number|duration; default count), startField, endField?, period: 'day'|'week', capacity: { default, perUser: Record<userId, number> } }`; compiler: two-level groups (assignee, period bucket) with `sum`; drag a bar to another lane to reassign.

Out: resource levelling suggestions, vacations and calendars (capacity is a number), cross-dataset workloads.

**Spec**

* Lanes from `views.groups` level 1 on `assigneeField` (unassigned lane last); cells from level 2 bucketed by `period` over the visible range (PAP-344 `TimeScale`); effort spread evenly across the days a record spans when `endField` exists.
* Cell fill = sum / capacity; colours `success` under 80 percent, `warning` 80 to 100, `danger` over 100 with the overflow number; clicking a cell emits `onFilter` for the assignee and period so a grid block lists the items.
* Rows expand to show the underlying bars (PAP-345 renderer); dragging a bar to another lane writes `assigneeField`; keyboard `Alt+Up|Down` reassigns.
* Capacity per user editable inline by `dataset.manage` holders and stored in `spec.options`; default 40 h per week or 5 items.

**Interface contract**

Provides: `<WorkloadView />`, `workloadOptionsSchema`, registration `kind: 'workload'`, `spreadEffort(record, period)`. Consumes: timeline engine and bars (PAP-345, PAP-344), groups and aggregates (PAP-336), `user` cells (PAP-339), `ViewHost` registry.

**Definition of done**

* View green in Vitest and Playwright on the demo seed; screenshots at 768, 1024, 1920 in three themes; axe clean; `docs/views/workload.md`; CHANGELOG.

**Test plan**

* Unit: effort spreading across spans and DST; capacity colours; bucket alignment with week start.
* Integration: two-level groups over 10k rows return within 300 ms.
* E2E: switch the demo tasks to workload by owner, see an over-allocated week, drag a bar to another owner and see both cells update.

**Demo**

Reviewer opens workload by owner for the next four weeks, spots a red cell, clicks it to list the tasks and reassigns one. Under two minutes.

**Edge cases**

* Records without dates: excluded with a count chip.
* Multi-user assignee (multiSelect): effort split equally, documented.

**Dependencies**

PAP-345 (hard), PAP-336 (hard). Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
