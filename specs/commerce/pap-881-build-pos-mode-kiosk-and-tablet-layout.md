---
identifier: "PAP-881"
title: "Build POS mode: kiosk and tablet layout, cart and tenders (Terminal, cash, gift card, points, manual), Stripe Terminal adapter, offline sales queue, receipts and shift close with Z-report"
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
blockedBy: ["PAP-23", "PAP-148", "PAP-181", "PAP-235", "PAP-260", "PAP-879", "PAP-880"]
blocks: []
key: "r4/commerce/pos-mode"
url: "https://linear.app/paperos/issue/PAP-881/build-pos-mode-kiosk-and-tablet-layout-cart-and-tenders-terminal-cash"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:00.514Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-881: Build POS mode: kiosk and tablet layout, cart and tenders (Terminal, cash, gift card, points, manual), Stripe Terminal adapter, offline sales queue, receipts and shift close with Z-report

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Sell at the counter: a POS mode on the kiosk shell (PAP-23) sized for tablets and touch, a fast cart with scanner input, tenders through a `TerminalPort` (Stripe Terminal adapter, cash, gift card and loyalty points from engagement, manual), offline sales queued through the PAP-148 outbox and reconciled later, printed or emailed receipts, and shift open and close with a Z-report.

**Scope**

In: Route `/pos` (spec) in kiosk mode: product grid with categories and search, barcode scan (PAP-260 or wedge), cart with line discounts within permission limits, customer attach (CRM), tender screen; `PosPort.session` (device registration, cash drawer float), `sale` (creates and pays an order with channel `pos`), `tender`, `closeShift`. `TerminalPort`: `stripe-terminal` (server-driven readers via PAP-181 connected account, connection token endpoint, reader status), `cash` (change calculation, drawer events), `giftCard` and `points` delegating to engagement `LoyaltyPort`, `manual`; split tenders. Offline: sales for cash and gift card tenders queue in the outbox with local stock decrement; card tenders require connectivity (reader needs it too); replay is idempotent by sale id; a banner shows queued count (PAP-148 indicator). Receipts through the print kit (PAP-235) to a receipt printer (ESC/POS via browser USB or a PDF fallback) or email/SMS; shift close: counted cash vs expected, variance posting, Z-report PDF; `pos.sale.completed|shift.closed` events.

Out: Table service and kitchen display for restaurants (restaurant pack v0.3 extension). Multi-register cash management beyond per-device shifts.

**Spec**

* Cart operations are local-first and under 50 ms; price resolution uses a cached price list snapshot refreshed on shift open and on `product.updated` events
* Card data never touches PaperOS (SAQ-A, PAP-359): the reader talks to Stripe; the API only exchanges connection tokens and payment intent ids
* Offline sales cannot exceed the cached stock for goods flagged `strictStock`; others allow negative with a flag for reconciliation
* Discount authority comes from the permission engine (PAP-59) with a manager PIN override path audited
* Shift reports post cash variance through PAP-394 and are immutable once closed

**Interface contract**

Provides: `PosPort` and `TerminalPort` with adapters, `/pos` kiosk route, offline sale queue, receipts, shift and Z-report, `pos.*` events, slot `pos.tender.methods`. Consumes: orders, kiosk mode (PAP-23), offline outbox and indicator (PAP-148, PAP-272), Connect (PAP-181), scanner (PAP-260), print kit (PAP-235), loyalty and gift cards (engagement), permission engine (PAP-59), posting rules (PAP-394). Consumed by: packs (retail, restaurant, salon retail shelf), engagement (member pricing and loyalty at POS), platform-ops (device health).

**Definition of done**

* Tablet demo: scan three items, attach a customer, split cash and Terminal (simulated reader), print a receipt, go offline and sell for cash, come back and reconcile, close the shift with a Z-report; postings reconcile
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: cart math and discounts; change calculation; split tenders; offline stock guard.
* Integration: Terminal connection token and payment intent flow with the Stripe simulated reader; outbox replay idempotency; shift close variance posting.
* E2E: touch-only flow at 768 and 1024 landscape; scanner wedge input; receipt PDF snapshot.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Ring up a sale on the tablet with a simulated Terminal reader, then pull the network cable, sell two more items for cash, reconnect and watch them sync, and close the shift.

**Edge cases**

* Reader disconnects mid-payment: the intent is cancelled or confirmed by webhook; the cart waits with a clear status and never double-charges
* Same variant edited (price) during a shift: the cached price holds until shift end unless the cashier refreshes; the change is flagged on the Z-report
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-880 (hard), PAP-23, PAP-148 (hard), PAP-181 (hard), PAP-260, PAP-235 (soft), engagement loyalty (soft: tenders hidden when absent).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/commerce/orders-fulfilment` = PAP-880.
