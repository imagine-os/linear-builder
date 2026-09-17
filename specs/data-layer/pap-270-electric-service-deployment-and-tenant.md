---
identifier: "PAP-270"
title: "Electric service deployment and tenant-scoped shape proxy (/api/sync/shape)"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: "PAP-36"
children: []
blockedBy: ["PAP-30", "PAP-34", "PAP-267"]
blocks: ["PAP-271"]
key: "child/PAP-36/15"
url: "https://linear.app/paperos/issue/PAP-270/electric-service-deployment-and-tenant-scoped-shape-proxy-apisyncshape"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:12.556Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-270: Electric service deployment and tenant-scoped shape proxy (/api/sync/shape)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deploy the ElectricSQL sync service on staging connected directly to Postgres with the `electric` role, and add the `GET /api/sync/shape` proxy in `apps/api` that validates the session and injects `tenant_id = <principal tenant>` into every shape so clients can never request another tenant's rows.

**Scope**

In: `ops/compose/electric.yml` and Coolify resource; publication `electric_pub`; proxy route with table allowlist from the shape registry; streamed responses; `SHAPE_FORBIDDEN` error; health from `/api/health`.

Out: client (child 2), outbox (child 3).

**Spec**

* Proxy forwards `table`, `offset`, `handle`, `live`, `columns`; appends the server `where`; strips client-supplied `where`.
* Non-registered table: 403 `SHAPE_FORBIDDEN`.
* Response streamed with Electric headers preserved; `x-sync-schema-hash` added.

**Interface contract**

Provides: route and error, registry lookup `getShapeDefinition(table)`, env `ELECTRIC_URL`. Consumes: publication and role (PAP-30; PAP-42 locally), API chain (PAP-35 child 1), RLS semantics (PAP-34).

**Definition of done**

* Electric on staging; health green.
* Cross-tenant shape request returns 403 (test); allowed shape streams rows for the caller's tenant only.
* `docs/data/sync.md` proxy section written.

**Test plan**

* Unit: query rewriting (client `where` stripped, tenant appended); allowlist.
* Integration (CI compose with Electric): stream a `workspaces` shape as tenant A and assert no tenant B rows; `live=true` long-poll returns a change within 2 s.
* Security: Sentinel reviews that the proxy never trusts client tenant hints.

**Demo**

Reviewer runs `curl -N "$API/api/sync/shape?table=workspaces&offset=-1" -H "x-tenant: acme" -H "authorization: Bearer $TOKEN"` and watches rows stream, then requests `table=users_secret` and gets 403. Under a minute.

**Edge cases**

* Electric restart invalidates handles: client receives 409 and re-fetches (child 2).
* Slot lag: alert via PAP-40 when replication lag exceeds 30 s.

**Dependencies**

PAP-35 child 1, PAP-30 or PAP-42, PAP-34 (hard). Blocks children 2 and 3.

**Agent**

Built by Forge (Ops Runner and Platform Engineer). Reviewed by Sentinel (Security Auditor).

**Size**

M
