---
identifier: "PAP-406"
title: "Sequence builder, template editor with preview and test send, enrolments grid and domain setup wizard"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: "PAP-191"
children: []
blockedBy: ["PAP-405"]
blocks: []
key: "growth/outreach/ui"
url: "https://linear.app/paperos/issue/PAP-406/sequence-builder-template-editor-with-preview-and-test-send-enrolments"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:47.457Z"
---

# PAP-406: Sequence builder, template editor with preview and test send, enrolments grid and domain setup wizard

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
