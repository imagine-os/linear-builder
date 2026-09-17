---
identifier: "PAP-447"
title: "Publish @paperos/contract-app-shell v0.1 with manifest"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Template scaffolds and runs on web"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-17", "PAP-433"]
blocks: ["PAP-62", "PAP-63", "PAP-70", "PAP-265", "PAP-450", "PAP-453"]
key: "module/app-shell/contract"
url: "https://linear.app/paperos/issue/PAP-447/publish-paperoscontract-app-shell-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:11:30.303Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-447: Publish @paperos/contract-app-shell v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-app-shell` v0.1 and the `app-shell` module manifest so every other module codes against a versioned package instead of `apps/web, apps/desktop, apps/mobile, packages/core (index, modules, pwa, windows, native, flags, i18n, nav)` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `critical`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/app-shell/` published as `@paperos/contract-app-shell` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-app-shell', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Forge', project: 'app-shell' }`, `swapRisk: 'critical'`, `kind: 'runtime host'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/app-shell.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-16, PAP-17 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `ShellSlots`: the slot registry with one Zod props schema per slot (`shell.nav`, `shell.sidebar`, `shell.inspector`, `shell.commandBar`, `shell.header.actions`, `shell.userMenu`, `shell.tenantSwitcher`, `shell.settings.sections`, `record.panel.tabs`, `view.toolbar`, `dashboard.blocks`)
* `RouteContribution` and `composeRoutes()` input shape (PAP-16, PAP-264), `NavItem`
* `LayoutPort` (`useLayout`, breakpoint names from PAP-14) and `WindowManagerPort` (`detach`, `dock`, `listDisplays`, topology hash; PAP-262)
* `ConfigPort` and `SecretsPort` (typed settings, secret names only; PAP-17, PAP-300 adapter)
* `FlagsPort` (`useFlag`, `useVariant`, `flagGuard`, `FlagKey`; PAP-366) and `I18nPort` (PAP-27)
* `NativeCapabilitiesPort` (camera, haptics, biometrics, secure storage, share; PAP-259) with web fallbacks declared as capabilities

Events declared with `defineTopic()` (payload schemas, version 1): `shell.window.opened|closed`, `flags.changed`, `module.enabled|disabled`.

Requires (manifest `requires[]`): \* `@paperos/contract-identity` ^0.1 (`Principal`, `useCan` for slot guards)

* `@paperos/contract-design-system` ^0.1 (component ids allowed in slots)
* `@paperos/contract-spec-builder` ^0.1 (route meta from page specs; optional)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-app-shell@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.app-shell`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-16 (Implement file-based router with layout slots (nav, sidebar,), PAP-17 (Define typed environment and config layer with per-target se). Consumed by: PAP-62 and PAP-63 (portal and console shells), PAP-70 (layout components), PAP-265 (module integration), every module that fills a slot, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (ten slot fills (one per slot, valid and invalid props), three route trees (empty app, full template, `--without` set), two display topologies, one config file per target); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/app-shell.md` generated; short ADR `docs/adr/00xx-contract-app-shell.md` recording what was pinned.
* Comments on PAP-62, PAP-63, PAP-70, PAP-265 that their Interface contract sections now import from `@paperos/contract-app-shell`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-16, PAP-17. Blocks PAP-62, PAP-63, PAP-70, PAP-265, `module/app-shell/conformance` and `module/app-shell/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Forge (Universal App Shell & Repo Template owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show app-shell` and sees the eleven slots with their props schemas, then edits a fill in a fixture to pass a wrong prop and watches `pnpm conformance app-shell` fail on that slot. Under a minute.
