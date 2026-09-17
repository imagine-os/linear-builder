---
identifier: "PAP-292"
title: "Table library spike and ADR: TanStack Table plus Virtual, AG Grid Community, Glide Data Grid and react-data-grid at 100k rows"
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
blockedBy: ["PAP-209"]
blocks: ["PAP-293"]
key: "child/PAP-213/0"
url: "https://linear.app/paperos/issue/PAP-292/table-library-spike-and-adr-tanstack-table-plus-virtual-ag-grid"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:18.297Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-292: Table library spike and ADR: TanStack Table plus Virtual, AG Grid Community, Glide Data Grid and react-data-grid at 100k rows

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Research M

**Goal**

Choose the grid library the views engine renders with by building the same 100k-row grid in four candidates and scoring them with the shared rubric plus table-specific extras, then record the ADR so `tables/grid-view` builds without re-litigating. Time-box 4 hours; if unmerged by 2026-09-21, PAP-165 proceeds with TanStack Table v8 and this ADR confirms or reverses it.

**Scope**

In: `spikes/data-libs/tables/` Vite routes per candidate with inline edit, column resize, frozen columns, grouping and 100k rows over TanStack Virtual where headless; Playwright scroll traces; axe; bundle sizes; scorecards with extras (headless vs rendered, virtualization at 100k, editing hooks, pinning, grouping primitives, server-side pagination hooks for PAP-163, `role=grid` semantics per PAP-152, dnd-kit compatibility, touch); ADR `docs/adr/NNNN-PAP-213-table-library.md`; registry drafts. Handsontable rejected on license.

Out: charts, maps, canvas and editor (siblings).

**Spec**

* Reference profile: Playwright on the CI runner with CPU throttling 4x; FPS from the trace's frame timings.
* AG Grid Community gaps versus Enterprise (row grouping) recorded explicitly.
* Glide's canvas rendering scored down on a11y and testability with the vision-agent dependency noted.

**Interface contract**

Provides: ADR with winner, fallback and migration hours, `results/tables.json`, registry entries, a comment on PAP-165 and PAP-163 with exact package and version. Consumes: PAP-209 rubric and `pnpm lib score`, PAP-66 tokens (soft), PAP-162 parity audit findings (cross-link, no repetition).

**Definition of done**

* Four routes merged under `spikes/` with results JSON and generated comparison table.
* Winner shows 100k rows at 55+ FPS scroll in a committed trace; screenshots at 375, 1024, 1920 in light and dark.
* ADR accepted with Nova and Atlas approval comments; PAP-165 description updated.

**Test plan**

* Playwright per route: scroll trace, inline edit, resize, pin, group; axe scan; screenshot at three widths and two themes.
* `pnpm lib score` validates every scorecard (evidence URLs required).
* Bundle: `vite build --mode analyze` per route committed.

**Demo**

Reviewer opens the ADR, reads the comparison table, then runs `pnpm spike tables --lib tanstack` and scrolls a 100k-row grid while editing a cell. Under two minutes.

**Edge cases**

* Candidate cannot virtualize columns: note for the 200-column importer case.
* TanStack Table v9 alpha: evaluate v8 stable, note the timeline.
* Tie within 5 points: migration-cost rule, no re-scoring.

**Dependencies**

PAP-209 (hard; use draft if unmerged), PAP-162 (cross-link). Informs PAP-165, PAP-163; PAP-165 defaults to TanStack if this is late.

**Agent**

Researched by Scout (Library Evaluator) paired with Nova (Views Engineer). Reviewed by Nova and Atlas.

**Size**

M
