---
identifier: "PAP-537"
title: "Kernel host integrations: Hono request-scope middleware, React `KernelProvider` and `useKernel`, worker job scope and the `apps/*/src/kernel.ts` boot files"
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
blockedBy: ["PAP-13", "PAP-267", "PAP-433", "PAP-434"]
blocks: ["PAP-265", "PAP-435", "PAP-437", "PAP-438", "PAP-444", "PAP-453", "PAP-454", "PAP-455", "PAP-458", "PAP-461", "PAP-464", "PAP-471", "PAP-472", "PAP-473", "PAP-480", "PAP-481", "PAP-482", "PAP-489", "PAP-490", "PAP-491", "PAP-496", "PAP-497", "PAP-538", "PAP-545", "PAP-546", "PAP-547", "PAP-548", "PAP-549", "PAP-552"]
key: "r4/module-system/kernel-integrations"
url: "https://linear.app/paperos/issue/PAP-537/kernel-host-integrations-hono-request-scope-middleware-react"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:38.204Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-537: Kernel host integrations: Hono request-scope middleware, React `KernelProvider` and `useKernel`, worker job scope and the `apps/*/src/kernel.ts` boot files

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-434 builds the container; wiring it into the three hosts (API, web, worker) is separable work that touches other modules' entry points and can run in parallel once `createKernel` exists. Splitting it keeps the container session pure and gives the gateway (PAP-437) and slots (PAP-438) the integration points they import.

**Scope**

In:

* `packages/kernel/hono.ts`: `kernelMiddleware(kernel)` creating `kernel.scope({ tenantId, actor, requestId })` from the PAP-267 context (PAP-34 session variables) and disposing it at response end; `c.get("kernel")` typed.
* `packages/kernel/react.tsx`: `<KernelProvider kernel>` and `useKernel()`, `usePort(token)` resolving in the browser scope (tenant and principal from the session), suspense-friendly lazy providers.
* `packages/kernel/worker.ts`: `withJobScope(job, fn)` for PAP-43 handlers creating a scope with `actor.type='service'` and the job's tenant.
* `apps/web/src/kernel.ts`, `apps/api/src/kernel.ts`, `apps/worker/src/kernel.ts`: the only files allowed to import module packages (R8 exception, PAP-439), calling each module's `bind(kernel)`; `pnpm modules:list` reads them.

Out: the container itself (PAP-434 sibling), flag selection (PAP-435), slots runtime (PAP-438).

**Spec**

* Scope creation per request under 50 microseconds (PAP-434 budget) including the middleware overhead.
* A handler resolving a request-scoped port after the response ended throws `SCOPE_DISPOSED`.
* React provider never resolves request-scoped ports; it exposes `singleton` and a browser `session` scope.
* Boot order: manifests validated, `bind` in topological order, then hosts start; a boot failure exits non-zero with the module and port.

**Interface contract**

Provides: `kernelMiddleware`, `KernelProvider`, `useKernel`, `usePort`, `withJobScope`, the three `kernel.ts` boot files; consumed by PAP-437 (gateway), PAP-438 (slots), PAP-444, every `Wire <module>` issue, PAP-265, PAP-266.

Consumes: `createKernel` and scopes (PAP-434 sibling), Hono app and context (PAP-267), session variables (PAP-34), jobs (PAP-43, soft), workspace layout (PAP-13).

**Definition of done**

* The three apps boot through the kernel on the compose stack; a request with `x-tenant` resolves a request-scoped port that sees the right `tenantId` (integration test).
* `SCOPE_DISPOSED` and boot-failure paths tested; `docs/platform/kernel.md` integrations section; Linear comment.

**Test plan**

* Unit: middleware scope lifecycle with 1,000 interleaved fake requests; React hook resolution; job scope actor type.
* E2E: compose stack boot of api and worker; web renders a slot fill through `usePort`.

**Demo**

Reviewer starts `paperos dev`, calls the API with two different `x-tenant` headers and sees each response echo its tenant from a request-scoped port; opens the web app and `usePort` renders the identity port's principal. Under a minute.

**Edge cases**

* Streaming response (push transport): scope disposed on stream close, not on headers sent.
* Vite HMR replaces `kernel.ts`: provider rebuilds singletons (PAP-434 rule) without a full reload.
* Worker job without a tenant (platform cron): `kernel.system()` scope with reason.

**Dependencies**

Hard: PAP-267, PAP-13; sibling: PAP-434 container. Soft: PAP-34, PAP-43. Blocks PAP-437, PAP-438.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-434 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-434 blocks this issue (`blocks` relation).
