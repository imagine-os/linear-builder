---
identifier: "PAP-731"
title: "Canvas diff mode and embeds: highlight graph changes between two spec hashes, `<FlowGraphEmbed>` for docs and record pages, thumbnail job"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-123", "PAP-322"]
blocks: []
key: "r4/collab/canvas-diff-embeds"
url: "https://linear.app/paperos/issue/PAP-731/canvas-diff-mode-and-embeds-highlight-graph-changes-between-two-spec"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:20.058Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-731: Canvas diff mode and embeds: highlight graph changes between two spec hashes, `<FlowGraphEmbed>` for docs and record pages, thumbnail job

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

PAP-123 already computes `diffGraphs()` and PAP-322 makes the canvas usable, but nobody can see what a PR changed in the UX flow, and the map lives only at `/_app/dev/canvas`. Add a diff mode fed by two spec hashes or git refs, and an embeddable read-only subgraph for docs pages, record detail pages and the release digest.

**Scope**

In: `packages/collab/canvas/diff/` with `DiffLayer` (added green, removed red dashed, changed amber, unchanged dimmed) and a toolbar toggle `Compare with: main | last release | <ref>`; oRPC `canvas.graph.diff({ appId, from, to })` reading `flow-graph.json` at two git refs through the Forgejo client; MDX and React `<FlowGraphEmbed pageId depth={1} />` rendering `subgraph()` read-only with an 'open in canvas' link; job `canvas.thumbnails` rendering PNG per page node with `html-to-image` in headless Chromium for docs and Linear comments. Out: editing in embeds, freehand (PAP-157), org chart (PAP-113).

**Spec**

* Diff input is two `FlowGraph` documents; node identity by stable id; changed = label, route, audiences or edge set differs; summary chips (`+3 nodes, -1 edge, 2 changed`) match PAP-123's `GraphDiff` output byte for byte.
* `?compare=<ref>` deep link (extends PAP-322's URL state); Gate 3 captures the diff view for PRs touching `specs/` and PAP-97 links it in the status comment.
* Embed renders without Yjs (no overlay), fits to 320 px minimum, lazy loads `@xyflow/react`; maximum 40 nodes, otherwise 'too many to embed' with a link.
* Thumbnails 480x300, regenerated when `specHash` changes, stored through PAP-37 with a `thumbnail` field written back into `flow-graph.json` meta for PAP-320's `PageNode`.
* Docs pages can pin an embed with `<FlowGraphEmbed pageId="customer-invoices" />`; record detail pages (PAP-361) get one under the header when the entity has a page node.

**Interface contract**

Provides: `canvas.graph.diff`, `DiffLayer`, `<FlowGraphEmbed>` (React and MDX), job `canvas.thumbnails`, `?compare=` param. Consumes: `diffGraphs`, `subgraph`, `FlowGraph` (PAP-123), `PaperCanvas` read-only and node types (PAP-320, PAP-322), Forgejo client (PAP-276, soft), files (PAP-37), jobs (PAP-43), `renderMdx` component registration (PAP-128). Consumed by: PAP-97 status comment, PAP-89 digest, PAP-361 detail pages, PAP-125 docs.

**Definition of done**

* Diff between two fixture graphs renders the three colours and the summary chips; embed renders inside a docs page and a record page at 375 and 1280; thumbnails appear on `PageNode`.
* Screenshots in light and dark; axe clean; `docs/collab/canvas.md` gains Diff and Embeds sections; CHANGELOG entry.

**Test plan**

* Unit: diff classification per change kind, embed node cap, thumbnail invalidation on hash change.
* Integration: `canvas.graph.diff` against a fixture repo with two commits through a mocked Forgejo API.
* E2E (Playwright): toggle compare, assert coloured nodes and chips; open a doc with an embed and click through to the canvas.

**Demo**

Open the canvas, choose Compare with main on a branch that adds a page, see the green node and the chip, then open the invoices doc and see the embedded neighbourhood. Under two minutes.

**Edge cases**

* Ref without a generated graph: server builds it on the fly with `buildFlowGraph` (under 5 s) or returns 409 with a hint.
* Node renamed (id changed): shows as removed plus added; a `--rename-hint` from PAP-123 marks it when routes match.
* Embed on a page with no node: renders nothing and logs once in dev.

**Dependencies**

Hard: PAP-322, PAP-123. Soft: PAP-276, PAP-37, PAP-43, PAP-97, PAP-361.

**Agent**

Builder: Nova (Canvas Cartographer). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
