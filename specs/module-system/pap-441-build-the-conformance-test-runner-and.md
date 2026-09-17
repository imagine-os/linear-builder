---
identifier: "PAP-441"
title: "Build the conformance test runner and golden fixture kit: `defineConformanceSuite`, capability handling, normalisation, `conformance.json` artefact and Gate 1 step"
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
blockedBy: ["PAP-239", "PAP-433"]
blocks: ["PAP-442", "PAP-450", "PAP-451", "PAP-452", "PAP-457", "PAP-460", "PAP-463", "PAP-468", "PAP-469", "PAP-470", "PAP-477", "PAP-478", "PAP-479", "PAP-486", "PAP-487", "PAP-488", "PAP-494", "PAP-495"]
key: "module-system/conformance-runner"
url: "https://linear.app/paperos/issue/PAP-441/build-the-conformance-test-runner-and-golden-fixture-kit"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:11:30.303Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-441: Build the conformance test runner and golden fixture kit: `defineConformanceSuite`, capability handling, normalisation, `conformance.json` artefact and Gate 1 step

**Model / Effort:** Opus 5 / medium

**Goal**

Build the shared machinery every per-module conformance suite plugs into: `defineConformanceSuite` with implementation factories and capability sets, golden fixture loading and hash pinning, output normalisation (ids, timestamps, ordering), a CLI that runs a suite against one or several implementations side by side, and the `conformance.json` gate artefact in the PAP-239 shape. The seventeen suites are written by their modules; this issue makes them uniform, diffable and gate-readable (`docs/module-system.md` section 5).

**Scope**

In:

* `packages/kernel/conformance`: `defineConformanceSuite(id, register)`, `describePort`, `caseFor(fixture)`, `capabilities`, statuses `passed|failed|pending|unsupported`, stable case ids `<module>.<port>.<n>`.
* Fixture kit: `loadFixtures(dir)`, schema validation against the contract, `fixtures.lock` hashes; a changed hash without a contract version bump fails.
* Normaliser: replaces UUIDv7, timestamps, signed cursors with placeholders; sorts unordered sets; configurable per port; shared with the flag swap's shadow diffs.
* CLI `paperos module conformance <id> --impl a[,b] [--strict] [--fixtures path]`: runs the suite per implementation, produces per-implementation results and an a-versus-b diff.
* `conformance.json` schema added to PAP-239's package; contact-sheet reporter (PAP-248) renders it; Gate 1 step `conformance` runs every registered suite against the default implementation with the memory doubles.

Out: the per-module suites and doubles (their issues), performance budgets (PAP-242).

**Spec**

* A suite must cover every port in the contract at v0.1; the runner fails `--strict` when a port has no cases.
* `unsupported` requires the implementation to declare the missing capability; an unexpected throw is `failed`.
* Diff between implementations is computed on normalised output and reported by case id; identical output is required for `passed` in side-by-side mode unless the case is marked `impl-specific`.
* Runs are hermetic: no network unless a case declares `live: true`, which Gate 1 skips and the nightly staging job runs.
* Total Gate 1 conformance time under 5 minutes across all suites with the memory doubles (parallel by module).

**Interface contract**

Provides: `defineConformanceSuite`, fixture kit and lock, normaliser, `paperos module conformance`, `conformance.json` schema and reporter, Gate 1 step `conformance`. Consumes: PAP-239 artefact package and reporter conventions, PAP-248 contact sheet, PAP-78 Gate 1, PAP-42 compose stack for real-adapter runs, manifest validator (which ports exist). Consumed by: the seventeen `Conformance test suite` issues, every `Wire <module>` issue, the flag swap (normaliser), the swap CLI (step 3), the shell swap drill.

**Test plan**

* Unit: status derivation, case id stability, capability handling, normaliser on fixtures with ids, timestamps and cursors.
* Integration: a sample suite with two implementations (one correct, one broken) yields the predicted diff by case id; `--strict` fails on an uncovered port.
* Artefact: `conformance.json` validates against the schema; the reporter renders counts and the diff table.
* Gate: the step runs in under 5 minutes on the template with the suites available at the time.

**Definition of done**

* Runner, kit, CLI, schema and gate step merged; sample suite committed as the template for module owners; reporter renders.
* `docs/platform/conformance.md` authoring guide; Linear comment with a sample artefact.

**Edge cases**

* Fixture that depends on another module's data (finance report over tables): the suite declares `requiresContracts` and the runner boots those modules' memory doubles.
* Flaky case (timing): marked `retry: 2` explicitly; the runner reports retries; PAP-90 quarantine reads the artefact.
* Implementation that passes only with a real database: `live: true` cases; the memory run must still cover the port's semantics or `--strict` fails.
* Huge fixtures (20 MB Yjs doc): stored under `fixtures/large/` with Git LFS and loaded lazily.

**Dependencies**

Blocked by module-system/manifest-schema, PAP-239.

**Agent**

Built by Sentinel. Reviewed by Forge and Atlas.

**Size**

M

**Demo**

Reviewer runs `paperos module conformance sample --impl good,bad` and sees `good` all green, `bad` failing three cases, and the diff table by case id; opens the `conformance.json` in the contact sheet. Under a minute.
