---
identifier: "PAP-404"
title: "Outreach schema, provider interface with Resend and Twilio adapters, scheduler worker, template rendering and idempotency"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: "PAP-191"
children: []
blockedBy: ["PAP-17", "PAP-43", "PAP-187", "PAP-565", "PAP-790", "PAP-791"]
blocks: ["PAP-405", "PAP-799", "PAP-800", "PAP-867", "PAP-910"]
key: "growth/outreach/model-worker"
url: "https://linear.app/paperos/issue/PAP-404/outreach-schema-provider-interface-with-resend-and-twilio-adapters"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:55.136Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-404: Outreach schema, provider interface with Resend and Twilio adapters, scheduler worker, template rendering and idempotency

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Send the right step to the right contact at the right time, exactly once, through pluggable providers.

**Scope**

In: `outreach/schema.ts`, `providers/{types,resend,twilio}.ts`, worker (`SELECT ... FOR UPDATE SKIP LOCKED`), Handlebars-style rendering with an allowlist, sandbox recipient rewrite. Out: compliance, warmup, replies, UI (siblings).

**Spec**

* Tables per the parent; `outreach_message` unique `(enrolment_id, step_id)`.
* Worker every minute: due enrolments, step conditions, render, send, record message and `crm_activity`; provider errors retried with backoff up to six hours then `failed`.
* Sandbox default rewrites non-allowlisted recipients to `sandbox+<hash>@paperos.test`.

**Interface contract**

Provides: schema, `OutreachProvider`, `outreach.sequences|steps|templates|enrolments.*`, `outreach.enrol`, worker job `outreach.tick`. Consumes: PAP-187, PAP-43, PAP-17, PAP-188 decision.

**Definition of done**

* Scheduler and rendering tests; one sandbox email and SMS delivered with test credentials, recorded.

*Round 4 amendment (2026-09-18):*
Round 4: CI passes with `noop` providers and recorded Resend and Twilio fixtures; the sandbox delivery to allowlisted addresses is attached when `RESEND_TEST_KEY` and `TWILIO_TEST_SID` exist, otherwise `skipped: no-credentials`. Every attempt is written to PAP-792 so reviewers can prove nothing left the allowlist.

**Test plan**

* Unit: selection, conditions, rendering with missing variables, idempotency.
* Integration: test-clock run of a two-step sequence.

**Demo**

Enrol an allowlisted contact and advance the test clock to see both messages with provider ids.

**Edge cases**

* Template edited mid-sequence keeps `template_version`; daily cap rolls sends to the next window.

**Dependencies**

PAP-187, PAP-43, PAP-17 (hard). Blocks siblings.

*Round 4 (2026-09-18): PAP-491 soft: this issue no longer blocks PAP-491 because PAP-404 is deferred to v0.2 and must not block scheduled work; PAP-491 proceeds (wire growth with the CRM core (PAP-189) and the contract stubs for outreach; the provider adapters and scheduler join when PAP-404 is reinstated) and reconciles when this issue lands.*

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/outbound-sandbox-ledger` = PAP-792.
