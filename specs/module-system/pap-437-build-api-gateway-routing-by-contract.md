---
identifier: "PAP-437"
title: "Build API gateway routing by contract: mount contract routers, resolve the bound implementation per request, `X-PaperOS-Impl` canary and response adapters"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-267", "PAP-268", "PAP-434", "PAP-537"]
blocks: ["PAP-442", "PAP-539"]
key: "module-system/gateway-routing"
url: "https://linear.app/paperos/issue/PAP-437/build-api-gateway-routing-by-contract-mount-contract-routers-resolve"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:08.869Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-437: Build API gateway routing by contract: mount contract routers, resolve the bound implementation per request, `X-PaperOS-Impl` canary and response adapters

**Model / Effort:** Sonnet 5 / high

**Goal**

Route API calls by contract instead of by module. oRPC routers are contributed per module today (PAP-268); this issue mounts each contract router once in `apps/api` and forwards every procedure to whichever implementation the kernel has selected for that request, so a swapped module needs no route changes, `X-PaperOS-Impl` lets staff and agents canary an implementation, and response adapters keep old clients working during a deprecation window (`docs/module-system.md` section 4 row 4).

**Scope**

In:

* `mountContract(app, kernel, contract)`: reads the contract's router signature (`routes.ts`), creates handlers that resolve the implementation's router from the kernel request scope and call the matching procedure; type-safe end to end.
* Routing table generated from manifests (`routes.json`: procedure, contract, providers, since) committed and served at `/api/v1/routes` for staff; OpenAPI (PAP-269) generated from the contract routers, so the public API is contract-shaped.
* `X-PaperOS-Impl` handling shared with the flag issue; `X-PaperOS-Contract-Version` response header.
* Response adapters: `defineResponseAdapter(contract, fromVersion, toVersion, fn)` applied when a client sends `Accept-Version: 0.1` after a contract bump; 30-day window enforced by the registry.
* Batch endpoint (PAP-304) routes each mutation through the same resolution.

Out: the middleware chain and error mapping (PAP-267), the client (PAP-268), REST exposure details (PAP-269), rate limits (PAP-304).

**Spec**

* One mount per contract; mounting a router directly from a module package fails lint R8.
* Resolution happens once per request in the kernel scope; a batch of 25 mutations resolves once.
* Unknown procedure for the selected implementation: 501 `NOT_IMPLEMENTED` with the impl name (staff) or 404 (customers).
* Response adapters are pure and tested with the old version's golden fixtures; they are removed by the swap CLI at step 7.
* Latency overhead under 0.2 ms per call (benchmarked).

**Interface contract**

Provides: `mountContract`, `routes.json`, `/api/v1/routes`, `defineResponseAdapter`, `Accept-Version` handling, `X-PaperOS-Contract-Version`. Consumes: PAP-267 Hono app and middleware, PAP-268 router conventions and `callAs`, kernel registry and scopes, contract packages' `routes.ts`, PAP-269 OpenAPI generation. Consumed by: every `Wire <module>` issue whose contract has routes, PAP-222 tenant API keys (stable public surface), the SDK, the swap CLI.

**Test plan**

* Unit: mount builds handlers for every procedure in the signature; missing procedure gives 501 or 404 by audience.
* Integration (compose): two implementations of `contract-tables` bound; `X-PaperOS-Impl` as staff switches the responder; as customer the header is ignored and audited.
* Adapters: `Accept-Version: 0.1` on a 0.2 contract returns the 0.1 shape validated against the 0.1 schema fixtures; after the window it returns 410 `GONE` with the ADR link.
* Benchmark: overhead budget; OpenAPI snapshot identical for both implementations.

**Definition of done**

* Gateway merged; `apps/api` mounts every existing router through it; `routes.json` committed; OpenAPI unchanged for clients; benchmarks green.
* `docs/platform/api.md` "Routing by contract" section; Linear comment.

**Edge cases**

* Contract router with streaming procedures (push transport): mounted with the same resolution; adapters not applied to streams.
* Implementation adds a procedure not in the contract: unreachable through the gateway; lint warns; the contract needs a minor bump.
* Two contracts declare the same router name: manifest validator `ROUTE_COLLISION` (PAP-264 already checks routes; extended to contract routers).
* Webhooks (`/api/webhooks/*`) and Better Auth routes: not contract routers; mounted as today, documented as exceptions.

**Dependencies**

Blocked by PAP-267, PAP-268, module-system/registry-di.

**Agent**

Built by Forge. Reviewed by Sentinel.

**Size**

M

**Demo**

Reviewer calls `views.list` as staff with `X-PaperOS-Impl: compiler-v2` and sees the header echoed and identical rows; calls again with `Accept-Version: 0.1` after a fixture bump and receives the adapted shape; opens `/api/v1/routes` and sees every procedure with its providers. Two minutes.
