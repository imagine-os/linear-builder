# Round 4 digest: Migration & Import Tools (`migration`)

Benchmarks: Airtable, Notion, ClickUp, Monday, Asana, Trello, Jira, Linear, HubSpot, Salesforce, Pipedrive, QuickBooks Online, Xero, FreshBooks, Wave, Zoho Books, Shopify, WooCommerce, Square, Google Sheets, Drive and Contacts, Dropbox and OneDrive, Baserow and NocoDB importers, Airbyte and Fivetran (connector conformance and incremental sync patterns)

Feature matrix: 51 rows (29 covered, 4 partial, 18 gap). New issues: 20 (4 children, 16 gap issues; 17 deferred to v0.2). Amendments: 8. Cross-project suggestions: 6.

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Source research sheets, field-type matrix, fixtures | covered | PAP-198 |  |
| Importer test accounts and fixture workspaces | partial | PAP-198, r4/migration/importer-test-accounts-and-fixture-workspaces | Inline WP2; now its own issue |
| Connector interface, engine, batching, resumability | covered | PAP-347 |  |
| Dry run, commit, rollback semantics | covered | PAP-348 |  |
| Type inference, mapping wizard, run history | covered | PAP-349 |  |
| Connector conformance harness and scaffold | gap | r4/migration/connector-conformance-harness-and-scaffold | Referenced by seven specs, owned by none |
| Shared OAuth connections, token refresh and revocation | gap | r4/migration/source-oauth-connections-and-token-refresh | Each connector re-implements auth |
| External id mapping, incremental cursors, re-sync safety | covered | PAP-201 |  |
| Scheduled re-sync, sync status, health alerts | partial | PAP-201, r4/migration/scheduled-resync-and-sync-status | PAP-201 out: scheduling |
| Webhook-driven near-real-time sync | gap | - | v0.3; noted in the resync issue |
| Duplicate detection and merge preview on import | partial | PAP-201, r4/migration/import-duplicate-detection-and-merge-preview | Exact keys only today |
| AI-assisted mapping suggestions | gap | r4/migration/ai-mapping-assistant |  |
| CSV, TSV, Excel, Google Sheets | covered | PAP-200 | Amend legacy xls library |
| Airtable: connector, fields, views | covered | PAP-414, PAP-415, PAP-416 |  |
| Airtable automations | gap | r4/migration/airtable-automations-conversion | PAP-202 out |
| Notion: connector, blocks, hierarchy | covered | PAP-417, PAP-418, PAP-419 | Deferred |
| ClickUp import | covered | PAP-204, r4/migration/clickup-connector-and-markup-mapping | Split into a child |
| Linear import (mirror own workspace) | covered | PAP-204, r4/migration/linear-connector-and-pm-mapping | Split into a child |
| Asana, Trello, Jira import | gap | r4/migration/asana-trello-jira-connectors |  |
| Monday and HubSpot via CSV recipes | covered | PAP-413 |  |
| Salesforce and Pipedrive CRM import | gap | r4/migration/salesforce-and-pipedrive-crm-import |  |
| Google and Outlook contacts, vCard | gap | r4/migration/contacts-import-google-outlook-vcard |  |
| Stripe history into CRM, billing and ledger | covered | PAP-423 | Rates table amendment |
| QuickBooks and Xero charts and opening balances | covered | PAP-424 |  |
| Finance import wizard and trial balance gate | covered | PAP-425 |  |
| FreshBooks, Wave, Zoho Books recipes | gap | r4/migration/accounting-csv-recipes-freshbooks-wave-zoho |  |
| Shopify, WooCommerce, Square commerce import | gap | r4/migration/shopify-woocommerce-square-import |  |
| Files from Google Drive, Dropbox, OneDrive | gap | r4/migration/drive-dropbox-files-import |  |
| Email and calendar history import (mbox, ICS) | gap | - | v0.3; no issue this round |
| Placeholder users and invite conversion | gap | r4/migration/placeholder-users-and-invite-conversion | Assumed by four importers |
| Export archive format and streaming job | covered | PAP-420 | PII amendment |
| Export UI, scheduling, encryption, links | covered | PAP-421 |  |
| Round-trip paperos connector and verification | covered | PAP-422 | `ledger.importJournal` amendment |
| Per-view CSV and XLSX export | covered | PAP-322, PAP-183 | Tables and finance projects |
| DSAR per-person export | covered | PAP-221 | Identity project |
| Template pack format, lint, applier, upgrade | covered | PAP-426 |  |
| Packs wave 1: agency, retail, SaaS, clinic, restaurant | covered | PAP-427 |  |
| Packs wave 2: law firm, real estate, property management, construction, ecommerce | gap | r4/migration/packs-wave-2-law-real-estate-property-construction-ecommerce | Brief asks for every business type |
| Packs wave 3: nonprofit, school, church, gym, salon | gap | r4/migration/packs-wave-3-nonprofit-school-church-gym-salon |  |
| Template gallery in onboarding and settings | covered | PAP-428, PAP-367 |  |
| Capture a tenant as a template pack | gap | r4/migration/template-pack-from-tenant |  |
| Pack marketplace or sharing between tenants | gap | - | v0.3; no issue this round |
| Migration agent (interview, plan, dry runs, approval) | covered | PAP-208 | Approval path amendment |
| Migration verification dashboard and cutover checklist | gap | r4/migration/migration-verification-dashboard-and-cutover |  |
| Import permissions and audit reasons | partial | PAP-347, PAP-349 | Amendment registers `import.*` set |
| Rate-limit and throughput registry per source | covered | PAP-198, PAP-347 |  |
| Attachment migration before URL expiry | covered | PAP-414, PAP-418 |  |
| Large-file uploads for imports | covered | PAP-200, PAP-37 |  |
| Contract package, conformance, kernel wiring | covered | PAP-492, PAP-494, PAP-496 |  |
| Two-way sync with sources | covered | PAP-101 | Non-goal beyond Linear (pm-linear) |
| Import from another PaperOS tenant (tenant move) | covered | PAP-422 |  |

