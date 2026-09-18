---
identifier: "PAP-773"
title: "Purchase orders and receiving: PO editor from vendor items, approval, partial receipts, three-way match to vendor bills and open-PO reporting"
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
blockedBy: ["PAP-772", "PAP-774"]
blocks: []
key: "r4/business-core/purchase-orders-and-receiving"
url: "https://linear.app/paperos/issue/PAP-773/purchase-orders-and-receiving-po-editor-from-vendor-items-approval"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:41.230Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-773: Purchase orders and receiving: PO editor from vendor items, approval, partial receipts, three-way match to vendor bills and open-PO reporting

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Retail, restaurant and construction businesses order before they are billed. Purchase orders with receiving and a three-way match (PO, receipt, bill) stop paying for goods never delivered and feed inventory quantities.

**Scope**

In: `fin_purchase_order (vendor_id, number, status: draft|approved|sent|partial|received|closed|cancelled, expected_at, ship_to jsonb, notes)`, `fin_purchase_order_line (item_id?, description, qty_ordered, qty_received, unit_cost_minor, expense_or_inventory_account_id)`, `fin_receipt (po_id, received_at, lines)`; PO PDF and send email via PAP-396 and PAP-397 templates; receiving screen with barcode-free quantity entry; `bills.createFromPo` pre-filling lines and flagging variances over tolerance; dataset `finance.openPurchaseOrders`; inventory hook `onReceive` for PAP-775.

Out: supplier portals, EDI, drop-shipping, landed cost allocation (v0.3).

**Spec**

* Receiving posts nothing for expense lines; inventory lines post `inventory.received` (debit `inventory`, credit `goods_received_not_invoiced`) when the inventory issue is present, else nothing until the bill.
* Three-way match tolerance per tenant (`fin_settings.po_match_tolerance_pct`, default 2); variances become a review item on the bill.
* Numbering through the PAP-395 sequence mechanism (`PO-` prefix format in `fin_settings`).
* Closing a PO with unreceived quantity records the shortfall reason.

**Interface contract**

Provides: `purchaseOrders.*`, `receipts.*`, `bills.createFromPo`, hook `onReceive`, datasets, PDF template `purchase-order`. Consumes: bills (PAP-772), items (PAP-774), PDF and email (PAP-396, PAP-397), sequences (PAP-395), grid (PAP-165).

**Definition of done**

* Unit and Playwright green; PDF snapshot; screenshots at 375, 1024, 1920 in three themes.
* Three-way match test: bill within tolerance auto-approves match, over tolerance creates a variance item.
* `docs/finance/purchasing.md`; CHANGELOG.

**Test plan**

* Unit: status machine, partial receipt arithmetic, tolerance logic, bill pre-fill.
* E2E: create a PO for two items, receive one fully and one partially, create the bill from the PO and see the variance flag.

**Demo**

Reviewer raises a PO, receives part of it, converts it to a bill and reads the variance banner. Under two minutes.

**Edge cases**

* Over-receipt beyond ordered quantity: allowed with a warning and a note on the line.
* Vendor changes price on the bill: variance by line, not total.
* PO cancelled after partial receipt: remaining lines cancelled, received lines kept.

**Dependencies**

Hard: PAP-772, PAP-774. Soft: PAP-775, PAP-396, PAP-397.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/business-core/inventory-stock-and-cogs` = PAP-775, `r4/business-core/item-catalogue` = PAP-774, `r4/business-core/vendor-bills-and-ap-payments` = PAP-772.
