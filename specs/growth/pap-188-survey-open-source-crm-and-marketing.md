---
identifier: "PAP-188"
title: "Survey open-source CRM and marketing stacks (Twenty, Postiz, Listmonk, Dub) for reuse vs build; write ADR"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P1"
type: "Research"
priority: 2
surfaces: ["Staff"]
milestone: "CRM core"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-190", "PAP-401"]
key: "growth/growth-research"
url: "https://linear.app/paperos/issue/PAP-188/survey-open-source-crm-and-marketing-stacks-twenty-postiz-listmonk-dub"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T05:24:45.959Z"
---

# PAP-188: Survey open-source CRM and marketing stacks (Twenty, Postiz, Listmonk, Dub) for reuse vs build; write ADR

**Goal**

Decide, before growth code is written, which parts of the marketing stack PaperOS borrows and which it builds: evaluate Twenty, Postiz, Listmonk, Dub, Chatwoot and Umami/PostHog against the library rubric and record the outcome as an ADR every growth issue then follows.

**Scope**

In: rubric from PAP-210 extended with multi-tenancy, embeddability, data ownership, deliverability and AGPL review under PAP-211; three integration shapes scored per product (run as a service, fork and embed, reimplement on the tables engine); `spikes/growth-stack/` with Coolify compose files, screenshots and API smoke scripts; data-model mapping to PAP-187 fields for PAP-202 importers; ADR `docs/adr/00xx-growth-stack.md`; registry entries for PAP-215.

Out: production deployment of any candidate, adapters, paid SaaS beyond a note.

**Spec**

* Time-box 1.5 agent-days, maximum 3 hours per product; unknowns become penalties.
* Hypothesis to confirm or reject: build CRM and segments on the tables engine; borrow Postiz adapters as reference or run it behind our approval queue; Listmonk only if Resend broadcasts prove insufficient; Dub via API for short links; reject running Twenty because it duplicates the tables engine.
* Score 1 to 5 on license fit, self-host effort, API completeness, tenant isolation, TypeScript quality, velocity (commits in 90 days), cost of exit; per product "what we take", "what we never take", hours per shape.
* Deliverability section: Resend versus Postmark versus SES for transactional and marketing volume, warmup, inbound parsing (feeds PAP-191 and PAP-197).
* Analytics section: Umami versus PostHog self-hosted versus own event table for PAP-194 under the privacy-first rule.
* Record OAuth app-review lead times per social platform so PAP-190 files applications immediately.

**Interface contract**

Provides: `results.json` (per-product scores and shape estimates), the ADR decisions consumed as constraints by PAP-190, PAP-191, PAP-194, PAP-197, provider recommendation consumed by PAP-191 and PAP-197, compose files reusable for staging spikes, mapping tables consumed by PAP-202 and PAP-206. Consumes: rubric (PAP-210), license policy (PAP-211), staging host (PAP-25). No code exports.

**Definition of done**

* Spikes committed (excluded from `turbo build`), compose files run on staging.
* ADR approved by Atlas and Beacon in PR review; decisions cross-referenced by comment on PAP-190, PAP-191, PAP-194, PAP-197.
* Screenshots of each candidate at 1280 and 1920; comparison table rendered from `results.json`.
* AGPL review for every candidate approved by Sentinel (Security Auditor).
* Registry entries or a Linear comment for Scout; CHANGELOG (docs); Linear comment with the ADR link and table.

**Test plan**

* Unit: `results.json` validated against a Zod schema; rubric totals recomputed by script and compared with the table.
* Integration: each compose file starts on staging and its smoke script (create contact, schedule post, send test email, create short link) exits 0; results recorded in `results.json`.
* Docs: link check on all evidence URLs.
* E2E and visual: none beyond the candidate screenshots.

**Demo**

Reviewer opens the ADR, reads the six one-paragraph decisions, then opens the comparison table and the Postiz screenshot to confirm the "borrow adapters, own the queue" call. Under two minutes.

**Edge cases**

* Product needs its own Postgres or Redis: score operational cost; never share our primary database.
* Platform OAuth review measured in weeks: record lead time and start applications.
* License changed recently (Dub): record the exact version evaluated.
* Incomplete self-host docs: score only what the spike achieved.
* Justin prefers a paid tool: open question in the ADR, not a blocker.

**Dependencies**

None hard; starts now (moved to Ready for Claude per the round-2 audit). Uses PAP-210 and PAP-211 drafts. Blocks PAP-190; informs PAP-191, PAP-194, PAP-197, PAP-202.

**Agent**

Builder: Scout (Library Evaluator) paired with Beacon. Reviewer: Atlas (decision), Sentinel (Security Auditor) for licenses.

**Size**

M: six time-boxed spikes with real installs.
