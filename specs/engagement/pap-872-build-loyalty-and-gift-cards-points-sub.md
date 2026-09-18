---
identifier: "PAP-872"
title: "Build loyalty and gift cards: points sub-ledger with earn and redeem rules, tiers, rewards at checkout, gift cards as liabilities with codes and balances, fraud limits"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Memberships, loyalty, announcements and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-179", "PAP-394", "PAP-396", "PAP-408", "PAP-871"]
blocks: []
key: "r4/engagement/loyalty-gift-cards"
url: "https://linear.app/paperos/issue/PAP-872/build-loyalty-and-gift-cards-points-sub-ledger-with-earn-and-redeem"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:58.655Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-872: Build loyalty and gift cards: points sub-ledger with earn and redeem rules, tiers, rewards at checkout, gift cards as liabilities with codes and balances, fraud limits

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Reward repeat business correctly on the books: a points sub-ledger built on PAP-179 (points are a liability with an assumed value), earn rules on bookings, orders and referrals, tiers by rolling points, rewards redeemed at checkout and POS, gift cards as prepaid liabilities with codes, balances and partial redemption, and fraud limits borrowed from PAP-408.

**Scope**

In: `loyalty_program` (points per Money unit, tiers, expiry policy, assumed value per point), `loyalty_account` (contact, balance cache, tier), `loyalty_entry` (earn|redeem|expire|adjust, points, source EntityRef) posting to ledger accounts `loyalty_liability` and `loyalty_expense` through PAP-394 rules; `gift_card` (code hash, initial and remaining Money, expiry per jurisdiction rules, purchaser, recipient), `gift_card_txn`. Earn triggers: `booking.completed`, `order.paid` (commerce), `referral.qualified` (PAP-407) via rules; redeem as a discount line on PAP-395 documents and a payment method in Checkout (PAP-396 gains `giftCard` and `points` tender types) and POS. Portal: balance, history, rewards catalogue, gift card purchase (Checkout) and send by email with a printable card (print kit); staff: adjust with reason (approval above a threshold via PAP-849), lookup by code. Fraud: velocity limits per account and IP, redemption caps per day, code entropy and attempt lockouts, adjustments audited (PAP-38) and reviewed weekly.

Out: Coalition or cross-tenant programs. Breakage accounting automation beyond expiry entries (finance decides in PAP-183 reports).

**Spec**

* Points and gift card balances are never stored as the truth: balances derive from entries and ledger postings; the cache is rebuilt by `rebuildBalances` (PAP-394 pattern) and verified nightly
* Gift card codes are stored hashed (like passwords); the plaintext appears once to the purchaser or recipient and in the printable card
* Redemptions are idempotent by document line or POS transaction id; a voided document reverses the redemption entry
* Expiry follows the program policy but never earlier than the jurisdiction minimum recorded in the PAP-126 compliance profile (many places forbid gift card expiry)
* Every entry emits `loyalty.*` or `giftcard.*` events for workflows and segments

**Interface contract**

Provides: `LoyaltyPort.earn|redeem|balance|issueGiftCard|redeemGiftCard`, tables and posting rules, portal pages, printable gift card, Checkout tender types, fraud limits. Consumes: ledger and posting rules (PAP-179, PAP-394), documents and Checkout (PAP-395, PAP-396), referral qualification and fraud rules (PAP-407, PAP-408), approvals, print kit (PAP-235), audit (PAP-38), compliance profile (PAP-126). Consumed by: commerce POS and orders, booking deposits, migration packs (salon, restaurant, retail), growth segments (tier as attribute).

**Definition of done**

* Demo customer earns points on two bookings, reaches a tier, redeems a reward on an invoice; a $50 gift card is bought, emailed, partially redeemed twice; ledger liability accounts reconcile to balances; velocity limit proven
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: earn and tier math; expiry policy floor; code hashing and lockout; idempotent redemption.
* Integration: redeem → document line → posting → void → reversal; nightly balance verification; approval above threshold.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Buy a gift card in the portal, redeem half of it at the demo POS and the rest on an invoice; open the ledger to show the liability shrinking; then earn points and redeem a reward.

**Edge cases**

* Gift card purchased on a connected account then refunded by the purchaser: remaining balance is frozen, partial redemptions already made are charged back to the purchaser per policy; the flow needs an approval
* Points program closed: remaining balances expire on a notified date with `expire` entries and a final liability release
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-871 (soft: shares portal and Connect setup), PAP-179, PAP-394, PAP-396 (hard), PAP-408 (soft: fraud rules), PAP-849 (soft).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/engagement/memberships-checkin` = PAP-871, `r4/workflows/approvals-framework` = PAP-849.
