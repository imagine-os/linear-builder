---
identifier: "PAP-442"
title: "Build the swap playbook automation: `paperos module swap <id> --to <impl>` walks propose, fork, conformance, shadow, canary, flip, remove with gates and rollback"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-435", "PAP-437", "PAP-440", "PAP-441"]
blocks: ["PAP-430", "PAP-446"]
key: "module-system/swap-cli"
url: "https://linear.app/paperos/issue/PAP-442/build-the-swap-playbook-automation-paperos-module-swap-id-to-impl"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:50:09.594Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-442: Build the swap playbook automation: `paperos module swap <id> --to <impl>` walks propose, fork, conformance, shadow, canary, flip, remove with gates and rollback

**Model / Effort:** Sonnet 5 / high

**Goal**

Encode the swap playbook (`docs/module-system.md` section 6) as a CLI that refuses to advance a step whose gate is red, so a rewrite of any module follows the same seven steps with the same evidence, and rollback is one command. It also writes the deprecation windows the compatibility matrix and gateway adapters read.

**Scope**

In:

* `paperos module swap <id> --to <impl>` with subcommands or `--step propose|fork|conformance|shadow|canary|flip|remove` and `--rollback`; state stored in `ops/swaps/<id>-<impl>.json` (step, timestamps, evidence links, operator).
* Gates per step: ADR present with the required fields (propose); manifest `provides` and flag exist, CI builds both (fork); `conformance.json` green for both and matrix unchanged or all consumers bumped (conformance); shadow diff count under threshold over N nightly runs and PAP-242 budgets met (shadow); flag rules for demo then staff tenants for one release train (canary); default flipped and window opened (flip); window expired, v1 unbound, `knip` clean, matrix regenerated (remove).
* Evidence collection: links to the artefacts, Gate 3 contact sheets with `X-PaperOS-Impl`, shadow diff summary, written into the ADR and posted as a Linear comment on the swap issue.
* `--rollback`: flips the flag to `default`, records the reason, re-opens the step; never touches data.
* For `critical` risk: creates one Linear issue per step under a swap umbrella using `PmSourcePort` and requires a Needs Justin card before `flip`.

Out: the actual second implementations, data migrations (adapter kit issue), UI for swaps beyond `/settings/modules`.

**Spec**

* Steps are strictly ordered; a red gate prints what is missing and how to produce it.
* Thresholds (shadow diff rate, nightly runs) come from the manifest `swapRisk`: critical 3 nightly runs and 0 diffs; high 2 and under 0.1 percent; medium 1 and under 1 percent; low skips shadow.
* `remove` refuses while any tenant override still points at the old impl or any topic is dual-published.
* Every command is idempotent and prints the state file path.
* Destructive migrations before `remove` are detected (migration adapter kit metadata) and block with a Needs Justin instruction.

**Interface contract**

Provides: `paperos module swap`, `paperos module status`, `ops/swaps/*.json` state, `compat-windows.json` writer, swap umbrella issue creation. Consumes: flag swap mechanism, conformance runner and artefacts, gateway response adapters, compatibility matrix, PAP-88 release train timing, PAP-130 ADR format, `PmSourcePort` (pm-linear contract) for issues, PAP-94 Needs Justin card shape. Consumed by: the shell swap drill, any future rewrite, PAP-430 `paperos upgrade` (which reuses the step gating for template upgrades), Atlas's dispatch.

**Test plan**

* Unit: state machine over the seven steps, gate evaluation with fixture evidence, thresholds by risk, idempotency.
* Integration: a scripted swap of the sample module from the conformance runner walks all seven steps on the compose stack with a fake release train clock; rollback at each step returns to `default`.
* Negative: missing ADR, red conformance, tenant override present at remove, dual-publish still on; each blocks with the predicted message.
* Linear: umbrella and step issues created on a sandbox team through `PmSourcePort` fixtures (no live writes in CI).

**Definition of done**

* CLI merged; scripted sample swap recording attached; negative cases tested; state files documented.
* `docs/platform/swap-playbook.md` (the human version of section 6 with the CLI commands); Linear comment.

**Edge cases**

* Operator runs steps out of order: refused with the current step.
* Two swaps of the same module at once: refused; one state file per module.
* Release train paused (PAP-88): canary duration counts trains, not days; the CLI says it is waiting for a train.
* Kernel restarts mid-shadow: shadow state is in the flag and table, not in memory; the CLI reads it back.

**Dependencies**

Blocked by module-system/flag-swap, module-system/conformance-runner, module-system/gateway-routing, module-system/compat-matrix. Blocks PAP-430.

**Agent**

Built by Forge. Reviewed by Atlas and Sentinel.

**Size**

M

**Demo**

Reviewer runs `paperos module swap sample --to v2 --step conformance` and it refuses because the ADR is missing; adds the ADR, reruns, and the CLI runs conformance for both impls, prints the diff and advances; `--rollback` flips the flag back and the state file shows the reason. Two minutes.
