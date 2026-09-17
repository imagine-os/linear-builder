---
identifier: "PAP-189"
title: "Build CRM pipeline (kanban), contact list and company views on the tables engine"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "CRM core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-165", "PAP-167", "PAP-187"]
blocks: []
key: "growth/crm-views"
url: "https://linear.app/paperos/issue/PAP-189/build-crm-pipeline-kanban-contact-list-and-company-views-on-the-tables"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-189: Build CRM pipeline (kanban), contact list and company views on the tables engine

**Goal**

Give every tenant a working sales workflow on day one: a deal pipeline kanban, a contacts grid and a company detail page, all rendered by the tables/views engine from saved view definitions rather than bespoke components, so CRM screens inherit filtering, grouping, sharing and permissions for free and prove the engine on a real domain.

**Scope**

In:
- Routes in `apps/web/src/routes/_app/crm/`: `pipeline`, `contacts`, `companies`, `companies/$id`, `contacts/$id`, `deals/$id`, built from the three page specs in `growth/crm-model` (extend with `deal-detail` and `contact-detail` specs here).
- Saved view definitions in `packages/growth/src/crm/views/*.view.json` following `tables/view-model-spec`: `deals-pipeline` (kanban grouped by `stage_id`, swimlane option by `owner_user_id`, card fields title, company, amount, expected close, WIP limit per stage optional), `contacts-all` (grid: name, email, company, lifecycle, owner, last activity; default sort last activity desc), `companies-all` (grid with rollup columns open deals count and pipeline value), plus per-audience defaults via `tables/view-sharing` (sales rep sees "My deals" by default).
- Detail pages composed from `design-system/layout-components` (`Inspector`, `SplitPane`): header with key fields, activity timeline (`design-system/data-display` `Timeline`), related lists rendered as embedded views, quick actions (log note, schedule task, move stage, convert lead).
- Drag-and-drop between stages via the kanban view calling `crm.deals.move`; optimistic update with `realtime/conflict-ux` banners on failure.
- Command registry entries (`input/command-registry`): "New deal", "New contact", "Go to pipeline".
- Seed demo data (40 companies, 200 contacts, 60 deals) in the `demo` profile for screenshots and tests.

Out: sequences, segments UI, imports, email compose (support inbox), reporting dashboards beyond the pipeline value rollup.

**Spec**

- Kanban card: `title`, company avatar (`AvatarStack`), amount formatted by tenant currency, days in stage badge (amber over 14, red over 30), owner avatar.
- Stage columns show count and sum aggregates from the view's `aggregations`.
- Moving to a `won` or `lost` stage opens a small dialog (won: confirm amount and close date; lost: reason select) before committing.
- Contacts grid inline-edits `lifecycle`, `owner`, `tags`; bulk actions: add to segment, assign owner, export CSV (`crm.contacts.export` permission).
- Company detail related lists: contacts, deals, activities, support conversations (placeholder until `growth/support-inbox`), each an embedded view with its own filter state in the URL.
- Empty states use `EmptyState` with a primary action ("Import contacts" linking to `migration/csv-excel`).
- All pages responsive: under `md` the kanban becomes a stage picker plus single-column list; inspector becomes a drawer.

**Definition of done**

- Five page specs validate; conformance tests from `spec-builder/conformance-tests` pass.
- Vitest: view JSON validates against the view model schema; move-stage dialog logic; permission-gated bulk actions.
- Playwright: create company, contact and deal; drag deal across two stages; won dialog; inline edit lifecycle; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for pipeline, contacts and company detail.
- axe clean; kanban drag has the keyboard alternative from `input/drag-drop`.
- `docs/growth/crm-views.md` (how to add a CRM field and have it appear in views); CHANGELOG entry; Linear comment with Pages demo link and screenshots.

**Edge cases**

- 2,000 deals in one stage: column virtualised; aggregates come from the server, not rendered cards.
- Deal with no company: card shows contact instead; grid rollups skip it.
- Concurrent stage move by two staff: last write wins with a banner and undo (`realtime/conflict-ux`).
- Pipeline with a single stage or zero stages: pipeline page shows setup prompt, not a blank board.
- Custom field added via `tables/field-types` after views exist: appears in the field picker, not automatically in cards.
- Customer-audience principal hitting `/crm/*`: redirected to portal with a 403 toast; permission tests cover it.

**Dependencies**

`growth/crm-model` and `tables/kanban-view` (hard). `tables/grid-view`, `tables/view-sharing`, `design-system/layout-components`, `design-system/data-display`, `input/drag-drop` (keyboard alternative), `realtime/conflict-ux` (soft). Unblocks `growth/segments` UI entry points and `growth/support-inbox` related list.

**Agent**

Built by Beacon (CRM Builder) with Nova (Views Engineer) consulted on view JSON. Reviewed by Sentinel (Visual Inspector across the matrix, Code Reviewer) and Iris for component usage.

**Size**

M: mostly configuration of the views engine plus two detail pages and dialogs.
