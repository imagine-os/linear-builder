---
key: "growth/support/email-threading"
title: "Support schema, inbound email parsing, threading heuristics, HTML sanitising, contact matching and outbound replies"
project: "growth"
parent: "PAP-197"
phase: "P2"
type: "Build"
priority: 3
size: "M"
surfaces: []
milestone: "Acquisition analytics"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012"
status: "pending"
---

# Support schema, inbound email parsing, threading heuristics, HTML sanitising, contact matching and outbound replies

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
