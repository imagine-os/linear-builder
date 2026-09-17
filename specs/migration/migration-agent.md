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
blockedBy: ["PAP-104", "PAP-199"]
blocks: []
key: "migration/migration-agent"
url: "https://linear.app/paperos/issue/PAP-208/create-the-migration-agent-character-that-interviews-users-about"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-208: Create the migration agent character that interviews users about current tools and runs the imports

**Goal**

Make migration a conversation: a Scout sub-character, Migration Guide, that interviews a new tenant about the tools they use today, proposes a migration plan (which importers, which templates, in what order, with time estimates from `migration/format-research`), runs dry runs, explains the reports in plain language, asks for the decisions only a human can make, and executes committed imports through the framework, reporting progress in-app and in Linear.

**Scope**

In:
- Character `packages/agents/characters/migration-guide.yaml` (parent Scout, `kind: sub`, model `claude-fable-5-1`, effort `high`, `permissionMode: dontAsk`, tools: Read, Grep, WebFetch, MCP `paperos-import` procedures (`sources.connect` link generation, `mappings.*`, `runs.dry`, `runs.commit` only with an approval token, `runs.rollback`), deny Bash and raw SQL; budget `perSessionUsd` 8) and prompt `packages/agents/prompts/migration-guide.md` (identity, interview style, hard limits, report format).
- Skill `.claude/skills/migrate-tenant/SKILL.md`: interview script (current tools, data volumes, what matters most, cutover date, who else uses it), plan template, decision points (dedupe strategy, people matching, identifier strategy, sample data), execution loop (dry run -> summarise -> ask -> commit), completion checklist (counts match, spot checks, export baseline taken via `migration/export`).
- In-app conversation surface: `_app/settings/migrate` chat built on `realtime/collab-text` messages with the agent as a participant (`realtime/agent-presence`), rendering plan and report cards (structured JSON blocks) with buttons that grant the approval token for commit; every exchange logged to `collab/prompt-log-store`.
- Interview knowledge: connector capabilities and limits read from `migration/format-research` docs and the connector registry at run time, so new importers appear without prompt changes.
- Handoff: when a decision exceeds the agent's remit (data over 5M rows, regulated data in the clinic template, ledger conversion dates), the agent files a `Needs Justin` item via `agents/handoffs` protocol or asks the tenant owner explicitly, and waits.
- Eval fixtures for `agents/eval-harness`: five scripted interviews (agency on Airtable and QuickBooks, SaaS on Notion and Stripe, restaurant on spreadsheets, clinic on ClickUp, mixed) with golden plans and a rubric (right importers, right order, correct limits cited, no commit without approval).

Out: building importers, live sync, migrating credentials, running against sources the tenant has not connected via OAuth themselves.

**Spec**

- Approval token: `runs.commit` requires `approvalToken` minted by the UI button click (or a Linear comment `approve <run_id>` by an owner); tokens are single use and expire in 30 minutes.
- Plan card schema: `{ steps[]: { importer, source, collections, estimateMinutes, dependsOn }, templates[], risks[], questions[] }` validated by Zod; the agent may not skip a step the plan lists without a recorded reason.
- Report card schema mirrors `import_run.stats` plus a plain-language summary limited to 150 words and the top 5 issues with suggested fixes (field-level mapping edits the agent can apply on request).
- The agent never sees raw customer records beyond dry-run examples (20 per field) and states this when asked.
- Session limits: 90 minutes or budget; on stop it writes a resumable plan file to the tenant's docs (`agents/memory`).
- Language: follows the tenant's locale for the conversation; plan and report JSON stay English.

**Definition of done**

- Character validates and appears in the org chart; smoke transcript shows in-role interview and a refusal to commit without a token.
- End-to-end on staging: interview a scripted tenant, produce a plan, run CSV and Airtable dry runs, get approval via button, commit, take an export baseline; recording attached.
- Eval harness: five fixtures score at or above 0.8; no fixture results in an unapproved commit (hard fail).
- Vitest: approval token lifecycle, plan and report schema validation, remit checks that trigger handoff.
- Playwright: chat surface with plan card, approve button, progress; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
- `docs/agents/migration-guide.md` and skill doc; CHANGELOG entry; Linear comment with recording and eval scores; Justin approves the character in one `Needs Justin` item.

**Edge cases**

- Tenant names a tool without an importer (Monday, HubSpot): agent proposes CSV export path with the exact export steps from `migration/format-research` and files a feature request comment.
- Dry run reveals 30 percent errors: agent must not commit; proposes mapping fixes and reruns dry, up to 3 iterations before escalating.
- Owner walks away mid-plan: state saved; next session resumes with a summary.
- Two owners give conflicting answers: agent records both and asks for one decision, no guessing.
- Source OAuth expires during the session: agent asks the owner to reconnect via link; never asks for passwords.
- Approval given by a non-owner: token minting is permission-gated; agent explains who can approve.

**Dependencies**

`migration/import-framework` and `agents/roster-v1` (hard). `agents/skills-library`, `agents/eval-harness`, `agents/handoffs`, `agents/memory`, `collab/prompt-log-store`, `realtime/collab-text` and `realtime/agent-presence` (fallback: plain message list), `migration/export`, importers as available.

**Agent**

Built by Scout (lead) with Quill drafting the prompt and interview script. Reviewed by Sentinel (Security Auditor for tool scope and token flow, Code Reviewer) and Justin approving the character.

**Size**

M: character, skill, one chat surface and evals over an existing framework.
