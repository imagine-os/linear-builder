---
key: "child/PAP-214/2"
title: "Confirm validation and runtime, cross-link confirmed choices, consolidate ADRs, compose files and registry entries"
project: "libraries"
parent: "PAP-214"
phase: "P0"
type: "Research"
priority: 2
size: "S"
surfaces: ["Developer"]
milestone: "Core adoptions decided"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-libraries-9-63c73eed632d"
identifier: "PAP-297"
status: "created"
createdAt: "2026-09-17"
---

# Confirm validation and runtime, cross-link confirmed choices, consolidate ADRs, compose files and registry entries

**Goal**

Close the backend survey: decide Zod 4 versus Valibot and ArkType and Node 22 versus Bun for the API, confirm the already-owned choices by cross-link (Better Auth, Drizzle, ElectricSQL, Hocuspocus, oRPC), and consolidate everything into the ADR index, `ops/compose/`, and registry entries. Time-box 2 hours.

**Scope**

In: validation and runtime scorecards (Bun tested against Tauri sidecars and native modules); cross-link sections pointing at PAP-56, PAP-32, PAP-31, PAP-139, PAP-35 with no re-scoring; ADR index update; registry drafts for every winner from all three children; CHANGELOG entry; summary comment on PAP-214 with the full decision table.

Out: any new candidates.

**Spec**

* Runtime defaults to Node 22 on any Bun incompatibility with a chosen library.
* Consolidated table columns: decision, package or image, version, RAM, consuming issue, fallback, migration hours, ADR.

**Interface contract**

Provides: ADRs `validation`, `runtime`, the consolidated decision table in `docs/libraries/backend-decisions.md`, registry drafts, ADR index entries. Consumes: siblings 1 and 2 outputs, PAP-209, PAP-216 CLI when live (else a Linear comment for Scout).

**Definition of done**

* Two ADRs accepted; decision table complete for all eleven decisions; registry drafts exist for each winner.
* License check passes on all chosen packages and images.
* CHANGELOG entry and summary comment posted.

**Test plan**

* Vitest smoke: Zod 4 and the runner-up validate the same 20 schemas; timing recorded.
* Bun compatibility script against the current lockfile committed with output.
* `pnpm lib registry check` passes if the registry is live.

**Demo**

Reviewer opens `backend-decisions.md` and sees eleven rows each linking to an accepted ADR, then runs `pnpm lib score docs/libraries/scorecards/runtime.yaml` and reads the table. Under one minute.

**Edge cases**

* A confirmed choice's research issue is still open: cross-link marked "pending" and not blocked.
* Registry not live: drafts kept in `docs/registry/drafts/` for PAP-216 to import.
* Sibling ADR still `proposed`: table marks it and the summary lists what is outstanding.

**Dependencies**

Siblings 1 and 2 (hard), PAP-209, PAP-216 (soft).

**Agent**

Researched by Scout (Library Evaluator). Reviewed by Atlas.

**Size**

S
