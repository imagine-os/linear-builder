---
identifier: "PAP-412"
title: "Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts and metrics"
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
blockedBy: ["PAP-411"]
blocks: ["PAP-806", "PAP-807", "PAP-840", "PAP-867", "PAP-898"]
key: "growth/support/console-ui"
url: "https://linear.app/paperos/issue/PAP-412/three-pane-inbox-on-a-saved-list-view-conversation-view-contact"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:13.692Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-412: Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts and metrics

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Give staff a fast, keyboard-first inbox that shows the whole customer beside every conversation.

**Scope**

In: `_app/support/` three-pane layout (PAP-169 list view with filters status, assignee, tag; conversation; contact sidebar with CRM fields, deals, past conversations), assign, snooze, canned replies, shortcuts `e`, `a`, `r` via PAP-151, first-response and resolution rollups for a dashboard block, `<ConversationList/>` embedded on PAP-189 pages.

**Spec**

* Single-pane under `lg`; inbox fully keyboard-operable; snooze unsnoozes on inbound.
* Metrics rolled up daily for a PAP-173 number block.

**Interface contract**

Provides: console routes, `<ConversationList contactId? companyId? />`, commands `support.*`, dataset `support.metrics`. Consumes: both siblings, PAP-169, PAP-151, PAP-70, PAP-173.

**Definition of done**

* Playwright inbox flows; screenshots at seven widths in light and dark; axe clean; `docs/growth/support.md`.

**Test plan**

* Unit: metrics rollup.
* E2E: assign, snooze, macro reply, keyboard-only pass.

**Demo**

Work three conversations with the keyboard only, then open the metrics block.

**Edge cases**

* 10k conversations paginate through the list view; deleted contact shows an unlinked sidebar.

**Dependencies**

Both siblings (hard), PAP-169, PAP-151, PAP-70, PAP-173 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Visual Inspector), Quill.

**Size**

M: one session.
