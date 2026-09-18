---
identifier: "PAP-865"
title: "Build booking pages and reminders: public /book/:slug flow, portal bookings, staff calendar actions, deposits via Checkout, reminders and no-show follow-ups through notifications"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Messaging channels, help center and surveys"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-62", "PAP-136", "PAP-344", "PAP-396", "PAP-431", "PAP-585", "PAP-725", "PAP-862", "PAP-864"]
blocks: ["PAP-876"]
key: "r4/engagement/booking-pages"
url: "https://linear.app/paperos/issue/PAP-865/build-booking-pages-and-reminders-public-bookslug-flow-portal-bookings"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-865: Build booking pages and reminders: public /book/:slug flow, portal bookings, staff calendar actions, deposits via Checkout, reminders and no-show follow-ups through notifications

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let customers book without calling: a public booking page per tenant and per service under the tenant brand and domain, a portal flow to view, reschedule and cancel, staff actions on the calendar view, deposits through PAP-396 Checkout, and reminder and follow-up notifications with quiet hours.

**Scope**

In: Public route `/book/:slug` (spec) on the public layout: service picker, resource picker (optional, "any available"), month and day slot picker in the viewer time zone, details form on the forms runtime (PAP-854) with per-service intake questions, hold on slot select, confirm; deposit step opens Checkout; confirmation page with add-to-calendar (ICS) and manage link. Portal `/portal/bookings` (list, detail, reschedule, cancel with policy explanation); `portal.home.cards` fill for the next booking. Staff: PAP-344 calendar actions (create, drag to reschedule with policy prompt, mark no-show or completed), record panel tab `bookings` (PAP-333) on contacts; bulk reminder resend. Reminders: kinds `booking.confirmed`, `booking.reminder` (24 h and 2 h defaults per service, email and SMS when PAP-910 exists), `booking.changed`; no-show follow-up template with a rebook link; all through PAP-136 with PAP-324 quiet hours.

Out: Calendar sync. Payments beyond deposits. Marketplace-style multi-vendor booking.

**Spec**

* Slot picker shows only slots valid at render time and revalidates on select; a taken slot shows an inline message and refreshes, never a dead end
* Public page budget: under 120 KB JS, LCP under 2.5 s on a mid-range phone (PAP-87), no third-party scripts except Turnstile when enabled
* Manage links are signed tokens tied to the booking and participant email; they allow reschedule and cancel only within policy
* Reminders are idempotent per booking and kind; a rescheduled booking cancels pending reminders and schedules new ones
* Every page has portal and public specs with denied and empty states; screenshots at 375, 768, 1024, 1920

**Interface contract**

Provides: `/book/:slug`, portal bookings pages, calendar actions, record tab, notification kinds `booking.*`, ICS attachment, manage-link tokens. Consumes: booking engine, portal shell (PAP-62), Checkout (PAP-396), notifications and quiet hours (PAP-136, PAP-324), custom domains and branding (PAP-431, PAP-75), calendar view (PAP-344), record panel (PAP-333), forms runtime, SMS channel (soft). Consumed by: migration packs (salon, clinic, gym booking pages), assistant Front Desk (`startBooking` handoff), growth (booking confirmations as sequence triggers).

**Definition of done**

* A customer books with a deposit on a phone in test mode, gets a confirmation with ICS, receives the reminder in Mailpit, reschedules from the portal; staff drags a booking on the calendar; Lighthouse budget met
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: slot picker state machine; manage token scope; reminder scheduling on reschedule.
* E2E: public flow at 375 and 1920 with a screen reader script; portal reschedule within and outside policy; no-show follow-up.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Book a haircut on the salon demo's public page from a phone with a $10 deposit, then move it from the portal and show the updated reminder schedule and the staff calendar.

**Edge cases**

* Customer books in a zone that skips the slot hour on DST day: the picker shows zone-correct times and the confirmation states both zones
* Deposit paid but hold expired during Checkout: booking is still created (payment wins) and staff are notified if it now conflicts, with a reschedule action
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-864 (hard), PAP-62, PAP-396, PAP-136 (hard), PAP-431, PAP-344, PAP-333 (soft), PAP-854 (soft: falls back to a fixed details form).

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/collab/sms-notification-channel` = PAP-910, `r4/engagement/booking-engine` = PAP-864, `r4/workflows/forms-schema-runtime` = PAP-854.
