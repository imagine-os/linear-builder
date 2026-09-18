---
identifier: "PAP-942"
title: "Cross-module unit of work: `UnitOfWorkPort` in `contract-data-layer` that lets a request span repositories from two modules in one transaction with the outbox"
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
key: "r4/triage/29"
url: "https://linear.app/paperos/issue/PAP-942/cross-module-unit-of-work-unitofworkport-in-contract-data-layer-that"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:11.039Z"
model: null
effort: null
estimate: null
dueDate: null
cycle: null
---

# PAP-942: Cross-module unit of work: `UnitOfWorkPort` in `contract-data-layer` that lets a request span repositories from two modules in one transaction with the outbox

**Triage (round 4, 2026-09-18)** — filed from the gap analysis, not yet specified. Priority 3 until Atlas promotes it; no estimate, due date or cycle. Type and Surface labels are provisional.

**Goal**

Business-core posting rules (PAP-394) and tables automations (PAP-388) both need it; today each module opens its own transaction.

**Source**

Suggested in `plan/round4/gaps/module-system.json` (crossProjectSuggestions) for project `data-layer`. Nearest existing issue at filing time: PAP-533 (0.38).

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

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/git-credential-helper` = PAP-533.
