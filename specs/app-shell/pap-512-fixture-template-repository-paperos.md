---
identifier: "PAP-512"
title: "Fixture template repository `paperos-template-fixture` with pinned tags `t1`, `t2`, `t3` for CLI create, bootstrap, upgrade and golden path tests"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-22", "PAP-503"]
blocks: []
key: "r4/app-shell/template-fixture-repo"
url: "https://linear.app/paperos/issue/PAP-512/fixture-template-repository-paperos-template-fixture-with-pinned-tags"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:00.202Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-512: Fixture template repository `paperos-template-fixture` with pinned tags `t1`, `t2`, `t3` for CLI create, bootstrap, upgrade and golden path tests

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Infra S

**Goal**

PAP-22 tests against `imagine-os/cli-sandbox`, PAP-51 against `paperos-bootstrap-fixture`, PAP-430 against a "fixture template repo" with tags `t1..t3` and a deliberate CLAUDE.md conflict, PAP-429 against three canned ideas. Each assumes a fixture nobody owns. One small, versioned fixture repo makes those tests reproducible and lets a cold session run them without touching the real template.

**Scope**

In:

* Repo `imagine-os/paperos-template-fixture`: a 30-file miniature of the template (two packages, one route, one spec, `ownership.yaml`, `.paperos/template.json`) generated from the real template by `scripts/fixture/build.ts` so it never drifts by hand.
* Tags: `t1` baseline; `t2` renames `useLayout` to `useShellLayout` and changes CI (exercises codemods and template-owned merge); `t3` edits CLAUDE.md in a way that conflicts with an app-side edit (exercises draft PRs with markers).
* Companion fixture apps under `fixtures/apps/` in `paperos-template`: `clinic-t1` created from `t1` with one app-side change, used by PAP-430 and PAP-364 tests; the three idea text files for PAP-429.
* `fixtures/README.md` listing every fixture, the tests that use it and how to regenerate.

Out: the tests themselves (PAP-22, PAP-51, PAP-430, PAP-429), the production template.

**Spec**

* `build.ts` is deterministic; CI compares the generated tree with the tagged one and fails on drift (`fixture-drift` step).
* Tags are immutable; a new scenario adds `t4`, never rewrites `t2`.
* The fixture repo is bootstrapped by `forge bootstrap` (PAP-51) so it also serves as that command's fixture; mirrored to Forgejo (PAP-47).
* No secrets, no real tenant data; `.paperos/template.json` points at the fixture tags.

**Interface contract**

Provides: repo and tags, `fixtures/apps/clinic-t1`, idea files, `fixture-drift` step; consumed by PAP-22, PAP-51, PAP-430, PAP-499, PAP-429, PAP-364.

Consumes: template layout (PAP-13), CLI create for the fixture app (PAP-22), bootstrap (PAP-51, soft), mirroring (PAP-47, soft).

**Definition of done**

* Repo exists on both forges with the three tags; `build.ts` regenerates `t1` byte-identically; `fixture-drift` green.
* PAP-430 and PAP-51 comment that their tests point at these fixtures; `fixtures/README.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: `build.ts` determinism (two runs identical); tag content assertions (rename present in `t2`, conflict in `t3`).
* E2E: `forge bootstrap paperos-template-fixture --dry-run` lists ten steps against it.

**Demo**

Reviewer runs `git clone` of the fixture, `git diff t1 t2 --stat` shows the rename and CI change, `git diff t2 t3` shows the CLAUDE.md edit. Under a minute.

**Edge cases**

* Real template renames a file the miniature copies: `build.ts` fails with the path, fixture updated in the same PR as the template change.
* Fixture used concurrently by two nightly jobs: read-only use only; writes go to throwaway `gp-` repos.

**Dependencies**

Hard: PAP-13, PAP-22. Soft: PAP-51, PAP-47. Feeds PAP-430, PAP-429, PAP-364.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/upgrade-codemods-fleet` = PAP-499.
