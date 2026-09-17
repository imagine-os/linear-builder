---
key: "gp/app-shell/upgrade"
title: "Build `paperos upgrade`: apply template updates to generated apps with three-way merge, codemods, regeneration and an upgrade pull request"
project: "app-shell"
parent: null
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: ["Developer", "Agent"]
milestone: "Multi-monitor and PWA polish"
intendedState: "Backlog"
blockedBy: ["PAP-22", "gp/spec-builder/gen-pipeline"]
blocks: []
source: "round2/pending-issues-golden-path.json (Golden Path)"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-golden-path-8-98e27ab16f4f"
status: "pending"
---

# Build `paperos upgrade`: apply template updates to generated apps with three-way merge, codemods, regeneration and an upgrade pull request

**Goal**

An app created in ten minutes must keep receiving the template's fixes for years, or every generated app becomes a fork that drifts. `paperos upgrade` moves a generated app from its recorded template tag to a newer one: three-way merge of template-owned files, codemods for renamed APIs, regeneration of `generated/**` through `paperos gen`, migration hints, and one pull request that has to pass the same gates as any other. This closes the template-upgrade gap the round-2 audit found in forge and app-shell; `gap/forge/template-upgrade` was merged into this issue on 2026-09-17 (FIX-6), which adds the `@paperos/*` package registry below.

**Scope**

In:

* `paperos upgrade [--to <tag>] [--dry-run] [--no-pr]` in `packages/cli/src/upgrade/`: reads `.paperos/template.json` (`{ ref, tag, appliedAt, ownership }` written by PAP-22 at creation), fetches the template at the current and target tags, computes the diff of template-owned paths, applies it as a three-way merge (`git merge-file`) onto the app, runs codemods, runs `paperos gen --force`, runs `pnpm check`, commits on `upgrade/template-<tag>` and opens a PR with the template CHANGELOG (PAP-133) section between the two tags.
* Ownership manifest `templates/ownership.yaml` in the template: `template` (always merged: CI, ops, configs, `packages/ui` internals), `generated` (rewritten by `paperos gen`), `app` (never touched: specs, logic files, app schema), `shared` (three-way merged with conflict markers: CLAUDE.md, README, `app.spec.yaml` defaults). PAP-22's rename map is reused so renamed identifiers merge cleanly.
* Codemods in `templates/codemods/<from>-<to>/*.ts` (jscodeshift or ts-morph) shipped with each template release that renames an exported API; the upgrade runs those in range.
* Module awareness: paths belonging to modules the app removed with `--without` (PAP-266, PAP-264) are skipped.
* Conflict report `.paperos/upgrade-report.md` listing merged, regenerated, conflicted and skipped files; conflicted files keep markers and the PR is opened as draft.
* Template release hook: `forge/release-tags` (PAP-53) publishes `template-upgrade-notes.md` per tag; the upgrade PR embeds it.
* Package registry (from `gap/forge/template-upgrade`): publish `@paperos/*` on each template tag to the Forgejo npm registry (`git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/`) with a GitHub Packages mirror; `.npmrc` template in generated apps; auth via the PAP-48 bot token in CI and the developer's Forgejo token locally; the upgrade PR bumps `@paperos/*` versions alongside the file merge.
* Package registry (from `gap/forge/template-upgrade`): publish `@paperos/*` on each template tag to the Forgejo npm registry (`git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/`) with a GitHub Packages mirror; `.npmrc` template in generated apps; auth via the PAP-48 bot token in CI and the developer's Forgejo token locally; the upgrade PR bumps `@paperos/*` versions alongside the file merge.
* Fleet mode `paperos upgrade --fleet imagine-os` (dry-run by default) listing every generated app and its template tag from `.paperos/template.json` via the forge API (PAP-276), for Atlas to schedule upgrades.

Out: database data migrations (app migrations are ordinary Drizzle migrations reviewed in the PR), upgrading external services, automatic merging of conflicted PRs.

**Spec**