## New issues

| Key | Title | Parent | Size | Model / effort | Prio | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/migration/importer-test-accounts-and-fixture-workspaces` | Importer test accounts and fixture workspaces: idempotent seed scripts, secret names in both forges, fixtures health workflow and the NJ-13 sign-up list | - | S (2) | Sonnet 5 / medium | 2 | no | Import framework and CSV |
| `r4/migration/connector-conformance-harness-and-scaffold` | Connector conformance harness and scaffold: `connectorConformance()` Vitest suite every SourceConnector passes, recorded-HTTP fixture conventions and `pnpm paperos connector scaffold` | - | M (3) | Sonnet 5 / high | 2 | no | Import framework and CSV |
| `r4/migration/source-oauth-connections-and-token-refresh` | Source connections: shared OAuth connect flow, encrypted token storage, refresh and revocation for every import connector, with a connections settings page | - | M (3) | Opus 5 / high | 2 | no | Airtable, Notion, ClickUp importers |
| `r4/migration/linear-connector-and-pm-mapping` | Linear connector: teams, states, labels, projects, cycles, issues, comments, relations and attachments into the PM module with identifiers preserved and the reusable StateMapping and PeopleMatching steps | PAP-204 | M (3) | Sonnet 5 / high | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/clickup-connector-and-markup-mapping` | ClickUp connector: spaces, folders, lists, tasks, subtasks, custom fields, statuses, comments and attachments into the PM module with ClickUp markup to Markdown | PAP-204 | M (3) | Sonnet 5 / medium | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/packs-wave-2-law-real-estate-property-construction-ecommerce` | Author business packs wave 2: law firm, real estate brokerage, property management, construction and ecommerce, with page specs, views, pipelines, charts of accounts, sample data and starter docs | PAP-207 | M (3) | Sonnet 5 / medium | 4 | yes | Business migrations |
| `r4/migration/packs-wave-3-nonprofit-school-church-gym-salon` | Author business packs wave 3: nonprofit, school, church, gym and salon, with donors and pledges, enrolment, membership billing, class schedules and appointment booking structures | PAP-207 | M (3) | Sonnet 5 / medium | 4 | yes | Business migrations |
| `r4/migration/scheduled-resync-and-sync-status` | Scheduled re-sync and sync status: per-source Routines calling runIncremental, sync status page with last run, drift and errors, pause and resume, and connector health alerts | - | S (2) | Sonnet 5 / medium | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/import-duplicate-detection-and-merge-preview` | Import duplicate detection and merge preview: fuzzy matching of incoming rows against existing records, per-collection dedupe strategies and a review step before commit | - | M (3) | Sonnet 5 / high | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/ai-mapping-assistant` | AI mapping assistant: Claude-suggested field mappings, types and transforms in the wizard from sampled values and target schema, with confidence, explanations and a spend cap | - | M (3) | Sonnet 5 / high | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/drive-dropbox-files-import` | Files import from Google Drive, Dropbox and OneDrive: folder picker, folder-to-docs and attachments mapping, hash dedupe, resumable transfer within storage quotas | - | M (3) | Sonnet 5 / medium | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/contacts-import-google-outlook-vcard` | Contacts import from Google Contacts, Outlook People and vCard files into the CRM with dedupe and consent-neutral defaults | - | S (2) | Sonnet 5 / medium | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/asana-trello-jira-connectors` | Asana, Trello and Jira import into the PM module: API connectors for Asana and Jira Cloud, Trello JSON export reader, reusing StateMapping, PeopleMatching and IdentifierStrategy | - | M (3) | Sonnet 5 / medium | 4 | yes | Business migrations |
| `r4/migration/salesforce-and-pipedrive-crm-import` | Salesforce and Pipedrive CRM import: Pipedrive API connector, Salesforce Data Loader CSV recipe with preset mappings, pipelines, stages, activities and associations into the CRM | - | M (3) | Sonnet 5 / medium | 4 | yes | Business migrations |
| `r4/migration/shopify-woocommerce-square-import` | Commerce import from Shopify, WooCommerce and Square: products and variants to items, customers to CRM, orders and refunds to documents and balanced ledger postings, inventory levels | - | M (3) | Opus 5 / high | 4 | yes | Business migrations |
| `r4/migration/accounting-csv-recipes-freshbooks-wave-zoho` | Accounting CSV recipes for FreshBooks, Wave and Zoho Books: guided exports, preset mappings for chart of accounts, customers, invoices and journals, and a shared opening-balance path | - | S (2) | Haiku 4.5 / low | 4 | yes | Business migrations |
| `r4/migration/template-pack-from-tenant` | Template pack from a tenant: export a tenant's structure (tables, views, pipelines, chart, segments, sequences, pages, navigation) as a lint-clean pack with optional anonymised sample data | - | S (2) | Sonnet 5 / medium | 4 | yes | Business migrations |
| `r4/migration/migration-verification-dashboard-and-cutover` | Migration verification dashboard and cutover checklist: source versus target counts and hashes per collection over time, parallel-run status, freeze notice and go-live sign-off | - | S (2) | Sonnet 5 / medium | 4 | yes | Business migrations |
| `r4/migration/placeholder-users-and-invite-conversion` | Placeholder users from imports and invite conversion: people matched by email become placeholders, an owner invites them in bulk, and history re-points on acceptance | - | S (2) | Sonnet 5 / medium | 4 | yes | Airtable, Notion, ClickUp importers |
| `r4/migration/airtable-automations-conversion` | Airtable automations conversion: read automation definitions from a base, map triggers and actions to PaperOS automations where supported, and report the rest as a manual checklist | - | S (2) | Sonnet 5 / medium | 4 | yes | Airtable, Notion, ClickUp importers |

