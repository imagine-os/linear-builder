---
identifier: "PAP-105"
title: "Build the shared skills library (page-from-spec, review-pr, screenshot-audit, write-adr, linear-update) as .claude/skills"
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
blocks: ["PAP-108", "PAP-110", "PAP-118", "PAP-134", "PAP-306", "PAP-308"]
key: "agents/skills-library"
url: "https://linear.app/paperos/issue/PAP-105/build-the-shared-skills-library-page-from-spec-review-pr-screenshot"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:23.614Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-105: Build the shared skills library (page-from-spec, review-pr, screenshot-audit, write-adr, linear-update) as .claude/skills

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Package the procedures every character repeats into `.claude/skills` so sessions do them the same way every time and spend fewer tokens rediscovering them: build a page from a spec, review a PR against the rubrics, audit screenshots, write an ADR, update Linear. Skills are versioned, linted, tested and listed in the character schema.

**Scope**

* In: five skills under `.claude/skills/<name>/` in `paperos-template` (`SKILL.md`, `scripts/`, `templates/`, `references/`), the skill lint, `skills.json`, `docs/agents/skills.md`.
* Out: the authoring skill (PAP-118, follows this format), Scout scan skill (PAP-218), reviewer prompts (PAP-81).

**Spec**

* `SKILL.md`: frontmatter `name`, `description` starting with a verb and containing trigger phrases, `version`, `owner`; body at most 1500 words; deep detail in `references/` loaded on demand.
* `page-from-spec`: read the spec, run PAP-120 scaffold (or manual steps with `TODO(PAP-120)` markers until it lands), implement logic, add stories, run PAP-122 conformance, capture screenshots at the PAP-82 matrix, open PR with PAP-49 template, copy the checklist into the PR body.
* `review-pr`: fetch diff, apply PAP-79 rubrics, emit the review JSON block (PAP-239 `Finding[]`) and the forge review; never approve own PR.
* `screenshot-audit`: inspect the Playwright artifact folder for overflow, truncation, contrast and misalignment; output PAP-84 annotation format; report `no-artifacts` when empty.
* `write-adr`: MADR template from PAP-44 numbered `NNNN-PAP-<key>-title.md`, registers in the decision log.
* `linear-update`: `scripts/comment.ts`, `scripts/state.ts`, `scripts/attach.ts` enforcing the PAP-92 templates, footer validation, dedupe and the 30-minute cadence; falls back to `artifacts/pending-comments/` on rate limit.
* Scripts: TypeScript via `tsx`, config from env (`LINEAR_API_KEY`, `PAPEROS_ISSUE`, `PAPEROS_CHARACTER`), last stdout line is JSON `{ ok, ... }`, exit non-zero on failure.

**Interface contract**

* Provides: `skills.json` (`{ id, version, owner, allowedCharacters[], scripts[] }[]`), `pnpm skills lint`, the `linear-update` CLI contract (`comment --status progress --body file.md`, `state --to "In Review"`, `attach --url`), review JSON writer `writeReviewBlock(findings)`.
* Consumers: PAP-104 prompts reference skills by id; PAP-108 `linear-update` validates handoff blocks; PAP-110 tasks exercise each skill; PAP-118 and PAP-218 follow the format and appear in `skills.json`; PAP-134 (rules and skills registry) indexes it.
* Requires: PAP-103 `skills[]` field; PAP-92 templates; PAP-79 rubric text; PAP-239 finding schema; PAP-82 artifact layout.

**Definition of done**

* Five skills present, lint passes, `skills.json` generated.
* Script tests pass with `nock`-mocked Linear.
* Dry run: a session invokes each skill on a toy repo; transcripts show the skill loaded and steps followed; `linear-update` posts a correctly formatted comment (screenshot).
* `review-pr` dry run on a seeded PR produces a JSON block that validates against PAP-239.
* Docs page; changelog; Linear comment with transcript links.

**Test plan**

* Unit: lint rules (word count, frontmatter, trigger phrase), footer validation, dedupe by body hash, cadence check with fake clock, ADR numbering with key suffix.
* Integration: each script against recorded Linear and forge responses; rate-limit fallback writes the pending file.
* e2e: five dry-run transcripts on the toy repo.
* Visual: the posted Linear comment at 1280 px and in the mobile app at 375 px.

**Demo**

In a toy worktree run `pnpm skill linear-update comment --status progress --body demo.md`, refresh the Linear issue and see the comment with footer; run it again immediately and watch it refuse for the 30-minute rule. One minute.

**Edge cases**

* Character not allowed to use a skill (Beacon on `review-pr`): script checks `PAPEROS_CHARACTER` against `skills.json` and refuses.
* Invalid spec: `page-from-spec` stops and runs validator fix suggestions.
* ADR number collision from parallel sessions: key suffix; reconciled on merge.
* `SKILL.md` grows past 1500 words: lint fails; move to `references/`.
* Screenshot folder missing: `no-artifacts`, never invented findings.

**Dependencies**

Blocked by PAP-103. Blocks PAP-110, PAP-118, PAP-134, PAP-306. Soft: PAP-79, PAP-82, PAP-239, PAP-120.

**Agent**

Built by Quill (lead) for prose and Atlas (Dispatcher) for scripts; reviewed by Sentinel.

**Size**

M
