---
identifier: "PAP-887"
title: "Build the two-sided marketplace model: vendor accounts on Connect, vendor audience and portal, listings, split payments with platform fees, vendor payouts and statements, disputes routing"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Operations packs, marketplace and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-55", "PAP-62", "PAP-181", "PAP-408", "PAP-585", "PAP-880"]
blocks: []
key: "r4/commerce/marketplace-model"
url: "https://linear.app/paperos/issue/PAP-887/build-the-two-sided-marketplace-model-vendor-accounts-on-connect"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-887: Build the two-sided marketplace model: vendor accounts on Connect, vendor audience and portal, listings, split payments with platform fees, vendor payouts and statements, disputes routing

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Let a tenant run a marketplace (a farmers' collective, a booking marketplace, a multi-vendor shop): vendors onboard to Connect as sub-accounts of the tenant's platform, a `vendor` audience with its own portal surface, listings that are catalog products owned by a vendor, orders that split across vendors with destination charges and platform fees, payouts with monthly statements (PAP-408 pattern), and dispute routing to the vendor.

**Scope**

In: `MarketplacePort`: `vendors` (`fin_party` + Connect account via PAP-181 onboarding links, status, fee schedule, payout schedule), `listings` (product ownership, approval queue via the approvals framework, visibility), `split(order)` (per-vendor sub-orders, destination charges or separate charges and transfers, platform fee rules), `payouts` (Stripe payout events, statements PDF via the print kit, ledger postings `marketplace.split` and `vendor.payout`). Vendor portal `/vendor` (spec) on the PAP-62 shell pattern with audience `vendor` (PAP-55): listings, orders to fulfil, payouts and statements, disputes; staff console `/commerce/marketplace` (vendors, approvals, fee schedules, payout runs). Orders integration: a customer order with lines from three vendors creates one payment and three vendor sub-orders; fulfilment per vendor; returns and refunds allocate per vendor; disputes (PAP-423 mapping) route to the vendor with platform oversight.

Out: Vendor self-signup marketing pages. Cross-tenant marketplaces (tenants selling to other tenants). Escrow beyond Stripe holds.

**Spec**

* Money split is computed server-side per line from the fee schedule and recorded before charging; Stripe transfer amounts must equal the recorded split (assertion) or the order fails closed
* Vendors see only their own lines, customers and payouts; RLS predicates scope by `vendor_id` through the audience attribute (PAP-227)
* Payout statements are immutable PDFs with a hash; a correction is a new statement
* Fee changes apply to new orders only; the schedule is versioned

**Interface contract**

Provides: `MarketplacePort` default adapter, `vendor` audience surfaces, tables, split and payout logic, statements, posting rules, `vendor.payout.created`, `listing.*` events. Consumes: orders, Connect onboarding and transfers (PAP-181), payout and statement pattern (PAP-408), audiences (PAP-55), portal shell pattern (PAP-62), attribute predicates (PAP-227), approvals, print kit (PAP-235), dispute mapping (PAP-423). Consumed by: packs (marketplace pack in v0.3 wave 4), growth (vendor CRM), platform-ops (Connect health per vendor).

**Definition of done**

* Demo: three vendors onboarded in test mode, a mixed order splits and pays, each vendor fulfils its part in the vendor portal, one refund allocates correctly, a payout statement is generated and postings reconcile to Stripe balance transactions
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: split math with fees, taxes and discounts; statement determinism; fee schedule versioning.
* Integration: transfer amount assertion; vendor RLS scoping; dispute routing; payout webhook mapping.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Buy from three vendors in one cart, show the split preview, pay in test mode, fulfil one line as a vendor, refund another, and generate the monthly statements.

**Edge cases**

* Vendor Connect account restricted after the sale: transfers fail; funds stay on the platform balance with a task for staff; the vendor portal shows the requirement
* Discount code spanning vendors: allocated proportionally and the platform absorbs rounding
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-880 (hard), PAP-181 (hard), PAP-408 (soft: pattern), PAP-55, PAP-62, PAP-227 (hard), PAP-423 (soft).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/commerce/orders-fulfilment` = PAP-880.
