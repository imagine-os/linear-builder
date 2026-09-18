---
identifier: "PAP-218"
title: "Create the Scout character routine: weekly scan for new libraries relevant to open issues"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Agent"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-216", "PAP-287", "PAP-493"]
blocks: []
key: "libraries/scout-agent"
url: "https://linear.app/paperos/issue/PAP-218/create-the-scout-character-routine-weekly-scan-for-new-libraries"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:34.449Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-218: Create the Scout character routine: weekly scan for new libraries relevant to open issues

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Make discovery continuous: every Monday the Scout character scans for libraries and products relevant to the issues open in Linear, pre-scores them with the rubric and license policy, records candidates in the registry and tells the owning issues, without noise or overspend. Discovery becomes a routine the org runs.

**Scope**

In:

* Skill `.claude/skills/scout-scan/SKILL.md` with `scripts/` (query builder, facts collector reuse, dedupe, report renderer) in the PAP-105 format.
* Workflow `.github/workflows/scout-scan.yml` (Monday 06:00 UTC, plus `workflow_dispatch`) asking PAP-96 to spawn Scout (Library Evaluator) with the skill.
* Report `docs/registry/scans/YYYY-MM-DD.md` rendered by PAP-128; `docs/registry/scans/seen.json` as dedupe memory.
* Linear actions: comments on relevant issues, up to three new Research issues per scan in Backlog, a pinned "Scout scans" issue updated each run.
* Watch list: adopted entries checked for license changes, archival or deprecation.
* Golden task for PAP-110.

Out: adoption decisions (research issues and ADRs), upgrades (PAP-217), the registry itself (PAP-216).

**Spec**

* Inputs: open Backlog and Ready for Claude issues labelled Build or Research (via `linear-update`), `registry.json`, `adr-index.json`, last three reports, `seen.json`.
* Queries: three to five per project, derived from titles and the project's category list; sources npm search, GitHub search (300+ stars, pushed within 12 months), WebSearch at 10 results per query; 60 candidates per run.
* Filtering: drop registry members unless a new major or status change; drop PAP-211 `block` tier; run `lib-facts` for a facts-only pre-score.
* Relevance: each candidate linked to issue keys with a one-sentence rationale, else dropped.
* Actions: `candidate` writes a registry entry via `pnpm lib add --status candidate`; `research` also creates a Backlog Research issue per PAP-93 with a scorecard stub; at most three per run; one comment per issue per run, none within 30 days of a prior mention; format from PAP-108.
* Budget: PAP-111 cap of $15 and 60 turns; on cap the report gets `partial: true` and leftovers become `deferred` in `seen.json`.
* Kill switch: `docs/registry/scout.paused` or the character budget switch.

*Round 4 amendment (2026-09-18):*
Scan sources include MCP servers (npm keyword `mcp`, the official registry when public) and Claude Code skills or plugins relevant to open issues; candidates of those kinds are routed to PAP-210 (catalog entry) and PAP-105 (skills) instead of the library registry, with the same one-comment-per-issue rule.

**Interface contract**

Provides: skill and scripts (`buildQueries(issues, categories)`, `dedupe(candidates, seen)`, `preScore(facts)`, `renderReport(run)`), `ScanReport` schema `{ date, summary, byProject: [{ project, candidates: [{ name, version, license, preScore, linkedIssues, action }] }], watchAlerts, budget, partial }`, `seen.json` schema, the pinned issue, golden task. Consumes: PAP-216 `lib add` and `registry.json`, PAP-104 Scout definition, PAP-105 skill format and `linear-update`, PAP-96 spawn path, PAP-111 budgets, PAP-110 harness, PAP-93 issue template, PAP-211 tiers, PAP-209 `--facts-only`, PAP-108 comment format, PAP-129 logging.

**Definition of done**

* Skill, scripts, workflow, report template and golden task merged; `pnpm agents build` lists the skill for Scout only.
* One real `workflow_dispatch` run against team PAP with a `PAP-SANDBOX` label produced a report, a candidate entry and a comment; links in the PR.
* Golden task scored nightly at or above threshold; no fixture exceeds the action limits.
* Report page screenshots at 375 and 1280 in light and dark; CHANGELOG; comment on the pinned issue.
* Atlas approves action limits; Sentinel confirms Linear scopes are comment and create-in-Backlog only.

**Test plan**

* Vitest: query builder from fixture issues, dedupe against `seen.json` including the 30-day rule, pre-score computation, report rendering snapshot, action limits (three research issues, one comment per issue), partial-run carry-over, kill switch.
* Eval: frozen issue list and mocked search results produce the expected report shape and actions.
* Playwright: report page at 375 and 1280, both themes.

**Demo**

Reviewer dispatches `scout-scan.yml` with the sandbox label, opens the new `docs/registry/scans/<date>.md` page, then finds the registry entry it created and the comment on the linked issue. Under two minutes after the run.

**Edge cases**

* Project without open issues: skipped, noted.
* Search rate-limited or down: partial report, `deferred` list.
* Fork of an adopted library: marked `related`.
* Adopted library changes license: priority 1 Research issue regardless of the cap.
* Duplicate across projects: one entry, multiple linked issues.
* Orchestrator unavailable: visible failure, retry next week; no direct Claude call bypassing PAP-129.

**Dependencies**

PAP-216 and PAP-104 (hard). Soft: PAP-105, PAP-96, PAP-111, PAP-110, PAP-93, PAP-211, PAP-209, PAP-108.

**Agent**

Built by Scout (Library Evaluator) with Atlas (Dispatcher) for the orchestrator hook. Reviewed by Atlas and Sentinel (Security Auditor, Code Reviewer).

**Size**

M: a skill and scripts; the Linear action rules and eval fixture need care.
