---
identifier: "PAP-878"
title: "Specify the commerce and operations domain model: product, variant, price list, stock location and movement, order and fulfilment, purchase order and bill, project and time entry, shift, asset and work order, mapped to fin_* and Stripe"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Commerce contract and catalog"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-126", "PAP-175", "PAP-177", "PAP-302", "PAP-394", "PAP-395"]
blocks: ["PAP-877", "PAP-879", "PAP-883"]
key: "r4/commerce/domain-model"
url: "https://linear.app/paperos/issue/PAP-878/specify-the-commerce-and-operations-domain-model-product-variant-price"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:00.122Z"
model: "claude-fable-5-1"
effort: "max"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-878: Specify the commerce and operations domain model: product, variant, price list, stock location and movement, order and fulfilment, purchase order and bill, project and time entry, shift, asset and work order, mapped to fin_* and Stripe

**Model / Effort:** Fable 5.1 (`claude-fable-5-1`) / max — Spec M

**Goal**

Draw the operational objects every business type shares and how they attach to the finance model: which objects are `fin_party`s, which lines become `fin_document` lines, which movements post to the ledger and through which PAP-394 rules, how Stripe products and prices mirror the catalog, and which terminology (PAP-126) renames them per industry, so eleven packs can be authored without inventing new tables.

**Scope**

In: `docs/commerce/model.md` with an ER diagram and Zod schemas in the contract: `Product` (`kind good|service|digital|bundle`, `taxCode`, `trackInventory`), `Variant` (`sku`, `barcode`, options, `stripePriceId?`), `PriceList` (currency, audience, validity, rules), `StockLocation`, `StockMovement` (append-only: `receipt|sale|return|adjustment|transfer|count`, qty, cost `Money`, source `EntityRef`), `Order` and `OrderLine` (channel `portal|pos|manual|marketplace`, status machine), `Fulfilment` (pickup, delivery, shipment with label ref), `Return`, `PurchaseOrder`, `Receipt`, `VendorBill`, `Project`, `TimeEntry`, `Shift`, `TimeOffRequest`, `Timesheet`, `Asset`, `MaintenanceSchedule`, `WorkOrder`, `CustomerSubscription`, `Vendor` (marketplace), `Listing`, `Payout`. Finance mapping table: which object creates or references `fin_party` (customers, vendors, employees are parties per PAP-175), which flows create `fin_document`s (order → invoice or receipt, bill → AP document, time → invoice), inventory valuation (weighted average, COGS on sale) and the posting rules to register. Stripe mapping: `Product`/`Variant` ↔ Stripe Product/Price on the platform or connected account (PAP-177, PAP-181); sync direction rules (PaperOS is the source; Stripe ids stored); Tax codes (PAP-182). Terminology defaults per industry in `industries.yaml` (PAP-126): product → dish, service, treatment, unit; order → ticket, job, case; vendor → supplier, subcontractor.

Out: Implementation. UI. Manufacturing, BOMs, multi-currency price lists beyond PAP-766.

**Spec**

* Stock is never a stored number of record: `onHand` is the sum of movements per location, cached and rebuilt like ledger balances (PAP-394 `rebuildBalances` pattern); reservations are movements of kind `reserve` with expiry
* Orders and bills own no money logic: they produce `fin_document`s and payments flow through PAP-396; refunds are credit notes plus Stripe refunds; COGS posts at fulfilment with the movement's cost
* Projects reuse PM entities (PAP-100) for tasks; a `Project` is a billing and reporting container over them; time entries reference tasks optionally
* Shifts reuse the scheduling `AvailabilityRule` shape (engagement) so a staff shift and a bookable slot are one truth; timesheets aggregate time entries and shifts for payroll (PAP-400 inputs)
* Every table has `tenant_id`, RLS, audit trigger and an `EntityRef` route registered for the assistant and search; every status machine is drawn and its events named

**Interface contract**

Provides: `docs/commerce/model.md`, ER diagram, Zod schemas for the objects above, finance and Stripe mapping tables, posting rule list, terminology defaults. Consumes: finance model (PAP-175), Stripe Billing and Connect (PAP-177, PAP-181), `Money` (PAP-302), documents (PAP-395), posting rules (PAP-394), business profile (PAP-126), PM entities (PAP-100). Consumed by: every issue in this project; PAP-183 (inventory valuation and COGS reports), PAP-427 packs (objects available), growth (order activity), assistant tools.

**Definition of done**

* Document merged with ADR; schemas exported; migration for the tables with RLS and harness enrolment; three worked flows (retail sale with stock, agency time-to-invoice, plumber work order to invoice) as JSON fixtures that validate and a posting trace for each
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schema fixtures; status machines as pure reducers with exhaustive transition tests; stock sum invariant on fixtures.
* Review: Ledger (Bookkeeper) checks the posting rule list against PAP-394; Sentinel checks that no object stores card or bank data (PAP-359).

**Demo**

Walk the retail flow: variant with stock in two locations, POS sale reserving then consuming stock, the receipt document, the COGS and revenue postings, and a return reversing them.

**Edge cases**

* Service-only business (agency): inventory tables exist but stay empty and hidden by the module toggle for that pack
* Same SKU sold on marketplace and directly: one variant, two channels; the marketplace split is a posting rule, not a second product

**Dependencies**

PAP-175, PAP-177 (hard), PAP-302, PAP-395, PAP-394 (hard), PAP-126, PAP-100 (soft).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/fx-rates` = PAP-766.
