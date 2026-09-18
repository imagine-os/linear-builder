---
identifier: "PAP-630"
title: "Grid fill handle: drag to fill down or across a range with copy, series and pattern detection for numbers and dates"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-165"
children: []
blockedBy: ["PAP-342"]
blocks: ["PAP-135", "PAP-166", "PAP-172", "PAP-173", "PAP-183", "PAP-189", "PAP-332", "PAP-333", "PAP-334", "PAP-386", "PAP-617", "PAP-623", "PAP-689"]
key: "r4/tables/grid-fill-handle"
url: "https://linear.app/paperos/issue/PAP-630/grid-fill-handle-drag-to-fill-down-or-across-a-range-with-copy-series"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:19.571Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-28"
cycle: null
---

# PAP-630: Grid fill handle: drag to fill down or across a range with copy, series and pattern detection for numbers and dates

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Airtable's fill handle and every spreadsheet's drag-to-fill are how people set fifty cells in one gesture. Add the handle to the grid selection with copy and series modes, writing through the same chunked path as paste.

**Scope**

In: `views/grid/{FillHandle,fillSeries}.tsx`; handle on the selection's bottom-right corner; `computeFill(source: Cell[][], target: Range, mode)`; `mod+d` fill down command; touch handle at coarse pointer sizes.

Out: formula auto-fill (formula fields are computed), fill across grouped boundaries when groups differ (refused with a hint), auto-complete suggestions.

**Spec**

* Handle appears on a single cell or rectangular range selection (PAP-341 `{ anchor, focus }`); dragging vertically or horizontally previews the fill with a ghost range; release writes via PAP-342's chunked `records.update` with progress and cancel above 200 rows.
* Modes: `copy` (default for text, select, checkbox, relation) repeats the source pattern; `series` (default for `number`, `currency`, `date`, `autonumber`-like text with trailing digits) extends linear differences: `1, 2 → 3, 4`, `Jan 1, Jan 8 → Jan 15` (calendar arithmetic in the actor timezone), `Task 1 → Task 2`; `Alt` while dragging toggles the mode; a chip shows the active mode.
* Writes respect `validateRecord` per row; denied or invalid rows are skipped and reported in the progress toast; all writes carry reason `fill:<sessionId>` and register with the undo stack as one entry.
* Coarse pointer: handle is 24 px and drag uses the PAP-150 `usePointerSurface` with long-press to start; keyboard: `mod+d` fills the selection from its first row, `mod+r` fills right.
* Read-only and computed columns show no handle; frozen column boundary does not stop the drag.

**Interface contract**

Provides: `<FillHandle />`, `computeFill`, commands `grid.fillDown|fillRight`, `FillMode` type. Consumes: selection model and keyboard reducer (PAP-341), chunked writes and optimistic commit (PAP-342), field `parse|format` (PAP-338), pointer surface (PAP-150), undo manager (PAP-641, soft: falls back to the revert toast).

**Definition of done**

* Unit tests for series detection across types; Playwright drag and keyboard fills; screenshots at 1024 and 1920 plus a touch capture at 768; axe clean.
* `docs/views/grid.md` keyboard map updated; CHANGELOG; Linear comment.

**Test plan**

* Unit: series detection (numbers, dates across month ends and DST, trailing digits); copy pattern cycling; range clamping to visible columns; skipped-row accounting.
* Integration: fill 500 rows writes in chunks with one undo entry.
* E2E: select two dated cells in `/demo/grid`, drag the handle down twenty rows, see weekly dates, `Alt` to switch to copy, release, then `mod+z`.

**Demo**

Reviewer types 1 and 2 in Estimate, drags the handle down ten rows to get 3 to 12, then fills a status across a column with `mod+d`. Under two minutes.

**Edge cases**

* Source range contains mixed types across columns: each column fills independently.
* Drag past the last loaded row: prefetches pages, capped at 1,000 rows per drag with a hint.
* Currency series with mixed currencies: refused, copy mode offered.
* Row deleted mid-fill: skipped, counted.

**Dependencies**

PAP-342 (hard). Soft: PAP-150, PAP-641.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/undo-manager` = PAP-641.
