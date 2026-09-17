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
blockedBy: ["PAP-43", "PAP-187"]
blocks: ["PAP-405", "PAP-491"]
key: "growth/outreach/model-worker"
url: "https://linear.app/paperos/issue/PAP-404/outreach-schema-provider-interface-with-resend-and-twilio-adapters"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:51.520Z"
model: "claude-sonnet-5"
effort: "low"
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

**Test plan**

* Unit: selection, conditions, rendering with missing variables, idempotency.
* Integration: test-clock run of a two-step sequence.

**Demo**

Enrol an allowlisted contact and advance the test clock to see both messages with provider ids.

**Edge cases**

* Template edited mid-sequence keeps `template_version`; daily cap rolls sends to the next window.

**Dependencies**

PAP-187, PAP-43, PAP-17 (hard). Blocks siblings.

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
