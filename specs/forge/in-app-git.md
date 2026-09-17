---
identifier: "PAP-54"
title: "Expose repo browsing, diffs and commit history inside PaperOS via the Forgejo API"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: ["PAP-276", "PAP-278", "PAP-277"]
blockedBy: ["PAP-16", "PAP-275", "PAP-45"]
blocks: []
key: "forge/in-app-git"
url: "https://linear.app/paperos/issue/PAP-54/expose-repo-browsing-diffs-and-commit-history-inside-paperos-via-the"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-54: Expose repo browsing, diffs and commit history inside PaperOS via the Forgejo API

**Goal**

Let developers and agents browse repositories, commit history, diffs and pull requests inside PaperOS, next to the specs and Linear issues those commits reference, using the Forgejo API as the backend. This is the first surface where code history becomes a first-class product object rather than an external tab.

**Scope**

- In: page specs and routes for repo list, file tree and file view, commit list and commit diff, PR list and PR detail; a server-side proxy to Forgejo with permission checks; syntax highlighting; links from commits to Linear issues and spec files; read-only.
- Out: editing files, merging PRs, code review comments (collab/comments may anchor to diffs later), and GitHub as a data source (Forgejo is the primary; mirrored content is identical).

**Spec**

In `imagine-os/paperos-template`:

- Specs: `specs/pages/dev/repos.spec.yaml`, `dev/repo.spec.yaml`, `dev/repo-file.spec.yaml`, `dev/repo-commits.spec.yaml`, `dev/repo-commit.spec.yaml`, `dev/repo-pulls.spec.yaml`, `dev/repo-pull.spec.yaml`, each with `access: { audiences: [developer, agent] }` in the format from spec-builder/access-section (if unmerged, use the draft shape and flag it).
- Routes (TanStack Router, apps/web): `/dev/repos`, `/dev/repos/$repo`, `/dev/repos/$repo/tree/$ref/$path`, `/dev/repos/$repo/commits/$ref`, `/dev/repos/$repo/commit/$sha`, `/dev/repos/$repo/pulls`, `/dev/repos/$repo/pulls/$n`. Layout slots from app-shell/router-layouts: sidebar = repo and branch picker, main = content, inspector = linked issue and spec panel.
- Backend: `packages/forge-client` wrapping the Forgejo API (reuse the generated client from forge/repo-bootstrap) and oRPC procedures in `apps/api/src/routes/forge.ts` (data-layer/api-layer): `repos.list`, `repos.tree`, `repos.file`, `repos.commits`, `repos.commit`, `pulls.list`, `pulls.get`. The server holds a read-only Forgejo token from forge/bot-accounts (`bot-scout` class scope); every procedure calls `can(actor, 'forge.read', { repo })` from identity/rbac-abac and filters private repos by the actor's membership. Responses cached 30 s in memory keyed by ref; commit and blob responses cached indefinitely by SHA.
- Components (packages/ui consumers): `RepoList`, `FileTree` (virtualised, lazy-loaded directories), `CodeView` using `shiki` with the design-system token theme, `DiffView` rendering unified and side-by-side from the Forgejo `.diff` endpoint parsed with `parse-diff`, `CommitList` with author avatar mapped through `.mailmap` so agent commits show the character avatar, `PullRequestHeader` showing gate check statuses from the Forgejo commit status API.
- Linking: commit trailers `Linear: PAP-<n>` become links to Linear and to the in-app PM view when pm-linear/pm-data-model exists; changed `specs/**/*.spec.yaml` paths link to the spec editor (spec-builder/spec-editor-ui) or raw file view if that has not shipped.
- Performance: file view refuses files over 2 MB with a download link; diffs over 3000 lines collapse per file.

**Definition of done**

- All seven pages render against the live Forgejo with real repos; Playwright screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark attached.
- Permission test: a customer-audience principal receives 403 on every `forge.*` procedure; a developer sees only repos they may read (Vitest integration tests).
- Commit with a `Linear:` trailer shows a working link; agent commits show the character avatar.
- Diff view handles binary files, renames and mode changes without crashing (fixture tests).
- Specs pass `spec validate` (spec-builder/validator); conformance tests generated.
- Lighthouse performance on `/dev/repos/$repo/commits/main` above 85 at 1280.
- Docs page `docs/product/in-app-git.md`; changelog entry under "Developer".
- Linear comment with the GitHub Pages demo link (mocked Forgejo data for the public demo) and screenshots.

**Edge cases**

- Repo with 50 000 files: tree loads one directory per request; breadcrumb navigation avoids full expansion.
- Ref name containing slashes (`release/2026-09-25`): route uses a splat and encodes the ref safely.
- Forgejo unreachable: pages show the design-system `EmptyState` with the last cached data and a retry, never a blank screen.
- Force-pushed branch invalidates cached commit list: cache key includes the ref's current SHA fetched cheaply first.
- Very wide diff lines (minified code): horizontal scroll within the diff, no page overflow at 320 width.
- Private repo becomes public: membership filter re-evaluates per request; no stale cache beyond 30 s.

**Dependencies**

- forge/forgejo-deploy (data source), app-shell/router-layouts (routes and slots). Soft: identity/rbac-abac (`can`), data-layer/api-layer (oRPC), forge/bot-accounts (read token), design-system/data-display (avatars, empty states), spec-builder/validator.

**Agent**

- Builds: Forge (lead) for backend and client; Nova's Views Engineer sub-agent may assist on the virtualised tree.
- Reviews: Sentinel (Code Reviewer, Visual Inspector across the width matrix, Security Auditor on the proxy).

**Size**

L: seven pages, a proxied API with permissions and a diff renderer, all needing the full visual matrix.
