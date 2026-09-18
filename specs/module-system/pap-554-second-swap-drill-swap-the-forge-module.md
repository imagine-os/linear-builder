---
identifier: "PAP-554"
title: "Second swap drill: swap the forge module to a read-only GitHub adapter behind `module.forge.impl`, walk the playbook for a `service`-kind module and record findings"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P2"
type: "Review"
priority: 4
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-442", "PAP-455", "PAP-539"]
blocks: []
key: "r4/module-system/service-swap-drill"
url: "https://linear.app/paperos/issue/PAP-554/second-swap-drill-swap-the-forge-module-to-a-read-only-github-adapter"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:06.676Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-554: Second swap drill: swap the forge module to a read-only GitHub adapter behind `module.forge.impl`, walk the playbook for a `service`-kind module and record findings

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review M

**Goal**

Deferred to v0.2 (past 2026-10-01). The shell drill (PAP-446) proves the runtime-host case; service modules (forge, realtime, pm-linear) swap differently: no slots, external systems, webhooks and CI artefacts. The PAP-455 demo already imagines flipping `forgejo` to `github`; making that a real adapter and drill validates the `ForgePort` contract, the DR story (GitHub-only mode) and the playbook for `medium` risk.

**Scope**

In:

* `packages/forge/src/github-adapter.ts`: `ForgePort` over the GitHub REST API with the `paperos-agents` App token (PAP-521): `repos`, `tree`, `blob`, `commits`, `pulls.list|get`; `mirrorStatus`, `bootstrap` and `pulls.create|merge` declared `unsupported`.
* Drill: `paperos module swap forge --to github` through steps 1 to 5 (propose, fork, conformance with `unsupported` handling, shadow on read ports for one nightly, canary on the demo tenant), then rollback; step 6 and 7 intentionally not taken.
* Measurements: conformance case coverage of the contract by the second adapter, shadow diff classes (ordering, pagination), latency delta, lines changed outside `packages/forge`.
* Report `docs/platform/drills/service-swap-2026-10.md` with findings filed on forge and module-system; `v1.0` recommendation for `contract-forge`.

Out: shipping GitHub as a production forge, write operations through GitHub, the shell drill.

**Spec**

* Success: zero edits outside `packages/forge` and the flag file; conformance green for supported ports; `unsupported` reported honestly (PAP-452 rule); rollback under 5 s.
* The drill runs on staging with the fixture repos only.
* Every workaround discovered is a finding, not a fix (PAP-446 rule).

**Interface contract**

Provides: GitHub read adapter, drill report and findings, timing numbers for the `service` kind; consumed by PAP-53 (GitHub-only read mode during a Forgejo outage becomes possible), PAP-442 (playbook v2), `docs/module-system.md` v2, PAP-449 `v1.0` cut.

Consumes: forge wired behind the kernel (PAP-455), swap CLI (PAP-442), conformance suite (PAP-452), App tokens, staging.

**Definition of done**

* Report, recording and findings published; adapter merged behind the flag with `unsupported` ports documented; Linear comment with numbers.

**Test plan**

* Unit: adapter mappers against recorded GitHub responses; `unsupported` declarations.
* E2E: the drill is the test: CLI state file shows steps 1 to 5 with evidence and a rollback.

**Demo**

Reviewer watches the recording: `paperos module swap forge --to github` passes conformance with three `unsupported` ports, shadow shows only pagination-size diffs, the demo tenant's repo browser reads from GitHub, `--rollback` returns to Forgejo. Three minutes.

**Edge cases**

* GitHub rate limit during shadow: sampled at 1 percent (PAP-435 default) and noted.
* Contract gap found (a port assumes Forgejo ids): filed as a Spec issue on forge with the ADR path.

**Dependencies**

Hard: PAP-455, PAP-442. Soft: PAP-452, PAP-521, PAP-53.

**Agent**

Builder: Sentinel (Code Reviewer sub-agent as builder) with Forge. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/github-app-identities` = PAP-521.
