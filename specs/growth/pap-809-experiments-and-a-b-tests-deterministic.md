---
identifier: "PAP-809"
title: "Experiments and A/B tests: deterministic assignment by anonymous or contact id, variants for landing blocks, email subjects and in-app messages, conversion goals from attribution and significance readout"
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
blockedBy: ["PAP-194", "PAP-794"]
blocks: []
key: "r4/growth/experiments-and-ab-tests"
url: "https://linear.app/paperos/issue/PAP-809/experiments-and-ab-tests-deterministic-assignment-by-anonymous-or"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:47.376Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-809: Experiments and A/B tests: deterministic assignment by anonymous or contact id, variants for landing blocks, email subjects and in-app messages, conversion goals from attribution and significance readout

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-193 and PAP-192 both exclude A/B tests and PAP-194 stops at reporting. One experiment primitive (assignment, exposure, goal) that landing pages, campaigns and in-app messages share turns the attribution pipeline into a decision tool instead of a dashboard.

**Scope**

In: `experiment (key, hypothesis, variants jsonb [{ key, weight }], surface: landing|email_subject|inapp|custom, goal_event, status: draft|running|stopped|concluded, started_at, winner?)`; assignment `assign(experimentKey, unitId)` by hashing `(experiment, unit)` so it is deterministic and stateless with a stored `attr_event` `experiment_exposed`; SDK method in `@paperos/attribution` and server helper; hooks in the landing publisher (block variants), campaigns (subject test reuses this) and in-app messages; results dataset joining exposures to goal events with per-variant conversion, lift and a two-proportion z-test readout with a 'not yet significant' guard; concluding an experiment pins the winner.

Out: multi-armed bandits, feature flags for engineering (PAP-366 owns flags), server-side experiments on pricing (business-core).

**Spec**

* Assignment unit is `anonymous_id` before identify and `contact_id` after, stitched by PAP-194 so a visitor keeps their variant.
* Exposure is recorded once per unit per experiment; goals count once per unit; results exclude bot-flagged events.
* Minimum sample and runtime guards are shown before any winner is suggested; the readout states the test used.

**Interface contract**

Provides: `experiments.*`, `assign`, SDK `experiment(key)`, results dataset `attr.experiments`, hooks for landing, campaigns and in-app. Consumes: attribution SDK, stitching and rollups (PAP-194), landing blocks (sibling), campaigns (PAP-799, soft), in-app messages (soft), flags (PAP-366, for the readout kill switch).

**Definition of done**

* Assignment distribution test within 1 percent of weights over 100k units; stitching keeps variants in a fixture; z-test verified against known values; screenshots at 375, 1024, 1920 light and dark of the results page.
* `docs/growth/experiments.md`; CHANGELOG.

**Test plan**

* Unit: hash assignment, weight distribution, once-only exposure and goal, z-test, guards.
* E2E: run a two-variant landing experiment with fixture traffic through the collector, submit goals for one variant more often, see lift and significance appear after the guard threshold.

**Demo**

Reviewer starts a hero-copy experiment, replays a fixture traffic script and reads the results table with a significant winner. Under two minutes.

**Edge cases**

* Variant removed mid-run: existing units keep it; results mark it 'retired'.
* Goal event also fired by non-exposed users: excluded.
* Experiment key reused: refused; keys are unique per tenant forever.

**Dependencies**

Hard: PAP-194, PAP-794. Soft: PAP-799, PAP-808, PAP-366.

**Agent**

Builder: Beacon (CRM Builder) with Nova on the SDK. Reviewer: Sentinel (Edge Case Hunter, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/growth/email-broadcast-campaigns` = PAP-799, `r4/growth/in-app-messages-and-announcements` = PAP-808, `r4/growth/webflow-landing-publisher-and-editor` = PAP-794.
