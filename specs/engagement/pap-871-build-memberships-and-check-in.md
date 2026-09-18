---
identifier: "PAP-871"
title: "Build memberships and check-in: membership plans on Stripe Connect subscriptions for the tenant's customers, member portal card with QR, check-in kiosk and scanner, attendance and lapse handling"
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
blockedBy: ["PAP-23", "PAP-177", "PAP-181", "PAP-260", "PAP-394", "PAP-864"]
blocks: ["PAP-872"]
key: "r4/engagement/memberships-checkin"
url: "https://linear.app/paperos/issue/PAP-871/build-memberships-and-check-in-membership-plans-on-stripe-connect"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:58.548Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-871: Build memberships and check-in: membership plans on Stripe Connect subscriptions for the tenant's customers, member portal card with QR, check-in kiosk and scanner, attendance and lapse handling

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Serve gyms, clubs, coworking spaces, churches and studios: membership plans billed through the tenant's Stripe Connect account (distinct from PAP-177, which bills the tenant), a member portal card with a rotating QR code, a check-in kiosk (PAP-23) and staff scanner (PAP-260 barcode plugin or keyboard wedge), class bookings limited by plan entitlements, attendance datasets, and lapse, pause and cancel flows with ledger postings.

**Scope**

In: `membership_plan` (price Money, interval, entitlements: class credits per period, booking limits, guest passes, access hours), `membership` (contact, plan, Stripe subscription id on the connected account, status trialing|active|past_due|paused|cancelled|lapsed, period), `checkin` (membership, location, method qr|scan|manual|kiosk, at). Billing: Stripe Billing on the connected account (PAP-181) with Checkout for enrolment (PAP-396 pattern), webhook state mapping, dunning through the PAP-180 WP4 reminders, proration on plan change; posting rules `membership.invoice.paid|refunded` (PAP-394) to revenue and Connect fees. Portal: `/portal/membership` (plan, status, next charge, pause, cancel per policy, update payment method through the Stripe portal), member card with QR (PAP-911) rotating every 60 s and an offline-capable static fallback; class credits shown on booking. Kiosk `/kiosk/checkin` (PAP-23 mode) with camera scan and name search; staff scanner in the console; check-in rules (active status, access hours, credits) with clear denial reasons; attendance dataset and dashboard blocks; lapse job.

Out: Access-control hardware integration (door locks; v0.3 via webhook). Family and corporate memberships (v0.3). Marketplace memberships.

**Spec**

* Money only moves through Stripe; the membership status is derived from subscription webhooks, never set by hand except `paused` and `cancelled` through Stripe API calls
* QR payloads are signed, contain only the membership id and expiry, and are verified server-side; a screenshot older than 60 s fails unless the static fallback (per-tenant setting) is on
* Booking engine integration: class bookings consume credits inside the booking transaction; cancellation within policy refunds the credit
* Kiosk works offline for check-in by caching the active member list (PAP-148 outbox for the check-in rows) and refuses when the cache is older than 24 h
* Every status change emits `membership.*` events for workflows (welcome sequence, lapse win-back) and segments

**Interface contract**

Provides: `MembershipPort.plans|enrol|checkIn|status`, tables, portal pages and card, kiosk and scanner, posting rules, `membership.*` events, attendance dataset. Consumes: booking engine (credits), Connect and Stripe client (PAP-181, PAP-177), posting rules (PAP-394), reminders and dunning (PAP-397), kiosk mode (PAP-23), barcode plugin (PAP-260), QR component (PAP-911), offline outbox (PAP-148), portal shell (PAP-62). Consumed by: PAP-872, commerce POS (member pricing), migration packs (gym, church, coworking), assistant Front Desk ("is my membership active?").

**Definition of done**

* A member enrols in test mode, sees the card, checks in at the kiosk by QR, books a class with a credit; a past-due fixture is denied with a reason; ledger shows the postings; offline kiosk check-in syncs
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: entitlement math; QR signing and expiry; status mapping from webhook fixtures; access-hours rules across DST.
* Integration: Checkout → webhook → active; proration on plan change; lapse job; credit consumption inside the booking transaction under concurrency.
* E2E: kiosk on a tablet width with camera mock; portal pause and cancel; screenshots.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Enrol in the gym demo's monthly plan in test mode, open the member card on a phone, check in on the kiosk tablet, book a class, then simulate a failed payment and watch the card go past-due with the dunning email.

**Edge cases**

* Stripe webhook arrives before the enrolment row commits: the handler retries with backoff (PAP-43) until the row exists, then maps status
* Member cancels with remaining credits: policy decides whether credits survive to period end; the portal states it plainly before confirming
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-864 (hard), PAP-181, PAP-177, PAP-394 (hard), PAP-23, PAP-260, PAP-148 (soft), PAP-911 (soft: inline QR fallback).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/design-system/labels-barcodes-qr` = PAP-911, `r4/engagement/booking-engine` = PAP-864, `r4/engagement/loyalty-gift-cards` = PAP-872.
