---
identifier: "PAP-752"
title: "Spec `analytics` section: product events per action and view compiled into the privacy-first event pipeline with a generated event catalogue"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-740"]
blocks: []
key: "r4/spec-builder/analytics-events-section"
url: "https://linear.app/paperos/issue/PAP-752/spec-analytics-section-product-events-per-action-and-view-compiled"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:37.459Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-752: Spec `analytics` section: product events per action and view compiled into the privacy-first event pipeline with a generated event catalogue

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (stretch pool; NJ-14 can reinstate). Not claimable before 10-01.

PAP-194 builds an acquisition analytics pipeline and PAP-195 segments on product usage, but which product events exist is decided ad hoc in code. Let the spec declare them: a page names the events its views and actions emit, codegen wires the calls, and a catalogue page lists every event with its owner and properties.

**Scope**

In: `analytics: { view?: EventName | false, actions?: Record<actionName, { event: EventName, props?: string[] }>, pii?: 'none' }` in the schema (v1.2 additive), codegen emitting `track()` calls in PAP-315's action binding and route load, generator `analytics-catalogue` writing `docs/.generated/analytics-events.json` and a docs page, rule `ANALYTICS_PROP_PII` (a listed prop flagged `pii: high` in the entity grammar is an error). Out: the pipeline (PAP-194), dashboards (PAP-173), consent (PAP-221).

**Spec**

* Event naming `<page>.<action|viewed>`, overridable; props limited to spec-known fields; `tenant_id` and `actor.type` added automatically, never `actor.id` for customers (PAP-194 privacy rule).
* Default: every public and customer page emits `viewed`; staff and agent pages emit nothing unless declared.
* Catalogue page groups by surface and links to the spec; PAP-195 segment builder reads the catalogue for its event picker.
* Consent: `track()` no-ops when PAP-221 consent is absent for the audience.
* Determinism and `--check` as for every generator.

**Interface contract**

Provides: `analytics` section schema, `track` emission, catalogue generator and page, rule id. Consumes: v1.1 schema mechanics, PAP-315 action binding, PAP-194 `track()` client, PAP-221 consent (soft), entity `pii` flags. Consumed by: PAP-194, PAP-195, PAP-173 dashboards.

**Definition of done**

* Landing and invoices pages emit declared events into PAP-194's dev sink; a PII prop fails validation; catalogue lists both pages.
* `docs/spec/analytics.md`; CHANGELOG entry.

**Test plan**

* Unit: schema, naming, PII rule, emission snapshot.
* Integration: events arrive in the PAP-194 sink in the compose stack.
* E2E: none.

**Demo**

Add `analytics: { actions: { payInvoice: { event: 'invoice.pay_clicked', props: ['amount'] } } }`, regenerate, click Pay in mock mode and see the event in the dev sink. Under one minute.

**Edge cases**

* Action without analytics: no call emitted.
* Event renamed: catalogue marks the old name `retired` for 30 days.
* Consent revoked mid-session: subsequent calls drop.

**Dependencies**

Hard: PAP-740. Soft: PAP-194 (its milestone is 10-01; the section ships against a dev sink until then), PAP-315, PAP-221, PAP-195. Deferred: v0.2.

**Agent**

Builder: Nova with Beacon. Reviewer: Sentinel (Security Auditor for PII).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/spec-builder/schema-v1-1-extensions` = PAP-740.
