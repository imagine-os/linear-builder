---
identifier: "PAP-783"
title: "Point of sale with Stripe Terminal: in-person checkout screen from the item catalogue, reader pairing and simulated reader, tips, receipts and daily Z-report postings"
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
blockedBy: ["PAP-181", "PAP-397", "PAP-774"]
blocks: []
key: "r4/business-core/stripe-terminal-pos"
url: "https://linear.app/paperos/issue/PAP-783/point-of-sale-with-stripe-terminal-in-person-checkout-screen-from-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:42.876Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-783: Point of sale with Stripe Terminal: in-person checkout screen from the item catalogue, reader pairing and simulated reader, tips, receipts and daily Z-report postings

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Retail, restaurants, salons and clinics take payments at a counter. A simple POS on the item catalogue with Stripe Terminal (simulated reader in test mode) turns the platform into a till without building a payment processor, and posts each day's sales the same way invoices do.

**Scope**

In: `/pos` route (staff, tablet-first layout, offline-tolerant cart in the PAP-148 queue), item grid with search and categories, cart with discounts (PAP-778), tips, split tender (card via Terminal, cash, other), Stripe Terminal JS SDK with `simulated: true` readers in test mode and reader registration in settings, `fin_pos_sale` records creating a paid `receipt` document per sale through PAP-395 and PAP-397 postings, cash drawer sessions with opening float and Z-report at close (sales by tender, tips payable, over or short posting), receipt print via PAP-235 and email or SMS receipt.

Out: Tap to Pay on phones (Tauri capability spike later), kitchen display, table management (restaurant pack tables are records), inventory decrement beyond the hook to PAP-775.

**Spec**

* Every sale is a `fin_transaction kind payment source pos` and a receipt document; refunds go through the refunds issue; tips post to `tips_payable`.
* Card entry happens only on the reader or Stripe-hosted surfaces (PAP-359); the app never sees PAN; Semgrep rule set applies.
* Offline: cart and cash sales queue locally and sync; card sales require connectivity and say so.
* Z-report is immutable once closed; reopening creates a new session.

**Interface contract**

Provides: `pos.*` procedures, route, Terminal connection token endpoint, `fin_pos_sale`, `fin_drawer_session`, Z-report dataset `finance.posDaily`, receipt templates. Consumes: items (PAP-774), Connect account (PAP-181), documents and postings (PAP-395, PAP-397), discounts, inventory hook, offline queue (PAP-148), PDF theme (PAP-235), SMS via growth outreach provider (optional).

**Definition of done**

* Simulated-reader flow recorded: three sales (card, cash, split with tip), close drawer, Z-report balanced to the ledger; no live key.
* Tablet screenshots at 768, 1024 landscape and 375; keyboard and touch tests; `docs/finance/pos.md` with the reader activation NJ checklist; CHANGELOG.

**Test plan**

* Unit: cart arithmetic with `Money`, split tender, tip allocation, Z-report totals, over or short.
* E2E: open a drawer, sell two items with a promo code paid by simulated card, one cash sale, close the drawer and open the Z-report and journal.

**Demo**

Reviewer rings up a coffee and a pastry, pays on the simulated reader, prints the receipt PDF, closes the day and reads the Z-report. Under two minutes.

**Edge cases**

* Reader disconnects mid-payment: PaymentIntent status polled; sale stays `pending` until resolved.
* Cash sale offline then price change online: sale keeps its snapshot.
* Tip exceeds a tenant cap: confirmation required.

**Dependencies**

Hard: PAP-774, PAP-181, PAP-397. Soft: PAP-778, PAP-775, PAP-148, PAP-235.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/business-core/discounts-and-promo-codes` = PAP-778, `r4/business-core/inventory-stock-and-cogs` = PAP-775, `r4/business-core/item-catalogue` = PAP-774.
