---
identifier: "PAP-195"
title: "Build audience segments from CRM and product usage that feed campaigns and in-app targeting"
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
blockedBy: ["PAP-163", "PAP-166", "PAP-187", "PAP-279"]
blocks: []
key: "growth/segments"
url: "https://linear.app/paperos/issue/PAP-195/build-audience-segments-from-crm-and-product-usage-that-feed-campaigns"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-195: Build audience segments from CRM and product usage that feed campaigns and in-app targeting

**Goal**

Let staff define audiences once and use them everywhere: segments built from CRM fields, product usage events and billing state through the shared filter builder, evaluated dynamically or frozen as static lists, and exposed to outreach sequences, social campaigns and in-app targeting (banners, feature flags, portal messages) through one `segments.membersOf` API.

**Scope**

In:
- Extend `crm_segment` from `growth/crm-model`: `definition jsonb` uses the filter tree grammar of `tables/filter-sort-group-ui` over a virtual "audience" data source joining `crm_contact`, `crm_company`, `crm_deal` aggregates, `attr_event` counts (`growth/attribution`), entitlements and plan (`business-core/entitlements`), and `user` login recency; `refresh: realtime|hourly|manual`; `size_estimate`; `owner`.
- Evaluator `packages/growth/src/segments/evaluate.ts`: compiles the filter tree through `tables/query-compiler` to SQL producing `(tenant_id, segment_id, contact_id)` membership; incremental mode recomputes only contacts touched since `last_evaluated_at` (via `updated_at` and event watermarks); pg-boss job per segment on its refresh schedule.
- API: `segments.list/get/create/update/archive`, `segments.preview(definition) -> { count, sample[] }` (limit 10, under 2 s), `segments.membersOf(id, cursor)`, `segments.contains(contactId, segmentIds[])` (indexed for in-app targeting), `segments.freeze(id)` to static.
- In-app targeting hook `useInSegment(key)` in `packages/growth/src/segments/react.ts` for the portal and console shells (`identity/customer-portal-shell`), resolving the current user's contact via `user.email` link and caching per session.
- Consumers wired: `growth/outreach-sequences` enrol-by-segment (dynamic segments auto-enrol new members if the sequence allows), `growth/social-scheduler` campaign audience note, `collab/notifications` audience filter.
- UI at `_app/marketing/segments`: list (grid view), builder page with the filter builder, live count and sample table, refresh settings, "used by" panel listing sequences and campaigns, membership history sparkline.

Out: ML lookalike audiences, external ad audience sync, per-user feature flags outside segments.

**Spec**

- Grammar additions to the filter builder: relative dates (`in the last 30 days`), event count comparators (`performed X at least N times in window`), aggregate on related (`has deal with stage kind won`), set membership (`in segment S`, no cycles).
- Evaluation is set-based SQL; a segment with over 1M candidate rows runs in batches of 50k with a progress row.
- Dynamic membership changes emit `segment.entered|exited` events with the contact id for consumers.
- Segment definitions are versioned (`definition_version`, previous stored) so a sequence can show which version enrolled a contact.
- `preview` runs with `statement_timeout 2000` and returns `estimated: true` from `EXPLAIN` row estimates when exceeded.
- Permissions `segment.read|write|use`; `use` allows selecting a segment without seeing its definition.

**Definition of done**

- Vitest: grammar compilation for each new operator, incremental evaluation equals full evaluation on fixtures, cycle detection for nested segments, enter/exit events, `contains` correctness.
- Performance: 200k contact fixture; full evaluation of a five-clause segment under 10 s, incremental under 1 s, `contains` under 20 ms (bench committed).
- Playwright: build a segment with three clauses including an event clause, see live count, freeze, use it in a sequence; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for list and builder.
- axe clean; filter builder keyboard-operable (inherits from `tables/filter-sort-group-ui`).
- `docs/growth/segments.md` (operators, refresh modes, targeting hook); CHANGELOG entry; Linear comment with screenshots and bench numbers.

**Edge cases**

- Segment references a custom field later deleted: definition marked invalid, evaluation paused, owner notified; members retained.
- Contact matches then unmatches within one refresh window: exit event only if it was a member at the last evaluation.
- Nested segment archived: parent becomes invalid with a clear message rather than silently shrinking.
- User with no CRM contact (staff testing portal): `useInSegment` returns false, no error.
- Timezone-relative dates: evaluated in tenant timezone; documented.
- Manual refresh spammed: coalesced; at most one evaluation in flight per segment.

**Dependencies**

`growth/crm-model` and `tables/filter-sort-group-ui` (hard). `tables/query-compiler`, `growth/attribution` (event clauses; skip operator if absent), `business-core/entitlements` (plan clauses, soft), `identity/customer-portal-shell` for the targeting hook demo.

**Agent**

Built by Beacon (CRM Builder) with Nova (Views Engineer) on compiler extensions. Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Atlas for the shared grammar.

**Size**

M: grammar extension, evaluator and one builder page; consumers are thin.
