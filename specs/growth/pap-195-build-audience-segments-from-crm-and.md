---
identifier: "PAP-195"
title: "Build audience segments from CRM and product usage that feed campaigns and in-app targeting"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-163", "PAP-166", "PAP-187", "PAP-279", "PAP-303", "PAP-337"]
blocks: []
key: "growth/segments"
url: "https://linear.app/paperos/issue/PAP-195/build-audience-segments-from-crm-and-product-usage-that-feed-campaigns"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:32.030Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-195: Build audience segments from CRM and product usage that feed campaigns and in-app targeting

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Let staff define audiences once and use them everywhere: segments built from CRM fields, product usage events and billing state through the shared filter builder, evaluated dynamically or frozen, and exposed to outreach, social campaigns, notifications and in-app targeting through one `segments.membersOf` API.

**Scope**

In: extend `crm_segment` (`definition: FilterTree` over a virtual "audience" source joining contacts, companies, deal aggregates, `attr_event` counts, entitlements and login recency; `refresh: realtime|hourly|manual`; `size_estimate`; `definition_version`); evaluator `packages/growth/src/segments/evaluate.ts`; procedures `segments.*`; hook `useInSegment(key)`; consumers PAP-191, PAP-190, PAP-136; UI `_app/marketing/segments`.

Out: lookalike audiences, ad-audience sync, per-user flags outside segments.

**Spec**

* Grammar extensions contributed through the PAP-279 extension hook and PAP-166 `extraOperators`: relative dates, `performed X at least N times in window`, `has deal with stage kind won`, `in segment S` (no cycles).
* Evaluation is set-based SQL compiled through PAP-163 producing `(tenant_id, segment_id, contact_id)`; incremental mode recomputes contacts touched since `last_evaluated_at` via `updated_at` and event watermarks; over 1M candidates batched at 50k with a progress row; one evaluation in flight per segment.
* `segments.preview(definition) -> { count, sample[] }` with `statement_timeout 2000`, returning `estimated: true` from `EXPLAIN` when exceeded.
* Membership changes emit `segment.entered|exited { segmentId, contactId }`.
* `segments.contains(contactId, segmentIds[])` indexed for in-app use under 20 ms; `useInSegment` resolves the current user's contact by email link and caches per session.
* Permissions `segment.read|write|use`; `use` allows selecting without seeing the definition.

**Interface contract**

Provides: `segments.list|get|create|update|archive|preview|membersOf|contains|freeze`, `useInSegment(key)`, events `segment.entered|exited`, `SegmentRef` type accepted by `outreach.enrol` (PAP-191), campaign audience notes (PAP-190) and notification audience filters (PAP-136), "used by" registry `registerSegmentConsumer`. Consumes: `crm_segment` (PAP-187), `FilterBuilder` and extension hook (PAP-166, PAP-279), compiler (PAP-163), `attr_event` (PAP-194, operator hidden if absent), entitlements (PAP-178, soft), portal shell for the targeting demo (PAP-64), jobs (PAP-43).

**Definition of done**

* Vitest, performance and Playwright below green; axe clean, builder keyboard-operable.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for list and builder.
* `docs/growth/segments.md` (operators, refresh modes, targeting hook); CHANGELOG; Linear comment with screenshots and bench numbers.

**Test plan**

* Unit: compilation of each new operator, cycle detection for nested segments, enter and exit event derivation, `contains` correctness, version bump on definition change.
* Integration: incremental evaluation equals full evaluation on fixtures; 200k-contact bench with a five-clause segment under 10 s full and 1 s incremental; `contains` under 20 ms; coalesced manual refresh.
* E2E: build a three-clause segment including an event clause, watch the live count, freeze it, select it in a sequence, and see a portal banner gated by `useInSegment`.
* Visual: matrix above.

**Demo**

Reviewer creates "Customers who viewed pricing twice in 30 days and have no open deal", sees the live count and sample, freezes it, opens a sequence and picks it as the audience, then logs in as a member on the portal and sees the targeted banner. Under two minutes.

**Edge cases**

* Custom field deleted: definition invalid, evaluation paused, owner notified, members kept.
* Match then unmatch within one window: exit only if previously a member.
* Nested segment archived: parent invalid with a clear message.
* Staff without a contact: `useInSegment` returns false.
* Relative dates in tenant timezone, documented.

**Dependencies**

PAP-187 (hard), PAP-166 (hard), PAP-163 (hard), PAP-194 (soft), PAP-178 (soft), PAP-64, PAP-43, PAP-279. Consumed by PAP-191, PAP-190, PAP-136.

**Agent**

Builder: Beacon (CRM Builder) with Nova on compiler extensions. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter), Atlas for the shared grammar.

**Size**

M: grammar extension, evaluator and one builder page.
