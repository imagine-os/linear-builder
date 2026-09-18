---
identifier: "PAP-481"
title: "Wire realtime behind the module registry with an adapter and feature flag"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140", "PAP-141", "PAP-326", "PAP-434", "PAP-435", "PAP-475", "PAP-478", "PAP-537", "PAP-538", "PAP-605", "PAP-606"]
blocks: []
key: "module/realtime/wire"
url: "https://linear.app/paperos/issue/PAP-481/wire-realtime-behind-the-module-registry-with-an-adapter-and-feature"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:03.250Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-481: Wire realtime behind the module registry with an adapter and feature flag

**Model / Effort:** Sonnet 5 / high

**Goal**

Make `realtime` a swappable module in practice: its implementation binds into the `@paperos/kernel` registry as the default adapter for `@paperos/contract-realtime`, every consumer resolves the ports from the kernel instead of importing `apps/collab-server, packages/collab (presence, window bus), packages/sync extensions`, and a `module.realtime.impl` variant flag can select a second implementation per tenant with shadow-run and five-second rollback (`docs/module-system.md` sections 4 and 6). After this issue, rewriting realtime touches no other module.

**Scope**

In:

* `packages/<impl>/src/adapter.ts` (or one file per port): classes or factories implementing each port from `@paperos/contract-realtime`, registered by `module.ts` `bind(kernel)`; request-scoped ports receive the tenant and actor from the kernel's request scope.
* Consumer migration: every import of `realtime` internals from another module (found by `pnpm gen:dep-map --undeclared`) replaced with `kernel.resolve(port)` or a hook from the contract; lint R8 turned from warning to error for this module.
* Flag `module.realtime.impl` declared in `flags.yaml` (PAP-366) with variants `default` and `next`; a `next` implementation stub that re-exports the default (so the mechanism is exercised before a real rewrite exists).
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

Provides: `realtime` bound in the kernel as `@paperos/contract-realtime` provider `default`, flag `module.realtime.impl`, manifest `slots.fills` and `events.subscribes` complete, `X-PaperOS-Impl` on this module's routes. Consumes: `@paperos/kernel` registry and DI (`module-system/registry-di`), flag swap mechanism (`module-system/flag-swap`), `@paperos/contract-realtime@0.1` and its conformance suite, the implementation from PAP-140, PAP-141, PAP-326, PAP-366 flags, PAP-267 middleware for the header. Consumed by: every consumer of the contract (PAP-321 (canvas overlay), PAP-146 (agents as participants), PAP-149 (follow mode), PAP-411 (support chat), PAP-142 rich text, PAP-131 comments live updates), the swap CLI, PAP-266's removal matrix.

**Test plan**

* Unit: `bind` registers every port; unbound port fails boot with its name; request scope carries tenant and actor.
* Integration (compose stack): conformance suite passes against the kernel-resolved provider (not a direct import); flipping `module.realtime.impl` to `next` for one tenant changes `X-PaperOS-Impl` for that tenant only within 5 s; kill switch returns `default`.
* Static: `pnpm gen:dep-map --undeclared` reports zero undeclared edges into `realtime`; lint R8 error level; `knip` finds no unused exports left behind by the migration.
* Shadow: e2e run with `shadow: true` produces zero diffs between `default` and the `next` stub.
* E2E: the module's main flows (from its umbrella's Definition of done) pass unchanged after the migration; Gate 3 screenshots identical to baseline.

**Definition of done**

* Kernel binding merged; zero undeclared imports into `realtime` across the monorepo; conformance green through the kernel; flag flip recording attached; shadow diff report empty.
* `docs/platform/modules.md` module page updated (bindings, flag, slots, events); dependency map regenerated and committed; Linear comment with the recording and report.

**Edge cases**

* A consumer that resolves a port at module-evaluation time: rewrite to lazy resolution; the lint flags top-level `kernel.resolve`.
* Flag service unavailable at boot: kernel falls back to `default`, never to `next`.
* Module disabled while a request is in flight: the request finishes on the old binding; the next request sees `MODULE_DISABLED`.

**Dependencies**

Blocked by `module/realtime/contract`, `module/realtime/conformance`, `module-system/registry-di`, `module-system/flag-swap` and PAP-140, PAP-141, PAP-326. Blocks PAP-266.

*Round 4 (2026-09-18): PAP-266 soft: this issue no longer blocks PAP-266 because the realtime wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); PAP-266 proceeds (PAP-266's removal matrix covers modules whose wire issue has merged; PAP-481 adds its module to the matrix and to* `paperos create --without` *when it lands) and reconciles when this issue lands.*

**Agent**

Built by Nova (Multiplayer & Realtime owner). Reviewed by Forge and Forge (kernel).

**Size**

M

**Demo**

Reviewer flips `module.realtime.impl` from `hocuspocus` to `memory` in a single-user test app and edits a doc: presence and live records still work locally, proving collab and tables consumed only the ports. Ninety seconds.
