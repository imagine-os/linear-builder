---
identifier: "PAP-390"
title: "Automation builder page, test run, run log with replay, five starter templates and import hooks"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: "PAP-174"
children: []
blockedBy: ["PAP-166", "PAP-389"]
blocks: []
key: "tables/automations/builder-log-templates"
url: "https://linear.app/paperos/issue/PAP-390/automation-builder-page-test-run-run-log-with-replay-five-starter"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:44.007Z"
---

# PAP-390: Automation builder page, test run, run log with replay, five starter templates and import hooks

**Goal**

Let staff build, test and debug automations without code, and give templates and importers a way to ship automations.

**Scope**

In: `specs/pages/tables/automations.page.spec.yaml`, builder page (trigger picker, `FilterBuilder` conditions, action list with drag reorder, test run), run log grid with replay, templates JSON for PAP-208, mapping hooks for PAP-202 and PAP-204.

**Spec**

* Builder keyboard-operable per PAP-158; test run executes against a sample record without side effects (dry-run flag on actions).
* Run log as a grid view with step expansion and replay; retention 90 days.
* Templates: appointment reminder, deal stage notification, overdue invoice nudge, new lead assignment, weekly digest.

**Interface contract**

Provides: builder route, `automationTemplates`, `mapImportedAutomation(source)` hook, run log dataset. Consumes: both siblings, `FilterBuilder` (PAP-166), drag (PAP-155), grid (PAP-165), page spec tooling (PAP-120).

**Definition of done**

* Playwright build, test run, real run, replay; screenshots at 375 and 1280 in three themes; parity matrix in docs; templates validate.

**Test plan**

* Unit: template JSON validates; import mapping fixtures.
* E2E: full flow from the parent's umbrella test; keyboard-only build.

**Demo**

Build "when Status becomes Done, notify owner", test it, edit a record, open the run.

**Edge cases**

* Template installed twice is idempotent; replay of a run with a deleted record fails clearly.

**Dependencies**

Both siblings (hard), PAP-166, PAP-165, PAP-155, PAP-120.

**Agent**

Builder: Nova with Iris on the builder. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
