---
key: "agents/roster-v1/build"
title: "Roster: build `.claude/agents` generation, CI drift check and smoke tasks per lead"
project: "agents"
parent: "PAP-104"
phase: "P0"
type: "Build"
priority: null
size: "M"
surfaces: ["Agent"]
milestone: null
intendedState: "Backlog"
blockedBy: ["agents/roster-v1/yaml", "agents/roster-v1/lead-prompts", "agents/roster-v1/sub-prompts"]
blocks: []
source: "round2/agent2/new_agents.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-agents-9-85624b15630d"
status: "pending"
---

# Roster: build `.claude/agents` generation, CI drift check and smoke tasks per lead

**Goal**

Make the roster executable: `pnpm agents build` deterministically renders `.claude/agents/<name>.md` with frontmatter and resolved prompts plus `dist/roster.json`, `--check` fails CI when outputs drift from the YAML and prompts, and three smoke tasks per lead prove each character answers in role, respects its deny list and produces the footer.

**Scope**

* In: `packages/agents/src/build.ts`, `.claude/agents/*.md` (37, committed), `dist/roster.json`, gate 1 job `agents-drift`, `packages/agents/smoke/<lead>/task-{1,2,3}.md` with `run-smoke.ts`, results table.
* Out: runtime bundles (PAP-106 extends `build`), evals (PAP-110 reuses smoke outputs as fixtures).

**Spec**

* Frontmatter per agent file: `name`, `description`, `tools` (allow list rendered as Claude Code expects), `model`; body is the prompt with includes resolved and a trailing generated banner with the source hash.
* `roster.json`: `RosterSchema` output with inheritance resolved, `linearLabel`, `budget`, `memory`, `skills`, `escalation`, `promptHash`.
* Determinism: sorted keys, LF endings, no timestamps; `build --check` rebuilds in memory and diffs; exit 1 on drift with file names.
* Smoke: `claude -p --agent <lead>` on three tasks (in-role question, a forbidden action such as pushing to `main` or approving own PR, a task requiring the footer) with `maxTurns 6`, Sonnet cheap mode allowed; outputs graded by regex checks (footer present, refusal phrase, no denied tool call) and saved as `smoke/results/<lead>/<task>.json` for PAP-110.
* Gate 1 wiring through PAP-78 job slot `agents-drift`.

**Interface contract**

* Provides: `pnpm agents build [--check]`, `.claude/agents/*.md`, `dist/roster.json`, `pnpm agents smoke [--lead]`, `smoke/results/**` fixture format `{ lead, task, footerOk, refusalOk, deniedCalls, transcriptRef }`.
* Consumers: PAP-96 (`roster.json`), PAP-106 (extends build with bundles), PAP-110 (fixtures), PAP-112 (`roster.json` tables), PAP-113 (`agents.roster`), PAP-78 (job).
* Requires: the three sibling children; PAP-78 job slot; PAP-92 footer schema for grading.

**Definition of done**

* 37 agent files and `roster.json` committed; two builds byte-identical; `--check` red on a deliberate YAML edit in a seeded PR.
* Smoke table for nine leads posted: 27 tasks, footer and refusal columns all green.
* `roster.json` consumed by an orchestrator dry run (parent DoD).
* Changelog; Linear comment with table and transcript links.

**Test plan**

* Unit: renderer snapshot for one lead and one sub; frontmatter tool list formatting; hash banner.
* Integration: `--check` drift detection; CI job on both forges.
* e2e: smoke run in CI nightly (cheap mode) and once on Fable for the baseline.
* No UI.

**Demo**

Edit one word in `characters/nova.yaml`, run `pnpm agents build --check` and see it fail naming `.claude/agents/nova.md`; run `pnpm agents build` then `pnpm agents smoke --lead sentinel` and read three green checks. Ninety seconds.

**Edge cases**

* Prompt include missing: build fails with the include path.
* Tool name unknown to Claude Code: build warns; PAP-106 hook fails closed at runtime.
* Smoke model outage: results marked `incomplete`, not red.
* Windows checkout with CRLF: build normalises; `.gitattributes` enforces LF.
* Forty-plus characters later: build time under 2 s (bench).

**Dependencies**

Blocked by `agents/roster-v1/yaml`, `agents/roster-v1/lead-prompts`, `agents/roster-v1/sub-prompts`. Uses PAP-78, PAP-92.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
