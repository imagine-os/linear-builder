---
identifier: "PAP-901"
title: "Build tenant health scores and ops dashboards: activation, usage, errors, sync lag, storage, billing state and NPS per tenant, alerts to platform staff, churn-risk segment feeding growth"
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
blockedBy: ["PAP-195", "PAP-328", "PAP-368", "PAP-391", "PAP-894", "PAP-897"]
blocks: []
key: "r4/platform-ops/tenant-health-scores"
url: "https://linear.app/paperos/issue/PAP-901/build-tenant-health-scores-and-ops-dashboards-activation-usage-errors"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:06.493Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-901: Build tenant health scores and ops dashboards: activation, usage, errors, sync lag, storage, billing state and NPS per tenant, alerts to platform staff, churn-risk segment feeding growth

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

See which tenants are thriving and which are about to leave: a nightly health score per tenant from activation milestones, active users, feature adoption, error rate, sync lag, storage growth, billing state and NPS when present, explained by factor, shown in `/admin` and as dashboard blocks, with alerts to platform staff on drops and a `churn-risk` segment (PAP-195) so growth sequences can act.

**Scope**

In: `tenant_health` (date, score 0 to 100, factors jsonb, trend) computed by a PAP-43 nightly job from: onboarding steps (PAP-367), `active_users` and `feature_adoption` (analytics), error rate (PAP-368), sync lag (PAP-328), storage and seats (PAP-391, PAP-432 counters), billing state (PAP-177), NPS (engagement, soft); weights in `health.yaml` with an ADR. `/admin` tenant grid column and detail tab with factor breakdown and 90-day trend; platform dashboard blocks (distribution, movers); alerts kind `health.dropped` when a tenant falls 15 points in a week. Segment source: `segments` rule attribute `tenant.healthScore` for the platform CRM (PAP-195); `health.score.changed` event.

Out: Predictive churn models (v0.3). Tenant-facing health (tenants see their own analytics, not the platform's score).

**Spec**

* Scores are explainable and reproducible: the job stores inputs alongside the score; a weight change recomputes history with a version marker
* Missing signals (module disabled) are excluded and weights renormalised, never treated as zero
* Only the platform audience reads `tenant_health`; RLS denies tenants

**Interface contract**

Provides: `HealthPort` default adapter, `tenant_health` dataset, `health.yaml`, admin column and tab, blocks, alert kind, segment attribute, `health.score.changed` event. Consumes: super-admin console, analytics datasets, usage (PAP-391), errors (PAP-368), sync lag (PAP-328), onboarding progress (PAP-367), billing state (PAP-177), segments (PAP-195), NPS (soft). Consumed by: growth (churn-risk sequences), PAP-89 digest (health section), business-core (billing page context for support).

**Definition of done**

* Scores for all staging tenants nightly with factor breakdowns; a fixture drop triggers the alert and the segment membership; trend renders
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: weighting and renormalisation; trend and drop detection.
* Integration: nightly job idempotency; RLS denial for tenant principals; segment attribute evaluation.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Open `/admin`, sort tenants by health, open the lowest, read the factor breakdown (no logins in 14 days, sync lag), and show it appearing in the churn-risk segment.

**Edge cases**

* Brand-new tenant (under 7 days): score shown as "activating" with milestone progress instead of a number
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-894 and PAP-897 (hard), PAP-391, PAP-368, PAP-328 (soft: factors degrade), PAP-195 (soft).

**Agent**

Builder: Forge. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/platform-ops/product-analytics` = PAP-897, `r4/platform-ops/superadmin-console` = PAP-894.
