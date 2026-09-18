---
identifier: "PAP-410"
title: "Support schema, inbound email parsing, threading heuristics, HTML sanitising, contact matching and outbound replies"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: "PAP-197"
children: []
blockedBy: ["PAP-37", "PAP-187", "PAP-474", "PAP-790", "PAP-791"]
blocks: ["PAP-411", "PAP-867"]
key: "growth/support/email-threading"
url: "https://linear.app/paperos/issue/PAP-410/support-schema-inbound-email-parsing-threading-heuristics-html"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:54.990Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-410: Support schema, inbound email parsing, threading heuristics, HTML sanitising, contact matching and outbound replies

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Turn raw inbound email into clean, correctly threaded conversations linked to the right contact, and send replies that thread in the customer's client.

**Scope**

In: `support/schema.ts`, `support.inbound` route (Resend inbound), `mailparser` 3.x, quoted-history stripping, `sanitize-html` 2.x allowlist, threading by `In-Reply-To`, `References`, subject plus sender, contact matching precedence, outbound via Resend with `Message-ID`, attachments via PAP-37. Out: chat, notes, console UI (siblings).

**Spec**

* Tables per the parent; `provider_message_id` unique for dedupe.
* Status rules: inbound reopens `resolved` within seven days else new; outbound sets `pending`.
* Auto-reply detection via `Auto-Submitted` and `Precedence: bulk`; never auto-reply to auto-replies.

**Interface contract**

Provides: schema, `support.conversations|messages|mailboxes.*`, inbound route, `threadInbound(email)`, `sanitiseHtml`. Consumes: PAP-187, PAP-37, PAP-38, provider per PAP-188, mailbox DNS (Needs Justin).

**Definition of done**

* 30 fixture emails threaded and sanitised correctly; real email round trip on staging recorded.

*Round 4 amendment (2026-09-18):*
Round 4: the 30 fixture emails are the gate; the real staging round trip is attached when the mailbox DNS (NJ) exists and is otherwise `skipped: no-credentials`. Inbound fixtures must include one message with a prompt-injection payload in the body and assert it is wrapped as T3 untrusted content before any agent (PAP-192, PAP-806) reads it.

**Test plan**

* Unit: threading, stripping, sanitiser, matching precedence, status rules.
* Integration: real inbound and threaded reply.

**Demo**

Send an email to the staging mailbox and read it in a raw conversation view; reply and show it threaded in the client.

**Edge cases**

* Same email CC'd to two mailboxes yields cross-linked conversations; 25 MB attachment kept as reference with warning.

**Dependencies**

PAP-187, PAP-37 (hard), PAP-38, mailbox DNS. Blocks siblings.

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel (Security Auditor for sanitisation, Edge Case Hunter).

**Size**

M: threading heuristics.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/support-ai-reply-drafts` = PAP-806.
