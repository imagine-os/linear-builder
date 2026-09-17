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
blockedBy: ["PAP-46", "PAP-133"]
blocks: ["PAP-358"]
key: "forge/release-tags"
url: "https://linear.app/paperos/issue/PAP-52/automate-semantic-release-tags-and-changelog-generation-on-merge-to"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:43.028Z"
---

# PAP-52: Automate semantic release tags and changelog generation on merge to main

**Goal**

Turn merges to `main` into versions automatically: Conventional Commits determine semver bumps per package and app, tags and releases are created on both forges, and structured release notes feed the in-app changelog (PAP-133). No one edits version numbers by hand. The feed JSON shape is agreed in PAP-133's comments before implementation begins.

**Scope**

In:

* `release-please` manifest mode for the monorepo; a release workflow that runs on either forge; per-package CHANGELOGs; `releases/feed.json`; artifact attachment; docs.

Out: the in-app changelog UI (PAP-133), store submission for Tauri builds (signing issue).

**Spec**

* `release-please-config.json` and `.release-please-manifest.json` with entries for `apps/web`, `apps/desktop`, `apps/mobile`, `apps/api`, `apps/worker`, every `packages/*`; `release-type: node`, `include-component-in-tag: true`, `separate-pull-requests: false`; tags `<component>-v<semver>` (`web-v0.4.0`); Tauri apps get `extra-files` for `tauri.conf.json`.
* Bumps: `feat` minor, `fix` and `perf` patch, `feat!` or `BREAKING CHANGE:` major; `bump-minor-pre-major: true`.
* Plugin `scripts/release/linear-links.ts` appends `(PAP-n)` links from trailers.
* `.github/workflows/release.yml`: on push to `main` open or update the release PR; on merge create tags and releases, upload artifacts, write `releases/feed.json`, comment on referenced Linear issues via PAP-97.
* Forgejo: same file runs the `release-please` CLI through `scripts/release/forgejo-provider.ts`.
* Lock: check for an open PR labelled `autorelease: pending` before creating.
* `scripts/check-no-manual-version.ts` in Gate 1 fails PRs editing `version` fields outside release PRs.
* `release-candidate` label produces `-rc.N` prereleases for PAP-88.

**Interface contract**

Provides:

* Tag format `<component>-v<semver>` consumed by PAP-26 (production deploys on `web-v*` and `api-v*`), PAP-19 (desktop artifacts on `desktop-v*`), the template-upgrade issue (`template-v*`).
* `releases/feed.json` validated by `scripts/release/feed.schema.json`: `{ releases: [{ component, version, tag, date, notes: [{ type, scope, subject, linear: 'PAP-n'|null, sha }], artifacts: [{ name, url, sha256 }] }] }` consumed by PAP-133.
* Gate 1 check `check-no-manual-version` (PAP-78).
* Label `release-candidate` and prerelease semantics for PAP-88.

Consumes: commit grammar and trailers (PAP-46), feed shape agreement (PAP-133), artifacts (PAP-19, soft), Linear comment path (PAP-97, soft).

**Definition of done**

* A `feat(ui):` merge yields a release PR; merging it creates `ui-v*` tag and release on both forges (URLs).
* `fix(web):` and `feat!` produce patch and major bumps in a fixture-branch run (screenshots of the release PR diff).
* `feed.json` validates (Vitest); Linear comments posted on referenced issues.
* Forgejo provider shim unit-tested with recorded responses; live Forgejo run URL included.
* `check-no-manual-version` in Gate 1; `docs/engineering/releases.md` merged; Sentinel approves; Quill reviews note readability.

**Test plan**

* Unit: `linear-links` plugin on fixture commits; feed generator against schema; Forgejo provider against recorded API responses; manual-version checker with passing and failing diffs.
* Integration: fixture branch with `fix(web):`, `feat(ui):`, `feat!(api):` commits; run release-please in dry mode; assert bumps.
* E2E: merge the release PR on the fixture repo; assert tags and releases exist on both forges and `feed.json` updated.
* Race: two workflow runs; second detects the `autorelease: pending` PR and exits.

**Demo**

Reviewer opens the latest release PR, reads the generated per-package CHANGELOG diff with `(PAP-n)` links, then opens `releases/feed.json` on `main` and the matching release page on Forgejo. Under 90 seconds.

**Edge cases**

* Non-conventional commit slipped through: ignored; recovery documented.
* Tag exists on GitHub via mirror before the Forgejo run: idempotent skip, upload missing assets only.
* Monorepo commit touching several packages: each component bumps.
* First release: `bootstrap-sha` in the manifest.
* Milestone note: PAP-133 lands 09-26, after this issue's 09-24 milestone; the feed shape is agreed in comments first so this issue is not blocked on PAP-133's UI.

**Dependencies**

PAP-46 (hard), PAP-133 (feed shape agreement; implementation may proceed once the shape is commented). Soft: PAP-19, PAP-88, PAP-97.

**Agent**

Built by Forge (lead) with Atlas (Merger) validating. Reviewed by Sentinel (Code Reviewer) and Quill (Changelog Scribe).

**Size**

M: configuration, one plugin, one provider shim, one checker.
