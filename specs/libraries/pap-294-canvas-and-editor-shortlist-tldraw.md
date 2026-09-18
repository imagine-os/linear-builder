---
identifier: "PAP-294"
title: "Canvas and editor shortlist: tldraw, React Flow, Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate, handed to collab research"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: "PAP-213"
children: []
blockedBy: ["PAP-209", "PAP-293"]
blocks: ["PAP-170", "PAP-621"]
key: "child/PAP-213/2"
url: "https://linear.app/paperos/issue/PAP-294/canvas-and-editor-shortlist-tldraw-react-flow-excalidraw-konva-tiptap"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:59.972Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-294: Canvas and editor shortlist: tldraw, React Flow, Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate, handed to collab research

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Research S

**Goal**

Produce a two-candidate shortlist per category for canvas and rich text, with facts and rubric pre-scores, and hand it to `collab/collab-research` (PAP-127) which owns the final decision, so no analysis is done twice. Time-box 2 hours.

**Scope**

In: facts via `scripts/lib-facts.ts` for eight libraries; pre-score on the rubric's facts-only criteria; license notes (tldraw `SEE LICENSE IN` watermark clause via PAP-211 tiers); one-paragraph rationale per exclusion; shortlist posted as a comment on PAP-127 and saved as `spikes/data-libs/shortlist.md`.

Out: spikes, ADRs, any decision.

**Spec**

* Shortlist format: `{ category, candidates: [{ id, version, license, preScore, why }], excluded: [{ id, why }] }` validated by the scorecard schema.
* tldraw's watermark and license and BlockNote's dependence on Tiptap called out explicitly.

**Interface contract**

Provides: `shortlist.md`, JSON in `results/shortlist.json`, comment on PAP-127. Consumes: PAP-209 facts collector and rubric, PAP-211 tiers. PAP-127 consumes the shortlist and must not re-collect facts.

**Definition of done**

* Shortlist committed and commented on PAP-127 within the time box.
* Every candidate has facts with checked-on dates and a license tier.

**Test plan**

* `pnpm lib score --facts-only` validates the JSON.
* Vitest lint asserts eight candidates and two per category in the shortlist.
* Reviewer check: Atlas confirms no overlap with PAP-127's scope.

**Demo**

Reviewer opens the comment on PAP-127 and reads two canvas and two editor candidates with license tier and pre-score, then opens `results/shortlist.json`. Under one minute.

**Edge cases**

* Facts collector rate-limited: cached facts with a warning.
* Library changed license recently (tldraw 2023): recorded in `why`.
* PAP-127 already merged: shortlist becomes a confirmation comment, no new work.

**Dependencies**

PAP-209 (hard; draft acceptable), PAP-211 (soft). Informs PAP-127, PAP-132, PAP-142.

**Agent**

Researched by Scout (Library Evaluator). Reviewed by Atlas.

**Size**

S
