---
identifier: "PAP-822"
title: "AI mapping assistant: Claude-suggested field mappings, types and transforms in the wizard from sampled values and target schema, with confidence, explanations and a spend cap"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-110", "PAP-111", "PAP-310", "PAP-349"]
blocks: []
key: "r4/migration/ai-mapping-assistant"
url: "https://linear.app/paperos/issue/PAP-822/ai-mapping-assistant-claude-suggested-field-mappings-types-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:39.238Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-822: AI mapping assistant: Claude-suggested field mappings, types and transforms in the wizard from sampled values and target schema, with confidence, explanations and a spend cap

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-349 infers types from values; it cannot know that `Cust Ref` is the customer relation or that `1,5` needs a locale transform. PAP-208 is a whole conversational agent; this is the inline, cheap version: a single tool call per collection that proposes the mapping, explains it and lets the user accept row by row, with a hard cap on cost.

**Scope**

In: `suggestMapping({ sourceSchema, samples, targetSchema })` calling the Claude API (per the `claude-api` skill) with a `propose_mapping` tool whose output is Zod-validated `{ fields: [{ source, target, type, transform?, confidence, reason }], newFields[], relations[] }`; wizard 'Suggest' button on the mapping step (PAP-349) applying suggestions as editable rows with a confidence badge and reason tooltip; feedback (accepted, changed, rejected) stored for the PAP-110 eval set; spend cap per tenant per day via PAP-111 counters; samples limited to 20 values per field with PII-classified fields masked before sending (PAP-355 `pii()`); `dryRun` mode returning a deterministic fixture in CI.

Out: autonomous commits (PAP-208 owns approval tokens), training, prompt customisation per tenant.

**Spec**

* Prompt includes the PAP-198 field-type matrix and the target dataset's `FieldDef`s; the model may only choose from existing targets, propose new fields or mark `skip`.
* Suggestions never write; the user's accepted mapping is what PAP-347 runs; a suggestion for a `relation` requires a resolvable key match in samples.
* Model responses are T3 content: validated by schema, never executed, and logged to PAP-129 with redaction.

**Interface contract**

Provides: `suggestMapping`, wizard integration, feedback dataset `import.mappingFeedback`, eval task `mapping-assistant` with 20 fixtures. Consumes: wizard and inference (PAP-349), cost controls (PAP-111), evals (PAP-110), PII classification (PAP-355), prompt log (PAP-129), field-type matrix (PAP-198).

**Definition of done**

* Eval at or above 0.85 exact-target accuracy on 20 fixture collections with recorded model responses; cap trips in a test; PII masking test; Playwright suggest flow; screenshots at 375, 1024, 1920 light and dark.
* `docs/migration/mapping-assistant.md`; CHANGELOG.

**Test plan**

* Unit: output validation, masking, cap counters, confidence badge thresholds, feedback recording.
* E2E: upload the HubSpot fixture without a preset, click Suggest, accept all but one, commit and verify the pipeline stages resolved.

**Demo**

Reviewer uploads an unfamiliar CSV, clicks Suggest and watches the mapping table fill with reasons, changes one and commits. Under one minute.

**Edge cases**

* Model unavailable: button disabled with the reason; inference-only mapping remains.
* Suggestion targets a field the actor cannot write: dropped with a note.
* Same file re-uploaded: cached suggestion by schema hash, no new spend.

**Dependencies**

Hard: PAP-349, PAP-111, PAP-110. Soft: PAP-355, PAP-129, PAP-198.

**Agent**

Builder: Scout (Import Mapper) with Quill on the prompt. Reviewer: Sentinel (Security Auditor for PII, Code Reviewer).

**Size**

M: one session.
