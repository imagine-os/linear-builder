---
identifier: "PAP-864"
title: "Build the booking engine: availability computation, slot search, holds with TTL, exclusion-constraint conflict prevention, reschedule and cancel policies, group capacity and waitlist"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Engagement contract and booking core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-303", "PAP-304", "PAP-556", "PAP-558", "PAP-565", "PAP-862", "PAP-863"]
blocks: ["PAP-865", "PAP-866", "PAP-871", "PAP-876"]
key: "r4/engagement/booking-engine"
url: "https://linear.app/paperos/issue/PAP-864/build-the-booking-engine-availability-computation-slot-search-holds"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-864: Build the booking engine: availability computation, slot search, holds with TTL, exclusion-constraint conflict prevention, reschedule and cancel policies, group capacity and waitlist

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Implement the model as `SchedulingPort`: `availability()` fast enough for a booking page, `hold()` that reserves for 10 minutes, `book()` that converts a hold or books directly under the exclusion constraint, `reschedule()` and `cancel()` that apply policies and fees, capacity and waitlist for group services, and events for everything.

**Scope**

In: `packages/engagement/src/scheduling/`: tables from the model; `availability({ serviceId, range, viewerTz, resourceIds? })` with a per-resource cached interval set (invalidated by rule, booking and sync events), p95 under 150 ms for a 30-day range; `hold` (`expires_at = now() + 10 min`, sweeper job PAP-43); `book` with `Idempotency-Key` (PAP-304) and the exclusion constraint as the last line of defence. Policies: `reschedule` re-runs availability and keeps the booking id; `cancel` computes the fee from the policy and creates a PAP-395 document line when non-zero; `no_show` and `completed` transitions by staff or by a job after end time (configurable). Group services: capacity check inside the transaction; `waitlist` FIFO with automatic promotion on cancellation and a 2-hour claim window notification. oRPC `scheduling.*` procedures with audience rules (customers only see their own bookings and public availability), datasets `bookings`, `resources`, `services` registered for views and the PAP-344 calendar.

Out: Pages and reminders (next issue). Calendar sync (own issue). Payments UI (PAP-396 handles the pay page).

**Spec**

* Availability never reads other tenants and never exposes other customers' booking details; public availability returns only free slots, never occupancy reasons
* Holds count against capacity; two customers cannot hold the last spot; the sweeper releases expired holds every minute and emits `booking.hold_expired`
* Rescheduling within the cancellation window applies the policy fee unless staff override with a reason (audited)
* All times stored as `timestamptz`; the API accepts and returns ISO strings with offsets plus the resource zone id
* A booking for a resource linked to a staff user writes an `AvailabilityRule(kind blocked)` shadow so shift and calendar views agree

**Interface contract**

Provides: `SchedulingPort` default adapter, tables, `scheduling.*` procedures, datasets, hold sweeper and status jobs, `booking.*` events. Consumes: the model and contract, recurrence engine, jobs (PAP-43), idempotency (PAP-304), events (PAP-303), documents for fees (PAP-395), calendar view (PAP-344). Consumed by: PAP-865, PAP-866, PAP-871 (class bookings), assistant Front Desk tools, commerce HR shifts, workflows triggers.

**Definition of done**

* Concurrency test: 200 parallel `book` calls for one slot yield exactly one booking and 199 `SLOT_TAKEN`; availability p95 under 150 ms on the demo tenant; waitlist promotion proven; staff calendar shows bookings live
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: interval math with buffers and capacity; policy fee computation; waitlist ordering.
* Integration: exclusion constraint under concurrency; hold expiry; idempotent book replay; reschedule inside and outside the window.
* Load: k6 (PAP-242) availability at 50 rps for a 30-day range.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Open the staff calendar for the salon demo, book a client into a free slot from the record panel, try to double-book the chair from a second window and get the conflict, then cancel inside the window and see the fee line.

**Edge cases**

* Availability rule deleted with future bookings: bookings stay; the calendar shows them as "outside availability" for staff to resolve
* Clock skew on the client: holds and slot validity are decided by database time and returned to the client
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-863 and PAP-862 (hard), PAP-43, PAP-304, PAP-303 (hard), PAP-395, PAP-344 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/engagement/booking-pages` = PAP-865, `r4/engagement/calendar-sync` = PAP-866, `r4/engagement/contract-publish` = PAP-862, `r4/engagement/memberships-checkin` = PAP-871, `r4/engagement/scheduling-model` = PAP-863.
