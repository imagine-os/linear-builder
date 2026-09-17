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
blocks: ["PAP-132", "PAP-142"]
key: "collab/collab-research"
url: "https://linear.app/paperos/issue/PAP-127/evaluate-tldraw-vs-react-flow-for-the-canvas-and-tiptap-vs-blocknote"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-127: Evaluate tldraw vs React Flow for the canvas and Tiptap vs BlockNote for docs; write ADR

**Goal**

Choose the canvas library (tldraw vs React Flow) and the rich-text editor (Tiptap vs BlockNote) for PaperOS in one time-boxed session, with spikes that prove Yjs collaboration and our scale, and record the decision as an ADR. Everything in the collab project and the realtime text editor builds on this choice.

**Scope**

In:
- Rubric scoring per `libraries/eval-rubric` (license, maintenance, bundle size, a11y, TypeScript quality, agent-friendliness) plus collab-specific criteria: Yjs binding maturity, custom node/element API, programmatic layout, read-only and locked elements, touch and pen support, export to PNG/SVG, theming with our tokens.
- Candidates: canvas `tldraw` 3.x (note: the tldraw SDK license requires the "Made with tldraw" watermark or a paid business license, which must be scored against `libraries/license-policy`) vs `@xyflow/react` 12 (MIT); editor `@tiptap/core` 2.x or 3.x with `y-prosemirror` (MIT core, some Pro extensions paid) vs `@blocknote/core` (MPL-2.0, built on Tiptap and ProseMirror, ships Yjs collaboration and block UI).
- Spikes in `spikes/collab-research/` (throwaway, not shipped): (1) render the example flow graph shape from `spec-builder/spec-to-canvas` with 300 nodes and 600 edges, measure FPS while panning, test locked nodes, groups and custom node renderers; (2) two browser contexts editing the same document through a local Hocuspocus with presence, measure time to first render and bundle size (`vite-bundle-visualizer`), test mentions, code blocks, tables, image upload hook, and read-only rendering for comments.
- ADR `docs/adr/00NN-PAP-<n>-canvas-and-editor.md` (context, decision, alternatives table with scores, consequences, review date) registered through `collab/decision-log` format; registry entries in `libraries/registry` (adopted, rejected with reasons).
- Recommendation expected unless spikes disagree: React Flow for the canvas (node and edge model matches the spec graph, MIT, ELK-friendly) and Tiptap with `y-prosemirror` for the editor (thin, shared with comments), with BlockNote noted as a later option for documents.

Out: production integration (`collab/canvas-view`, `realtime/collab-text`), evaluating whiteboard products such as Excalidraw or Miro embedding (note them in alternatives only).

**Spec**

- Time box: one session, at most 60 turns and 4 hours wall clock; if spikes are inconclusive, decide on license and model fit and record the uncertainty.
- Scores 1 to 5 per criterion with one-sentence evidence and a link; totals weighted per the rubric weights.
- Bundle measurements taken from a production Vite build of each spike, gzip sizes recorded.
- Licence check run with the CI license checker from `libraries/license-policy` on both spike lockfiles.
- Findings summarised in the Linear comment in under 300 words with the decision on the first line.

**Definition of done**

- ADR merged with status `accepted`, scores table, spike links and a review date of 2027-01-01.
- Two spike repos or folders with README and measured numbers (FPS at 300 nodes, gzip size, time to first collaborative render).
- Registry updated for four libraries.
- Linear comment with decision, numbers and screenshots of both spikes at 1280.
- Follow-up issues adjusted: `collab/canvas-view` and `realtime/collab-text` titles reference the chosen libraries.

**Edge cases**

- tldraw license terms changed recently: quote the exact license text and version evaluated in the ADR.
- React Flow lacks freeform drawing for annotations: note the plan (sticky notes and shapes as custom nodes, pen via `input/pen` later).
- BlockNote pins a Tiptap version that conflicts with `realtime/collab-text` needs: record the peer dependency matrix.
- Both editors fail the a11y criterion on screen-reader navigation of tables: record as a known gap with a mitigation issue.
- Spike Hocuspocus not yet deployed (`realtime/yjs-server`): run it locally in Docker; note the difference.
- Team disagreement after the ADR: the ADR lists the criteria that would reopen it (license change, unmaintained for 6 months, blocking a11y bug).

**Dependencies**

None hard. Uses `libraries/eval-rubric` and `libraries/license-policy` if merged, otherwise the rubric from the plan. Unblocks `collab/canvas-view`, `realtime/collab-text`, `collab/comments` editor choice.

**Agent**

Built by Scout (Library Evaluator) with Nova (Canvas Cartographer) running spikes. Reviewed by Atlas (decision) and Sentinel (Security Auditor for license).

**Size**

S: one session, two spikes, one ADR.
