---
identifier: "PAP-806"
title: "Support AI reply drafts and FAQ bot: grounded suggested replies for staff, a help-center-grounded first response in the widget with human handoff, never auto-sent"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-111", "PAP-412", "PAP-805"]
blocks: []
key: "r4/growth/support-ai-reply-drafts"
url: "https://linear.app/paperos/issue/PAP-806/support-ai-reply-drafts-and-faq-bot-grounded-suggested-replies-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:47.203Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-806: Support AI reply drafts and FAQ bot: grounded suggested replies for staff, a help-center-grounded first response in the widget with human handoff, never auto-sent

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-197 excludes AI auto-replies, rightly. Drafts are different: a grounded suggestion the agent edits and sends cuts handling time, and a widget bot that answers from the help center and hands off to a human when unsure deflects without pretending to be a person. Everything stays inside the approval rule that governs every growth agent.

**Scope**

In: Beacon sub-character `support-drafter` (`claude-sonnet-5`, tools: read conversation, search help articles, read CRM summary fields; no send tools) with prompt and skill; `support.drafts.suggest(conversationId)` returning `{ body, sources[], confidence }` validated by Zod, shown in the PAP-412 reply box as an editable draft with a 'Drafted by' badge; widget bot mode (per-tenant toggle) answering with citations when confidence is above a threshold and otherwise creating the conversation with the transcript; per-tenant budget via PAP-111; eval set of 30 conversations with golden drafts for PAP-110; feedback (accepted, edited, rejected) recorded for the eval loop.

Out: autonomous sending, voice, translation (PAP-27 handles locale of the UI), training on tenant data.

**Spec**

* Grounding: every claim cites an article or a prior message; drafts with unsupported claims fail self-check and are dropped.
* The bot discloses it is automated in the first message; any 'human' keyword or two low-confidence turns hand off immediately.
* No contact PII beyond first name is placed in the prompt; conversation bodies are passed through the PAP-410 sanitiser first; prompt and completion logged to PAP-129 with redaction.

**Interface contract**

Provides: character and skill, `support.drafts.*`, widget bot mode, eval task `support-drafter`, feedback dataset `growth.supportDraftFeedback`. Consumes: help center articles and suggestions, console reply box (PAP-412), widget (PAP-411), cost controls (PAP-111), evals (PAP-110), prompt log (PAP-129), roster (PAP-104), agent principals (PAP-60).

**Definition of done**

* Eval at or above 0.8 on the 30 fixtures with zero unsupported claims; tool scope test proves no send capability; budget cap trips in a test.
* Playwright: draft appears, agent edits and sends; bot answers a fixture question with a citation and hands off on 'human'; screenshots at 375, 1024, 1920 light and dark.
* `docs/agents/support-drafter.md`; CHANGELOG; Justin approves the character (NJ item).

**Test plan**

* Unit: output schema validation, citation check, confidence threshold, handoff triggers, PII scrubbing.
* E2E: the Playwright flows above using the PAP-110 runner with recorded model responses.

**Demo**

Reviewer opens a fixture conversation, reads the suggested reply with two citations, edits one sentence and sends; then asks the widget bot a question and types 'human' to see the handoff. Under two minutes.

**Edge cases**

* Help center empty: bot mode disabled with an explanation; drafts fall back to conversation context only.
* Model refusal or timeout: no draft, agent sees nothing but a retry link.
* Customer writes in another language: draft in that language when the article set supports it, else handoff.

**Dependencies**

Hard: PAP-805, PAP-412, PAP-111. Soft: PAP-411, PAP-110, PAP-129, PAP-104, PAP-60.

**Agent**

Builder: Beacon (lead) with Quill on the prompt. Reviewer: Sentinel (Security Auditor for tool scope and PII, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/help-center-knowledge-base` = PAP-805.
