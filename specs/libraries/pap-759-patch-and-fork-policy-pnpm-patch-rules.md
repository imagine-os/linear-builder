---
identifier: "PAP-759"
title: "Patch and fork policy: `pnpm patch` rules, `patches/` entries in the registry with upstream PR link and expiry, CI check that every patch is registered"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Infra"
priority: 3
surfaces: ["Developer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-211", "PAP-216"]
blocks: []
key: "r4/libraries/patch-fork-policy"
url: "https://linear.app/paperos/issue/PAP-759/patch-and-fork-policy-pnpm-patch-rules-patches-entries-in-the-registry"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:16.199Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-759: Patch and fork policy: `pnpm patch` rules, `patches/` entries in the registry with upstream PR link and expiry, CI check that every patch is registered

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

An agent that hits a library bug at 3 a.m. will run `pnpm patch`, fix it locally and move on. Six months later nobody knows why `patches/foo@1.2.3.patch` exists or whether upstream fixed it. PAP-215 already says `fork` needs Justin; extend the same governance down to patches: every patch has a registry row, an upstream link and an expiry, checked in CI.

**Scope**

In: `docs/libraries/patch-policy.md` (when to patch, when to fork, when to vendor; upstream-first rule); registry entry extension `patches[] { file, reason, upstreamIssue, upstreamPr?, expires, owner }` (PAP-216 schema, additive); `pnpm lib patch add <pkg> --reason --upstream <url>` wrapping `pnpm patch-commit` and writing the registry row; check `pnpm lib registry check` rule: every file in `patches/` and every `pnpm.patchedDependencies` entry has a row, no row without a file, expired patches fail; Renovate (PAP-217) config to open a `patch-review` issue when the patched package upgrades; `docs/libraries/patch-policy.md`. Out: forks (Needs Justin per PAP-215), vendoring of whole products.

**Spec**

* Patch rules: allowed only for bugs with an upstream issue link filed by us or found; maximum 200 changed lines; expiry 90 days, renewable once by the owner with a comment; a second renewal needs an ADR.
* `patchedDependencies` in `package.json` must pin the exact version the patch was made for; Renovate bumps that touch a patched package are labelled `needs-patch-review` and never automerge (PAP-217 rule).
* Fork path: `fork` status in the registry (PAP-216) requires an accepted ADR with Justin among deciders; the fork lives in `imagine-os/<upstream>-fork` with a `FORK.md` diff summary regenerated weekly.
* Vendored snippets (copy of a small MIT function) are `docs/registry/trivial.yaml` entries with the source URL and license text.
* License: a patch keeps the upstream license; `THIRD_PARTY_NOTICES.md` (PAP-211) lists patched packages with the patch file name.

**Interface contract**

Provides: policy doc, registry `patches[]` field, `pnpm lib patch add`, check rules, Renovate label rule. Consumes: registry schema and check (PAP-216), notices generator (PAP-211), Renovate preset (PAP-217, soft), ADR process (PAP-130). Consumed by: PAP-217, PAP-306 re-audit (expiring patches), PAP-358 supply-chain policy (patched packages are pinned by digest), Scout sessions.

**Definition of done**

* Policy merged; a fixture patch without a row fails the check; an expired row fails; `pnpm lib patch add` writes both files; notices list the patch.
* `docs/libraries/patch-policy.md`; CHANGELOG entry; comment on PAP-217 with the label rule.

**Test plan**

* Unit: check rules with fixtures, expiry with a fake clock, line-count guard.
* Integration: `pnpm lib patch add` on a fixture package in a temp workspace.
* E2E: none.

**Demo**

Run `pnpm lib patch add left-pad --reason 'null input' --upstream https://github.com/x/y/issues/1`, edit, commit, run the check clean; set `expires` to yesterday and see it fail. Under two minutes.

**Edge cases**

* Patch for a package under `spikes/`: ignored.
* Upstream merged the fix: Renovate PR carries `needs-patch-review`; the check reminds the owner to drop the patch when the version matches `upstreamPr` release.
* Patch touches a license header: rejected by the line filter.

**Dependencies**

Hard: PAP-216, PAP-211. Soft: PAP-217, PAP-130, PAP-358, PAP-306.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Sentinel (Code Reviewer) with Atlas on the policy text.

**Size**

S: half a session.
