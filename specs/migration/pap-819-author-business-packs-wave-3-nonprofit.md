---
identifier: "PAP-819"
title: "Author business packs wave 3: nonprofit, school, church, gym and salon, with donors and pledges, enrolment, membership billing, class schedules and appointment booking structures"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Business migrations"
state: "Backlog"
parent: "PAP-207"
children: []
blockedBy: ["PAP-426", "PAP-427"]
blocks: []
key: "r4/migration/packs-wave-3-nonprofit-school-church-gym-salon"
url: "https://linear.app/paperos/issue/PAP-819/author-business-packs-wave-3-nonprofit-school-church-gym-and-salon"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:50.126Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-819: Author business packs wave 3: nonprofit, school, church, gym and salon, with donors and pledges, enrolment, membership billing, class schedules and appointment booking structures

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Wave 3 covers community and membership businesses whose shape is people and recurring relationships rather than products: donors and pledges, students and enrolment, congregations and giving, members and classes, clients and appointments. They are the strongest test of segments, recurring billing and booking structures the platform claims to cover.

**Scope**

In: `packages/import/templates/{nonprofit,school,church,gym,salon}/`: nonprofit (donors, donations and pledges with fund dimensions, grants pipeline, restricted and unrestricted fund accounts, year-end statement doc); school (students, guardians, courses, enrolments, terms calendar, tuition schedules, attendance form view); church (members and households, giving with fund dimensions, groups, events calendar, volunteer scheduling); gym (members, membership plans as recurring schedules, class schedule calendar with capacity, check-ins, churn segment, win-back sequence); salon (clients, services as items, stylists, appointments calendar with booking structure for PAP-798, product retail items, rebooking sequence); role presets; previews.

Out: donation receipts tax compliance beyond a template note, LMS features, church management integrations, POS hardware.

**Spec**

* Fund accounting uses the PAP-769 `fund` dimension where present, else tags with a report line.
* Membership and tuition billing structures are recurring schedules (PAP-765) when business-core is enabled, else plain tables.
* Every pack passes the wave-1 lint minimums and `extends: base`; sensitive fields (students, health notes in gym) marked `sensitive: true`.

**Interface contract**

Provides: five packs with previews, role presets, item counts in `docs/migration/templates.md`. Consumes: pack format (PAP-426), wave-1 conventions (PAP-427), conformance (PAP-122), dimensions, recurring schedules, booking structures (growth round-4 issue, soft), calendar view (PAP-168).

**Definition of done**

* All five pass lint and the apply script (conformance, views render, trial balance zero); composing gym plus salon works; Justin reviews content lists in one NJ item; screenshots at 1280 both themes per pack plus 375 for two; CHANGELOG.

**Test plan**

* Unit: lint; relation integrity; sensitive annotations present where required; fund dimension references resolve or degrade.
* E2E: apply the gym pack with sample data, open the class calendar with capacities, enrol a fictional member, remove sample data.

**Demo**

Reviewer applies the nonprofit pack, opens the donors grid and the fund-filtered P&L on sample data, then removes the sample data. Under two minutes.

**Edge cases**

* Booking issue absent: salon appointments stay a calendar view without public booking; pack notes it.
* Fund dimension missing: giving still posts; report line suggests enabling dimensions.

**Dependencies**

Hard: PAP-426, PAP-427. Soft: PAP-122, PAP-168, PAP-769, PAP-765, PAP-798.

**Agent**

Builder: Scout (Template Packager) with Quill and Beacon (sequences). Reviewer: Sentinel (Visual Inspector; Justin for realism).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/business-core/ledger-dimensions-registry` = PAP-769, `r4/business-core/recurring-invoices-dunning` = PAP-765, `r4/growth/booking-pages-and-availability` = PAP-798.
