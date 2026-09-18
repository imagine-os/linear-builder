---
identifier: "PAP-813"
title: "Importer test accounts and fixture workspaces: idempotent seed scripts, secret names in both forges, fixtures health workflow and the NJ-13 sign-up list"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-17", "PAP-48", "PAP-198", "PAP-521"]
blocks: []
key: "r4/migration/importer-test-accounts-and-fixture-workspaces"
url: "https://linear.app/paperos/issue/PAP-813/importer-test-accounts-and-fixture-workspaces-idempotent-seed-scripts"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:08.158Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-28"
cycle: null
---

# PAP-813: Importer test accounts and fixture workspaces: idempotent seed scripts, secret names in both forges, fixtures health workflow and the NJ-13 sign-up list

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

PAP-198 is Ready for Claude as a research issue and carries work package 2 (test accounts) inline; a builder finishing the nine sheets should not also wait weeks on sign-ups. This issue takes the work package out as its own claimable item: the external state every live integration test assumes (Airtable base, Notion workspace, ClickUp workspace, Stripe test account, QuickBooks sandbox, Xero demo, Google OAuth app), seeded idempotently from the PAP-198 fixtures, with credentials where CI and agents can reach them.

**Scope**

In: `packages/import/fixtures/seed/<source>.ts` seeders (Airtable 8 tables, relations, lookups, rollups, 3 formulas, 40 attachments, 6 views; Notion 3 databases, 25 pages 4 deep, 30 images, inline database, synced block; ClickUp 3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments; Stripe 50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds; QuickBooks sandbox chart plus 30 journals), each idempotent via the API's upsert or a stable external key; env names in the PAP-17 schema (`AIRTABLE_TEST_PAT`, `NOTION_TEST_TOKEN`, `CLICKUP_TEST_TOKEN`, `STRIPE_TEST_KEY`, `QBO_TEST_CLIENT_ID|SECRET|REALM`, `XERO_TEST_CLIENT_ID|SECRET`, `GOOGLE_TEST_CLIENT_ID|SECRET`) with values in the Forgejo and GitHub secret stores per PAP-48 and the Scout bot vault; `docs/migration/test-accounts.md`; weekly `import-fixtures-health.yml` running each connector's `discover` and commenting drift on PAP-198; commands `pnpm fixtures seed <source>` and `pnpm fixtures health`; the NJ-13 comment posted on claim day.

Out: connectors themselves, production customer accounts, live-mode keys, Google consent-screen verification (stays in testing mode).

**Spec**

* Every workspace name starts with `PaperOS Test`, holds only fictional data and carries a banner doc saying so.
* Seeders run offline against recorded API responses in CI (idempotence asserted on a second run) and live only when the env name is set.
* Consumers (PAP-200, PAP-414, PAP-417, PAP-423, PAP-424, the ClickUp and Linear children) read only the env names and report `skipped: no-credentials` when unset; nothing here blocks them.
* Xero has no persistent sandbox: pin recorded fixtures because the demo company resets monthly; QuickBooks sandbox reseed documented; Google testing-mode refresh tokens expire in 7 days and the health workflow warns 2 days before.
* Default if NJ-13 is unanswered by 2026-09-24: proceed with Stripe, Google and ClickUp; record the rest as `skipped: no-credentials`.

**Interface contract**

Provides: seed scripts, env names, `docs/migration/test-accounts.md`, health workflow, `pnpm fixtures seed|health`, the NJ-13 list. Consumes: fixtures and sheets (PAP-198), env schema (PAP-17), secret conventions (PAP-48), secret scan (PAP-80), Stripe test account (NJ-10).

**Definition of done**

* Seed scripts committed with recorded-response tests; health workflow dry run green on recorded responses; one live run per account once credentials land or the default applied and documented.
* Secrets present in both forges' stores (verified by `pnpm security:accounts-check`, no value in the repo); docs page merged; CHANGELOG; Linear comment on PAP-198 listing counts per source.

**Test plan**

* Unit: seeder idempotence on recorded responses; env-name lint against the PAP-17 schema; banner presence check.
* E2E: `pnpm fixtures health` prints a table with green counts for every source that has credentials and `no-credentials` for the rest.

**Demo**

Reviewer runs `pnpm fixtures health` and reads the table, then opens `docs/migration/test-accounts.md` to find who owns each login and the reseed steps. Under one minute.

**Edge cases**

* Airtable free tier lacks attachment API access: Team trial cost noted in NJ-13; UI-export fixtures fallback.
* Notion integration not granted to a page: health lists it as 'no access'.
* Provider consent-screen change: workflow fails loudly, never silently green.

**Dependencies**

Hard: PAP-198 work package 1 (sheets and fixtures), PAP-17, PAP-48. Soft: PAP-80, NJ-10, NJ-13. Blocks nothing hard (consumers skip without credentials).

**Agent**

Builder: Scout (Import Mapper) with Forge (Ops Runner) on secret stores; sign-ups by Justin. Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
