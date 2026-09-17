---
identifier: "PAP-49"
title: "Author PR template linking Linear issue, page spec, screenshots and the review-gate checklist"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Docs"
priority: 2
surfaces: ["Developer", "Agent"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-46"]
blocks: []
key: "forge/pr-templates"
url: "https://linear.app/paperos/issue/PAP-49/author-pr-template-linking-linear-issue-page-spec-screenshots-and-the"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-49: Author PR template linking Linear issue, page spec, screenshots and the review-gate checklist

**Goal**

Every pull request opened by an agent or a human carries the same structure: the Linear issue, the page specs touched, a summary, the screenshot matrix, the test plan, the review-gate checklist, risk and rollback. Reviewer agents and Justin then always know where to look, and a lint step rejects PRs missing the essentials.

**Scope**

- In: PR template files for both forges, a generator script that pre-fills the template from Linear, a lightweight CI check that validates the body, and guidance in the session playbook.
- Out: the reviewer agents themselves (quality/review-agents) and screenshot capture (quality/playwright-matrix); this issue only reserves the sections they fill.

**Spec**

In `imagine-os/paperos-template`:

- `.github/PULL_REQUEST_TEMPLATE.md` and an identical `.forgejo/PULL_REQUEST_TEMPLATE.md` (Forgejo also honours `.gitea/`; keep one source and copy via `scripts/sync-templates.ts` so they never diverge; a test asserts byte equality).
- Template sections, in order, each a level-2 heading with an HTML comment explaining what to put there (comments are the only HTML permitted):
  1. `Linear` - `Closes PAP-<n>` line plus the issue title.
  2. `Specs` - list of `specs/**/page.spec.yaml` files added or changed, or the literal `No spec changes (infra/docs)`.
  3. `Summary` - three to six bullets, plain language for Justin.
  4. `Screenshots` - a table with rows for the seven widths from app-shell/device-matrix-research (placeholders `320`, `375`, `768`, `1024`, `1280`, `1536`, `1920` until that issue lands) and columns light/dark; Gate 3 replaces placeholders with image links.
  5. `Test plan` - commands run and their results.
  6. `Review gates` - checkboxes: Gate 1 static, Gate 2 correctness, Gate 2 security, Gate 2 spec conformance, Gate 3 visual, Gate 4 edge cases; bots tick these via the checks API, agents must not tick them by hand.
  7. `Risk and rollback` - one of `low/medium/high` with a sentence and the revert command.
  8. `Character` - who built it and which sub-agents were used.
- Generator `scripts/pr-body.ts --issue PAP-<n> [--specs auto]`: fetches the issue title and description from Linear GraphQL (token from env `LINEAR_API_KEY`), detects changed spec files via `git diff --name-only origin/main...HEAD`, and prints a filled body to stdout; the session playbook (pm-linear/session-playbook) tells sessions to pipe it into `gh pr create --body-file -` or the Forgejo `tea` CLI.
- CI check `pr-lint` (`.github/workflows/pr-lint.yml`, `.forgejo/workflows/pr-lint.yml`): fails when the body lacks a `PAP-\d+` reference, the Specs section is empty, or a `Review gates` checkbox has been ticked by a non-bot author (compare body author with a bot list from forge/bot-accounts). Runs in under 20 seconds, node 22, no external deps beyond `@actions/github`.

**Definition of done**

- Both template files exist and are byte-identical (test).
- `pnpm tsx scripts/pr-body.ts --issue PAP-5` produces a valid body with the issue title (recorded output in PR).
- `pr-lint` fails a PR with no Linear key and passes one that complies (two demo PRs linked).
- Template referenced from `docs/engineering/branch-policy.md` and `CLAUDE.md`.
- Sentinel Code Reviewer approves; Quill reviews wording of the HTML comments.
- Screenshot of a rendered PR on GitHub and on Forgejo at 1280 width attached.
- Linear comment with the demo PR links; changelog entry under "Docs".

**Edge cases**

- Issue not found in Linear (typo): generator exits 2 with the key and a hint; does not print a partial body.
- PR closes several issues: multiple `Closes` lines allowed; lint accepts one or more.
- Docs-only PR with no screenshots: the Screenshots table may be replaced by `Not applicable (no UI change)`, and lint accepts that exact phrase.
- Forgejo renders task lists differently from GitHub: verify the checkbox syntax `- [ ]` renders on both; screenshot proves it.
- Body over 65 536 characters (GitHub limit) from long test output: generator truncates the Test plan section with a link to the CI run.

**Dependencies**

- forge/branch-policy (defines commit and PR conventions the template references). Soft: app-shell/device-matrix-research (final width list), forge/bot-accounts (bot author list), pm-linear/session-playbook (usage instructions).

**Agent**

- Builds: Quill (Changelog Scribe sub-agent) for the template wording; Forge writes `pr-body.ts` and the lint workflow.
- Reviews: Sentinel (Code Reviewer) plus Atlas for fit with the orchestrator flow.

**Size**

S: templates and a short script, with two demonstration PRs as evidence.
