---
identifier: "PAP-889"
title: "Author vertical packs wave 3: ecommerce, nonprofit, school, church, construction, property management, trades and field service"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Operations packs, marketplace and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-426", "PAP-880", "PAP-885", "PAP-888"]
blocks: ["PAP-890"]
key: "r4/commerce/vertical-packs-wave3"
url: "https://linear.app/paperos/issue/PAP-889/author-vertical-packs-wave-3-ecommerce-nonprofit-school-church"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:03.855Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 5
dueDate: null
cycle: null
---

# PAP-889: Author vertical packs wave 3: ecommerce, nonprofit, school, church, construction, property management, trades and field service

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build L

**Goal**

Finish the list in the brief with seven packs on the same format: ecommerce (catalog, orders, fulfilment, returns, subscriptions, reviews), nonprofit (donors as contacts, donations as documents with fund accounting in the chart of accounts, pledges, volunteers as shifts, grant projects), school (students and guardians as audiences, classes as group services, enrolment forms, tuition invoicing, attendance), church (members, giving, groups, events with bookings, volunteer scheduling), construction (jobs as projects, estimates via documents and e-sign, subcontractor bills, change orders, daily logs as forms, progress billing), property management (properties and units as assets, leases as customer subscriptions, maintenance work orders, tenant portal, owner statements), trades and field service (work orders, estimates, parts, technician mobile flow, service agreements).

**Scope**

In: Seven pack directories with the full `pack.yaml` content set as in wave 2; terminology and compliance hints (school: student privacy profile; nonprofit: fund and restricted gift accounts; property: security deposit liability accounts). Audience definitions per pack (`student`, `guardian`, `donor`, `member`, `tenant-resident`, `owner`, `subcontractor`) composed from PAP-55 segments with portal navigation per audience. Gallery cards, starter workflows (enrolment, donation acknowledgement, lease renewal, change order approval), starter documents (receipt letters, lease, estimate), starter assistant characters.

Out: Regulatory filings (990s, 1099s, tax receipts formats beyond a template marked review required). Payment rails beyond Stripe (ACH is Stripe ACH).

**Spec**

* Same idempotency, lint and coverage rules as wave 2; property management leases must produce correct deposit liability postings in the conformance run
* Fund accounting for nonprofits and churches uses account dimensions on `fin_account` (PAP-392) rather than parallel charts; the pack documents the convention
* School packs default to the strictest privacy profile for the `student` audience and never expose guardian contact data to other guardians (attribute policy in the pack roles)

**Interface contract**

Provides: seven pack directories, audiences and terminology entries, gallery cards, starter content. Consumes: wave 2 conventions, pack format (PAP-426), orders and assets (commerce), subscriptions (leases), engagement bookings and memberships, workflows and documents, audiences (PAP-55). Consumed by: PAP-890, PAP-428, PAP-208, PAP-429.

**Definition of done**

* Seven packs apply, lint and re-apply idempotently; gallery shows eleven new packs in total; a property management demo runs lease → rent invoice → maintenance work order → owner statement from pack content
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: pack lint and coverage; audience policy tests generated from pack roles (PAP-64 pattern).
* Integration: apply each pack to a blank tenant in CI shards; posting traces for donation, tuition, rent and progress billing fixtures.

**Demo**

Apply the property management pack, add a unit and a resident, start the lease subscription in test mode, log a maintenance request from the resident portal, complete it as a technician, and generate the owner statement.

**Edge cases**

* Tenant applies two packs (church plus school): shared objects merge by name; navigation shows both audiences; the report lists overlaps

**Dependencies**

PAP-888 (hard: conventions), PAP-880, PAP-885, PAP-886 (soft: content skipped when absent), PAP-426 (hard).

**Agent**

Builder: Scout. Reviewer: Ledger (Bookkeeper).

**Size**

L: two sessions; split at the first natural seam if the first session does not reach the integration test.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/commerce/assets-work-orders` = PAP-885, `r4/commerce/customer-subscriptions` = PAP-886, `r4/commerce/orders-fulfilment` = PAP-880, `r4/commerce/pack-conformance-tests` = PAP-890, `r4/commerce/vertical-packs-wave2` = PAP-888.