## Amendments to existing specs

* **PAP-198** (Scope): Round 4: work package 2 (test accounts and fixture workspaces) is superseded by `r4/migration/importer-test-accounts-and-fixture-workspaces` once created; this issue then closes when work package 1 (nine sheets, matrix, fixtures, `index.json`) is In Review, and the NJ-13 comment is posted by whichever claimer starts first. Until the new issue exists the inline text stands.
* **PAP-422** (Spec): Round 4: `ledger.importJournal` does not exist in PAP-179 or its children. Restore ledger history through `ledger.postEvent` with `source_type: 'import'`, `source_id: '<run_id>:<entry_number>'` (idempotent per the contracts document) and a `JournalDraft` per archived entry; reversal on rollback uses `ledger.reverseRun` from PAP-425. A batch `importJournal(entries[])` convenience is requested from business-core as a Spec issue (see cross-project suggestions) and adopted when it lands.
* **PAP-208** (Spec): Round 4 security correction: tenant owners are not Linear users, and the Security Model treats only Justin's Linear comments as T1. Remove the 'owner's Linear comment `approve <run_id>`' path for tenants; approval tokens are minted only by the in-app button under an owner principal (or `import.approve` permission). The Linear comment path remains solely for the PaperOS demo tenant when the comment `user.id` is Justin's.
* **PAP-200** (Edge cases): Round 4: the `xlsx` (SheetJS) npm package is stale (0.18.5, known advisories); use the vendor's own registry build (0.20+) pinned by URL under the PAP-211 license check, or drop `.xls` and show a 'save as .xlsx' hint. Decide in the PR and record it in the spreadsheet docs.
* **PAP-420** (Spec): Round 4: `identity/users.jsonl` and every CRM and support file must honour PAP-355 `pii()` classification: exports are complete for the tenant's own data (GDPR portability) but the writer records which columns are PII in `manifest.json` so PAP-421's encryption prompt is mandatory when any are present, and `scope.redactPii: true` produces a pseudonymised archive for vendors and demos.
* **PAP-423** (Spec): Round 4: 'the finance rates table' is `fin_fx_rate` from `r4/business-core/fx-rates-and-conversion`; call `fx.rateAt(invoice.created, currency, functional)` for base equivalents and mark lines `stale: true` when the rate is more than three business days old. Never store a rate computed from Stripe amounts as a platform rate.
* **PAP-347** (Spec): Round 4: the `parseCurrency` transform must output `Money` (`{ amountMinor: string, currency }` on the wire, bigint at runtime) using the PAP-175 ISO exponent table; it never emits floats, and locale detection (`1.234,56` versus `1,234.56`) is an explicit transform argument with a dry-run warning when ambiguous.
* **PAP-349** (Spec): Round 4: register the permission set `import.read|run|rollback|approve|manage` with PAP-59 in this child (`import.rollback` is referenced but never defined); `run` defaults to admin and owner, `approve` to owner (consumed by PAP-208 token minting), and every wizard route declares its permission in its page spec so PAP-64 generates the matrix. Every import write carries `X-PaperOS-Reason: import:<run_id>`.

