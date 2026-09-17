---
identifier: "PAP-434"
title: "Build the module registry and dependency-injection container (`@paperos/kernel`): typed ports, scopes, side-by-side implementations"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Kernel and lint live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-433"]
blocks: ["PAP-265", "PAP-435", "PAP-437", "PAP-438", "PAP-444", "PAP-453", "PAP-454", "PAP-455", "PAP-458", "PAP-461", "PAP-464", "PAP-471", "PAP-472", "PAP-473", "PAP-480", "PAP-481", "PAP-482", "PAP-489", "PAP-490", "PAP-491", "PAP-496", "PAP-497"]
key: "module-system/registry-di"
url: "https://linear.app/paperos/issue/PAP-434/build-the-module-registry-and-dependency-injection-container"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:50:05.968Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-434: Build the module registry and dependency-injection container (`@paperos/kernel`): typed ports, scopes, side-by-side implementations

**Model / Effort:** Opus 5 / medium

**Goal**

Build the piece of middle tooling that every swap depends on: `packages/kernel` (`@paperos/kernel`) with `createKernel()`, which loads manifests, resolves `requires` topologically, binds providers to typed port tokens and resolves them per scope, and allows two implementations of the same contract to be bound side by side so a flag (next issue) can choose between them. After this, no module imports another module; it asks the kernel (`docs/module-system.md` section 4, first row).

**Scope**

In:

* `createKernel({ appSpec, manifests })`: validation (manifest issue), topological order, cycle and version conflict errors with module ids.
* `port<T>(contract, name)` typed tokens; `kernel.bind(token, provider, { impl, scope })`; `kernel.resolve(token, { impl? })`; `kernel.scope(requestContext)` returning a child container carrying `tenantId`, `actor`, `requestId` from PAP-34's session variables.
* Scopes `singleton`, `request`, `transient`; disposal hooks; lazy providers.
* `kernel.describe()` (bindings, impls, consumers) feeding `pnpm modules:list` and the docs generator.
* Integration points: Hono middleware (PAP-267) that creates the request scope; React `KernelProvider` and `useKernel()` in `packages/kernel/react` for slot fills and hooks; worker entry (PAP-43) request scope per job.
* Adoption in the template: `apps/web`, `apps/api`, `apps/worker` boot through `createKernel`.

Out: flag-based selection (next issue), slots runtime (own issue), the event bus (PAP-303), any module adapters (wire issues).

**Spec**

* Unbound required port at boot: `PORT_UNBOUND <contract>.<port> required by <module>`; optional port resolves `undefined`.
* Resolution is O(1) after boot; request scope creation under 50 microseconds (benchmarked, since it runs per request and per job).
* Two bindings for one token must differ in `impl`; `resolve` without `impl` returns `default`; the selection hook (flag issue) can override per scope.
* No global singleton: tests create isolated kernels; the template exposes one instance from `apps/*/src/kernel.ts`.
* Providers receive `(scope) => Impl` and may resolve other ports; circular resolution throws with the chain.

**Interface contract**

Provides: `@paperos/kernel`: `createKernel`, `port`, `bind`, `resolve`, `scope`, `describe`, Hono and React integrations, `pnpm modules:list`. Consumes: manifest schema and validator, PAP-13 workspace, PAP-267 middleware chain (soft; a standalone Hono app in tests until it merges), PAP-34 session variable names. Consumed by: the flag swap, gateway, slots, conformance runner and swap CLI issues; every `Wire <module>` issue; PAP-265, PAP-266.

**Test plan**

* Unit: topological order on chains, diamonds, cycles; unbound and duplicate bindings; scope isolation (two concurrent request scopes never share request-scoped instances, tested with 1,000 interleaved resolutions).
* Benchmark (Vitest bench): scope creation and resolution against the budgets; regression fails the PR.
* Integration: `apps/api` boots through the kernel on the compose stack; a request with `x-tenant` resolves a request-scoped port that sees the right `tenantId`.
* Type: `resolve(port<ViewQueryPort>)` returns `ViewQueryPort`; binding a wrong shape is a compile error.

**Definition of done**

* Package merged; the three apps boot through it; benchmarks in budget; coverage 95 percent.
* `pnpm modules:list` prints the resolved graph with bindings; `docs/platform/kernel.md` written; ADR; Linear comment.

**Edge cases**

* Provider throws during boot: kernel reports the module and port and aborts; no partial boot in production, partial boot allowed in dev with a banner.
* Hot module reload in Vite: kernel disposes and rebuilds singletons; request scopes are never cached across reloads.
* A port used inside a Yjs or Electric callback outside any request: `kernel.system()` scope with `actor.type='service'` and an explicit reason (PAP-38).
* Tauri multi-window: one kernel per window; window bus (realtime contract) is the only cross-window channel.

**Dependencies**

Blocked by module-system/manifest-schema, PAP-13. Blocks PAP-265.

**Agent**

Built by Forge. Reviewed by Atlas and Sentinel.

**Size**

M

**Demo**

Reviewer runs `pnpm modules:list` and sees eighteen modules, their bindings and consumers; comments out the identity binding and `pnpm dev` fails with `PORT_UNBOUND @paperos/contract-identity.PermissionPort required by tables`. Under a minute.
