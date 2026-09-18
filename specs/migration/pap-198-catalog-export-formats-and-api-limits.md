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
blocks: ["PAP-199", "PAP-347", "PAP-413", "PAP-492", "PAP-813"]
key: "migration/format-research"
url: "https://linear.app/paperos/issue/PAP-198/catalog-export-formats-and-api-limits-of-airtable-notion-clickup"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:45.597Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-28"
cycle: {"number": 1, "name": "C1 Foundation & core systems", "startsAt": "2026-09-18", "endsAt": "2026-09-25"}
---

# PAP-198: Catalog export formats and API limits of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Research M

**Goal**

Before any importer is written, know exactly what each source lets us pull, in what shape and how fast. Produce one verified reference sheet per source (Airtable, Notion, ClickUp, Monday, HubSpot, QuickBooks, Xero, Linear, Google Sheets), a field-type matrix and anonymised fixtures, so PAP-199 designs `SourceConnector` against real constraints and every importer starts from recorded data.

**Scope**

In:

* `docs/migration/sources/<source>.md` on a fixed template: auth (OAuth scopes or PAT), SDK (`@notionhq/client` 4.x, `@linear/sdk`, `intuit-oauth`, `xero-node`, REST for Airtable and ClickUp, GraphQL for Monday, HubSpot v3), pagination, rate limits with source URL and `checkedOn`, page sizes, incremental support, attachment URL expiry, export UI formats, webhooks, sandbox availability, quirks, terms-of-service notes, and a closing "connector implications" section (auth flow, sync strategy, attachment strategy, three hardest edge cases).
* `docs/migration/field-type-matrix.md`: every source type mapped to a PAP-164 type with a lossy flag.
* Fixtures in `packages/import/fixtures/<source>/` (anonymised, under 1 MB, covering relations, multi-select, attachments, formulas, nesting, archived items) plus recorded API responses for offline tests.
* Throughput table: 10k rows, 100k rows, 1k attachments per source at documented limits.
* Work package 2 (below): the test accounts and fixture workspaces those sheets and fixtures seed, formerly the pending issue `migration/test-accounts`.

Out: connectors, mapping UI, sources beyond the list, production customer accounts, live-mode keys.

*Round 4 amendment (2026-09-18):*
Round 4: work package 2 (test accounts and fixture workspaces) is superseded by PAP-813 once created; this issue then closes when work package 1 (nine sheets, matrix, fixtures, `index.json`) is In Review, and the NJ-13 comment is posted by whichever claimer starts first. Until the new issue exists the inline text stands.

**Spec**

* Time-box 1 agent-day, 45 minutes per source; unknowns recorded as `unverified` with a link.
* Frontmatter per sheet: `source`, `checkedOn`, `sdk`, `rateLimit`, `incremental`, `attachmentExpiry`; a Vitest lint asserts presence.
* Fixtures are the seed content for work package 2 (test accounts), so counts match its numbers: Airtable 8 tables and 40 attachments, Notion 3 databases and 25 pages, ClickUp 3 lists and 150 tasks, Stripe 120 invoices.

**Work package 2: importer test accounts and fixture workspaces (was the pending issue** `migration/test-accounts`**, folded in on 2026-09-17, round-2 FIX-5)**

Create the external state every migration integration test assumes and no other issue provisions: a PaperOS demo Airtable base, a Notion test workspace, a ClickUp workspace, a Stripe test-mode account, a QuickBooks Online sandbox company, access to the Xero demo company and a Google Cloud OAuth app for Sheets and Drive, each seeded with the fixture content work package 1 produces, with credentials stored where CI and agents can reach them. Build it on branch `PAP-198/wp2-test-accounts` after work package 1 (the nine sheets, matrix and fixtures) is In Review, and report it in a comment on this issue.

