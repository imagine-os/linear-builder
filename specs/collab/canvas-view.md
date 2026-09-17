---
identifier: "PAP-132"
title: "Build the canvas view (tldraw or React Flow) showing the UX flow of the whole app, generated from specs and editable"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff", "Developer"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-127", "PAP-140"]
blocks: ["PAP-113", "PAP-157"]
key: "collab/canvas-view"
url: "https://linear.app/paperos/issue/PAP-132/build-the-canvas-view-tldraw-or-react-flow-showing-the-ux-flow-of-the"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-132: Build the canvas view (tldraw or React Flow) showing the UX flow of the whole app, generated from specs and editable

**Goal**

Show the whole app as a live map: pages, transitions, entities and external systems generated from specs, laid out automatically, filterable by audience, annotated and rearranged collaboratively in real time, with comments on any node. This is the "canvas view of the UX flow" Justin asked for, and the base other graph views (agent org chart) reuse.

**Scope**

In:
- `packages/collab/canvas/` on `@xyflow/react` 12 (per `collab/collab-research` ADR; if tldraw wins, the node model below still applies) with custom node types `PageNode` (title, route, surface colour from tokens, audience chips, status badge, thumbnail when available, open-spec and open-page actions), `EntityNode`, `ExternalNode` (connector icon), `StartNode`, `GroupNode` (surface and nav-section compounds), `NoteNode` (sticky note, markdown), `RegionNode` (labelled rectangle); edge types `navigate`, `mutation`, `integration`, `reads`, `writes` with distinct styles and labels (`on`, `guard`).
- Loader from `spec-builder/spec-to-canvas` `FlowGraph` (`specs/.generated/flow-graph.json` served by oRPC `canvas.graph.get(appId)` with `specHash`); spec-derived nodes and edges are locked (not deletable, positions overridable).
- Collaborative overlay in a Yjs document `canvas:<appId>` on `realtime/yjs-server` (Hocuspocus room): `positions` map (node id to xy override), `notes`, `regions`, `hidden` set, `viewportBookmarks`; awareness shows cursors and selections via `realtime/presence`; undo and redo with `y-undomanager`.
- Route `/_app/dev/canvas` (developer and staff) with toolbar: audience filter, surface filter, edge kind toggles, search and focus node, fit view, minimap, reset layout, export PNG/SVG (`html-to-image`), stale banner when `specHash` differs from the loaded graph with a reload action.
- Comments: nodes are comment anchors (`anchor_type: canvas_node`) via `collab/comments`; comment count badge on nodes.
- Keyboard: arrow keys move selection, `Enter` opens spec, `/` search; touch pan and pinch; pen deferred to `input/pen`.

Out: editing specs on the canvas (opens `spec-builder/spec-editor-ui`), freehand drawing, runtime analytics overlays, the org chart itself (`agents/org-chart-ui` reuses this package).

**Spec**

- Rendering budget: 300 nodes and 600 edges at 60 fps while panning on a 2020 laptop; use `onlyRenderVisibleElements`, memoised nodes, edge simplification below zoom 0.4.
- Merge rule: generated positions apply unless an override exists; "reset layout" clears overrides for selected nodes only.
- Node colours and typography from `design-system/tokens`; dark theme supported; minimum readable label at zoom 0.6.
- Yjs doc persisted by Hocuspocus to Postgres; document name authorised for the tenant's staff via the auth hook.
- Deep link `?node=<id>&audience=<id>` restores filter and focus.

**Definition of done**

- Vitest: loader mapping, override merge, filter logic, stale detection; Playwright: load the example graph, filter by audience, move a node in one context and see it move in another within 1 s, add a note, comment on a node, export PNG; screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 render read-only with a "larger screen recommended" notice.
- Performance run with a generated 300-node graph shows 55 fps or more (numbers in comment).
- axe clean for toolbar and node focus order.
- `docs/collab/canvas.md`; CHANGELOG entry; Linear comment with screenshots, video from `quality/video-replays` and the demo link.
- `agents/org-chart-ui` owner confirms the node API is reusable (comment).

**Edge cases**

- Graph regenerated with a renamed page id: override orphaned; a cleanup action lists orphans.
- Two users drag the same node: Yjs last-writer wins; a brief highlight shows the other cursor.
- Hocuspocus down: canvas loads read-only from the JSON with a banner; notes disabled.
- Thousands of `reads` edges: hidden by default above 500 edges, toggle shows them.
- Node thumbnail 404: placeholder with surface icon.
- Export of a 20k-pixel canvas: export the current viewport or a selected region, capped at 8k pixels.

**Dependencies**

`spec-builder/schema` and `spec-builder/spec-to-canvas` (graph), `realtime/yjs-server` (hard for collaboration), `collab/collab-research` (library). Soft: `collab/comments`, `realtime/presence`, `quality/playwright-matrix` thumbnails. Unblocks `agents/org-chart-ui`, `input/pen`, `collab/screenshot-annotations` shares the overlay code.

**Agent**

Built by Nova (Canvas Cartographer, CRDT Engineer). Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Iris for visual consistency.

**Size**

L: custom nodes, collaborative overlay, filters, export and performance work.
