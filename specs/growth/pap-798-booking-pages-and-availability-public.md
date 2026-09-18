---
identifier: "PAP-798"
title: "Booking pages and availability: public scheduling links with availability rules, Google and Microsoft calendar busy-time checks, meeting activities, reminders and reschedule links"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-168", "PAP-346", "PAP-352", "PAP-790"]
blocks: []
key: "r4/growth/booking-pages-and-availability"
url: "https://linear.app/paperos/issue/PAP-798/booking-pages-and-availability-public-scheduling-links-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:26.667Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-798: Booking pages and availability: public scheduling links with availability rules, Google and Microsoft calendar busy-time checks, meeting activities, reminders and reschedule links

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Salons, clinics, agencies and sales teams all book meetings. PAP-352 decides whether [Cal.com](<http://Cal.com>) is embedded or borrowed; either way PaperOS needs the CRM-facing half: a booking link per staff member or team, availability, a public page and a `meeting` activity with reminders.

**Scope**

In: `booking_event_type (owner_user_id|team, slug, duration_min, buffer, availability jsonb weekly rules, timezone, location: video|phone|in_person, questions jsonb, round_robin)`, `booking (event_type_id, contact_id, starts_at, ends_at, status: confirmed|cancelled|rescheduled|no_show, calendar_event_id)`; public `/book/:slug` page with slot picker honouring tenant branding; busy-time checks via Google Calendar and Microsoft Graph (OAuth per PAP-57, tokens via PAP-353) or the embedded [Cal.com](<http://Cal.com>) adapter behind a `BookingProviderPort` when PAP-352 says embed; ICS attachments and calendar event creation; reminders and reschedule and cancel links through PAP-370 and PAP-405 SMS; `crm_activity kind meeting` and lead creation for unknown bookers with consent capture.

Out: payments at booking (deposits issue in business-core), resource booking (rooms, chairs: restaurant and salon packs model them as tables; v0.3 links them).

**Spec**

* Slot computation is pure and tested across DST and timezone boundaries; double booking prevented with an advisory lock per owner and slot.
* Provider port has `fixture` (deterministic busy times), `google`, `microsoft` and `calcom` adapters; CI uses `fixture` only.
* Reminders at 24 h and 1 h via PAP-136 kinds; the public page is rate limited (PAP-267) and stores `ip_hash` only.

**Interface contract**

Provides: `booking.*` procedures, `BookingProviderPort`, public route, `BookingWidget` for portal and landing pages, activity source `meeting`, notification kinds `booking.*`. Consumes: CRM schema, OSS mode decision (PAP-352), calendar view (PAP-168) for staff schedule, OAuth (PAP-57), encryption (PAP-353), email and SMS (PAP-370, PAP-405 soft), consent centre, rate limits (PAP-267).

**Definition of done**

* Slot engine property tests; no double booking under 50 concurrent requests; fixture adapter end to end; screenshots at 320, 375, 768, 1024, 1920 light and dark; axe clean.
* `docs/growth/booking.md`; CHANGELOG.

**Test plan**

* Unit: availability rules, buffers, DST, round robin fairness, ICS generation.
* E2E: create an event type, open the public page, book as a new visitor, see the meeting on the contact timeline and the staff calendar, reschedule via the link.

**Demo**

Reviewer publishes a 30-minute link, books a slot in a private window and watches the meeting appear on the calendar and the contact. Under two minutes.

**Edge cases**

* Owner's calendar token expired: slots computed from rules only with a banner to the owner.
* Booker's timezone differs: both shown on the confirmation.
* Cancellation inside the buffer: allowed, marked late.

**Dependencies**

Hard: PAP-790, PAP-352, PAP-168. Soft: PAP-57, PAP-353, PAP-370, PAP-405, PAP-267, PAP-791.

**Agent**

Builder: Beacon (CRM Builder) with Nova on the slot picker. Reviewer: Sentinel (Edge Case Hunter for time zones, Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791, `r4/growth/crm-schema-routers-page-specs` = PAP-790.
