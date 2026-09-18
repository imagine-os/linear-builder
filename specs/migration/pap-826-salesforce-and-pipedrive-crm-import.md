---
identifier: "PAP-826"
title: "Salesforce and Pipedrive CRM import: Pipedrive API connector, Salesforce Data Loader CSV recipe with preset mappings, pipelines, stages, activities and associations into the CRM"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-201", "PAP-413", "PAP-790"]
blocks: []
key: "r4/migration/salesforce-and-pipedrive-crm-import"
url: "https://linear.app/paperos/issue/PAP-826/salesforce-and-pipedrive-crm-import-pipedrive-api-connector-salesforce"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:50.851Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-826: Salesforce and Pipedrive CRM import: Pipedrive API connector, Salesforce Data Loader CSV recipe with preset mappings, pipelines, stages, activities and associations into the CRM

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-413 covers HubSpot by recipe. Pipedrive is the SMB favourite with a clean API and Salesforce is what agencies and real-estate teams leave; one connector and one recipe, both landing in the CRM model with pipelines and activities intact, complete the CRM source set.

**Scope**

In: `connectors/pipedrive/` (API token or OAuth via the connections issue: organizations, persons, deals with pipelines and stages, activities, notes, files; custom fields to `custom jsonb`); Salesforce recipe `docs/migration/recipes/salesforce.md` (Data Loader or Reports export of Accounts, Contacts, Leads, Opportunities with stage history, Tasks and Events, with Ids and lookup Ids) plus preset `presets/salesforce.json` resolving associations through PAP-201 with `system: salesforce-csv`, detector signatures in PAP-200's `detectSourcePreset`; stage mapping to `crm_pipeline_stage` with probability import; activity kinds mapping; owner matching by email.

Out: Salesforce API connector (reopen criterion: three tenants ask), custom objects beyond a generic table import, Einstein or Pardot data.

**Spec**

* Opportunity stage history becomes `system` activities so the sales dashboard funnel works on imported data.
* Pipedrive `won_time` and `lost_reason` map to `won_at`, `lost_at`, `lost_reason`; currencies kept as given.
* Both pass the dedupe pass when present; else email and domain keys.

**Interface contract**

Provides: Pipedrive connector, Salesforce recipe and preset, detector signatures, stage and activity mapping tables in `docs/growth/crm-model.md` appendix. Consumes: recipe pattern and detector (PAP-413, PAP-200), CRM schema (growth child), mappings (PAP-201), connections issue, dedupe issue (soft), conformance harness.

**Definition of done**

* Recorded Pipedrive fixture (200 persons, 60 deals, 3 pipelines) and Salesforce fixture CSVs import with correct counts, stages and associations; rerun zero duplicates; recipe rendered with screenshots at 1280; CHANGELOG.

**Test plan**

* Unit: stage probability mapping, association resolution, activity kinds, detector signatures.
* E2E: upload the Salesforce fixture set, accept the preset, commit and open the deals pipeline with stage history on a deal.

**Demo**

Reviewer connects the mocked Pipedrive account, imports and opens the pipeline kanban with the same stages and probabilities. Under two minutes.

**Edge cases**

* Salesforce export in a non-English org: detector falls back to Id-column shapes and warns.
* Deal stage not in the tenant pipeline: created with a report line (PAP-413 rule).
* Pipedrive custom field of type `monetary`: stored as `Money` with its currency.

**Dependencies**

Hard: PAP-413, PAP-790, PAP-201. Soft: PAP-200, connections issue, dedupe issue, conformance harness.

**Agent**

Builder: Scout (Import Mapper) with Beacon on CRM mapping. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/crm-schema-routers-page-specs` = PAP-790.
