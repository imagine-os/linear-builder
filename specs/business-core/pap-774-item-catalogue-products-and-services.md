---
identifier: "PAP-774"
title: "Item catalogue: products and services with SKU, prices per currency, default revenue and expense accounts, tax codes and Stripe Price sync for tenant checkout"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-175", "PAP-395"]
blocks: ["PAP-773", "PAP-775", "PAP-783", "PAP-788", "PAP-810", "PAP-827"]
key: "r4/business-core/item-catalogue"
url: "https://linear.app/paperos/issue/PAP-774/item-catalogue-products-and-services-with-sku-prices-per-currency"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:41.312Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-774: Item catalogue: products and services with SKU, prices per currency, default revenue and expense accounts, tax codes and Stripe Price sync for tenant checkout

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Invoice, quote and bill lines are free text today. A shared catalogue of what a business sells and buys gives consistent pricing, correct revenue accounts and tax codes per line, and is the object inventory, POS, purchase orders and CRM deal products all reference.

**Scope**

In: `fin_item (tenant_id, sku unique, name, kind: product|service|bundle, description, unit, is_active, sell: { prices jsonb [{ currency, amount_minor, price_list? }], revenue_account_id, tax_code, stripe_product_id?, stripe_price_ids jsonb }, buy: { default_cost_minor, expense_or_inventory_account_id, preferred_vendor_id? }, track_inventory bool, custom jsonb)`; `items.*` procedures; item picker in the PAP-395 line editor filling description, price, account and tax; price lists per customer group; optional Stripe Product and Price sync on the connected account (`items.syncStripe`) so PAP-396 Checkout uses catalogue prices; dataset and grid `/finance/items`; CSV import through PAP-200 with a preset.

Out: stock quantities and COGS (PAP-775), variants matrices (retail pack models them as items with attributes), subscriptions for tenant customers (recurring issue).

**Spec**

* Prices are `Money` per currency; missing currency falls back through PAP-766 with a badge.
* Changing an item's account or price never rewrites issued documents (lines snapshot the values at issue).
* Stripe sync is idempotent on `metadata.paperos_item_id`; archived items archive the Stripe price, never delete.
* Bundles expand to component lines at pick time with the bundle price allocated by `Money.allocate`.

**Interface contract**

Provides: `fin_item`, `items.*`, `ItemPicker`, `items.syncStripe`, dataset `finance.items`, CSV preset `items`. Consumes: document lines and sequences (PAP-395), accounts and tax codes (PAP-175, PAP-182 optional), Stripe client (PAP-177), Connect (PAP-181 optional), grid (PAP-165), CSV importer (PAP-200).

**Definition of done**

* Unit and Playwright green; Stripe sync verified in test mode with recorded fixtures; screenshots at 375, 1024, 1920 in three themes.
* Invoice created from three catalogue items posts revenue to three different accounts (integration test).
* `docs/finance/items.md`; CHANGELOG.

**Test plan**

* Unit: price resolution order (customer price list, currency, fallback), bundle allocation, sync idempotency, snapshot on issue.
* E2E: create two items, build a quote from the picker, accept it, and see the revenue split in the journal.

**Demo**

Reviewer adds a service item with a USD and EUR price, creates an invoice for a EUR customer from the picker and sees the right price and account. Under two minutes.

**Edge cases**

* SKU collision on import: suffixed and reported by the dry run.
* Item archived while on a draft document: line kept with a warning at issue.
* Tax code unsupported by Stripe Tax: manual rate path from PAP-182.

**Dependencies**

Hard: PAP-395, PAP-175. Soft: PAP-177, PAP-181, PAP-182, PAP-200, PAP-766. Blocks inventory, purchase orders and POS issues.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/fx-rates-and-conversion` = PAP-766, `r4/business-core/inventory-stock-and-cogs` = PAP-775.
