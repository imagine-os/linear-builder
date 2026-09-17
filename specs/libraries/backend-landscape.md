---
identifier: "PAP-214"
title: "Survey backend building blocks (Better Auth, Drizzle, Electric, Hocuspocus, Inngest, Resend) and recommend"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-209"]
blocks: ["PAP-43"]
key: "libraries/backend-landscape"
url: "https://linear.app/paperos/issue/PAP-214/survey-backend-building-blocks-better-auth-drizzle-electric-hocuspocus"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-214: Survey backend building blocks (Better Auth, Drizzle, Electric, Hocuspocus, Inngest, Resend) and recommend

**Goal**

Settle the server-side building blocks the plan has not yet decided, confirm the ones it has, and record everything as ADRs so Forge, Nova and Ledger stop making independent choices: job queue, transactional email, PDF generation, search engine, observability stack, feature flags and object storage are open; auth, ORM, sync, realtime and API layer have owning research issues and are confirmed here by cross-link only. Every choice must self-host in Docker on the Coolify VPS.

**Scope**

In:
- Open decisions with candidates: jobs and workflows (Inngest self-hosted, Trigger.dev self-hosted, BullMQ with Redis, pg-boss, Graphile Worker); email (Resend, Postmark, Amazon SES via Nodemailer, self-hosted Postal); PDF (Playwright print to PDF, `@react-pdf/renderer`, Typst); search (Postgres `tsvector` + pgvector, ParadeDB `pg_search`, Meilisearch, Typesense); observability (OpenTelemetry collector with Grafana LGTM, SigNoz, HyperDX); feature flags (Unleash, Flagsmith, own table plus `identity/rbac-abac` policies); storage (MinIO, Garage, SeaweedFS); validation (Zod 4 confirmed vs Valibot, ArkType); runtime (Node 22 LTS vs Bun for the API).
- Confirmations by cross-link: Better Auth (`identity/auth-research`), Drizzle (`data-layer/drizzle-schema`), ElectricSQL (`data-layer/sync-research`), Hocuspocus (`realtime/realtime-research`), oRPC (`data-layer/api-layer`).
- Resource budget table: RAM and CPU footprint of each service measured in Docker on a 16 GB profile, since everything shares one VPS.
- ADRs for each open decision (may be one ADR with sections per decision if Atlas prefers) and registry entries.

Out: implementing any of them (owned by `data-layer/*`, `collab/notifications`, `business-core/invoicing`, `data-layer/search`, `data-layer/observability`), payroll and social APIs (own research issues).

**Spec**

- Time-box 1.5 agent-days; each decision at most 90 minutes; measure with `docker stats` after a 5-minute warm-up under a scripted load of 50 req/s where applicable.
- Rubric extras: self-host maturity and docs, Postgres-native (fewer moving parts wins), memory footprint, TypeScript SDK quality, local dev story (`docker compose up` in `ops/compose/`), multi-tenant isolation, exit cost.
- Constraints: total added RAM for chosen services under 6 GB; Redis is acceptable only if two or more chosen services need it; anything requiring Kubernetes is rejected.
- Deliverable `ops/compose/candidates/` with one compose file per candidate used for measurement, deleted or moved to `spikes/` on merge.
- Each ADR names the consuming issue, the exact package or image tag, env vars to add to `app-shell/env-config`, and the fallback candidate with migration hours.
- Email ADR must cover deliverability (DKIM, SPF, DMARC setup) and sandbox mode for agent sessions (`email:send (sandbox until approved)` per Beacon's access scope).
- Search ADR must consider `data-layer/search`'s plan for `tsvector` + pgvector as the baseline and justify any extra service.

**Definition of done**

- ADRs accepted for jobs, email, PDF, search, observability, feature flags, storage, validation and runtime; Forge and Atlas approval comments.
- Resource budget table committed with measured numbers and the total under budget.
- Compose files for the winners merged into `ops/compose/` (others removed), each starting cleanly with `docker compose up` in CI on a Forgejo runner (`forge/actions-runner`) or GitHub.
- Registry entries drafted; license check from `libraries/license-policy` passes on all chosen images and packages.
- Consuming issue descriptions updated with the decisions (comments on each).
- CHANGELOG entry; Linear comment with the summary table.

**Edge cases**

- Candidate is open source but self-hosting is undocumented or license-gated (Trigger.dev, Inngest tiers): score self-host path only and verify the license tier.
- Service needs Redis or ClickHouse (SigNoz): count the extra footprint against the 6 GB budget.
- Bun incompatibility with a chosen library (Tauri sidecars, native modules): runtime decision defaults to Node 22.
- PDF rendering needs fonts and CJK support: test with a sample invoice containing CJK and RTL text.
- Email provider blocks sending from unverified domains in test: use sandbox mode and document the verification steps as a Justin task.
- Feature flag needs are covered by page-spec access rules: record "no new service" as a valid decision.

**Dependencies**

`libraries/eval-rubric` (hard; use the draft if unmerged). Soft: `identity/auth-research`, `data-layer/sync-research`, `realtime/realtime-research` (link both ways, do not duplicate). Informs `data-layer/search`, `data-layer/observability`, `data-layer/file-storage`, `collab/notifications`, `business-core/invoicing`, `growth/outreach-sequences`.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner) running the Docker measurements. Reviewed by Forge and Atlas.

**Size**

L: nine decisions, each small, but the measurements and compose files add up.
