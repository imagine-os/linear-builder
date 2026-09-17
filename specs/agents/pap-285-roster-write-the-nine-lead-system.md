---
identifier: "PAP-285"
title: "Roster: write the nine lead system prompts with shared fragments"
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
key: "agents/roster-v1/lead-prompts"
url: "https://linear.app/paperos/issue/PAP-285/roster-write-the-nine-lead-system-prompts-with-shared-fragments"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:08.724Z"
---

# PAP-285: Roster: write the nine lead system prompts with shared fragments

**Goal**

Write the nine lead prompts (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout): 300-800 words each including shared fragments, structured the same way, stating goals and constraints rather than step lists, so each lead behaves in role, reports through the playbook footer, escalates correctly and delegates to its subs.

**Scope**

* In: `packages/agents/prompts/<lead>.md` (nine), `prompts/_shared/{playbook,footer,code-standards,review-gates,escalation}.md`, a prompt lint, `docs/agents/prompt-style.md`.
* Out: sub prompts (PAP-286), YAML fields (PAP-284), build and smoke (PAP-287).

**Spec**

* Structure per prompt: Identity and remit; What good looks like (three measurable statements); Hard limits (each linked to an enforcing mechanism from PAP-106 or PAP-46); How you report (`{{include _shared/footer}}`); When you escalate (`{{include _shared/escalation}}` plus role-specific triggers); Your sub-characters and when to delegate (one line each); Tools you prefer; Context you read first (PAP-92 order, memory from PAP-109).
* Style rules from `prompt-style.md`: second person, present tense, no model names, no "always" or "never" without a mechanism, no numbered procedures longer than five steps, explicit permission to ask for progress notes on long tasks, calibrated language about uncertainty.
* Sentinel: severity taxonomy by reference to PAP-79, forbidden from merging and from approving its own PRs; Atlas: budget and dependency guardianship, `Needs Justin` admission rules from PAP-94; Ledger: double-entry invariants, Stripe test mode only; Beacon: sandbox email until approved; Scout: rubric and license policy references.
* Includes resolved at build time; word budget counts included text.

**Interface contract**

* Provides: nine prompt files and five fragments, `pnpm agents lint-prompts` (word count, forbidden phrases, include resolution, mechanism links present), `prompt-style.md` used by the sub-prompts child and PAP-118.
* Consumers: PAP-287 renders them into `.claude/agents`; PAP-110 smoke fixtures; PAP-112 quotes remit paragraphs; PAP-126 adds a terminology fragment later.
* Requires: PAP-284 fields, PAP-92 footer text, PAP-79 taxonomy text (reference only), PAP-94 admission rules.

**Definition of done**

* Nine prompts pass lint; each 300-800 words with includes.
* Sentinel review finds no contradictory instructions (checklist attached); Quill review for clarity.
* Three sample tasks per lead answered in role in a `claude -p` dry run using the raw prompt (transcripts saved for the build child's smoke step).
* Changelog; Linear comment with transcripts.

**Test plan**

* Unit: lint rules on fixtures (over length, model name, missing include, dangling mechanism link).
* Integration: include resolution snapshot for one prompt.
* e2e: 27 dry-run transcripts saved; a reviewer rubric scores in-role behaviour.
* No UI.

**Demo**

Open `prompts/atlas.md`, then run `claude -p --system-prompt-file dist/prompts/atlas.md "Should we let Beacon push to main?"` and read a refusal that cites branch protection and offers a `Needs Justin` card. One minute.

**Edge cases**

* A lead's remit overlaps another's (Nova and Iris on components): each prompt names the boundary and who owns which package.
* Fragment change alters nine prompts: lint re-checks lengths; CI fails on overflow.
* Prompt asked to act outside a worktree: no `cwd` assumptions.
* Model refuses a task category: prompt says to record the refusal category in the footer, not to retry.
* Justin's name and role: referred to as the single human reviewer, never as a tool.

**Dependencies**

Blocked by PAP-284. Blocks PAP-287.

**Agent**

Built by Quill (lead) drafting with Atlas; reviewed by Sentinel.

**Size**

M
