---
key: "growth/outreach/model-worker"
title: "Outreach schema, provider interface with Resend and Twilio adapters, scheduler worker, template rendering and idempotency"
project: "growth"
parent: "PAP-191"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "Campaigns and social"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012"
identifier: "PAP-404"
status: "created"
createdAt: "2026-09-17"
---

# Outreach schema, provider interface with Resend and Twilio adapters, scheduler worker, template rendering and idempotency

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
