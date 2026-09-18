---
identifier: "PAP-778"
title: "Discounts and promotion codes: tenant-level coupon rules for quotes, invoices and checkout plus Stripe Coupons and Promotion Codes for platform plans"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-177", "PAP-395"]
blocks: ["PAP-408"]
key: "r4/business-core/discounts-and-promo-codes"
url: "https://linear.app/paperos/issue/PAP-778/discounts-and-promotion-codes-tenant-level-coupon-rules-for-quotes"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:41.678Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-778: Discounts and promotion codes: tenant-level coupon rules for quotes, invoices and checkout plus Stripe Coupons and Promotion Codes for platform plans

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Two audiences need discounts: PaperOS itself (plan promotions, referral credits in PAP-408) and every tenant selling to its customers. One `fin_discount` model covers percentage, fixed and free-period rules with limits, redemption tracking and correct revenue contra postings, syncing to Stripe where Stripe collects the money.

**Scope**

In: `fin_discount (scope: platform|tenant, code, kind: percent|fixed|free_periods, value, currency?, applies_to: all|items[]|plans[], starts_at, ends_at, max_redemptions, per_customer_limit, min_subtotal_minor, stackable, status)`, `fin_discount_redemption`; validation `discounts.validate(code, cart)`; document-level and line-level discount application in PAP-395 `computeTotals` (contra-revenue line to `discounts_given`); Checkout `discounts` and `allow_promotion_codes` on PAP-396 sessions; platform scope synced to Stripe Coupons and Promotion Codes for PAP-177 plans; settings pages for both scopes; redemption dataset.

Out: loyalty points and gift cards (v0.3, noted in the matrix), affiliate reward calculation (PAP-408 consumes credits from here).

**Spec**

* Code normalisation: uppercase, Crockford-safe, profanity filter shared with PAP-407.
* Redemption counting is transactional with an advisory lock per code; `max_redemptions` never exceeded under 50 parallel checkouts (test).
* Discount lines snapshot the rule at issue; deleting a rule never changes issued documents.
* Platform sync idempotent on `metadata.paperos_discount_id`; credit-type rewards from PAP-408 become Stripe customer balance adjustments through this module's `discounts.grantCredit`.

**Interface contract**

Provides: `fin_discount`, `discounts.validate|apply|grantCredit|sync`, `computeTotals` discount hook, Checkout wiring, datasets `finance.discounts`, `finance.redemptions`. Consumes: documents and totals (PAP-395), Checkout (PAP-396), Stripe client and plans (PAP-177), items (PAP-774, soft), profanity filter (PAP-407, soft).

**Definition of done**

* Unit, concurrency and Playwright green; Stripe sync verified in test mode with recorded fixtures; screenshots at 375, 1024, 1920 in three themes.
* PAP-408 credit rewards flow through `grantCredit` (comment on PAP-408).
* `docs/finance/discounts.md`; CHANGELOG.

**Test plan**

* Unit: each rule kind, stacking rules, limits, min subtotal, code normalisation, contra-revenue posting.
* E2E: create a 10 percent code, apply it on an invoice, pay via Checkout with the promotion code and see the contra-revenue line.

**Demo**

Reviewer creates `WELCOME10`, adds it to a quote, accepts and pays it in test mode and sees the discount line and redemption count. Under two minutes.

**Edge cases**

* Expired code at checkout time: rejected with the expiry date.
* Percentage on a multi-rate tax invoice: applied pre-tax per line with `Money.allocate`.
* Stripe coupon deleted in the Dashboard: sync recreates it and comments in the settings page.

**Dependencies**

Hard: PAP-395, PAP-177. Soft: PAP-396, PAP-407, PAP-774. Blocks PAP-408 (credit rewards).

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Edge Case Hunter for stacking, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/item-catalogue` = PAP-774.
