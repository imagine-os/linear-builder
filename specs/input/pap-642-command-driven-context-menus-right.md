---
identifier: "PAP-642"
title: "Command-driven context menus: right-click, long-press and the ContextMenu key render scoped commands for records, cells, cards, nodes and selections"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-237", "PAP-289"]
blocks: ["PAP-132", "PAP-167", "PAP-343"]
key: "r4/input/command-context-menus"
url: "https://linear.app/paperos/issue/PAP-642/command-driven-context-menus-right-click-long-press-and-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:35.317Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-23"
cycle: null
---

# PAP-642: Command-driven context menus: right-click, long-press and the ContextMenu key render scoped commands for records, cells, cards, nodes and selections

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Linear, Figma and VS Code show the same actions in the palette, the shortcut sheet and the right-click menu because all three read one registry. PAP-237 ships a `Menu` with a context trigger and PAP-154 suppresses the native long-press menu, but nothing turns registered commands into a context menu for a target. Build that bridge once so grids, boards, canvas and lists never hand-write menus.

**Scope**

In: `packages/input/src/commands/{ContextMenu,useContextTarget}.tsx`; `defineCommand` extension `menu?: { group, order, showIn: ['context','toolbar','palette'] }`; `<CommandContextMenu scope target />`; `useContextTarget(ref, { kind, id, selection })`; keyboard opener (`ContextMenu` key, `Shift+F10`); touch long-press via PAP-154 `useLongPress`.

Out: menu rendering primitives (PAP-237), toolbar rendering (view toolbar issue), the palette (PAP-290).

**Spec**

* Right-click, long-press (500 ms, coarse pointer) or `Shift+F10` on an element with `useContextTarget` opens `Menu` at the pointer (or anchored to the element for keyboard) listing `registry.list(ctx)` filtered to `menu.showIn` containing `context`, grouped by `menu.group` with separators, ordered by `menu.order`, with `ShortcutHint` from the effective keymap (PAP-153 seam).
* `ctx.target = { kind: 'record'|'cell'|'card'|'node'|'row'|'selection', id, datasetRef?, fieldId?, count }` so `when(ctx)` guards can hide "Delete" for read-only rows and pluralise labels ("Delete 3 records").
* Native menu preserved when no command matches or when the target is a link or editable text without `allowInInput` commands; `preventDefault` only when the menu opens.
* Focus returns to the target on close; `Escape` closes; submenus for `menu.group` with more than eight items; `agentCallable` unaffected.
* Stories: grid cell, kanban card, canvas node targets in three themes; performance under 8 ms to open with 300 registered commands.

**Interface contract**

Provides: `<CommandContextMenu />`, `useContextTarget`, `menu` extension on `CommandDef`, `ContextTarget` type (exported in `contract-input`). Consumes: registry `list|execute` and scopes (PAP-289), `Menu` (PAP-237), `useLongPress` (PAP-154, soft: pointer fallback), effective chords (PAP-153, soft), `LiveAnnouncer` (PAP-152). Consumed by PAP-343 column and row menus, PAP-167 cards, PAP-132 canvas nodes, gallery and list rows.

**Definition of done**

* Menus open on the three sample targets by mouse, touch emulation and keyboard; screenshots at 375 and 1280 in three themes; axe clean; changelog; docs section in `docs/platform/input/commands.md`; Linear comment on PAP-343 and PAP-167.

**Test plan**

* Unit: filtering by `showIn` and `when`; grouping and ordering; pluralised labels from `count`; native fallback decision table.
* Component: open by right-click and `Shift+F10`, focus restore, submenu keyboard navigation.
* E2E: right-click a row in `/demo/grid`, run Duplicate; long-press a kanban card on a touch context; `Shift+F10` on a focused cell; a viewer session sees no Delete.

**Demo**

Reviewer right-clicks a grid row, reads the same commands as `mod+k` shows with shortcuts, long-presses a card on the phone viewport and opens the same menu by keyboard. Under two minutes.

**Edge cases**

* Right-click during a drag: ignored.
* Target unmounts while open: menu closes, focus to region entry (PAP-152).
* RTL: submenu opens to the left.
* Multi-select of mixed kinds: only commands valid for all targets.

**Dependencies**

PAP-289 (hard), PAP-237 (hard). Soft: PAP-154, PAP-153, PAP-152. Blocks PAP-343, PAP-167, PAP-132 (they consume instead of hand-writing menus).

**Agent**

Builder: Nova (Product Systems Engineer). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.
