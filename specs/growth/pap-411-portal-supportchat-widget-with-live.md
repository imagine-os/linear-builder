---
identifier: "PAP-411"
title: "Portal SupportChat widget with live sync and presence, unauthenticated email capture and internal notes on comment threads"
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
blockedBy: ["PAP-131", "PAP-319", "PAP-410", "PAP-475"]
blocks: ["PAP-412", "PAP-805", "PAP-841"]
key: "growth/support/chat-notes"
url: "https://linear.app/paperos/issue/PAP-411/portal-supportchat-widget-with-live-sync-and-presence-unauthenticated"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-411: Portal SupportChat widget with live sync and presence, unauthenticated email capture and internal notes on comment threads

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Add the in-app channel and internal collaboration: customers chat from the portal in real time and staff discuss privately on the same conversation.

**Scope**

In: `<SupportChat/>` in the PAP-64 shell creating `channel: chat` conversations, live messages via PAP-143 with 3-second polling fallback, presence and typing via PAP-141, email capture for anonymous visitors upgraded on login, internal notes as PAP-131 threads with `visibility: internal`. Out: console UI (sibling).

**Spec**

* Widget works unauthenticated with email capture; messages land within one second when realtime is available.
* Notes reuse comment mentions and Linear escalation unchanged; agents may note, not reply.

**Interface contract**

Provides: `<SupportChat/>`, `support.chat.start|send`, note anchoring convention `anchor_type: entity`. Consumes: threading child, PAP-64, PAP-143, PAP-141, PAP-131.

**Definition of done**

* Playwright chat round trip under one second; note with mention; screenshots of the widget at 320, 375, 1024.

**Test plan**

* Unit: email capture upgrade, permission matrix for agents.
* E2E: portal message appears in a raw console list and the reply returns; fallback polling works with realtime disabled.

**Demo**

Open the portal as a customer, send a chat, reply from the console, add an internal note.

**Edge cases**

* Company with three contacts links the individual; offline customer sees queued state.

**Dependencies**

Threading child (hard), PAP-131 (hard), PAP-64, PAP-143 and PAP-141 (soft).

**Agent**

Builder: Beacon with Nova on live chat. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
