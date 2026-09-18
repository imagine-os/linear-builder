---
identifier: "PAP-801"
title: "Lead scoring and routing: fit and engagement score rules, lifecycle promotion thresholds, round-robin and territory assignment, SLA timer on new leads"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-194", "PAP-195", "PAP-790"]
blocks: []
key: "r4/growth/lead-scoring-and-routing"
url: "https://linear.app/paperos/issue/PAP-801/lead-scoring-and-routing-fit-and-engagement-score-rules-lifecycle"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:46.413Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-801: Lead scoring and routing: fit and engagement score rules, lifecycle promotion thresholds, round-robin and territory assignment, SLA timer on new leads

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Leads arrive from forms, imports and referrals and sit in `new`. Scoring turns attributes and behaviour into a number, routing hands the lead to a person, and the lifecycle moves from `lead` to `mql` and `sql` on rules instead of by hand.

**Scope**

In: `crm_score_model (name, rules jsonb [{ clause: FilterTree, points, decay_days? }], thresholds { mql, sql })` evaluated incrementally by a PAP-43 job on contact changes and attribution events; `crm_contact.score`, `score_updated_at`, breakdown panel on the contact page; routing rules `crm_routing_rule (clause, strategy: owner|round_robin|territory, pool user_ids[], territory_field)` applied on `lead.created` and score threshold crossing; SLA timer (`first_touch_due_at`) with PAP-136 alert and escalation to manager; lifecycle promotion writes a `system` activity; datasets for reporting.

Out: predictive or ML scoring, external enrichment (PAP-802 feeds attributes), quota management.

**Spec**

* Rules reuse `FilterTree` from PAP-279 with the PAP-195 extensions (`performed X at least N times in window`), so the same builder edits them.
* Scores recompute incrementally (only contacts touched since the watermark) with a nightly full pass; decay reduces engagement points by day.
* Round robin is fair per pool and skips users out of office (PAP-136 status if available); assignment is idempotent per lead.

**Interface contract**

Provides: `crm.scoring.*`, `crm.routing.*`, contact score fields and breakdown component, activity kinds, dataset `crm.scoreDistribution`, event `crm.lead.assigned`. Consumes: CRM schema, segments grammar (PAP-195), attribution events (PAP-194), jobs (PAP-43), notifications (PAP-136), filter builder (PAP-166).

**Definition of done**

* Fixture of 500 contacts scores deterministically and matches a brute-force evaluation; round robin fairness within one; Playwright rule builder; screenshots at 375, 1024, 1920 light and dark.
* `docs/growth/scoring-routing.md`; CHANGELOG.

**Test plan**

* Unit: rule evaluation, decay, threshold crossings in both directions, routing strategies, SLA timers.
* E2E: define a model, submit a fixture form lead with UTM, see the score, the assignment and the SLA badge; let the fixture clock pass the SLA and see the escalation.

**Demo**

Reviewer creates two rules, watches a seeded lead cross the MQL threshold and land on a rep with a 2-hour SLA badge. Under two minutes.

**Edge cases**

* Rule references a deleted custom field: model paused, owner notified (PAP-195 pattern).
* Territory field empty: falls back to round robin with a note.
* Score drop below threshold: lifecycle never demotes automatically; an activity records it.

**Dependencies**

Hard: PAP-790, PAP-195, PAP-194. Soft: PAP-43, PAP-136, PAP-166.

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/contact-enrichment-port` = PAP-802, `r4/growth/crm-schema-routers-page-specs` = PAP-790.
