---
identifier: "PAP-44"
title: "Write ADR: keep Git as the format, self-host Forgejo, mirror GitHub, defer any custom VCS"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Forgejo live and mirrored"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: []
key: "forge/vcs-decision-adr"
url: "https://linear.app/paperos/issue/PAP-44/write-adr-keep-git-as-the-format-self-host-forgejo-mirror-github-defer"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-44: Write ADR: keep Git as the format, self-host Forgejo, mirror GitHub, defer any custom VCS

**Goal**

Record, as an Architecture Decision Record, why PaperOS keeps Git as its storage format, self-hosts Forgejo as the primary forge, mirrors to the GitHub org imagine-os, and defers any custom version control system. The ADR must be concrete enough that a future agent can tell whether the conditions that would reopen the decision have been met, and it becomes the reference every forge issue links to.

**Scope**

- In: the ADR document, a comparison table of alternatives, explicit reopen criteria, and a one-paragraph summary for the Linear project description.
- In: registering the ADR in the decision log index (`docs/decisions/README.md`).
- Out: any implementation work (covered by forge/forgejo-deploy and forge/mirror).
- Out: choosing the CI runner or backup tooling; those get their own ADR notes inside their issues.

**Spec**

Create `docs/decisions/ADR-0001-version-control-and-forge.md` in the `imagine-os/paperos-template` repo (create `docs/decisions/` if absent). Use MADR 4 structure with these headings in order: Status (Accepted, date 2026-09-17, deciders: Atlas, Forge, Justin), Context, Decision, Alternatives Considered, Consequences, Reopen Criteria, Links.

Alternatives Considered must be a table with rows for: (a) GitHub only; (b) self-hosted GitLab CE; (c) Gitea; (d) Forgejo; (e) Jujutsu (jj) on a Git backend; (f) Pijul as a new format; (g) a from-scratch PaperOS VCS. Columns: agent tooling compatibility (Claude Code, gh CLI, Actions), self-host cost (RAM, disk, ops hours/week), migration effort in days, license (note GitLab CE is MIT but EE features are proprietary; Forgejo is GPLv3+ since v9), risk of vendor capture, and a 1-5 score using the rubric from libraries/eval-rubric if it has landed, otherwise state the six criteria inline.

Decision section states: Git remains the format; Forgejo (pin the current stable major) is the primary forge; GitHub is a mirror and public front door; Forgejo Actions is the CI fallback; a custom VCS is deferred. Consequences lists at least five, including "every agent must push to Forgejo first" and "GitHub-only features (Copilot review, Dependabot) are conveniences, not dependencies".

Reopen Criteria must be measurable: mirror drift incidents exceeding 2 per week for a month; Forgejo unable to sustain 50 concurrent agent pushes per minute in forge/dr-drill load checks; a semantic or spec-aware merge requirement that Git cannot express and that blocks more than 3 issues; or Forgejo losing its OSS governance. Add a Links section pointing to forge/forgejo-deploy, forge/mirror, forge/dr-drill and the Linear project.

Also add a 120-word summary to `docs/decisions/README.md` under a table (ID, title, status, date).

**Definition of done**

- ADR file exists at the path above, passes `pnpm biome check` for markdown formatting, and renders in GitHub preview without broken tables.
- Comparison table has all seven alternatives with every column filled; no "TBD".
- Reopen criteria are all numerically testable.
- `docs/decisions/README.md` index row added.
- PR opened using the forge/pr-templates template (or the interim template if that issue has not merged), linked to this Linear issue.
- Sentinel's Code Reviewer sub-agent approves; Quill reviews wording.
- Linear comment posted with the rendered ADR link on GitHub and a three-line summary.
- Changelog entry under "Docs" in the PR summary.

**Edge cases**

- libraries/eval-rubric has not merged: write the six criteria inline and add a TODO link to the rubric issue rather than blocking.
- `docs/decisions/` already contains an ADR-0001 from collab/decision-log: take the next free number and update the index accordingly.
- Forgejo licence changes mid-build: the ADR must record the version and licence checked.
- Justin disagrees with deferring a custom VCS: the ADR Status becomes "Proposed" and the issue moves to Needs Justin with the table as the decision aid.
- Reviewer cannot verify a cost figure: cite a source URL in a footnote; unsourced numbers are a review blocker.

**Dependencies**

- None blocking. Soft references: libraries/eval-rubric (criteria), collab/decision-log (ADR index format), forge/forgejo-deploy and forge/mirror (consumers of this decision).

**Agent**

- Builds: Forge (lead), drafting personally rather than via a sub-agent because it is a decision document.
- Reviews: Sentinel (Code Reviewer sub-agent) for structure and testability; Quill for prose and index placement.

**Size**

S: a single document with a bounded comparison table and no code.
