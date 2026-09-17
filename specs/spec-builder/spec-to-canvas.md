---
identifier: "PAP-123"
title: "Emit the UX-flow graph (pages, transitions, roles) from specs for the canvas view"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-117"]
blocks: []
key: "spec-builder/spec-to-canvas"
url: "https://linear.app/paperos/issue/PAP-123/emit-the-ux-flow-graph-pages-transitions-roles-from-specs-for-the"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-123: Emit the UX-flow graph (pages, transitions, roles) from specs for the canvas view

**Goal**

Compile every page spec plus `app.spec.yaml` into one UX-flow graph (pages, transitions, audiences, entities, external systems) with deterministic layout positions, so the canvas view opens an accurate map of the whole app and updates whenever specs change. Specs draw the map; nobody maintains a diagram by hand.

**Scope**

In:
- `buildFlowGraph(specs: ResolvedPageSpec[], app: AppSpec): FlowGraph` in `packages/spec/src/graph/build.ts` with Zod 4 `FlowGraph` schema:
  `nodes: [{ id, type: page|external|entity|start, label, route?, surface?, audiences[], layoutTemplate?, status, specPath, thumbnail? }]`,
  `edges: [{ id, from, to, kind: navigate|mutation|integration|reads|writes, on?, guard?, audiences[] }]`,
  `groups: [{ id, kind: surface|navSection, label, nodeIds[] }]`, `meta: { app, generatedAt, specHash }`.
- Edge derivation: `events[]` produce `navigate` edges; `data.queries` produce `reads` edges to entity nodes; `data.mutations` produce `writes`; `integrations[]` produce `integration` edges to external nodes; `navigation` roots produce `start` node edges per audience.
- Layout with `elkjs` 0.9 (layered, direction right, groups as compound nodes) run in Node; positions stored in the graph so the canvas renders instantly and consistently across clients.
- CLI `pnpm spec gen:graph` writing `specs/.generated/flow-graph.json` (committed, drift-checked) and `flow-graph.diff.json` against `origin/main` (added, removed, changed nodes and edges) for PR comments.
- Thumbnail lookup: if `quality/playwright-matrix` artifacts exist for the page at 1280 light, attach the MinIO URL.
- Loader `packages/collab/canvas/loaders/spec.ts` that maps `FlowGraph` to React Flow nodes and edges (types agreed with `collab/canvas-view`).

Out: rendering and editing (`collab/canvas-view`), manual annotations, runtime analytics on edges.

**Spec**

- Node ids are stable: `page:<specId>`, `entity:<entityId>`, `ext:<connector>`, `start:<audience>`; positions are keyed by id so manual overrides in the canvas survive regeneration.
- Audience filtering is precomputed: each node and edge lists audiences that can reach it, computed from `access.view` and edge guards, so the canvas can filter without re-evaluating policies.
- Unreachable pages (no incoming navigate edge and not in navigation) get `flags: [unreachable]`; dead transitions to deprecated pages get `flags: [deadEnd]`; both listed in the PR comment.
- Layout is deterministic given the same input (ELK options fixed, node order sorted); verified by generating twice.
- Graph for 300 pages builds and lays out under 5 s.

**Definition of done**

- Vitest: edge derivation for each kind, audience reachability, flags, stable ids, layout determinism (two runs equal), diff output.
- Graph generated for paperos-template examples and rendered in `collab/canvas-view` (screenshot at 1280 and 1920) or, if the canvas is not merged, in a temporary React Flow dev route.
- PR comment shows the diff summary on a seeded spec change (link).
- `docs/spec/flow-graph.md` documents the schema; CHANGELOG entry; Linear comment with screenshots.
- Drift job in gate 1 fails when specs change without regenerating.

**Edge cases**

- Cyclic navigation (A to B to A): ELK handles cycles; edges marked `back: true` for styling.
- Page reachable by many audiences (50): audiences stored as ids, not expanded labels, to keep the file small.
- Spec with `x-external` transition to another app: external node of type `external` labelled with the app id.
- Entity referenced by no page: included with `flags: [orphan]` so the data team sees it.
- Thousands of edges: `reads` and `writes` edges collapsed per page-entity pair with counts.
- Thumbnail artifact expired (30-day retention): field omitted, canvas shows a placeholder.

**Dependencies**

`spec-builder/schema` and `spec-builder/app-level-spec` (hard). `collab/canvas-view` for the loader contract (agree node and edge types in a shared file `packages/collab/canvas/types.ts` first). Soft: `quality/playwright-matrix` thumbnails, `spec-builder/integrations-section` external nodes. Consumed by `agents/org-chart-ui` for the same graph loader pattern.

**Agent**

Built by Nova (Canvas Cartographer). Reviewed by Quill for spec semantics and Sentinel (Code Reviewer).

**Size**

M: pure data transformation plus ELK layout and a diff.
