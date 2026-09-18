---
identifier: "PAP-943"
title: "Monthly partition helper for finance event tables"
project: "data-layer"
projectName: "Data Layer & Database"
phase: ""
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: null
state: "Triage"
parent: null
children: []
blockedBy: []
blocks: []
key: "r4/triage/30"
url: "https://linear.app/paperos/issue/PAP-943/monthly-partition-helper-for-finance-event-tables"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:07:52.270Z"
model: null
effort: null
estimate: null
dueDate: null
cycle: null
---

# PAP-943: Monthly partition helper for finance event tables

**Triage (round 4, 2026-09-18)** — filed from the gap analysis, not yet specified. Priority 3 until Atlas promotes it; no estimate, due date or cycle. Type and Surface labels are provisional.

**Goal**

`fin_usage_event`, `usage_event` (PAP-391) and `attr_event` (PAP-194) each write their own partition-ahead job; one `definePartitionedTable()` helper in `packages/db` would remove three copies.

**Source**

Suggested in `plan/round4/gaps/business-core.json` (crossProjectSuggestions) for project `data-layer`. Nearest existing issue at filing time: PAP-203 (0.45).

**Scope**

To be specified when promoted (round-4 triage skeleton).

**Spec**

To be specified when promoted (round-4 triage skeleton).

**Interface contract**

To be specified when promoted (round-4 triage skeleton).

**Test plan**

To be specified when promoted (round-4 triage skeleton).

**Definition of done**

To be specified when promoted (round-4 triage skeleton).

**Edge cases**

To be specified when promoted (round-4 triage skeleton).

**Dependencies**

To be specified when promoted (round-4 triage skeleton).

**Agent**

To be specified when promoted (round-4 triage skeleton).

**Size**

To be specified when promoted (round-4 triage skeleton).

**Demo**

To be specified when promoted (round-4 triage skeleton).
