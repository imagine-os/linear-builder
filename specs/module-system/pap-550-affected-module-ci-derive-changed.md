---
identifier: "PAP-550"
title: "Affected-module CI: derive changed modules from the dependency map and the diff, run only their Gate 1 steps plus their consumers' conformance suites, with a full run on `main` and nightly"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-78", "PAP-439"]
blocks: []
key: "r4/module-system/affected-module-ci"
url: "https://linear.app/paperos/issue/PAP-550/affected-module-ci-derive-changed-modules-from-the-dependency-map-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:05.588Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-550: Affected-module CI: derive changed modules from the dependency map and the diff, run only their Gate 1 steps plus their consumers' conformance suites, with a full run on `main` and nightly

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Nx and Turborepo both win their speed from "affected" graphs; PaperOS has a better graph than either, the manifest dependency map, and does not use it in CI. With eighteen modules, eighteen conformance suites and twenty PRs an hour, Gate 1 time is the schedule's hidden bottleneck. This issue makes PRs pay only for what they touch while keeping the safety of a full run on `main`.

**Scope**

In:

* `tools/affected/affected.ts`: from `git diff --name-only <base>...<head>` and `ownership.json` (PAP-305) map files to modules and contracts; expand through `dependency-map.json` (PAP-439) to consumers (one level for implementation changes, transitive for contract changes); output `affected.json` `{ modules, contracts, consumers, reason }`.
* Gate 1 (PAP-78) reads it: Turbo filters `--filter=...[<base>]` unioned with the affected set; conformance step runs the affected modules' suites plus every consumer suite of a changed contract; `contract:diff` (PAP-544) only for changed contracts.
* Safety rails: changes to `packages/core`, `packages/kernel`, root configs, `ownership.json` or the map itself force a full run; `main` and the nightly (PAP-253) always run everything; a `full-ci` label forces it on a PR.
* Check summary lists the affected set and the reason so a reviewer can see why a suite was skipped.

Out: Turbo remote caching (off by PAP-13 decision), Gate 2 to 4 selection (quality owns; they may read `affected.json`), the dependency map itself (PAP-439).

**Spec**

* Determinism: same diff and map produce the same `affected.json` (golden tests).
* Mapping unknown paths (new files without an owner) forces a full run and names the path so `ownership.json` gets updated.
* Runtime under 3 s; the step never becomes the long pole.
* Undeclared imports are already a Gate 1 failure (PAP-439), so the map is trustworthy as the expansion source.

**Interface contract**

Provides: `affected.json` schema and `pnpm affected`, Gate 1 filter wiring, `full-ci` label; consumed by PAP-78, PAP-441 (conformance step), PAP-82 (may select pages by module later), PAP-253, PAP-99 (scheduler can weigh CI cost).

Consumes: dependency map and lint (PAP-439), ownership file (PAP-305), Gate 1 workflow (PAP-78), Turbo pipeline (PAP-13).

**Definition of done**

* Fixture PR touching only `packages/crm` runs crm tests and the growth suite, skips tables (summary shows the reason); a contract change to `contract-tables` runs all four consumers' suites; a root config change runs everything.
* Median Gate 1 time on module-only PRs measured before and after (target under 50 percent); `docs/engineering/ci.md` affected section; CHANGELOG; Linear comment.

**Test plan**

* Unit: path to module mapping; one-level vs transitive expansion; safety-rail triggers; golden `affected.json` fixtures.
* E2E: three fixture PRs on the template with timings in the job summary.

**Demo**

Reviewer opens a PR that edits one file in `packages/finance`, reads the check summary "affected: business-core; consumers: growth (referrals), tables? no", and sees Gate 1 finish in half the usual time. Under a minute.

**Edge cases**

* Generated code (PAP-120 output) changed by a spec edit: mapped to the spec's module and the generator; both run.
* Rename across modules: both old and new owners affected.
* Map stale in the PR (author forgot to regenerate): PAP-439 fails first; this step reports `map-stale` and runs full.

**Dependencies**

Hard: PAP-439, PAP-78. Soft: PAP-305, PAP-13, PAP-253, PAP-544.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/module-system/contract-diff` = PAP-544.
