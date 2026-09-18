---
identifier: "PAP-269"
title: "OpenAPI docs, health endpoints and staging deploy of apps/api"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: "PAP-35"
children: []
blockedBy: ["PAP-268"]
blocks: ["PAP-36", "PAP-39", "PAP-40", "PAP-119", "PAP-129", "PAP-163", "PAP-193", "PAP-222", "PAP-242", "PAP-311", "PAP-312", "PAP-335", "PAP-366", "PAP-431", "PAP-501", "PAP-546", "PAP-566", "PAP-684", "PAP-793"]
key: "child/PAP-35/14"
url: "https://linear.app/paperos/issue/PAP-269/openapi-docs-health-endpoints-and-staging-deploy-of-appsapi"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:28.067Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-269: OpenAPI docs, health endpoints and staging deploy of apps/api

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Serve OpenAPI 3.1 and a Scalar docs page, expose `/api/health` with database check and build SHA, lint the spec in CI and deploy `apps/api` to staging through PAP-26 so the typed client has a live target.

**Scope**

In: `/api/v1/openapi.json`, `/api/docs` (Scalar), `/api/health`, `redocly lint` in Gate 1, Coolify resource `paperos-staging-api`, `docs/data/api.md`.

Out: production hardening beyond PAP-26 defaults.

**Spec**

* OpenAPI generated from oRPC metadata; versioned path `/api/v1`; breaking changes need an ADR.
* Health returns `{ ok, db: 'ok'|'fail', version, sha }` and 503 on db failure.
* Docs page disabled in production unless `API_DOCS=1`.

**Interface contract**

Provides: `/api/docs`, `/api/v1/openapi.json`, `/api/health` for PAP-40 checks and PAP-26 smoke tests; staging base URL for the client. Consumes: children 1 and 2, PAP-26 pipeline, PAP-30 staging database.

**Definition of done**

* `/api/health` and `/api/docs` reachable over TLS on staging (screenshot of Scalar at 1280).
* `redocly lint` green; `docs/data/api.md` written; Linear comment with the docs URL.

**Test plan**

* Unit: health handler with db up and down.
* Static: `redocly lint`; OpenAPI snapshot for breaking-change detection.
* Integration: PAP-26 smoke test hits health after deploy.
* Visual: Scalar page at 1280 and 375.

**Demo**

Reviewer opens `https://staging.PAPEROS_DOMAIN/api/docs`, expands `users.me`, sends it with the dev token and tenant header from the Scalar console and reads the response. Under a minute.

**Edge cases**

* Database down: health 503, docs still render.
* Docs exposed in production by mistake: env guard test.

**Dependencies**

Children 1 and 2 (hard), PAP-26, PAP-30.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel.

**Size**

S
