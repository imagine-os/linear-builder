---
identifier: "PAP-52"
title: "Automate semantic release tags and changelog generation on merge to main"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-133", "PAP-46"]
blocks: []
key: "forge/release-tags"
url: "https://linear.app/paperos/issue/PAP-52/automate-semantic-release-tags-and-changelog-generation-on-merge-to"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-52: Automate semantic release tags and changelog generation on merge to main

**Goal**

Turn merges to `main` into versions automatically: Conventional Commits determine semver bumps per package and app, tags and GitHub/Forgejo releases are created, and structured release notes are emitted in a form the in-app changelog (collab/changelog) can render. No agent or human edits version numbers by hand.

**Scope**

- In: release automation configuration for the monorepo, a release workflow that runs on either forge, per-package CHANGELOG files, a machine-readable release feed, attachment of build artifacts, and documentation.
- Out: the in-app changelog UI (collab/changelog) and app store submission for Tauri builds (later app-shell work); this issue only attaches artifacts to releases.

**Spec**

In `imagine-os/paperos-template`:

- Tool: `release-please` in manifest mode (`release-please-config.json`, `.release-please-manifest.json`) with a package entry for `apps/web`, `apps/desktop`, `apps/mobile` and every `packages/*` directory, `release-type: node`, `include-component-in-tag: true`, `separate-pull-requests: false` so one release PR aggregates. Tag format `<component>-v<semver>` (for example `web-v0.4.0`, `ui-v0.2.1`). Tauri apps additionally get `extra-files` entries for `tauri.conf.json` version fields.
- Bump rules: `feat` -> minor, `fix`/`perf` -> patch, `feat!` or `BREAKING CHANGE:` footer -> major (pre-1.0 uses `bump-minor-pre-major: true`). Commit trailers `Linear: PAP-<n>` are parsed by a small `release-please` plugin (`scripts/release/linear-links.ts`) that appends `(PAP-<n>)` links to each changelog line.
- Workflow `.github/workflows/release.yml`: on push to `main`, run `release-please` to open or update the release PR; when that PR merges, create tags and releases. On Forgejo the same file runs with the `release-please` CLI against the Forgejo API through a compatibility shim (`scripts/release/forgejo-provider.ts`) because the official action targets GitHub; the shim implements the create-tag, create-release and upload-asset calls used. Tags created on one forge propagate through forge/mirror; the workflow checks for an existing tag before creating to stay idempotent across both.
- Release notes feed: after releases are created, `scripts/release/emit-feed.ts` writes `releases/feed.json` (array of `{ component, version, date, sections: { features, fixes, breaking }, linearIssues, prNumbers, commitRange }`) and commits it to the `gh-pages` branch so the changelog module can fetch it statically; also posts a Linear comment on each referenced issue (`Released in web-v0.4.0`).
- Artifacts: the release workflow downloads the latest successful Tauri build artifacts (from app-shell/tauri-desktop CI) for the tagged SHA and attaches them; if none exist the step logs `[skip]`.
- Human changelog: `CHANGELOG.md` per package maintained by release-please; the aggregate `docs/changelog/index.md` is generated from the feed by the same script for collab/changelog to render.

**Definition of done**

- A `feat(ui):` commit merged to `main` results in a release PR; merging it creates `ui-v*` tag and release on both forges (URLs in PR).
- A `fix(web):` and a `feat!` commit produce patch and major bumps respectively in a test run on a fixture branch (screenshots of the release PR diff).
- `releases/feed.json` validates against `scripts/release/feed.schema.json` (Vitest test); Linear comments posted on referenced issues.
- Forgejo provider shim has unit tests with recorded responses; live run URL on Forgejo included.
- No manual version edits remain; `scripts/check-no-manual-version.ts` in gate 1 fails PRs that touch `version` fields outside release PRs.
- `docs/engineering/releases.md` merged, explaining bump rules and how to hotfix.
- Sentinel Code Reviewer approves; Quill (Changelog Scribe) reviews note readability.
- Changelog entry (self-referential, produced by the tool itself).

**Edge cases**

- Non-conventional commit slips through (hook bypassed): release-please ignores it; gate-1 commitlint from forge/branch-policy should already block; the docs note the recovery (`git commit --amend` on the branch).
- Two release PRs open at once due to a race on both forges: the workflow acquires a lock by checking for an open PR labelled `autorelease: pending` before creating.
- Tag exists on GitHub via mirror before Forgejo run: idempotent check skips creation and only uploads missing assets.
- Prerelease needed for a release candidate (quality/release-train): `prerelease: true` with `-rc.N` suffix supported via a `release-candidate` label on the release PR.
- Monorepo commit touching several packages: each affected component bumps; the commit appears in each CHANGELOG.
- Very first release with no prior tag: `bootstrap-sha` set in the manifest to the template's initial commit.

**Dependencies**

- forge/branch-policy (Conventional Commits and trailers), collab/changelog (consumer contract for the feed; agree the JSON shape in that issue's comments before implementing). Soft: app-shell/tauri-desktop (artifacts), quality/release-train (RC labels).

**Agent**

- Builds: Forge (lead), with Atlas's Merger sub-agent validating the merge flow.
- Reviews: Sentinel (Code Reviewer) and Quill (Changelog Scribe).

**Size**

M: release-please is mature, but the Forgejo shim and cross-forge idempotency need careful testing.
