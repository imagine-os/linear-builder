---
identifier: "PAP-827"
title: "Commerce import from Shopify, WooCommerce and Square: products and variants to items, customers to CRM, orders and refunds to documents and balanced ledger postings, inventory levels"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-201", "PAP-347", "PAP-394", "PAP-774"]
blocks: []
key: "r4/migration/shopify-woocommerce-square-import"
url: "https://linear.app/paperos/issue/PAP-827/commerce-import-from-shopify-woocommerce-and-square-products-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:51.678Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-827: Commerce import from Shopify, WooCommerce and Square: products and variants to items, customers to CRM, orders and refunds to documents and balanced ledger postings, inventory levels

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Retail and ecommerce businesses arrive with a store. Products, customers, orders and refunds from Shopify, WooCommerce and Square map onto the item catalogue, the CRM and the ledger the same way Stripe history does in PAP-423, so gross profit and customer history are right from the conversion date.

**Scope**

In: `connectors/{shopify,woocommerce,square}/` via the connections issue (Shopify Admin GraphQL with cursor pagination and cost-based throttling, WooCommerce REST v3 with keys, Square API with OAuth): products and variants to `fin_item` (SKU, prices, inventory flag), customers to `crm_contact|crm_company`, orders to `receipt` or `invoice` documents (PAP-395) with lines, discounts, shipping, taxes, and postings through `postingRulesCommerce(order)` (revenue per item, sales tax liability, processor fees from payouts where available, refunds reversing), inventory levels as opening stock movements for PAP-775, payouts as transfers; conversion-date gate like PAP-425; posting rules reviewed by Ledger.

Out: storefront themes and content, live order sync (scheduled resync issue), fulfilment and shipping integrations, marketplaces.

**Spec**

* Amounts in minor units in order currency with functional equivalents from PAP-766; every journal balances or the dry run stops.
* Orders before the conversion date import as documents only (history) unless 'post history' is chosen; after it they post.
* Recorded fixtures from each platform's development store are the CI gate; live runs need store credentials (NJ) and skip otherwise.

**Interface contract**

Provides: three connectors, `postingRulesCommerce`, variant-to-item mapping, opening stock movements, wizard steps reusing PAP-425's `ConversionDate` and `TrialBalance`. Consumes: framework, items, posting rules (PAP-394), documents (PAP-395), CRM schema, inventory (soft), FX, finance wizard steps (PAP-425), connections, conformance harness.

**Definition of done**

* Fixture stores import with counts equal to manifests; P&L from PAP-183 matches each platform's sales report within rounding (table attached); rollback via reversing entries returns the trial balance; Ledger signs off the posting rules doc; screenshots at 375, 1024, 1920 light and dark; CHANGELOG.

**Test plan**

* Unit: posting rules on 15 order fixtures (discounts, partial refunds, multi-currency, gift cards as liabilities), variant mapping, throttling.
* E2E: connect the mocked Shopify store, pick a conversion date, review the trial balance, commit, open the P&L and the items grid.

**Demo**

Reviewer imports the Shopify development store fixture and opens the P&L showing revenue by product and a balanced trial balance, then rolls back. Under two minutes.

**Edge cases**

* Order with a deleted product: line kept as description-only with a placeholder item.
* Square cash orders: no processor fee, posted to `cash`.
* Gift card sales: liability, not revenue, until redeemed.

**Dependencies**

Hard: PAP-347, PAP-774, PAP-394, PAP-201. Soft: PAP-395, PAP-425, PAP-775, PAP-766, connections issue, conformance harness.

**Agent**

Builder: Scout (Import Mapper) with Ledger (Bookkeeper) owning posting rules. Reviewer: Sentinel (Security Auditor, Code Reviewer; Ledger for accounting).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/business-core/fx-rates-and-conversion` = PAP-766, `r4/business-core/inventory-stock-and-cogs` = PAP-775, `r4/business-core/item-catalogue` = PAP-774.
