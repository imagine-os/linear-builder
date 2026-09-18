---
identifier: "PAP-879"
title: "Build catalog and inventory: products, variants, price lists, stock per location with the append-only movement ledger, reservations, counts, low-stock alerts, barcodes and Stripe price sync"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Commerce contract and catalog"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-177", "PAP-333", "PAP-338", "PAP-725", "PAP-877", "PAP-878"]
blocks: ["PAP-880", "PAP-881", "PAP-882", "PAP-885", "PAP-886", "PAP-888", "PAP-892"]
key: "r4/commerce/catalog-inventory"
url: "https://linear.app/paperos/issue/PAP-879/build-catalog-and-inventory-products-variants-price-lists-stock-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-879: Build catalog and inventory: products, variants, price lists, stock per location with the append-only movement ledger, reservations, counts, low-stock alerts, barcodes and Stripe price sync

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Implement the catalog and stock half of the model: products and variants with options, images and barcodes, price lists per audience and currency, stock per location derived from an append-only movement ledger with reservations and counts, low-stock alerts through notifications, and Stripe Product and Price sync so Checkout and subscriptions reference real catalog entries.

**Scope**

In: `packages/commerce/src/catalog/` and `inventory/`: tables from the model; `CatalogPort` (`resolvePrice(variant, audience, currency, qty, date)` applying price list rules and quantity breaks) and `InventoryPort` (`move`, `reserve` with TTL and `release`, `count` with variance movements, `stock(variant, location)` cached view); datasets `products`, `variants`, `stock_levels`, `stock_movements` registered for the grid (PAP-165) with the record surface (PAP-333) and a `stock` record tab. Console pages `/commerce/products` (grid, product editor with variant matrix generator, images via PAP-37 with variants), `/commerce/inventory` (levels by location, adjust, transfer, count sheet), spec files for each. Barcodes: `barcode` field type from PAP-911 with scanner input (PAP-260 or keyboard wedge), label printing for shelf and product labels. Stripe sync job: create or update Product and Price on the platform or the connected account (PAP-181 setting) with idempotency; archived variants archive prices; `stripePriceId` stored; alerts kind `stock.low` via PAP-136 when `onHand − reserved < reorderPoint`.

Out: Orders (next issue). Purchase receipts create movements but live in purchasing. Serial and lot tracking (v0.3).

**Spec**

* Movements are immutable rows with a trigger rejecting UPDATE and DELETE (PAP-392 pattern); corrections are new `adjustment` movements with a reason; `onHand` cache rebuilt nightly and verified against the sum
* Reservations expire (default 15 minutes for carts, configurable per channel); a fulfilment converts the reservation into a `sale` movement in one transaction
* Weighted-average cost per variant per location updates on receipts; sale movements carry the cost at the moment of sale for COGS postings (owned by orders)
* Price resolution is pure and testable: list precedence, audience match, validity window, quantity breaks, tax-inclusive flag per price list
* Variant matrix generation is bounded (200 variants per product) with a clear message beyond

**Interface contract**

Provides: `CatalogPort` and `InventoryPort` default adapters, tables and datasets, console pages, barcode field type usage, Stripe sync job, `product.updated`, `stock.moved|low` events. Consumes: the model and contract, Stripe client (PAP-177, PAP-181), field types (PAP-338), record surface (PAP-333), notifications (PAP-136), files (PAP-37), grid (PAP-165), labels and scanner (PAP-911, PAP-260). Consumed by: PAP-880, PAP-881, PAP-882, PAP-886 (prices), engagement loyalty (order lines), packs wave 2 and 3, PAP-183 valuation report.

**Definition of done**

* Demo retail tenant with 50 products and 300 variants across two locations; a 500-movement fixture sums to the cached levels; concurrent reservations for the last unit yield one success; Stripe test account shows synced prices; low-stock alert fires; label printed
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: price resolution over 40 fixtures; matrix generation; weighted-average cost; movement immutability trigger.
* Integration: reserve and release under concurrency; count variance movements; Stripe sync idempotency with recorded fixtures.
* E2E: product editor, variant matrix, scan a barcode into the inventory adjust form; screenshots.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Create a T-shirt with size and colour variants, receive 20 units into the warehouse, scan one at the counter to check stock, adjust a count, and open Stripe test mode to show the synced prices.

**Edge cases**

* Variant deleted with stock on hand: refused; must be adjusted to zero or archived with a note
* Two locations count the same variant simultaneously: each count is its own movement; the level is the sum; no lost update
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-878 and PAP-877 (hard), PAP-177 (hard: sync), PAP-338, PAP-333, PAP-136 (soft), PAP-911 (soft: text fallback).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 7 round-4 file keys in this description to Linear identifiers: `r4/commerce/contract-publish` = PAP-877, `r4/commerce/customer-subscriptions` = PAP-886, `r4/commerce/domain-model` = PAP-878, `r4/commerce/orders-fulfilment` = PAP-880, `r4/commerce/pos-mode` = PAP-881, `r4/commerce/purchasing-ap` = PAP-882, `r4/design-system/labels-barcodes-qr` = PAP-911.
