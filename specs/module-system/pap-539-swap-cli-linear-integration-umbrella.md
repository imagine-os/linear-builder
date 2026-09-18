---
identifier: "PAP-539"
title: "Swap CLI Linear integration: umbrella and per-step issues through `PmSourcePort`, evidence comments per gate and the Needs Justin card before `flip` for critical-risk modules"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-94", "PAP-435", "PAP-437", "PAP-440", "PAP-441", "PAP-442", "PAP-465", "PAP-538", "PAP-541", "PAP-542"]
blocks: ["PAP-446", "PAP-554"]
key: "r4/module-system/swap-linear-umbrella"
url: "https://linear.app/paperos/issue/PAP-539/swap-cli-linear-integration-umbrella-and-per-step-issues-through"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:47.821Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-10-01"
cycle: null
---

# PAP-539: Swap CLI Linear integration: umbrella and per-step issues through `PmSourcePort`, evidence comments per gate and the Needs Justin card before `flip` for critical-risk modules

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-442 encodes the seven playbook steps; the Linear side (creating a swap umbrella, one issue per step for `critical` modules, posting evidence and raising the Needs Justin card) depends on the pm-linear contract and on PAP-94's card shape, which land later. Splitting it lets the state machine merge first and keeps the CLI usable offline from Linear.

**Scope**

In:

* `packages/kernel/swap/linear.ts`: `ensureSwapUmbrella(moduleId, impl)` and `ensureStepIssue(step)` through `PmSourcePort` (PAP-465), idempotent by a `swap:<module>:<impl>:<step>` marker; labels `Build`, `swap`; umbrella carries the ADR link and the state file path.
* Evidence comments: after each gate passes, a comment on the step issue with artefact links (`conformance.json`, contact sheets with `X-PaperOS-Impl`, shadow summary) in the PAP-108 handoff format.
* Needs Justin card before `flip` for `critical` risk: created in the PAP-94 shape with the one-page summary the drill (PAP-446) also produces; the CLI blocks `flip` until the card is approved (`/approve` comment detected through PAP-97 or polled).
* `--no-linear` flag for offline runs (records evidence locally and prints the pending comments).

Out: the step state machine and gates (PAP-442 sibling), the Linear API client (pm-linear), the ADR (PAP-130).

**Spec**

* All writes go through `PmSourcePort`, never the Linear SDK directly (module boundary rule).
* Issue cap (`USAGE_LIMIT_EXCEEDED`, NJ-1): queued in the state file `pendingIssues[]` and replayed; the CLI proceeds for non-critical risk.
* Card text is generated from the state file so the reviewer sees the same numbers the CLI enforced.

**Interface contract**

Provides: `ensureSwapUmbrella`, `ensureStepIssue`, evidence comment format, the `swap` label, `--no-linear`; consumed by PAP-442 (calls after each step), PAP-446 (drill evidence), PAP-94 (card source), Atlas dispatch.

Consumes: `PmSourcePort` (PAP-465), Needs Justin card shape (PAP-94), handoff format (PAP-108, soft), webhook approval detection (PAP-97, soft), ADR link (PAP-130, soft).

**Definition of done**

* Sandbox team: a scripted critical swap creates the umbrella, seven step issues and one card; evidence comments appear after each fake gate; `flip` refused until `/approve` (transcript).
* `--no-linear` run produces the same evidence locally; CHANGELOG; Linear comment.

**Test plan**

* Unit: marker idempotency; card text generation from a fixture state; cap queueing.
* E2E: `PmSourcePort` fixture double (no live writes in CI); one live sandbox run recorded.

**Demo**

Reviewer runs `paperos module swap sample --to v2 --step conformance` and opens the created step issue with the `conformance.json` link, then sees the card appear before `flip` and the CLI wait on it. Two minutes.

**Edge cases**

* Umbrella exists from an earlier aborted swap: reused; steps re-linked.
* Justin rejects the card: the CLI records the reason and `--rollback` is offered.
* pm-linear module disabled in the app: `--no-linear` implied with a warning.

**Dependencies**

Hard: PAP-465, PAP-94. Sibling: PAP-442. Soft: PAP-108, PAP-97, PAP-130.

**Agent**

Builder: Forge (Platform Engineer); Atlas (Dispatcher) reviews the card. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-442 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-442 blocks this issue (`blocks` relation).
