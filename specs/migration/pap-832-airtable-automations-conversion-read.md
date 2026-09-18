---
identifier: "PAP-832"
title: "Airtable automations conversion: read automation definitions from a base, map triggers and actions to PaperOS automations where supported, and report the rest as a manual checklist"
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
blockedBy: ["PAP-390", "PAP-416"]
blocks: []
key: "r4/migration/airtable-automations-conversion"
url: "https://linear.app/paperos/issue/PAP-832/airtable-automations-conversion-read-automation-definitions-from-a"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:05.698Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-832: Airtable automations conversion: read automation definitions from a base, map triggers and actions to PaperOS automations where supported, and report the rest as a manual checklist

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-202 leaves automations out. An Airtable base is often half automations ('when status becomes Done, send an email'); recreating the common ones on PAP-174 and listing the rest as a checklist is the difference between a migrated base and a migrated workflow.

**Scope**

In: reader for Airtable automation definitions (Meta API where exposed for the plan, else guided export of the automation list as JSON from the UI with a recipe) producing `SourceAutomation { trigger, conditions, actions[] }`; mapper to PAP-174 `automation` rows: triggers `record matches conditions`, `record enters view` (via PAP-416's filter parser), `form submitted`, `scheduled`; actions `update record`, `create record`, `send email` (through PAP-370, sandbox), `send Slack` (PAP-325), `run script` becomes a manual checklist item with the script attached; conversion report section in `RunReport`; automations imported disabled by default with an enable review step.

Out: Airtable scripting translation, Interfaces, Zapier or Make flows.

**Spec**

* Every converted automation carries `source: airtable:<automationId>` for PAP-201 mapping so re-import updates rather than duplicates.
* Field and view references resolve through the PAP-415 and PAP-416 mappings; unresolved references fail the automation into the checklist, never a broken rule.
* Email actions render Airtable's template syntax into the PAP-389 template expressions where the variables map; otherwise the body is kept with a warning.

**Interface contract**

Provides: automation reader, `mapAirtableAutomation()`, report section, enable-review step, recipe for manual export. Consumes: view and filter mapping (PAP-416), automation builder and templates (PAP-390, PAP-389, PAP-388), email (PAP-370), Slack (PAP-325, soft), mappings (PAP-201).

**Definition of done**

* Fixture of 12 automations: 8 convert and pass PAP-390's test run, 4 land in the checklist with reasons; rerun updates not duplicates; screenshots at 375, 1024 light and dark of the report and review step; `docs/migration/airtable.md` automations section; CHANGELOG.

**Test plan**

* Unit: trigger and action mapping table, template variable rewriting, unresolved reference handling.
* E2E: import the demo base with automations, review the 8 converted ones, enable one, trigger it with a record change and see the run log.

**Demo**

Reviewer imports the demo base, opens the automations report, enables 'notify on Done' and flips a record to Done to see the sandbox email in the outbound ledger. Under two minutes.

**Edge cases**

* Automation references a table that was excluded: checklist item with the table named.
* Scheduled automation in Airtable's timezone: converted with the tenant timezone and a note.

**Dependencies**

Hard: PAP-416, PAP-390. Soft: PAP-389, PAP-388, PAP-370, PAP-325, PAP-201.

**Agent**

Builder: Scout (Import Mapper) with Nova on automations. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.
