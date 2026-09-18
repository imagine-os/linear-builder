---
identifier: "PAP-498"
title: "Publish `@paperos/*` packages to the Forgejo npm registry on every template tag with a GitHub Packages mirror and a generated-app `.npmrc`"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: "PAP-430"
children: []
blockedBy: ["PAP-22", "PAP-48", "PAP-52", "PAP-273", "PAP-362", "PAP-503", "PAP-521", "PAP-522"]
blocks: []
key: "r4/app-shell/upgrade-package-registry"
url: "https://linear.app/paperos/issue/PAP-498/publish-paperos-packages-to-the-forgejo-npm-registry-on-every-template"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:57.951Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-498: Publish `@paperos/*` packages to the Forgejo npm registry on every template tag with a GitHub Packages mirror and a generated-app `.npmrc`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra M

**Goal**

Generated apps must consume `@paperos/*` as versioned packages so `paperos upgrade` (PAP-430) can bump versions instead of copying files. This child publishes every workspace package to the Forgejo npm registry (`git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/`) on each `template-v*` tag, mirrors to GitHub Packages for DR, and ships the `.npmrc` the template and generated apps use. PAP-430 folded `gap/forge/template-upgrade` in and listed this as one bullet; it is a session of its own.

**Scope**

In:

* `.github/workflows/publish-packages.yml` triggered by `template-v*` tags (PAP-52 format): `pnpm -r publish --no-git-checks --registry <forgejo>` for every `packages/*` with `private: false`, then `npm publish` to GitHub Packages as the mirror.
* Package metadata: `publishConfig.registry`, `files`, `exports` and `types` on every publishable package; `size-limit` per package; `pnpm pack --dry-run` check in Gate 1 so a package that forgets `files` fails before a tag.
* `templates/.npmrc` and `apps/*/.npmrc`: scoped registry for `@paperos`, `//git.PAPEROS_DOMAIN/...:_authToken=${FORGEJO_NPM_TOKEN}`, GitHub Packages as `@paperos-mirror` fallback documented in `docs/cli/upgrade.md`.
* Auth: CI uses the PAP-48 `bot-forge` token with `write:package`; developers use a personal Forgejo token; tokens never in the repo.
* Retention: keep the last 20 versions per package; `forge packages prune` script and a monthly cron.

Out: the upgrade merge logic (PAP-430), codemods and fleet mode (PAP-499), publishing to [npmjs.org](<http://npmjs.org>).

**Spec**

* Versions come from release-please (PAP-52); this workflow never edits `version` fields (`check-no-manual-version` stays green).
* Publish is idempotent: an existing version is skipped with `[skip]`, never overwritten; a changed tarball for an existing version fails the job.
* Provenance: when PAP-358 lands, `npm publish --provenance` on GitHub and a cosign attestation on Forgejo.
* Generated apps pin exact versions in `package.json`; the template pins `workspace:*`.
* Registry down: `pnpm install` in generated apps falls back to the GitHub Packages mirror through the second scoped line in `.npmrc`.

**Interface contract**

Provides: workflow `publish-packages.yml`, `.npmrc` templates, `forge packages prune`, the rule that `@paperos/*` versions are release-please versions; consumed by PAP-430 (version bumps in the upgrade PR), PAP-22 (copies `.npmrc`), PAP-53 (registry restore check).

Consumes: Forgejo packages enabled (PAP-273), tag format (PAP-52), bot tokens (PAP-48), provenance steps (PAP-358, soft).

**Definition of done**

* Tag `template-v0.0.1-test` publishes every public package to both registries; `npm view @paperos/core --registry <forgejo>` shows the version; the tag is then deleted.
* A generated fixture app installs from the Forgejo registry with `--frozen-lockfile`, then from the mirror with the Forgejo host blackholed (recording).
* `pnpm pack --dry-run` check in Gate 1; prune script tested; `docs/cli/upgrade.md` registry section; CHANGELOG; Linear comment with the package list.

**Test plan**

* Unit: `files` and `exports` lint over every package with a fixture missing `types`.
* Unit: prune script keeps the newest 20 of 25 fake versions.
* Unit: idempotent publish: existing version yields `[skip]`, changed tarball fails.
* E2E: CI: publish on a test tag to both registries, install in the fixture app from each, remove the tag.

**Demo**

Reviewer runs `npm view @paperos/ui versions --registry https://git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/` and sees the tagged versions, then opens the GitHub Packages page showing the same version. Under a minute.

**Edge cases**

* Package with a build step that emits to `dist/`: `prepack` runs `pnpm build`; a missing `dist` fails `pack --dry-run`.
* Private package (`packages/pm` until PAP-100 stabilises) is skipped and listed in the summary.
* Token rotated mid-publish: job fails on the first 401 with the secret name, no partial version left because the version check runs first.

**Dependencies**

Hard: PAP-273 (packages enabled), PAP-52 (tags), PAP-48 (bot token). Soft: PAP-358. Consumed by PAP-430, PAP-22, PAP-53.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/upgrade-codemods-fleet` = PAP-499.
