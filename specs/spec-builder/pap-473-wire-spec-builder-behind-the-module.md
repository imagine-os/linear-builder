---
identifier: "PAP-473"
title: "Wire spec-builder behind the module registry with an adapter and feature flag"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-115", "PAP-312", "PAP-314", "PAP-434", "PAP-435", "PAP-467", "PAP-470", "PAP-537", "PAP-538"]
blocks: []
key: "module/spec-builder/wire"
url: "https://linear.app/paperos/issue/PAP-473/wire-spec-builder-behind-the-module-registry-with-an-adapter-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:04.234Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-473: Wire spec-builder behind the module registry with an adapter and feature flag

**Model / Effort:** Sonnet 5 / high

**Goal**

Make `spec-builder` a swappable module in practice: its implementation binds into the `@paperos/kernel` registry as the default adapter for `@paperos/contract-spec-builder`, every consumer resolves the ports from the kernel instead of importing `packages/spec, specs/`, and a `module.spec-builder.impl` variant flag can select a second implementation per tenant with shadow-run and five-second rollback (`docs/module-system.md` sections 4 and 6). After this issue, rewriting spec-builder touches no other module.

**Scope**

In:

* `packages/<impl>/src/adapter.ts` (or one file per port): classes or factories implementing each port from `@paperos/contract-spec-builder`, registered by `module.ts` `bind(kernel)`; request-scoped ports receive the tenant and actor from the kernel's request scope.
* Consumer migration: every import of `spec-builder` internals from another module (found by `pnpm gen:dep-map --undeclared`) replaced with `kernel.resolve(port)` or a hook from the contract; lint R8 turned from warning to error for this module.
* Flag `module.spec-builder.impl` declared in `flags.yaml` (PAP-366) with variants `default` and `next`; a `next` implementation stub that re-exports the default (so the mechanism is exercised before a real rewrite exists).
* Slot fills and route contributions moved from code into the manifest; event subscriptions declared in `events.subscribes`.
* Shadow mode wiring for the module's read ports (`shadow: true` diffs into `swap_shadow_diff`).

Out: a real second implementation (the shell swap drill covers the shell; others come when a rewrite is proposed); changes to the contract (own issue).

**Spec**

* `bind(kernel)` registers one provider per port with `{ impl: 'default' }`; boot fails with the port name if a port from `provides` is unbound.
* Resolution order per request: kill switch, tenant flag rule, audience rule, default (PAP-366 order); the chosen `impl` is echoed as `X-PaperOS-Impl` on API responses and as a data attribute on slot fills.
* Consumers hold no reference across requests to a resolved request-scoped port.
* Shadow mode runs the secondary after the primary, never blocks the response, records `{ caseId, requestId, diff }` with a 1 percent sample by default.
* Disabling the module (PAP-266 `tenant_module`) unbinds its providers for that tenant; consumers with `requires[].optional=false` fail closed with `MODULE_DISABLED` (409).

**Interface contract**

Provides: `spec-builder` bound in the kernel as `@paperos/contract-spec-builder` provider `default`, flag `module.spec-builder.impl`, manifest `slots.fills` and `events.subscribes` complete, `X-PaperOS-Impl` on this module's routes. Consumes: `@paperos/kernel` registry and DI (`module-system/registry-di`), flag swap mechanism (`module-system/flag-swap`), `@paperos/contract-spec-builder@0.1` and its conformance suite, the implementation from PAP-115, PAP-314, PAP-312, PAP-366 flags, PAP-267 middleware for the header. Consumed by: every consumer of the contract (PAP-361 (entity-derived specs), PAP-362 (`paperos gen`), PAP-249 (scenario planner), PAP-320 (canvas loader), PAP-118 (authoring skill), PAP-64 (permission matrix tests)), the swap CLI, PAP-266's removal matrix.

**Test plan**

* Unit: `bind` registers every port; unbound port fails boot with its name; request scope carries tenant and actor.
* Integration (compose stack): conformance suite passes against the kernel-resolved provider (not a direct import); flipping `module.spec-builder.impl` to `next` for one tenant changes `X-PaperOS-Impl` for that tenant only within 5 s; kill switch returns `default`.
* Static: `pnpm gen:dep-map --undeclared` reports zero undeclared edges into `spec-builder`; lint R8 error level; `knip` finds no unused exports left behind by the migration.
* Shadow: e2e run with `shadow: true` produces zero diffs between `default` and the `next` stub.
* E2E: the module's main flows (from its umbrella's Definition of done) pass unchanged after the migration; Gate 3 screenshots identical to baseline.

**Definition of done**

* Kernel binding merged; zero undeclared imports into `spec-builder` across the monorepo; conformance green through the kernel; flag flip recording attached; shadow diff report empty.
* `docs/platform/modules.md` module page updated (bindings, flag, slots, events); dependency map regenerated and committed; Linear comment with the recording and report.

**Edge cases**

* A consumer that resolves a port at module-evaluation time: rewrite to lazy resolution; the lint flags top-level `kernel.resolve`.
* Flag service unavailable at boot: kernel falls back to `default`, never to `next`.
* Module disabled while a request is in flight: the request finishes on the old binding; the next request sees `MODULE_DISABLED`.

**Dependencies**

Blocked by `module/spec-builder/contract`, `module/spec-builder/conformance`, `module-system/registry-di`, `module-system/flag-swap` and PAP-115, PAP-314, PAP-312. Blocks nothing in Linear yet; it is a precondition for any future rewrite of this module.

**Agent**

Built by Quill (Spec Builder owner). Reviewed by Sentinel and Forge (kernel).

**Size**

M

**Demo**

Reviewer registers a second generator implementation behind `module.spec-builder.impl=gen-next`, runs `paperos gen` on the demo app and diffs the two outputs byte for byte. Two minutes.
