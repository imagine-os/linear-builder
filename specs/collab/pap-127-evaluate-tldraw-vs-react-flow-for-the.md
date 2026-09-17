---
identifier: "PAP-127"
title: "Evaluate tldraw vs React Flow for the canvas and Tiptap vs BlockNote for docs; write ADR"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Docs and prompt log stores"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-132", "PAP-142", "PAP-320"]
key: "collab/collab-research"
url: "https://linear.app/paperos/issue/PAP-127/evaluate-tldraw-vs-react-flow-for-the-canvas-and-tiptap-vs-blocknote"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:28.297Z"
---

# PAP-127: Evaluate tldraw vs React Flow for the canvas and Tiptap vs BlockNote for docs; write ADR

**Goal**

Choose the canvas library (tldraw vs React Flow) and the rich-text editor (Tiptap vs BlockNote) in one time-boxed session, prove the choice with two Yjs spikes at our scale, and record it as an ADR. PAP-132 (canvas), PAP-142 (editor) and PAP-131 (comments composer) build on this decision.

**Scope**

In:

* Rubric scoring per PAP-209 plus collab criteria: Yjs binding maturity, custom node API, programmatic layout, locked elements, touch and pen, PNG/SVG export, theming with tokens.
* Candidates: canvas `tldraw` 3.x (watermark or paid business license, scored against PAP-211) vs `@xyflow/react` 12 (MIT); editor `@tiptap/core` 3.x with `y-prosemirror` (MIT core) vs `@blocknote/core` (MPL-2.0, built on Tiptap).
* Spikes in `spikes/collab-research/` (throwaway): (1) render the `FlowGraph` fixture from PAP-123 with 300 nodes and 600 edges, measure FPS while panning, test locked nodes, groups and custom renderers; (2) two browser contexts editing one document through a local Hocuspocus container, measure time to first collaborative render and gzip bundle size, test mentions, code blocks, tables, image upload hook and read-only rendering.
* ADR `docs/adr/00NN-PAP-127-canvas-and-editor.md` in the PAP-130 format; registry entries in PAP-216 for four libraries.

Out: production integration, whiteboard products (Excalidraw, Miro) beyond a line in alternatives.

**Spec**

* Time box: one session, at most 60 turns and 4 hours; if spikes are inconclusive, decide on license and model fit and record the uncertainty.
* Scores 1 to 5 per criterion with one-sentence evidence and a link; totals weighted per rubric weights. Bundle sizes from a production Vite build, gzip. License check with the PAP-211 CI checker on both spike lockfiles.
* Expected outcome unless spikes disagree: React Flow for the canvas (node and edge model matches the spec graph, MIT, ELK-friendly) and Tiptap with `y-prosemirror` for the editor, BlockNote noted as a later document option.
* Linear comment under 300 words with the decision on the first line.

**Interface contract**

Exposes: ADR file with frontmatter `status: accepted`, `issue: PAP-127`, `reviewDate: 2027-01-01`; `spikes/collab-research/results.json` `{ canvas: { lib, fps300, gzipKb }, editor: { lib, ttfcrMs, gzipKb } }`; four registry rows (`adopted` or `rejected`). Downstream issues read the ADR's `decision` block: PAP-132 imports the chosen canvas package, PAP-142 the editor package; PAP-127 also fixes the peer-dependency matrix (`yjs`, `y-prosemirror`, `@tiptap/*` versions) that PAP-140 and PAP-142 pin. Consumes: PAP-209 rubric weights, PAP-211 checker, PAP-123 graph fixture shape (use the example JSON in the plan if PAP-123 is unmerged).

**Definition of done**

* ADR merged, status `accepted`, scores table, spike links, reopen criteria.
* Two spike folders with README and measured numbers (FPS at 300 nodes, gzip size, time to first collaborative render).
* Registry updated for four libraries; peer-dependency matrix recorded.
* Linear comment with decision, numbers and 1280 px screenshots of both spikes.
* PAP-132 and PAP-142 titles updated to name the chosen libraries.

**Test plan**

* Unit: none shipped; each spike has a `pnpm bench` script that reprints the ADR numbers.
* Integration: spike 2 runs against `docker compose up hocuspocus` and asserts two clients converge on the same text (Playwright, two contexts).
* Visual: screenshots of both spikes at 1280 px in light and dark attached to the comment; no baselines kept.
* Review check: Sentinel reruns the license checker on the lockfiles and confirms the ADR quotes the exact tldraw license text and version.

**Demo**

Open the ADR, read the first line of the decision. Run `pnpm --filter spike-canvas bench` and see FPS at 300 nodes printed; run `pnpm --filter spike-editor dev`, open two tabs, type in one and watch the other. Under two minutes.

**Edge cases**

* tldraw license terms changed recently: quote text and version evaluated.
* React Flow lacks freehand drawing: note the plan (sticky notes and shapes as custom nodes, ink via PAP-157).
* BlockNote pins a Tiptap version that conflicts with PAP-142 needs: record the peer matrix.
* Both editors fail screen-reader table navigation: record as a known gap with a mitigation issue.
* Hocuspocus (PAP-140) not deployed: run it locally in Docker and note the difference.

**Dependencies**

None hard (Ready). Uses PAP-209 and PAP-211 if merged, else the rubric from the plan. Blocks PAP-132, PAP-142; informs PAP-131.

**Agent**

Built by Scout (Library Evaluator) with Nova (Canvas Cartographer) running spikes. Reviewed by Atlas (decision) and Sentinel (Security Auditor for license).

**Size**

S: one session, two spikes, one ADR.
