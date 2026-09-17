---
identifier: "PAP-151"
title: "Build the global command registry with keyboard shortcuts, command palette and per-page scoping"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: null
children: ["PAP-289", "PAP-290", "PAP-291"]
blockedBy: ["PAP-67", "PAP-150", "PAP-238"]
blocks: ["PAP-153", "PAP-159", "PAP-165", "PAP-341"]
key: "input/command-registry"
url: "https://linear.app/paperos/issue/PAP-151/build-the-global-command-registry-with-keyboard-shortcuts-command"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:03:42.162Z"
---

# PAP-151: Build the global command registry with keyboard shortcuts, command palette and per-page scoping

**Goal**

Umbrella: make everything in a PaperOS app a command. One registry knows every action, its label, shortcut, scope and permission, and powers shortcuts, the palette, menus, toolbars, voice and gamepad; agents invoke the same commands through an audited endpoint. Planned as three work packages; the umbrella owns the manifest, docs and integration test.

**Scope**

Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Command registry core, scoping and chord matcher** — `defineCommand`, `CommandRegistry`, `CommandScopeProvider` scope stack (global → page → component), chord and sequence matching on PAP-150's `Chord`, `when` guards, conflict warnings, `pnpm commands:manifest` with duplicate-ID failure.
2. **Command palette and help sheet UI** — `CommandPalette` on PAP-70 `CommandBar` with `fuse.js` scoring, grouped results, virtualised list (max 50), argument prompts from `argsSchema`, recents; `?` help sheet; `CommandButton`.
3. **Agent execution endpoint, telemetry and default commands** — oRPC `commands.execute` for `commands:execute` scope limited to `agentCallable` commands with `can()` and audit rows; `command.executed` telemetry; defaults `nav.*`, `ui.toggleSidebar|toggleInspector|toggleTheme`, `edit.undo|redo`, `help.shortcuts`, `search.open`.

Parent owns `docs/platform/input/commands.md` generated from the manifest, Storybook stories, integration test.

Out: keymaps (PAP-153), voice (PAP-159), gamepad mapping (PAP-158), menu rendering.

**Spec**

* IDs dot-namespaced (`record.duplicate`); innermost scope wins; page specs declare `commands:` (PAP-114) registered by PAP-120.
* `when(ctx)` receives `{ route, selection, focusedScope, permissions, capabilities, isEditing }`; hidden commands never appear.
* Palette `role="combobox"` with `aria-activedescendant`; results update under 16 ms for 2,000 commands.
* Browser-reserved chords warned and never claimed; `allowInInput` gates firing inside editable text.

**Interface contract**

Exposes (owned by the work packages): `defineCommand({ id, title, description?, icon?, keywords?, scope, shortcut?, when?, permission?, argsSchema?, agentCallable?, voice?, run })`, `CommandRegistry { register, unregister, execute(id, args, source), list(ctx), setBindingsResolver(fn) }` (resolver hook for PAP-153), hooks `useCommand`, `useCommands`, `useShortcut`, components `CommandPalette`, `CommandButton`, `ShortcutHint`, `commands.manifest.json` `{ commands: [{ id, title, scope, shortcut, keywords, permission, agentCallable, page? }] }` consumed by PAP-153, PAP-159 and docs; oRPC `commands.execute({ id, args }) -> { ok, result | error }`; telemetry event `command.executed { id, source }`. Consumes: `Chord` utilities and modality (PAP-150), `CommandBar`, `Dialog`, `Combobox` (PAP-70, PAP-237, PAP-238), `can()` (PAP-227), oRPC and audit (PAP-267, PAP-38), spec `commands:` section (PAP-114).

**Definition of done**

* All three work packages merged; palette opens with `mod+k` on every page and lists page-scoped commands from a sample spec.
* Manifest generated in CI and committed; docs page lists every command from it.
* Storybook palette stories (empty, results, argument prompt) in three themes, axe clean; changelog; Linear comment with demo link.

**Test plan**

* Integration (parent): Playwright at 375 (full-screen sheet) and 1280: `mod+k`, type "inbox", `Enter` navigates; `g i` sequence navigates; inside a Tiptap field `mod+b` bolds instead of firing a global command; a customer session does not see a staff-only command; agent key executes an `agentCallable` command and is denied on a non-callable one with an audit row.
* Unit tests per work package (chord parsing, scope precedence, `when` guards, duplicate IDs, permission hiding, scorer ranking, endpoint allow/deny).
* Performance: bench with 2,000 registered commands, palette filter under 16 ms.
* Visual: Gate 3 captures of palette and help sheet at 375 and 1280, three themes.

**Demo**

Press `mod+k`, type “theme”, run “Toggle theme”; press `?` to read the shortcuts sheet; press `g i` to jump to the inbox; from a terminal call `commands.execute` with an agent key and watch the audit row appear. Under two minutes.

**Edge cases**

* Same chord in sibling scopes: focused one wins.
* Palette over an open Dialog: stacks and restores focus.
* Async `run` throws: palette closes, toast, registry healthy.
* Non-Latin layouts: letters by `code`, symbols by `key`.

**Dependencies**

PAP-67, PAP-150 (hard, encoded). Soft: PAP-70, PAP-59, PAP-35, PAP-114. Blocks PAP-153, PAP-159, PAP-155; consumed by PAP-142, PAP-138, PAP-152, PAP-158, PAP-149.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer, Security Auditor for the endpoint); Iris reviews palette visuals.

**Size**

L, planned as three M/S work packages (child issues pending the issue limit).
