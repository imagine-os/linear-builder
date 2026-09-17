---
key: "input/commands/palette-help-ui"
title: "Command palette and help sheet UI"
project: "input"
parent: "PAP-151"
phase: "P0"
type: "Build"
priority: 1
size: null
surfaces: ["Customer", "Staff"]
milestone: "Keyboard and command system"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
status: "pending"
---

# Command palette and help sheet UI

**Goal**

Give PAP-151 its face: a `CommandPalette` with fuzzy search, grouped and virtualised results, shortcut hints, recents and argument prompts, plus the `?` shortcuts sheet and a `CommandButton` that exposes any command with `aria-keyshortcuts`.

**Scope**

In:

* `CommandPalette` on PAP-70 `CommandBar` and PAP-237 `Dialog`: `fuse.js` 7 scoring over title and keywords, grouped by scope, at most 50 virtualised results, recents in `localStorage`, argument prompts from `argsSchema` (typed inputs and entity pickers via a `pickers` slot), opened with `mod+k`; full-screen sheet under `md`.
* Help sheet on `?` or `mod+/` listing active commands by scope with effective chords.
* `CommandButton commandId` and `ShortcutHint`.
* Storybook: empty, results, argument prompt, help sheet in three themes.

Out: registry (sibling 1), endpoint (sibling 3).

**Spec**

* `role="combobox"`, results `role="listbox"`, `aria-activedescendant`; results update under 16 ms for 2,000 commands.
* Palette stacks above an open Dialog and restores focus.

**Interface contract**

Exposes components above and `usePaletteProvider()` slot for PAP-138's search mode. Consumes registry `list(ctx)` and `execute` (sibling 1), `CommandBar`, `Dialog`, `Combobox` (PAP-70, PAP-237, PAP-238), effective chords via the resolver seam (PAP-153).

**Definition of done**

* Palette opens on every page; screenshots at 375 and 1280; Storybook stories axe clean; Linear comment.

**Test plan**

* Vitest: scorer ranking fixtures, grouping, recents persistence, argument prompt validation from Zod.
* Component: keyboard navigation, `aria-activedescendant` updates, focus restore after close, stacking over a Dialog.
* Playwright: `mod+k`, type, `Enter` executes at 375 (sheet) and 1280; `?` opens the sheet.
* Performance: 2,000-command filter under 16 ms.
* Visual: Gate 3 captures, three themes.

**Demo**

Press `mod+k`, type “theme”, run it; press `?` to browse shortcuts; run a command with an argument prompt and pick an entity. Under two minutes.

**Edge cases**

* No results: empty state with "Search everything" hint.
* Very long titles: truncated with tooltip.

**Dependencies**

Sibling 1, PAP-70 (hard). PAP-237, PAP-238, PAP-153 (soft).

**Agent**

Built by Nova with Iris on visuals. Reviewed by Sentinel (Visual Inspector).

**Size**

M: one complex component and a sheet.
