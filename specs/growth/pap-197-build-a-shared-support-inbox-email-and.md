---
identifier: "PAP-197"
title: "Build a shared support inbox (email and in-app chat) linked to CRM contacts"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: ["PAP-410", "PAP-411", "PAP-412"]
blockedBy: ["PAP-37", "PAP-131", "PAP-187", "PAP-319"]
blocks: []
key: "growth/support-inbox"
url: "https://linear.app/paperos/issue/PAP-197/build-a-shared-support-inbox-email-and-in-app-chat-linked-to-crm"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:10.373Z"
---

# PAP-197: Build a shared support inbox (email and in-app chat) linked to CRM contacts

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Put every support conversation next to the customer record: a shared inbox receiving email (Resend inbound) and in-app chat from the portal, threaded into conversations linked to contacts and companies, with assignment, tags, replies, internal notes through the comments system, and history on contact and company pages. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-410 Schema, inbound parsing with `mailparser`, quoted-history stripping, threading heuristics, HTML sanitising, contact matching, outbound replies with `Message-ID` threading.
* PAP-411 Portal `<SupportChat/>` widget with live sync and presence, unauthenticated email capture, internal notes on PAP-131 threads, status rules.
* PAP-412 Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts, metrics rollup.

Out: phone, WhatsApp, public knowledge base, AI auto-replies, SLA escalation policies beyond a timer.

**Spec**

Decisions binding all children:

* `support_mailbox (address, display_name, signature, auto_reply)`, `support_conversation (mailbox_id, contact_id, company_id, channel: email|chat, subject, status: open|pending|snoozed|resolved, assignee_user_id, priority, tags, snoozed_until, first_response_at, resolved_at, sla jsonb)`, `support_message (conversation_id, direction: inbound|outbound|note, author_id, author_kind, body_json, body_text, body_html_sanitised, attachments, provider_message_id unique, headers jsonb, delivered_at, read_at)`, `support_canned_reply`.
* Contact matching: exact email, then plus-address stripped, then domain to company only.
* Sanitiser allowlist: basic formatting, links with `rel="noopener"`, inline images rewritten to stored files; scripts and styles removed.
* Status rules: inbound reopens `resolved` within seven days else new conversation; outbound sets `pending`; inbound unsnoozes.
* Permissions `support.read|reply|assign|manage`; customers see only their conversations; agents may note, not reply.
* Every reply is a `crm_activity kind email`; every inbound event audited.

**Interface contract**

Provides: `support.conversations|messages|mailboxes|cannedReplies.*`, inbound route `support.inbound`, `<SupportChat/>`, `<ConversationList contactId? companyId? />` embedded on PAP-189 detail pages, events `support.conversation.opened|resolved`, metrics rollup for a dashboard block. Consumes: contacts and activities (PAP-187), comments threads (PAP-131), record sync and presence (PAP-143, PAP-141, polling fallback), files (PAP-37), portal shell (PAP-64), outreach replies (PAP-191), commands (PAP-151), Resend inbound (provider per PAP-188), notifications (PAP-136 core).

**Definition of done**

* All three children Done.
* Integration: a real email to the staging mailbox appears in the inbox, the reply arrives threaded in the sender's client (recording).
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for inbox, conversation and portal widget; axe clean; inbox keyboard-operable.
* `docs/growth/support.md` (mailbox setup, DNS, macros); CHANGELOG; Linear comment with recording.

**Test plan**

Umbrella `support.e2e.spec.ts`: post 30 fixture inbound emails (Gmail, Outlook, Apple Mail quoting, one auto-reply, one duplicate webhook) and assert threading, stripped quotes, sanitised HTML, contact matching precedence and exactly one message per `provider_message_id`; reply from the console and assert the outbound `In-Reply-To`; send a portal chat message and assert it appears in the console within one second and the reply returns; add an internal note with a mention; snooze and reopen by an inbound message; assert first-response metrics in the rollup.

**Demo**

Reviewer sends an email to the staging mailbox, watches it appear in the inbox linked to the seeded contact, replies with a macro using `r`, opens the portal as that customer to send a chat message and sees it land in the console live. Under two minutes.

**Edge cases**

* Auto-reply loops: `Auto-Submitted` and `Precedence: bulk` honoured; never auto-reply to auto-replies.
* Attachment over 25 MB or blocked type: reference kept with a warning.
* Same email CC'd to two mailboxes: one conversation each, cross-linked.
* New address from a known customer: merge suggested manually.
* Chat from a company with three contacts links the individual.

**Dependencies**

PAP-187 (hard), PAP-131 (hard), PAP-37 (hard), PAP-143 and PAP-141 (soft, polling fallback), PAP-64, PAP-191 (soft), PAP-151, PAP-136 core, mailbox DNS (Needs Justin).

**Agent**

Builder: Beacon (CRM Builder) with Nova on live chat. Reviewer: Sentinel (Security Auditor for sanitisation and permissions, Visual Inspector, Edge Case Hunter for threading), Quill.

**Size**

L, split into three M children.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [growth](<https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
