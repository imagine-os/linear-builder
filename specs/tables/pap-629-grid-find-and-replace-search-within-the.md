---
identifier: "PAP-629"
title: "Grid find and replace: search within the current view, match navigation, per-type replace with preview and batch write"
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
blockedBy: ["PAP-71", "PAP-151", "PAP-163", "PAP-164", "PAP-291", "PAP-337", "PAP-340", "PAP-342", "PAP-613", "PAP-656"]
blocks: []
key: "r4/tables/grid-find-and-replace"
url: "https://linear.app/paperos/issue/PAP-629/grid-find-and-replace-search-within-the-current-view-match-navigation"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:19.438Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-28"
cycle: null
---

# PAP-629: Grid find and replace: search within the current view, match navigation, per-type replace with preview and batch write

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Airtable and every spreadsheet let a user press `mod+f` inside the grid, step through matching cells and replace text in bulk. The toolbar `SearchBox` filters rows; this adds in-place find with match highlighting and a replace flow that previews before writing.

**Scope**

In: `views/grid/{FindReplaceBar,useFindMatches}.tsx`; commands `grid.find`, `grid.findNext|findPrev`, `grid.replace`; server-side match count via `views.count` with a `contains` filter across text-like fields; batch write through `records.update` in chunks of 200 (PAP-342 chunking).

Out: regex replace (option flagged `deferred`), replace across datasets, find in non-grid kinds (they use the toolbar search).

**Spec**

* `mod+f` inside a focused grid opens the bar (browser find stays on `mod+shift+f`, documented in the `?` sheet); typing highlights matches in loaded rows (`mark` elements, case-insensitive, diacritics-folded with `Intl.Collator`); Enter and Shift+Enter move focus to the next or previous match, scrolling virtualised rows into view.
* Field scope: all visible `text|longText|email|url|phone|select|multiSelect` columns by default, narrowable to one column from the column menu; matches in select options match by option name.
* Replace: input plus "Replace" and "Replace all (n)"; preview lists up to 20 before and after values; writes go through `records.update` with `expectedVersion`; conflicts skipped and reported; every write is one audit row with reason `find-replace:<sessionId>`.
* Counts beyond loaded rows come from `views.count` with a `contains` condition so the bar says "12 of 3,204 matches, 40 loaded"; "Replace all" above 200 rows runs as a PAP-334-style batch with progress and an undo toast.
* Read-only users get find without replace; commands are `agentCallable: false`.

**Interface contract**

Provides: `<FindReplaceBar />`, `useFindMatches`, commands above, `foldForSearch(text)` helper reused by the toolbar `SearchBox`. Consumes: editing and chunked writes (PAP-342), `records.update` (PAP-613), `views.count` (PAP-337), selection and keyboard reducer (PAP-341), undo toast (PAP-334, soft), commands (PAP-151).

**Definition of done**

* Playwright flows green; unit tests for folding and match navigation; screenshots of the bar at 375, 1024, 1920; axe clean (matches announced as "match 3 of 12").
* Keyboard map in `docs/views/grid.md` updated; CHANGELOG; Linear comment.

**Test plan**

* Unit: diacritic folding; match ordering across columns and virtual rows; replace preview construction; conflict skipping.
* Integration: replace across 1,000 rows writes exactly the matching rows and one audit row each.
* E2E: press `mod+f` in `/demo/grid`, type a client name, step through matches, replace all in one column, undo from the toast.

**Demo**

Reviewer finds "Acme" across the demo grid, steps through three matches, replaces with "Acme Corp" in the Client column and undoes it. Under two minutes.

**Edge cases**

* Match inside a collapsed group: group expands on navigation.
* Row deleted between preview and replace: skipped and counted.
* Formula and computed columns: matched, never replaced (greyed).
* Empty search string: bar shows count 0, replace disabled.

**Dependencies**

PAP-342 (hard), PAP-613 (hard). Soft: PAP-334, PAP-151.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/records-crud-procedures` = PAP-613.
