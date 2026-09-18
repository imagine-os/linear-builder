---
identifier: "PAP-542"
title: "Reference module `sample`: `@paperos/contract-sample` with `good`, `bad` and `v2` implementations, fixtures, conformance suite and manifests used by the runner, swap CLI, drill rehearsal and scaffold"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Kernel and lint live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-433"]
blocks: ["PAP-441", "PAP-442", "PAP-539", "PAP-541"]
key: "r4/module-system/sample-module"
url: "https://linear.app/paperos/issue/PAP-542/reference-module-sample-paperoscontract-sample-with-good-bad-and-v2"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:04.646Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-542: Reference module `sample`: `@paperos/contract-sample` with `good`, `bad` and `v2` implementations, fixtures, conformance suite and manifests used by the runner, swap CLI, drill rehearsal and scaffold

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build S

**Goal**

PAP-441 tests with "a sample suite with two implementations", PAP-442 with "a scripted swap of the sample module", PAP-433 with golden manifests, PAP-445 with a fixture workspace; none of them owns the sample. A tiny reference module with a deliberately broken implementation and a v2 is the fixture every kernel issue needs and the template every contract author copies. It is the `hello world` of the module system.

**Scope**

In:

* `packages/contracts/sample/`: `@paperos/contract-sample@0.1.0` with one port `GreetingPort { greet(name): Greeting; list(cursor?): Page<Greeting> }`, one topic `sample.greeted` v1, one slot fill target `shell.header.actions`, one route `sample.greet`, Zod schemas, JSON Schema, `fixtures/` (five greetings, one cursor page pair), `conformance/` suite with memory double.
* `packages/sample/`: implementations `good` (default), `bad` (wrong ordering and a missing capability, so exactly three cases fail), `v2` (identical behaviour, different internals, provides the same contract version) with `module.ts` manifests (`kind: runtime`, `swapRisk: low`, `owner: { agent: "Forge", project: "module-system" }`).
* Registration in the three `kernel.ts` boot files behind `module.sample.impl`; `flags.yaml` entry; `ops/swaps/` fixture state for the CLI tests; `docs/platform/sample-module.md` as the worked example referenced by the scaffold.
* Removal note: the sample ships in the template as a dev-only module (`optional: true`, disabled for tenants by default, excluded by `paperos create` unless `--with sample`).

Out: real functionality, UI beyond one header button, the runner and CLI themselves.

**Spec**

* Total under 600 lines including tests; every file commented as the reference pattern.
* `bad` fails exactly cases `sample.GreetingPort.2`, `.4` and reports `unsupported` for `list` pagination; asserted by PAP-441's mutation test.
* `v2` passes side-by-side diff with zero differences after normalisation (PAP-541).
* The manifest is one of the golden manifests PAP-433 validates.

**Interface contract**

Provides: `@paperos/contract-sample`, `packages/sample` with three impls, fixtures and suite, `module.sample.impl` flag, the worked example doc; consumed by PAP-441, PAP-442, PAP-433 (golden manifest), PAP-445 (fixture page), PAP-446 (dry rehearsal before the shell), PAP-543 (template), PAP-545.

Consumes: manifest schema (PAP-433), contract-zero types (PAP-302, soft), kernel (PAP-434, soft; the package compiles without it).

**Definition of done**

* Contract, three implementations and suite merged; `pnpm modules:validate` green; `bad` fails its three cases and nothing else; `v2` diff empty.
* Doc page merged and linked from `docs/module-system.md`; Linear comment.

**Test plan**

* Unit: schemas accept and reject fixtures; memory double passes; each impl's expected conformance outcome.
* E2E: `paperos module conformance sample --impl good,bad,v2` once PAP-441 lands (its demo).

**Demo**

Reviewer opens `packages/sample/README.md`, reads the three-file layout, then runs `pnpm test --filter @paperos/contract-sample` and sees the memory double pass and `bad` fail three named cases. Under a minute.

**Edge cases**

* A contract author copies the sample and forgets to rename the topic: manifest validator `TOPIC_DUPLICATE` names both modules.
* Sample accidentally enabled in production: `optional: true` and disabled by default; the removal matrix (PAP-266) includes it.
* Kernel not merged yet: package builds and tests standalone; `kernel.ts` registration is a follow-up commit.

**Dependencies**

Hard: PAP-433. Soft: PAP-302, PAP-434. Blocks PAP-441, PAP-442.

**Agent**

Builder: Forge (Platform Engineer); Atlas confirms the pattern. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/module-system/conformance-normaliser` = PAP-541, `r4/module-system/module-scaffold` = PAP-543, `r4/module-system/test-kernel` = PAP-545.
