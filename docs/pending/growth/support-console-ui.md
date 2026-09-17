---
key: "growth/support/console-ui"
title: "Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts and metrics"
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

# Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts and metrics

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
