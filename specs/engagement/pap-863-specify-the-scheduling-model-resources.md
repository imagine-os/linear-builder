---
identifier: "PAP-863"
title: "Specify the scheduling model: resources, services, availability rules on the recurrence engine, holds, bookings, buffers, time zones and cancellation policies"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Engagement contract and booking core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-27", "PAP-187", "PAP-302", "PAP-344", "PAP-352", "PAP-791"]
blocks: ["PAP-862", "PAP-864"]
key: "r4/engagement/scheduling-model"
url: "https://linear.app/paperos/issue/PAP-863/specify-the-scheduling-model-resources-services-availability-rules-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:22.347Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-863: Specify the scheduling model: resources, services, availability rules on the recurrence engine, holds, bookings, buffers, time zones and cancellation policies

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Define scheduling once for salons, clinics, gyms, trades and meeting rooms: resources (people, rooms, equipment) with availability rules expressed as recurrence sets, services with durations, buffers and required resource kinds, holds that expire, bookings with participants and policies, all in the tenant and resource time zones, recording what the [Cal.com](<http://Cal.com>) spike (PAP-352) taught us to borrow.

**Scope**

In: `docs/engagement/scheduling.md` and Zod schemas: `Resource` (`kind person|room|equipment`, `timezone`, `capacity`, `links: { userId?, fin_employee? }`), `Service` (`duration`, `bufferBefore|After`, `price Money?`, `resourceRequirements[]`, `bookableBy audiences`, `leadTime`, `horizon`, `cancellationPolicy`), `AvailabilityRule` (`rrule` via the recurrence engine, `window`, `kind available|blocked`, source `manual|calendar-sync|shift`), `Hold` (`expiresAt`), `Booking` (`service`, `resources[]`, `participants[] (contacts)`, `start/end`, `status held|confirmed|rescheduled|cancelled|no_show|completed`, `source portal|public|staff|assistant`, `payment?`, `notes`). Availability algorithm as a written spec: rules ∪ synced busy ∪ existing bookings → free intervals per resource → slot generation per service (step, alignment) → intersection across required resource kinds → lead time and horizon → capacity for group services. Time zones: every rule stores its zone; slots are generated in the resource zone and presented in the viewer zone (PAP-27 helpers); DST transitions handled by the recurrence engine tests. Policies: cancellation windows and fees (Money), no-show handling, reschedule limits, deposit requirement; group services (classes) with capacity and a FIFO waitlist.

Out: Engine implementation. UI. Staff shift planning (commerce HR reuses the availability rule shape).

**Spec**

* Double-booking prevention is a database guarantee: `booking_resource` rows carry a `tstzrange` with an exclusion constraint per resource; holds use the same table with a TTL so the invariant covers both
* Bookings link to CRM contacts (PAP-187) as participants; a participant without a contact creates one with consent status `transactional` (PAP-187 WP0) so reminders may be sent
* Money on bookings uses the PAP-395 document model: a deposit or fee is an invoice line, never a separate charge path
* Every booking status change emits an event carrying `previous`, `by ActorRef` and `reason`, which reminders, surveys and workflows consume

**Interface contract**

Provides: `docs/engagement/scheduling.md`, schemas `Resource`, `Service`, `AvailabilityRule`, `Hold`, `Booking`, the availability algorithm spec, exclusion-constraint rule, policy model. Consumes: `Money`/`EntityRef` (PAP-302), calendar view time model (PAP-344), OSS spike findings (PAP-352), Intl and timezone helpers (PAP-27), CRM contacts (PAP-187), recurrence engine (PAP-908). Consumed by: every scheduling issue here; commerce HR shifts; assistant Front Desk tools; migration packs (`services[]`, `resources[]` in `pack.yaml`).

**Definition of done**

* Document and schemas merged; migration with exclusion constraint and RLS; three worked examples (salon chair, clinic room plus doctor, gym class of 12) as JSON fixtures that validate
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schema fixtures; the availability algorithm as a pure function against 25 fixture days including DST forward and back, buffers, capacity and lead time.
* Review: Sentinel checks the consent path for participants and the exclusion constraint against concurrent holds.

**Demo**

Walk the clinic example: a doctor and a room with different rules, a 30-minute service with a 10-minute buffer; show the generated slots for a patient in another time zone.

**Edge cases**

* Resource moves time zone (staff relocates): rules keep their original zone; the change is a new rule version
* Service requiring two resource kinds where only one is free: no slot; the report explains which kind blocked

**Dependencies**

PAP-302, PAP-344 (hard), PAP-908 (hard), PAP-352, PAP-27, PAP-187 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/recurrence-engine` = PAP-908.
