# Gap issues for migration (from gaps.json plus the audit's Monday/HubSpot coverage note).
GAPS = [
{
 "key": "migration/test-accounts", "project": "migration", "milestone": "Import framework and CSV",
 "phase": "P1", "type": "Infra", "surfaces": ["Developer", "Agent"], "priority": 2, "size": "S", "state": "Backlog",
 "blockedBy": ["PAP-198"], "blocks": ["PAP-200", "PAP-202", "PAP-203", "PAP-204", "PAP-206"],
 "title": "Provision importer test accounts and fixture workspaces: Airtable demo base, Notion test workspace, ClickUp workspace, Stripe test account, QuickBooks sandbox, Xero demo, Google OAuth app; one Needs Justin item",
 "description": """**Goal**

Create the external state every migration integration test assumes and no issue provisions: a PaperOS demo Airtable base, a Notion test workspace, a ClickUp workspace, a Stripe test-mode account, a QuickBooks Online sandbox company, access to the Xero demo company and a Google Cloud OAuth app for Sheets and Drive, each seeded with the fixture content the importer DoDs name, with credentials stored where CI and agents can reach them. One Needs Justin item collects the sign-ups only a human can do.

**Scope**

In:

* Seed scripts `packages/import/fixtures/seed/<source>.ts` that populate each workspace from the anonymised fixtures in PAP-198 (Airtable: 8 tables, relations, lookups, rollups, 3 formulas, 40 attachments, 6 views; Notion: 3 databases, 25 pages 4 deep, 30 images, inline database, synced block; ClickUp: 3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments; Stripe: 50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds; QuickBooks: sandbox chart plus 30 journals).
* Secrets: names in `app-shell/env-config` (`AIRTABLE_TEST_PAT`, `NOTION_TEST_TOKEN`, `CLICKUP_TEST_TOKEN`, `STRIPE_TEST_KEY`, `QBO_TEST_CLIENT_ID|SECRET|REALM`, `XERO_TEST_CLIENT_ID|SECRET`, `GOOGLE_TEST_CLIENT_ID|SECRET`), values in the Forgejo and GitHub secret stores via `forge/bot-accounts` conventions and in the Scout bot's vault.
* `docs/migration/test-accounts.md`: what exists, who owns the login, how to reseed, token rotation dates.
* A weekly `import-fixtures-health.yml` workflow that runs each connector's `discover` against the real account and posts drift (counts changed, token expired) to a pinned Linear issue.
* The Needs Justin item listing every sign-up, consent screen and payment method step with defaults.

Out: production customer accounts, live-mode keys, any importer code.

**Spec**

* Every workspace name starts with `PaperOS Test` and contains only fictional data; a banner doc in each says so.
* Seeding is idempotent: rerunning updates rather than duplicates (uses each API's upsert or a stable external key).
* Xero has no persistent sandbox: use the demo company and pin recorded fixtures because it resets monthly.
* Google OAuth app stays in testing mode with test users listed; the consent screen is not submitted for verification in this build.
* Tokens are personal to the Scout bot user where possible so rotation is one place.

**Interface contract**

Provides: env var names above, `pnpm fixtures seed <source>` and `pnpm fixtures health`, `docs/migration/test-accounts.md`, the health workflow and pinned issue. Consumes: PAP-198 fixtures, PAP-17 env schema, PAP-48 secret conventions. Integration tests in PAP-200, PAP-202, PAP-203, PAP-204 and PAP-206 read only these names and skip with `skipped: no-credentials` when unset.

**Definition of done**

* All seven accounts exist and `pnpm fixtures health` reports green counts for each.
* Seed scripts committed and rerunnable; fixture counts match the numbers above.
* Secrets present in both forges' stores; no value in the repo (secret scan from PAP-80 passes).
* Needs Justin item created with every human step and closed by Justin.
* Docs page merged; CHANGELOG entry; Linear comment listing counts per source.

**Test plan**

* Vitest: seed scripts against recorded API responses (idempotence on second run).
* CI: health workflow dry run using recorded responses; a live run once credentials land.
* Manual: open each workspace and confirm the "test data" banner and counts.

**Demo**

Reviewer runs `pnpm fixtures health` and sees seven green rows with record counts and token expiry dates, then opens the Airtable demo base link in the docs page. Under one minute.

**Edge cases**

* Airtable free tier lacks attachment API access: use a Team trial or document the plan cost in the Justin item.
* Notion integration not granted to a page: health check lists it as "no access".
* Stripe test clock data: fixtures avoid test clocks so counts stay stable.
* QuickBooks sandbox resets after inactivity: reseed step documented.
* Google app in testing mode expires refresh tokens after 7 days: health check warns 2 days before.
* Provider adds a consent screen change: workflow fails loudly, not silently green.

**Dependencies**

PAP-198 (fixtures to seed from). Soft: PAP-17, PAP-48, PAP-80. Blocks integration DoDs of PAP-200, PAP-202, PAP-203, PAP-204, PAP-206.

**Agent**

Built by Scout (Import Mapper) with Forge (Ops Runner) for secret stores; Justin completes sign-ups. Reviewed by Sentinel (Security Auditor).

**Size**

S: scripts are small; waiting on sign-ups is the long part, so file the Justin item on day one.
"""
},
{
 "key": "migration/monday-hubspot-recipes", "project": "migration", "milestone": "Airtable, Notion, ClickUp importers",
 "phase": "P2", "type": "Build", "surfaces": ["Staff"], "priority": 4, "size": "S", "state": "Backlog",
 "blockedBy": ["PAP-198", "PAP-200"], "blocks": [],
 "title": "Import Monday and HubSpot through guided CSV export recipes with preset mappings (no API connector in this build)",
 "description": """**Goal**

Close the coverage gap the audit found: Monday and HubSpot have reference sheets in PAP-198 but no importer. Instead of two more API connectors before 2026-10-01, ship guided export recipes and preset mappings so a user can move a Monday board or a HubSpot CRM export into PaperOS through the CSV importer with correct types, pipelines and relations, and record API connectors as a reopen criterion.

**Scope**

In:

* Recipes `docs/migration/recipes/{monday,hubspot}.md` rendered in-app: exact export clicks with screenshots at 1280, which files to download (Monday board Excel export; HubSpot contacts, companies, deals CSV exports with associations), and known pitfalls.
* Preset mappings `packages/import/presets/{monday,hubspot}.json` in the PAP-199 mapping JSON format: Monday columns (status, people, date, timeline, numbers, link, dropdown, subitems as relations) and HubSpot properties (lifecycle stage, deal stage to `growth/crm-model` pipeline stage, associations to relations by record id).
* Wizard hook: when the CSV importer detects Monday or HubSpot headers (signature columns such as `Record ID`, `Associated Company IDs`, Monday `Subitems`), it offers the preset with a link to the recipe.
* Reopen criteria in the recipe: build API connectors when three tenants ask or when PAP-198 throughput shows CSV is insufficient over 50k rows.

Out: API connectors, OAuth, incremental sync for these sources.

**Spec**

* Presets validated by the mapping Zod schema in CI; each has a fixture CSV and expected table shape.
* HubSpot associations resolve through the CSV `Associated ... IDs` columns using the PAP-201 relation pass with `system: hubspot-csv`.
* Monday timeline columns split into start and end date fields; people columns matched by email.

**Interface contract**

Provides: presets, recipes, header signature detector `detectSourcePreset(headers): 'monday'|'hubspot'|null`, fixture CSVs. Consumes: PAP-200 CSV connector and wizard, PAP-199 mapping format, PAP-201 relation pass, PAP-187 pipeline stages, PAP-198 sheets. PAP-208 uses the recipes when a tenant names either tool.

**Definition of done**

* Both presets import their fixture CSVs into correct tables with relations and pipeline stages (integration test).
* Recipes rendered with screenshots; detector offers the preset in the wizard.
* `docs/migration/recipes/` linked from the sources index; CHANGELOG entry; Linear comment.

**Test plan**

* Vitest: detector on 10 header sets (true positives, near misses), preset schema validation, Monday timeline split, HubSpot association resolution.
* Playwright: upload the HubSpot deals fixture, accept the preset, dry run, commit, open the pipeline kanban; screenshots at 375 and 1280 in light and dark.
* Docs lint: every recipe step has a screenshot.

**Demo**

Reviewer uploads `fixtures/hubspot/deals.csv`, sees "Looks like a HubSpot export, apply preset?", accepts, commits and opens the deals pipeline with stages populated. Under two minutes.

**Edge cases**

* Export in a non-English HubSpot portal: header names differ; detector falls back to `Record ID` only and warns.
* Monday subitems exported as a separate sheet: recipe explains ordering; preset maps the sheet as a relation table.
* Duplicate contacts across HubSpot files: dedupe on email by default.
* HubSpot deal stage not in the tenant pipeline: created as a new stage with a report line.
* Very large exports (over 200k rows): wizard recommends the 10k sample dry run.

**Dependencies**

PAP-198 and PAP-200 (hard). Soft: PAP-201, PAP-187.

**Agent**

Built by Scout (Import Mapper) with Beacon for HubSpot CRM mapping. Reviewed by Sentinel (Edge Case Hunter) and Quill for the recipes.

**Size**

S: two presets, two recipes, one detector.
"""
},
]


# FIX-5 (2026-09-17): folded into live issues as work packages; never create. See round2/folded-into-live-issues.json.
import json as _json, os as _os
_FOLDED = {f["key"] for f in _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "folded-into-live-issues.json")))["folded"]}
GAPS = [g for g in GAPS if g["key"] not in _FOLDED]