## Cross-project suggestions

* **business-core**: `ledger.importJournal(entries[], { runId })` batch posting and `ledger.reverseRun(runId)` in `@paperos/contract-business-core` — PAP-422 and PAP-425 call them; PAP-179's children expose only `postEvent`, `post` and `reverse`. A batch API with run-scoped reversal keeps import rollback inside the immutability rules and belongs to the ledger owner.
* **identity**: Generic OAuth provider registration API for non-login connections — `r4/migration/source-oauth-connections-and-token-refresh` needs to build authorization URLs and exchange codes for Airtable, Notion, QuickBooks, Xero, Dropbox and Shopify without registering them as Better Auth login providers; PAP-57 should expose the plumbing (state signing, PKCE helpers, callback mounting) as a port.
* **app-shell**: Onboarding wizard step 'Bring your data' linking the migration agent and template gallery — PAP-367 chooses a template and skips straight to invites; a step that offers `_app/settings/migrate` (PAP-208) and the CSV importer (PAP-200) is where most real tenants start.
* **tables**: Persist `unsupported` view kinds and formula snapshots with an upgrade hook — PAP-416, PAP-426 and the wave-2 packs save Gantt and unsupported views as `unsupported`; PAP-161 should define that state and an `onKindSupported` hook so imported views light up when PAP-168 lands.
* **pm-linear**: Accept `placeholder` principals in `pm_issue.assignee` and `pm_comment.author` — `r4/migration/placeholder-users-and-invite-conversion` needs PAP-100's tables to reference a `principal_ref` (`user|placeholder`) without breaking PAP-101 sync.
* **collab**: Public or unauthenticated docs import path guard for imported Notion and Drive docs — PAP-128 receives thousands of imported MDX files from PAP-419 and `r4/migration/drive-dropbox-files-import`; a bulk import path with a size budget and a `source` frontmatter contract avoids one PR per document when the repo is the store.

## What was missing and why it matters

1. Seven connector specs cite a `connectorConformance()` suite nobody writes and five describe their own OAuth flow and 'encrypted' token storage; a harness plus a shared connections layer are the middle tooling that makes connectors swappable and reviewable once.
2. The test accounts every live integration test assumes sat inside a Ready-for-Claude research issue; they are now a claimable Infra issue with the NJ-13 list and a no-credentials default.
3. Incremental import existed only as a CLI: no schedule, no status page, no drift, no cutover checklist and no placeholder-user model, so a migration could be started but never finished.
4. Source coverage stopped at seven tools; Asana, Trello, Jira, Salesforce, Pipedrive, Shopify, WooCommerce, Square, cloud drives, contacts and three accounting tools cover the businesses the brief names, mostly by reusing the PM, CRM and finance mapping already specified.
5. Templates covered five verticals; two more waves, a capture-from-tenant round trip and three security corrections (Linear-comment approvals, PII in exports, a nonexistent ledger API) move 'one size fits all' from a slogan to a plan.
