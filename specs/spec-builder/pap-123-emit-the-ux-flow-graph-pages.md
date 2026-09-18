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
blocks: ["PAP-132", "PAP-320", "PAP-362", "PAP-731"]
key: "spec-builder/spec-to-canvas"
url: "https://linear.app/paperos/issue/PAP-123/emit-the-ux-flow-graph-pages-transitions-roles-from-specs-for-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:41.216Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-26"
cycle: null
---

# PAP-123: Emit the UX-flow graph (pages, transitions, roles) from specs for the canvas view

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Compile every page spec plus `app.spec.yaml` into one UX-flow graph (pages, transitions, audiences, entities, external systems) with deterministic layout positions, so the canvas view opens an accurate map of the whole app and updates whenever specs change. Specs draw the map; nobody maintains a diagram by hand.

**Scope**

* In: `buildFlowGraph()` in `packages/spec/src/graph/build.ts`, Zod `FlowGraph`, ELK layout, audience reachability, flags, `pnpm spec gen:graph [--diff]`, `docs/spec/flow-graph.md`, a temporary dev route if PAP-132 is not merged.
* Out: canvas rendering and interaction (PAP-132), thumbnails production (PAP-82), the org chart (PAP-113 reuses the loader pattern).

**Spec**

* `nodes[] { id, type: page | external | entity | start, label, route?, surface?, audiences[], layoutTemplate?, status, specPath, thumbnail?, flags[], position }`, `edges[] { id, from, to, kind: navigate | mutation | integration | reads | writes, on?, guard?, audiences[], back?, count? }`, `groups[] { id, kind: surface | navSection, label, nodeIds[] }`, `meta { app, generatedAt, specHash }`.
* Derivation: `events[]` produce `navigate`; `data.queries` produce `reads`, `data.mutations` produce `writes` (collapsed per page and entity with counts); `integrations[]` produce `integration` edges to `ext:<connector>`; navigation roots produce `start:<audience>` edges.
* Stable ids `page:<id>`, `entity:<id>`, `ext:<connector>`, `start:<audience>`; positions keyed by id so manual overrides survive.
* Layout with `elkjs` 0.9 layered, direction right, groups as compound nodes, fixed options and sorted node order for determinism; 300 pages under 5 s.
* Flags: `unreachable`, `deadEnd`, `orphan` (entity with no page), listed in the PR comment; audiences precomputed from `access.view` and guards.

*Round 4 amendment (2026-09-18):*
Derive `relation` edges between `entity` nodes from `entities[].fields[].relation` (field grammar) labelled with the field id and `one|many`; self-relations render as loops; entity nodes with zero pages and zero relations are the `orphan` flag. Nodes carry `flags[]` from the page `flags` section when present.

**Interface contract**

* Provides: `FlowGraphSchema`, type `FlowGraph`, `buildFlowGraph(specs, app)`, `diffGraphs(a, b): GraphDiff`, `apps/web/src/generated/flow-graph.json`, node and edge types shared in `packages/collab/canvas/types.ts` (agreed with PAP-132 first).
* Consumers: PAP-132 canvas loader, PAP-124 Graph tab (neighbourhood query `subgraph(graph, pageId, depth)`), PAP-113 loader pattern, PAP-97 PR comment diff summary, PAP-138 search (page and entity index).
* Requires: PAP-114 and PAP-117 (hard), PAP-121 for external nodes (soft), PAP-82 thumbnails (soft), PAP-132 type agreement.

**Definition of done**

* Vitest: edge derivation per kind, reachability, flags, stable ids, layout determinism, diff output.
* Graph generated for the template examples and rendered in PAP-132 (screenshots at 1280 and 1920 px) or the temporary React Flow route.
* PR comment shows the diff summary on a seeded spec change.
* Docs; drift job in gate 1; changelog; Linear comment with screenshots.

**Test plan**

* Unit: fixtures for each derivation rule; cycle marks `back: true`; collapse counts; orphan and dead-end detection.
* Determinism: build twice, deep-equal; bench 300-page fixture under 5 s.
* Integration: `gen:graph --diff` between two fixture sets produces the expected summary.
* Visual: rendered graph at 1280 and 1920 px in both themes.

**Demo**

Add a transition from the invoices page to a new `invoice-detail` spec, run `pnpm spec gen:graph --diff`, read "1 node, 1 edge added", open the canvas and see the new page connected. One minute.

**Edge cases**

* Cyclic navigation: `back` edges styled differently.
* Fifty audiences on one page: ids only.
* `x-external` transition: external node labelled with the app id.
* Thousands of `reads` edges: collapsed with counts.
* Thumbnail expired: field omitted; canvas placeholder.

**Dependencies**

Blocked by PAP-114, PAP-117 and, per the current plan edge, PAP-132 (the canvas). In practice PAP-132 consumes this graph, so agree `packages/collab/canvas/types.ts` in the first day and ship the dev-route fallback; the audit recommends flipping that edge. Soft: PAP-121, PAP-82.

**Agent**

Built by Nova (Canvas Cartographer); reviewed by Quill for spec fidelity.

**Size**

M

*Round 4 critique fix (2026-09-18):* PAP-132 is named as a hard dependency above but stays a soft dependency (no `blocks` relation): milestone inversion 2026-09-29 > 2026-09-26. Start when it is In Review or work against its contract and leave a TODO naming it.
