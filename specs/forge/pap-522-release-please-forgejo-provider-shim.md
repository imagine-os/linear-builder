---
identifier: "PAP-522"
title: "release-please Forgejo provider shim: dual-forge tags and releases, asset upload, the `autorelease: pending` lock and recorded-response tests"
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
blockedBy: ["PAP-46", "PAP-50", "PAP-52", "PAP-133", "PAP-273", "PAP-519"]
blocks: ["PAP-358", "PAP-498", "PAP-523", "PAP-672"]
key: "r4/forge/release-forgejo-provider"
url: "https://linear.app/paperos/issue/PAP-522/release-please-forgejo-provider-shim-dual-forge-tags-and-releases"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:49.946Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-522: release-please Forgejo provider shim: dual-forge tags and releases, asset upload, the `autorelease: pending` lock and recorded-response tests

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

release-please knows GitHub; PAP-52 promises identical tags and releases on Forgejo so DR (PAP-53) and the mirror stay consistent. The provider shim is the risky half and a session of its own, leaving the GitHub configuration, the Linear-links plugin and the manual-version checker to the parent.

**Scope**

In:

* `scripts/release/forgejo-provider.ts`: implements the release-please `GitHub` client surface the CLI needs (`getCommits`, `createRelease`, `createPullRequest`, `getLabels`) over the Forgejo API v1 using the generated client (PAP-51), so `release-please release-pr` and `release-please github-release` run on Forgejo Actions.
* Dual-forge semantics: tags are created on Forgejo first, mirrored to GitHub by PAP-47; the GitHub release job waits for the tag to arrive (poll 60 s) then creates the release and uploads assets; if the tag already exists on GitHub via the mirror the job uploads missing assets only.
* Lock: before opening a release PR, look for an open PR labelled `autorelease: pending` on either forge; if found, update instead of create.
* Recorded-response tests (`msw`) for every provider method; a live run on the fixture repo (PAP-512).

Out: release-please manifest configuration and bump rules (PAP-52), changelog rendering (PAP-133), artifact signing (PAP-358).

**Spec**

* Release notes body identical on both forges (byte compare in the test).
* `feed.json` (PAP-52) is written once by whichever forge runs first; the second run verifies and skips.
* Provider handles Forgejo pagination and the missing `compare` endpoint by walking commits between tags.
* Exit codes and logs match the GitHub path so PAP-88 tooling is forge-agnostic.

**Interface contract**

Provides: `forgejo-provider.ts`, dual-forge release semantics, lock behaviour; consumed by PAP-52 (workflow), PAP-53 (tags present after restore), PAP-88 (`-rc.N` prereleases on both forges), PAP-256 (desktop tags).

Consumes: Forgejo API and packages (PAP-273), runners (PAP-50), generated client (PAP-51), mirror timing (PAP-47), fixture repo.

**Definition of done**

* Fixture repo: `feat(ui):` merge yields a release PR on Forgejo; merging creates `ui-v*` tag and release on both forges with identical notes (URLs).
* Race test: two runs, second exits on the lock; recorded-response tests green; CHANGELOG; Linear comment.

**Test plan**

* Unit: every provider method against recorded responses; pagination; missing-compare fallback; lock detection.
* E2E: live fixture run on Forgejo Actions; assert GitHub release created after mirror.

**Demo**

Reviewer opens the Forgejo Actions run that created `ui-v0.1.1`, then the matching GitHub release page with the same notes and assets. Under a minute.

**Edge cases**

* Mirror lag over 10 minutes: GitHub job times out with a clear message and is retried by the next push.
* Tag exists on GitHub but not Forgejo (manual tag): job refuses and files a divergence through PAP-520.
* Forgejo API version drift: provider pins the API version and fails fast on an unknown field.

**Dependencies**

Hard: PAP-273, PAP-50. Soft: PAP-51 client, PAP-47, PAP-512. Parent PAP-52 consumes.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/app-shell/template-fixture-repo` = PAP-512, `r4/forge/mirror-drift-monitor` = PAP-520.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-52 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-52 blocks this issue (`blocks` relation).
