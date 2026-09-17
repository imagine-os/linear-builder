---
key: "growth/outreach/ui"
title: "Sequence builder, template editor with preview and test send, enrolments grid and domain setup wizard"
project: "growth"
parent: "PAP-191"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "Campaigns and social"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012"
status: "pending"
---

# Sequence builder, template editor with preview and test send, enrolments grid and domain setup wizard

**Goal**

Let staff build and run sequences without engineering help and see exactly what happened to each enrolment.

**Scope**

In: builder (steps with delay editors, channel, template picker, conditions via PAP-166 `FilterBuilder`), template editor with live preview and test send to the allowlist, enrolments as a PAP-165 grid, domain wizard with DNS records and warmup status. Out: drafting (PAP-192).

**Spec**

* Builder validates delays and channel mix; enrol by contacts or segment (PAP-195 `SegmentRef`).
* Template editor shows variables, renders a sample contact, blocks save on missing variables.
* Domain wizard polls `dns_status` and shows warmup stage and daily cap.

**Interface contract**

Provides: routes `_app/marketing/outreach/*`, `<SequenceBuilder />`, `<TemplateEditor />`. Consumes: both siblings, PAP-166, PAP-165, PAP-195 (soft).

**Definition of done**

* Playwright build, enrol, view enrolments; screenshots at seven widths in light and dark; axe clean.

**Test plan**

* Unit: builder validation.
* E2E: the parent's umbrella flow through the UI.

**Demo**

Build a two-step sequence, send a test email, enrol a contact, open the enrolments grid.

**Edge cases**

* Unverified domain blocks activation with the wizard link; template with missing variable fails in preview.

**Dependencies**

Both siblings (hard), PAP-166, PAP-165, PAP-195 (soft).

**Agent**

Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
