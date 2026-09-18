---
identifier: "PAP-413"
title: "Import Monday and HubSpot through guided CSV export recipes with preset mappings (no API connector in this build)"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-198", "PAP-200"]
blocks: ["PAP-826", "PAP-828"]
key: "migration/monday-hubspot-recipes"
url: "https://linear.app/paperos/issue/PAP-413/import-monday-and-hubspot-through-guided-csv-export-recipes-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:55:52.712Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-413: Import Monday and HubSpot through guided CSV export recipes with preset mappings (no API connector in this build)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

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
