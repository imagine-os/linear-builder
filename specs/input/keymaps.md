---
identifier: "PAP-153"
title: "Support user-customizable keymaps with presets (default, Vim-style, Linear-like) synced per user"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-151"]
blocks: []
key: "input/keymaps"
url: "https://linear.app/paperos/issue/PAP-153/support-user-customizable-keymaps-with-presets-default-vim-style"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-153: Support user-customizable keymaps with presets (default, Vim-style, Linear-like) synced per user

**Goal**

Let power users bring their habits: choose a keymap preset (Default, Vim-style, Linear-like), rebind any command, and have those bindings follow them to every device and window. Keymaps are a layer over the command registry, so no command changes and conflicts are detected before they bite.

**Scope**

In:
- `packages/input/src/keymaps/`: `Keymap = { id, name, base?: presetId, bindings: Record<commandId, Chord[] | null> }`; resolver merges preset → user overrides → page-scope overrides and feeds the registry's matcher (`input/command-registry` exposes `setBindingsResolver`).
- Presets shipped in `presets/`: `default` (registry defaults), `vim` (`j/k` list navigation, `g g`/`G`, `/` search, `:` palette, `h/l` collapse/expand, Escape semantics), `linear` (`c` create, `e` edit, `x` select, `s` status, `a` assign, `g i` inbox, `g b` board), documented with a comparison table.
- Settings UI at `/settings/keyboard`: preset picker, searchable command list with current chords, click-to-record binding (captures next chord, shows conflicts inline, allows two chords per command), reset per command and per keymap, import/export JSON.
- Persistence: `user_preferences.keymap jsonb` via `identity/better-auth` user attributes (or `data-layer/core-entities` `user` extension), synced across devices through `realtime/record-sync` and across windows through `realtime/multi-window-sync`; local cache in `localStorage` for first paint.
- Conflict detection: same chord bound to two commands in overlapping scopes is flagged; browser-reserved chords blocked; a `when`-guard explanation shown ("only when a row is selected").

Out: per-tenant keymaps, macros, mouse-button bindings, remapping inside Tiptap beyond registry commands.

**Spec**

- Resolver output is memoised per scope stack; rebinding updates in under one frame; `input/command-registry` help sheet and palette hints read effective chords from the resolver, never from `defineCommand` defaults.
- Vim preset implements a tiny modal layer: `normal` (default in lists and read views) and `insert` (any editable focused); `Escape` returns to normal without blurring; mode shown in the status bar when the vim preset is active.
- Recording UI uses `input/input-abstraction` key normalisation; ignores lone modifiers; supports sequences by pausing 1 s.
- Export format is the `Keymap` JSON, validated by Zod on import; unknown command IDs are kept but greyed out ("not available in this app").
- Manifest-driven: the settings list is built from `commands.manifest.json` so every app's commands appear automatically; page-scoped commands are grouped by page title from the spec.
- Copy in `packages/input/src/copy/keymaps.ts`; all controls from `design-system/primitives`.

**Definition of done**

- Switching to the Linear preset makes `c` open create on a sample list page and `g i` navigate; Playwright tests for all three presets on key flows at 768 and 1440 px, screenshots of the settings page.
- Vitest tests: merge precedence, conflict detection, import validation, vim mode transitions.
- Preference persists across reload and to a second browser within 2 s (sync test).
- Storybook story of the settings page (empty search, conflict state, recording state) in three themes; axe clean.
- Docs `docs/platform/input/keymaps.md` with the preset comparison table.
- Changelog entry and Linear comment with demo link.

**Edge cases**

- User rebinds `mod+k` away from the palette: allow, but require a replacement binding for `palette.open` before saving.
- Chord uses a key missing on the current layout (`§`): shows a warning and still stores it.
- Preset updated in a later release adds a binding that conflicts with a user override: user override wins; changelog notes it.
- Vim normal mode and a customer-facing page with text-heavy forms: vim layer only applies where `role` is list, grid or tree; forms stay insert.
- Import file from another app with 40 unknown commands: imports the rest, lists unknowns.
- Two windows change bindings simultaneously: last write wins; both windows re-resolve on the sync event.

**Dependencies**

- `input/command-registry` (resolver hook, manifest), `input/input-abstraction` (key normalisation), `identity/better-auth` or `data-layer/core-entities` (preference storage), `realtime/record-sync` and `realtime/multi-window-sync` (propagation), `design-system/primitives`.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for conflict rules); Iris reviews the settings UI.

**Size**

M: resolver is small; presets and settings UI carry the bulk.
