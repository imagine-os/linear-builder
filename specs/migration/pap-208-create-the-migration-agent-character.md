---
identifier: "PAP-208"
title: "Create the migration agent character that interviews users about current tools and runs the imports"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-199", "PAP-287", "PAP-332", "PAP-334", "PAP-349"]
blocks: []
key: "migration/migration-agent"
url: "https://linear.app/paperos/issue/PAP-208/create-the-migration-agent-character-that-interviews-users-about"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:10.135Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-208: Create the migration agent character that interviews users about current tools and runs the imports

**Goal**

Make migration a conversation: a Scout sub-character, Migration Guide, interviews a new tenant about current tools, proposes a plan (importers, templates, order, time estimates from PAP-198), runs dry runs, explains reports plainly, asks only the decisions a human must make, and commits imports through the framework with an approval token, reporting progress in-app and in Linear.

**Scope**

In:

* Character `packages/agents/characters/migration-guide.yaml` (parent Scout, `kind: sub`, model `claude-fable-5-1`, effort `high`, `permissionMode: dontAsk`; tools Read, Grep, WebFetch and MCP `paperos-import` procedures `sources.connect`, `mappings.*`, `runs.dry`, `runs.commit` with approval token, `runs.rollback`; Bash and raw SQL denied; `perSessionUsd` 8) and prompt `packages/agents/prompts/migration-guide.md`.
* Skill `.claude/skills/migrate-tenant/SKILL.md`: interview script, plan template, decision points, execution loop (dry -> summarise -> ask -> commit), completion checklist with an export baseline via PAP-205.
* Chat surface `_app/settings/migrate` on PAP-142 messages with the agent as participant (PAP-146), plan and report cards as JSON blocks, approve button minting the token; exchanges logged to PAP-129.
* Capabilities and limits read at run time from PAP-198 `index.json` and the connector registry, so new importers need no prompt change.
* Handoff to Needs Justin or the owner when a decision exceeds remit (over 5M rows, regulated data, conversion dates).
* Five eval fixtures for PAP-110 with golden plans and a rubric.

Out: building importers, live sync, migrating credentials, sources the tenant has not connected.

**Spec**

* `runs.commit` requires `approvalToken` minted by the UI button or an owner's Linear comment `approve <run_id>`; single use, 30-minute expiry, permission-gated.
* Plan card `{ steps[]: { importer, source, collections, estimateMinutes, dependsOn }, templates[], risks[], questions[] }`; report card mirrors `import_run.stats` plus a 150-word summary and top five issues with suggested fixes.
* The agent sees at most 20 dry-run examples per field.
* Session cap 90 minutes or budget; resumable plan saved via PAP-109.
* Conversation follows tenant locale; JSON stays English.

**Interface contract**

Provides: character and prompt, skill, MCP server `paperos-import` exposing the procedures above with Zod schemas, `PlanCard` and `ReportCard` schemas, approval token API `import.approvals.mint|consume`, route `_app/settings/migrate`, eval fixtures. Consumes: PAP-199 `runDry|runImport|rollbackRun` and `RunReport`, PAP-104 roster, PAP-105 skill format, PAP-108 handoff protocol, PAP-109 memory, PAP-110 harness, PAP-129 log, PAP-142 and PAP-146 (fallback: plain message list), PAP-205 export, PAP-198 `index.json`, PAP-207 pack metadata, `PAP-413` recipes.

**Definition of done**

* Character validates and appears in the org chart; smoke transcript shows an in-role interview and a refusal to commit without a token.
* Staging end to end: scripted tenant interviewed, plan produced, CSV and Airtable dry runs, approval by button, commit, export baseline taken; recording attached.
* Five eval fixtures score at or above 0.8; any unapproved commit is a hard fail.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark of the chat with plan card and approve button; axe clean.
* `docs/agents/migration-guide.md`; CHANGELOG; Linear comment with recording and scores; Justin approves the character in one Needs Justin item.

**Test plan**

* Vitest: token lifecycle (single use, expiry, permission), plan and report schemas, remit checks triggering handoff, procedure allowlist (no Bash, no SQL).
* Eval harness: five interviews (agency on Airtable and QuickBooks, SaaS on Notion and Stripe, restaurant on spreadsheets, clinic on ClickUp, mixed) scored nightly.
* Playwright: chat, plan card, approve, progress; visual baselines at the seven widths, both themes.

**Demo**

Reviewer opens Settings > Migrate, names Airtable and QuickBooks in three answers, receives a plan card with estimates, requests a dry run, reads the plain-language report and clicks Approve to watch the commit. Under two minutes with fixture sources.

**Edge cases**

* Tool without an importer (Monday, HubSpot): CSV recipe path proposed.
* Dry run with 30 percent errors: no commit; three mapping iterations then escalation.
* Owner leaves mid-plan: state saved and resumed with a summary.
* Conflicting owners: both recorded, one decision requested.
* OAuth expires: reconnect link; never passwords.
* Non-owner approval: minting denied; agent names who can approve.

**Dependencies**

PAP-199 and PAP-104 (hard). PAP-105, PAP-108, PAP-109, PAP-110, PAP-129, PAP-142, PAP-146, PAP-205, importers as available.

**Agent**

Built by Scout (lead) with Quill drafting the prompt. Reviewed by Sentinel (Security Auditor, Code Reviewer); Justin approves the character.

**Size**

M: character, skill, one chat surface and evals over an existing framework.
