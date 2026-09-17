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
children: []
blockedBy: ["PAP-103"]
blocks: ["PAP-106", "PAP-108", "PAP-109", "PAP-110", "PAP-112", "PAP-113", "PAP-192", "PAP-208", "PAP-218"]
key: "agents/roster-v1"
url: "https://linear.app/paperos/issue/PAP-104/write-the-nine-lead-characters-and-their-sub-characters-as"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-104: Write the nine lead characters and their sub-characters as .claude/agents definitions with system prompts

**Goal**

Bring the org to life: write the nine lead characters (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout) and their 28 sub-characters from plan.json as validated character YAML files with carefully written system prompts, and generate the `.claude/agents/*.md` definitions that Claude Code loads, so the orchestrator can spawn any of them by name.

**Scope**

In:
- `packages/agents/characters/*.yaml` for all 37 characters, fields filled from plan.json `agents[]` (role, reportsTo, tools, access, plugins, subAgents) and completed with model, effort, permission mode, budgets, skills, memory path and escalation rules.
- System prompts in `packages/agents/prompts/<name>.md`, 300-800 words each, structured as: identity and remit, what good looks like, hard limits (what it may never do), how it reports (playbook footer), when it escalates, its sub-characters and when to delegate, its favourite tools. Prompts follow the Fable 5.1 guidance: state goals and constraints, avoid over-prescriptive step lists, ask for progress notes on long tasks.
- Shared prompt fragments `packages/agents/prompts/_shared/` (playbook pointer, comment footer, code standards, review gates) included by reference at build time to avoid drift.
- `pnpm agents build` implementation: renders `.claude/agents/<name>.md` with frontmatter (`name`, `description`, `tools`, `model`) and the prompt body; writes `packages/agents/dist/roster.json` consumed by the orchestrator and the org chart.
- Delegation wiring: each lead's `description` names the situations it handles so Claude Code's automatic sub-agent selection works; subs are listed in the lead's prompt with one-line triggers.
- Three smoke tasks per lead (in `packages/agents/smoke/`) run once via `claude -p --agents` to confirm each character answers in role, respects its deny list and produces the footer; outputs saved as fixtures for `agents/eval-harness`.

Out: runtime enforcement of allowlists (`agents/tool-scopes`), persistent memory contents (`agents/memory`), handoff protocol text (`agents/handoffs`), the handbook (`agents/character-docs`).

**Spec**

- Defaults: leads `claude-fable-5-1`, effort `xhigh`, `acceptEdits`; subs that mostly read (Library Evaluator, Prompt Logger, Changelog Scribe) `claude-sonnet-5` at `medium`; reviewers (Sentinel subs) `claude-fable-5-1` at `high` with `permissionMode: plan` and no Write/Edit tools.
- Budgets seeded from the plan's area shares: Sentinel and its subs get 30 percent of daily allowance; Atlas 8; builders share the rest; exact numbers in `roster.yaml` defaults.
- Escalation rule shared by all: `when: "irreversible action or spend over budget" action: needs-justin`; Atlas additionally `when: "cycle in dependencies" action: needs-justin`.
- Sentinel prompts include the severity taxonomy from `quality/review-rubrics` by reference and explicitly forbid merging.
- Build is deterministic; CI fails if `.claude/agents` is out of date with the YAML (`pnpm agents build --check`).

**Definition of done**

- `pnpm agents validate` passes for all 37 characters; tree renders (`pnpm agents tree`) and matches plan.json.
- `.claude/agents/*.md` generated and committed; `--check` wired into CI gate 1.
- Smoke tasks executed for each lead; transcripts show in-role behaviour, correct footer and a refusal when asked to do something outside the deny list; summary table posted as a Linear comment.
- Prompts reviewed by Sentinel for contradictory instructions and by Quill for clarity; each prompt under 800 words (word-count test).
- `roster.json` consumed successfully by `pm-linear/orchestrator` in a dry run.
- Changelog entry; Linear comment with the tree and smoke results.

**Edge cases**

- Two subs with near-identical descriptions (Code Reviewer vs Edge Case Hunter): sharpen descriptions until a classification test of 20 sample tasks routes each correctly.
- A lead's prompt exceeds the budget when shared fragments are included: fragments count toward the limit; trim.
- Character invoked outside a repo checkout (Atlas planning session): prompts must not assume `cwd` is a worktree.
- Model unavailable (refusal fallback or outage): orchestrator substitutes the roster's `fallbackModel` (default `claude-opus-5`); prompts must not name the model.
- Justin renames a character: `name` is the id; `displayName` changes freely.
- Plan.json adds a tenth lead later: no code change, only YAML plus a Character label in Linear.

**Dependencies**

- `agents/character-schema` (schema, validator, build stub).
- Soft: `pm-linear/session-playbook` (referenced by prompts), `quality/review-rubrics` (referenced by Sentinel prompts).

**Agent**

Built by Atlas (lead) with Quill (Page Spec Writer) drafting prompts; reviewed by Sentinel (Code Reviewer) and Justin via a single `Needs Justin` item approving the roster, since hiring characters requires his sign-off.

**Size**

L: 37 characters, 37 prompts, a build pipeline and smoke runs.
