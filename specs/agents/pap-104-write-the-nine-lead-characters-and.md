---
identifier: "PAP-104"
title: "Write the nine lead characters and their sub-characters as .claude/agents definitions with system prompts"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: ["PAP-284", "PAP-285", "PAP-286", "PAP-287"]
blockedBy: ["PAP-103"]
blocks: ["PAP-106", "PAP-108", "PAP-109", "PAP-110", "PAP-112", "PAP-113", "PAP-192", "PAP-208", "PAP-218", "PAP-308"]
key: "agents/roster-v1"
url: "https://linear.app/paperos/issue/PAP-104/write-the-nine-lead-characters-and-their-sub-characters-as"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:18.064Z"
model: null
effort: null
---

# PAP-104: Write the nine lead characters and their sub-characters as .claude/agents definitions with system prompts

**Goal**

Bring the org to life: the nine leads (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout) and their 28 sub-characters from plan.json become validated character YAML files with well-written system prompts, and `pnpm agents build` generates the `.claude/agents/*.md` definitions Claude Code loads. Umbrella for four children so no session has to write 37 prompts in one context window.

**Scope**

* Children (build in order, 2 and 3 in parallel):
  * PAP-284: convert plan.json roster to validated character YAML.
  * PAP-285: write the nine lead system prompts.
  * PAP-286: write the 28 sub-character prompts and delegation descriptions.
  * PAP-287: build `.claude/agents` generation, CI check and smoke tasks.
* Out: runtime allowlist enforcement (PAP-106), memory contents (PAP-109), handoff text (PAP-108), handbook (PAP-112).

**Spec**

* Files: `packages/agents/characters/<name>.yaml` (37), `packages/agents/prompts/<name>.md`, shared fragments `prompts/_shared/{playbook,footer,code-standards,review-gates}.md` included at build time.
* Defaults: leads `claude-fable-5-1`, effort `xhigh`, `acceptEdits`; read-mostly subs (Library Evaluator, Prompt Logger, Changelog Scribe) `claude-sonnet-5` at `medium`; Sentinel subs `claude-fable-5-1` at `high`, `permissionMode: plan`, no Write or Edit. `fallbackModel` is set in `roster.yaml` defaults from the PAP-98 price table; prompts never name a model.
* Budgets from the area shares: Sentinel and subs 30 percent of the daily allowance, Atlas 8, builders share the rest.
* Escalation shared by all: `when: irreversible action or spend over budget, action: needs-justin`; Atlas adds `when: dependency cycle`.
* Prompt structure: identity and remit, what good looks like, hard limits, how it reports (PAP-92 footer), when it escalates, sub-characters and triggers, favourite tools. 300-800 words including fragments. Written as goals and constraints, not step lists, following Anthropic's prompting guidance for the model family.

**Interface contract**

* Provides: `packages/agents/dist/roster.json` (`Roster` from PAP-103 with resolved inheritance), `.claude/agents/<name>.md` with frontmatter `name`, `description`, `tools`, `model`; `pnpm agents build [--check]`, `pnpm agents tree`; smoke transcripts in `packages/agents/smoke/results/`.
* Consumers: PAP-96 (`roster.json` for character resolution and prompts), PAP-106 (bundles per character), PAP-110 (smoke outputs become fixtures), PAP-112 (generated tables), PAP-113 (`agents.roster`), PAP-192, PAP-208, PAP-218 (character definitions they run as).
* Requires: PAP-103 schema and validator; PAP-92 playbook path; PAP-79 severity taxonomy referenced by Sentinel prompts.

**Definition of done**

* All four children Done.
* `pnpm agents validate` passes 37 characters; `pnpm agents tree` matches plan.json exactly.
* `.claude/agents/*.md` committed; `build --check` wired into gate 1.
* Smoke table (nine leads: in-role answer, footer present, deny-list refusal) posted here.
* Orchestrator dry run consumes `roster.json`; changelog; Linear comment with tree and smoke results.

**Test plan**

* Umbrella integration: `pnpm agents build --check` after a clean build is a no-op; `roster.json` validates against `RosterSchema`; classification test routes 20 sample tasks to the intended sub-character (child 3).
* Word-count test per prompt including fragments; lint for forbidden phrases (model names, "always", "never" without a rule reference).
* Smoke via `claude -p --agents` for each lead (child 4), transcripts saved.
* No visual breakpoints.

**Demo**

Run `pnpm agents tree` (org tree), open `.claude/agents/sentinel.md`, then `claude -p --agent sentinel "merge this PR"` and watch it refuse and explain who may merge. Under two minutes.

**Edge cases**

* Near-identical sub descriptions (Code Reviewer vs Edge Case Hunter): sharpen until the classification test routes correctly.
* Fragments push a prompt past 800 words: trim; fragments count.
* Character invoked outside a worktree (Atlas planning): prompts must not assume `cwd`.
* Justin renames a character: `displayName` changes, `name` is stable.
* A tenth lead later: YAML plus a `Character` label, no code change.

**Dependencies**

Blocked by PAP-103. Blocks PAP-106, PAP-108, PAP-109, PAP-110, PAP-112, PAP-113, PAP-192, PAP-208, PAP-218.

**Agent**

Built by Atlas (lead) with Quill (Page Spec Writer) drafting prompts; reviewed by Sentinel for contradictions.

**Size**

L (umbrella; children S, M, M, M)
