---
identifier: "PAP-945"
title: "Per-module Postgres schema namespaces (`CREATE SCHEMA <module>`) with RLS defaults, so a module's tables are physically grouped and a swap can expand-contract inside one schema"
project: "data-layer"
projectName: "Data Layer & Database"
phase: ""
type: "Spec"
priority: 3
surfaces: ["Developer"]
milestone: null
state: "Triage"
parent: null
children: []
blockedBy: []
blocks: []
key: "r4/triage/32"
url: "https://linear.app/paperos/issue/PAP-945/per-module-postgres-schema-namespaces-create-schema-module-with-rls"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:07:54.090Z"
model: null
effort: null
estimate: null
dueDate: null
cycle: null
---

# PAP-945: Per-module Postgres schema namespaces (`CREATE SCHEMA <module>`) with RLS defaults, so a module's tables are physically grouped and a swap can expand-contract inside one schema

**Triage (round 4, 2026-09-18)** — filed from the gap analysis, not yet specified. Priority 3 until Atlas promotes it; no estimate, due date or cycle. Type and Surface labels are provisional.

**Goal**

PAP-265 applies migrations per module but tables share `public`; swap safety and `pnpm modules:purge` (PAP-266) become simpler with namespaces.

**Source**

Suggested in `plan/round4/gaps/module-system.json` (crossProjectSuggestions) for project `data-layer`. Nearest existing issue at filing time: PAP-401 (0.38).

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
