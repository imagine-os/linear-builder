---
identifier: "PAP-352"
title: "Spike Cal.com and Formbricks, then write the OSS products mode ADR, borrow reference docs and embed integration contracts"
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
blockedBy: ["PAP-351"]
blocks: []
key: "child/PAP-215/2"
url: "https://linear.app/paperos/issue/PAP-352/spike-calcom-and-formbricks-then-write-the-oss-products-mode-adr"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:41.073Z"
---

# PAP-352: Spike Cal.com and Formbricks, then write the OSS products mode ADR, borrow reference docs and embed integration contracts

**Goal**

Finish the product evaluation and make it actionable: spike the two remaining products, then write the single ADR with the mode matrix for all nine, a borrow reference doc (data model diagram and UX patterns) for every `borrow` verdict and an embed contract (SSO, API surface, tenant mapping, theming, export path, owner) for every `embed` verdict. Time-box 4 hours plus writing.

**Scope**

In: `spikes/oss-products/{calcom,formbricks}/` as in the siblings; ADR `docs/adr/NNNN-PAP-215-oss-products.md` with per-product sections and summary matrix; `docs/registry/reference/<id>.md` with Mermaid data model per borrow; embed contracts per embed; registry entries `adopted` (embed), `reference` (borrow), `rejected`; comments on PAP-188, PAP-162, PAP-197, PAP-100.

Out: integrating anything.

**Spec**

* Expected licenses: [Cal.com](<http://Cal.com>) AGPL-3.0 plus commercial `ee`, Formbricks AGPL-3.0 plus `ee`.
* `fork` requires Justin and is expected to be zero products.
* Matrix columns: product, license, tier, mode, RAM, owner character, consuming issue.

**Interface contract**

Provides: ADR with matrix, reference docs, embed contracts, registry entries, comments. Consumes: siblings 1 and 2 scorecards and metrics, PAP-209, PAP-211, PAP-216 CLI when live.

**Definition of done**

* Nine spikes, nine scorecards, one accepted ADR with Atlas, Nova and Beacon approvals.
* Reference docs for every borrow, contracts for every embed, registry entries for all nine.
* CHANGELOG entry; Linear comment with the matrix and screenshot gallery.

**Test plan**

* `compose-smoke` for the two new products.
* Vitest lint: every product in the matrix has a mode, a scorecard path and a registry entry.
* Mermaid diagrams render in the docs engine (screenshot).

**Demo**

Reviewer opens the ADR, reads the nine-row matrix, clicks through to one borrow reference doc with its data model diagram and one embed contract. Under two minutes.

**Edge cases**

* Single-company upstream with recent license changes: fork risk raised, borrow preferred.
* Product requires a paid tier for API: embed scored down with exact gate.
* Registry not live: entries drafted in `docs/registry/drafts/`.

**Dependencies**

Siblings 1 and 2 (hard), PAP-209, PAP-211, PAP-216 (soft).

**Agent**

Researched by Scout (Library Evaluator) with Forge. Reviewed by Atlas, Nova and Beacon.

**Size**

M
