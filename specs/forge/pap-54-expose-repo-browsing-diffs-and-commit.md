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
children: ["PAP-276", "PAP-277", "PAP-278"]
blockedBy: ["PAP-16", "PAP-45", "PAP-275"]
blocks: []
key: "forge/in-app-git"
url: "https://linear.app/paperos/issue/PAP-54/expose-repo-browsing-diffs-and-commit-history-inside-paperos-via-the"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:45.357Z"
model: null
effort: null
---

# PAP-54: Expose repo browsing, diffs and commit history inside PaperOS via the Forgejo API

**Goal**

Umbrella: let developers and agents browse repositories, commit history, diffs and pull requests inside PaperOS next to the specs and Linear issues those commits reference, read-only, with Forgejo as the backend. Three children. Deferral note from the audit: this is the lowest-priority forge issue and may slip past 10-01 without affecting any other project; children are ordered so the backend proxy lands first and stays useful on its own.

**Scope**

Children:

1. **PAP-276** — Forge client, oRPC procedures and permission checks (`packages/forge-client`, `repos.list|tree|file|commits|commit`, `pulls.list|get`, `can(actor, 'forge.read', { repo })`, caching).
2. **PAP-277** — Repo, tree, file and commit-list pages (`/dev/repos`, `/dev/repos/$repo`, `tree/$ref/$path`, `commits/$ref`) with specs and layout slots.
3. **PAP-278** — Diff view, PR pages and Linear links (`commit/$sha`, `pulls`, `pulls/$n`, syntax highlighting, `Linear:` trailer links, character avatars, mocked data for the Pages demo).

Out: editing files, merging PRs, review comments (PAP-131 may anchor to diffs later), GitHub as a data source.

**Spec**

* Specs under `specs/pages/dev/*.spec.yaml` with `access: { audiences: [developer, agent] }` (PAP-59 shape).
* Routes in TanStack Router; layout slots from PAP-16: sidebar repo and branch picker, main content, inspector linked issue and spec panel.
* Server token: read-only Forgejo token of the `bot-scout` class (PAP-48); cache keyed by ref SHA fetched cheaply first; 30 s max staleness for membership filtering.
* Diff rendering handles binary, rename and mode changes; `shiki` highlighting lazy-loaded per language.
* Public Pages demo uses a mocked Forgejo fixture so no token ships to the client.

**Interface contract**

Provides:

* oRPC `forge.repos.*` and `forge.pulls.*` with DTOs `RepoDto`, `TreeEntryDto`, `CommitDto = { sha, message, author: { name, character?: CharacterName }, linearKeys: string[], date }`, `DiffDto`, `PullDto`.
* Permission action `forge.read` registered with PAP-59.
* Component `CommitLink` and `DiffView` in `@paperos/ui` reusable by PAP-131 and PAP-89.
* `packages/forge-client` wrapping the generated client from PAP-51.

Consumes: Forgejo API (PAP-45), routes and slots (PAP-16), `can()` (PAP-59), oRPC host (PAP-35), token (PAP-48), `EmptyState` and avatars (PAP-71), validator (PAP-118).

**Definition of done**

* All three children Done.
* Integration test: all seven pages render against live Forgejo; a customer principal gets 403 on every `forge.*` procedure; a commit with a `Linear:` trailer shows a working link; Lighthouse performance above 85 on the commits page at 1280.
* Screenshots at all seven widths in light and dark; `docs/product/in-app-git.md`; changelog under Developer; Linear comment with the Pages demo link.

**Test plan**

* Unit: DTO mappers from Forgejo payloads; trailer parser; diff parser fixtures for binary, rename, mode change, huge minified line.
* Permission: `callAs(customer)` forbidden on every procedure; developer sees only permitted repos.
* Integration: procedures against a Forgejo fixture container in CI compose.
* E2E: Playwright navigates the seven routes with mocked data at seven widths; ref with slashes; Forgejo-down state shows `EmptyState` with retry.
* Performance: Lighthouse on the commits page.

**Demo**

Reviewer opens `/dev/repos/paperos-template/commits/main`, clicks a commit by "Forge (PaperOS agent)", reads the diff with highlighting, clicks the `PAP-n` link in the inspector to reach Linear, then opens the PR list. Under 90 seconds.

**Edge cases**

* 50,000-file repo: one directory per request.
* Ref names with slashes: splat route with safe encoding.
* Forgejo unreachable: cached data plus retry, never blank.
* Force-pushed branch: cache key includes current SHA.
* Wide diff lines: horizontal scroll inside the diff at 320.

**Dependencies**

PAP-16, PAP-45 (hard). Soft: PAP-35, PAP-48, PAP-59, PAP-71, PAP-118. No downstream consumers; safe to defer.

**Agent**

Built by Forge (lead) for backend and client; Nova's Views team advises on the diff grid. Reviewed by Sentinel.

**Size**

L as an umbrella; children are M, M, M.
