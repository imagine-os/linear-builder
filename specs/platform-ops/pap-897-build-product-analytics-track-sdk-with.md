---
identifier: "PAP-897"
title: "Build product analytics: track() SDK with an event schema registry, consent-aware first-party pipeline reusing the attribution collector, funnels, retention and feature adoption datasets, tenant-facing analytics for their own customers"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Product analytics, experiments and abuse controls"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-173", "PAP-187", "PAP-194", "PAP-291", "PAP-303", "PAP-355", "PAP-387", "PAP-556", "PAP-561", "PAP-791", "PAP-893"]
blocks: ["PAP-898", "PAP-899", "PAP-901", "PAP-907"]
key: "r4/platform-ops/product-analytics"
url: "https://linear.app/paperos/issue/PAP-897/build-product-analytics-track-sdk-with-an-event-schema-registry"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:24.416Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-897: Build product analytics: track() SDK with an event schema registry, consent-aware first-party pipeline reusing the attribution collector, funnels, retention and feature adoption datasets, tenant-facing analytics for their own customers

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Know what people do in the product without a third-party tracker: a `track(event, props)` SDK for web and Tauri with a schema registry so events are typed and reviewed, a consent-aware first-party pipeline that extends the PAP-194 collector, monthly-partitioned `product_events`, and funnels, retention cohorts and feature adoption as datasets and dashboard blocks, at two levels: PaperOS about its tenants, and each tenant about its own customers in the portal.

**Scope**

In: `packages/analytics`: `defineEvent(name, schema)` registry (`events.yaml` generated, reviewed in PR like topics), `track`, `identify` (principal hash, never email), `page` (route spec key), `group` (tenant); client batching under 4 KB gzipped extra over PAP-194's SDK; server-side `track` for API and jobs; automatic events from the command registry telemetry (PAP-291) and page specs (`page.viewed`, `state.shown`). Pipeline: `POST /api/v1/public/collect` extended (PAP-194) → outbox → `product_events(tenant_id, actor_hash, event, props jsonb, ts, session_id, source)` partitioned monthly; consent modes from PAP-194 and PAP-187 (GPC, DNT, tenant consent mode) enforced at the edge; `pii` lint on props schemas (PAP-355). Datasets and blocks: `funnels` (defined in `funnels.yaml` or in-app: ordered steps with windows), `retention_cohorts` (weekly), `feature_adoption` (per command and page), `active_users`; PAP-173 blocks; tenant scope selectable: platform (all tenants, platform audience) or tenant (their customers). Tenant-facing: `/console/analytics` showing their customers' portal behaviour (bookings funnel, order funnel) built from the same events with the tenant as `group`; portal consent banner integration.

Out: Session replay (next issue). Ad-platform conversion APIs. Data warehouse export (PAP-205 archive gains events in v0.3).

**Spec**

* No event ships without a schema entry; unknown events are dropped at the edge and counted; props are validated and PII-linted in CI
* Actor identity is a per-tenant salted hash of the principal id; anonymous visitors use the PAP-194 first-party cookie; identify stitches with `attr_identity`
* Retention: raw events 13 months, rollups indefinitely (PAP-355 rules); tenants can shorten
* Query performance: funnels and retention computed by SQL over partitions with daily rollups; p95 under 2 s for 90 days on the demo volume (PAP-242 budget)
* Consent off means nothing is stored, not stored-and-hidden; the SDK returns immediately

**Interface contract**

Provides: `AnalyticsPort` default adapter, `packages/analytics` SDK and registry, `product_events` and rollup datasets, funnel and retention blocks, `/console/analytics`, `analytics.event` envelope. Consumes: attribution collector and consent (PAP-194), consent centre (PAP-187), event bus (PAP-303), PII annotations and retention (PAP-355), dashboards (PAP-173), command telemetry (PAP-291), page specs (PAP-114), performance budgets (PAP-242). Consumed by: PAP-898, PAP-899, PAP-901, growth segments (behavioural attributes, PAP-195), engagement announcements (v0.3 behavioural targeting), assistant (usage questions).

**Definition of done**

* 20 platform events and 10 portal events defined and flowing on staging; onboarding funnel and weekly retention render for the platform audience; a demo tenant sees its booking funnel; consent off proven to store nothing; PII lint catches a fixture
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schema validation and drop; hashing; consent gating; funnel SQL over fixtures.
* Integration: SDK batch → collector → partition; rollup job; tenant scoping in datasets (RLS).
* E2E: portal consent banner off → no events; on → events; console analytics renders.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Walk a new user through onboarding on staging, then open the platform onboarding funnel and see the drop-off step; switch to the demo tenant and show their booking funnel from the portal.

**Edge cases**

* Clock-skewed client timestamps: server time wins for partitioning; client time kept in props for ordering within a session
* Event schema changed incompatibly: new version name (`event.v2`) required; the lint blocks in-place changes
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-194 (hard: collector and consent), PAP-303, PAP-355 (hard), PAP-173, PAP-291 (soft), PAP-187 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/platform-ops/experiments` = PAP-899, `r4/platform-ops/session-replay` = PAP-898, `r4/platform-ops/tenant-health-scores` = PAP-901.
