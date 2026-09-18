---
identifier: "PAP-909"
title: "Add CDN and edge caching for public assets, public views and embeds, and signed file downloads, with cache keys, purge on change and a provider decision (Caddy cache versus Bunny or Cloudflare)"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Infra"
priority: 4
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-26", "PAP-37", "PAP-87", "PAP-172", "PAP-431", "PAP-624"]
blocks: []
key: "r4/data-layer/cdn-edge-cache"
url: "https://linear.app/paperos/issue/PAP-909/add-cdn-and-edge-caching-for-public-assets-public-views-and-embeds-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:26.667Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-909: Add CDN and edge caching for public assets, public views and embeds, and signed file downloads, with cache keys, purge on change and a provider decision (Caddy cache versus Bunny or Cloudflare)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Make public pages fast everywhere and stop MinIO from serving the same image ten thousand times: an ADR choosing between Caddy's cache module on the VPS and a CDN in front (Bunny or Cloudflare) for static bundles, public view and form pages, help center and status pages, and signed file downloads, with cache keys that respect tenant hosts, purge hooks on publish and a per-PR budget check.

**Scope**

In: ADR with measurements from a PAP-87 Lighthouse run from three regions; chosen provider configured as code in `paperos-infra` (PAP-25) with custom-domain support matching PAP-431 (on-demand TLS must still work). Cache rules: immutable hashed bundles (1 year), public pages (60 s stale-while-revalidate), file variants (signed URLs with cache-friendly signatures scoped by tenant, 1 h), never for authenticated API responses; purge hook `cache.purge(paths)` called by publish events (views PAP-172, help center, status page). Observability: hit ratio and origin egress in PAP-40 dashboards.

Out: Edge compute. Image optimisation at the edge (variants exist in PAP-37).

**Spec**

* Signed download URLs include the variant and tenant in the path so the cache never serves one tenant's file under another host
* Purge is idempotent and asynchronous; publish flows do not wait on it
* Fallback: if the CDN is down, DNS failover to origin is documented in the runbook

**Interface contract**

Provides: the ADR, provider config as code, cache rules, `cache.purge`, dashboards. Consumes: files and variants (PAP-37), deploy pipeline (PAP-26), public tokens (PAP-172), performance budgets (PAP-87), custom domains (PAP-431), infra repo (PAP-25), observability (PAP-40). Consumed by: app-shell static deploys, engagement help center and booking pages, workflows public forms, platform-ops status and trust pages.

**Definition of done**

* Public demo page LCP under 1.5 s from EU and US test locations; hit ratio dashboard live; purge proven on a view republish; custom domain still issues TLS
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Integration: cache headers per rule; purge; cross-tenant signed URL isolation.
* Perf: PAP-87 runs before and after.

**Demo**

Load the demo public view from two regions before and after, show the LCP drop and the cache hit ratio, then republish the view and see the purge.

**Edge cases**

* Tenant custom domain behind the CDN needs its own certificate path: documented per provider; the domain wizard (PAP-431) shows provider-specific CNAME instructions

**Dependencies**

PAP-37, PAP-26, PAP-431 (hard), PAP-172, PAP-87, PAP-40 (soft).

**Agent**

Builder: Forge. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
