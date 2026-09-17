---
identifier: "PAP-40"
title: "Wire OpenTelemetry tracing, slow-query logging and Grafana dashboards for API and sync"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-30", "PAP-35", "PAP-269"]
blocks: []
key: "data-layer/observability"
url: "https://linear.app/paperos/issue/PAP-40/wire-opentelemetry-tracing-slow-query-logging-and-grafana-dashboards"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:45.357Z"
---

# PAP-40: Wire OpenTelemetry tracing, slow-query logging and Grafana dashboards for API and sync

**Goal**

Make latency and errors visible per route, tenant and agent: OpenTelemetry traces from the web client through the API to Postgres, slow-query logging and Grafana dashboards on the VPS that reviewers and the release digest link to, so regressions are seen before customers report them.

**Scope**

In:

* Stack via Coolify (`ops/compose/observability.yml`): Grafana 11, Prometheus, Loki, Tempo, OTel Collector, `postgres_exporter` (PAP-30), `node_exporter`, cAdvisor; VPN-only until PAP-57 SSO.
* API: `@opentelemetry/sdk-node` 2.x auto-instrumentation plus an oRPC middleware span with `paperos.tenant_id`, `paperos.actor_kind`, `paperos.actor_id`, `paperos.procedure`, `paperos.request_id`, `linear.issue`.
* Web and Tauri: `sdk-trace-web` with fetch instrumentation, `traceparent` propagation, Web Vitals as metrics; 10 percent sampling in production, 100 percent on staging, always on error.
* Six dashboards provisioned from JSON; alerts for 5xx rate, p95 latency, slow queries, disk.
* Client error reports from the app-shell error-handling issue land in the same collector.

Out: business analytics (PAP-194), cost metering (PAP-99 consumes attributes).

**Spec**

* Env `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_TRACES_SAMPLER`, `OTEL_TRACES_SAMPLER_ARG` (PAP-17).
* Request id equals trace id where possible; API returns `x-request-id` and `traceparent`; error toasts show the short id.
* PII policy: no emails, names or bodies on spans; a span processor drops disallowed keys using `pii.json` (PAP-41) plus a static denylist.
* Retention: Tempo 7 days, Loki 14, Prometheus 30.
* k6 script `ops/observability/k6/api-smoke.js` (200 VUs, 5 min) on staging validates dashboards and alerts.
* Browser export via `/api/otel` proxy to defeat ad blockers.

**Interface contract**

Provides:

* Span attribute names above as the metering contract for PAP-99 and PAP-114.
* Headers `x-request-id`, `traceparent` on every API response (PAP-35 emits, this issue standardises).
* Endpoint `POST /api/otel` (OTLP/HTTP proxy) used by the web SDK and the client error-reporting issue.
* Grafana dashboards `api-overview`, `tenant-latency`, `postgres`, `sync`, `web-vitals`, `host`, provisioned from `ops/observability/dashboards/*.json`; alert routes to Linear via PAP-97 or email.
* Metrics `paperos_kiosk_*` scraped from PAP-23 health.

Consumes: API middleware hook (PAP-35), exporter (PAP-30), `pii.json` (PAP-41), env schema (PAP-17), SSO (PAP-57, soft).

**Definition of done**

* A trace from a web click to a Postgres query appears in Tempo with tenant attributes (screenshot).
* Six dashboards provisioned on a fresh Grafana with no manual clicks; screenshots at 1280 and 1920.
* Induced 5xx storm fires the alert and creates a Linear issue or email (evidence).
* Vitest: PII filter, request id propagation; k6 summary committed.
* Web Vitals from the Pages demo bucketed by breakpoint; `docs/ops/observability.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: span processor drops `user.email` and any key in `pii.json`; sampler keeps error spans at 0 percent ratio.
* Integration (CI compose with collector): a request through `apps/api` yields a trace with the expected attributes (assert via Tempo API).
* Load: k6 run on staging; dashboards populate; p95 panel matches k6 summary within 10 percent.
* Alerting: inject 5xx for 2 minutes with a feature toggle; alert fires; evidence saved.
* Visual: six dashboards at 1280 and 1920.

**Demo**

Reviewer clicks a button on staging, copies the request id from the toast footer, pastes it into Grafana Explore and follows the trace from browser span to SQL statement, then opens the tenant-latency dashboard. Under 2 minutes over the tailnet.

**Edge cases**

* Collector down: batch exporter drops on full queue, never blocks.
* High-cardinality metric labels forbidden; lint test.
* Clock skew: server receive time orders dashboards.
* Log disk pressure: Loki retention plus Docker log rotation.
* Rare errors under sampling: tail-based always-on-error in the collector.

**Dependencies**

PAP-35 (hard), PAP-30 (exporter, now encoded). Soft: PAP-41, PAP-57, PAP-97. Consumed by PAP-87, PAP-88, PAP-99, PAP-114, PAP-147.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Code Reviewer).

**Size**

M: compose stack, two SDK setups, six dashboards.
