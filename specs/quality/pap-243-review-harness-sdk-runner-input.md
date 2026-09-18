---
identifier: "PAP-243"
title: "Review harness: SDK runner, input assembly, finding validation and posting"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: "PAP-81"
children: []
blockedBy: ["PAP-78", "PAP-79", "PAP-239", "PAP-678", "PAP-704"]
blocks: ["PAP-84", "PAP-85", "PAP-244", "PAP-245", "PAP-249", "PAP-464", "PAP-677", "PAP-679", "PAP-685"]
key: "quality/review-agents/harness"
url: "https://linear.app/paperos/issue/PAP-243/review-harness-sdk-runner-input-assembly-finding-validation-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:29.821Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-243: Review harness: SDK runner, input assembly, finding validation and posting

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Build the engine the three reviewers run on: a Claude Agent SDK runner with read-only tools, PR context assembly under a token budget, finding validation against `packages/contracts`, idempotent posting to GitHub and Forgejo, and cost capture.

**Scope**

* In: `packages/agents/src/review/runReview()`, context assembler, `postReview()` for both forges, status setter, cost and prompt-log capture, `review.yml` workflow skeleton, re-review incremental mode.
* Out: reviewer prompts (siblings), rubrics (PAP-79).

**Spec**

* `runReview({ pr, reviewer, cwd }) => GateReport<'review'>` using `query({ prompt, options: { model: 'claude-fable-5-1', systemPrompt, allowedTools: ['Read','Grep','Glob','Bash'], permissionMode: 'bypassPermissions', cwd, maxTurns: 40 } })` with Bash allowlisted to `git diff`, `pnpm test --filter`, `pnpm typecheck`; final message must parse as `{ findings, rubricCoverage, summary }`, one retry with the parse error appended.
* Context: diff, changed files with 40 lines of context, PR body, Linear issue text, referenced `page.spec.yaml`, `gate1.json`, `security.json`, `registry.json`, `rules.json`; cap 150k tokens, priority order documented, omissions logged; over 3 000 changed lines split by package; over 10 000 post S1 "PR too large".
* Posting: `@octokit/rest` and the Gitea-compatible API; one review per reviewer, event `REQUEST_CHANGES` if any S0 or more than 3 S1 else `COMMENT`; inline comments carry `<!-- finding:<id> -->`; re-runs update in place; resolved findings get "Resolved in <sha>".
* Statuses via contracts `GATE_STATUSES`; cost to `reports/review-cost.json` and the prompt log hook (PAP-107) when present.

*Round 4 amendment (2026-09-18):*

* Reviewer model routing (round 4, cost doc section 4b): `runReview()` does not hard-code `claude-fable-5-1`. It reads the PR's issue `Model` label through `linear.ids`: after an Opus 5 or Fable 5.1 builder the reviewer runs Opus 5 at `effort: high`; after a Sonnet 5 builder it runs Sonnet 5 at `high`; the QA gate summariser runs Haiku 4.5 at `low`; the four release-candidate reviews (PAP-254) run Fable 5.1 at `high`. The chosen model and effort are written into `review-cost.json` and the review footer so PAP-98 prices the run correctly.

**Interface contract**

* Provides: `runReview()`, `assembleContext()`, `postReview()`, `ReviewerDefinition` type `{ name, promptPath, rubricIds, statusName }`, workflow `review.yml`.
* Requires: `packages/contracts` (Finding, GateReport, statuses), PAP-78 `gate1.json` and `workflow_run` trigger, PAP-48 bot identities, PAP-49 PR template fields.
* Consumers: sibling reviewers, PAP-84 (reuses runner with image input), PAP-85, PAP-110.

**Definition of done**

* Runner executes a stub reviewer on a real PR and posts a review with one inline comment and a status (links).
* Re-push updates the same comment and resolves a fixed finding (screenshot).
* Tool allowlist test: a prompt that tries `curl` is denied and logged as an S2 agent-behaviour finding.
* Context budget test: a 200-file PR logs omitted files and stays under 150k tokens.
* Posting works on Forgejo dev instance (link).

**Test plan**

* Unit: context prioritisation, JSON parse retry, event selection rules, comment idempotency keys.
* Integration: mocked SDK stream to end-to-end post on a sandbox repo.
* Cost: 10 stub runs under $0.50 each.

**Demo**

`pnpm review:run --pr 12 --reviewer stub` against the sandbox repo, then open the PR: one review, one inline comment, `gate/2-review` status. Under two minutes.

**Edge cases**

* API outage: backoff then `status: error`, never green.
* Binary files in diff: skipped with a note.
* PR from a fork without secrets: review skipped with a comment.

**Dependencies**

PAP-78, PAP-79, `packages/contracts` (hard). Blocks the two sibling children.

**Agent**

Built by Sentinel with Atlas (SDK harness pattern shared with PAP-96). Reviewed by Forge.

**Size**

M.
