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
children: []
blockedBy: ["PAP-150", "PAP-238", "PAP-67"]
blocks: ["PAP-153", "PAP-159", "PAP-165"]
key: "input/command-registry"
url: "https://linear.app/paperos/issue/PAP-151/build-the-global-command-registry-with-keyboard-shortcuts-command"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-151: Build the global command registry with keyboard shortcuts, command palette and per-page scoping

**Goal**

Make everything in a PaperOS app a command: a single registry knows every action, its label, shortcut, scope and permission, and powers keyboard shortcuts, the command palette, menus, toolbars, voice and gamepad. Discoverability comes for free (the palette lists what you can do here), and agents can invoke the same commands programmatically.

**Scope**

In:
- `packages/input/src/commands/`: `defineCommand({ id, title, description?, icon?, keywords?, scope: 'global'|'page'|'component', shortcut?: Chord | Chord[], when?: (ctx) => boolean, permission?: string, run: (ctx, args?) => void|Promise, argsSchema?: Zod })`, `CommandRegistry` with `register/unregister/execute/list(ctx)`, and React hooks `useCommand(def)` (registers for the component's lifetime), `useCommands(scopeId)`, `useShortcut(chord, handler)`.
- Scoping: scope stack (`global` → page route id → focused component scope) managed by `CommandScopeProvider`; the innermost matching command wins; page specs declare `commands:` (`spec-builder/schema`) and `spec-builder/layout-codegen` registers them.
- Keyboard: chord parser and matcher using the `mod+shift+k` format from `input/input-abstraction`, sequences (`g i`, 1 s timeout), platform display (`⌘⇧K` vs `Ctrl+Shift+K`), conflict detection with a dev-time warning, and a `when` guard (e.g. not inside editable text unless `allowInInput`).
- Command palette: `CommandPalette` built on `design-system/layout-components` `CommandBar`, fuzzy search (`fuse.js` 7.x, or `cmdk`'s scorer), grouped by scope, shows shortcut hints, recent commands (local), argument prompts for commands with `argsSchema` (simple typed inputs, entity pickers via a `pickers` slot), opened with `mod+k`.
- Shortcut help sheet (`?` or `mod+/`) listing active commands grouped by scope.
- Agent access: `POST /api/commands/execute` (oRPC) for agent principals with scope `commands:execute`, limited to commands flagged `agentCallable: true`; results audited.

Out: custom keymaps (`input/keymaps`), voice (`input/voice`), menus rendering (primitives), gamepad mapping (`input/gamepad`).

**Spec**

- IDs are dot-namespaced (`nav.goToInbox`, `record.duplicate`, `editor.bold`); a Vitest test fails on duplicate IDs across the registry at build time via a generated `commands.manifest.json` (`pnpm commands:manifest`) that also feeds docs and `input/keymaps`.
- `when` receives `{ route, selection, focusedScope, permissions, capabilities, isEditing }`; `permission` is checked with `packages/permissions` `can()` and hidden commands never appear in the palette.
- Execution telemetry: `command.executed { id, source: 'keyboard'|'palette'|'menu'|'voice'|'gamepad'|'api' }` to `data-layer/observability`; failures toast with the error and are logged.
- Palette renders at most 50 results, virtualised; results update under 16 ms for 2,000 commands (benchmark test).
- Accessibility: palette input `role="combobox"`, results `role="listbox"`, `aria-activedescendant`; help sheet is a Dialog; shortcuts announced via `aria-keyshortcuts` on buttons that expose a command (`<CommandButton commandId />`).
- Default global commands shipped: `nav.*` for spec-declared navigation, `ui.toggleSidebar`, `ui.toggleInspector`, `ui.toggleTheme`, `edit.undo/redo`, `help.shortcuts`, `search.open`.

**Definition of done**

- Palette opens with `mod+k` on every page, lists page-scoped commands from a sample spec, executes with keyboard only; Playwright tests at 375 (full-screen sheet) and 1280 px, screenshots attached.
- Vitest tests: chord parsing (incl. sequences, macOS/Linux), scope precedence, `when` guards, duplicate-ID detection, permission hiding.
- Manifest generated in CI and committed; docs page lists all commands from it.
- Agent execution endpoint tested with an agent key (allowed and denied cases) and audit rows.
- Storybook stories for palette (empty, results, argument prompt) in three themes, axe clean.
- Changelog entry and Linear comment with demo link.

**Edge cases**

- Shortcut typed while focus is in a Tiptap editor: only `allowInInput` commands fire; `mod+b` goes to the editor.
- Two components register the same chord in sibling scopes: focused one wins; unfocused registrations are inert.
- Browser-reserved chords (`mod+w`, `mod+t`): warn at registration; never claim them.
- Non-Latin keyboard layouts: match on `event.code` for letters, `event.key` for symbols; document the trade-off.
- Palette opened while a Dialog is open: stacks above it and returns focus correctly.
- Command `run` throws asynchronously: palette closes, toast shows, error logged; registry stays healthy.

**Dependencies**

- `design-system/primitives` and `design-system/layout-components` (CommandBar, Dialog), `input/input-abstraction` (chord format), `identity/rbac-abac` (`can()`), `data-layer/api-layer` (execute endpoint), `spec-builder/schema` (`commands:` section, may land after; registry works without it).

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer, Security Auditor for the agent endpoint); Iris reviews palette visuals.

**Size**

L: it is the hub for keyboard, palette, voice and gamepad, and must be right before others build on it.
