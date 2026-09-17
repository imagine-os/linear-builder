---
identifier: "PAP-215"
title: "Evaluate whole OSS products to embed or fork (Twenty CRM, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz)"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Research"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-209"]
blocks: []
key: "libraries/oss-products"
url: "https://linear.app/paperos/issue/PAP-215/evaluate-whole-oss-products-to-embed-or-fork-twenty-crm-nocodb-baserow"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-215: Evaluate whole OSS products to embed or fork (Twenty CRM, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz)

**Goal**

Decide, product by product, whether PaperOS embeds, forks, borrows from or rejects whole open-source products that overlap with planned systems: Twenty (CRM), NocoDB and Baserow (tables), Plane (project management), Cal.com (scheduling), Formbricks (forms and surveys), Postiz (social scheduling), plus Chatwoot (support inbox) and Listmonk (email campaigns) because `growth/support-inbox` and `growth/outreach-sequences` need the same answer. Each decision is recorded in one ADR with a mode and handed to the owning project.

**Scope**

In:
- Four modes with definitions: `embed` (run as a separate service, integrate via API, SSO from Better Auth and theming; `service` license context), `fork` (vendor code into the monorepo; almost never, requires Justin), `borrow` (study data model and UX, reimplement on the tables and views engine), `reject`.
- Spike: run each product with `docker compose` from `spikes/oss-products/<id>/`, seed one tenant with sample data, exercise the core flow, capture screenshots at 375 and 1280, record RAM, startup time, and export completeness.
- Scorecards per `libraries/eval-rubric` with extras: license and tenancy (`libraries/license-policy` service tier), API completeness for the flows we need, SSO and embedding (iframe, theming, deep links), data ownership and export formats, ops footprint, UX distance from what `tables/view-model-spec` will offer, upstream velocity and fork risk.
- One ADR `docs/adr/NNNN-PAP-<issue>-oss-products.md` with a per-product section and a summary matrix; registry entries with status `adopted` (embed), `rejected` or `reference` (borrow).

Out: actually integrating anything (`growth/*`, `tables/*`, `pm-linear/*` own that), evaluating libraries (other landscape issues), re-deciding Linear as system of record (settled by the plan).

**Spec**

- Time-box 2 agent-days; each product at most 2 hours including compose start-up; if a product does not start within 20 minutes on the reference VPS profile, score ops down and move on.
- Expected licenses to verify at evaluation time: Twenty AGPL-3.0, NocoDB AGPL-3.0, Baserow MIT core with premium modules, Plane AGPL-3.0, Cal.com AGPL-3.0 plus commercial `ee`, Formbricks AGPL-3.0 plus `ee`, Postiz AGPL-3.0, Chatwoot MIT, Listmonk AGPL-3.0. AGPL forces `embed` or `borrow`, never `fork` into shipped code, per policy.
- Required flows per product: Twenty (create company, contact, deal, move stage, API read), NocoDB and Baserow (create table, relation, filter, kanban, API and webhook), Plane (issue, cycle, board, API), Cal.com (event type, booking, webhook), Formbricks (survey, embed, response webhook), Postiz (connect a mock provider, schedule a post, approval), Chatwoot (inbox, assign, reply, contact link), Listmonk (list, campaign, template, bounce handling).
- Compose files use pinned image tags; secrets via `.env.example`; measurements from `docker stats` after five minutes idle and after the flow.
- Borrow deliverable: for each `borrow` verdict, a short `docs/registry/reference/<id>.md` with the data model diagram (Mermaid) and the UX patterns worth copying, linked from the consuming issue (`tables/feature-parity-audit`, `growth/crm-model`, `pm-linear/pm-data-model`).
- Embed deliverable: for each `embed` verdict, the integration contract: SSO method, API surface used, tenant mapping, theming limits, export path, and which character owns it.

**Definition of done**

- Nine compose spikes committed under `spikes/oss-products/`, each with `README.md`, screenshots at 375 and 1280, and `metrics.json`.
- ADR accepted with the mode matrix and per-product rationale; Atlas, Nova (tables), Beacon (growth) approvals in PR comments.
- Registry entries created or drafted for all nine; license checker passes with `service` context recorded.
- Borrow reference docs written for every `borrow` verdict; embed contracts for every `embed` verdict.
- Comments posted on `growth/growth-research`, `tables/feature-parity-audit`, `growth/support-inbox`, `pm-linear/pm-data-model` with the relevant verdicts.
- CHANGELOG entry; Linear comment with the matrix and screenshot gallery.

**Edge cases**

- Product requires a paid tier for SSO or API (common in `ee` folders): score embed down and record the exact gate.
- Product ships its own auth and cannot trust an external session: embed requires a proxy or is downgraded to borrow.
- Multi-tenancy is per-instance only (one deployment per tenant): ops cost multiplies; usually reject for embed.
- Export is UI-only with no API: fail data-ownership gate.
- Upstream is a single-company project with recent license changes: raise fork risk, prefer borrow.
- Docker images need more than 2 GB RAM (Cal.com, Twenty): record and weigh against the VPS budget from `libraries/backend-landscape`.

**Dependencies**

`libraries/eval-rubric` (hard). Soft: `libraries/license-policy` (service tier), `tables/feature-parity-audit` (shares NocoDB and Baserow findings, cross-link only). Informs `growth/growth-research`, `growth/crm-model`, `growth/support-inbox`, `growth/social-scheduler`, `pm-linear/pm-data-model`, `tables/view-model-spec`.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner) for compose and metrics. Reviewed by Atlas, with Nova and Beacon as consumers.

**Size**

L: nine products to run, exercise and document, even at two hours each.
