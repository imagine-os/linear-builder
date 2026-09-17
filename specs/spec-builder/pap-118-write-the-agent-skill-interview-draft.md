---
identifier: "PAP-118"
title: "Write the agent skill: interview -> draft page spec -> validate -> open Linear issue"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Spec schema and validator"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-105", "PAP-115"]
blocks: ["PAP-307", "PAP-360"]
key: "spec-builder/spec-authoring-skill"
url: "https://linear.app/paperos/issue/PAP-118/write-the-agent-skill-interview-draft-page-spec-validate-open-linear"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:16.505Z"
---

# PAP-118: Write the agent skill: interview -> draft page spec -> validate -> open Linear issue

**Goal**

Give every character a repeatable way to turn a request into a validated page spec and a contract-valid Linear issue: interview the requester or read a brief, draft `page.spec.yaml`, run the validator until clean, commit on a branch, open a PR and the issue. This is how hundreds of specs get written without Justin editing YAML.

**Scope**

* In: `.claude/skills/author-spec/` (`SKILL.md`, `references/question-bank.md`, `templates/page.spec.yaml`, `scripts/{context,commit,open-issue}.ts`), listing in `skills.json` for Quill, Atlas and Nova, `docs/agents/skills.md` update.
* Out: freeform issue triage for humans (PAP-307 reuses this skill's scripts), the editor UI (PAP-124), the validator (PAP-115).

**Spec**

* Flow: `context.ts` prints audiences, entities, existing page ids and routes from the app spec so names are never invented; interview of at most 12 questions from the bank grouped by surface, skipped when the brief answers them; draft from the template; `paperos-spec validate --format json` with up to three fix rounds; `commit.ts` writes `specs/pages/<id>.spec.yaml` on branch `spec/<id>` with commit `spec(<id>): add page spec` and `Linear:` and `Character:` trailers (PAP-46), pushes, opens a PR (PAP-49); `open-issue.ts` creates "Build `<id>` page from spec" in contract format (PAP-93) with the spec link, labels and Size, idempotent by `spec:<id>` marker.
* Drafting rules: prefer registry components (PAP-74); every action has an access entry; every entity exists in the app spec; at least five edge cases across empty, huge, offline, denied, concurrent edit; field prose at most two sentences.
* Budget guard: abort after 40 turns leaving a `draft` spec and a comment.
* Every script's last stdout line is JSON `{ ok, specPath, prUrl?, issueUrl?, issues[] }`.

**Interface contract**

* Provides: skill id `author-spec` in `skills.json`, script CLIs `author-spec context`, `author-spec commit --id <id>`, `author-spec open-issue --id <id> [--parent PAP-n]`, the question bank as data (`question-bank.yaml` with `surface`, `section`, `question`, `skipIf`).
* Consumers: Quill, Atlas, Nova sessions; PAP-307 calls `open-issue` for issues that need a spec; PAP-125 uses the skill to write the fourth example; PAP-110 golden task for Quill.
* Requires: PAP-115 CLI, PAP-105 lint and `linear-update`, PAP-93 `validateIssue`, PAP-46 trailers, PAP-49 PR template, PAP-117 app spec (soft).

**Definition of done**

* Dry run from a brief ("customers list and pay invoices") produces a spec valid within two rounds, a PR and an issue (links in comment).
* Second dry run from Justin's pasted answers.
* Vitest for scripts: context output, trailer format, issue body passes `validateIssue`, idempotent re-run.
* Lint passes; listed in `skills.json`; docs updated; changelog; Linear comment with both transcripts.

**Test plan**

* Unit: question selection given a brief (skip logic), template rendering, `open-issue` idempotency against a mocked Linear search, trailer regex.
* Integration: full script chain against a temp git remote and `nock` Linear.
* e2e: two dry-run transcripts saved under `packages/agents/smoke/author-spec/`.
* No UI breakpoints.

**Demo**

Run `claude -p --agent quill "use author-spec: customers list and pay invoices"`; watch it ask at most a handful of questions, print the validator result, and end with a PR link and a Linear issue whose description has all contract sections. Two minutes.

**Edge cases**

* Brief needs a missing entity: stop and propose a data-layer issue, never invent a table.
* Validator package not built: build once, then fail loudly.
* Page id exists: offer update, set `status: draft`, note in `x-history`.
* Linear rate limit: `linear-update` writes to `artifacts/pending-comments/`.
* Interview reveals two pages: draft both and cross-link via `events`.

**Dependencies**

Blocked by PAP-115, PAP-105. Soft: PAP-93, PAP-46, PAP-49, PAP-117.

**Agent**

Built by Quill (Page Spec Writer) with Atlas (Decomposer) on the issue script; reviewed by Sentinel.

**Size**

M
