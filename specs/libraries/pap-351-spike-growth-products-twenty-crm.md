---
identifier: "PAP-351"
title: "Spike growth products: Twenty CRM, Chatwoot, Listmonk and Postiz with compose, seeded flows, metrics and scorecards"
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
blockedBy: ["PAP-350"]
blocks: ["PAP-352"]
key: "child/PAP-215/1"
url: "https://linear.app/paperos/issue/PAP-351/spike-growth-products-twenty-crm-chatwoot-listmonk-and-postiz-with"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:34.565Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-351: Spike growth products: Twenty CRM, Chatwoot, Listmonk and Postiz with compose, seeded flows, metrics and scorecards

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Research M

**Goal**

Run Twenty, Chatwoot, Listmonk and Postiz, exercise the CRM, support inbox, campaign and social scheduling flows the growth project needs, and produce scorecards with provisional modes for the sibling ADR so `growth/*` stops guessing. Time-box 8 hours.

**Scope**

In: `spikes/oss-products/{twenty,chatwoot,listmonk,postiz}/` with compose, env example, README, `metrics.json`, screenshots at 375 and 1280; flows: Twenty (company, contact, deal, stage move, API read), Chatwoot (inbox, assign, reply, contact link), Listmonk (list, campaign, template, bounce handling), Postiz (mock provider, schedule, approval); scorecards with product extras.

Out: the ADR (sibling 3).

**Spec**

* Expected licenses to verify: Twenty AGPL-3.0, Chatwoot MIT, Listmonk AGPL-3.0, Postiz AGPL-3.0.
* Cross-link PAP-188 (growth research) findings; do not repeat them.
* SSO gated behind paid tiers recorded as an exact gate.

**Interface contract**

Provides: four spike folders, four scorecards, metrics, provisional modes for sibling 3, comments on PAP-188, PAP-187, PAP-197, PAP-190. Consumes: PAP-209, PAP-211, PAP-188 findings, PAP-25 profile.

**Definition of done**

* Four compose spikes start in CI and locally; screenshots and metrics committed.
* Scorecards validate with provisional modes and rationale.
* Comments posted on the four growth issues.

**Test plan**

* `compose-smoke` per product.
* Playwright flow scripts with screenshots at 375 and 1280.
* Scorecard validation.

**Demo**

Reviewer starts the Twenty compose, opens the seeded pipeline and moves a deal, then reads the scorecard's embed section on SSO limits. Under two minutes after pull.

**Edge cases**

* Product ships its own auth and cannot trust Better Auth: embed needs a proxy or downgrades to borrow.
* Twenty image over 2 GB RAM: recorded against budget.
* Postiz needs real provider apps: mock provider only; note for PAP-190.

**Dependencies**

PAP-209 (hard), PAP-211 (soft), PAP-188 (cross-link). Blocks sibling 3.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner). Reviewed by Beacon and Atlas.

**Size**

M
