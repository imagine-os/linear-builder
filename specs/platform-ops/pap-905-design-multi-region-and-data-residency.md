---
identifier: "PAP-905"
title: "Design multi-region and data residency: region per tenant, EU region stack, host and API routing, per-region backups, residency in the business profile and provisioning plan, as an ADR with a runbook"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Spec"
priority: 4
surfaces: ["Developer"]
milestone: "Compliance evidence, residency and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-26", "PAP-126", "PAP-270", "PAP-354", "PAP-431", "PAP-563"]
blocks: []
key: "r4/platform-ops/data-residency"
url: "https://linear.app/paperos/issue/PAP-905/design-multi-region-and-data-residency-region-per-tenant-eu-region"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:14.285Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-905: Design multi-region and data residency: region per tenant, EU region stack, host and API routing, per-region backups, residency in the business profile and provisioning plan, as an ADR with a runbook

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Decide how PaperOS will keep EU (and later other) tenants' data in region before a customer asks: an ADR choosing region-per-tenant on independent stacks (Postgres, MinIO, Hocuspocus, Electric, jobs) over a shared control plane, how a tenant's region is chosen (PAP-126 business profile and onboarding) and never changed without a migration job, how hosts and the API route by tenant region (Caddy and the PAP-431 host resolution), what is global (identity directory, billing on Stripe, Linear, the platform admin), per-region backups and DR (PAP-354), and a provisioning runbook and cost table for the first EU region.

**Scope**

In: `docs/adr/NNNN-data-residency.md`: options (single region, region-per-tenant, cell architecture), decision, consequences; `docs/platform/regions.md` with the routing design (`tenant.region` column, region-aware `PAPEROS_REGION` in PAP-17 config, Caddy per region, a global router that redirects by tenant host or session), the global versus regional data inventory, and the cross-region rules (no cross-region joins; global services hold only pointers). Business profile: `business.residency: eu|us|uk` in `app.spec.yaml` (PAP-126) and the onboarding question; `ResidencyPort.regionFor(tenant)` and `route(request)` interfaces in the contract with a single-region default implementation. Provisioning plan: Coolify project per region on a Hetzner EU location (PAP-25 pattern), compose files parametrised by region, secrets per region (PAP-300 broker scopes), backups to an in-region bucket (PAP-354), DR drill per region; cost table; migration procedure for moving a tenant (export PAP-205 → import PAP-422 → cutover with a freeze window).

Out: Running the second region (Needs Justin decision with the cost table). Active-active replication.

**Spec**

* Residency is a property of the tenant set at creation; changing it is a supervised migration, never a flag flip
* Global services never store tenant business data: identity holds accounts and tenant pointers; Stripe holds billing; Linear holds work; everything else is regional
* Every regional stack runs the same images and migrations; the compat matrix (PAP-440) and release train (PAP-254) deploy regions sequentially with a per-region status component
* Backups never leave their region; the DR drill restores in-region; the platform admin console shows region per tenant

**Interface contract**

Provides: the residency ADR, `regions.md` design, `ResidencyPort` interface with a single-region adapter, business profile field, provisioning runbook and cost table. Consumes: VPS and deploy pipeline (PAP-25, PAP-26), DR (PAP-354), host resolution (PAP-431), business profile (PAP-126), Electric deployment (PAP-270), config layer (PAP-17), credential broker (PAP-300), export and import (PAP-205, PAP-422). Consumed by: app-shell config, data-layer deployments, platform admin console (region column), onboarding wizard, compliance profiles (gdpr recommends eu).

**Definition of done**

* ADR merged and approved by Atlas; `ResidencyPort` in the contract with the single-region adapter passing conformance; cost table and runbook filed to Needs Justin as an informational decision for when the first EU tenant asks
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: contract interfaces and fixtures; business profile schema change validated.
* Review: Forge and Sentinel review the global/regional inventory against the data model (PAP-33) for any leak of tenant data into global tables.

**Demo**

Walk the design diagram: a UK clinic's request hitting the global router, redirected to the EU stack, its backups in Falkenstein, while its Stripe billing and Linear issues stay global.

**Edge cases**

* Tenant with staff in two regions: the tenant lives in one region; users are global; latency for the far staff is accepted and documented
* Shared demo tenant used by golden-path tests: pinned to the primary region

**Dependencies**

PAP-25, PAP-26, PAP-354, PAP-431 (hard: designs being extended), PAP-126, PAP-270, PAP-17, PAP-300 (soft).

**Agent**

Builder: Forge. Reviewer: Atlas (Merger).

**Size**

M: one session.
