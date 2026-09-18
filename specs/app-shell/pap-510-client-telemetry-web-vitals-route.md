---
identifier: "PAP-510"
title: "Client telemetry: web vitals, route timings, feature-usage events and a consent gate flowing into `/api/otel` with per-tenant dashboards and a `useTrack()` hook"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-17"]
blocks: []
key: "r4/app-shell/client-telemetry"
url: "https://linear.app/paperos/issue/PAP-510/client-telemetry-web-vitals-route-timings-feature-usage-events-and-a"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:55.552Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-510: Client telemetry: web vitals, route timings, feature-usage events and a consent gate flowing into `/api/otel` with per-tenant dashboards and a `useTrack()` hook

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

PAP-40 traces the API and sync, PAP-368 reports client errors, PAP-87 measures Lighthouse in CI and PAP-194 tracks acquisition; nobody measures what real users experience in the shell: LCP and INP per route, navigation timings, feature usage per audience. Linear, Arc and VS Code all ship this. Without it the vision agent judges screenshots while the product flies blind.

**Scope**

In:

* `packages/core/src/telemetry/`: `initTelemetry({ consent })`, `web-vitals` collection (LCP, INP, CLS, TTFB) per route id, TanStack Router navigation timings, `track(event, props)` and `useTrack()` for feature usage, batching to `POST /api/otel` (PAP-40 collector) as OTel logs with the PAP-40 PII denylist applied.
* Consent gate: `tenant.settings.telemetry` (`off|essential|full`) plus the user cookie consent from PAP-221; `essential` sends vitals only, anonymised; `full` includes feature events with `principal.id` hashed per tenant.
* Dashboards: Grafana `client-vitals.json` (p75 LCP and INP per route and breakpoint, PAP-14 names) and `feature-usage.json` (events per audience) provisioned by PAP-40 conventions; a `/settings/telemetry` staff toggle.
* Event catalogue `telemetry-events.yaml` (name, props schema, owner module) validated in CI; undeclared events fail typecheck through a generated `TrackEvent` union (PAP-366 pattern).

Out: acquisition and marketing attribution (PAP-194), error reporting (PAP-368), session replay, third-party analytics SDKs.

**Spec**

* Sampling: vitals 100 percent, navigation timings 10 percent, feature events 100 percent under `full`; configurable per tenant.
* Payload size under 2 KB per batch on average; flushed on `visibilitychange` and every 10 s; queued in IndexedDB offline (shared queue with PAP-368, capped 500).
* Route ids, not URLs, are recorded so record ids never leak; search params dropped.
* Desktop and mobile add `target` and app version; kiosk adds `display`.

**Interface contract**

Provides: `initTelemetry`, `track`, `useTrack`, `TrackEvent` union, `telemetry-events.yaml`, dashboards, `/settings/telemetry`; consumed by PAP-194 (funnel events via the same catalogue), PAP-87 (field data beside lab data), PAP-88 digests, PAP-113 (agent console usage), PAP-84 (route-level regressions).

Consumes: collector and denylist (PAP-40), router (PAP-16), consent records (PAP-221, soft), tenant settings (PAP-58), breakpoint names (PAP-14), flags (PAP-366, soft).

**Definition of done**

* Navigating three routes on the preview produces vitals rows in Grafana within a minute (screenshot); `essential` mode sends no `principal` field (assertion).
* `TrackEvent` typecheck fails on an undeclared event; offline queue flushes on reconnect (Playwright).
* Dashboards committed; `docs/platform/telemetry.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: consent matrix (tenant × user) to fields sent; batching and flush triggers; denylist scrub; catalogue validation.
* E2E: Playwright toggles consent, navigates, asserts request payloads; offline queue.

**Demo**

Reviewer opens `/settings/telemetry`, sets `full`, navigates the dashboard and grid, then opens the Grafana client-vitals board and sees p75 INP per route for the demo tenant. Under 2 minutes.

**Edge cases**

* Ad blocker blocks `/api/otel`: silent failure, no retries storm (max 3 then drop).
* Very long session (kiosk, 24 h): route timing buffer bounded; periodic flush.
* Tenant switches consent to `off`: queue cleared immediately, no further sends.

**Dependencies**

Hard: PAP-16, PAP-17. Soft: PAP-40 (console and OTLP-file exporter until the collector and dashboards land; the dashboards ship when PAP-40 is In Review), PAP-221, PAP-58, PAP-366, PAP-368 (shared queue). Feeds PAP-194, PAP-87, PAP-88.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
