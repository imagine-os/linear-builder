---
identifier: "PAP-775"
title: "Inventory stock levels and COGS: stock movements per location, weighted-average and FIFO costing, cost of goods sold postings on sale, adjustments and low-stock alerts"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-394", "PAP-774"]
blocks: []
key: "r4/business-core/inventory-stock-and-cogs"
url: "https://linear.app/paperos/issue/PAP-775/inventory-stock-levels-and-cogs-stock-movements-per-location-weighted"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:41.398Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-775: Inventory stock levels and COGS: stock movements per location, weighted-average and FIFO costing, cost of goods sold postings on sale, adjustments and low-stock alerts

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Retail and restaurant packs model inventory as plain tables with no accounting behind them. This gives stock quantities per location and the COGS postings that make gross profit on the P&L real, behind the item catalogue so every sale and receipt moves stock consistently.

**Scope**

In: `fin_stock_movement (item_id, location_id, qty numeric(14,4), unit_cost_minor, kind: receipt|sale|adjustment|transfer|count, source EntityRef, occurred_at)` append-only, `fin_stock_level` materialised per `(item, location)`, `fin_location`; costing method per tenant (`weighted_average` default, `fifo` with layers); hooks: `onReceive` from purchase orders, `invoice.issued` lines with `track_inventory` post `cogs` (debit `cogs`, credit `inventory`) at the current cost; adjustments and stock counts with variance postings; low-stock alert via PAP-136 when `qty < reorder_point`; datasets `finance.stockLevels`, `finance.stockMovements`; grid pages under `/finance/inventory`.

Out: serial and lot tracking, manufacturing and BOMs, landed cost, multi-warehouse transfers in transit (v0.3).

**Spec**

* Movements are immutable; corrections are new movements; every posting carries the movement id as `source_id` so `ledger.postEvent` stays idempotent.
* Weighted average recomputed per receipt; FIFO consumes layers oldest first and stores the layer ids on the sale movement; both proven against a textbook fixture.
* Negative stock allowed per tenant setting with a warning; COGS uses the last known cost until the next receipt back-fills the variance to `cogs_adjustment`.
* Voided invoices reverse the COGS posting and the movement (new `sale` movement with negative qty).

**Interface contract**

Provides: tables, `inventory.*` procedures, costing engine `costOf(item, location, qty)`, posting rules `inventory.*`, `cogs`, datasets, alert kind `inventory.low_stock`. Consumes: items (PAP-774), posting rules (PAP-394), documents (PAP-395, PAP-397 void), purchase orders (PAP-773, optional), notifications (PAP-136), grid (PAP-165).

**Definition of done**

* Textbook fixture: 12 receipts and sales under both methods match hand-computed COGS to the cent; property test that stock value equals the `inventory` account balance after any movement sequence.
* Playwright: receive, sell through an invoice, count and adjust; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/inventory.md`; CHANGELOG.

**Test plan**

* Unit: weighted average, FIFO layers, negative stock path, void reversal, reorder alert once per crossing.
* E2E: receive 10 units at two costs, invoice 6, check gross profit on the P&L and the remaining layer.

**Demo**

Reviewer receives stock via a PO, issues an invoice for part of it and opens the P&L to see COGS and gross profit appear. Under two minutes.

**Edge cases**

* Sale before any receipt: COGS at zero cost, flagged, back-filled on the first receipt.
* Item switched from service to product: movements start from a counted opening balance.
* Costing method change: allowed only at a period boundary with an opening revaluation entry.

**Dependencies**

Hard: PAP-774, PAP-394. Soft: PAP-395, PAP-397, PAP-773, PAP-136.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Edge Case Hunter for costing, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/item-catalogue` = PAP-774, `r4/business-core/purchase-orders-and-receiving` = PAP-773.
