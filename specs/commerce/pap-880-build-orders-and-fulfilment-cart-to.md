---
identifier: "PAP-880"
title: "Build orders and fulfilment: cart to order state machine, payment via Checkout on platform or connected account, pickup, delivery and shipping label port, returns and refunds with ledger postings, portal order history"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Orders, POS, purchasing, projects and HR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-182", "PAP-394", "PAP-395", "PAP-396", "PAP-725", "PAP-877", "PAP-879"]
blocks: ["PAP-881", "PAP-887", "PAP-889", "PAP-892"]
key: "r4/commerce/orders-fulfilment"
url: "https://linear.app/paperos/issue/PAP-880/build-orders-and-fulfilment-cart-to-order-state-machine-payment-via"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-opus-5"
effort: "high"
estimate: 5
dueDate: null
cycle: null
---

# PAP-880: Build orders and fulfilment: cart to order state machine, payment via Checkout on platform or connected account, pickup, delivery and shipping label port, returns and refunds with ledger postings, portal order history

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build L

**Goal**

Sell things end to end: a cart and order state machine (`draft → placed → paid → fulfilling → fulfilled → closed`, with `cancelled`, `returned`, `refunded` branches), payment through PAP-396 Checkout on the platform or the tenant's connected account with Stripe Tax, fulfilment by pickup, delivery or shipment through a `ShippingLabelPort`, returns with restocking movements, refunds as credit notes plus Stripe refunds, and a portal order history.

**Scope**

In: `OrderPort`: `create` (from portal cart, staff, POS, marketplace) reserving stock, `pay` (Checkout session or manual payment PAP-397), `fulfil` (per line, converts reservations to sale movements, posts COGS), `return` (RMA, inspection, restock or write-off movement), `refund` (credit note PAP-395 + Stripe refund with idempotency); order → `fin_document` receipt or invoice per tenant setting. Fulfilment kinds: `pickup` (ready notification and pickup code), `delivery` (routes as a dataset for the map view PAP-170, driver assignment), `shipment` (`ShippingLabelPort` with a `manual` adapter and an EasyPost adapter behind a flag; tracking number and events). Console `/commerce/orders` (grid with status tabs, order detail with timeline, fulfil and return drawers, pick list print via the print kit), portal `/portal/orders` (history, detail, tracking, return request), notification kinds `order.*`. Posting rules registered with PAP-394: `order.paid` (revenue, tax, fees, receivable), `order.fulfilled` (COGS/inventory), `order.refunded`, `return.restocked`.

Out: Storefront theme (portal pages are the storefront in v0.2; a public shop is v0.3). Carrier rate shopping. Subscriptions (own issue).

**Spec**

* Order totals are computed server-side from resolved prices and Stripe Tax (PAP-182) at placement; a price change after placement never changes an order
* Payment completion is webhook-only (SAQ-A, PAP-359); an order waiting for payment releases its reservations after the channel TTL
* Partial fulfilment and partial refund are first-class; refunds cannot exceed captured amounts minus prior refunds (server-enforced)
* Returns require an RMA; restock or write-off is a movement with cost; refund method follows the original tender
* Every transition is idempotent by `(orderId, transition, key)` and emits its event; the timeline shows actor and reason

**Interface contract**

Provides: `OrderPort` default adapter, `ShippingLabelPort` with two adapters, tables and datasets, console and portal pages, posting rules, notification kinds, `order.*` events. Consumes: catalog and inventory, Checkout and manual payments (PAP-396, PAP-397), documents and credit notes (PAP-395), posting rules (PAP-394), Stripe Tax (PAP-182), notifications (PAP-136), map view (PAP-170), print kit (PAP-235), portal shell (PAP-62). Consumed by: PAP-881, PAP-887, engagement loyalty (`order.paid` earn), growth (orders as CRM activity), assistant (order lookups), packs (retail, restaurant, ecommerce).

**Definition of done**

* Portal order paid in test mode → fulfilled by shipment with a manual label → partial return restocked → partial refund; ledger trial balance reconciles; a delivery route renders on the map; screenshots of console and portal at three widths
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: state machine exhaustive; totals and tax with recorded Stripe Tax fixtures; refund cap enforcement.
* Integration: webhook idempotency; reservation TTL release; posting traces per rule; concurrent fulfilment of the same line refused.
* E2E: portal checkout at 375; staff fulfil and return flows; pick list print.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Order two T-shirts in the portal, pay in test mode, fulfil from the console with a printed pick list and label, return one, refund it, and show the ledger entries and stock movement for each step.

**Edge cases**

* Stock oversold by a manual order (staff override): the order is placed with a backorder flag and the low-stock alert escalates; fulfilment waits for receipt
* Refund after the connected account has insufficient balance: Stripe fails; the refund stays `pending` with a staff notification and retry
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-879 (hard), PAP-396, PAP-395, PAP-394 (hard), PAP-182 (hard for tax), PAP-397, PAP-136, PAP-170 (soft).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

L: two sessions; split at the first natural seam if the first session does not reach the integration test.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/commerce/catalog-inventory` = PAP-879, `r4/commerce/marketplace-model` = PAP-887, `r4/commerce/pos-mode` = PAP-881.
