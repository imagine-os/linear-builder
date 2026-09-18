---
identifier: "PAP-899"
title: "Build experiments on feature flags: experiment definitions over PAP-366 variants, deterministic assignment, exposure events, metrics from product analytics, sequential readouts with guardrails and a results page"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Product analytics, experiments and abuse controls"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-173", "PAP-366", "PAP-387", "PAP-435", "PAP-897"]
blocks: []
key: "r4/platform-ops/experiments"
url: "https://linear.app/paperos/issue/PAP-899/build-experiments-on-feature-flags-experiment-definitions-over-pap-366"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:26.667Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-899: Build experiments on feature flags: experiment definitions over PAP-366 variants, deterministic assignment, exposure events, metrics from product analytics, sequential readouts with guardrails and a results page

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Turn flag variants into learning: an `experiment` wraps a PAP-366 variant flag with a hypothesis, audience, allocation, primary and guardrail metrics from product analytics, deterministic assignment by actor hash, `experiment.exposed` events, a sequential-test readout (always-valid inference so peeking is safe) and a results page, for PaperOS about its tenants and for tenants about their portal customers.

**Scope**

In: `experiment` (flag key, hypothesis, variants with weights, audience `FilterTree` over segments, start, end, primary metric, guardrails, minimum sample), `experiment_assignment` (actor hash, variant, first exposure); `ExperimentPort.assign` integrates with the PAP-366 evaluator as a rule source so `useVariant` returns the assigned variant and logs exposure once per actor per experiment. Readout job: metrics computed from `product_events` (conversion, count, sum) per variant; mSPRT sequential test with a configurable alpha; guardrail metrics with stop rules; results page `/admin/experiments/:id` and tenant `/console/experiments` with charts (PAP-173 blocks), decision log (ship, stop, extend) written as an ADR-lite record. Module swap integration: `module.<id>.impl` shadow and canary runs (PAP-435) can be declared as experiments so a swap gets a statistical readout of error rate and latency.

Out: Bayesian or CUPED variance reduction (v0.3). Multi-armed bandits.

**Spec**

* Assignment is a pure function of `(experimentId, actorHash, salt)`; changing weights mid-experiment creates a new experiment version and is discouraged by the UI
* Exposure is logged only when the variant actually affects rendering (`useVariant` call site), not at assignment, so dilution is measured correctly
* Guardrail breach (error rate, latency from PAP-40, refund rate) auto-stops and reverts to control through the flag kill switch with a notification
* Sample ratio mismatch check runs daily and flags broken assignment

**Interface contract**

Provides: `ExperimentPort` default adapter, tables, assignment rule source for flags, readout job, results pages, `experiment.exposed` event, decision records. Consumes: product analytics events and datasets, flags and evaluator (PAP-366), swap mechanism (PAP-435), dashboards (PAP-173), latency metrics (PAP-40), notifications (PAP-136). Consumed by: module-system swap playbook (PAP-442 canary readouts), growth (landing page and pricing tests for tenants), engagement (announcement copy tests in v0.3).

**Definition of done**

* A demo experiment on the onboarding template step runs on staging with synthetic traffic, reaches a readout, and a guardrail breach fixture auto-stops it; a module swap declared as an experiment produces an error-rate readout
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: assignment determinism and weights; mSPRT math against reference values; SRM check.
* Integration: exposure once per actor; guardrail stop flips the kill switch; results page numbers equal SQL over fixtures.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Create an experiment on the portal booking button copy for the demo tenant, generate synthetic exposures and conversions, open the readout and show the sequential confidence band, then trigger a guardrail and watch it stop.

**Edge cases**

* Actor consents to analytics after being assigned: assignment stands (flag consistency) but exposure and metrics start from consent time; the readout notes the censoring
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-897 (hard), PAP-366 (hard), PAP-435, PAP-173, PAP-40 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/platform-ops/product-analytics` = PAP-897.
