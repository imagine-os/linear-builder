---
identifier: "PAP-476"
title: "Publish @paperos/contract-input v0.1 with manifest"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150", "PAP-433"]
blocks: ["PAP-153", "PAP-154", "PAP-158", "PAP-159", "PAP-479", "PAP-482", "PAP-651", "PAP-653"]
key: "module/input/contract"
url: "https://linear.app/paperos/issue/PAP-476/publish-paperoscontract-input-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:03.039Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 2
dueDate: "2026-09-23"
cycle: null
---

# PAP-476: Publish @paperos/contract-input v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-input` v0.1 and the `input` module manifest so every other module codes against a versioned package instead of `packages/input (command registry, input abstraction, dnd, voice)` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `low`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/input/` published as `@paperos/contract-input` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-input', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Nova', project: 'input' }`, `swapRisk: 'low'`, `kind: 'runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/input.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-150 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `InputEvent` unified abstraction for mouse, touch, pen, gamepad (PAP-150) with `pressure`, `pointerType`, `modifiers`
* `CommandRegistryPort`: `defineCommand`, `scope`, `chord`, `execute`, `list`, agent execution endpoint (PAP-289 to PAP-291)
* `KeymapPreset` schema (default, Vim-style, Linear-like; PAP-153) and `FocusPort` (roving tabindex, skip links, restore; PAP-152)
* `DndPort` sensors and `SortableList`, `KanbanDnd` contracts (PAP-329 to PAP-331)
* `VoiceRoutePort` (PAP-159) and `GesturePort` (PAP-154); slot fill `shell.commandBar:palette`

Events declared with `defineTopic()` (payload schemas, version 1): `command.executed`, `keymap.changed`.

Requires (manifest `requires[]`): \* `@paperos/contract-app-shell` ^0.1 (command bar slot)

* `@paperos/contract-design-system` ^0.1

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-input@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.input`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-150 (Design a unified input event abstraction so components handl). Consumed by: PAP-153 (keymaps), PAP-154 (touch gestures), PAP-158 (gamepad), PAP-159 (voice), PAP-167 kanban, PAP-341 grid keyboard navigation, PAP-157 pen, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (twenty input events across pointer types, eight chord sequences (including conflicts), three keymap presets, four drag sequences with keyboard alternative, two voice transcripts); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Iris confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/input.md` generated; short ADR `docs/adr/00xx-contract-input.md` recording what was pinned.
* Comments on PAP-153, PAP-154, PAP-158, PAP-159 that their Interface contract sections now import from `@paperos/contract-input`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-150. Blocks PAP-153, PAP-154, PAP-158, PAP-159, `module/input/conformance` and `module/input/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Nova (Multi-Input Control & Accessibility owner). Reviewed by Iris and Atlas (contract ownership).

**Size**

S

**Demo**

Reviewer runs `pnpm contract:show input` and replays the eight chord fixtures through the reference matcher, seeing the conflict fixture rejected at registration. Under a minute.
