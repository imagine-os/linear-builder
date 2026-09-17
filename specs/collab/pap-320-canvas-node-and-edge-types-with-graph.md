---
identifier: "PAP-320"
title: "Canvas node and edge types with graph loader"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer", "Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: "PAP-132"
children: []
blockedBy: ["PAP-114", "PAP-127"]
blocks: ["PAP-321"]
key: "collab/canvas/nodes-edges-loader"
url: "https://linear.app/paperos/issue/PAP-320/canvas-node-and-edge-types-with-graph-loader"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:27.539Z"
---

# PAP-320: Canvas node and edge types with graph loader

**Goal**

Lay the foundation of the canvas view (PAP-132): React Flow node and edge types for the spec graph, the oRPC loader that serves the generated `FlowGraph` with a hash, and locked spec-derived elements that cannot be deleted.

**Scope**

In:

* `packages/collab/canvas/` on `@xyflow/react` 12: nodes `PageNode` (title, route, surface colour, audience chips, status badge, thumbnail, open-spec and open-page actions), `EntityNode`, `ExternalNode`, `StartNode`, `GroupNode`, `NoteNode`, `RegionNode`; edges `navigate`, `mutation`, `integration`, `reads`, `writes` with labels `on` and `guard`.
* oRPC `canvas.graph.get(appId) -> { graph, specHash, generatedAt }` reading `specs/.generated/flow-graph.json` (PAP-123).
* `registerNodeType(kind, component)` registry (PAP-113 adds `CharacterNode`).
* Layout: generated positions from the graph; locked flag on spec-derived nodes and edges.

Out: Yjs overlay, filters, export, performance run (siblings).

**Spec**

* Node colours and typography from PAP-66 tokens; dark theme; minimum readable label at zoom 0.6.
* Edge styles distinct per kind; `reads`/`writes` dashed.
* Storybook story per node type in light and dark.

**Interface contract**

Exposes `PaperCanvas` (read-only mode), node and edge components, `registerNodeType`, `canvas.graph.get`, `CanvasGraph` TypeScript type mirroring `FlowGraph`. Consumes `FlowGraph` JSON (PAP-123), spec schema (PAP-114), tokens (PAP-66), `Badge` and chips (PAP-71), PAP-127's library decision.

**Definition of done**

* Example graph renders with all node and edge kinds; Storybook stories published; axe clean on toolbar-less canvas focus order.
* Linear comment with 1280 screenshots in both themes.

**Test plan**

* Vitest: loader maps every `FlowGraph` node and edge kind, unknown kinds fall back to a generic node with a warning, locked elements reject `onNodesDelete`.
* Component: each node type story renders and passes axe.
* Playwright: load the example graph at 1280, click a page node's open-spec action, assert navigation.

**Demo**

Open `/_app/dev/canvas`, see the generated map with coloured surfaces, hover an edge label, click a page node and open its spec. Under two minutes.

**Edge cases**

* Node thumbnail 404: placeholder with surface icon.
* Graph with zero edges: renders nodes in a grid.
* `specHash` missing: treated as stale.

**Dependencies**

PAP-123, PAP-114, PAP-127 (hard). Blocks siblings 2 and 3.

**Agent**

Built by Nova (Canvas Cartographer). Reviewed by Iris (visual consistency) and Sentinel (Code Reviewer).

**Size**

M: seven node types, five edge types and a loader.
