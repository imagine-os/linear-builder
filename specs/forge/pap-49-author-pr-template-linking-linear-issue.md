---
identifier: "PAP-49"
title: "Author PR template linking Linear issue, page spec, screenshots and the review-gate checklist"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Docs"
priority: 2
surfaces: ["Agent", "Developer"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-46"]
blocks: []
key: "forge/pr-templates"
url: "https://linear.app/paperos/issue/PAP-49/author-pr-template-linking-linear-issue-page-spec-screenshots-and-the"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:42.663Z"
---

# PAP-49: Author PR template linking Linear issue, page spec, screenshots and the review-gate checklist

**Goal**

Every PR opened by an agent or human carries the same structure: Linear issue, specs touched, summary, screenshot matrix, test plan, review-gate checklist, risk and rollback. Reviewer agents and Justin always know where to look, and a lint rejects PRs missing the essentials.

**Scope**

In:

* Template files for both forges kept byte-identical by `scripts/sync-templates.ts`; generator `scripts/pr-body.ts --issue PAP-n`; CI check `pr-lint`; guidance in PAP-93.

Out: reviewer agents (PAP-81), screenshot capture (PAP-82); this reserves their sections.

**Spec**

* `.github/PULL_REQUEST_TEMPLATE.md` and `.forgejo/PULL_REQUEST_TEMPLATE.md`; sections as level-2 headings with an HTML comment each: Linear (`Closes PAP-<n>` plus title); Specs (files or `No spec changes (infra/docs)`); Summary (three to six plain bullets); Screenshots (seven widths from PAP-14 by light and dark, or `Not applicable (no UI change)`); Test plan (commands and results); Review gates (checkboxes for Gate 1 static, Gate 2 correctness, security, spec conformance, Gate 3 visual, Gate 4 edge cases, ticked only by bots via the checks API); Risk and rollback; Interface changes (new: any change to a contract listed in an issue's Interface contract section).
* `pr-body.ts` fills Linear and Specs from the Linear API and `git diff --name-only`.
* `pr-lint` (GitHub Action and Forgejo workflow) fails on missing Linear key, missing required headings, or hand-ticked gate boxes.

**Interface contract**

Provides:

* Heading names and order as the parsing contract for PAP-81 (posts findings under Review gates), PAP-82 (fills Screenshots), PAP-89 (review report reads Summary and Test plan), PAP-97 (reads `Closes` lines), PAP-133 (reads Summary for changelog).
* Sentinel phrases `Not applicable (no UI change)` and `No spec changes (infra/docs)` accepted by lint.
* `scripts/pr-body.ts` CLI used by PAP-93 and PAP-96 when opening PRs.
* Check name `pr-lint` required by PAP-46 rulesets.

Consumes: commit and PR conventions (PAP-46), widths (PAP-14), bot author list (PAP-48, soft).

**Definition of done**

* Both template files byte-identical (test).
* `pr-body.ts --issue PAP-5` produces a valid body with the issue title (output in PR).
* `pr-lint` fails a PR without a Linear key and passes a compliant one (two demo PRs linked).
* Template referenced from `docs/engineering/branch-policy.md` and `CLAUDE.md`.
* Sentinel approves; Quill reviews the comments; rendered screenshots on GitHub and Forgejo at 1280; Linear comment; changelog under Docs.

**Test plan**

* Unit: `sync-templates.ts` equality; `pr-body.ts` with a mocked Linear response and a fixture diff; lint parser fixtures (missing key, multiple `Closes`, hand-ticked gate, docs-only phrase).
* Integration: two demo PRs on the fixture repo, one failing and one passing `pr-lint` on both forges.
* Visual: rendered PR screenshots on GitHub and Forgejo at 1280 showing task lists render.

**Demo**

Reviewer runs `pnpm tsx scripts/pr-body.ts --issue PAP-13 | head -40`, opens the passing demo PR on GitHub and the same PR mirrored on Forgejo, and compares the rendered checklists. Under a minute.

**Edge cases**

* Unknown issue key: exit 2 with a hint, no partial body.
* PR closing several issues: multiple `Closes` lines accepted.
* Docs-only PR: Screenshots replaced by the sentinel phrase.
* Forgejo task-list rendering verified by screenshot.
* Body over 65,536 characters: Test plan truncated with a CI link.

**Dependencies**

PAP-46 (hard). Soft: PAP-14, PAP-48, PAP-93.

**Agent**

Built by Quill (Changelog Scribe) for the template, Forge for scripts. Reviewed by Sentinel (Code Reviewer).

**Size**

S: two templates, two small scripts.
