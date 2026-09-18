---
identifier: "PAP-790"
title: "CRM schema, routers, datasets, search registrations and the three page specs (the schema half of PAP-187)"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Staff"]
milestone: "CRM core"
state: "Backlog"
parent: "PAP-187"
children: []
blockedBy: ["PAP-33", "PAP-34", "PAP-279", "PAP-448"]
blocks: ["PAP-189", "PAP-193", "PAP-194", "PAP-195", "PAP-401", "PAP-404", "PAP-410", "PAP-485", "PAP-791", "PAP-792", "PAP-793", "PAP-796", "PAP-797", "PAP-798", "PAP-801", "PAP-802", "PAP-824", "PAP-826"]
key: "r4/growth/crm-schema-routers-page-specs"
url: "https://linear.app/paperos/issue/PAP-790/crm-schema-routers-datasets-search-registrations-and-the-three-page"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:43.548Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-790: CRM schema, routers, datasets, search registrations and the three page specs (the schema half of PAP-187)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Spec M

**Goal**

PAP-187 is an L that carries two deliverables: the customer-graph schema every growth issue waits on, and the consent centre folded in as work package 0. Splitting them makes the schema claimable on day one and reviewable as a Spec. This child is the schema half: the twelve `crm_*` tables, Zod types, routers, datasets, search registrations, events and the three page specs, exactly as PAP-187's Spec decides them.

**Scope**

In: `packages/growth/src/crm/schema.ts` (`crm_company`, `crm_contact`, `crm_contact_company`, `crm_lead`, `crm_pipeline`, `crm_pipeline_stage`, `crm_deal`, `crm_activity`, `crm_segment`, `crm_segment_member`, `crm_tag`, `crm_entity_tag`, `crm_external_ref`) with RLS, `drizzle-zod` types, routers `crm.companies|contacts|leads|deals|activities|segments.*` plus `crm.leads.convert` and `crm.deals.move`, `registerDataset` and search registrations, `defineTopic` for `crm.deal.stage_changed`, `crm.lead.converted`, `crm.contact.created`, page specs `specs/crm/pipeline|contacts|company-detail.spec.yaml`, `docs/growth/crm-model.md` with ER diagram and Twenty and HubSpot mapping.

Out: consent, suppression and the public preference routes (sibling PAP-791), UI (PAP-189), segment evaluation (PAP-195), importers.

**Spec**

* Columns per the PAP-187 Spec; add `crm_contact.user_id uuid?` (portal principal link used by PAP-195 `useInSegment`, PAP-397 portal invoices and PAP-411 chat) and `crm_contact.party_id?` to `fin_party` for statements and payments; `crm_deal.amount_minor bigint` plus `currency` per the contracts document.
* `consent jsonb` on `crm_contact` is reserved as a denormalised cache the sibling fills; this child ships it empty with a comment.
* Conversion `crm.leads.convert` is one transaction creating contact, optional company and deal and emitting `crm.lead.converted`; stage change trigger writes a `system` activity and sets `won_at|lost_at`.
* Permissions `crm.*.read|write|export` registered with PAP-59; customer audiences never see CRM datasets.
* Cursor pagination and `FilterTree` filters per PAP-268; every table is a dataset so PAP-189 views are JSON only.

**Interface contract**

Provides: the twelve tables, Zod types, routers, datasets `crm.contacts|companies|deals|activities`, search registrations, the three events, three page specs, `docs/growth/crm-model.md`. Consumes: core entities (PAP-33), RLS (PAP-34), `FilterTree` (PAP-279), API conventions (PAP-268), search (PAP-39), datasets (PAP-161, stub if absent), spec schema (PAP-117), `fin_party` (PAP-175, soft).

**Definition of done**

* Migration applies and rolls back on Postgres 17; `pnpm db:check` clean; cross-tenant harness green on all twelve tables.
* Three page specs validate with PAP-117; ER diagram renders; contract doc reviewed by Quill and Ledger.
* Drizzle Studio screenshot of seed data at 1280 and 1920; ADR `docs/adr/00xx-crm-model.md`; CHANGELOG; Linear comment on PAP-187.

**Test plan**

* Unit: unique email and domain constraints, conversion rollback on failure, stage trigger, cursor pagination per router, `crm.deals.move` bulk.
* E2E: none beyond Studio screenshots (no UI); `pnpm tsx scripts/crm-demo.ts` converts a lead, moves the deal to Won and prints the system activity and outbox event.

**Demo**

Reviewer runs `pnpm db:seed --profile demo`, browses contacts and deals in Drizzle Studio, then runs the CRM demo script. Under two minutes.

**Edge cases**

* Phone-only contact allowed; phone uniqueness is a merge suggestion, not a constraint.
* Same person at two companies: `crm_contact_company` history with from and to dates.
* Deleting a stage with deals blocked until moved.
* Foreign-currency amount stored as given; reporting converts via PAP-766.

**Dependencies**

Hard: PAP-33, PAP-34, PAP-279. Soft: PAP-268, PAP-39, PAP-117, PAP-161, PAP-175. Blocks PAP-189, PAP-401, PAP-404, PAP-410, PAP-193, PAP-194, PAP-195, PAP-485 and the consent sibling.

**Agent**

Builder: Beacon (CRM Builder) with Forge (Schema Wright). Reviewer: Sentinel (Security Auditor, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/fx-rates-and-conversion` = PAP-766, `r4/growth/consent-compliance-centre` = PAP-791.