* Three-way merge base is the template at the app's recorded tag with the rename map applied, so the app's rename does not show as a conflict.
* Order: fetch, merge template-owned paths, apply codemods, `paperos gen --force`, `pnpm i --frozen-lockfile=false` (lockfile is `shared`), `pnpm check`; a failing `check` still opens the PR as draft with the failure log attached.
* `--dry-run` prints the file table and the codemods that would run, without writing.
* Idempotent: rerunning on an app already at the target tag exits 0 with "up to date"; a partially applied upgrade (crash) is resumed from `.paperos/upgrade.state.json`.
* Version policy: upgrades skip no minor tag; `--to` beyond the next minor applies tags in sequence so codemods compose.
* The upgrade PR uses the PAP-49 template with the `Linear:` trailer pointing at an issue the CLI creates in the app's Linear project ("Upgrade template to <tag>", Type Build) through the `linear-update` skill.

**Interface contract**

Provides: `upgradeApp(opts): UpgradeReport`, the `ownership.yaml` schema, the codemod folder convention, `.paperos/template.json` schema (co-owned with PAP-22, which writes it), and `--fleet` listing. Consumes: PAP-22 rename map and `template.json`, `paperos gen --force` (pipeline issue), module manifests (PAP-264, PAP-266), release tags and notes (PAP-53), PR template (PAP-49), changelog sections (PAP-133), forge client for fleet mode (PAP-276, soft). Consumed by: every generated app, Atlas fleet scheduling, the golden path acceptance workflow (`workflow_call` re-verification after an upgrade), PAP-24 template guide.

**Test plan**

* Unit: ownership classification for a fixture tree; three-way merge with rename map (no false conflicts); codemod range selection across three tags; idempotent rerun; resume after simulated crash.
* Integration: create the clinic app at tag `t1` (fixture template repo), release `t2` with a renamed API and a CI change, run `paperos upgrade --to t2`, assert the PR diff touches only template and generated paths and `pnpm check` passes; then a `t3` with a deliberate conflict in CLAUDE.md produces a draft PR with markers and a report.
* Fleet: fake forge listing three apps at mixed tags renders the table.

**Definition of done**

* Command merged; the fixture-template integration test runs in CI; one real upgrade PR opened on a `gp-` app from the acceptance workflow and merged green.
* `ownership.yaml` committed to the template and validated in gate 1 (every path in the repo classified).
* `docs/cli/upgrade.md` and a section in the template guide (PAP-24); `template-upgrade-notes.md` produced by the release process for the next tag.
* CHANGELOG; Linear comment with the fixture upgrade diff summary.

**Edge cases**

* App modified a `template` path (allowed but discouraged): merged three-way; conflict markers if incompatible; the report explains how to move the change into `app` space.
* Template removed a file the app still imports: `pnpm check` fails, PR opened as draft with the typecheck output.
* Codemod throws on one file: recorded in the report, other files continue, PR draft.
* App's `.paperos/template.json` missing (created before PAP-22 wrote it): `--from <tag>` required; the CLI suggests the tag by matching template file hashes.
* Upgrade across a `specVersion` bump (spec versioning pending issue): the spec codemods run first and the upgrade stops for review if any spec fails validation.
* Fleet mode without forge credentials: falls back to GitHub org listing (PAP-22 client) and warns.
* Template major bump: upgrade refuses without `--allow-major` and links the ADR.
* Registry down: `pnpm install` falls back to the GitHub Packages mirror.
* Template major bump: upgrade refuses without `--allow-major` and links the ADR.
* Registry down: `pnpm install` falls back to the GitHub Packages mirror.

**Dependencies**

Hard: PAP-22, `paperos gen` pipeline. Soft: PAP-264, PAP-266, PAP-53, PAP-49, PAP-133, PAP-276, PAP-24, PAP-45 (Forgejo packages), PAP-48 (bot token), PAP-52 (release feed); PAP-29's drill upgrades a drill app with this command. Blocks nothing in this round; every generated app depends on it operationally.

**Agent**

Built by Forge (Platform Engineer); reviewed by Sentinel (correctness, merge safety) and Atlas for fleet scheduling.

**Size**

M: merge logic, ownership manifest, codemod runner, fixture template, fleet listing.

**Demo**

Recording of `paperos upgrade --dry-run` then the real run on the clinic app producing a green PR, with the report and the fleet table for three `gp-` apps.
