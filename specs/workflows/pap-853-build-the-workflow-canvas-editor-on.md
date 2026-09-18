---
identifier: "PAP-853"
title: "Build the workflow canvas editor on React Flow: node palette from the step catalogue, validation, versions and diff, test runs with fixture events, convert from automation"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "E-signature, canvas editor and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-320", "PAP-321", "PAP-331", "PAP-390", "PAP-851", "PAP-852"]
blocks: []
key: "r4/workflows/canvas-editor"
url: "https://linear.app/paperos/issue/PAP-853/build-the-workflow-canvas-editor-on-react-flow-node-palette-from-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:55.170Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-853: Build the workflow canvas editor on React Flow: node palette from the step catalogue, validation, versions and diff, test runs with fixture events, convert from automation

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let a staff user draw a process: a canvas editor reusing the PAP-320 node and edge types and the PAP-321 collaborative overlay, a palette from the step catalogue, inline config forms, validation that blocks publishing broken graphs, versions with a visual diff, test runs against fixture events, and a one-click conversion from a table automation (PAP-390).

**Scope**

In: Route `/console/workflows/:id/edit` (spec) with the canvas engine from PAP-320 (`workflow.step` node type, `workflow.edge` with condition labels), Yjs-backed layout and notes (PAP-321) so two people can edit together, keyboard-accessible node operations (PAP-330). Palette and inspector: drag from the catalogue (PAP-331 `DropZone`), inspector shows the step config form; validation panel (unreachable steps, missing `next`, cycles without a wait, unknown expressions) blocks publish. Versions: publish creates a version; version list with a graph diff (added, removed, changed nodes); rollback republishes an older version. Test run: pick a fixture event (or a recent real event from PAP-303) and run in dry-run mode with the run engine's replay; timeline shown beside the canvas; `Convert to workflow` from the PAP-390 automation page maps trigger, conditions and actions.

Out: Freeform drawing beyond notes. BPMN import/export.

**Spec**

* The canvas is generated from the definition and writes back to it; layout is a separate document so a definition diff never contains coordinates
* Autolayout (dagre) on demand; manual positions persist per version
* Large graphs (300 nodes) stay at 60 fps with the PAP-322 virtualisation techniques; minimap and search
* Validation messages deep-link to the node and are announced to screen readers; publish is disabled with the reasons listed

**Interface contract**

Provides: editor page, `workflow.step|edge` node types, version diff component, test run panel, convert-from-automation action. Consumes: canvas node types and overlay (PAP-320, PAP-321), performance techniques (PAP-322), automation builder (PAP-390), drag-and-drop (PAP-331), keyboard alternative (PAP-330), step catalogue and engine. Consumed by: business packs (workflows authored and exported as pack content), assistant ("build me a workflow" drafts open here in v0.3).

**Definition of done**

* Two users co-edit a workflow; publish blocked by validation then succeeds; test run shows a timeline; conversion from a starter automation produces a valid definition; screenshots at 1024 and 1920 (phones show read-only)
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: graph validation rules over 15 fixture graphs; diff algorithm; autolayout determinism.
* E2E: drag a node, configure, connect, publish, roll back; keyboard-only node insertion (PAP-330); two contexts co-editing.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Convert the "notify on overdue invoice" automation into a workflow, add an approval and a wait, publish, and test-run it with last week's real event.

**Edge cases**

* Definition edited by API while open in the editor: the Yjs overlay shows a stale banner (PAP-144) and offers reload; the editor never silently overwrites
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-852 (hard), PAP-320, PAP-321 (hard), PAP-390, PAP-331, PAP-330 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/workflows/step-catalogue` = PAP-852.
