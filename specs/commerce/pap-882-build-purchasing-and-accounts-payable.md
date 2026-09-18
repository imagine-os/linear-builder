---
identifier: "PAP-882"
title: "Build purchasing and accounts payable: purchase orders, receiving into stock, vendor bills with OCR capture, three-way match, approval policies, bill payment scheduling and AP postings"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Orders, POS, purchasing, projects and HR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-183", "PAP-185", "PAP-394", "PAP-395", "PAP-879"]
blocks: []
key: "r4/commerce/purchasing-ap"
url: "https://linear.app/paperos/issue/PAP-882/build-purchasing-and-accounts-payable-purchase-orders-receiving-into"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:00.626Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-882: Build purchasing and accounts payable: purchase orders, receiving into stock, vendor bills with OCR capture, three-way match, approval policies, bill payment scheduling and AP postings

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Run the buying side: purchase orders to vendors (`fin_party` vendors from PAP-175), receiving that creates stock movements at cost, vendor bills captured by upload with the PAP-185 receipt OCR, three-way match (PO, receipt, bill) with tolerances, approval through the workflows approvals framework, payment scheduling with runs, and AP postings so PAP-183's AP aging has real data.

**Scope**

In: `PurchasingPort`: `po` (draft, issue by email PDF via the print kit, acknowledge), `receive` (partial receipts create `receipt` movements with landed cost allocation), `bill` (create from upload with OCR line extraction reusing PAP-185, or from PO), `match` (quantity and price tolerances, exceptions queue), `schedulePayment` (due dates, early-payment terms, batch payment run marking bills paid with a manual or Stripe payout reference). Console pages `/commerce/purchasing` (POs grid and editor, receiving screen with scanner, bills inbox with OCR review side by side, match exceptions, payment runs) with specs. Approvals: policy keys `po.issue` and `bill.approve` with Money thresholds through PAP-849; segregation of duties enforced (receiver ≠ approver). Posting rules: `stock.received` (inventory asset vs goods-received-not-invoiced), `bill.approved` (expense or inventory vs AP), `bill.paid` (AP vs cash); reports registered for PAP-183 AP aging drill-down.

Out: Automated vendor payments through a payments API (v0.3; bills are marked paid with a reference). Vendor portal (marketplace issue covers vendor audience).

**Spec**

* Three-way match runs on bill creation and on every receipt; tolerances per tenant (default 2 percent price, 0 quantity); mismatches block approval until resolved with a reason
* Landed costs (freight, duty) allocate across received lines by value or quantity and adjust weighted-average cost
* Bills are `fin_document`s of kind `bill` (PAP-395 model) with vendor numbering; duplicate detection on vendor + reference + amount
* Payment runs are immutable once executed; reversing requires a new run

**Interface contract**

Provides: `PurchasingPort` default adapter, tables, console pages, approval policy keys, posting rules, `po.*` and `bill.*` events, AP datasets. Consumes: catalog and inventory, receipt OCR (PAP-185), posting rules (PAP-394), documents (PAP-395), AP aging report (PAP-183), approvals framework, print kit (PAP-235), scanner (PAP-260). Consumed by: PAP-183 (AP aging depth), packs (retail, restaurant, construction, trades), platform-ops (spend metrics).

**Definition of done**

* Demo: issue a PO, receive partially with a scanner, upload the vendor bill PDF, OCR proposes lines, match flags a price variance, manager approves with a reason, payment run marks it paid; AP aging shows it; postings reconcile
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: match tolerances; landed cost allocation; duplicate detection; payment run immutability.
* Integration: partial receipts and cost updates; approval segregation; posting traces.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Buy 100 mugs: PO to the supplier, receive 60, upload the bill for 60 at a slightly higher price, watch the match exception, approve, schedule payment, and open AP aging.

**Edge cases**

* Bill arrives before any receipt (services): match degrades to two-way and the policy may require a second approver
* Vendor changes bank details on a bill: flagged as a fraud signal (PAP-356 event) and requires re-verification before payment
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-879 (hard), PAP-185, PAP-394, PAP-395 (hard), PAP-183 (soft), PAP-849 (hard for approvals; a simple role gate as fallback).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/commerce/catalog-inventory` = PAP-879, `r4/workflows/approvals-framework` = PAP-849.
