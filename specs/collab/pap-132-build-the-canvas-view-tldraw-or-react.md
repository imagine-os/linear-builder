---
identifier: "PAP-132"
title: "Build the canvas view (tldraw or React Flow) showing the UX flow of the whole app, generated from specs and editable"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: ["PAP-322", "PAP-320", "PAP-321"]
blockedBy: ["PAP-114", "PAP-123", "PAP-127", "PAP-140", "PAP-641", "PAP-642", "PAP-643"]
blocks: ["PAP-113", "PAP-157"]
key: "collab/canvas-view"
url: "https://linear.app/paperos/issue/PAP-132/build-the-canvas-view-tldraw-or-react-flow-showing-the-ux-flow-of-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:31:01.574Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-29"
cycle: null
---

# PAP-132: Build the canvas view (tldraw or React Flow) showing the UX flow of the whole app, generated from specs and editable

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Umbrella: show the whole app as a live map. Pages, transitions, entities and external systems come from specs, lay out automatically, filter by audience, and can be annotated and rearranged collaboratively with comments on any node. This is the canvas view Justin asked for and the base PAP-113 (agent org chart) reuses. Planned as three work packages; the umbrella owns the integration test and performance evidence.

**Scope**

Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Canvas node and edge types with graph loader** — `@xyflow/react` 12 (per PAP-127) custom nodes `PageNode`, `EntityNode`, `ExternalNode`, `StartNode`, `GroupNode`, `NoteNode`, `RegionNode`; edges `navigate`, `mutation`, `integration`, `reads`, `writes`; oRPC `canvas.graph.get(appId)` serving `FlowGraph` from PAP-123 with `specHash`; locked spec-derived elements.
2. **Collaborative overlay: notes, regions, overrides in Yjs** — room `canvas:<appId>` on PAP-140 holding `positions`, `notes`, `regions`, `hidden`, `viewportBookmarks`; presence cursors from PAP-141; undo via `y-undomanager`; reset layout for selected nodes.
3. **Filters, deep links, export and 300-node performance run** — audience and surface filters, edge-kind toggles, search and focus, minimap, `?node=&audience=` deep links, PNG/SVG export (`html-to-image`), stale banner on `specHash` change, fps evidence.

Parent owns route `/_app/dev/canvas`, comment anchors on nodes (`canvas_node`, PAP-131), `docs/collab/canvas.md`, integration test.

Out: editing specs on the canvas (PAP-124), freehand drawing (PAP-157), the org chart itself.

**Spec**

* Budget: 300 nodes and 600 edges at 60 fps while panning on a 2020 laptop; `onlyRenderVisibleElements`, memoised nodes, edge simplification below zoom 0.4.
* Merge rule: generated positions apply unless an override exists.
* Colours and type from PAP-66 tokens; dark theme; minimum readable label at zoom 0.6.
* Room authorised for tenant staff via the PAP-140 auth hook.

**Interface contract**

Exposes: package `packages/collab/canvas` with `<PaperCanvas graph overlayRoom filters onNodeOpen />`, node type registry `registerNodeType(kind, component)` (PAP-113 registers `CharacterNode`), `CanvasOverlayDoc` Yjs schema (`Y.Map` keys above), `useCanvasOverlay(room)`, `exportCanvas({ format, region })`; oRPC `canvas.graph.get(appId) -> { graph: FlowGraph, specHash, generatedAt }`; comment anchor `canvas:<canvasId>:<nodeId>`; deep-link params. Consumes: `FlowGraph { nodes[{ id, kind, label, route?, surface?, audiences[], status }], edges[{ id, from, to, kind, on?, guard? }] }` from PAP-123, provider from PAP-140, awareness payload from PAP-141, `useThreads` from PAP-131, thumbnails from PAP-82 when present.

**Definition of done**

* All three work packages merged; integration test green; performance run shows 55 fps or more on a generated 300-node graph (numbers in the comment).
* Screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 render read-only with a "larger screen recommended" notice.
* axe clean for toolbar and node focus order; `docs/collab/canvas.md`; CHANGELOG entry; Linear comment with screenshots, PAP-83 video and demo link; PAP-113 owner confirms the node API is reusable.

**Test plan**

* Integration (parent): Playwright, two contexts on the example graph: filter by audience `customer`, drag `PageNode` "Inbox" in context A and assert its position in B within 1 s, add a note, comment on a node, export PNG and assert file size > 0, change `specHash` on the mock and assert the stale banner. Runs at 1280 and 1920.
* Performance: Playwright CDP trace while panning a generated 300/600 graph for 5 s; assert mean fps ≥ 55; result JSON committed.
* Unit tests per work package (loader mapping, override merge, filter logic, stale detection, export bounds).
* Visual: Gate 3 baselines at five widths, both themes; Storybook stories per node type with axe.

**Demo**

Open `/_app/dev/canvas`, filter to the customer audience, drag a page node, add a sticky note, open a second tab and see both changes; click a node, press `Enter` to open its spec; export PNG. Under two minutes.

**Edge cases**

* Renamed page id: orphaned override listed by a cleanup action.
* Two users drag one node: Yjs last writer wins with a brief cursor highlight.
* Hocuspocus down: read-only from JSON with a banner.
* Over 500 `reads` edges: hidden by default, toggle shows them.
* 20k-pixel export: viewport or selection only, capped at 8k pixels.

**Dependencies**

PAP-114, PAP-123, PAP-127, PAP-140 (hard). Soft: PAP-131, PAP-141, PAP-82. Blocks PAP-113, PAP-157; shares overlay code with PAP-137.

**Agent**

Built by Nova (Canvas Cartographer, CRDT Engineer). Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Iris for visual consistency.

**Size**

L, planned as three M work packages (child issues pending the issue limit).
