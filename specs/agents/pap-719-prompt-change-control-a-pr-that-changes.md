---
identifier: "PAP-719"
title: "Prompt change control: a PR that changes a character prompt, skill or rule runs that character's eval tasks in cheap mode, posts the score delta, records the prompt version in sessions and offers one-command rollback"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-287", "PAP-310"]
blocks: []
key: "r4/agents/prompt-change-control-and-experiments"
url: "https://linear.app/paperos/issue/PAP-719/prompt-change-control-a-pr-that-changes-a-character-prompt-skill-or"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:21.090Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-719: Prompt change control: a PR that changes a character prompt, skill or rule runs that character's eval tasks in cheap mode, posts the score delta, records the prompt version in sessions and offers one-command rollback

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Prompts are code with no test gate: PAP-287 hashes them and PAP-310 detects regressions the night after a change ships. LangSmith and Braintrust treat prompt versions as first-class with datasets and comparisons. This issue closes the loop before merge: a prompt, skill or rule change triggers the affected character's golden tasks in cheap mode, the PR shows the delta against the last baseline, every session records the prompt version it ran with, and rollback is one command.

**Scope**

* In: Gate 1 job `prompt-evals` (path filter `packages/agents/prompts/**`, `.claude/skills/**`, `.claude/rules/**`, `packages/agents/characters/**`) mapping changed files to characters and running `pnpm evals run --character <name> --model claude-sonnet-5 --effort low`, delta comment section "Prompt evals" with per-task scores versus the seven-run baseline, `promptVersion` (hash from PAP-287) in `sessions` and the footer, `pnpm agents rollback-prompt <character> --to <hash>` (reverts files from git and rebuilds), `docs/agents/prompt-change-control.md`, an `experiment:` label for A/B runs of two prompt variants on the same tasks.
* Out: the eval tasks and judge (PAP-309, PAP-310), full-model evals on PRs (nightly only), prompt authoring rules (PAP-285).

**Spec**

* Mapping: changed lead prompt runs that lead's three tasks and one task per sub; changed sub prompt runs the sub's task; changed shared fragment runs one task per lead (nine); changed skill runs the tasks that exercise it (`skills.json` to task index); cap $5 per PR, over cap samples and says so.
* Delta: scores from `eval_runs` compared with the median of the last seven nightly runs at the same task version; a drop over 15 percent is S1 in the sticky comment and blocks merge for Sentinel and Atlas prompts, warns for others; deterministic graders run first so a broken footer fails fast.
* `promptVersion`: the PAP-287 prompt hash per character stored in `sessions.prompt_version` and the footer; PAP-98 and PAP-310 group by it so a regression names the version.
* Rollback: `pnpm agents rollback-prompt <character> --to <hash>` checks out the prompt and YAML from the commit that produced the hash, rebuilds, opens a PR labelled `rollback`; the eval job runs on it like any change.
* Experiments: label `experiment:<name>` on a PR runs the tasks twice (base and head prompts) with the same fixtures and posts a side-by-side table; nothing merges from an experiment without a normal review.

**Interface contract**

* Provides: job `prompt-evals`, comment section, `sessions.prompt_version`, footer field `promptVersion`, `pnpm agents rollback-prompt`, label `experiment:*`.
* Consumes: PAP-287 hashes and build, PAP-308 runner and `eval_runs`, PAP-310 baselines and thresholds, PAP-105 `skills.json`, PAP-98 metering, PAP-111 cap.

**Definition of done**

* Seeded prompt break (Iris asked to skip axe) drops the score and the PR is blocked with the delta table (link); reverting restores green.
* Rollback command opens a valid PR from a past hash (recording); `promptVersion` appears in three live footers.
* Experiment label run posts a side-by-side table (screenshot); docs; changelog.

**Test plan**

* Unit: file-to-character mapping, cap sampling, delta math with missing baselines, rollback commit resolution.
* E2E: sandbox PR with a seeded prompt regression through the real job in cheap mode.

**Demo**

Open the seeded Iris PR: the "Prompt evals" section shows two tasks down 40 percent and a red status; run `pnpm agents rollback-prompt iris --to <hash>` and see the rollback PR. Under two minutes.

**Edge cases**

* No baseline yet (new character): absolute scores only, warn never block, note in the comment.
* Cheap-mode score differs systematically from Fable nightly: deltas compare cheap to cheap (baseline stored per model).
* Fragment change touching nine leads over cap: one task per lead, S1 only for Sentinel and Atlas.
* Prompt change intended to alter behaviour (new rule): author adds `evals: expected-change` in the PR body; the job posts but does not block, and the nightly re-baselines.

**Dependencies**

Hard: PAP-287, PAP-310. Soft: PAP-308, PAP-105, PAP-98, PAP-111, PAP-285.

**Agent**

Builder: Sentinel (Code Reviewer) with Atlas. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.
