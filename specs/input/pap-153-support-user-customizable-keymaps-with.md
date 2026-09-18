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
blockedBy: ["PAP-151", "PAP-291", "PAP-476"]
blocks: ["PAP-647", "PAP-648", "PAP-649", "PAP-653"]
key: "input/keymaps"
url: "https://linear.app/paperos/issue/PAP-153/support-user-customizable-keymaps-with-presets-default-vim-style"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:43.076Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-153: Support user-customizable keymaps with presets (default, Vim-style, Linear-like) synced per user

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let power users bring their habits: pick a keymap preset (Default, Vim-style, Linear-like), rebind any command, and have bindings follow them to every device and window. Keymaps layer over the command registry; conflicts are detected before they bite.

**Scope**

In:

* `packages/input/src/keymaps/`: `Keymap = { id, name, base?, bindings: Record<commandId, Chord[] | null> }`; resolver merging preset → user overrides → page-scope overrides, plugged into PAP-151's `setBindingsResolver`.
* Presets: `default`, `vim` (`j/k`, `g g`/`G`, `/`, `:`, `h/l`, modal normal/insert layer), `linear` (`c`, `e`, `x`, `s`, `a`, `g i`, `g b`) with a comparison table.
* Settings `/settings/keyboard`: preset picker, searchable command list from `commands.manifest.json`, click-to-record binding with inline conflicts, two chords per command, reset, import and export JSON.
* Persistence: `user_preferences.keymap jsonb` (PAP-33 user extension), synced through PAP-143 and across windows through PAP-145; `localStorage` cache for first paint.
* Conflict detection: overlapping scopes, browser-reserved chords, `when`-guard explanations.

Out: per-tenant keymaps, macros, mouse buttons, Tiptap internals.

**Spec**

* Resolver memoised per scope stack; rebinding applies within one frame; help sheet and palette hints read effective chords from the resolver.
* Vim layer only where `role` is list, grid or tree; `Escape` returns to normal without blurring; mode shown in the status bar.
* Recording ignores lone modifiers; sequences by pausing 1 s.
* Import validated by Zod; unknown command IDs kept and greyed.

*Round 4 amendment (2026-09-18):*

* Round 4: the resolver gains two fixed layers between presets and user overrides: `a11y` (written by PAP-647: with `singleKeyShortcuts: 'off'` every modifier-less chord and sequence resolves to `null`; with `'modifierOnly'` they resolve to `alt+<key>`) and `macros` (PAP-648). The settings page shows the active layer that produced each effective chord, and the export format includes `layers` so imports are faithful.

**Interface contract**

Exposes: `Keymap` Zod schema and JSON export format, `resolveBindings(scopeStack) -> Map<commandId, Chord[]>`, `useKeymap()`, `useEffectiveChord(commandId)` (used by PAP-151 hints and PAP-159 aliases), preset files `presets/*.json`, `KeymapSettingsPage`, window message type `keymap.changed` (PAP-145), oRPC `preferences.keymap.get|set`. Consumes: `setBindingsResolver`, `commands.manifest.json` (PAP-151), `parseChord`/`formatChord` (PAP-150), `user_preferences` column (PAP-33), shape on `user_preferences` (PAP-143), `WindowBus` (PAP-145), primitives (PAP-67).

**Definition of done**

* Linear preset makes `c` open create and `g i` navigate on the sample list page; preference persists across reload and reaches a second browser within 2 s.
* Storybook settings stories (empty search, conflict, recording) in three themes, axe clean; screenshots at 768 and 1440.
* `docs/platform/input/keymaps.md` with the comparison table; changelog; Linear comment with demo link.

**Test plan**

* Vitest: merge precedence (preset < user < page), conflict detection across overlapping scopes, reserved-chord block, import validation with unknown IDs, vim mode transitions, `palette.open` replacement rule.
* Integration: `preferences.keymap.set` through `callAs` persists and RLS scopes to the user.
* Playwright: switch presets and run key flows for all three at 768 and 1440; record a new chord for `record.duplicate` and see the conflict warning; second context receives the change within 2 s.
* Visual: Gate 3 captures of the settings page states at 768 and 1440, three themes.

**Demo**

Open `/settings/keyboard`, choose Linear, go to a list and press `c`, then `g i`; return, search “duplicate”, click record, press `mod+d`, see the conflict note, save; reload and confirm it stuck. Under two minutes.

**Edge cases**

* Rebinding `mod+k` requires a replacement for `palette.open`.
* Key missing on the layout (`§`): warning, still stored.
* Preset update conflicts with a user override: override wins.
* Two windows rebind at once: last write wins, both re-resolve.

**Dependencies**

PAP-151 (hard, encoded). Soft: PAP-150, PAP-33, PAP-143, PAP-145, PAP-67. Consumed by PAP-159, PAP-158.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for conflict rules); Iris reviews the settings UI.

**Size**

M: resolver is small; presets and settings UI carry the bulk.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/input/accessibility-input-preferences` = PAP-647, `r4/input/macros-and-command-chains` = PAP-648.
