---
key: "migration/test-accounts"
title: "Provision importer test accounts and fixture workspaces: Airtable demo base, Notion test workspace, ClickUp workspace, Stripe test account, QuickBooks sandbox, Xero demo, Google OAuth app; one Needs Justin item"
project: "migration"
parent: null
phase: "P1"
type: "Infra"
priority: 2
size: "S"
surfaces: ["Developer", "Agent"]
milestone: "Import framework and CSV"
intendedState: "Backlog"
blockedBy: ["PAP-198"]
blocks: ["PAP-200", "PAP-202", "PAP-203", "PAP-204", "PAP-206"]
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
status: "folded"
into: "PAP-198"
---

# Provision importer test accounts and fixture workspaces: Airtable demo base, Notion test workspace, ClickUp workspace, Stripe test account, QuickBooks sandbox, Xero demo, Google OAuth app; one Needs Justin item

> **FOLDED.** Folded into PAP-198 as work package 2 (FIX-5). Do not create; text kept for reference.

**Goal**

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
