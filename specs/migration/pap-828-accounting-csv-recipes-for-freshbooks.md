---
identifier: "PAP-828"
title: "Accounting CSV recipes for FreshBooks, Wave and Zoho Books: guided exports, preset mappings for chart of accounts, customers, invoices and journals, and a shared opening-balance path"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Docs"
priority: 4
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-413", "PAP-424"]
blocks: []
key: "r4/migration/accounting-csv-recipes-freshbooks-wave-zoho"
url: "https://linear.app/paperos/issue/PAP-828/accounting-csv-recipes-for-freshbooks-wave-and-zoho-books-guided"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:05.485Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: null
cycle: null
---

# PAP-828: Accounting CSV recipes for FreshBooks, Wave and Zoho Books: guided exports, preset mappings for chart of accounts, customers, invoices and journals, and a shared opening-balance path

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Docs S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

QuickBooks and Xero get API connectors; the long tail of small-business accounting (FreshBooks, Wave, Zoho Books) does not justify one each before anyone asks. Recipes plus presets, in the PAP-413 pattern, let those users land a chart and opening balances through the CSV importer and the PAP-425 finance wizard.

**Scope**

In: `docs/migration/recipes/{freshbooks,wave,zoho-books}.md` with export clicks and screenshots at 1280; presets `presets/{freshbooks,wave,zoho-books}.json` mapping chart of accounts (`mapChartOfAccounts` from PAP-424 by type name), customers and vendors to `fin_party`, invoices to `fin_document` history, journals or trial balance to the PAP-424 `openingJournal` path; detector signatures for each export's header set; fixture CSVs per tool; reopen criteria for API connectors.

Out: API connectors, payroll history, bank feeds (bank issue in business-core).

**Spec**

* Each preset validates against the mapping Zod schema in CI and has a fixture with an expected table shape and a balanced opening journal.
* Recipes state clearly what is lossy per the PAP-198 field-type matrix (for example FreshBooks expense categories to accounts by name).
* Detector falls back to a manual 'choose your tool' picker when headers are localised.

**Interface contract**

Provides: three recipes, three presets, fixtures, detector signatures, an 'accounting CSV' section in `docs/migration/finance-imports.md`. Consumes: recipe pattern (PAP-413), chart mapping and opening journal (PAP-424), finance wizard (PAP-425), CSV importer (PAP-200).

**Definition of done**

* Each fixture imports to a chart and a balanced opening journal in the wizard (integration test); recipes rendered with screenshots; detector offers the preset; CHANGELOG; sources index updated.

**Test plan**

* Unit: detector on 9 header sets, preset schema validation, account type name mapping.
* E2E: upload the Wave trial balance fixture, accept the preset, walk the finance wizard to a green trial balance.

**Demo**

Reviewer uploads the FreshBooks chart export, accepts the preset and sees the mapped chart with kinds and a balanced opening journal. Under one minute.

**Edge cases**

* Export lacks account codes: generated in a reserved range and flagged (PAP-424 rule).
* Currency column absent: functional currency assumed with a warning.

**Dependencies**

Hard: PAP-413, PAP-424. Soft: PAP-425, PAP-200.

**Agent**

Builder: Scout (Import Mapper) with Ledger reviewing mappings. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
