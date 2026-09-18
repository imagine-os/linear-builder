---
identifier: "PAP-286"
title: "Roster: write the 28 sub-character prompts and delegation descriptions"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: "PAP-104"
children: []
blockedBy: ["PAP-284"]
blocks: ["PAP-287"]
key: "agents/roster-v1/sub-prompts"
url: "https://linear.app/paperos/issue/PAP-286/roster-write-the-28-sub-character-prompts-and-delegation-descriptions"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:10.558Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-286: Roster: write the 28 sub-character prompts and delegation descriptions

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Write the 28 sub-character prompts and the one-sentence `description` fields that drive Claude Code's automatic delegation, sharp enough that a classification test routes twenty sample tasks to the intended sub every time (Code Reviewer versus Edge Case Hunter, Dispatcher versus Decomposer, Views Engineer versus Canvas Cartographer).

**Scope**

* In: `packages/agents/prompts/<sub>.md` (28, 150-500 words with includes), refined `description` fields written back into the YAML, `packages/agents/test/delegation.test.ts` with 20 labelled tasks, `prompts/_shared/sub-footer.md`.
* Out: lead prompts (PAP-285), build (PAP-287).

**Spec**

* Structure: Who you are and who you report to; The one job (two sentences); Inputs you expect (artifact types from PAP-108 handoffs); Output contract (exact artifact: review JSON, migration files, stories, spec file); Limits (tools denied in YAML restated with the mechanism); When to hand back to your lead.
* `description` grammar: "Use when <trigger phrases>; not for <nearest sibling's job>." Under 200 characters.
* Reviewer subs (Sentinel's four): read-only wording, output the PAP-239 `Finding[]` block, severity from PAP-79, never approve or merge.
* Read-mostly subs on Sonnet: shorter prompts, explicit instruction to summarise rather than paraphrase transcripts (Prompt Logger), to preserve provenance (Changelog Scribe), to score with the rubric only (Library Evaluator).
* Classification test: 20 tasks with an expected sub; a cheap model call picks a sub from the 28 descriptions; pass threshold 20 of 20, allowed to fix descriptions until it passes.

**Interface contract**

* Provides: 28 prompt files, updated `description` fields, the delegation test and its task fixture (reused by PAP-110 as an Atlas golden task), `sub-footer.md`.
* Consumers: PAP-287, PAP-110, PAP-112 sub sections, PAP-108 (artifact expectations align with handoff kinds).
* Requires: PAP-284, `prompt-style.md` from the lead-prompts child (may start from its draft), PAP-108 kinds (draft acceptable).

**Definition of done**

* 28 prompts pass lint; descriptions under 200 characters.
* Delegation test 20 of 20 on two consecutive runs.
* Sentinel review of reviewer subs for read-only consistency; Quill review for clarity.
* Changelog; Linear comment with the classification table.

**Test plan**

* Unit: lint, description grammar regex, word counts.
* Integration: delegation test in CI (cheap mode, cost under $1).
* e2e: one dry run per Sentinel sub on a seeded PR fixture producing a valid `Finding[]` block.
* No UI.

**Demo**

Run `pnpm agents delegation-test` and watch twenty tasks route correctly; then feed "find the empty-state bug on the invoices page" and see `edge-case-hunter` chosen over `code-reviewer`. One minute.

**Edge cases**

* Two subs legitimately fit a task: the test fixture names a primary and an acceptable alternate.
* Sub prompt refers to a tool the YAML denies: lint fails via the PAP-112 prose rule reused here.
* Description too generic ("helps with code"): grammar regex rejects.
* Sub invoked directly by Justin: prompt says to report to the lead in the footer anyway.
* Plan adds a sub: template file plus a fixture task.

**Dependencies**

Blocked by PAP-284. Blocks PAP-287. Soft: PAP-108, PAP-239.

**Agent**

Built by Quill (Page Spec Writer) with Sentinel on reviewer subs; reviewed by Atlas.

**Size**

M
