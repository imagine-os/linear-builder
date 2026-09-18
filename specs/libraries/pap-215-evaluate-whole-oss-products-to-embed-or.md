---
identifier: "PAP-215"
title: "Evaluate whole OSS products to embed or fork (Twenty CRM, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz)"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: null
children: ["PAP-351", "PAP-350", "PAP-352"]
blockedBy: ["PAP-209"]
blocks: []
key: "libraries/oss-products"
url: "https://linear.app/paperos/issue/PAP-215/evaluate-whole-oss-products-to-embed-or-fork-twenty-crm-nocodb-baserow"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:57:19.274Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-24"
cycle: null
---

# PAP-215: Evaluate whole OSS products to embed or fork (Twenty CRM, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz)

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Decide, product by product, whether PaperOS embeds, forks, borrows from or rejects whole open-source products overlapping planned systems: Twenty (CRM), NocoDB and Baserow (tables), Plane (PM), [Cal.com](<http://Cal.com>) (scheduling), Formbricks (forms), Postiz (social), plus Chatwoot (support) and Listmonk (campaigns) for PAP-197 and PAP-191. One ADR records a mode per product and hands it to the owning project. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Tables and PM products** (M, 6 hours): NocoDB, Baserow, Plane; compose spikes, seeded flows (table, relation, filter, kanban, API, webhook; issue, cycle, board, API), metrics, scorecards, provisional modes.
* **WP2 Growth products** (M, 8 hours): Twenty, Chatwoot, Listmonk, Postiz; flows (company, contact, deal, stage, API; inbox, assign, reply; list, campaign, template, bounce; mock provider, schedule, approval).
* **WP3 [Cal.com](<http://Cal.com>), Formbricks and the ADR** (M, 4 hours plus writing): remaining spikes; ADR with per-product sections and mode matrix; `docs/registry/reference/<id>.md` with Mermaid data model for every `borrow`; embed contracts (SSO, API surface, tenant mapping, theming, export path, owner) for every `embed`; registry entries.

Out: integrating anything (growth, tables, pm-linear own that), library evaluation (siblings), re-deciding Linear as system of record.

**Spec**

* Modes: `embed` (separate service via API, SSO from Better Auth, theming; `service` license context), `fork` (vendor into monorepo; requires Justin, expected zero), `borrow` (study model and UX, reimplement on PAP-161), `reject`.
* Spikes under `spikes/oss-products/<id>/` with pinned images, `.env.example`, `README.md`, `metrics.json` (RAM idle and after flow, startup, export completeness), screenshots at 375 and 1280; a product not starting within 20 minutes on the reference profile is scored down and skipped.
* Expected licenses to verify: Twenty, NocoDB, Plane, [Cal.com](<http://Cal.com>), Formbricks, Postiz, Listmonk AGPL-3.0 (some with `ee`); Baserow MIT core; Chatwoot MIT. AGPL forces `embed` or `borrow`.
* Rubric extras: license and tenancy tier, API completeness for our flows, SSO and embedding, data ownership and export, ops footprint, UX distance, upstream velocity and fork risk.
* Order WP1 and WP2 in parallel, then WP3, on `PAP-215/wp<n>-<slug>`; total time-box 2 agent-days.

**Interface contract**

Provides: ADR `docs/adr/NNNN-PAP-215-oss-products.md` with the nine-row matrix (product, license, tier, mode, RAM, owner, consuming issue), nine scorecards and `metrics.json`, borrow reference docs, embed contracts, registry entries (`adopted` for embed, `reference` for borrow, `rejected`), comments on PAP-188, PAP-187, PAP-197, PAP-190, PAP-162, PAP-100, PAP-161. Consumes: PAP-209 rubric, PAP-211 `service` tier, PAP-162 and PAP-188 findings by link, PAP-25 profile, PAP-216 CLI when live.

**Definition of done**

* Three work packages merged and reported.
* Integration check: all nine compose spikes start in the `compose-smoke` CI job; every product has a scorecard, metrics, screenshots and a mode in the matrix (Vitest lint).
* ADR accepted with Atlas, Nova and Beacon approvals; reference docs for every borrow; contracts for every embed; registry entries or drafts for all nine.
* Comments posted on the consuming issues; CHANGELOG; Linear comment with matrix and screenshot gallery.

**Test plan**

* `compose-smoke` per product with health probe.
* Playwright flow scripts per product saving screenshots at 375 and 1280.
* `pnpm lib score` validation; Vitest lint over the matrix; Mermaid diagrams render in the docs engine (screenshot).

**Demo**

Reviewer opens the ADR matrix, starts the NocoDB compose and opens the seeded kanban, then reads one borrow reference doc's data model diagram and one embed contract's SSO section. Under two minutes after images pull.

**Edge cases**

* Paid tier for SSO or API (`ee` folders): embed scored down with the exact gate.
* Product cannot trust an external session: proxy or downgrade to borrow.
* Per-instance tenancy: ops cost multiplies; usually reject for embed.
* UI-only export: data-ownership gate fails.
* Single-company upstream with license changes: fork risk raised.
* Images over 2 GB RAM ([Cal.com](<http://Cal.com>), Twenty): weighed against the PAP-214 budget.

**Dependencies**

PAP-209 (hard). Soft: PAP-211, PAP-162, PAP-188 (cross-link), PAP-216. Informs PAP-188, PAP-187, PAP-197, PAP-190, PAP-100, PAP-161.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner) for compose and metrics. Reviewed by Atlas, with Nova and Beacon as consumers.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: [Round 2 pending issues: libraries (9)](https://linear.app/paperos/document/round-2-pending-issues-libraries-9-63c73eed632d)
