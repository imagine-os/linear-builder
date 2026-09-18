---
identifier: "PAP-112"
title: "Publish the character handbook: who does what, how to summon them, what they may not do"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Docs"
priority: 2
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-287"]
blocks: []
key: "agents/character-docs"
url: "https://linear.app/paperos/issue/PAP-112/publish-the-character-handbook-who-does-what-how-to-summon-them-what"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:40.473Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-112: Publish the character handbook: who does what, how to summon them, what they may not do

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Docs M

**Goal**

Publish the handbook a human opens to understand the agent org: who each character is, what it owns, how to summon it from Linear or the CLI, what it may never do and how to change it. Written for Justin first, generated from the roster wherever possible so it never drifts from reality.

**Scope**

* In: `docs/agents/handbook/` (index with org chart, one page per lead with sub sections, `summoning.md`, `limits.md`, `changing-the-org.md`, `glossary.md`), `pnpm agents docs [--check]`, the `@character` mention handler.
* Out: the org chart UI (PAP-113), prompt content (PAP-104), the privilege matrix generation (PAP-106).

**Spec**

* Per-character page: role and remit, reports to, subs with triggers, generated tables for tools, MCP servers and access scopes from `roster.json` and the PAP-106 matrix, skills, budgets, escalation rules, example tasks it excels at, tasks to route elsewhere, three completed issues (linked), memory file link. Under 1200 words; index under 600; plain language with glossary links.
* Every "may not" statement links to the enforcing mechanism (deny list line, hook, branch protection rule).
* Frontmatter `generatedFrom`, `lastVerified`; CI fails if `roster.json` changed and docs were not regenerated.
* Mention handler: on `Comment.create` from a human containing `@atlas`..`@scout`, spawn a read-only session (`plan` mode, `maxTurns` 8, Sonnet unless the question is architectural), reply in a comment with the PAP-92 footer, cost capped at $3 through PAP-111; agent-authored mentions ignored.

**Interface contract**

* Provides: handbook pages in the PAP-128 docs engine (repo markdown fallback), `pnpm agents docs --check`, the mention handler registered via PAP-97 `registerWebhookHandler("linear", "Comment", "create")`, a `summon` contract: assign `Character/<name>` and move to `Ready for Claude`, or `pnpm agents run <name> --issue PAP-123`.
* Consumers: Justin and future staff; PAP-95 (links the origin story); PAP-113 drawer "Open handbook page" links `docs/agents/handbook/<name>`; PAP-134 registry indexes the pages.
* Requires: PAP-104 `roster.json`, PAP-106 matrix, PAP-97 webhooks, PAP-111 cap, PAP-128 rendering.

**Definition of done**

* All pages render with generated tables matching `roster.json`; `--check` in CI.
* `@sentinel` mention on a test issue gets a relevant reply within two minutes (screenshot).
* Read-through by Sentinel for accuracy against the privilege matrix and by Quill for clarity; every "may not" links.
* Screenshots at 375 and 1280 px; changelog; Linear comment with links and screenshots.

**Test plan**

* Unit: table generation snapshot from a roster fixture; prose lint flagging tool names absent from the generated table; word counts.
* Integration: mention handler on recorded comment webhooks, agent-author ignore, cost cap enforcement with a fake meter.
* e2e: live mention on staging.
* Visual: two handbook pages at 375 px (phone) and 1280 px in light and dark through the docs engine.

**Demo**

Open the handbook index on a phone, tap Sentinel, read its "may not merge" line and follow the link to the branch protection rule; then post `@sentinel is RLS on pm_issue correct?` on a test issue and read the reply. Two minutes.

**Edge cases**

* Retired character: page moves to `handbook/retired/` with the ADR; mentions redirect.
* Mention asking for an action: reply explains actions come from issues and offers to draft one (PAP-93 contract) on `yes`.
* Roster and prose disagree: CI lint fails.
* Docs engine down: markdown readable on the forge; relative links.
* Long access tables (Atlas): collapsed details block.

**Dependencies**

Blocked by PAP-104. Uses PAP-106, PAP-97, PAP-128, PAP-111.

**Agent**

Built by Quill (lead); reviewed by Sentinel (accuracy) and Atlas (org fit).

**Size**

M
