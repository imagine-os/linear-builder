---
identifier: "PAP-435"
title: "Build the feature-flag swap mechanism: `module.<id>.impl` variant flags, per-tenant selection, shadow-run diffs and kill-switch rollback"
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
blockedBy: ["PAP-434", "PAP-537", "PAP-541"]
blocks: ["PAP-442", "PAP-453", "PAP-454", "PAP-455", "PAP-458", "PAP-461", "PAP-464", "PAP-471", "PAP-472", "PAP-473", "PAP-480", "PAP-481", "PAP-482", "PAP-489", "PAP-490", "PAP-491", "PAP-496", "PAP-497", "PAP-538", "PAP-539", "PAP-549", "PAP-846", "PAP-861", "PAP-876", "PAP-892", "PAP-899", "PAP-907"]
key: "module-system/flag-swap"
url: "https://linear.app/paperos/issue/PAP-435/build-the-feature-flag-swap-mechanism-moduleidimpl-variant-flags-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:39.586Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-435: Build the feature-flag swap mechanism: `module.<id>.impl` variant flags, per-tenant selection, shadow-run diffs and kill-switch rollback

**Model / Effort:** Sonnet 5 / high

**Goal**

Turn the kernel's side-by-side bindings into a swap you can operate: a reserved variant flag family `module.<id>.impl` evaluated per request through PAP-366, so an implementation can be turned on for one tenant, shadowed against the current one with diffs recorded, promoted to default, and rolled back with the kill switch in under five seconds without a deploy (`docs/module-system.md` section 4 row 2 and section 6 steps 2 to 6).

**Scope**

In:

* Kernel selection hook: `kernel.select(token, scope)` reads `useVariant('module.<id>.impl')` from the request scope; falls back to `default` when the flag is missing or the flag service is down.
* Reserved flag declarations generated into `flags.yaml` from manifests (one variant flag per module, values are the bound `impl` names); undeclared `impl` values fail flag validation.
* `shadow` binding option: run secondary after primary for read ports, sample rate, `swap_shadow_diff` table (`tenant_id`, `module_id`, `port`, `case_id`, `request_id`, `primary_hash`, `secondary_hash`, `diff jsonb`, `latency_primary_ms`, `latency_secondary_ms`), retention 14 days.
* `X-PaperOS-Impl` request header (staff and agents only, PAP-59 `can('module:impl:force')`) and response header; data attribute on slot fills.
* `/settings/modules` staff page: per module the bound impls, current default, tenant overrides, shadow toggle, diff count, kill switch; audit events on every change.
* `paperos module status <id>` CLI reading the same data.

Out: the swap CLI's step gating (own issue), data migration adapters (own issue), any real second implementation.

**Spec**

* Evaluation order per PAP-366: kill switch, tenant rule, audience rule, segment rule, default; kill switch always resolves `default`.
* Selection is decided once per request scope and reused for every resolve in that scope (no mixed impls within one request).
* Shadow never changes the response, never blocks it beyond 5 ms of scheduling, and is disabled automatically when the diff table exceeds 100k rows for a module.
* Diff is computed on the JSON of the port result after the conformance runner's normalisation (ids, timestamps) so shadow diffs and conformance cases speak the same language (`caseId` when derivable).
* Flip propagation to all clients under 5 s, measured, as PAP-366 guarantees.

**Interface contract**

Provides: `kernel.select`, `shadow` binding option, `swap_shadow_diff` table and `modules.shadowDiffs` procedure, `X-PaperOS-Impl`, `/settings/modules`, `paperos module status`, generated `module.*.impl` flags. Consumes: kernel registry, PAP-366 flags (`useVariant`, kill switch, rules), PAP-59 `can`, PAP-38 audit, PAP-267 middleware for headers, PAP-33 tables. Consumed by: every `Wire <module>` issue, the swap CLI, the shell swap drill, PAP-88 release train (canary steps).

**Test plan**

* Unit: selection order table; missing flag and flag-service-down both yield `default`; header override denied for customers.
* Integration (compose): two tenants, two impls, 200 concurrent requests, each response header matches its tenant's rule; kill switch flips both to `default` within 5 s (measured in the test).
* Shadow: a deliberately different secondary produces diffs with the right case ids; an identical one produces none; auto-disable at the row cap.
* E2E: Playwright on `/settings/modules` flips a module for the demo tenant and asserts the data attribute changes on a slot fill; screenshots at four widths.

**Definition of done**

* Mechanism merged; propagation timing recording attached; settings page screenshots; audit events present.
* `docs/platform/modules.md` "Operating a swap" section; Linear comment with the recording.

**Edge cases**

* Impl bound in code but flag value not yet deployed: selection falls back to `default` and logs once per boot.
* Tenant override to an impl that was later unbound: evaluator treats it as `default` and opens a Needs Justin-free warning on the settings page.
* Shadow on a write port: refused at bind time (`SHADOW_WRITE_PORT`); writes are swapped only by the CLI's canary step.
* Offline client (PAP-148): last known impl snapshot used, never `next` by default.

**Dependencies**

Blocked by module-system/registry-di, PAP-366.

*Round 4 (2026-09-18): PAP-366 soft: runtime feature flags (09-29) land after the contracts milestone (09-27); until it lands, PAP-435 selects* `module.<id>.impl` *variants through the config port (PAP-444) and env; move selection onto PAP-366 flags with per-tenant targeting when they land. The* `blocks` *relation PAP-366 -> PAP-435 was removed.*

**Agent**

Built by Forge. Reviewed by Sentinel.

**Size**

M

**Demo**

Reviewer opens `/settings/modules`, sets `tables` to `compiler-v2` for the Acme tenant with shadow on, loads a CRM view as Acme and sees `X-PaperOS-Impl: compiler-v2` and zero diffs; hits Kill and the header returns to `default` within five seconds. Ninety seconds.

*Round 4 critique fix (2026-09-18):* PAP-366 appears in the Hard list above and in a round-4 soft note; it is soft (no `blocks` relation). Read the Hard list without it.

*Round 4 critique fix (2026-09-18):* PAP-538 was split out as a follow-on issue (FIX-R4-1); this issue is a leaf again with its Model / Effort labels and estimate restored, and it blocks PAP-538.