* Seed scripts `packages/import/fixtures/seed/<source>.ts` populate each workspace from the anonymised fixtures (Airtable: 8 tables, relations, lookups, rollups, 3 formulas, 40 attachments, 6 views; Notion: 3 databases, 25 pages 4 deep, 30 images, inline database, synced block; ClickUp: 3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments; Stripe: 50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds; QuickBooks: sandbox chart plus 30 journals). Seeding is idempotent: rerunning updates rather than duplicates (each API's upsert or a stable external key). Every workspace name starts with `PaperOS Test`, contains only fictional data and carries a banner doc saying so.
* Secrets: names registered in the PAP-17 env schema (`AIRTABLE_TEST_PAT`, `NOTION_TEST_TOKEN`, `CLICKUP_TEST_TOKEN`, `STRIPE_TEST_KEY`, `QBO_TEST_CLIENT_ID|SECRET|REALM`, `XERO_TEST_CLIENT_ID|SECRET`, `GOOGLE_TEST_CLIENT_ID|SECRET`), values in the Forgejo and GitHub secret stores following PAP-48 conventions and in the Scout bot's vault; tokens belong to the Scout bot user where possible so rotation is one place. No value in the repo (the PAP-80 secret scan passes).
* `docs/migration/test-accounts.md`: what exists, who owns the login, how to reseed, token rotation dates. Xero has no persistent sandbox: use the demo company and pin recorded fixtures because it resets monthly. The Google OAuth app stays in testing mode with test users listed; the consent screen is not submitted for verification in this build.
* Weekly `import-fixtures-health.yml` workflow runs each connector's `discover` against the real account and posts drift (counts changed, token expired, "no access") as a comment on this issue; `pnpm fixtures seed <source>` and `pnpm fixtures health` are the commands.
* Interface: the integration tests of PAP-200, PAP-202, PAP-203, PAP-204 and PAP-206 read only the env names above and skip with `skipped: no-credentials` when they are unset; their recorded-fixture tests must pass regardless, so those issues are not blocked by this work package.
* Edge cases: Airtable free tier lacks attachment API access (Team trial, cost noted in the ask below); Notion integration not granted to a page (health lists it as "no access"); Stripe fixtures avoid test clocks so counts stay stable; QuickBooks sandbox resets after inactivity (reseed step documented); Google testing-mode refresh tokens expire after 7 days (health warns 2 days before); a provider consent-screen change fails the workflow loudly, never silently green.
* Done when: all seven accounts exist and `pnpm fixtures health` reports green counts for each; seed scripts committed and rerunnable with the counts above; secrets present in both forges' stores; docs page merged; CHANGELOG entry; Linear comment listing counts per source. Tests: Vitest for the seed scripts against recorded API responses (idempotence on the second run); health workflow dry run on recorded responses, then one live run once credentials land; manual check of each workspace banner.

**Needs Justin — NJ-13: importer test-account sign-ups (only a human can do these)**

The builder who claims this issue posts the list below as a comment on the day it is claimed, with the defaults, and moves this issue to Needs Justin only when work package 1 is In Review and work package 2 waits on nothing but the sign-ups. Justin replies `/approve` (defaults) or edits the list; the builder then finishes work package 2. Waiting on sign-ups is the long part, so file it on day one.

1. Airtable: create a workspace `PaperOS Test`, start a Team trial (attachment API needs it; if it lapses, document the plan cost or accept UI-export fixtures) and issue a personal access token with `data.records:read|write`, `schema.bases:read|write` scoped to that workspace.
2. Notion: create workspace `PaperOS Test`, an internal integration, and share the root test page with it.
3. ClickUp: free workspace `PaperOS Test`; personal API token from Settings > Apps.
4. Stripe: enable test mode on the existing account (already NJ-10 for PAP-177); a restricted key with read and write on customers, products, subscriptions, invoices and refunds.
5. QuickBooks Online: developer account, one sandbox company; app keys (client id, secret) and the sandbox realm id.
6. Xero: developer account; the demo company is enough, no paid org.
7. Google Cloud: project `paperos-test`, OAuth client (web) in testing mode with the Scout bot address as a test user, Sheets and Drive APIs enabled (also NJ-10 for PAP-224 and PAP-200).

Default if no reply by 2026-09-24: proceed with Stripe, Google and ClickUp (already needed elsewhere or free), record the others as `skipped: no-credentials` and keep the recorded-fixture path as the only test for Airtable, Notion, QuickBooks and Xero.

**Interface contract**

Provides: the nine sheets, `field-type-matrix.md`, fixtures folder layout `fixtures/<source>/{export,api}/`, `fixtures/README.md`, and a machine-readable `docs/migration/sources/index.json` (`{ source, rateLimit, incremental, attachmentExpiry }`) that PAP-199 reads for `capabilities.rateLimit` defaults and PAP-208 reads for time estimates. Consumes: nothing in-repo; PAP-128 renders the pages when it lands. Consumers: PAP-199, PAP-200, PAP-202, PAP-203, PAP-204, PAP-206, PAP-208, `PAP-413`, and PAP-188 for the HubSpot CRM mapping section.

**Definition of done**

* Nine sheets, matrix and `index.json` merged; sources index page renders in the docs engine (or as plain Markdown if PAP-128 is late).
* Fixtures for Airtable, Notion, ClickUp, Linear, QuickBooks, Stripe and CSV committed with the anonymisation README.
* Every limit and expiry claim carries a URL and `checkedOn`; lint green.
* Screenshots of each source's export UI at 1280 attached.
* CHANGELOG entry; Linear comment linking the index and notifying PAP-199, PAP-202, PAP-203, PAP-204, PAP-206.
* Work package 2 done as listed above, or its NJ-13 comment posted and the default (recorded fixtures only) applied after 2026-09-24.

**Test plan**

* Vitest: frontmatter lint over all sheets; `index.json` validates against a Zod schema; every fixture folder has a README and files under 1 MB.
* Fixture smoke: each recorded API fixture parses with the SDK types it claims.
* Review: Scout and Atlas sign the throughput table in the PR; disagreements resolved there.

**Demo**

Reviewer opens `docs/migration/sources/airtable.md`, checks the rate-limit line has a URL and date, opens `field-type-matrix.md` to find `rollup`, then lists `fixtures/airtable/` and sees eight table exports. Under two minutes.

**Edge cases**

* API access needs a paid plan (Airtable attachments, some ClickUp endpoints): note plan and UI-export fallback.
* Limits differ per plan or per token versus workspace: record both and the safe default.
* Soft-deleted items visible via API (Notion `archived`, Linear `trashed`): document whether to import as archived.
* Monday and HubSpot: sheets written; importer path is CSV recipes, not a connector.
* Trial workspace lacks paid features (formulas): fixture marked partial.

**Dependencies**

None; ready now. Blocks PAP-199 (interface design). Work package 2 gates only the live integration tests of PAP-200, PAP-202, PAP-203, PAP-204 and PAP-206, which skip with `skipped: no-credentials` until it lands; soft for work package 2: PAP-17 (env schema), PAP-48 (secret conventions), PAP-80 (secret scan). Informs every importer.

**Agent**

Researched by Scout (Import Mapper); work package 2 built by Scout with Forge (Ops Runner) for the secret stores, sign-ups by Justin (NJ-13). Reviewed by Atlas for completeness, Quill for the docs template and Sentinel (Security Auditor) for work package 2.

**Size**

M: nine sources at 45 minutes plus fixtures and the matrix (work package 1); work package 2 is S of scripting, the waiting on sign-ups is the long part.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/importer-test-accounts-and-fixture-workspaces` = PAP-813.
