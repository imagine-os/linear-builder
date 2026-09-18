---
identifier: "PAP-840"
title: "Build summaries and drafting copilots: record and thread summaries, reply drafts for support and outreach into pending approval, notes to tasks"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Actions, copilots and portal assistant"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-131", "PAP-192", "PAP-319", "PAP-333", "PAP-370", "PAP-412", "PAP-836"]
blocks: []
key: "r4/assistant/summaries-and-drafting"
url: "https://linear.app/paperos/issue/PAP-840/build-summaries-and-drafting-copilots-record-and-thread-summaries"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-840: Build summaries and drafting copilots: record and thread summaries, reply drafts for support and outreach into pending approval, notes to tasks

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Save staff the reading and the first draft: one-click summaries of a record's activity timeline or a comment thread, reply drafts in the support inbox and outreach sequences that land as `pending_approval` items in the tenant voice (PAP-192 pattern, never sent by the model), and "turn these notes into tasks" that proposes PM issues for confirmation.

**Scope**

In: `CopilotPort.summarise(entityRef | threadRef, { length, audience })` grounded on PAP-333 activity, PAP-131 comments and linked documents; cached per entity version with a `stale` marker; rendered as a `Summary` card at the top of the record panel (slot `record.panel.summary`) with citations. `CopilotPort.draft({ kind: 'support-reply'|'outreach-email'|'outreach-sms'|'comment', context, tone })` using the tenant voice profile (from PAP-192 `CampaignDraft` voice fields) and the conversation history; output is a `pending_approval` draft on the support conversation (PAP-412 reply box prefill) or an outreach template suggestion (PAP-406), always human-edited before send. Notes to tasks: paste or select text → proposed PM issues (PAP-100 entities) with assignee suggestions from mentions; confirmation card per task via the action catalogue. Voice profile settings on `tenant_ai_settings` (tone, banned phrases, sign-off, languages via PAP-27) with a preview.

Out: Sending anything. Meeting transcription (out; v0.3 with PAP-159). Marketing campaign drafting (PAP-192 owns; this issue reuses its schema).

**Spec**

* Summaries cite at least one source per claim; a claim without a citation is dropped by a post-processing check (the model is asked to tag each sentence with chunk ids)
* Drafts respect consent and suppression (`canContact` from PAP-187 WP0) by refusing to draft to a suppressed contact with an explanation
* Language: drafts are produced in the contact's preferred language when known, else tenant default; the voice profile applies per language
* Every draft records `assistant.draft.created` with the conversation id so approval queues can show provenance ("drafted by assistant, edited by Sam")
* Summary length presets: one line (for grids, via a computed field type `aiSummary` registered with PAP-338 as read-only), paragraph, bullet list

**Interface contract**

Provides: `CopilotPort.summarise|draft`, `record.panel.summary` fill, `aiSummary` computed field type, voice profile settings, events `assistant.draft.created`. Consumes: record activity (PAP-333), comments (PAP-131), support inbox reply box (PAP-412), voice schema (PAP-192), outreach templates (PAP-406), consent (PAP-187), email package (PAP-370) for preview rendering, PM entities (PAP-100). Consumed by: growth (inbox and sequences), engagement (review responses, booking confirmations), pm-linear (notes to issues), commerce (order notes).

**Definition of done**

* Summary card on contact, deal, invoice and PM issue records in the demo tenant with citations; support reply draft appears in the reply box as editable text with provenance
* Eval: 30 summary fixtures graded by the LLM judge (PAP-310) for faithfulness ≥ 4/5 and zero uncited claims
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: citation post-check drops uncited sentences; suppression refusal; language selection; cache invalidation on new activity.
* E2E: draft a support reply, edit, send through the normal inbox path; the sent message carries the human as sender and the draft provenance in the activity timeline.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Open a long support conversation, click Summarise, then Draft reply; edit one sentence and send; the timeline shows the assistant drafted and Sam sent.

**Edge cases**

* Record with no activity: summary card shows the empty state with a suggestion to add a note, no model call made
* Contact who unsubscribed after the draft was created: the send path (PAP-405) still blocks; the draft card shows the block reason
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-836 (hard), PAP-333, PAP-131 (hard), PAP-412, PAP-192, PAP-406 (soft: features degrade to a copyable draft), PAP-370 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/assistant/conversation-runtime` = PAP-836.
