---
identifier: "PAP-499"
title: "Template codemod runner (`templates/codemods/<from>-<to>/*.ts`) and `paperos upgrade --fleet` listing every generated app and its template tag"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: "PAP-430"
children: []
blockedBy: ["PAP-22", "PAP-503"]
blocks: []
key: "r4/app-shell/upgrade-codemods-fleet"
url: "https://linear.app/paperos/issue/PAP-499/template-codemod-runner-templatescodemodsfrom-tots-and-paperos-upgrade"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:58.187Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-499: Template codemod runner (`templates/codemods/<from>-<to>/*.ts`) and `paperos upgrade --fleet` listing every generated app and its template tag

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Two separable halves of PAP-430: the codemod runner that rewrites renamed APIs in app-owned files during an upgrade, and fleet mode that lets Atlas see which generated apps are behind. Splitting them lets the merge engine (the parent) land without waiting on ts-morph work.

**Scope**

In:

* `packages/cli/src/upgrade/codemods.ts`: discover `templates/codemods/<fromTag>-<toTag>/*.ts` in the template checkout, order them by tag range, run each with `ts-morph` over `app`-owned and `shared`-owned paths from `ownership.yaml`, collect a per-file result.
* Codemod authoring contract: `export default defineCodemod({ id, description, files: glob[], transform(sourceFile) })`; `paperos codemod test <id>` runs the codemod over `__fixtures__/before` and diffs against `after`.
* `paperos upgrade --fleet <org> [--json]`: lists apps from the GitHub org (PAP-22 `GitHubClient`), reads `.paperos/template.json` from each default branch, prints name, tag, versions behind, last upgrade PR.
* Two shipped codemods as examples: `rename-useLayout-to-useShellLayout` (fixture) and `move-offlinebanner-import` (PAP-18 moved `OfflineBanner` to `@paperos/ui`).

Out: three-way merge and PR creation (PAP-430), registry publishing (PAP-498), fleet scheduling of upgrades (Atlas by hand).

**Spec**

* Codemods are pure functions over a `ts-morph` project; a throw in one file is recorded and the runner continues.
* Range selection: upgrading `t1` to `t3` runs `t1-t2` then `t2-t3`; a codemod folder named for a skipped minor is an error.
* Fleet listing uses the GitHub client; the Forgejo client (PAP-276, deferred) is used when its token exists, otherwise a warning line.
* `--json` output `{ apps: [{ name, tag, behind, lastUpgradePr }] }` for the PAP-306 weekly re-audit.

**Interface contract**

Provides: `runCodemods(range, paths): CodemodReport`, `defineCodemod`, `paperos codemod test`, `paperos upgrade --fleet`; consumed by PAP-430 (calls `runCodemods` after the merge), PAP-306 (fleet JSON), PAP-24 (authoring section).

Consumes: PAP-22 `GitHubClient` and `.paperos/template.json` schema (co-owned with PAP-430), `ownership.yaml` classes (PAP-430).

**Definition of done**

* Both example codemods pass their fixture tests; the runner applies them in range order on the fixture app.
* Fleet listing renders three fake apps at mixed tags; JSON validates.
* `docs/cli/upgrade.md` codemod authoring section; CHANGELOG; Linear comment.

**Test plan**

* Unit: range ordering across three tags, skipped-minor error, throw-in-one-file continues.
* Unit: fixture before/after diff for both codemods.
* Unit: fleet table rendering with a missing `template.json` (shown as `unknown`).
* E2E: integration with PAP-430: upgrade fixture app `t1` to `t2`, assert the renamed import compiles.

**Demo**

Reviewer runs `paperos codemod test rename-useLayout-to-useShellLayout` and sees the fixture diff pass, then `paperos upgrade --fleet imagine-os --json` against the fake client listing three apps. Under a minute.

**Edge cases**

* Codemod touches a `template`-owned path: refused; those paths are merged, not transformed.
* App with hundreds of files: `ts-morph` project loads only matched globs; under 30 s for 2,000 files.
* Rate limit while listing the fleet: header-driven wait, partial table with a warning.

**Dependencies**

Hard: PAP-22. Soft: PAP-276 (deferred; GitHub listing is the default), PAP-306. Parent PAP-430 consumes `runCodemods`.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/upgrade-package-registry` = PAP-498.
