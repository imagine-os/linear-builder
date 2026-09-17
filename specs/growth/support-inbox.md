---
identifier: "PAP-197"
title: "Build a shared support inbox (email and in-app chat) linked to CRM contacts"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-131", "PAP-187", "PAP-37"]
blocks: []
key: "growth/support-inbox"
url: "https://linear.app/paperos/issue/PAP-197/build-a-shared-support-inbox-email-and-in-app-chat-linked-to-crm"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-197: Build a shared support inbox (email and in-app chat) linked to CRM contacts

**Goal**

Put every support conversation next to the customer record: a shared inbox that receives email (Resend inbound) and in-app chat from the customer portal, threads them into conversations linked to CRM contacts and companies, lets staff assign, tag, reply and add internal notes using the comments system, and shows the conversation history on contact and company pages.

**Scope**

In:
- Schema `packages/growth/src/support/schema.ts`: `support_mailbox` (`address`, `display_name`, `signature`, `auto_reply`), `support_conversation` (`mailbox_id`, `contact_id`, `company_id`, `channel: email|chat`, `subject`, `status: open|pending|snoozed|resolved`, `assignee_user_id`, `priority`, `tags`, `snoozed_until`, `first_response_at`, `resolved_at`, `sla jsonb`), `support_message` (`conversation_id`, `direction: inbound|outbound|note`, `author_id`, `author_kind`, `body_json`, `body_text`, `body_html_sanitised`, `attachments uuid[]`, `provider_message_id`, `headers jsonb`, `delivered_at`, `read_at`), `support_canned_reply`.
- Inbound email: Resend inbound webhook -> `support.inbound`; parse with `mailparser` 3.x, sanitise HTML with `sanitize-html` 2.x, strip quoted history, thread by `In-Reply-To`, `References` and subject plus sender fallback, upsert `crm_contact` by sender.
- Outbound: reply via Resend from the mailbox address with `Message-ID` threading; attachments through `data-layer/file-storage`.
- In-app chat: portal widget `<SupportChat/>` (`identity/customer-portal-shell`) creating `channel: chat` conversations; messages sync live through `realtime/record-sync`; typing and presence via `realtime/presence`.
- Internal notes reuse `collab/comments` threads anchored to the conversation (`anchor_type: entity`), `visibility: internal`, so mentions and Linear escalation work unchanged.
- Console UI `_app/support/`: three-pane inbox (conversation list as a saved grid/list view with filters status, assignee, tag; conversation view; contact sidebar with CRM fields, deals and past conversations), assignment, snooze, macros, keyboard shortcuts via `input/command-registry` (`e` resolve, `a` assign, `r` reply).
- Metrics: first response and resolution time per conversation into `attr_daily`-style rollup for a support dashboard block.

Out: phone, WhatsApp, public knowledge base, AI auto-replies (a later content-agent skill), SLA escalation policies beyond a timer field.

**Spec**

- Contact matching: exact email, then plus-address stripped, then domain to company only (conversation unlinked from contact but linked to company).
- Sanitisation allowlist: basic formatting, links with `rel="noopener"`, inline images rewritten to stored files; scripts and styles removed.
- Status rules: inbound message reopens `resolved` within 7 days, else new conversation; outbound reply sets `pending`; snooze unsnoozes on inbound.
- Permissions: `support.read|reply|assign|manage`; customers see only their own conversations in the portal; agents (`identity/agent-principals`) may add notes, not reply.
- Chat widget works unauthenticated with email capture, upgrading to the contact on login.
- All inbound events audited; every reply logged as `crm_activity kind email`.

**Definition of done**

- Vitest: threading heuristics on 30 fixture emails (Gmail, Outlook, Apple Mail quoting), sanitiser, contact matching precedence, status rules, permission matrix.
- Integration: send a real email to the staging mailbox, see it in the inbox, reply, receive reply threaded (recording attached).
- Playwright: portal chat message appears in console within 1 s and reply returns; internal note with mention; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for inbox, conversation and portal widget (single-pane under `lg`).
- axe clean; inbox fully keyboard-operable.
- `docs/growth/support.md` (mailbox setup, DNS, macros); CHANGELOG entry; Linear comment with recording and screenshots.

**Edge cases**

- Auto-reply loops (out-of-office ping-pong): detect `Auto-Submitted` and `Precedence: bulk` headers; never auto-reply to auto-replies.
- Attachment over 25 MB or blocked type: stored reference with warning, not dropped silently.
- Same email CC'd to two mailboxes: one conversation per mailbox, cross-linked.
- Customer writes from a new address: new contact suggested for merge with existing (manual).
- Chat from a customer whose company has 3 staff contacts: conversation links the individual; company visible in sidebar.
- Resend inbound webhook retried: dedupe on `provider_message_id`.

**Dependencies**

`growth/crm-model` and `collab/comments` (hard). `realtime/record-sync` and `realtime/presence` for chat (fallback: 3 s polling), `data-layer/file-storage`, `identity/customer-portal-shell`, `growth/outreach-sequences` (replies to sequences open conversations), `input/command-registry`.

**Agent**

Built by Beacon (CRM Builder) with Nova consulted on live chat. Reviewed by Sentinel (Security Auditor for HTML sanitisation and permissions, Visual Inspector, Edge Case Hunter for threading) and Quill.

**Size**

L: two channels, threading heuristics, a three-pane console and a portal widget.
