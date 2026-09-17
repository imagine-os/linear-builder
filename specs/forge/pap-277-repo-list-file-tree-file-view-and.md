---
identifier: "PAP-277"
title: "Repo list, file tree, file view and commit-list pages with specs"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Agent", "Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: "PAP-54"
children: []
blockedBy: ["PAP-16", "PAP-276"]
blocks: ["PAP-278"]
key: "child/PAP-54/22"
url: "https://linear.app/paperos/issue/PAP-277/repo-list-file-tree-file-view-and-commit-list-pages-with-specs"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:23:19.632Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-277: Repo list, file tree, file view and commit-list pages with specs

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Add specs and routes `/dev/repos`, `/dev/repos/$repo`, `tree/$ref/$path` and `commits/$ref` using PAP-16 slots (sidebar repo and branch picker, main content, inspector linked issue and spec panel), lazily loading one directory per request and highlighting files with `shiki`.

**Scope**

In: four page specs with `access: { audiences: [developer, agent] }`, routes, components `RepoPicker`, `FileTree`, `FileView`, `CommitList`, mocked fixture for the Pages demo.

Out: diff and PR pages (child 3).

**Spec**

* Tree loads one directory per request; breadcrumbs.
* Ref with slashes via splat route with safe encoding.
* `EmptyState` with retry when the backend is unavailable.

**Interface contract**

Provides: routes, components in `@paperos/ui`, specs passing PAP-118. Consumes: procedures (child 1), slots (PAP-16), `EmptyState` and avatars (PAP-71).

**Definition of done**

* Four pages render against live Forgejo and against the mock on Pages; screenshots at seven widths light and dark.
* Specs validate; conformance tests generated; Lighthouse above 85 on the commits page at 1280.

**Test plan**

* Unit: breadcrumb and ref encoding.
* E2E: Playwright with mocked data at seven widths; ref `release/2026-09-25`; Forgejo-down state.
* Performance: Lighthouse on commits page.

**Demo**

Reviewer opens `/dev/repos`, picks `paperos-template`, browses to `packages/core/src/index.ts`, then opens the commit list on `main`. Under a minute.

**Edge cases**

* 50,000 files: lazy directories.
* Binary file view: size and download link only.

**Dependencies**

Child 1, PAP-16 (hard). Soft: PAP-71, PAP-118. Blocks child 3.

**Agent**

Built by Forge with Nova's Views team advising. Reviewed by Sentinel (Visual Inspector).

**Size**

M
