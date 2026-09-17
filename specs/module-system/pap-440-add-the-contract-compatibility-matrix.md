---
identifier: "PAP-440"
title: "Add the contract compatibility matrix CI job: resolve every `requires` against provided versions, publish `compat-matrix.md` and fail on incompatible bumps"
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
blockedBy: ["PAP-433", "PAP-439"]
blocks: ["PAP-442"]
key: "module-system/compat-matrix"
url: "https://linear.app/paperos/issue/PAP-440/add-the-contract-compatibility-matrix-ci-job-resolve-every-requires"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:50:08.325Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-440: Add the contract compatibility matrix CI job: resolve every `requires` against provided versions, publish `compat-matrix.md` and fail on incompatible bumps

**Model / Effort:** Sonnet 5 / medium

**Goal**

Answer "who breaks if this contract moves?" before merging. A CI job reads every manifest, resolves each `requires` range against the provider's `provides.version`, and writes `docs/platform/compat-matrix.md` and `.json` with cells `ok`, `ahead`, `behind` or `-`; it fails a PR that introduces `ahead` (consumer needs a version nobody provides) or an expired `behind` (provider moved a major and the 30-day window has passed). The matrix is also what the Blueprint's dependency views colour (`docs/module-system.md` section 2.2).

**Scope**

In:

* `pnpm compat`: matrix computation from manifests and contract `package.json` versions; per-port detail when `requires[].ports` is set (which port moved).
* Deprecation window tracking: `compat-windows.json` (contract, old major, flipped at, expires at) written by the swap CLI and read here.
* Outputs: Markdown table, JSON with a stable schema, GitHub check summary with the changed cells only.
* Gate 1 step `compat` (PAP-78) and a nightly run that comments on the owning Linear issue when a window is about to expire (7 days).

Out: deciding versions (contract owners), publishing packages to a registry (workspace-private for this build).

**Spec**

* Pre-1.0 semantics: `^0.x` ranges, minor is breaking; after 1.0 standard semver.
* `behind` is a warning inside the window and a failure after it; `ahead` is always a failure.
* A consumer with `optional: true` on a missing provider is `-`, not `ahead`.
* The job is deterministic and under 5 s.

**Interface contract**

Provides: `pnpm compat`, `compat-matrix.md`, `compat-matrix.json` (schema), `compat-windows.json` reader, Gate 1 step `compat`, nightly expiry comments. Consumes: manifests and validator, contract package versions, dependency map generator (shared loader), PAP-78 Gate 1, PAP-97 for Linear comments. Consumed by: contract owners, the swap CLI (step 3 gate), PAP-306 re-audit, the Blueprint dependency views, the docs generator.

**Test plan**

* Fixtures: matrices for ok, ahead, behind-in-window, behind-expired, optional-missing; exact cell values and exit codes.
* Gate: a PR bumping `contract-tables` to 0.2 with consumers on `^0.1` fails with the consumer list.
* Nightly: expiry comment fixture posted to a sandbox issue.

**Definition of done**

* Job merged and green on the template; matrix committed; Gate 1 step live; nightly scheduled.
* `docs/platform/compat-matrix.md` linked from `docs/module-system.md`; Linear comment.

**Edge cases**

* Two implementations of one contract at different versions: the higher version is the provided one for resolution; the lower is flagged `stale-impl`.
* A contract with no consumers: row exists with all `-` so orphaned contracts are visible.
* Window file missing for a `behind` cell: treated as expired (fail closed) with a message to run the CLI step.

**Dependencies**

Blocked by module-system/manifest-schema, module-system/dependency-lint-and-map.

**Agent**

Built by Forge. Reviewed by Atlas.

**Size**

S

**Demo**

Reviewer opens `compat-matrix.md` and sees seventeen rows all `ok`; bumps `contract-collab` to 0.2 in a branch and the check fails listing PM, growth, migration and libraries as `ahead`, each with the port they use. Under a minute.
