---
identifier: "PAP-446"
title: "Run the shell swap drill: build a deliberately minimal second shell that provides `@paperos/contract-app-shell`, walk the swap playbook end to end, measure, roll back, record"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P2"
type: "Review"
priority: 3
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-82", "PAP-248", "PAP-438", "PAP-442", "PAP-453", "PAP-539"]
blocks: []
key: "module-system/shell-swap-drill"
url: "https://linear.app/paperos/issue/PAP-446/run-the-shell-swap-drill-build-a-deliberately-minimal-second-shell"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:39.238Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-446: Run the shell swap drill: build a deliberately minimal second shell that provides `@paperos/contract-app-shell`, walk the swap playbook end to end, measure, roll back, record

**Model / Effort:** Opus 5 / high

**Goal**

Prove Justin's requirement rather than assert it: rewrite the shell and watch everything else reconnect. A second, intentionally minimal shell (`apps/web-minimal`) implements `@paperos/contract-app-shell` at the same version, passes the shell conformance suite, is shadow-built and screenshot-compared, flipped for the demo tenant, rolled back, then flipped as default and removed again, all through `paperos module swap app-shell --to minimal`. The drill produces numbers for PAP-29 and a punch list for the module system.

**Scope**

In:

* `apps/web-minimal`: a plain React tree with the eleven slots, `composeRoutes`, `useLayout`, a no-op window manager declaring `unsupported` for detach, the config and flags ports; no styling beyond tokens; under 1,500 lines.
* Walk all seven playbook steps with the CLI, collecting evidence: ADR, conformance for both shells, Gate 3 contact sheets at seven widths for both (PAP-82, PAP-84 vision diff), shadow build, canary on the demo tenant, flip, rollback timing, remove.
* Measurements: lines changed outside `apps/web-minimal` (target: zero in module packages), time from `--step fork` to `--step flip`, rollback latency, screenshot diff count classified (expected styling versus defects).
* Punch list: every place a module reached the shell outside the contract, filed as issues on the owning project.
* Report `docs/platform/drills/shell-swap-2026-09.md` and a five-minute recording.

Out: shipping the minimal shell (it is deleted at step 7), redesigning the shell contract (findings become Spec issues).

**Spec**

* Success is defined before the drill: zero edits in `packages/<module>` (excluding `apps/*` and the kernel), conformance green for both shells, every module's nav item, record panel tab and command present in the minimal shell, rollback under 5 s.
* Any module edit needed during the drill is a finding, not a fix: the drill stops, the finding is filed, and resumes only after the fix lands through the owning module.
* The drill runs on staging with the seeded demo tenant (PAP-240), never production.
* The recording follows the PAP-29 format so the two drills compare.

*Round 4 amendment (2026-09-18):*

* Success criteria also count lines changed in `apps/web` (must be zero outside the kernel boot file) and in `packages/contracts/app-shell` (must be zero, or the drill is a contract change, not a swap). \* PAP-84 vision diff is a hard dependency for the screenshot classification; PAP-82 alone gives contact sheets without verdicts. \* Rehearsal: the drill is first run end to end on PAP-542 (`good` to `v2`) the day before, so CLI defects surface before the shell run.

**Interface contract**

Provides: `apps/web-minimal` (temporary), the drill report, the punch list issues, timing numbers for PAP-29, `v1.0` cut recommendation for `contract-app-shell`. Consumes: swap CLI, flag swap, slots runtime, conformance runner and the app-shell suite, `Wire app-shell`, Gate 3 (PAP-82) and vision agent (PAP-84), PAP-240 seed, PAP-88 release train for canary timing. Consumed by: PAP-29 (blank-screen drill numbers), the `v1.0` contract cut, `docs/module-system.md` v2, Justin's decision on any real shell rewrite.

**Test plan**

* The drill is the test. Acceptance: the success criteria above, the CLI state file showing all seven steps with evidence links, the report reviewed by Atlas.
* Regression: after step 7, the full Gate suite on the default shell is identical to before the drill (no residue).

**Definition of done**

* Report, recording and punch list published; numbers posted to PAP-29; findings filed on owning projects; `apps/web-minimal` removed; Linear comment.
* A Needs Justin card summarising: what a real shell rewrite would cost given the drill (one page).

**Edge cases**

* A slot the minimal shell cannot render (dashboard blocks need layout): declared `unsupported`; the conformance report shows it; the drill notes whether the contract should split the slot.
* Modules that fill slots conditionally on flags: canary tenant has all flags on so every fill is exercised.
* Vision agent flags styling differences as defects: the report classifies them; only functional gaps count against success.
* Drill exceeds the 2026-10-01 window: stop at the last completed step, publish partial numbers, file the remainder as a P2 issue.

**Dependencies**

Blocked by module-system/swap-cli, module/app-shell/wire, module-system/ui-slots, PAP-82. Blocks PAP-29.

*Round 4 (2026-09-18): PAP-29 soft: this issue no longer blocks PAP-29 because the shell swap drill (10-01) lands after the blank-screen drill (09-29); PAP-29 proceeds (the first blank-screen drill run uses the default shell only; weekly runs add the swap drill step once PAP-446 exists) and reconciles when this issue lands.*

**Agent**

Built by Sentinel. Reviewed by Atlas and Forge.

**Size**

M

**Demo**

Reviewer watches the five-minute recording: `paperos module swap app-shell --to minimal` steps through conformance and shadow, the demo tenant reloads into the minimal shell with every module's navigation and panels present, `--rollback` restores the full shell in under five seconds, and the report shows zero lines changed in module packages. Five minutes.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/module-system/sample-module` = PAP-542.
