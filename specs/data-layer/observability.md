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
blockedBy: ["PAP-269", "PAP-30", "PAP-35"]
blocks: []
key: "data-layer/observability"
url: "https://linear.app/paperos/issue/PAP-40/wire-opentelemetry-tracing-slow-query-logging-and-grafana-dashboards"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-40: Wire OpenTelemetry tracing, slow-query logging and Grafana dashboards for API and sync

**Goal**

Make latency and errors visible per route, per tenant and per agent: OpenTelemetry traces from the web client through the API to Postgres, slow-query logging, and Grafana dashboards on the VPS that reviewers and the release digest can link to, so performance regressions are seen before customers report them.

**Scope**

In:
- Observability stack via Coolify (`ops/compose/observability.yml`): Grafana 11, Prometheus, Loki, Tempo, OpenTelemetry Collector (OTLP gRPC/HTTP), `postgres_exporter` (from `data-layer/postgres-provision`), `node_exporter`, cAdvisor; all behind Caddy with Better Auth SSO or Grafana OAuth when `identity/better-auth` lands, VPN-only until then.
- API instrumentation: `@opentelemetry/sdk-node` 2.x with auto-instrumentations for HTTP, `pg`/postgres.js, `undici`; oRPC middleware creating a span per procedure with attributes `paperos.tenant_id`, `paperos.actor_kind`, `paperos.actor_id`, `paperos.procedure`, `paperos.request_id`, `linear.issue` when supplied by agents.
- Web/Tauri instrumentation: `@opentelemetry/sdk-trace-web` with fetch instrumentation and `traceparent` propagation to the API; Web Vitals (LCP, INP, CLS) exported as metrics; sampled 10 percent in prod, 100 percent in staging.
- Postgres: `log_min_duration_statement = 500ms`, `auto_explain` for over 2 s, `pg_stat_statements` dashboard, logs shipped to Loki via `promtail`.
- Sync and realtime: Electric and Hocuspocus metrics scraped (`realtime/yjs-server` exposes them).
- Dashboards as code in `ops/observability/dashboards/*.json`: API overview (RPS, p50/p95/p99, error rate by procedure), Tenant view (top tenants by latency/errors), Agent view (requests and errors per `actor_id` of kind agent), Postgres (connections, slow queries, replication lag, disk), Sync (shape latency, outbox failures), Web Vitals by breakpoint bucket.
- Alerts: error rate over 2 percent for 5 min, p95 over 1 s, disk over 80 percent, backup age over 26 h, replication slot lag over 1 GB; routed to a Linear issue via `pm-linear/webhooks` (or email until then).

Out: SLO contracts, paid APM, RUM session replay (`quality/video-replays` covers test replays), log-based billing.

**Spec**

- Env: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_TRACES_SAMPLER=parentbased_traceidratio`, `OTEL_TRACES_SAMPLER_ARG` per env (`app-shell/env-config`).
- Request id equals trace id where possible; API returns `x-request-id` and `traceparent` headers; error toasts show the short id for support.
- PII policy: never attach emails, names or payload bodies to spans; tenant and actor ids only; enforced by a span processor that drops disallowed attribute keys and a test.
- Retention: Tempo 7 days, Loki 14 days, Prometheus 30 days on the 8 GB box; documented sizing.
- Load profile: run the `load` seed plus a k6 script `ops/observability/k6/api-smoke.js` (200 VUs, 5 min) on staging to validate dashboards populate and alerts fire under induced errors.

**Definition of done**

- A trace from a click in the web app to a Postgres query appears in Tempo with tenant attributes (screenshot).
- All six dashboards provisioned from JSON on a fresh Grafana (no manual clicks); screenshots at 1280 and 1920.
- Induced 5xx storm fires the error alert and creates a Linear issue or email (evidence attached).
- Vitest: PII attribute filter, request id propagation; k6 run summary committed.
- Web Vitals from the Pages demo visible bucketed by breakpoint.
- `docs/ops/observability.md`; CHANGELOG; Linear comment with Grafana links (VPN note).

**Edge cases**

- Collector down: SDK must not block requests; batch exporter with drop-on-full queue.
- High-cardinality attributes (request id as a metric label): forbidden in metrics, allowed in traces; lint test.
- Ad blockers blocking browser OTLP export: send via API proxy path `/api/otel` instead.
- Clock skew between VPS and clients: spans use server-received time for ordering in dashboards.
- Disk pressure from logs: Loki retention plus Docker log rotation.
- Sampling hiding rare errors: always sample when span has error status (tail-based via collector).

**Dependencies**

`data-layer/api-layer` (hard), `data-layer/postgres-provision` (exporter). Consumed by `quality/perf-budgets`, `quality/release-train` (digest links), `realtime/load-test`, `pm-linear/credit-metering` (agent attribution), `agents/cost-controls`.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Code Reviewer; Security Auditor for PII policy and access).

**Size**

M: mostly configuration and dashboards as code, plus a load run to prove them.
