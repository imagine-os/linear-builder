---
identifier: "PAP-278"
title: "Commit diff view, pull request pages and Linear trailer links"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer", "Agent"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: "PAP-54"
children: []
blockedBy: ["PAP-277"]
blocks: []
key: "child/PAP-54/23"
url: "https://linear.app/paperos/issue/PAP-278/commit-diff-view-pull-request-pages-and-linear-trailer-links"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:14.826Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-278: Commit diff view, pull request pages and Linear trailer links

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Complete the surface with `/dev/repos/$repo/commit/$sha`, `pulls` and `pulls/$n`: a `DiffView` handling binary, rename and mode changes with horizontal scroll inside the diff at 320, `CommitLink` and `PAP-n` links in the inspector, character avatars for agent commits, and the mocked public demo.

**Scope**

In: three page specs and routes, `DiffView` and `CommitLink` in `@paperos/ui`, inspector panel showing linked Linear issue and spec files touched, docs page `docs/product/in-app-git.md`.

Out: review comments (PAP-131 later), merging.

**Spec**

* Diff parser fixtures for binary, rename, mode change, huge minified line.
* Linear link uses the workspace URL from PAP-91 config.
* Inspector lists `specs/**` files in the diff with links to the spec editor when PAP-124 exists.

**Interface contract**

Provides: `DiffView`, `CommitLink` reusable by PAP-131 and PAP-89; routes. Consumes: procedures (child 1), pages scaffolding (child 2).

**Definition of done**

* Three pages render live and mocked; `Linear:` trailer link works; agent commit shows the character avatar.
* Diff fixtures pass; screenshots at seven widths; docs page and changelog; Linear comment with the Pages demo link.

**Test plan**

* Unit: diff parser fixtures; link builder.
* E2E: Playwright at seven widths; wide diff line at 320 shows no page overflow.
* Visual: light and dark for diff view.

**Demo**

Reviewer opens a commit by "Forge (PaperOS agent)", reads the highlighted diff, clicks the `PAP-n` link in the inspector to reach Linear, then opens the PR list. Under a minute.

**Edge cases**

* Commit without trailer: inspector says no linked issue.
* PR from a bot with hundreds of files: file list virtualised.

**Dependencies**

Children 1 and 2 (hard). Soft: PAP-91, PAP-124.

**Agent**

Built by Forge. Reviewed by Sentinel (Visual Inspector).

**Size**

M
