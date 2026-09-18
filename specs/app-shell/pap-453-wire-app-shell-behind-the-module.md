---
identifier: "PAP-453"
title: "Wire app-shell behind the module registry with an adapter and feature flag"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-264", "PAP-366", "PAP-434", "PAP-435", "PAP-447", "PAP-450", "PAP-501", "PAP-537", "PAP-538"]
blocks: ["PAP-446"]
key: "module/app-shell/wire"
url: "https://linear.app/paperos/issue/PAP-453/wire-app-shell-behind-the-module-registry-with-an-adapter-and-feature"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:07.748Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-453: Wire app-shell behind the module registry with an adapter and feature flag

**Model / Effort:** Sonnet 5 / high

**Goal**

Make `app-shell` a swappable module in practice: its implementation binds into the `@paperos/kernel` registry as the default adapter for `@paperos/contract-app-shell`, every consumer resolves the ports from the kernel instead of importing `apps/web, apps/desktop, apps/mobile, packages/core (index, modules, pwa, windows, native, flags, i18n, nav)`, and a `module.app-shell.impl` variant flag can select a second implementation per tenant with shadow-run and five-second rollback (`docs/module-system.md` sections 4 and 6). After this issue, rewriting app-shell touches no other module.

**Scope**

In:

* `packages/<impl>/src/adapter.ts` (or one file per port): classes or factories implementing each port from `@paperos/contract-app-shell`, registered by `module.ts` `bind(kernel)`; request-scoped ports receive the tenant and actor from the kernel's request scope.
* Consumer migration: every import of `app-shell` internals from another module (found by `pnpm gen:dep-map --undeclared`) replaced with `kernel.resolve(port)` or a hook from the contract; lint R8 turned from warning to error for this module.
* Flag `module.app-shell.impl` declared in `flags.yaml` (PAP-366) with variants `default` and `next`; a `next` implementation stub that re-exports the default (so the mechanism is exercised before a real rewrite exists).
* Slot fills and route contributions moved from code into the manifest; event subscriptions declared in `events.subscribes`.
* Shadow mode wiring for the module's read ports (`shadow: true` diffs into `swap_shadow_diff`).

Out: a real second implementation (the shell swap drill covers the shell; others come when a rewrite is proposed); changes to the contract (own issue).

**Spec**

* `bind(kernel)` registers one provider per port with `{ impl: 'default' }`; boot fails with the port name if a port from `provides` is unbound.
* Resolution order per request: kill switch, tenant flag rule, audience rule, default (PAP-366 order); the chosen `impl` is echoed as `X-PaperOS-Impl` on API responses and as a data attribute on slot fills.
* Consumers hold no reference across requests to a resolved request-scoped port.
* Shadow mode runs the secondary after the primary, never blocks the response, records `{ caseId, requestId, diff }` with a 1 percent sample by default.
* Disabling the module (PAP-266 `tenant_module`) unbinds its providers for that tenant; consumers with `requires[].optional=false` fail closed with `MODULE_DISABLED` (409).

*Round 4 amendment (2026-09-18):*

* Flag variants: `module.app-shell.impl` declares `default`, `next` (the re-exporting stub built here) and `minimal` (the drill shell from PAP-446, bound only when `apps/web-minimal` exists); the Demo section's `minimal` flip therefore runs after PAP-446 binds it, and the merge-time demo uses `next`.

**Interface contract**

Provides: `app-shell` bound in the kernel as `@paperos/contract-app-shell` provider `default`, flag `module.app-shell.impl`, manifest `slots.fills` and `events.subscribes` complete, `X-PaperOS-Impl` on this module's routes. Consumes: `@paperos/kernel` registry and DI (`module-system/registry-di`), flag swap mechanism (`module-system/flag-swap`), `@paperos/contract-app-shell@0.1` and its conformance suite, the implementation from PAP-16, PAP-264, PAP-366, PAP-366 flags, PAP-267 middleware for the header. Consumed by: every consumer of the contract (PAP-62 and PAP-63 (portal and console shells), PAP-70 (layout components), PAP-265 (module integration), every module that fills a slot), the swap CLI, PAP-266's removal matrix.

**Test plan**

* Unit: `bind` registers every port; unbound port fails boot with its name; request scope carries tenant and actor.
* Integration (compose stack): conformance suite passes against the kernel-resolved provider (not a direct import); flipping `module.app-shell.impl` to `next` for one tenant changes `X-PaperOS-Impl` for that tenant only within 5 s; kill switch returns `default`.
* Static: `pnpm gen:dep-map --undeclared` reports zero undeclared edges into `app-shell`; lint R8 error level; `knip` finds no unused exports left behind by the migration.
* Shadow: e2e run with `shadow: true` produces zero diffs between `default` and the `next` stub.
* E2E: the module's main flows (from its umbrella's Definition of done) pass unchanged after the migration; Gate 3 screenshots identical to baseline.

**Definition of done**

* Kernel binding merged; zero undeclared imports into `app-shell` across the monorepo; conformance green through the kernel; flag flip recording attached; shadow diff report empty.
* `docs/platform/modules.md` module page updated (bindings, flag, slots, events); dependency map regenerated and committed; Linear comment with the recording and report.

**Edge cases**

* A consumer that resolves a port at module-evaluation time: rewrite to lazy resolution; the lint flags top-level `kernel.resolve`.
* Flag service unavailable at boot: kernel falls back to `default`, never to `next`.
* Module disabled while a request is in flight: the request finishes on the old binding; the next request sees `MODULE_DISABLED`.

**Dependencies**

Blocked by `module/app-shell/contract`, `module/app-shell/conformance`, `module-system/registry-di`, `module-system/flag-swap` and PAP-16, PAP-264, PAP-366. Blocks module-system/shell-swap-drill.

**Agent**

Built by Forge (Universal App Shell & Repo Template owner). Reviewed by Sentinel and Forge (kernel).

**Size**

M

**Demo**

Reviewer flips `module.app-shell.impl` to `minimal` for the demo tenant in `/settings/flags`, reloads and sees every module's navigation and record panel tabs rendered by the stub shell; flips back and the full shell returns within five seconds. Ninety seconds.
