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
blockedBy: ["PAP-165", "PAP-167", "PAP-187", "PAP-333", "PAP-343", "PAP-483", "PAP-614", "PAP-630", "PAP-790", "PAP-791"]
blocks: ["PAP-491", "PAP-795", "PAP-796", "PAP-810", "PAP-811"]
key: "growth/crm-views"
url: "https://linear.app/paperos/issue/PAP-189/build-crm-pipeline-kanban-contact-list-and-company-views-on-the-tables"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:35.814Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-189: Build CRM pipeline (kanban), contact list and company views on the tables engine

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give every tenant a working sales workflow on day one: a deal pipeline kanban, a contacts grid and company, contact and deal detail pages, all rendered by the views engine from saved view definitions so CRM screens inherit filtering, grouping, sharing and permissions and prove the engine on a real domain.

**Scope**

In: routes `apps/web/src/routes/_app/crm/` (`pipeline`, `contacts`, `companies`, `companies/$id`, `contacts/$id`, `deals/$id`) from the PAP-187 specs plus `deal-detail` and `contact-detail` specs; view JSON `packages/growth/src/crm/views/*.view.json` (`deals-pipeline`, `contacts-all`, `companies-all`); per-audience defaults via PAP-172; detail pages from PAP-70 layouts; won and lost dialogs; commands "New deal", "New contact", "Go to pipeline"; demo seed of 40 companies, 200 contacts, 60 deals.

Out: sequences, segment UI, imports, email compose, dashboards beyond pipeline value.

**Spec**

* Kanban card: title, company avatar, amount in tenant currency, days-in-stage badge (amber over 14, red over 30), owner avatar; stage headers show count and sum from `aggregations`.
* Moving to a `won` or `lost` stage opens a dialog (won: amount and close date; lost: reason) through the PAP-167 `onMove` hook before commit.
* Contacts grid inline-edits `lifecycle`, `owner`, `tags`; bulk actions add to segment, assign owner, export CSV (`crm.contacts.export`).
* Company detail: header, activity `Timeline` (PAP-71), related lists (contacts, deals, activities, support placeholder for PAP-197) as embedded views with URL filter state.
* Detail routes reuse the shared record detail shell when PAP-333 lands; until then a local `Inspector` layout.
* Empty states link to PAP-200 import; under `md` the kanban becomes a stage picker plus list and the inspector a drawer.

**Interface contract**

Provides: the six routes, three view JSON files as the reference for "views from JSON", `WonLostDialog`, `useDealMove()`, commands `crm.*`, demo seed profile `crm`. Consumes: schema and routers (PAP-187), kanban `onMove` (PAP-167), grid (PAP-165), defaults and sharing (PAP-172, soft), layouts (PAP-70), `Timeline`, `AvatarStack` (PAP-71), keyboard drag (PAP-155), conflict banners (PAP-144, soft), commands (PAP-151). Consumed by PAP-195 (entry points), PAP-197 (related list), PAP-193 (lead landing).

**Definition of done**

* Five page specs validate; PAP-123 conformance tests pass.
* Vitest, Playwright and axe below green; kanban has the PAP-155 keyboard alternative.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for pipeline, contacts and company detail.
* `docs/growth/crm-views.md` (adding a CRM field that appears in views); CHANGELOG; Linear comment with Pages demo and screenshots.

**Test plan**

* Unit: view JSON validates against `viewSpecSchema`; won and lost dialog reducer; permission-gated bulk actions.
* Integration: `crm.deals.move` through the kanban writes stage and `sort_key`; per-audience default resolves "My deals" for a sales rep.
* E2E: create company, contact and deal; drag a deal across two stages; won dialog; inline lifecycle edit; customer-audience principal redirected from `/crm/*` with a 403 toast.
* Visual: seven widths, light and dark, three pages.

**Demo**

Reviewer opens `/crm/pipeline` on the seeded tenant, drags a deal to Won and fills the dialog, opens the company page from the card, logs a note in the timeline and sees the contacts grid update lifecycle inline. Under two minutes.

**Edge cases**

* 2,000 deals in one stage: virtualised column, server aggregates.
* Deal without a company shows the contact; rollups skip it.
* Concurrent stage moves: last write wins with banner and undo.
* Pipeline with no stages shows a setup prompt.
* Custom field added later appears in the picker, not automatically on cards.

**Dependencies**

PAP-187 (hard), PAP-167 (hard), PAP-165 (hard), PAP-172 (soft), PAP-70, PAP-71, PAP-155, PAP-144 (soft), PAP-123. Feeds PAP-195, PAP-197.

**Agent**

Builder: Beacon (CRM Builder) with Nova consulted on view JSON. Reviewer: Sentinel (Visual Inspector, Code Reviewer), Iris for component usage.

**Size**

M: mostly configuration of the views engine plus two detail pages and dialogs.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
