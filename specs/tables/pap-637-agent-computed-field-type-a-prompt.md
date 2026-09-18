---
identifier: "PAP-637"
title: "Agent-computed field type: a prompt template over record fields filled by a scoped agent job with cost units, caching and manual override"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-111", "PAP-340", "PAP-389"]
blocks: []
key: "r4/tables/agent-computed-field"
url: "https://linear.app/paperos/issue/PAP-637/agent-computed-field-type-a-prompt-template-over-record-fields-filled"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:37.020Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-637: Agent-computed field type: a prompt template over record fields filled by a scoped agent job with cost units, caching and manual override

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). Airtable AI fields, Notion AI autofill and Baserow's AI field let a table summarise, classify or draft from other columns. PaperOS has agents as principals; give tables an `agent` field type that fills from a prompt template through the existing `agent.run` action with budgets, caching and audit.

**Scope**

In: `fields/agent.ts` with options `{ prompt (template over `{Field}` refs), outputType: 'text'|'select'|'number'|'boolean', model: 'haiku'|'sonnet', trigger: 'onChange'|'manual', dependsOn: fieldId[] }`; job `fields.agent.compute` batching 20 records per call; `record.agent_cache jsonb` with input hash; manual override with a lock icon; cost units to PAP-111 budgets.

Out: agent tools or web access from a field, free-form chat per record, training.

**Spec**

* Compute runs only server-side as the `tables-agent` principal with `agentCallable` restricted to the `agent.run` action (PAP-389) at the tenant's daily field budget; results cached by hash of the dependency values; recompute on dependency change when `trigger: 'onChange'`, else via a "Recompute" button (bulk from the column menu, capped 1,000 per run).
* Output validated against `outputType` (select must match an option name, number parsed); failures render `#AGENT` with the error; every compute writes an audit row with prompt hash, model, tokens and cost.
* Prompt template shares the PAP-171 expression subset for references; PII fields (PAP-355 `pii` annotation) are excluded unless the tenant setting `agentFields.allowPii` is on; injection defences from PAP-299 wrap record content as untrusted.
* Overrides: a user can edit the value, which locks it (`agent_cache.locked`); unlock recomputes.

**Interface contract**

Provides: `agent` FieldType, job `fields.agent.compute`, procedures `fields.agentRecompute`, cost telemetry `field.agent.computed`. Consumes: action runtime and `agent.run` (PAP-389), computed storage and conversions (PAP-340), budgets and kill switch (PAP-111), PII annotations (PAP-355), injection defences (PAP-299), jobs (PAP-43).

**Definition of done**

* Type green in Vitest and integration with a mock model; stories at 375, 1024, 1920; audit and budget tests; `docs/views/agent-fields.md` with the privacy note; CHANGELOG; Security Auditor sign-off.

**Test plan**

* Unit: template rendering; hash and cache; output validation per type; PII exclusion; lock semantics.
* Integration: 100 changed records produce five batched calls; budget exhaustion pauses with a banner; kill switch stops the job.
* E2E: add a "Summary" agent field over Notes, edit a note, watch the summary refresh, override and lock it.

**Demo**

Reviewer adds a sentiment select filled by an agent over the notes column and recomputes ten rows. Under two minutes.

**Edge cases**

* Model unavailable: `#AGENT` with retry schedule, never blocks other writes.
* Dependency field converted: cache invalidated, recompute queued.

**Dependencies**

PAP-389 (hard), PAP-340 (hard), PAP-111 (hard). Soft: PAP-355, PAP-299. Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer) with Atlas on budgets. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
