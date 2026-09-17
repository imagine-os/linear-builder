---
identifier: "PAP-81"
title: "Build gate 2: three Claude reviewer agents (correctness, security, spec-conformance) posting structured PR reviews"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: ["PAP-243", "PAP-244", "PAP-245"]
blockedBy: ["PAP-239", "PAP-78", "PAP-79"]
blocks: ["PAP-241", "PAP-253", "PAP-85", "PAP-88"]
key: "quality/review-agents"
url: "https://linear.app/paperos/issue/PAP-81/build-gate-2-three-claude-reviewer-agents-correctness-security-spec"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-81: Build gate 2: three Claude reviewer agents (correctness, security, spec-conformance) posting structured PR reviews

**Goal**

Build Gate 2: three Claude reviewer agents (correctness, security, spec-conformance) that run on every PR after Gate 1 passes, review against the shared rubrics, post one structured GitHub or Forgejo review each with inline comments, and set commit statuses that block merge on blockers. This replaces the human code review Justin cannot supply.

**Scope**

In:
- `packages/agents/src/review/`: `runReview({ pr, reviewer })` using the Claude Agent SDK (TypeScript) with model `claude-fable-5-1`, tools limited to read-only repo access (`Read`, `Grep`, `Glob`, `Bash` allowlisted to `git diff`, `pnpm test --filter`, `pnpm typecheck`), plus the rubric and spec files.
- Three reviewer definitions in `.claude/agents/reviewers/{correctness,security,spec-conformance}.md` (Sentinel sub-characters) with system prompts embedding the relevant rubric, the finding schema and output rules.
- Inputs assembled per PR: diff, changed files with context, PR body (from `forge/pr-templates`), linked Linear issue text, relevant `page.spec.yaml` files, `gate1.json`, `security.json`, `registry.json`, guidelines `rules.json`.
- Output: findings validated against `finding.schema.ts`, deduped by ID, posted as a single review (event `REQUEST_CHANGES` if S0 or more than 3 S1, else `COMMENT`; agents never `APPROVE`, that is Gate aggregation's job), inline comments for findings with file and line, summary comment using the rubric template.
- Commit statuses `gate/2-correctness`, `gate/2-security`, `gate/2-spec`; aggregate `gate/2-review`.
- Workflow `.github/workflows/review.yml` triggered by `workflow_run` of Gate 1 success and by `pull_request` label `re-review`; runs three reviewers in parallel with a shared cache of the PR context.
- Cost and log capture: tokens and cost per reviewer written to `reports/review-cost.json` and to the prompt log store (`collab/prompt-log-store`, via `agents/prompt-logging-hook` when available).
- Re-review on new commits only reviews the incremental diff but re-validates open findings and resolves fixed ones.

Out: autofix PRs (later), reviewing non-code artifacts, human review UI.

**Spec**

- SDK usage: `query({ prompt, options: { model, systemPrompt, allowedTools, permissionMode: 'bypassPermissions', cwd: worktreePath, maxTurns: 40 } })`; final message must be JSON matching `{ findings: Finding[], rubricCoverage: { [rubricId]: 'checked'|'n/a' }, summary: string }`; parse failures retry once with the error appended.
- Diff over 3,000 changed lines: split by package and review in chunks; over 10,000 lines: post S1 "PR too large, split" and review only specs and security-critical paths.
- Context budget: cap included file content at 150k tokens by prioritising changed files, their tests, referenced specs; log what was omitted.
- Posting via `@octokit/rest` for GitHub and Forgejo's Gitea-compatible API for Forgejo; the same review is posted to whichever forge hosts the PR (primary per `forge/mirror`).
- Findings with `confidence < 0.5` become `question` comments; `autofixable: true` findings include a `suggestion` diff block.
- Idempotency: existing review comments carrying the finding ID in a hidden HTML comment are updated, not duplicated; resolved findings get a reply "Resolved in <sha>".
- Time budget: each reviewer under 6 minutes; total gate under 10 minutes; timeouts produce an S1 "review incomplete" finding rather than a silent pass.
- Calibration: `pnpm review:calibrate` runs each reviewer over `docs/quality/rubrics/calibration/` and reports agreement; threshold 0.8 recorded in `agents/eval-harness` later.

**Definition of done**

- Three reviewers run on a real PR and post structured reviews with inline comments and statuses (links).
- Seeded PR with an authz bug, a null-handling bug and a missing empty state: each reviewer catches its case at S0/S1; a clean PR yields `COMMENT` with zero blockers.
- Calibration agreement at or above 0.8 for all three reviewers on the 15-case set.
- Re-push resolves fixed findings and does not duplicate comments (evidence screenshot).
- Cost per PR review reported in the summary and under $6 average across 10 PRs.
- `docs/quality/review-agents.md` (how to read, how to re-run, how to waive); CHANGELOG entry; Linear comment with example review links and cost table.

**Edge cases**

- PR body missing the Linear link: spec-conformance posts S1 and proceeds with the spec files it can infer from changed routes.
- Agent tries to write files or run network commands: tool allowlist denies; the attempt is logged as an S2 agent-behaviour finding.
- Rate limits or API outage: exponential backoff, then status `error` with a retry label, never green.
- Reviewer contradicts Gate 1 (claims tests fail when they pass): findings citing test results must include the command output as evidence or are downgraded.
- Binary or generated files in diff: skipped with a note; generated drift is Gate 1's job.
- Agent's own PR (Sentinel fixing rubrics): still reviewed; self-review is fine because the reviewer sessions are separate.

**Dependencies**

`quality/ci-gate1` and `quality/review-rubrics` (hard). Soft: `forge/pr-templates`, `forge/bot-accounts` (posting identity), `quality/security-scans` (input), `spec-builder/validator`, `design-system/guidelines-docs` (`rules.json`), `collab/prompt-log-store`. Consumed by `quality/edge-case-hunter`, `quality/release-train`, `agents/eval-harness`.

**Agent**

Built by Sentinel (Code Reviewer and Security Auditor sub-agents define their own prompts) with Atlas providing the SDK harness pattern shared with `pm-linear/orchestrator`. Reviewed by Atlas and Forge; Quill checks the spec-conformance prompt.

**Size**

L: three prompts, an SDK harness, forge posting for two APIs, idempotent re-review and calibration.
