---
identifier: "PAP-810"
title: "Deal products and quote from deal: line items on deals from the finance item catalogue, amount roll-up, one-click quote creation and acceptance syncing the deal to Won"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "CRM core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-189", "PAP-395", "PAP-774"]
blocks: []
key: "r4/growth/deal-products-and-quotes"
url: "https://linear.app/paperos/issue/PAP-810/deal-products-and-quote-from-deal-line-items-on-deals-from-the-finance"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:47.584Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-810: Deal products and quote from deal: line items on deals from the finance item catalogue, amount roll-up, one-click quote creation and acceptance syncing the deal to Won

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

A deal amount typed by hand and an invoice typed again is how numbers diverge. Deal line items priced from the catalogue, a quote generated from them through the finance document port and acceptance moving the deal to Won connect CRM and finance the way HubSpot Quotes and Pipedrive Products do.

**Scope**

In: `crm_deal_line (deal_id, item_id?, description, quantity, unit_price_minor, currency, discount_pct, position)` with roll-up trigger to `crm_deal.amount_minor`; line editor on the deal page using the finance `ItemPicker` through `@paperos/contract-business-core`; `crm.deals.createQuote` calling `documents.create` with the lines and linking `crm_deal.quote_document_id`; listeners on `document.accepted|paid` (catalogue topics `invoice.*` and the quote acceptance event) moving the deal stage per pipeline settings (`won_on: accepted|paid`); quote status chip on the kanban card; pipeline value reports use line data when present.

Out: CPQ rules and approval matrices, subscriptions from deals (recurring issue), e-signature (business-core out).

**Spec**

* Currency per deal; mixed-currency lines refused; amounts are `Money` and roll up with `Money.add`.
* Quote creation snapshots lines; later deal edits prompt to regenerate a new quote version rather than mutate an issued one.
* All finance access goes through the contract ports resolved from the kernel, never `packages/finance` imports (lint R8).

**Interface contract**

Provides: `crm_deal_line`, `crm.deals.lines.*`, `crm.deals.createQuote`, stage automation on acceptance, kanban quote chip, dataset `crm.dealLines`. Consumes: CRM views (PAP-189), item catalogue (PAP-774), documents (PAP-395, PAP-396 acceptance), kernel ports (PAP-490), FX (PAP-766, soft).

**Definition of done**

* Roll-up trigger tests; quote creation integration through the kernel-resolved port; acceptance moves the deal in a test; Playwright line editor; screenshots at 375, 1024, 1920 light and dark.
* `docs/growth/deal-products.md`; CHANGELOG.

**Test plan**

* Unit: roll-up with discounts, currency guard, snapshot versioning, stage mapping.
* E2E: add two catalogue items to a deal, create the quote, accept it from the public page and see the deal in Won with the amount matching the quote total.

**Demo**

Reviewer prices a deal from the picker, clicks Create quote, accepts it in a private window and watches the kanban card move to Won. Under two minutes.

**Edge cases**

* Business-core module disabled for the tenant: line editor hidden, amount editable by hand (fail-open read, `MODULE_DISABLED` on quote creation).
* Item archived after adding: line kept with a warning at quote time.
* Deal lost after quote issued: quote voided with a prompt.

**Dependencies**

Hard: PAP-189, PAP-774, PAP-395. Soft: PAP-396, PAP-490, PAP-766.

**Agent**

Builder: Beacon (CRM Builder) with Ledger consulted. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/fx-rates-and-conversion` = PAP-766, `r4/business-core/item-catalogue` = PAP-774.
