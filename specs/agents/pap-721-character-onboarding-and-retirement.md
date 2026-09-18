---
identifier: "PAP-721"
title: "Character onboarding and retirement: `pnpm agents new <name> --lead <lead>` scaffolds YAML, prompt, smoke tasks, eval task, label and bundle and files the Needs Justin hiring card; `pnpm agents retire <name>` archives with an ADR"
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
blockedBy: ["PAP-94", "PAP-287"]
blocks: []
key: "r4/agents/character-onboarding-and-retirement-wizard"
url: "https://linear.app/paperos/issue/PAP-721/character-onboarding-and-retirement-pnpm-agents-new-name-lead-lead"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:31.611Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-721: Character onboarding and retirement: `pnpm agents new <name> --lead <lead>` scaffolds YAML, prompt, smoke tasks, eval task, label and bundle and files the Needs Justin hiring card; `pnpm agents retire <name>` archives with an ADR

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-104 says a tenth lead is "YAML plus a label, no code change" and the project non-goal is autonomous hiring without a Needs Justin approval; PAP-112 documents changing the org. Nothing generates the seven files a new character needs in the right places or files the approval. A wizard makes adding or retiring a character a ten-minute, approved, reversible operation instead of a hand-copied one.

**Scope**

* In: `packages/agents/src/cli/{new,retire}.ts`: `pnpm agents new <name> --lead <lead> [--sub] --role "..." --scopes a,b --model ... --interactive`, scaffolding (character YAML from `roster.yaml` defaults, prompt from the PAP-285 template with `{{include}}`s, three smoke tasks, one eval task skeleton, `Character/<Name>` label via PAP-91 script for leads, bundle and plugin rebuild), the hiring decision card (PAP-94), `pnpm agents retire <name>` (YAML `status: retired`, prompt moved to `retired/`, handbook page to `handbook/retired/`, ADR via `write-adr`, label kept, mentions redirected per PAP-112), docs section "Changing the org".
* Out: the approval itself (Justin), prompt quality (PAP-285 lint and reviews), eval content beyond the skeleton (PAP-309).

**Spec**

* `new` validates with `pnpm agents validate` before writing anything; a lead requires `--reports-to atlas`; a sub requires `--lead` and inherits tools as a subset (`SUB_TOOL_NOT_IN_LEAD`).
* Files: `characters/<name>.yaml`, `prompts/<name>.md`, `smoke/<name>/task-{1,2,3}.md`, `evals/tasks/<name>/intro-1/task.yaml`, handbook stub `docs/agents/handbook/<name>.md`, `Character/<Name>` label (leads), `.claude/agents/<name>.md` and bundle via `pnpm agents build`, plugin version bump.
* Approval: the wizard opens a PR labelled `roster-change` and files a Needs Justin card `Decision needed: hire <name> (<role>, reports to <lead>, scopes ...)` with the PR link; the PR's Gate 1 `agents-drift` job fails until the card is `approve`d (checked through PAP-97 `decision-applied`); Atlas merges after approval.
* `retire`: sets `status: retired`, keeps the YAML for history, removes the character from `roster.json` active set and bundles, redirects `@mentions` (PAP-112 handler) to the lead, writes the ADR, opens a PR with the same approval gate.
* Both commands are idempotent and print a checklist of what they created or changed.

**Interface contract**

* Provides: `pnpm agents new|retire`, label `roster-change`, the hiring card template, `status: retired` semantics in `roster.json`.
* Consumes: PAP-287 build, PAP-285 prompt template and lint, PAP-91 label script, PAP-94 cards and PAP-97 decision events, PAP-112 handbook conventions, PAP-130 ADRs, plugin packaging (round-4 issue).

**Definition of done**

* `pnpm agents new calibration-auditor --lead sentinel --sub` scaffolds the PAP-241 sub, passes validate, lint and build, opens the PR and files the card (recording); Gate 1 blocks until approval and passes after `approve`.
* `retire` on a toy character produces the ADR, redirect and PR (test); docs; changelog; Linear comment with the recording.

**Test plan**

* Unit: scaffold snapshot, inheritance checks, idempotency, approval gate check with a mocked decision event.
* E2E: live run for the Calibration Auditor sub (a real addition PAP-241 proposes).

**Demo**

Run `pnpm agents new calibration-auditor --lead sentinel --sub --interactive`, answer four questions, open the PR and the Needs Justin card; reply `approve` and watch Gate 1 turn green. Two minutes.

**Edge cases**

* Name collides with an existing character: refused with the existing file path.
* Justin rejects the hire: PR closed by Atlas; files removed by reverting the branch; nothing merged.
* Retiring a lead with active subs: refused until subs are reassigned with `--reassign-to`.
* Character added by hand without the wizard: `agents-drift` and the handbook `--check` flag the missing pieces.

**Dependencies**

Hard: PAP-287, PAP-94. Soft: PAP-285, PAP-91, PAP-97, PAP-112, PAP-130, PAP-715.

**Agent**

Builder: Atlas (Decomposer) with Quill. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/agents/claude-code-plugin-packaging` = PAP-715.
