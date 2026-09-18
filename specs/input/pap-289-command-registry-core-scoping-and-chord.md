---
identifier: "PAP-289"
title: "Command registry core, scoping and chord matcher"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: "PAP-151"
children: []
blockedBy: ["PAP-67", "PAP-150", "PAP-238"]
blocks: ["PAP-290", "PAP-482", "PAP-641", "PAP-642", "PAP-643", "PAP-646"]
key: "input/commands/registry-core"
url: "https://linear.app/paperos/issue/PAP-289/command-registry-core-scoping-and-chord-matcher"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-23"
cycle: null
---

# PAP-289: Command registry core, scoping and chord matcher

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Build the heart of PAP-151: `defineCommand`, a registry with a scope stack, chord and sequence matching on PAP-150's `Chord`, `when` guards, conflict warnings and a build-time manifest that fails on duplicate IDs.

**Scope**

In:

* `packages/input/src/commands/`: `defineCommand({ id, title, description?, icon?, keywords?, scope, shortcut?, when?, permission?, argsSchema?, agentCallable?, voice?, run })`, `CommandRegistry { register, unregister, execute, list, setBindingsResolver }`, hooks `useCommand`, `useCommands`, `useShortcut`.
* `CommandScopeProvider` scope stack (global → page route id → focused component); innermost match wins.
* Matcher: chords, sequences (`g i`, 1 s timeout), platform display, browser-reserved warnings, `allowInInput` guard.
* `pnpm commands:manifest` → `commands.manifest.json`; Vitest fails on duplicate IDs.

Out: palette UI (sibling 2), agent endpoint and defaults (sibling 3).

**Spec**

* IDs dot-namespaced; `when(ctx)` receives `{ route, selection, focusedScope, permissions, capabilities, isEditing }`.
* `permission` checked with `can()`; hidden commands excluded from `list`.
* Letters matched on `event.code`, symbols on `event.key`.

*Round 4 amendment (2026-09-18):*

* Round 4: the matcher ignores `keydown` while `event.isComposing` is true and the 229 keyCode, and resets pending sequences on composition start. The registry accepts a `root` id so each OS window mounts its own scope root (PAP-646); `CommandDef` gains optional `menu?: { group, order, showIn: ('context'|'toolbar'|'palette'|'native')[] }` (consumed by PAP-642 and PAP-649), `windowScope?: 'any'|'main'`, `macroSafe?: boolean` and `undoable?: boolean` metadata; all appear in `commands.manifest.json`.

**Interface contract**

Exposes the API above, `CommandDef` and `CommandContext` types, `commands.manifest.json` schema, `setBindingsResolver` seam for PAP-153. Consumes `parseChord`, `matchChord`, `formatChord` (PAP-150), `can()` (PAP-227), spec `commands:` section (PAP-114, optional).

**Definition of done**

* Registry used by a sample page with spec-declared commands; manifest committed; Linear comment with test summary.

**Test plan**

* Vitest: chord parsing on macOS and Linux mocks, sequences and timeout, scope precedence with sibling scopes, `when` guards, `allowInInput` inside a contenteditable, duplicate-ID failure, permission hiding, reserved-chord warning, non-Latin layout matching.
* Bench: `list()` over 2,000 commands under 2 ms.

**Demo**

In the sample page press `g i` and watch navigation; register a duplicate ID in a scratch file and run `pnpm commands:manifest` to see the failure. Under two minutes.

**Edge cases**

* Async `run` throws: error toast hook, registry healthy.
* Same chord in sibling scopes: focused wins.

**Dependencies**

PAP-150 (hard). PAP-59, PAP-114 (soft). Blocks siblings 2 and 3.

**Agent**

Built by Nova. Reviewed by Sentinel (Code Reviewer).

**Size**

M: the core API and matcher with a wide unit suite.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/input/command-context-menus` = PAP-642, `r4/input/multi-window-command-and-focus-routing` = PAP-646, `r4/input/native-menu-from-command-manifest` = PAP-649.
