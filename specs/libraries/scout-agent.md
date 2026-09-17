---
identifier: "PAP-218"
title: "Create the Scout character routine: weekly scan for new libraries relevant to open issues"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Agent"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-216"]
blocks: []
key: "libraries/scout-agent"
url: "https://linear.app/paperos/issue/PAP-218/create-the-scout-character-routine-weekly-scan-for-new-libraries"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-218: Create the Scout character routine: weekly scan for new libraries relevant to open issues

**Goal**

Make discovery continuous: every Monday the Scout character scans for libraries and products relevant to the issues currently open in Linear, pre-scores them with the rubric and license policy, records candidates in the registry and tells the owning issues, without creating noise or spending more than its budget. Discovery becomes a routine the org runs, not a thing someone remembers to do.

**Scope**

In:
- Skill `.claude/skills/scout-scan/SKILL.md` with `scripts/` (query builder, facts collector reuse, dedupe, report renderer) in the `agents/skills-library` format.
- Scheduled workflow `.github/workflows/scout-scan.yml` (Monday 06:00 UTC, also `workflow_dispatch`) that asks the orchestrator (`pm-linear/orchestrator`) to spawn Scout (Library Evaluator) with the skill.
- Scan report `docs/registry/scans/YYYY-MM-DD.md` rendered by the docs engine, and `docs/registry/scans/seen.json` as dedupe memory.
- Linear actions: comments on relevant issues, up to three new Research issues per scan in Backlog, and a pinned "Scout scans" issue updated with each summary.
- Watch list: adopted registry entries checked for license changes, archival, or deprecation notices.
- Golden task for `agents/eval-harness`.

Out: making adoption decisions (research issues and ADRs do that), upgrading versions (`libraries/upgrade-bot`), building the registry (`libraries/registry`).

**Spec**

- Inputs each run: open Linear issues in Backlog and Ready for Claude with labels Build or Research (Linear API via the `linear-update` skill script), `registry.json`, `adr-index.json`, previous three scan reports and `seen.json`.
- Query building: per project with open issues, derive three to five queries from issue titles and the project's category list (for example `tables` -> "react virtualized grid", "formula engine typescript"); sources are npm search, GitHub search (stars over 300, pushed within 12 months), and WebSearch limited to 10 results per query; total candidates capped at 60 per run.
- Filtering: drop anything already in the registry unless a new major version or a status-relevant change appeared; drop license-policy `block` tier; run `scripts/lib-facts.ts` for the rest and compute a facts-only pre-score (maintenance, license, bundle size, TypeScript quality; a11y and agent-friendliness left `unknown`).
- Relevance: each surviving candidate is linked to specific issue keys with a one-sentence rationale; candidates without a linked issue are dropped.
- Report sections: summary line, new candidates per project (name, version, license, pre-score, linked issues, recommended action `ignore|candidate|research`), watch-list alerts, budget used. Actions: `candidate` writes a registry entry with `status: candidate` via `pnpm lib add`; `research` additionally creates a Linear Research issue in Backlog using the `pm-linear/issue-contract` template with the scorecard stub attached; at most three research issues per run.
- Commenting rules: at most one comment per issue per run, none if the same candidate was mentioned in the last 30 days (`seen.json`), comment format from `agents/handoffs`.
- Budget: `agents/cost-controls` cap of $15 and 60 turns per run; on hitting the cap the report is written with a `partial: true` flag and the remaining candidates are carried to `seen.json` as `deferred`.
- Kill switch: a `scout.paused` file in `docs/registry/` or the character budget switch stops the run with a comment on the pinned issue.

**Definition of done**

- Skill, scripts, workflow, report template and golden task merged; `pnpm agents build` lists the skill for Scout only.
- Vitest: query builder from fixture issues, dedupe against `seen.json`, pre-score computation, report rendering snapshot, action limits (three research issues, one comment per issue).
- Golden task in `agents/eval-harness`: frozen issue list and mocked search results produce a report matching the expected shape and actions; scored nightly.
- One real dispatch run against Linear team PAP with a `PAP-SANDBOX` label produced a report, a candidate entry and a comment; links in the PR.
- Scan report page screenshot at 375 and 1280 in the docs engine; CHANGELOG entry; Linear comment on the pinned "Scout scans" issue.
- Atlas approves the action limits; Sentinel confirms Linear scopes are comment and create-in-Backlog only.

**Edge cases**

- No open issues in a project: skip it; report says so.
- Search API rate-limited or down: partial report, `deferred` list, no failure email storms.
- Candidate is a fork of an adopted library: mark `related` to the adopted entry rather than a new candidate.
- Adopted library changes license (watch list): create a Research issue with priority 1 regardless of the three-issue cap and mention `libraries/license-policy`.
- Duplicate candidates across projects: one registry entry, multiple linked issues.
- Orchestrator unavailable: workflow fails visibly and retries next week; no direct Claude call bypassing logging (`agents/prompt-logging-hook`).

**Dependencies**

`libraries/registry` (hard: candidate entries), `agents/roster-v1` (hard: Scout character definition). Soft: `agents/skills-library` (skill format, `linear-update`), `pm-linear/orchestrator` (spawn path), `agents/cost-controls`, `agents/eval-harness`, `pm-linear/issue-contract`, `libraries/license-policy`, `libraries/eval-rubric`.

**Agent**

Built by Scout (Library Evaluator) with Atlas (Dispatcher) for the orchestrator hook. Reviewed by Atlas and Sentinel (Security Auditor for Linear scopes, Code Reviewer).

**Size**

M: mostly a skill and scripts, but the Linear action rules and eval fixture need care to avoid noise.
