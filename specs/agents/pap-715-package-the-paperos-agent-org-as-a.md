---
identifier: "PAP-715"
title: "Package the PaperOS agent org as a Claude Code plugin: agents, skills, hooks, rules and MCP allowlists installable into any repo with one command and versioned with the roster"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-105", "PAP-287", "PAP-709"]
blocks: []
key: "r4/agents/claude-code-plugin-packaging"
url: "https://linear.app/paperos/issue/PAP-715/package-the-paperos-agent-org-as-a-claude-code-plugin-agents-skills"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:31.030Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-715: Package the PaperOS agent org as a Claude Code plugin: agents, skills, hooks, rules and MCP allowlists installable into any repo with one command and versioned with the roster

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

The roster, skills, hooks and rules are built into `paperos-template`, but the schema lists `plugins[]`, the character sheets name plugins (`code-review`, `security-review`, `linear-api`), and every generated app plus the orchestrator, sandbox and QA repos need the same `.claude/` content. Round 3 asked for everything to be plug and play: packaging the org as a Claude Code plugin with a marketplace manifest makes `paperos create` and every other repo install it in one command and upgrade it by version.

**Scope**

* In: `packages/claude-plugin/` producing `paperos-agents` (plugin manifest, `agents/`, `skills/`, `hooks/`, `rules/`, `.mcp.json` templates, `commands/` for `/request-approval` and `/handoff`), `marketplace.json` for the `imagine-os` plugin marketplace repo, `pnpm plugin:build --check` (deterministic from `roster.json`, `skills.json`, hooks and bundles), `pnpm plugin:install <repo>` wrapper around `claude plugin install`, version pinned to `roster.json.version`, install steps in `paperos create` (PAP-22) and `forge bootstrap` (PAP-51), `docs/agents/plugin.md`.
* Out: publishing outside `imagine-os`, per-character bundles (they stay generated per session by PAP-106), rewriting skills (PAP-105), the rules and skills registry UI (PAP-134 reads the same files).

**Spec**

* Plugin layout follows Claude Code's plugin structure: `plugin.json` (name `paperos-agents`, version, description, author), `agents/*.md` from `.claude/agents` (PAP-287), `skills/*/SKILL.md` from `.claude/skills` (PAP-105, PAP-118, PAP-218), `hooks/hooks.json` (PAP-106 enforce-scope and PAP-107 logging), `rules/session-playbook.md` (PAP-92), `.mcp.json` template with server ids from PAP-210 and env names only, `commands/` slash commands.
* Build: `pnpm plugin:build` copies generated artefacts, rewrites relative paths, stamps `version` from `roster.json`, and writes a content hash; `--check` fails Gate 1 on drift; the marketplace repo `imagine-os/paperos-plugins` holds `marketplace.json` listing the plugin and its versions.
* Install: `claude plugin marketplace add imagine-os/paperos-plugins` then `claude plugin install paperos-agents@<version>`; `pnpm plugin:install` wraps both and writes `.claude/settings.json` `enabledPlugins`; project-level `.claude/` overrides remain possible and are documented as the escape hatch.
* Versioning: semver from `roster.json`; a prompt or skill change bumps patch, a new character minor, a schema change major (PAP-103 `schemaVersion`); the changelog entry is generated from the diff.
* Consumers: `paperos create` (PAP-22) and `forge bootstrap` (PAP-51) install the plugin instead of copying `.claude/`; the orchestrator's session image (PAP-280) installs it at build time; the QA sandbox repo installs it.

**Interface contract**

* Provides: plugin `paperos-agents`, marketplace repo and `marketplace.json`, `pnpm plugin:build|install`, version convention, install steps for consumers.
* Consumes: PAP-287 agents and `roster.json`, PAP-105 skills, PAP-106 hooks, PAP-92 rules, PAP-210 catalog, Claude Code plugin CLI, PAP-22 and PAP-51 for wiring.

**Definition of done**

* Plugin builds deterministically; `--check` in Gate 1; installed into a fresh clone of the sandbox repo with one command and `claude -p --agent sentinel` answers in role (recording).
* Version bump rules tested on fixture diffs; marketplace repo created and mirrored (PAP-47).
* `paperos create` on a toy app installs the plugin instead of copying `.claude/` (PR reference); docs; changelog; Linear comment with the recording.

**Test plan**

* Unit: layout builder snapshot, path rewriting, version bump derivation, hash drift.
* E2E: install into a fresh repo in CI and run one smoke task per lead in cheap mode.

**Demo**

In an empty repo run `pnpm dlx paperos plugin:install`, then `claude -p --agent atlas "who merges PRs?"` and read the in-role answer citing the Merger. Under two minutes.

**Edge cases**

* Claude Code plugin format changes: the builder targets the documented format and a fixture install test catches breakage nightly.
* A repo needs a subset of characters (QA sandbox needs Sentinel only): `pnpm plugin:build --characters sentinel` produces a variant plugin `paperos-agents-quality`.
* Hooks need repo-specific paths (worktree root): hooks read `CLAUDE_PROJECT_DIR`, never hard-coded paths.
* Local `.claude/` and plugin disagree: project settings win per Claude Code precedence; the drift check reports it.

**Dependencies**

Hard: PAP-287, PAP-105, PAP-709. Soft: PAP-92, PAP-107, PAP-210, PAP-22, PAP-51, PAP-280, PAP-47.

* Soft dependency (round 4): PAP-22 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-25) is later than PAP-22's (2026-09-24); build against its interface and reconcile when it lands.
  **Agent**

Builder: Atlas (Dispatcher) with Quill. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/agents/character-bundles-and-enforce-scope-hook` = PAP-709.
