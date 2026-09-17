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
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:41.509Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-44: Write ADR: keep Git as the format, self-host Forgejo, mirror GitHub, defer any custom VCS

**Goal**

Record as an ADR why PaperOS keeps Git as its storage format, self-hosts Forgejo as the primary forge, mirrors to the GitHub org imagine-os and defers any custom VCS. It must be concrete enough that a future agent can tell whether the reopen conditions are met, and it is the reference every forge issue links to.

**Scope**

In:

* `docs/decisions/ADR-0001-version-control-and-forge.md` in `imagine-os/paperos-template` (MADR 4), a comparison table, numerically testable reopen criteria, a one-paragraph summary for the project description.
* Index row in `docs/decisions/README.md`.

Out: implementation (PAP-45, PAP-47), CI runner and backup tool choices (their own issues).

**Spec**

* Headings in order: Status (Accepted, 2026-09-17, deciders Atlas, Forge, Justin), Context, Decision, Alternatives Considered, Consequences, Reopen Criteria, Links.
* Alternatives table rows: GitHub only; GitLab CE; Gitea; Forgejo; Jujutsu on a Git backend; Pijul; from-scratch PaperOS VCS. Columns: agent tooling compatibility, self-host cost (RAM, disk, ops hours per week), migration effort in days, licence (Forgejo GPLv3+ since v9; GitLab CE MIT with proprietary EE), vendor-capture risk, 1-5 score using PAP-210's rubric or the six criteria inline.
* Decision: Git stays the format; Forgejo (pinned stable major) is primary; GitHub is mirror and public front door; Forgejo Actions is the CI fallback; custom VCS deferred.
* Consequences: at least five, including "every repo exists twice and drift is monitored" (PAP-47) and "agents authenticate with bot identities on both forges" (PAP-48).
* Reopen criteria, each measurable: for example monthly forge ops above 4 hours, Forgejo licence change, GitHub outage above 24 h in a quarter, a Git-format limitation blocking a spec-builder feature.

**Interface contract**

Provides:

* The ADR path and number that PAP-45, PAP-47, PAP-50, PAP-53 and the project description link to.
* Decision-log index format (`docs/decisions/README.md` table: number, title, status, date) that PAP-130 adopts.
* A `Reopen Criteria` block with a checklist that PAP-88's release digest can quote when a criterion trips.

Consumes: PAP-210 rubric if merged; otherwise the six criteria are stated inline with a TODO link.

**Definition of done**

* ADR at the path above passes `pnpm biome check` and renders on GitHub without broken tables.
* Seven alternatives, every column filled, no "TBD"; every cost figure has a source footnote.
* Reopen criteria all numeric.
* Index row added; PR uses the PAP-49 template or the interim one.
* Sentinel (Code Reviewer) approves; Quill reviews wording.
* Linear comment with the rendered ADR link and a three-line summary; changelog entry under Docs.

**Test plan**

* Static: `biome check` on Markdown; a small `scripts/adr-lint.ts` asserts the seven headings exist in order and the table has seven rows and six columns.
* Review: Sentinel verifies each source URL resolves; Quill checks the summary paragraph is under 120 words.
* Visual: GitHub render screenshot at 1280 showing the table intact.

**Demo**

Reviewer opens the ADR on GitHub, scrolls the alternatives table, reads the five consequences and the reopen checklist, then opens `docs/decisions/README.md` to see the index row. Under a minute.

**Edge cases**

* Rubric not merged: six criteria inline plus TODO.
* ADR-0001 already taken by PAP-130: use the next number and update the index.
* Licence changes mid-build: record version and licence checked.
* Justin disagrees with deferring a custom VCS: Status becomes Proposed and the issue moves to Needs Justin with the table as the decision aid.

**Dependencies**

None; ready now. Soft: PAP-210, PAP-130. Consumers: PAP-45, PAP-47, PAP-50, PAP-53.

**Agent**

Drafted by Forge (lead) personally. Reviewed by Sentinel (Code Reviewer) and Quill.

**Size**

S: one document with a sourced table.
