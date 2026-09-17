---
identifier: "PAP-438"
title: "Build the UI slot and extension system in the shell: named slots with Zod props, manifest-declared fills, guards, ordering and the `<Slot>` runtime"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-433", "PAP-434"]
blocks: ["PAP-62", "PAP-63", "PAP-265", "PAP-446"]
key: "module-system/ui-slots"
url: "https://linear.app/paperos/issue/PAP-438/build-the-ui-slot-and-extension-system-in-the-shell-named-slots-with"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:50:07.195Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-438: Build the UI slot and extension system in the shell: named slots with Zod props, manifest-declared fills, guards, ordering and the `<Slot>` runtime

**Model / Effort:** Sonnet 5 / high

**Goal**

Give the shell a small, versioned surface that modules plug into, so a rewritten shell only has to expose the same slot ids with the same props. PAP-16 adds layout slots to the router; this issue turns them into the contract in `@paperos/contract-app-shell` (`ShellSlots`), lets modules declare fills in their manifests, and ships the `<Slot>` runtime that renders, orders and guards them (`docs/module-system.md` section 4 row 5).

**Scope**

In:

* Slot registry in `contract-app-shell`: `shell.nav`, `shell.sidebar`, `shell.inspector`, `shell.commandBar`, `shell.header.actions`, `shell.userMenu`, `shell.tenantSwitcher`, `shell.settings.sections`, `record.panel.tabs`, `view.toolbar`, `dashboard.blocks`, each with a Zod props schema, cardinality (single, ordered list) and allowed component kinds.
* `packages/kernel/slots`: `registerFill(slot, fill)` from manifests at boot; `<Slot name props />` and `useSlotFills(name)`; ordering by `order` then module id; `when` guards evaluated with `can()` and `useFlag`; lazy imports with `ui.skeleton` fallback and error boundary per fill (PAP-368 contract).
* Dev-mode validation: unknown slot or invalid props throws at boot with module and slot; production renders nothing and emits `slot.fill_rejected` telemetry.
* Migration of existing fills: navigation items, inspector panels and command palette contributions currently hard-wired in `apps/web` move to manifests of their modules.
* Storybook stories per slot with golden fills (PAP-69) for Gate 3.

Out: the layout components themselves (PAP-70), window management (PAP-262), codegen of page-level slot mapping (PAP-315, which consumes this).

**Spec**

* Slot ids and props are part of `contract-app-shell` and follow its semver; adding a slot is minor, changing props is major.
* A fill references a component by registered `ui.<name>` id (PAP-74) or a lazy import inside its own module package; never a component from another module package.
* Props passed by the shell to a fill are validated once per mount in dev, never in production hot paths.
* Guard failure hides the fill and its nav item; the route stays protected by `can()` independently.
* Render budget: 100 fills across all slots add under 16 ms to first paint (measured in Storybook).

**Interface contract**

Provides: `ShellSlots` in `contract-app-shell`, `<Slot>`, `useSlotFills`, `registerFill`, `slot.fill_rejected` telemetry, Storybook slot stories. Consumes: PAP-16 router layout slots, kernel registry and React integration, manifest `slots.fills`, PAP-74 component ids, PAP-59 `can`, PAP-366 flags, PAP-368 error boundary contract, PAP-69 Storybook. Consumed by: every module that fills a slot (`Wire <module>` issues), PAP-62 and PAP-63 shells, PAP-265, PAP-315 layout codegen, the shell swap drill.

**Test plan**

* Unit: registration, ordering, cardinality violation (two fills in a single slot), guard evaluation, invalid props rejected in dev and dropped in production.
* Integration: `apps/web` boots with every module's manifest fills; the navigation matches the previous hard-wired list exactly (snapshot).
* Visual: Storybook stories per slot at seven widths through Gate 3 (PAP-246); a11y (PAP-73) on the rendered slots.
* Benchmark: 100-fill render budget.

**Definition of done**

* Slot contract and runtime merged; all existing contributions moved to manifests; `apps/web` shows no hard-wired module UI; stories and screenshots attached; budget met.
* `docs/platform/slots.md` with the slot table; ADR; Linear comment.

**Edge cases**

* Fill from a disabled module (PAP-266): unregistered for that tenant at scope creation; the nav item disappears without a reload.
* Two fills claim the same `order`: tie broken by module id; documented.
* Slot rendered before the kernel has booted (SSR or first paint): renders the fallback; never throws.
* Multi-window (PAP-262): each window renders its own slots; a fill can declare `windows: ['main']` to stay out of detached panels.

**Dependencies**

Blocked by PAP-16, module-system/manifest-schema, module-system/registry-di. Blocks PAP-62, PAP-63, PAP-265.

**Agent**

Built by Forge. Reviewed by Iris.

**Size**

M

**Demo**

Reviewer runs Storybook, opens `shell.nav` and sees fills from tables, PM, CRM and finance in order; disables the CRM module for the demo tenant in `/settings/modules` and the CRM item vanishes; adds a fill with a wrong prop in a fixture manifest and `pnpm dev` refuses to boot, naming slot and module. Ninety seconds.
