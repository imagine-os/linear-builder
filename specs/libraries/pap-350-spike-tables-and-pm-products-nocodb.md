---
identifier: "PAP-350"
title: "Spike tables and PM products: NocoDB, Baserow and Plane with compose, seeded flows, metrics and scorecards"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Research"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: "PAP-215"
children: []
blockedBy: ["PAP-209"]
blocks: ["PAP-351"]
key: "child/PAP-215/0"
url: "https://linear.app/paperos/issue/PAP-350/spike-tables-and-pm-products-nocodb-baserow-and-plane-with-compose"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:41.073Z"
---

# PAP-350: Spike tables and PM products: NocoDB, Baserow and Plane with compose, seeded flows, metrics and scorecards

**Goal**

Run NocoDB, Baserow and Plane from pinned compose files, exercise the flows the tables and PM projects care about, capture metrics and screenshots, and produce scorecards with a provisional mode (`embed|fork|borrow|reject`) for the sibling ADR. Time-box 6 hours.

**Scope**

In: `spikes/oss-products/{nocodb,baserow,plane}/` with `docker-compose.yml`, `.env.example`, `README.md`, `metrics.json` (RAM idle and after flow, startup time, export completeness), screenshots at 375 and 1280; flows: NocoDB and Baserow (create table, relation, filter, kanban, API and webhook), Plane (issue, cycle, board, API); scorecards with product extras (license and tenancy tier, API completeness, SSO and embedding, data ownership, ops footprint, UX distance from PAP-161, upstream velocity).

Out: the ADR (sibling 3), other products.

**Spec**

* Product not started within 20 minutes on the reference profile: ops scored down, move on.
* Expected licenses to verify: NocoDB AGPL-3.0, Baserow MIT core with premium modules, Plane AGPL-3.0; AGPL forces `embed` or `borrow`.
* Share findings with PAP-162 by cross-link, never repeat its feature audit.

**Interface contract**

Provides: three spike folders, three scorecards, `metrics.json` per product, provisional modes for sibling 3. Consumes: PAP-209 rubric extras, PAP-211 `service` tier, PAP-162 findings, PAP-25 VPS profile.

**Definition of done**

* Three compose spikes start in CI (`compose-smoke`) and locally; screenshots and metrics committed.
* Scorecards validate; each has a provisional mode with a one-paragraph rationale.
* Comment on PAP-162 and PAP-100 with the relevant findings.

**Test plan**

* `compose-smoke` per product with a health probe.
* Playwright scripts for each required flow saving screenshots at 375 and 1280.
* `pnpm lib score` validation.

**Demo**

Reviewer runs `docker compose -f spikes/oss-products/nocodb/docker-compose.yml up`, opens the seeded kanban, then reads `metrics.json` and the scorecard. Under two minutes after images pull.

**Edge cases**

* Multi-tenancy per instance only: ops cost multiplied; usually reject for embed.
* Export is UI-only: data-ownership gate fails.
* Image needs more than 2 GB RAM: recorded against the PAP-214 budget.

**Dependencies**

PAP-209 (hard), PAP-211 (soft), PAP-162 (cross-link). Blocks sibling 3.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner). Reviewed by Nova and Atlas.

**Size**

M
