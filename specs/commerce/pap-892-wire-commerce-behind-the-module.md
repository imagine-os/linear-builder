---
identifier: "PAP-892"
title: "Wire commerce behind the module registry with an adapter and feature flag"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Operations packs, marketplace and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-267", "PAP-366", "PAP-434", "PAP-435", "PAP-877", "PAP-879", "PAP-880", "PAP-883", "PAP-884", "PAP-891"]
blocks: []
key: "r4/commerce/wire"
url: "https://linear.app/paperos/issue/PAP-892/wire-commerce-behind-the-module-registry-with-an-adapter-and-feature"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:04.283Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-892: Wire commerce behind the module registry with an adapter and feature flag

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make `commerce` a swappable module in practice: its implementation binds into the `@paperos/kernel` registry as the default adapter for `@paperos/contract-commerce`, every consumer resolves the ports from the kernel instead of importing `packages/commerce, apps/web/src/commerce, packs/*`, and a `module.commerce.impl` variant flag can select a second implementation per tenant with shadow-run and five-second rollback (`docs/module-system.md` sections 4 and 6). After this issue, rewriting commerce touches no other module.

**Scope**

In: `packages/commerce/src/adapter.ts` (or one file per port): classes or factories implementing each port from `@paperos/contract-commerce`, registered by `module.ts` `bind(kernel)`; request-scoped ports receive the tenant and actor from the kernel's request scope. Consumer migration: every import of `commerce` internals from another module (found by `pnpm gen:dep-map --undeclared`) replaced with `kernel.resolve(port)` or a hook from the contract; lint R8 turned from warning to error for this module. Flag `module.commerce.impl` declared in `flags.yaml` (PAP-366) with variants `default` and `next`; a `next` implementation stub that re-exports the default so the mechanism is exercised before a real rewrite exists. Slot fills and route contributions moved from code into the manifest; event subscriptions declared in `events.subscribes`; shadow mode wiring for the module's read ports (`shadow: true` diffs into `swap_shadow_diff`).

Out: A real second implementation. Changes to the contract (own issue).

**Spec**

* `bind(kernel)` registers one provider per port with `{ impl: 'default' }`; boot fails with the port name if a port from `provides` is unbound
* Resolution order per request: kill switch, tenant flag rule, audience rule, default (PAP-366 order); the chosen `impl` is echoed as `X-PaperOS-Impl` on API responses and as a data attribute on slot fills
* Consumers hold no reference across requests to a resolved request-scoped port
* Shadow mode runs the secondary after the primary, never blocks the response, records `{ caseId, requestId, diff }` with a 1 percent sample by default; write ports and sending ports are never shadowed (PAP-435 rule)
* Disabling the module (PAP-266 `tenant_module`) unbinds its providers for that tenant; consumers with `requires[].optional=false` fail closed with `MODULE_DISABLED` (409)

**Interface contract**

Provides: `commerce` bound in the kernel as `@paperos/contract-commerce` provider `default`, flag `module.commerce.impl`, manifest `slots.fills` and `events.subscribes` complete, `X-PaperOS-Impl` on this module's routes. Consumes: `@paperos/kernel` registry and DI (PAP-434), flag swap mechanism (PAP-435), `@paperos/contract-commerce@0.1` and its conformance suite, PAP-366 flags, PAP-267 middleware for the header, and this project's Build issues. Consumed by: business-core reports (PAP-183), growth (order and subscription activity), engagement (loyalty earn, shifts), assistant (order and stock tools), platform-ops (commerce metrics), migration (gallery and importers), the swap CLI (PAP-442) and PAP-266's removal matrix.

**Definition of done**

* Kernel binding merged; zero undeclared imports into `commerce` across the monorepo; conformance green through the kernel; flag flip recording attached; shadow diff report empty
* `docs/platform/modules.md` module page updated (bindings, flag, slots, events); dependency map regenerated and committed
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: `bind` registers every port; unbound port fails boot with its name; request scope carries tenant and actor.
* Integration: conformance suite passes against the kernel-resolved provider (not a direct import); flipping `module.commerce.impl` to `next` for one tenant changes `X-PaperOS-Impl` for that tenant only within 5 s; kill switch returns `default`.
* Static: `pnpm gen:dep-map --undeclared` reports zero undeclared edges into `commerce`; lint R8 error level; `knip` finds no unused exports left behind.
* E2E: the module's main flows (from its model issue's Definition of done) pass unchanged after the migration; Gate 3 screenshots identical to baseline.

**Demo**

Flip `module.commerce.impl` to `next` for the demo tenant in the console, watch `X-PaperOS-Impl: next` appear on the module's routes within five seconds, then hit the kill switch and watch it revert.

**Edge cases**

* A consumer that cached a port instance at module scope: the lint rule R10 flags it and the integration test proves the flag flip is not observed by a cached instance (so the rule must hold)
* Two tenants on different implementations sharing one worker process: job handlers resolve the port inside the job with the job's tenant scope, never at worker boot
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-877 and PAP-891 (hard), PAP-434, PAP-435 (hard), PAP-366, PAP-267 (soft), the project's Build issues (hard: nothing to bind before they land).

* Soft dependency (round 4): PAP-266 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-10-16) is later than PAP-266's (2026-09-29), so it must not block it; build against its interface and reconcile when it lands.
  **Agent**

Builder: Ledger. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/commerce/conformance` = PAP-891, `r4/commerce/contract-publish` = PAP-877.
