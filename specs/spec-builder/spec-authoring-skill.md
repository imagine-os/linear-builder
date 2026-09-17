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
blocks: []
key: "spec-builder/spec-authoring-skill"
url: "https://linear.app/paperos/issue/PAP-118/write-the-agent-skill-interview-draft-page-spec-validate-open-linear"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-118: Write the agent skill: interview -> draft page spec -> validate -> open Linear issue

**Goal**

Give every character a repeatable way to turn a request into a validated page spec and a Linear issue: interview the requester (or read a brief), draft `page.spec.yaml`, run the validator until clean, commit on a branch and open a spec-complete issue. This is how hundreds of specs get written without Justin editing YAML.

**Scope**

In:
- `.claude/skills/author-spec/SKILL.md` (under 1500 words, frontmatter per `agents/skills-library` lint) with `references/question-bank.md`, `templates/page.spec.yaml`, and scripts in `scripts/` run with `tsx`.
- Flow: (1) `scripts/context.ts` prints `app.spec.yaml` audiences, entities, existing page ids and routes so the model never invents names; (2) interview of at most 12 questions from the bank, grouped by surface (customer, staff, agent), skipped when a brief answers them; (3) draft YAML from `templates/page.spec.yaml`; (4) `paperos-spec validate --format json` and up to three fix rounds; (5) `scripts/commit.ts` writes `specs/pages/<id>.spec.yaml` on branch `spec/<id>` with commit `spec(<id>): add page spec` plus `Linear:` and `Character:` trailers (`forge/branch-policy`), pushes and opens a PR using `forge/pr-templates`; (6) `scripts/open-issue.ts` creates the Linear issue "Build <title> from spec" via the `linear-update` skill with the `pm-linear/issue-contract` body (spec path, acceptance criteria copied from `edgeCases` and `states`, surfaces, definition of done), labels `Build` plus Surface labels, project from `meta.owner` mapping, state `Backlog`; moves to `Ready for Claude` only when validation is clean and every `dependsOn` issue is Done.
- Open questions recorded under `x-open-questions` in the spec and, if any is blocking, one `Needs Justin` comment batched per `pm-linear/justin-queue` rules.
- Skill tests in `packages/agents/skills-tests/author-spec/`: scripts against fixtures with mocked Linear (`nock`) and a toy repo.

Out: the validator itself, the editor UI, decomposition of epics (Atlas Decomposer uses this skill per page).

**Spec**

- Question bank covers purpose and metric, audiences and actions, data read/written, integrations, layout template and slots, states copy, transitions, edge cases (at least five prompted categories: empty, huge, offline, denied, concurrent edit).
- Drafting rules in SKILL.md: prefer existing components from `registry.json`; every action gets an access entry; every entity in `data` must exist in `app.spec.yaml`; no prose longer than two sentences per field.
- `open-issue.ts` is idempotent: searches Linear for an issue with `spec:<id>` in the description and updates instead of duplicating.
- Budget guard: the skill aborts after 40 turns and leaves a `draft` status spec with a comment, so a runaway interview cannot burn credits.
- Output on the last line of every script is JSON `{ ok, specPath, prUrl?, issueUrl?, issues: [] }`.

**Definition of done**

- Dry run transcript: a session invokes the skill on a brief ("customers list and pay invoices") and produces a spec that validates first or second round, a PR and a Linear issue (links in comment).
- Second dry run from a live interview with Justin's answers pasted as a brief.
- Vitest for scripts: context output, commit trailer format, issue body matches `pm-linear/issue-contract` schema, idempotent re-run.
- Lint passes (`agents/skills-library` word and frontmatter rules); listed in `skills.json` for Quill, Atlas and Nova.
- `docs/agents/skills.md` updated; CHANGELOG entry; Linear comment with both transcripts.

**Edge cases**

- Brief asks for an entity that does not exist: skill stops and proposes a `data-layer` issue instead of inventing a table.
- Validator unavailable (package not built): skill runs `pnpm --filter spec build` once, then fails loudly rather than skipping validation.
- Page id already exists: skill offers to update it and bumps `status` back to `draft` with a changelog note in `x-history`.
- Linear rate limit: `linear-update` writes to `artifacts/pending-comments/` for the orchestrator to flush.
- Requester answers in another language: spec copy fields stay in the app default locale; original answers stored under `x-interview`.
- Interview reveals the page should be two pages: skill drafts both and cross-links via `events`.

**Dependencies**

`spec-builder/validator` (hard), `agents/skills-library` (`linear-update`, lint, `skills.json`) (hard). Soft: `pm-linear/issue-contract`, `forge/pr-templates`, `spec-builder/app-level-spec`.

**Agent**

Built by Quill (Page Spec Writer) with Atlas (Decomposer) on `open-issue.ts`. Reviewed by Sentinel (Code Reviewer) and Atlas for the Linear contract.

**Size**

M: prose plus three scripts, but two dry runs with real Linear are required.
