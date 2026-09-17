---
identifier: "PAP-198"
title: "Catalog export formats and API limits of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P1"
type: "Research"
priority: 3
surfaces: ["Staff"]
milestone: "Import framework and CSV"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-199"]
key: "migration/format-research"
url: "https://linear.app/paperos/issue/PAP-198/catalog-export-formats-and-api-limits-of-airtable-notion-clickup"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-198: Catalog export formats and API limits of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks

**Goal**

Before building any importer, know exactly what each source system lets us pull, in what shape and how fast: catalogue the export formats, API endpoints, auth models, pagination, rate limits, attachment access and schema quirks of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks (plus Xero, Linear and Google Sheets since importers for them are planned), so `migration/import-framework` designs its connector interface against real constraints.

**Scope**

In:
- One reference sheet per source in `docs/migration/sources/{source}.md` with a fixed template: auth (OAuth scopes or PAT), base URL and SDK (`@notionhq/client` 4.x, `@linear/sdk`, `intuit-oauth`, `xero-node`, Airtable REST, ClickUp REST v2, Monday GraphQL, HubSpot v3), list and pagination shape, rate limits (Airtable 5 rps per base, Notion 3 rps average, HubSpot 100 per 10 s, QuickBooks 500 per minute per realm, and so on, each verified against current docs with the date checked), maximum page sizes, incremental sync support (`last_edited_time`, `updatedAt`, CDC or none), attachment URL expiry (Airtable URLs expire after hours, Notion after 1 h), export UI formats (CSV, JSON, Markdown+CSV zip, IIF, QBO), webhook availability, sandbox availability, and known schema quirks.
- Field type matrix `docs/migration/field-type-matrix.md`: every source field type mapped to a `tables/field-types` type with lossy flags (for example Airtable `barcode` -> text, Notion `rollup` -> computed then rollup, ClickUp `custom_field.dropdown` -> select, QuickBooks `Account.Classification` -> ledger account type).
- Sample exports captured into `packages/import/fixtures/{source}/` (anonymised, under 1 MB each) from real trial workspaces, plus recorded API responses (Polly.js or hand-saved JSON) for offline tests.
- Throughput estimates: time to import 10k rows, 100k rows and 1k attachments per source at documented limits, in a table.
- Legal notes: terms of service constraints on bulk export or scraping per source.

Out: writing connectors, mapping UI, evaluating sources beyond the list beyond a one-line mention.

**Spec**

- Time-box 1 agent-day; 45 minutes per source; unknowns recorded as "unverified" with a link to where the answer lives.
- Each reference sheet ends with a "connector implications" section: recommended auth flow, recommended sync strategy (full, incremental by timestamp, cursor), attachment strategy (stream to `data-layer/file-storage` immediately because URLs expire), and the three hardest edge cases.
- Fixtures cover: relations and lookups, multi-select, attachments, formulas, nested pages or subtasks, and archived or deleted items.
- Output consumed by `migration/import-framework` for the `SourceConnector` interface and by each importer issue; their descriptions are updated with verified limits by comment.

**Definition of done**

- Nine reference sheets and the field type matrix merged under `docs/migration/`, rendering in the docs engine with the sources index page.
- Fixtures committed for at least Airtable, Notion, ClickUp, Linear, QuickBooks and CSV; fixture README explains anonymisation.
- Throughput table reviewed by Scout and Atlas; disagreements resolved in the PR.
- Every rate limit and expiry claim carries a source URL and a checked-on date; Vitest lint asserts the frontmatter `checkedOn` is present.
- Screenshots of each source's export UI at 1280 attached.
- CHANGELOG entry; Linear comment linking the index page and notifying `migration/import-framework`, `migration/airtable`, `migration/notion`, `migration/clickup-linear`, `migration/stripe-quickbooks`.

**Edge cases**

- Source requires a paid plan for API access (Airtable attachments on free tier, ClickUp some endpoints): note the plan and a UI-export fallback.
- Rate limits differ by plan or per token vs per workspace: record both and the safe default.
- Attachment URLs expire mid-import: connector implication is stream-on-discovery.
- Sources with soft-deleted items visible via API (Notion `archived`, Linear `trashed`): document whether to import as archived.
- Monday and HubSpot have no importer issue yet: sheets still written; note as follow-on.
- Trial workspace lacks features (formulas need paid): fixtures marked partial.

**Dependencies**

None; can start now. Informs `migration/import-framework` (interface design) and every importer; overlaps with `growth/growth-research` on HubSpot mapping (share the CRM mapping section).

**Agent**

Researched by Scout (Import Mapper). Reviewed by Atlas for completeness and Quill for the docs template.

**Size**

M: nine sources at 45 minutes each plus fixtures and the matrix.
