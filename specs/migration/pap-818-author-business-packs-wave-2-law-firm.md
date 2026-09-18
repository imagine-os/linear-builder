---
identifier: "PAP-818"
title: "Author business packs wave 2: law firm, real estate brokerage, property management, construction and ecommerce, with page specs, views, pipelines, charts of accounts, sample data and starter docs"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Business migrations"
state: "Backlog"
parent: "PAP-207"
children: []
blockedBy: ["PAP-114", "PAP-161", "PAP-199", "PAP-349", "PAP-426", "PAP-427"]
blocks: []
key: "r4/migration/packs-wave-2-law-real-estate-property-construction-ecommerce"
url: "https://linear.app/paperos/issue/PAP-818/author-business-packs-wave-2-law-firm-real-estate-brokerage-property"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:49.935Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-818: Author business packs wave 2: law firm, real estate brokerage, property management, construction and ecommerce, with page specs, views, pipelines, charts of accounts, sample data and starter docs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

'One size fits all' needs more than five shapes. Wave 2 covers the businesses that move the most money per record: matters and trust accounting for law firms, listings and commissions for brokerages, units and leases for property management, jobs and progress billing for construction, and a catalogue with orders for ecommerce, each passing the PAP-426 lint and conformance the first five pass.

**Scope**

In: `packages/import/templates/{law-firm,real-estate,property-management,construction,ecommerce}/`: law firm (matters, clients, time entries, trust ledger accounts flagged `client_trust` with a separate `trust_cash` subtype, conflict check segment, intake sequence); real estate (listings, showings calendar, offers pipeline, commission split chart lines, buyer and seller segments); property management (properties, units, leases with recurring rent schedules via PAP-765, maintenance requests kanban, deposits liability accounts); construction (jobs, estimates and change orders, progress billing with retainage liability, subcontractors as vendors, schedule Gantt saved `unsupported` until PAP-168); ecommerce (products with variants as items, orders, customers, returns, inventory hooks to PAP-775, abandoned-cart segment); staff role presets; preview screenshots by Playwright.

Out: regulatory certification (trust accounting rules noted, not audited), MLS or listing-portal integrations, storefront themes.

**Spec**

* Each pack `extends: base`; lint minimums apply (3 page specs, 6 views, 1 pipeline, 1 chart, 2 segments, 1 sequence, 1 doc); charts balance to zero on apply.
* Money-sensitive structures (trust cash, deposits, retainage) use ledger subtypes from PAP-175 so PAP-183 reports them correctly; sample data never shows real names or addresses.
* Packs reference finance features by contract capability; when a module is disabled the pack applies with those sections skipped and reported.

**Interface contract**

Provides: five packs with previews at 1280 both themes, role presets, item counts in `docs/migration/templates.md`. Consumes: pack format and applier (PAP-426), authoring conventions from wave 1 (PAP-427), conformance (PAP-122), finance subtypes (PAP-175), recurring schedules and inventory (business-core round-4 issues, soft).

**Definition of done**

* All five pass lint; applied to empty tenants every page passes PAP-122 conformance, every view renders, trial balance zero (script and report attached); composing property-management plus ecommerce works.
* Justin reviews the five content lists in one Needs Justin item; screenshots at 1280 both themes per pack plus 375 for two; CHANGELOG.

**Test plan**

* Unit: lint on all five; sample data relation integrity; subtype presence for trust, deposit and retainage accounts.
* E2E: apply property management with sample data, open the units calendar and the rent schedule, remove sample data, structure intact.

**Demo**

Reviewer applies the law-firm pack, opens a matter with its time entries and the trust ledger view, then removes sample data. Under two minutes.

**Edge cases**

* Tenant already applied retail: ecommerce merges product tables, never changes types.
* Finance module disabled: charts skipped with a report line and a re-apply hint.

**Dependencies**

Hard: PAP-426, PAP-427. Soft: PAP-122, PAP-175, PAP-168, PAP-765, PAP-775.

**Agent**

Builder: Scout (Template Packager) with Quill and Ledger (trust and retainage charts). Reviewer: Sentinel (Visual Inspector, Edge Case Hunter; Justin for realism).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/inventory-stock-and-cogs` = PAP-775, `r4/business-core/recurring-invoices-dunning` = PAP-765.
